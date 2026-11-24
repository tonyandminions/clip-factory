#!/usr/bin/env python3
"""Daily fresh pick, step 1: find and rank the newest GTA 6 moments with Twitch's OFFICIAL API (Helix).

Route A (Justin, 11-20): this only FINDS and RANKS moments. It never downloads video.
Justin grabs the winning clip himself (screen recording or ClipSpeed) and drops it in the
Google Drive folder "T&M Fresh Drop"; the Fresh Pick task builds and posts it from there.

Needs a free Twitch developer app (dev.twitch.tv -> Console -> Register Your Application)
with its Client ID / Client Secret stored as GitHub Actions secrets TWITCH_CLIENT_ID and
TWITCH_CLIENT_SECRET. Uses the app access token (client credentials) only: no user login.

Usage:
  python3 scripts/fresh_scan.py --out fresh/            # writes <stamp>.json + latest.json + latest.md
  python3 scripts/fresh_scan.py --selftest              # scoring test with fake clips, no network

Score (higher = more likely to hit), tuned in fresh_config.json:
  velocity   views per hour since the clip was made (the crowd's own signal)
  clippers   how many different viewers clipped the same moment (strongest signal)
  hook       title words that match what wins for us: a GTA 6 mechanic discovered > a story/reaction
  live       the streamer is live on GTA 6 right now (the moment is still hot)
  campaign   paid campaign weight (expired campaigns drop to growth weight)
  fresh      decays over 48 h
Already-posted moments (posted_sources.json, same VOD within 45 s or same clip slug) are dropped.
"""
import argparse, datetime as dt, json, math, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.twitch.tv/helix"
PAD = 45


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def parse_ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


class Helix:
    def __init__(self, cid, secret):
        # Pasted secrets often carry a stray space or newline; Twitch rejects those.
        cid, secret = cid.strip(), secret.strip()
        try:
            tok = http_json("https://id.twitch.tv/oauth2/token",
                            data=urllib.parse.urlencode({"client_id": cid, "client_secret": secret,
                                                         "grant_type": "client_credentials"}).encode())
        except urllib.error.HTTPError as e:
            # Twitch's reply names the problem (e.g. "invalid client secret") and never echoes the keys.
            body = e.read().decode(errors="replace")[:300]
            sys.exit(f"Twitch token request failed: HTTP {e.code} {body} "
                     f"(client id length {len(cid)}, secret length {len(secret)})")
        self.h = {"Client-ID": cid, "Authorization": "Bearer " + tok["access_token"]}

    def get(self, path, params):
        q = urllib.parse.urlencode(params, doseq=True)
        return http_json(f"{API}/{path}?{q}", headers=self.h)


def load_json(name, default):
    p = os.path.join(ROOT, name)
    return json.load(open(p)) if os.path.exists(p) else default


def already_posted(clip, posted):
    for e in posted:
        if clip.get("id") and e.get("clip") == clip["id"]:
            return e.get("name") or True
        if clip.get("video_id") and clip.get("vod_offset") is not None and str(e.get("vod")) == str(clip["video_id"]):
            s, en = e.get("start"), e.get("end")
            if s is None:
                continue
            a, b = clip["vod_offset"], clip["vod_offset"] + clip.get("duration", 30)
            if a <= (en or s) + PAD and b >= s - PAD:
                return e.get("name") or True
    return None


def hook_type(title, cfg):
    t = " " + (title or "").lower() + " "
    if any(w in t for w in cfg["skip_words"]):
        return "skip"
    if any(w in t for w in cfg["hook_words"]["mechanic"]):
        return "mechanic"
    if any(w in t for w in cfg["hook_words"]["story"]):
        return "story"
    return "other"


