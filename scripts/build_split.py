#!/usr/bin/env python3
"""Build a 1080x1920 streamer split clip with nothing drawn over the footage.

Layout (y px):  title band 186-326 | facecam 334-874 | caption band 874-1000
                | gameplay 1000-1608 | clear bottom for platform UI.

usage: build_split.py SRC OUT --title "line" "*lime line" [--caps caps.json]
       [--cam x,y,w,h] [--game x,y,w,h] [--ss S --to T]
caps.json: [[start, end, "TEXT"], ...]  (times relative to the output)
"""
import argparse, json, subprocess

import os
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
a = ap.parse_args()
import re as _re  # STRIP_EMOJI: Poppins has no emoji glyphs
a.title = [_re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\uFE0F]", "", t).strip() for t in a.title]

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
y0 = TITLE_TOP + (CAM_Y - TITLE_TOP - len(a.title) * line_h) // 2
for i, l in enumerate(a.title):
    col = "white"
    if l.startswith("*"):
        col, l = LIME, l[1:]
    dt.append(f"drawtext=fontfile={FONT}:text='{esc(l)}':fontsize={a.tsize}:fontcolor={col}:"
              f"borderw=4:bordercolor=black:x=(w-text_w)/2:y={y0 + i * line_h}")
if a.credit:
    dt.append(f"drawtext=fontfile={FONT}:text='{esc(a.credit)}':fontsize=30:fontcolor=white@0.85:borderw=3:bordercolor=black:x=(w-text_w)/2:y={CAP_Y}+(126-text_h)/2" + ("" if not a.caps else ":enable='lt(t,0)'"))
if a.caps:
    for s, e, t in json.load(open(a.caps)):
        col = "white"
        if t.startswith("*"):
            col, t = LIME, t[1:]
        dt.append(f"drawtext=fontfile={FONT}:text='{esc(t)}':fontsize=62:fontcolor={col}:"
                  f"borderw=5:bordercolor=black:x=(w-text_w)/2:y={CAP_Y}+(126-text_h)/2-4:"
                  f"enable='between(t,{s},{e})'")

fc = (
    f"[0:v]scale=1920:1080:flags=lanczos,setsar=1,fps=30,split=3[b][c][g];"
    f"[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.32[bg];"
    f"[c]crop={cw}:{ch}:{cx}:{cy},scale={camscale},setsar=1[cam];"
    f"[g]crop={gw}:{gh}:{gxe}:{gye},scale=1080:{GAME_H},setsar=1[game];"
    f"[bg][cam]overlay={camx}:{CAM_Y}[t1];[t1][game]overlay=0:{GAME_Y}[t2];"
    f"[t2]{','.join(dt)},setsar=1[v]"
)
cmd = ["ffmpeg", "-v", "error", "-y"]
if a.ss is not None: cmd += ["-ss", str(a.ss)]
if a.to is not None: cmd += ["-to", str(a.to)]
cmd += ["-i", a.src, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out]
subprocess.run(cmd, check=True)
print("built", a.out)
