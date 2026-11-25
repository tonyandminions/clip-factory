#!/usr/bin/env python3
"""Quality gate for queue.json (README rule 2, Justin 11-25: clips must make sense and be funny or tell the viewer something).
usage: quality_gate.py [queue.json]   exit 1 and a list of failures if any ready/candidate/new item fails.
Checks what a script can check; the rest of rule 2 (stands alone, payoff shown, hook) is judged by reading the clip."""
import json, re, sys
q = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "queue.json"))["items"]
NON_EVENT = re.compile(r"\b(trying to|tries to|can'?t|couldn'?t just|first seconds|playing gta|plays gta|reacts? to)\b", re.I)
bad = []
for i in q:
    new = str(i.get("added", "")) >= "2026-11-25"
    if i.get("status") not in ("ready", "candidate") and not (new and i.get("status") == "scheduled"):
        continue
    n, errs = i.get("name"), []
    p = i.get("point") or {}
    if p.get("type") not in ("funny", "tip", "wow") or len(p.get("line", "")) < 20:
        errs.append('no "point" {type: funny|tip|wow, line: why a stranger cares}')
    plats = i.get("platforms") or []
    plats = [x.lower() for x in (plats.split() if isinstance(plats, str) else plats)]
    yt = not plats or any(x in ("youtube", "yt") for x in plats)
    title = i.get("yt_title") or ""
    if yt and NON_EVENT.search(title):
        errs.append(f"YouTube title describes a non-event: {NON_EVENT.search(title).group(0)!r}")
    if yt and (i.get("part") in (1, "1") or re.search(r"part\s*1", title, re.I)):
        errs.append("Part 1 on YouTube (post the payoff clip only)")
    cap = (i.get("caption") or "").split("\n")[0]
    if i.get("status") == "ready" and len(cap) < 25:
        errs.append("caption's first line doesn't say what happens")
    if errs:
        bad.append((n, errs))
for n, errs in bad:
    print(f"FAIL {n}: " + "; ".join(errs))
print(f"{len(bad)} failing" if bad else "quality gate: all ready/new items pass")
sys.exit(1 if bad else 0)
