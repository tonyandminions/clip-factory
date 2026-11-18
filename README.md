# clip-factory

Tony & Minions clip pipeline. Commit a job file to `jobs/` and the `clip` workflow:

1. downloads the clip (yt-dlp, works for Twitch clips and VODs),
2. transcribes it (faster-whisper, word timestamps) into phrase captions with swears dropped,
3. builds the 1080x1920 split edit (title band, streamer cam, caption band, gameplay; nothing drawn over the footage),
4. makes an upload-sized copy (under 3.6 MB) plus a full-quality copy,
5. uploads everything as a workflow artifact (`clips-<run>`).

Job format: see the docstring in `scripts/run_job.py`. Use `"probe": true` to only download, transcribe and make a contact sheet when you still need to find the cam position.

Crop presets (1920x1080 sources):

| Streamer | cam | camfit | game |
|---|---|---|---|
| Lacy (gameplay overlay) | 0,8,493,246 | no | 493,240,1200,675 |
| Lacy (cutscene, larger cam) | 0,10,572,286 | no | 576,200,1100,619 |
| TheBurntPeanut (peanut avatar, bottom left) | 336,770,220,310 | yes | 480,100,1200,675 |

Rules live in the Side Business folder (`LACY Workflow 11-18.md`, Clip Style Guide).

## What performs (update as numbers come in)
- 11-18, first ~80 min on IG: Burnt Peanut "vs GTA 6 traffic" 646 views vs LACY clips 127–277.
  Why it likely won: relatable everyday-GTA frustration (driving/traffic), loud reaction in the first
  2 seconds, ~30 s, simple "<streamer> vs GTA 6 ___" title.
- Apply to LACY picks: favour driving/cops/relatable "first time playing" frustration and big reactions;
  cold-open on the loudest line (trim dead air at the start); 15–30 s; titles like "LACY vs GTA 6 ___".
- Skip: long cutscene dialogue, map scrolling, real-life just-chatting, anything crude/sexual/drug.

## Live route (ClipSpeed → VOD)
`"live": {"channel","vod","ref","gen_utc","back","pad"}` downloads the VOD window and finds the
ClipSpeed clip inside it by audio (match ≥0.9 is good; <0.3 means the window missed — widen `back`).
`gen_utc` = the 10-digit epoch in ClipSpeed's `captioned_<id>_<epoch-ms>.mp4` filename.
Each job gets its own runner (matrix), so push many probes at once.

## Posting playbook (anti-spam, 11-18)
- 4–5 posts/day per platform, ≥75–90 min apart; prime slots 11a–1p and 6–10p ET.
- One post per moment, ever. Check TikTok Studio for posts made by other chats before scheduling (BP "worst driver" was already up).
- Every clip: style variant (--style) + story setup line (--setup) + title in our words. No identical caption templates; 2–4 specific hashtags.
- Hook in the first 1–2 s; 15–35 s; end on the payoff.
- Never: bots/bought followers/views (strike = removed from every Reach campaign), sexualised covers or framing,
  AI voice/footage, logos, links in captions, "follow for part 2" bait.
- Paid campaigns need the streamer's name in caption/on-screen + #Name, English, ≥50% US/CA/UK/AU/NZ audience, submit ≤30 min.

## No reposts (check before every schedule)
- Every posted/scheduled source moment lives in `posted_sources.json` (VOD id + offsets, Twitch clip slug, caption).
- Before scheduling anything: `python3 scripts/dedupe_check.py --vod <id> --start <s> --end <e>` (or `--clip <slug>`). It fails if the moment is within 45s of anything already used. Then add the new entry.
- One moment = one post per platform, ever. Two viewers' Twitch clips of the same moment count as the same moment.
- Other chats post directly in the TikTok/YouTube apps — check TikTok Studio + YouTube Studio scheduled lists too, not just Metricool.
