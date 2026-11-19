#!/usr/bin/env python3
"""Find the best moments in the last N minutes of a channel's newest Twitch VOD (no ClipSpeed credits).

scan_vod.py <channel> <minutes> <out_dir> [--top 6] [--vod URL] [--no-chat]
Two signals, per second:
  loud   audio loudness peaks (the streamer yelling, explosions)
  chat   chat replay bursts compared with this stream's own normal rate, moved ~7 s earlier
         (chat reacts after the moment). What chat types says what kind of moment it was:
         funny (KEKW, LUL, ICANT...), hype (POG, NO WAY...), fail (L, F, RIP...), scare (monkaS),
         clip (people asking for a clip). Idea from ColinGPT9/clips-studio (AGPL); written fresh here.
Moments are ranked by both together (chat counts more: it's what viewers reacted to). Each moment
gets +/-20 s transcribed. Writes scan.json / scan.txt with VOD offsets you can feed to a
{"vod": ..., "vod_start", "vod_end"} job, plus the top moments by each signal alone for comparison.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request
from collections import Counter
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("channel"); ap.add_argument("minutes", type=float); ap.add_argument("od")
ap.add_argument("--top", type=int, default=6); ap.add_argument("--vod")
ap.add_argument("--no-chat", action="store_true")
a = ap.parse_args(); os.makedirs(a.od, exist_ok=True)

GQL, CID = "https://gql.twitch.tv/gql", "kimne78kx3ncx6brgo4mv6wki5h1ko"  # Twitch's public web client id
CHAT_LAG = 7          # seconds chat trails the moment
CLASSES = {
    "funny": r"^(kekw|kekl|lul|lulw|omegalul|icant|lmao+|lmfao+|lo+l|haha+|hah|xd+|pepelaugh|aware|😂+|💀+|dead|kek)$",
    "hype":  r"^(pog|pogu|poggers|pogchamp|poggies|no ?way|w+|lets ?go+|holy|insane|gg|clean|goated|ez)$",
    "fail":  r"^(l+|f+|rip|sadge|unlucky|bruh+|ratio|ff|pain|nooo+)$",
    "scare": r"^(monkas|monkaw|monkaomega|scared|jumpscare|ahh+)$",
    "clip":  r"(clip (it|that)|clipped|clip this|clip)$",
    "huh":   r"^(\?+|huh|what+|wtf|wut|ayo|hmm+)$",
    "bye":   r"^(gn|gnight|good ?night|night|bye+|cya|o7|peace|later|raid)$",  # stream ending: not a moment
}
CRE = {k: re.compile(v, re.I) for k, v in CLASSES.items()}

def gql(query, variables):
    req = urllib.request.Request(GQL, data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Client-ID": CID, "Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

COMMENTS = """query($videoID: ID!, $offset: Int) { video(id: $videoID) { comments(contentOffsetSeconds: $offset) {
  edges { node { contentOffsetSeconds commenter { id } message { fragments { text } } } } } } }"""

def chat_replay(vod_id, t0, t1, budget=420):
    """[(second, chatter_id, text)] for t0..t1. Paged by offset (cursor paging trips Twitch's integrity check)."""
    seen, off, end = set(), int(t0), time.monotonic() + budget
    while off < t1 and time.monotonic() < end:
        try:
            edges = (((gql(COMMENTS, {"videoID": vod_id, "offset": off}).get("data") or {}).get("video") or {})
                     .get("comments") or {}).get("edges") or []
        except Exception as e:
            print("chat page failed", off, e, flush=True); time.sleep(2); off += 30; continue
        if not edges:
            break
        last = off
        for e in edges:
            n = e["node"]; t = float(n["contentOffsetSeconds"]); last = max(last, t)
            cid = (n.get("commenter") or {}).get("id")
            if cid and t0 <= t <= t1:
                seen.add((t, cid, "".join(str(f.get("text") or "") for f in ((n.get("message") or {}).get("fragments") or []))))
        off = max(off + 1, int(last) + 1)
    return sorted(seen)

def classify(text):
    toks = [w for w in re.split(r"\s+", text.strip()) if w][:6]
    hits = set()
    for k, r in CRE.items():
        if r.search(text.strip()) or any(r.match(w) for w in toks):
            hits.add(k)
    return hits

vurl = a.vod
if not vurl:
    lst = json.loads(subprocess.check_output(["yt-dlp", "-J", "--flat-playlist", "--playlist-items", "1",
          f"https://www.twitch.tv/{a.channel}/videos?filter=archives&sort=time"]))
    vurl = lst["entries"][0]["url"]
meta = json.loads(subprocess.check_output(["yt-dlp", "-J", vurl]))
dur = float(meta.get("duration") or 0)
start = max(0, dur - a.minutes * 60)

# --- chat (runs first: cheap, and tells us if it's usable) ---
chat_curve, chat_info = None, {}
m = re.search(r"/videos/(\d+)", vurl)
if m and not a.no_chat:
    t_c = time.time()
    msgs = chat_replay(m.group(1), start, dur)
    print(f"chat: {len(msgs)} messages in {time.time() - t_c:.0f}s", flush=True)
    if len(msgs) >= 50:
        n = int(dur - start) + 1
        cnt = np.zeros(n); kinds = [Counter() for _ in range(n)]; texts = [Counter() for _ in range(n)]
        react = np.zeros(n); plain = np.zeros(n); seen_users = [set() for _ in range(n)]
        for t, cid, text in msgs:
            i = int(t - start); txt = text.strip()
            if not (0 <= i < n) or not txt or txt.startswith("!") or cid in seen_users[i]:
                continue  # bot commands, one message per person per second
            seen_users[i].add(cid); cnt[i] += 1
            k = classify(txt)
            for kk in k: kinds[i][kk] += 1
            if "bye" in k:
                continue
            if k: react[i] += 1
            else: plain[i] += 1; texts[i][txt.lower()[:30]] += 1
        # copy-paste / giveaway spam ("type Mandy in chat"): one plain text is most of a 10 s window
        spam = np.zeros(n, bool)
        for i in range(n):
            c = Counter()
            for j in range(max(0, i - 5), min(n, i + 5)): c.update(texts[j])
            tot = sum(c.values())
            if tot >= 5 and c.most_common(1)[0][1] >= 0.35 * tot:
                spam[i] = True
        plain[spam] = 0
        W = 6
        burst = np.convolve(react + 0.35 * plain, np.ones(W), "same")          # reactions in a ~6 s window
        cbase = np.array([np.median(burst[max(0, i - 120):max(1, i - 10)]) for i in range(n)]) + 1.0
        ratio = burst / cbase
        chat_curve = np.roll(ratio, -CHAT_LAG); chat_curve[-CHAT_LAG:] = 1
        chat_info = {"msgs": msgs, "kinds": kinds, "cnt": cnt, "spam": int(spam.sum())}
        print(f"chat: {int(spam.sum())} seconds of copy-paste/giveaway spam ignored", flush=True)
        json.dump([[round(t, 1), x] for t, _, x in msgs], open(os.path.join(a.od, "chat.json"), "w"))
    else:
        print("chat: too quiet to use, loudness only", flush=True)

# --- loudness ---
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

def z(v):
    v = np.asarray(v, float); s = v.std() or 1.0
    return (v - np.median(v)) / s

loud_z = z(smooth)
if chat_curve is not None:
    L = min(len(loud_z), len(chat_curve))
    chat_z = z(np.log(np.maximum(chat_curve[:L], 0.2)))
    combined = 0.65 * chat_z + 0.35 * loud_z[:L]
else:
    L = len(loud_z); chat_z = None; combined = loud_z

# never pick dead air (BRB / muted), the stream's first 2 minutes, or its last 5 if it has ended
blocked = np.zeros(L, bool)
blocked |= smooth[:L] < base - 12
if start < 120: blocked[: int(120 - start)] = True
ended = (meta.get("timestamp") or 0) + dur < time.time() - 600 and not meta.get("is_live")
if ended: blocked[max(0, L - 300):] = True
combined = np.where(blocked, -1e9, combined)
if chat_z is not None: chat_z = np.where(blocked, -1e9, chat_z)
loud_z = np.where(np.concatenate([blocked, np.zeros(len(loud_z) - L, bool)]), -1e9, loud_z)

def pick(score, k):
    peaks = []
    for i in np.argsort(-score):
        if all(abs(i - p) >= 60 for p in peaks) and 25 < i < len(score) - 10:
            peaks.append(int(i))
        if len(peaks) >= k:
            break
    return peaks


from faster_whisper import WhisperModel
model = WhisperModel(os.environ.get("WHISPER_MODEL", "small.en"), device="cpu", compute_type="int8")
def describe(p, how):
    seg = x[max(0, (p - 20)) * sec:(p + 20) * sec]
    segs, _ = model.transcribe(seg, language="en", vad_filter=True)
    r = {"vod_offset": round(start + p, 1), "vod_start": round(start + p - 22, 1), "vod_end": round(start + p + 14, 1),
         "picked_by": how, "loud_db_over_median": round(float(smooth[p] - base), 1),
         "text": " ".join(s.text.strip() for s in segs)}
    if chat_curve is not None:
        k = Counter()
        for i in range(p - 3, min(p + 15, len(chat_info["kinds"]))):  # chat in the ~15 s after the moment
            k.update(chat_info["kinds"][i])
        r["chat_x_normal"] = round(float(chat_curve[p]), 1)
        r["chat_reactions"] = dict(k.most_common(3))
        r["chat_sample"] = [t for (tt, _, t) in chat_info["msgs"] if start + p - 2 <= tt <= start + p + 14][:8]
    return r

# stream business (giveaways, sub goals, ads, signing off) is never a clip: skip it and take the next one
BUSINESS = re.compile(r"giveaway|pick (a|the) winner|winner is|type .{1,20} in (the )?chat|subscribe|sub goal|"
                      r"sponsor|promo code|ad break|be right back|brb|see (you|y'all) (guys )?tomorrow|"
                      r"go(ing)? to (sleep|bed)|sleep on stream|get some (actual )?sleep|end(ing)? (the )?stream|raid", re.I)
def keep(cands, how, k):
    out = []
    for p in cands:
        r = describe(p, how)
        if BUSINESS.search(r["text"]):
            print("skipped (stream business):", r["vod_offset"], r["text"][:80], flush=True); continue
        out.append(r)
        if len(out) >= k: break
    return sorted(out, key=lambda r: r["vod_offset"])
top = pick(combined, a.top * 3)
res = keep(top, "both", a.top)
used = [int(r["vod_offset"] - start) for r in res]
extra = {"loud_only": keep([p for p in pick(loud_z[:L], a.top) if all(abs(p - q) > 20 for q in used)], "loud", a.top),
         "chat_only": keep([p for p in (pick(chat_z, a.top) if chat_z is not None else []) if all(abs(p - q) > 20 for q in used)], "chat", a.top)}
out = {"vod": vurl, "vod_duration": dur, "scanned_from": start, "chat_used": chat_curve is not None,
       "chat_messages": len(chat_info.get("msgs", [])), "peaks": res, "compare": extra}
json.dump(out, open(os.path.join(a.od, "scan.json"), "w"), indent=1)
with open(os.path.join(a.od, "scan.txt"), "w") as f:
    for r in res + extra["loud_only"] + extra["chat_only"]:
        ch = f" chat x{r.get('chat_x_normal')} {r.get('chat_reactions')}" if "chat_x_normal" in r else ""
        f.write(f"[{r['vod_start']}-{r['vod_end']}] ({r['picked_by']}) +{r['loud_db_over_median']}dB{ch}  {r['text']}\n")
print("SCAN", json.dumps({k: v for k, v in out.items() if k != "compare"})[:2000], flush=True)
