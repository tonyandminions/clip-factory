#!/usr/bin/env python3
"""Turn a ClipSpeed live-clip moment into raw 16:9 Twitch VOD footage.

live_fetch.py <channel> <ref_url> <gen_utc> <out_dir> [--back 240] [--pad 0,0]
  ref_url : ClipSpeed clip mp4 (any of its renders; only the audio is used)
  gen_utc : when ClipSpeed generated the clip, ISO UTC (e.g. 2026-11-18T16:34:30Z)
Downloads the window [gen-back, gen+20] from the channel's newest VOD, finds the
clip inside it by audio cross-correlation, and prints JSON {src, ss, to, vod, offset}.
"""
import json, subprocess, sys, os, argparse, datetime
import numpy as np

def sh(*c):
    print("+", " ".join(c), flush=True); subprocess.run(c, check=True)

def pcm(path, sr=8000):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32)

ap = argparse.ArgumentParser()
ap.add_argument("channel"); ap.add_argument("ref"); ap.add_argument("gen"); ap.add_argument("od")
ap.add_argument("--back", type=float, default=240); ap.add_argument("--pad", default="0,0")
a = ap.parse_args()
os.makedirs(a.od, exist_ok=True)
ref = os.path.join(a.od, "ref.mp4")
sh("curl", "-sSL", "--retry", "3", "-o", ref, a.ref)
lst = json.loads(subprocess.check_output(["yt-dlp", "-J", "--flat-playlist", "--playlist-items", "1",
      f"https://www.twitch.tv/{a.channel}/videos?filter=archives&sort=time"]))
vurl = lst["entries"][0]["url"]
meta = json.loads(subprocess.check_output(["yt-dlp", "-J", vurl]))
vts = meta.get("timestamp")
gen = datetime.datetime.fromisoformat(a.gen.replace("Z", "+00:00")).timestamp()
end = gen - vts + 20
start = max(0, end - a.back - 20)
win = os.path.join(a.od, "window.mp4")
sh("yt-dlp", "-q", "--no-warnings", "-S", "res,fps,ext:mp4:m4a", "--merge-output-format", "mp4",
   "--download-sections", f"*{start:.0f}-{end:.0f}", "-o", win, vurl)
r, w = pcm(ref), pcm(win)
n = 1 << int(np.ceil(np.log2(len(r) + len(w))))
xc = np.fft.irfft(np.fft.rfft(w, n) * np.conj(np.fft.rfft(r, n)), n)[: len(w) - len(r) + 1]
norm = np.sqrt(np.convolve(w * w, np.ones(len(r)), "valid")) * np.sqrt((r * r).sum()) + 1e-9
score = xc / norm
lag = int(np.argmax(score)); conf = float(score[lag])
ss = lag / 8000; rd = len(r) / 8000
p0, p1 = (float(x) for x in a.pad.split(","))
res = {"src": win, "ss": round(max(0, ss - p0), 2), "to": round(ss + rd + p1, 2), "vod": vurl,
       "vod_offset": round(start + ss, 1), "match": round(conf, 3)}
print("LIVE_FETCH", json.dumps(res), flush=True)
json.dump(res, open(os.path.join(a.od, "live.json"), "w"))
