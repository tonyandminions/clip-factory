#!/usr/bin/env python3
"""Build a 1080x1920 streamer split clip with nothing drawn over the footage.

Layout (y px):  title band 186-326 | facecam 334-874 | caption band 874-1000
                | gameplay 1000-1608 | clear bottom for platform UI.

usage: build_split.py SRC OUT --title "line" "*lime line" [--caps caps.json]
       [--cam x,y,w,h] [--game x,y,w,h] [--ss S --to T] [--capstyle word --words words.json]
caps.json: [[start, end, "TEXT"], ...]  (times relative to the output)
"""
import argparse, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FONT = os.environ.get("CLIP_FONT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", "Poppins-Bold.ttf"))
LIME = "0xB8FF3B"
TITLE_TOP, CAM_Y, CAM_H, CAP_Y, GAME_Y, GAME_H = 222, 334, 540, 874, 1000, 608

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%").replace(",", "\\,")

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--title", nargs="+", required=True)
ap.add_argument("--caps")
ap.add_argument("--cam", default="0,10,572,286")
ap.add_argument("--game", default="576,200,1100,619")
ap.add_argument("--alt", help="x,y,start,end: shift game crop origin during a time window")
ap.add_argument("--ss", type=float); ap.add_argument("--to", type=float)
ap.add_argument("--tsize", type=int, default=48)
ap.add_argument("--camfit", action="store_true", help="keep cam aspect, scale to band height, center (avatar cams)")
ap.add_argument("--credit", help="small credit line under the title band, e.g. twitch.tv/name")
ap.add_argument("--setup", help="story/context line shown in the caption band for the first seconds")
ap.add_argument("--setup-dur", type=float, default=2.8)
ap.add_argument("--native", action="store_true", help="don't rescale the source to 1920x1080 (ClipSpeed vertical clips): crops are in source pixels")
ap.add_argument("--style", default="auto", help="0-7 or auto (hash of output name): accent colour, stack order, look")
ap.add_argument("--capstyle", default="phrase", choices=["phrase", "word"], help="word = phrase on screen, spoken word lit up in the accent colour")
ap.add_argument("--words", help="words.json from transcribe.py (real word timings for --capstyle word)")
a = ap.parse_args()
import re as _re  # STRIP_EMOJI: Poppins has no emoji glyphs
a.title = [_re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\uFE0F]", "", t).strip() for t in a.title]

# --- style variants (so every clip doesn't share one template) ---
ACCENTS = ["0xB8FF3B", "0xFFD84D", "0x5CE1FF", "0xFF9A3C"]
if a.style == "auto":
    import hashlib
    st = int(hashlib.md5(os.path.basename(a.out).encode()).hexdigest(), 16) % 8
else:
    st = int(a.style) % 8
LIME = ACCENTS[st % 4]
GAME_FIRST = st in (1, 2, 5, 6)          # gameplay band on top, cam below
BG_DARK = "-0.45" if st >= 4 else "-0.32"
CAP_SIZE = 58 if st % 2 else 62
if GAME_FIRST:
    GAME_Y, CAP_Y, CAM_Y2 = 334, 334 + GAME_H, 334 + GAME_H + 126
else:
    CAM_Y2 = CAM_Y
print("style", st, "accent", LIME, "game_first", GAME_FIRST)

cx, cy, cw, ch = map(int, a.cam.split(","))
gx, gy, gw, gh = map(int, a.game.split(","))

dt = []
camscale, camx = f'1080:{CAM_H}', '0'
if a.camfit:
    camscale, camx = f'-2:{CAM_H}', '(W-w)/2'
gxe, gye = str(gx), str(gy)
if a.alt:
    ax, ay, s0, s1 = a.alt.split(",")
    gxe = f"'if(between(t,{s0},{s1}),{ax},{gx})'"
    gye = f"'if(between(t,{s0},{s1}),{ay},{gy})'"
line_h = int(a.tsize * 1.22)
y0 = TITLE_TOP + (334 - TITLE_TOP - len(a.title) * line_h) // 2
for i, l in enumerate(a.title):
    col = "white"
    if l.startswith("*"):
        col, l = LIME, l[1:]
    dt.append(f"drawtext=fontfile={FONT}:text='{esc(l)}':fontsize={a.tsize}:fontcolor={col}:"
              f"borderw=4:bordercolor=black:x=(w-text_w)/2:y={y0 + i * line_h}")
if a.credit:
    dt.append(f"drawtext=fontfile={FONT}:text='{esc(a.credit)}':fontsize=30:fontcolor=white@0.85:borderw=3:bordercolor=black:x=(w-text_w)/2:y={CAP_Y}+(126-text_h)/2" + ("" if not a.caps else ":enable='lt(t,0)'"))
caps = json.load(open(a.caps)) if a.caps else []
if a.setup:
    sd = a.setup_dur
    words = esc(a.setup).split(" ")
    lines = [" ".join(words)]
    if len(a.setup) > 26:
        best = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    fs = 50 if len(lines) == 1 else 42
    for i, l in enumerate(lines):
        yy = f"{CAP_Y}+(126-{len(lines)}*{int(fs*1.15)})/2+{i*int(fs*1.15)}"
        dt.append(f"drawtext=fontfile={FONT}:text='{l}':fontsize={fs}:fontcolor=white:borderw=4:bordercolor=black:"
                  f"x=(w-text_w)/2:y={yy}:enable='lt(t,{sd})'")
    shifted = []
    for c0, c1, t in caps:
        if c0 < sd:
            if c1 <= sd + 0.3:
                continue
            c0 = sd
        shifted.append([c0, c1, t])
    caps = shifted
assf = None
if caps and a.capstyle == "word":
    from wordcaps import make_ass, ass_filter
    words = json.load(open(a.words)) if a.words and os.path.exists(a.words) else []
    assp = os.path.splitext(a.out)[0] + "_caps.ass"
    n = make_ass(caps, words, assp, y=CAP_Y + 63, size=CAP_SIZE, accent=LIME)
    assf = ass_filter(assp, os.path.dirname(FONT)); print("word captions", n, "events")
    caps = []
if caps:
    for s, e, t in caps:
        col = "white"
        if t.startswith("*"):
            col, t = LIME, t[1:]
        dt.append(f"drawtext=fontfile={FONT}:text='{esc(t)}':fontsize={CAP_SIZE}:fontcolor={col}:"
                  f"borderw=5:bordercolor=black:x=(w-text_w)/2:y={CAP_Y}+(126-text_h)/2-4:"
                  f"enable='between(t,{s},{e})'")

PRE = "" if a.native else "scale=1920:1080:flags=lanczos,"
fc = (
    f"[0:v]{PRE}setsar=1,fps=30,split=3[b][c][g];"
    f"[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness={BG_DARK}[bg];"
    f"[c]crop={cw}:{ch}:{cx}:{cy},scale={camscale},setsar=1[cam];"
    f"[g]crop={gw}:{gh}:{gxe}:{gye},scale=1080:{GAME_H},setsar=1[game];"
    f"[bg][cam]overlay={camx}:{CAM_Y2}[t1];[t1][game]overlay=0:{GAME_Y}[t2];"
    f"[t2]{','.join(dt + ([assf] if assf else []))},setsar=1[v]"
)
cmd = ["ffmpeg", "-v", "error", "-y"]
if a.ss is not None: cmd += ["-ss", str(a.ss)]
if a.to is not None: cmd += ["-to", str(a.to)]
cmd += ["-i", a.src, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out]
subprocess.run(cmd, check=True)
print("built", a.out)
