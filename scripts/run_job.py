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
  "captions": "auto",                     # "auto" (whisper), "none", or [[s,e,"TEXT"],...]
  "capstyle": "ab",                       # "word" = phrase stays up, spoken word lights up; "phrase"; "ab" = split test
  "level": true,                          # even out loudness (-14 LUFS); false to keep the original audio
  "credit": null,                         # small credit line in the caption band when captions are none
  "probe": false,                         # true = only download, transcribe, contact sheet
  "post": false,                          # true = also make a <3.6 MB copy for browser uploads
  "live": null,                           # {"channel","ref","gen_utc","back":240,"pad":"0,0"} ClipSpeed live moment
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


def run(job):
    name = job["name"]
    od = os.path.join("out", name); os.makedirs(od, exist_ok=True)
    src = os.path.join(od, "source.mp4")
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
    tr = [sys.executable, os.path.join(HERE, "transcribe.py"), src, od]
    if job.get("ss") is not None: tr += ["--ss", str(job["ss"])]
    if job.get("to") is not None: tr += ["--to", str(job["to"])]
    capstyle = job.get("capstyle", DEFAULT_CAPSTYLE)
    if capstyle == "ab":  # A/B test (11-19): half the clips word-by-word, half phrase, fixed by name
        import hashlib
        capstyle = "word" if int(hashlib.md5(name.encode()).hexdigest(), 16) % 2 else "phrase"
    json.dump({"capstyle": capstyle, "level": job.get("level", True)}, open(os.path.join(od, "build.json"), "w"))
    if cap == "auto" or job.get("probe") or (capstyle == "word" and isinstance(cap, list)):
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
    if capsfile:
        cmd += ["--caps", capsfile, "--capstyle", capstyle, "--words", os.path.join(od, "words.json")]
    sh(*cmd)
    if job.get("overlay"):  # required campaign logo, visible start to finish
        add_overlay(hq, job["overlay"], od)
    if job.get("level", True):  # even loudness: -14 LUFS, peaks under -1.5 dB (two-pass, no pumping)
        level_audio(hq)
    if job.get("post", False):  # browser-upload copy (<3.6 MB); Metricool uses the HQ file
        sh("bash", os.path.join(HERE, "post_encode.sh"), hq, os.path.join(od, f"{name}_post.mp4"))
    # preview strip of the finished edit
    d2 = dur(hq)
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-vf", f"fps=6/{d2},scale=270:-1,tile=6x1",
       "-frames:v", "1", "-q:v", "3", os.path.join(od, "preview.jpg"))

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
       "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-c:a", "copy", "-movflags", "+faststart", tmp)
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
