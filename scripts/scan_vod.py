#!/usr/bin/env python3
"""Find the loudest moments in the last N minutes of a channel's newest Twitch VOD (no ClipSpeed credits).

scan_vod.py <channel> <minutes> <out_dir> [--top 6] [--vod URL]
Downloads audio only, finds loudness peaks (>=60 s apart), transcribes +/-20 s around each,
and writes scan.json / scan.txt with VOD offsets you can feed to a {"vod": ..., "vod_start", "vod_end"} job.
"""
import argparse, json, os, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("channel"); ap.add_argument("minutes", type=float); ap.add_argument("od")
ap.add_argument("--top", type=int, default=6); ap.add_argument("--vod")
a = ap.parse_args(); os.makedirs(a.od, exist_ok=True)
vurl = a.vod
if not vurl:
    lst = json.loads(subprocess.check_output(["yt-dlp", "-J", "--flat-playlist", "--playlist-items", "1",
          f"https://www.twitch.tv/{a.channel}/videos?filter=archives&sort=time"]))
    vurl = lst["entries"][0]["url"]
meta = json.loads(subprocess.check_output(["yt-dlp", "-J", vurl]))
dur = float(meta.get("duration") or 0)
start = max(0, dur - a.minutes * 60)
aud = os.path.join(a.od, "scan_audio.m4a")
subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", "bestaudio/worst", "--download-sections", f"*{start:.0f}-{dur:.0f}",
                "-o", aud, vurl], check=True, stdin=subprocess.DEVNULL, timeout=900)
raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", aud, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
x = np.frombuffer(raw, np.float32)
sec = 16000
n = len(x) // sec
rms = np.array([np.sqrt(np.mean(x[i*sec:(i+1)*sec] ** 2)) for i in range(n)])
db = 20 * np.log10(rms + 1e-6)
smooth = np.convolve(db, np.ones(3) / 3, "same")
base = np.median(smooth)
order = np.argsort(-smooth)
peaks = []
for i in order:
    if all(abs(i - p) >= 60 for p in peaks) and 25 < i < n - 10:
        peaks.append(int(i))
    if len(peaks) >= a.top:
        break
from faster_whisper import WhisperModel
model = WhisperModel(os.environ.get("WHISPER_MODEL", "small.en"), device="cpu", compute_type="int8")
res = []
for p in sorted(peaks):
    seg = x[max(0, (p - 20)) * sec:(p + 20) * sec]
    segs, _ = model.transcribe(seg, language="en", vad_filter=True)
    text = " ".join(s.text.strip() for s in segs)
    res.append({"vod_offset": round(start + p, 1), "vod_start": round(start + p - 22, 1), "vod_end": round(start + p + 14, 1),
                "loud_db_over_median": round(float(smooth[p] - base), 1), "text": text})
out = {"vod": vurl, "vod_duration": dur, "scanned_from": start, "peaks": res}
json.dump(out, open(os.path.join(a.od, "scan.json"), "w"), indent=1)
with open(os.path.join(a.od, "scan.txt"), "w") as f:
    for r in res:
        f.write(f"[{r['vod_start']}-{r['vod_end']}] +{r['loud_db_over_median']}dB  {r['text']}\n")
print("SCAN", json.dumps(out)[:2000], flush=True)
