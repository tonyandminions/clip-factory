#!/usr/bin/env python3
"""Record N minutes of a live Twitch stream (for streamers without public VODs), find the loudest
moments, cut ~36 s around each, upload the cuts to the GitHub release 'raw-clips', and write
scan.txt / scan.json / sheet.jpg. Feed a cut back in as {"url": "<asset url>", ...} to build it.

record_live.py <channel> <minutes> <out_dir> [--top 5]
"""
import argparse, json, os, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("channel"); ap.add_argument("minutes", type=float); ap.add_argument("od")
ap.add_argument("--top", type=int, default=5)
a = ap.parse_args(); os.makedirs(a.od, exist_ok=True)
name = os.path.basename(a.od.rstrip("/"))

def run(*c, **k):
    print("+", " ".join(c)[:200], flush=True); return subprocess.run(c, check=True, stdin=subprocess.DEVNULL, **k)

stream = subprocess.check_output(["yt-dlp", "-g", "-f", "best[height<=1080]/best", f"https://www.twitch.tv/{a.channel}"],
                                 stdin=subprocess.DEVNULL).decode().split()[0]
rec = os.path.join(a.od, "rec.ts")
run("ffmpeg", "-v", "error", "-y", "-t", str(int(a.minutes * 60)), "-i", stream, "-c", "copy", rec, timeout=int(a.minutes * 60) + 300)
raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", rec, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
x = np.frombuffer(raw, np.float32); sec = 16000; n = len(x) // sec
db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i*sec:(i+1)*sec] ** 2)) for i in range(n)]) + 1e-6)
sm = np.convolve(db, np.ones(3) / 3, "same"); base = float(np.median(sm))
peaks = []
for i in np.argsort(-sm):
    if 25 < i < n - 15 and all(abs(i - p) >= 60 for p in peaks):
        peaks.append(int(i))
    if len(peaks) >= a.top:
        break
from faster_whisper import WhisperModel
model = WhisperModel(os.environ.get("WHISPER_MODEL", "small.en"), device="cpu", compute_type="int8")
repo = os.environ.get("GITHUB_REPOSITORY", "tonyandminions/clip-factory")
subprocess.run(["gh", "release", "view", "raw-clips"], stdin=subprocess.DEVNULL, capture_output=True).returncode == 0 or \
    run("gh", "release", "create", "raw-clips", "--title", "raw clips", "--notes", "Raw 16:9 cuts for building edits")
res, thumbs = [], []
for k, p in enumerate(sorted(peaks)):
    s0 = max(0, p - 22)
    seg = os.path.join(a.od, f"{name}_cut{k+1}.mp4")
    run("ffmpeg", "-v", "error", "-y", "-ss", str(s0), "-t", "36", "-i", rec, "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", seg)
    th = os.path.join(a.od, f"th{k}.jpg")
    run("ffmpeg", "-v", "error", "-y", "-ss", "20", "-i", seg, "-frames:v", "1", "-vf", "scale=480:-1", th); thumbs.append(th)
    segs, _ = model.transcribe(x[s0 * sec:(s0 + 36) * sec], language="en", vad_filter=True)
    text = " | ".join(f"[{t.start:.1f}-{t.end:.1f}] {t.text.strip()}" for t in segs)
    run("gh", "release", "upload", "raw-clips", seg, "--clobber")
    url = f"https://github.com/{repo}/releases/download/raw-clips/{os.path.basename(seg)}"
    res.append({"cut": k + 1, "url": url, "rec_offset": s0, "loud_db_over_median": round(float(sm[p] - base), 1), "text": text})
json.dump({"channel": a.channel, "cuts": res}, open(os.path.join(a.od, "scan.json"), "w"), indent=1)
with open(os.path.join(a.od, "scan.txt"), "w") as f:
    for r in res:
        f.write(f"cut{r['cut']} +{r['loud_db_over_median']}dB {r['url']}\n   {r['text']}\n")
ins = " ".join(f"-i {t}" for t in thumbs)
if thumbs:
    run("bash", "-c", f"ffmpeg -v error -y {ins} -filter_complex 'hstack=inputs={len(thumbs)}' {os.path.join(a.od, 'sheet.jpg')}" if len(thumbs) > 1
        else f"cp {thumbs[0]} {os.path.join(a.od, 'sheet.jpg')}")
os.remove(rec)
print("RECORD", json.dumps(res)[:3000], flush=True)
