# clip-factory — Tony & Minions

## READ FIRST — hard rules (every chat and scheduled task)
1. **No reposts.** Check `posted_sources.json` with `scripts/dedupe_check.py` before building or scheduling; register every clip you schedule. "rejected" entries are banned forever.
2. **Retention.** Best line in the first second, 15–30 s, cut dead air with `segments`.
3. **Cap.** Feed posts: 6/day per platform through Sun 11/22, 4/day after; 90+ min apart; paid clips only in :10 slots. Stories: separate, 6/day, 40+ min apart.
4. **Variety.** Never the same streamer twice in a row; max 2 per streamer per day; Part 2 never before Part 1.
5. **Safety.** No nudity, sexual jokes, slurs, crude humor, or cutscene-only clips. No bots, no passwords, never join campaigns without Justin.
6. **Credits.** ClipSpeed has ~127 one-time credits (~36/hour live). Use only for YourRAGE live on GTA 6, max 45 min/session, keep 30 in reserve, never its Generate/AI tools. Free sources first: Twitch clips, `scan`, `record`. Don't spend vidIQ or Metricool AI credits.
7. **Git.** `git pull --rebase` before every push; retry on conflict. Job files in `jobs/` trigger builds — never move or rewrite old ones.
8. **Chrome.** Close every tab you open. Never click Delete on posts (ask Justin).
9. **PC files.** Write edited copies to a NEW filename in outputs before committing back; check the byte size.
10. **Paid submissions** within 30 min of posting (Submitter task runs at :18 after each :10 slot).


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

## Cap, slots, rotation, parts (launch week + after)
- Cap per platform, counting every post (incl. Speed posted natively): **6/day Thu 11/19–Sun 11/22**, **4/day from Mon 11/23**. 90+ min apart.
- Slots ET — launch week: 9:10, 11:10, 13:20 (Speed, native), 15:10, 18:10, 20:10. From 11/23: 9:10, 13:20, 18:10, 20:10. Paid clips ONLY in :10 slots (the Submitter task runs at :18 after each).
- Rotation: never the same streamer back-to-back; max 2/streamer/day; aim for 2 LACY, 1 Clix or Jason, 1 BP, 1 Speed, 1 women streamer/YourRAGE. Paid clips get 11:10, 18:10, 20:10.
- Part 1 / Part 2: setup → payoff moments get split. Same `style`, title accent "PART 1"/"PART 2", caption "(Part 1)"/"(Part 2)". Part 2 goes 2–6 h after Part 1 or next day same slot; pin "Part 2 is up 👀" on Part 1.
- Shared schedule doc on the PC: Documents/Side Business/Posting Schedule 11-18.md (every chat reads/updates it).

## Ready queue (queue.json)
Clip Finder appends finished clips; Scheduler pops them into open slots. Each item:
`{"name","streamer","campaign":"LACY|Clix|JasonTheWeen|YourRAGE|growth","media":"https://raw.githubusercontent.com/tonyandminions/clip-factory/out/run-N/NAME/NAME_HQ.mp4","caption","yt_title","cover_ms","part":null|{"series","n"},"vod","start","end","clip","status":"ready|scheduled","slot":null,"added"}`
- Part 2 is never scheduled before its Part 1. Same series = same style.
- Metricool payload: providers tiktok+instagram+youtube+facebook; youtubeData short/GAMING/madeForKids false; facebookData REEL; instagramData REEL (TRIAL_REEL for BP growth tests); paid captions must include the streamer name + hashtag (#LACY, #Clix, #JasonTheWeen, #YourRAGE).

## Retention rules (from TikTok Studio data, 11/18)
- BP traffic (30s, loud reaction in second 1): 10.5s avg watch, 11% finished, 94% For You → 222 views.
- LACY dog (47s, slow open): 1.8s avg watch, everyone gone by 0:01, 0% finished → 6 views.
- So: the loudest/funniest line or the key visual in the FIRST SECOND; 15–30s (Part 1 ≤ 35s); no dead air.
- Use `"segments": [[s,e],[s,e]]` (source seconds) to cut silent stretches; manual caption times are then relative to the joined clip. Skip the setup line when the first second already has a spoken line.

## Flash-forward opening (no new code)
`segments` can be out of order: put a 1–2 s peak first, then the story from the start.
Example: `"segments": [[75.0,77.0],[38.5,45.2],[56.5,79.5]]` shows the punchline, then replays it in context.
Use it when the payoff comes late in the clip (more than ~6 s in). Don't use it on Part 2s; they already open on the payoff.

## Writing files back to the PC
Re-committing the same /mnt/user-data/outputs path can push a cached older copy. Always write the edited file to a NEW filename in outputs (e.g. add a timestamp) before device_commit_files, then list the folder and check the byte size matches.

## Stories (Instagram + Facebook)
- Purpose: keep the story ring lit when new people land on the profile, and send followers to each new Reel. Stories don't go to For You/Explore and don't count toward the feed cap.
- Cap: max 6 stories/day per platform, 40+ min apart. Story Crew task runs 8:41 AM (teasers for the day's Reels + Part 2 countdowns) and 2:41 PM (missed teasers + one "live now" card).
- Types: teaser = first ~10 s of the Reel, banner "NEW CLIP" / "PART 1 IS UP" / "PART 2 IS UP", CTA "full video on our page"; countdown card 30 min before a Part 2; one "<STREAMER> IS LIVE" card a day.
- Job: `{"name":"STORY_x","story":{"src":URL,"ss":0,"to":10,"top":"NEW CLIP","bottom":"full video on our page"}}` or `{"story":{"src":URL,"card":true,"t":3,"lines":[...],"bottom":"..."}}` → out/run-N/STORY_x/STORY_x_story.mp4.
- Metricool: providers instagram + facebook only, instagramData {type STORY}, facebookData {type STORY}, no text. Teaser goes 40–70 min after its Reel; never before it.
- Polls/questions/link stickers can't be added through the API. If Justin wants one, schedule that story with autoPublish:false so the Metricool app pings his phone to add the sticker and post it.
