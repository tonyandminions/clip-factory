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
  "credit": null,                         # small credit line in the caption band when captions are none
  "probe": false,                         # true = only download, transcribe, contact sheet
  "post": false,                          # true = also make a <3.6 MB copy for browser uploads
  "live": null                            # {"channel","ref","gen_utc","back":240,"pad":"0,0"} ClipSpeed live moment
}
Outputs go to out/<name>/: source.mp4, transcript.txt, caps.json, <name>_HQ.mp4, <name>_post.mp4, sheet.jpg
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def sh(*cmd, timeout=900):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL, timeout=timeout)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

def run(job):
    name = job["name"]
    od = os.path.join("out", name); os.makedirs(od, exist_ok=True)
    src = os.path.join(od, "source.mp4")
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
    D = dur(src)
    # contact sheet of the raw source (to check cam / overlay positions)
    sh("ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
       f"fps=12/{D},scale=480:-1,drawtext=fontfile={HERE}/../fonts/Poppins-Bold.ttf:text='%{{pts\\:hms}}':fontsize=16:fontcolor=yellow:box=1:boxcolor=black:x=380:y=4,tile=4x3",
       "-frames:v", "1", "-q:v", "3", os.path.join(od, "sheet.jpg"))
    cap = job.get("captions", "auto")
    tr = [sys.executable, os.path.join(HERE, "transcribe.py"), src, od]
    if job.get("ss") is not None: tr += ["--ss", str(job["ss"])]
    if job.get("to") is not None: tr += ["--to", str(job["to"])]
    if cap == "auto" or job.get("probe"):
        sh(*tr)
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
        cmd += ["--caps", capsfile]
    sh(*cmd)
    if job.get("post", False):  # browser-upload copy (<3.6 MB); Metricool uses the HQ file
        sh("bash", os.path.join(HERE, "post_encode.sh"), hq, os.path.join(od, f"{name}_post.mp4"))
    # preview strip of the finished edit
    d2 = dur(hq)
    sh("ffmpeg", "-v", "error", "-y", "-i", hq, "-vf", f"fps=6/{d2},scale=270:-1,tile=6x1",
       "-frames:v", "1", "-q:v", "3", os.path.join(od, "preview.jpg"))

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