def cluster(clips):
    """Group clips of the same moment (same VOD, offsets within PAD s; no VOD: same streamer, made within 3 min)."""
    groups = []
    for c in sorted(clips, key=lambda c: -c["view_count"]):
        for g in groups:
            h = g[0]
            if h["broadcaster_login"] != c["broadcaster_login"]:
                continue
            if h.get("video_id") and c.get("video_id") and h.get("vod_offset") is not None and c.get("vod_offset") is not None:
                if h["video_id"] == c["video_id"] and abs(h["vod_offset"] - c["vod_offset"]) <= PAD:
                    g.append(c); break
            elif abs((parse_ts(h["created_at"]) - parse_ts(c["created_at"])).total_seconds()) <= 180:
                g.append(c); break
        else:
            groups.append([c])
    return groups


def score_group(g, cfg, live, now):
    best = g[0]  # most-viewed clip of the moment = the one Justin grabs
    login = best["broadcaster_login"]
    r = cfg["roster"][login]
    views = sum(c["view_count"] for c in g)
    age_h = max(0.5, (now - min(parse_ts(c["created_at"]) for c in g)).total_seconds() / 3600)
    velocity = views / age_h
    titles = " | ".join(dict.fromkeys(c["title"] for c in g))
    ht = hook_type(titles, cfg)
    if ht == "skip":
        return None
    weight = r["weight"]
    until = r.get("until")
    expired = bool(until and now.date().isoformat() > until)
    if expired:
        weight = cfg["expired_weight"]
    dur = best.get("duration", 0)
    pts = {
        "velocity": round(10 * math.log10(1 + velocity), 2),
        "clippers": round(4 * math.log2(len(g)), 2),
        "hook": {"mechanic": 6, "story": 2}.get(ht, 0),  # 11-21: TikTok views come from search -> mechanic facts win
        "live": 2 if login in live else 0,
        "length": (1 if cfg["ideal_duration"][0] <= dur <= cfg["ideal_duration"][1] else 0)
                  - (3 if dur < cfg["min_duration"] else 0),
    }
    fresh = max(0.4, 1 - age_h / 48)
    score = round(sum(pts.values()) * weight * fresh, 2)
    return {
        "score": score, "streamer": login, "name": best["broadcaster_name"], "campaign": r["campaign"],
        "campaign_expired": expired, "platforms": r["platforms"], "rule_note": r.get("note", ""),
        "hook_type": ht, "title": best["title"], "all_titles": titles, "views": views,
        "clippers": len(g), "age_h": round(age_h, 1), "views_per_h": round(velocity), "duration": dur,
        "url": best["url"], "clip": best["id"], "vod": best.get("video_id") or None,
        "vod_offset": best.get("vod_offset"), "created_at": best["created_at"],
        "thumbnail": best.get("thumbnail_url"), "live_now": login in live, "points": pts, "fresh": round(fresh, 2),
    }


def rank(clips, cfg, live, posted, now):
    fresh_clips, dropped = [], []
    for c in clips:
        hit = already_posted(c, posted)
        (dropped if hit else fresh_clips).append(c if not hit else {"title": c["title"], "posted_as": hit})
    out = [s for s in (score_group(g, cfg, live, now) for g in cluster(fresh_clips)) if s]
    out.sort(key=lambda s: -s["score"])
    return out, dropped


