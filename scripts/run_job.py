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
  "post": false                           # true = also make a <3.6 MB copy for browser uploads
}
Outputs go to out/<name>/: source.mp4, transcript.txt, caps.json, <name>_HQ.mp4, <name>_post.mp4, sheet.jpg
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def sh(*cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

def run(job):
    name = job["name"]
    od = os.path.join("out", name); os.makedirs(od, exist_ok=True)
    src = os.path.join(od, "source.mp4")
    if job.get("file"):
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
    for k in ("cam", "game", "alt", "ss", "to", "credit"):
        if job.get(k) is not None:
            cmd += [f"--{k}", str(job[k])]
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

if __name__ == "__main__":
    for path in sys.argv[1:]:
        data = json.load(open(path))
        for job in (data if isinstance(data, list) else [data]):
            try:
                run(job)
            except Exception as e:
                print(f"JOB FAILED {job.get('name')}: {e}", flush=True)
