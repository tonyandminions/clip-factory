#!/usr/bin/env python3
"""Transcribe a clip with faster-whisper and write phrase captions.

usage: transcribe.py SRC OUTDIR [--ss S] [--to T]
writes OUTDIR/transcript.txt (timestamped lines), OUTDIR/caps.json ([[start, end, TEXT], ...])
and OUTDIR/words.json ([[start, end, word, is_swear], ...]) for word-by-word captions
Swear words are dropped from captions (the audio is untouched).
"""
import argparse, json, os, re, subprocess
import numpy as np
from faster_whisper import WhisperModel

SWEARS = re.compile(r"^(\w*fuck\w*|f\*+\w*|\w*shit\w*|\w*bitch\w*|(dumb|bad|jack|smart|fat)?ass(hole)?s?|dick\w*|puss(y|ies)|cunt\w*|nigg\w*|fag\w*|retard\w*|damn|goddamn|bastard\w*|cock\w*|whore\w*|slut\w*|hoe?s?)$", re.I)
MAX_WORDS, MAX_CHARS, GAP = 4, 24, 0.35

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("outdir")
ap.add_argument("--ss", type=float, default=0.0); ap.add_argument("--to", type=float)
ap.add_argument("--model", default=os.environ.get("WHISPER_MODEL", "large-v3-turbo"))
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)

# 11-25: small.en garbled game words ("spikes trip", "pause" for "push", "IG bottle"), so captions made no sense.
# Bigger model + a vocabulary hint; falls back to small.en if the big model can't load.
VOCAB = ("GTA 6 livestream. Jason, Lucia, Vice City, Leonida, Snapmatic, wanted level, spike strip, tracker, "
         "Lamborghini, chop shop, heist, NPC, chat, cops, alligator, seaplane, Rockstar, PS5, L3, R2, triangle.")
try:
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
except Exception as e:
    print("model", a.model, "failed:", e, "-> small.en", flush=True)
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     check=True, capture_output=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True, language="en", beam_size=5,
                           initial_prompt=VOCAB, condition_on_previous_text=False)

words, lines, unsure = [], [], []
for s in segs:
    lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
    for w in (s.words or []):
        t0, t1 = w.start - a.ss, w.end - a.ss
        if t1 <= 0 or (a.to is not None and w.start >= a.to):
            continue
        words.append((max(0.0, t0), t1, w.word.strip()))
        if (w.probability or 0) < 0.55:
            unsure.append(f"{max(0.0, t0):6.2f}  {w.word.strip()}  ({w.probability:.2f})")
open(os.path.join(a.outdir, "transcript.txt"), "w").write("\n".join(lines) + "\n")
# words Whisper wasn't sure about: check these by ear / against the picture before writing captions
open(os.path.join(a.outdir, "caps_review.txt"), "w").write("\n".join(unsure) + "\n")
# word timings for word-by-word captions (wordcaps.py); swears flagged so they never show
json.dump([[round(w[0], 3), round(w[1], 3), w[2], bool(SWEARS.match(re.sub(r"[^\w*]", "", w[2])))] for w in words],
          open(os.path.join(a.outdir, "words.json"), "w"))

caps, cur = [], []
def flush():
    if not cur:
        return
    kept = [w for w in cur if not SWEARS.match(re.sub(r"[^\w*]", "", w[2]))]
    if kept:
        text = " ".join(w[2] for w in kept).upper().strip(" ,.")
        if text:
            caps.append([round(cur[0][0], 2), round(cur[-1][1], 2), text])
    cur.clear()

for w in words:
    if cur and (len(cur) >= MAX_WORDS or w[0] - cur[-1][1] > GAP
                or len(" ".join(x[2] for x in cur + [w])) > MAX_CHARS
                or cur[-1][2].endswith((".", "?", "!"))):
        flush()
    cur.append(w)
flush()
# hold each caption until the next one starts (max +0.6s) so it doesn't flicker
for i, c in enumerate(caps):
    nxt = caps[i + 1][0] if i + 1 < len(caps) else c[1] + 0.6
    c[1] = round(min(nxt, c[1] + 0.6), 2)
# every other caption in lime for rhythm
for i, c in enumerate(caps):
    if i % 3 == 1:
        c[2] = "*" + c[2]
json.dump(caps, open(os.path.join(a.outdir, "caps.json"), "w"), indent=0)
print(f"{len(caps)} captions, {len(words)} words")