def scan(cfg):
    h = Helix(os.environ["TWITCH_CLIENT_ID"], os.environ["TWITCH_CLIENT_SECRET"])
    game = h.get("games", {"name": cfg["game_name"]})["data"]
    if not game:
        sys.exit(f"game not found: {cfg['game_name']}")
    gid = game[0]["id"]
    logins = list(cfg["roster"])
    users = {u["id"]: u["login"] for u in h.get("users", {"login": logins})["data"]}
    live = {s["user_login"].lower(): s for s in h.get("streams", {"user_id": list(users), "first": 100})["data"]
            if s.get("game_id") == gid}
    now = now_utc()
    start = (now - dt.timedelta(hours=cfg["hours"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    clips = []
    for uid, login in users.items():
        data = h.get("clips", {"broadcaster_id": uid, "started_at": start,
                               "ended_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "first": 50})["data"]
        for c in data:
            if c.get("game_id") != gid:
                continue
            c["broadcaster_login"] = login
            clips.append(c)
    return clips, live, now


def write(out_dir, ranked, dropped, live, now, cfg):
    os.makedirs(out_dir, exist_ok=True)
    stamp = now.astimezone(dt.timezone(dt.timedelta(hours=-5))).strftime("%Y-%m-%d_%H%M")
    doc = {"scanned_at": now.isoformat(), "hours": cfg["hours"], "live_on_gta6": sorted(live),
           "top": ranked[:cfg["top"]], "others": ranked[cfg["top"]:cfg["top"] + 15], "already_posted": dropped[:30]}
    for n in (f"{stamp}.json", "latest.json"):
        json.dump(doc, open(os.path.join(out_dir, n), "w"), indent=1)
    lines = [f"# Fresh pick shortlist {stamp} ET (last {cfg['hours']} h, Twitch official API)", "",
             "Live on GTA 6 now: " + (", ".join(sorted(live)) or "nobody"), ""]
    for i, s in enumerate(ranked[:cfg["top"]], 1):
        lines.append(f"{i}. **{s['name']}** ({s['campaign']}{', ENDED' if s['campaign_expired'] else ''}) score {s['score']}: "
                     f"\"{s['title']}\" - {s['views']} views in {s['age_h']} h by {s['clippers']} clipper(s), "
                     f"{s['duration']:.0f} s, {s['hook_type']} - {s['url']}")
    if not ranked:
        lines.append("No new GTA 6 moments from the roster in this window.")
    open(os.path.join(out_dir, "latest.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


def selftest():
    cfg = load_json("fresh_config.json", {})
    now = now_utc()
    t = lambda h: (now - dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")
    clips = [
        {"id": "A", "broadcaster_login": "lacy", "broadcaster_name": "LACY", "title": "lacy found out gas runs out", "view_count": 900, "created_at": t(3), "duration": 30, "video_id": "1", "vod_offset": 1000, "url": "u/A"},
        {"id": "A2", "broadcaster_login": "lacy", "broadcaster_name": "LACY", "title": "GAS LOL", "view_count": 300, "created_at": t(3), "duration": 25, "video_id": "1", "vod_offset": 1010, "url": "u/A2"},
        {"id": "B", "broadcaster_login": "clix", "broadcaster_name": "Clix", "title": "clix funny", "view_count": 2000, "created_at": t(20), "duration": 40, "video_id": "2", "vod_offset": 50, "url": "u/B"},
        {"id": "C", "broadcaster_login": "kreekcraft", "broadcaster_name": "KreekCraft", "title": "giveaway time", "view_count": 5000, "created_at": t(2), "duration": 30, "video_id": "3", "vod_offset": 5, "url": "u/C"},
        {"id": "D", "broadcaster_login": "lacy", "broadcaster_name": "LACY", "title": "posted already", "view_count": 5000, "created_at": t(2), "duration": 30, "video_id": "2932194507", "vod_offset": 7840, "url": "u/D"},
    ]
    posted = load_json("posted_sources.json", {}).get("entries", [])
    ranked, dropped = rank(clips, cfg, {"lacy"}, posted, now)
    assert [s["clip"] for s in ranked] == ["A", "B"], [s["clip"] for s in ranked]
    assert ranked[0]["clippers"] == 2 and ranked[0]["hook_type"] == "mechanic"
    assert dropped and dropped[0]["posted_as"], dropped
    print("selftest ok:", [(s["clip"], s["score"]) for s in ranked])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fresh")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    cfg = load_json("fresh_config.json", None)
    if not os.environ.get("TWITCH_CLIENT_ID") or not os.environ.get("TWITCH_CLIENT_SECRET"):
        sys.exit("TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET secrets are not set (Justin registers the free Twitch developer app).")
    clips, live, now = scan(cfg)
    posted = load_json("posted_sources.json", {}).get("entries", [])
    ranked, dropped = rank(clips, cfg, live, posted, now)
    write(a.out, ranked, dropped, live, now, cfg)


if __name__ == "__main__":
    main()
