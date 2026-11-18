#!/usr/bin/env python3
"""Refuse to schedule a clip whose source moment we already posted or scheduled.

Usage:
  python3 scripts/dedupe_check.py --vod 2932226282 --start 5740 --end 5770
  python3 scripts/dedupe_check.py --clip StupidGiantGrasshopperBudBlast-S2jrqYRqUgEfiAFv
  python3 scripts/dedupe_check.py --caption "zero patience for traffic"

Exit code 1 (and prints the match) if it overlaps anything in posted_sources.json.
Add the new entry to posted_sources.json as soon as it is scheduled.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "posted_sources.json")
PAD = 45  # seconds of slack: two clips within 45s of each other count as the same moment


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vod")
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--clip")
    ap.add_argument("--caption")
    a = ap.parse_args()
    reg = json.load(open(REG))["entries"]
    hits = []
    for e in reg:
        if a.clip and e.get("clip") and a.clip.split("/")[-1] == e["clip"]:
            hits.append((e, "same Twitch clip"))
            continue
        if a.vod and e.get("vod") == str(a.vod) and a.start is not None:
            end = a.end if a.end is not None else a.start + 30
            if a.start < e["end"] + PAD and end > e["start"] - PAD:
                hits.append((e, f"overlaps VOD {e['vod']} {e['start']}-{e['end']}s"))
                continue
        if a.caption and e.get("caption"):
            shared = words(a.caption) & words(e["caption"])
            if len(shared) >= 3:
                hits.append((e, f"similar caption ({', '.join(sorted(shared))})"))
    if hits:
        for e, why in hits:
            print(f"DUPLICATE: {e['name']} [{e['status']} {e.get('date','')}] - {why}")
        sys.exit(1)
    print("OK: new moment")


if __name__ == "__main__":
    main()
