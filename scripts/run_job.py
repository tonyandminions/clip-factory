#!/usr/bin/env python3
"""Run one clip job: download -> transcribe -> split edit -> upload-sized encode -> contact sheet.

Job JSON (jobs/<anything>.json), a single object or a list of objects:
{
  "name": "LACY_BankJob",                 # output file stem
  "url": "https://www.twitch.tv/<ch>/clip/<slug>",   # any yt-dlp URL, or "file": "path/in/repo"
  "title": ["LACY tried his first", "*bank robbery in GTA 6"],   # "*" = lime line
  "cam": "0,8,493,246", "camfit": false,  # cam crop x,y,w,h in the 1920x1080 source; camfit = avatar cams
  "game": "493,240,1200,675",             # gameplay crop (avoid cam/chat/overlays)
  "alt": null,                            # "x,y,t0,t1" shift gameplay crop during a window
  "ss": null, "to": null,                 # trim (seconds in source)
  "captions": [[0.2,1.8,"TEXT"]],         # hand-checked list [[s,e,"TEXT"],...] or "none". "auto" (whisper) is PROBE-ONLY
                                          #   since 11-25: auto captions garbled words and went out unread. Probe first, fix
                                          #   caps.json (see caps_review.txt for unsure words), pass the list.
  "native": false,                        # true = crops are in source pixels (source is not 1920x1080), e.g. re-captioning
                                          #   one of our finished HQ files: cam "0,334,1080,540", game "0,1000,1080,608"
  "capstyle": "ab",                       # "word" = phrase stays up, spoken word lights up; "phrase"; "ab" = split test
  "level": true,                          # even out loudness (-14 LUFS); false to keep the original audio
  "credit": null,                         # small credit line in the caption band when captions are none
  "probe": false,                         # true = only download, transcribe, contact sheet
  "post": false,                          # true = also make a <3.6 MB copy for browser uploads
  "live": null,                           # {"channel","ref","gen_utc","back":240,"pad":"0,0"} ClipSpeed live moment
  "explain": null,                        # explainer freeze (Justin 11-21, TikTok originality): {"t": 2.0, "dur": 1.8,
                                          #   "head": "GTA 6 MECHANIC", "text": "Cars run out of gas. No gas station = you walk."}
                                          #   t/dur in seconds of the FINISHED clip; audio keeps playing, picture freezes with a card
  "csband": false,                        # ClipSpeed live clip (official ClipSpeed connector, 11-24): finds the cam+game band
                                          #   between ClipSpeed's black title/caption bars, drops their burned captions/title,
                                          #   cam = band top, game = bottom 16:9 of the band; rebuilt with OUR title + captions
  "mute": null,                           # "auto" = silence every swear Whisper finds (words.json flags; damn/goddamn/hoe left in)
                                          #   and/or [[s,e],...] extra windows in seconds of the FINISHED clip
                                          #   (Justin 11-24: "no bleeps, just cut audio" - a short silent gap, no tone)
                                          #   a slur found in the finished clip FAILS the build (cut it out with "segments" instead)
  "blur": null,                           # [{"t0","t1","x","y","w","h"}] blur a box (FINISHED 1080x1920 frame) for a time window,
                                          #   e.g. a revealing in-game outfit; YouTube/Facebook only (README content rules)
  "yt1440": false,                        # also write NAME_YT1440.mp4 (1440x2560) for Justin's direct YouTube uploads:
                                          #   YouTube is widely reported to give 1440p+ uploads its better (VP9) encode
  "overlay": null                         # campaign logo/watermark on the WHOLE clip (KreekCraft, Clix x JBL):
                                          # {"url": png/webp/Drive link, "w": 230, "x": "main_w-overlay_w-36", "y": "main_h*0.52", "alpha": 1.0}
}
Outputs go to out/<name>/: source.mp4, transcript.txt, caps.json, <name>_HQ.mp4, <name>_post.mp4, sheet.jpg
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CAPSTYLE = os.environ.get("CAPSTYLE", "ab")  # "word", "phrase" or "ab" (split test, see README)

def sh(*cmd, timeout=900):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL, timeout=timeout)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

def fit_1080(src, od):
    """Crop the black bars a phone screen recording adds, then scale to the 1920x1080 frame the
    crop presets expect. If what's left isn't roughly 16:9 (e.g. a vertical recording), pad instead."""
    log = subprocess.run(["ffmpeg", "-v", "info", "-ss", "1", "-t", "6", "-i", src, "-vf", "cropdetect=24:2:0",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", log)
    vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1"
    if m:
        w, h, x, y = map(int, m[-1])
        if h and 1.6 <= w / h <= 1.95:
            vf = f"crop={w}:{h}:{x}:{y},scale=1920:1080,setsar=1"
    out = os.path.join(od, "fit.mp4")
    sh("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "veryfast",
       "-crf", "16", "-c:a", "aac", "-b:a", "192k", out)
    os.replace(out, src)


def cs_band(src, od):
    """ClipSpeed vertical clip (1080x1920): its cam+game band sits between black bars that hold ClipSpeed's
    burned title (top) and captions (bottom). Rows of the band are mostly non-black in nearly every frame;
    caption rows are mostly black between the letters. Returns (cam, game) crops in source pixels + info."""
    import numpy as np
    W, H = 216, 384
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=2,scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
    rowfill = np.median((fr > 18).mean(axis=2), axis=0)          # share of non-black pixels per row, median over time
    good = rowfill > 0.6
    best, start = (0, 0), None
    for i, g in enumerate(list(good) + [False]):       # longest run of band rows
        if g and start is None:
            start = i
        elif not g and start is not None:
            if i - start > best[1] - best[0]:
                best = (start, i)
            start = None
    y0, y1 = best
    iw, ih = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height", "-of", "csv=p=0", src], capture_output=True,
                                     text=True, check=True).stdout.strip().split(",")[:2])
    by0, by1 = int(y0 * ih / H), int(y1 * ih / H)
    bh = by1 - by0
    gh = int(iw * 9 / 16) // 2 * 2
    chh = (bh - gh) // 2 * 2
    ok = bh < ih * 0.9 and 0.25 * iw <= chh <= 0.8 * iw
    info = {"src_size": [iw, ih], "band": [0, by0, iw, bh], "cam_h": chh, "game_h": gh, "confident": bool(ok)}
    json.dump(info, open(os.path.join(od, "csband.json"), "w"))
    print("csband", info, flush=True)
    cam = f"0,{by0},{iw},{max(chh, 2)}"
    game = f"0,{by1 - gh},{iw},{gh}"
    return cam, game, info


MILD = {"damn", "goddamn", "hoe", "hoes", "ho"}
SLUR = re.compile(r"^(nigg\w*|fag\w*|retard\w*)$", re.I)

def mute_windows(od, extra=None, auto=True):
    """Swear windows (s, e) in the finished clip from words.json, plus any extra windows. Raises on a slur."""
    win = [tuple(map(float, w)) for w in (extra or [])]
    wp = os.path.join(od, "words.json")
    if auto and os.path.exists(wp):
        for t0, t1, w, sw in json.load(open(wp)):
            clean = re.sub(r"[^\w]", "", w).lower()
            if SLUR.match(clean):
                open(os.path.join(od, "SLUR_FOUND.txt"), "w").write(f"{t0}-{t1} {w}\n")
                raise SystemExit(f"SLUR in finished clip at {t0}-{t1}: cut it out with segments (README content rules)")
            if sw and clean not in MILD:
                win.append((max(0.0, t0 - 0.06), t1 + 0.06))
    win.sort()
    merged = []
    for a, b in win:
        if merged and a <= merged[-1][1] + 0.05: merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else: merged.append((a, b))
    return merged

def add_mute(hq, windows, od):
    """Cut the audio (silence, no bleep tone) in each window; video copied."""
    if not windows: return
    cond = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in windows)
    tmp = os.path.join(od, "mute.mp4")
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-af", f"volume=0:enable='{cond}'", "-c:v", "copy",
       "-c:a", "aac", "-b:a", "192k", tmp)
    os.replace(tmp, hq)
    json.dump([[round(a, 2), round(b, 2)] for a, b in windows], open(os.path.join(od, "muted.json"), "w"))

def add_blur(hq, regions, od):
    """Blur boxes ({"t0","t1","x","y","w","h"} in the finished 1080x1920 frame) for their time windows."""
    if not regions: return
    n = len(regions); tmp = os.path.join(od, "blur.mp4")
    fc = f"[0:v]split={n + 1}[base]" + "".join(f"[s{i}]" for i in range(n)) + ";"
    prev = "base"
    for i, r in enumerate(regions):
        x, y, w, h = (int(r[k]) // 2 * 2 for k in ("x", "y", "w", "h"))
        rad = max(8, min(w, h) // 6)
        fc += (f"[s{i}]crop={w}:{h}:{x}:{y},boxblur={rad}:3[b{i}];"
               f"[{prev}][b{i}]overlay={x}:{y}:enable='between(t,{float(r['t0'])},{float(r['t1'])})'[v{i}];")
        prev = f"v{i}"
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-filter_complex", fc.rstrip(";"), "-map", f"[{prev}]", "-map", "0:a?",
       "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", tmp)
    os.replace(tmp, hq)

def run(job):
    name = job["name"]
    od = os.path.join("out", name); os.makedirs(od, exist_ok=True)
    src = os.path.join(od, "source.mp4")
    if job.get("restyle"):  # add the TikTok explainer card to an already-built HQ (ours, on the out branch / Metricool)
        hq = os.path.join(od, f"{name}_HQ.mp4")
        sh("curl", "-sSL", "--retry", "3", "-o", hq, job["restyle"]["src"])
        add_explain(hq, job["explain"], od)
        d2 = dur(hq)
        sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-vf", f"fps=6/{d2},scale=270:-1,tile=6x1",
           "-frames:v", "1", "-q:v", "3", os.path.join(od, "preview.jpg"))
        sh("ffmpeg", "-v", "error", "-y", "-ss", str(float(job["explain"].get("t", 2.0)) + 0.6), "-i", hq,
           "-frames:v", "1", "-vf", "scale=540:-1", os.path.join(od, "sheet.jpg"))
        json.dump({"restyle": True, "explain": job["explain"]}, open(os.path.join(od, "build.json"), "w"))
        return
    if job.get("story"):  # IG/FB Story from a finished clip: {"src","ss","to","top","bottom"} or {"src","card":true,"lines":[..],"t"}
        S = job["story"]; local = os.path.join(od, "in.mp4")
        sh("curl", "-sSL", "--retry", "3", "-o", local, S["src"])
        args = [sys.executable, os.path.join(HERE, "make_story.py"), "--src", local, "--out", os.path.join(od, f"{name}_story.mp4"),
                "--top", S.get("top", "NEW CLIP"), "--bottom", S.get("bottom", "full video on our page")]
        if S.get("accent"): args += ["--accent", S["accent"]]
        if S.get("card"): args += ["--card", "--lines", "|".join(S.get("lines", [])), "--t", str(S.get("t", 3)), "--dur", str(S.get("dur", 6))]
        else: args += ["--ss", str(S.get("ss", 0)), "--to", str(S.get("to", 12))]
        sh(*args); os.remove(local)
        return
    if job.get("record"):  # record a live stream: {"channel","minutes","top"}
        R = job["record"]
        sh(sys.executable, os.path.join(HERE, "record_live.py"), R["channel"], str(R.get("minutes", 10)), od, "--top", str(R.get("top", 5)),
           timeout=int(R.get("minutes", 10) * 60) + 600)
        return
    if job.get("scan"):  # loudness scan of a VOD: {"channel","minutes","top"}
        S = job["scan"]
        sh(sys.executable, os.path.join(HERE, "scan_vod.py"), S["channel"], str(S.get("minutes", 30)), od,
           "--top", str(S.get("top", 6)), *(["--vod", S["vod"]] if S.get("vod") else []))
        return
    if job.get("vod_start") is not None:  # explicit VOD section {"vod","vod_start","vod_end"}
        sh("yt-dlp", "-q", "--no-warnings", "-S", "res,fps,ext:mp4:m4a", "--merge-output-format", "mp4",
           "--download-sections", f"*{job['vod_start']}-{job['vod_end']}", "-o", src, job["vod"])
    elif job.get("live"):  # ClipSpeed live moment -> raw VOD window, aligned by audio
        L = job["live"]
        sh(sys.executable, os.path.join(HERE, "live_fetch.py"), L["channel"], L["ref"], L["gen_utc"], od,
           "--back", str(L.get("back", 240)), "--pad", L.get("pad", "0,0"),
           *(["--vod", L["vod"]] if L.get("vod") else []))
        info = json.load(open(os.path.join(od, "live.json")))
        os.replace(info["src"], src)
        if info["match"] < 0.3:
            print(f"WARNING low audio match {info['match']}", flush=True)
        if job.get("ss") is None: job["ss"] = info["ss"]
        if job.get("to") is None: job["to"] = info["to"]
    elif job.get("file"):
        sh("cp", job["file"], src)
    else:
        sh("yt-dlp", "-q", "--no-warnings", "-S", "res,fps,ext:mp4:m4a", "--merge-output-format", "mp4", "-o", src, job["url"])
    if job.get("csband"):  # ClipSpeed clip -> our own edit (their burned captions/title are outside the band)
        cam, game, _ = cs_band(src, od)
        job.setdefault("cam", cam); job.setdefault("game", game)
        job["_native"] = True
    if job.get("fit1080"):  # phone screen recording / ClipSpeed download (fresh pick, route A) -> clean 1920x1080
        fit_1080(src, od)
    # "segments": [[s,e],...] in source seconds — keep only these parts (cuts dead air), joined in order.
    segs = job.get("segments")
    if segs and not job.get("probe"):
        fc = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];"
                     for i, (a, b) in enumerate(segs))
        fc += "".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
        cut = os.path.join(od, "cut.mp4")
        sh("ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "aac", "-b:a", "192k", cut)
        os.replace(cut, src)
        job["ss"] = None; job["to"] = None
    D = dur(src)
    # contact sheet of the raw source (to check cam / overlay positions)
    sh("ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
       f"fps=12/{D},scale=480:-1,drawtext=fontfile={HERE}/../fonts/Poppins-Bold.ttf:text='%{{pts\\:hms}}':fontsize=16:fontcolor=yellow:box=1:boxcolor=black:x=380:y=4,tile=4x3",
       "-frames:v", "1", "-q:v", "3", os.path.join(od, "sheet.jpg"))
    cap = job.get("captions", "auto")
    if cap == "auto" and not job.get("probe"):
        sys.exit('captions "auto" is probe-only (11-25). Run {"probe": true} first, read transcript.txt + caps_review.txt, '
                 'fix the words in caps.json and pass them as "captions": [[s,e,"TEXT"],...]. A clip whose captions '
                 "don't make sense doesn't get posted.")
    if job.get("native"):
        job["_native"] = True
    tr = [sys.executable, os.path.join(HERE, "transcribe.py"), src, od]
    if job.get("ss") is not None: tr += ["--ss", str(job["ss"])]
    if job.get("to") is not None: tr += ["--to", str(job["to"])]
    capstyle = job.get("capstyle", DEFAULT_CAPSTYLE)
    if capstyle == "ab":  # A/B test (11-19): half the clips word-by-word, half phrase, fixed by name
        import hashlib
        capstyle = "word" if int(hashlib.md5(name.encode()).hexdigest(), 16) % 2 else "phrase"
    json.dump({"capstyle": capstyle, "level": job.get("level", True)}, open(os.path.join(od, "build.json"), "w"))
    if cap == "auto" or job.get("probe") or job.get("mute") or (capstyle == "word" and isinstance(cap, list)):
        sh(*tr)  # also writes words.json (word timings) for word-by-word captions
    if job.get("probe"):
        return
    capsfile = None
    if cap == "auto":
        capsfile = os.path.join(od, "caps.json")
    elif isinstance(cap, list):
        capsfile = os.path.join(od, "caps_manual.json"); json.dump(cap, open(capsfile, "w"))
    hq = os.path.join(od, f"{name}_HQ.mp4")
    cmd = [sys.executable, os.path.join(HERE, "build_split.py"), src, hq, "--title", *job["title"]]
    for k in ("cam", "game", "alt", "ss", "to", "credit", "setup", "style", "setup_dur"):
        if job.get(k) is not None:
            cmd += [f"--{k.replace('_', '-')}", str(job[k])]
    if job.get("camfit"):
        cmd += ["--camfit"]
    if job.get("_native"):
        cmd += ["--native"]
    if capsfile:
        cmd += ["--caps", capsfile, "--capstyle", capstyle, "--words", os.path.join(od, "words.json")]
    sh(*cmd)
    if job.get("explain"):  # freeze-frame explainer card; before the logo so the logo stays on top
        add_explain(hq, job["explain"], od)
    if job.get("blur"):  # blur boxes (revealing in-game outfit etc.), under the logo
        add_blur(hq, job["blur"], od)
    if job.get("overlay"):  # required campaign logo, visible start to finish
        add_overlay(hq, job["overlay"], od)
    if job.get("level", True):  # even loudness: -14 LUFS, peaks under -1.5 dB (two-pass, no pumping)
        level_audio(hq)
    if job.get("mute") or os.path.exists(os.path.join(od, "words.json")):
        # the slur check always runs when we have word timings; muting only when asked
        m = job.get("mute")
        wins = mute_windows(od, m if isinstance(m, list) else None, auto=True)
        if m:
            add_mute(hq, wins, od)
    if job.get("yt1440"):
        y = os.path.join(od, f"{name}_YT1440.mp4")
        sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-vf", "scale=1440:2560:flags=lanczos", "-c:v", "libx264",
           "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", y)
    if job.get("post", False):  # browser-upload copy (<3.6 MB); Metricool uses the HQ file
        sh("bash", os.path.join(HERE, "post_encode.sh"), hq, os.path.join(od, f"{name}_post.mp4"))
    # preview strip of the finished edit
    d2 = dur(hq)
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-vf", f"fps=6/{d2},scale=270:-1,tile=6x1",
       "-frames:v", "1", "-q:v", "3", os.path.join(od, "preview.jpg"))
    gate_check(hq, capsfile, d2, od)

def gate_check(hq, capsfile, D, od):
    """README rule 2 checks a script can do on the finished clip. Writes gate.txt (published to the out branch):
    'OK' or one WARN line each. Whoever built the clip reads it and fixes or explains before scheduling."""
    warns = []
    def vol(ss, t):
        e = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-ss", str(ss), "-t", str(t), "-i", hq, "-vn",
                            "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.search(r"mean_volume: (-?[\d.]+) dB", e)
        return float(m.group(1)) if m else None
    caps = json.load(open(capsfile)) if capsfile and os.path.exists(capsfile) else []
    first = min((c[0] for c in caps), default=None)
    v0, v1 = vol(0, 1.5), vol(0, D)
    quiet = v0 is not None and v1 is not None and v0 < v1 - 6
    if quiet and (first is None or first > 1.5):
        warns.append(f"WARN slow open: first 1.5 s is quiet ({v0} dB vs {v1} dB clip average) and no line before "
                     f"{first} s. Start on the action or the best line (rule 2.4).")
    if not 12 <= D <= 30.5:
        warns.append(f"WARN length {D:.1f} s is outside 12-30 s (rule 2.4).")
    if caps:
        last = max(c[1] for c in caps)
        if D - last < 0.25:
            warns.append("WARN the last caption runs to the final frame: check the clip doesn't end mid-sentence (rule 2.3).")
        if D - last > 4:
            warns.append(f"WARN {D - last:.1f} s after the last line: trim the tail unless the payoff is visual (rule 2.3).")
        gaps = sorted(caps)
        big = [(a[1], b[0]) for a, b in zip(gaps, gaps[1:]) if b[0] - a[1] > 6]
        if big:
            warns.append(f"WARN silent stretch(es) with no captions {big}: cut dead air unless it's action (rule 2.4).")
    open(os.path.join(od, "gate.txt"), "w").write("\n".join(warns or ["OK"]) + "\n")
    print("GATE:", *(warns or ["OK"]), sep="\n  ", flush=True)

def level_audio(path, target=-14.0, tp=-1.5, lra=11.0):
    """Two-pass loudnorm: measure, then apply one linear gain so every clip lands at the same loudness."""
    meas = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-vn", "-af",
                           f"loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    m = re.findall(r"\{[^{}]*\}", meas)
    if not m:
        print("level: no audio, skipped", flush=True); return
    j = json.loads(m[-1])
    if float(j["input_i"]) < -60:
        print("level: silent, skipped", flush=True); return
    tmp = path.replace(".mp4", "_lvl.mp4")
    af = (f"loudnorm=I={target}:TP={tp}:LRA={lra}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    sh("ffmpeg", "-v", "error", "-y", "-i", path, "-map", "0", "-c:v", "copy", "-af", af, "-ar", "48000",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp)
    os.replace(tmp, path)
    print(f"level: {j['input_i']} LUFS -> {target}", flush=True)

def add_explain(hq, ex, od):
    """Freeze the picture for `dur` s at `t` (finished-clip seconds) with a slight punch-in and an explainer card.
    Audio keeps playing (no silence, no desync); the video resumes at t+dur. TikTok originality layer (11-21)."""
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    T = float(ex.get("t", 2.0)); D = float(ex.get("dur", 1.8))
    total = dur(hq)
    T = max(0.3, min(T, total - D - 0.3))
    still = os.path.join(od, "explain_still.png"); card = os.path.join(od, "explain_card.png")
    sh("ffmpeg", "-v", "error", "-y", "-ss", f"{T:.3f}", "-i", hq, "-frames:v", "1", still)
    im = Image.open(still).convert("RGB")
    W, H = im.size
    z = 1.06  # punch-in
    zw, zh = int(W / z), int(H / z)
    im = im.crop(((W - zw) // 2, (H - zh) // 2, (W - zw) // 2 + zw, (H - zh) // 2 + zh)).resize((W, H), Image.LANCZOS)
    im = im.convert("RGBA")
    font_path = os.path.join(HERE, "..", "fonts", "Poppins-Bold.ttf")
    f_head = ImageFont.truetype(font_path, 40); f_body = ImageFont.truetype(font_path, 58)
    head = (ex.get("head") or "GTA 6 MECHANIC").upper()
    lines = textwrap.wrap(ex["text"], width=int(ex.get("wrap", 24)))[:4]
    pad, gap = 40, 14
    body_h = [f_body.getbbox(l)[3] - f_body.getbbox(l)[1] for l in lines]
    head_h = f_head.getbbox(head)[3] - f_head.getbbox(head)[1]
    box_w = int(W * 0.9)
    box_h = pad * 2 + head_h + 22 + sum(body_h) + gap * (len(lines) - 1)
    x0 = (W - box_w) // 2
    y0 = int(H * float(ex.get("y", 0.60))) - box_h // 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(layer)
    dr.rectangle((0, 0, W, H), fill=(0, 0, 0, 70))  # dim the frozen frame a little
    dr.rounded_rectangle((x0, y0, x0 + box_w, y0 + box_h), radius=34, fill=(12, 12, 16, 228), outline=(184, 255, 59, 255), width=5)
    y = y0 + pad
    dr.text((W // 2, y), head, font=f_head, fill=(184, 255, 59, 255), anchor="mt"); y += head_h + 22
    for l, h in zip(lines, body_h):
        dr.text((W // 2, y), l, font=f_body, fill=(255, 255, 255, 255), anchor="mt"); y += h + gap
    Image.alpha_composite(im, layer).convert("RGB").save(card)
    tmp = hq.replace(".mp4", "_ex.mp4")
    fc = f"[0:v][1:v]overlay=0:0:enable='between(t,{T:.3f},{T + D:.3f})',format=yuv420p[v]"
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-loop", "1", "-i", card, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
       "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-c:a", "copy", "-movflags", "+faststart", tmp)
    os.replace(tmp, hq)
    for f in (still,):
        os.remove(f)
    print(f"explain: freeze {T:.2f}-{T + D:.2f}s '{head}: {ex['text']}'", flush=True)

def add_overlay(hq, ov, od):
    url = ov["url"]
    m = re.search(r"drive\.google\.com/(?:file/(?:u/\d+/)?d/|open\?id=)([\w-]+)", url)
    if m:
        url = f"https://drive.usercontent.google.com/download?id={m.group(1)}&export=download&confirm=t"
    raw = os.path.join(od, "overlay_raw"); png = os.path.join(od, "overlay.png")
    sh("curl", "-sSL", "--retry", "3", "-o", raw, url)
    from PIL import Image  # handles webp (incl. first frame of animated), png, jpg
    im = Image.open(raw); im.seek(0); im = im.convert("RGBA")
    bb = im.split()[3].getbbox()  # trim transparent padding so w/x/y place the visible logo itself
    if bb and ov.get("trim", True):
        p = 6; im = im.crop((max(bb[0]-p, 0), max(bb[1]-p, 0), min(bb[2]+p, im.width), min(bb[3]+p, im.height)))
    print("overlay size after trim", im.size, flush=True)
    im.save(png)
    w = int(ov.get("w", 230)); x = str(ov.get("x", "main_w-overlay_w-36")); y = str(ov.get("y", "main_h*0.52"))
    a = float(ov.get("alpha", 1.0))
    tmp = hq.replace(".mp4", "_ov.mp4")
    fc = f"[1:v]scale={w}:-1,format=rgba,colorchannelmixer=aa={a}[o];[0:v][o]overlay=x={x}:y={y}:format=auto,format=yuv420p[v]"
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-loop", "1", "-i", png, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
       "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-c:a", "copy", "-movflags", "+faststart", tmp)
    os.replace(tmp, hq); os.remove(raw)

def safe(job):
    try:
        run(job)
    except Exception as e:
        print(f"JOB FAILED {job.get('name')}: {e}", flush=True)

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    jobs = []
    for path in sys.argv[1:]:
        data = json.load(open(path))
        jobs += data if isinstance(data, list) else [data]
    # jobs are mostly download/network bound: run up to 3 at once (CLIP_WORKERS to change)
    with ThreadPoolExecutor(int(os.environ.get("CLIP_WORKERS", "3"))) as ex:
        list(ex.map(safe, jobs))
