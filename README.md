# clip-factory — Tony & Minions

## READ FIRST — hard rules (every chat and scheduled task)
**Strategy source of truth:** `Documents\Side Business\Platform Playbook.md` on the PC (per-platform caps, slot grid, originality rules, 2026 research + sources). The schedule lives in `Posting Schedule 11-18.md` next to it.

1. **No reposts.** Check `posted_sources.json` with `scripts/dedupe_check.py` before building or scheduling; register every clip you schedule. "rejected" entries are banned forever.
2. **Retention.** Best line in the first second, 15–30 s, cut dead air with `segments`.
3. **Per-platform caps (from Fri 11/20, Justin 11-19 "do what's right for each one").** TikTok 3 · Instagram 4 · YouTube 4 · Facebook 3 · X 4 per day, counting every post incl. native Speed ones. Each slot only goes to its platforms (grid below) — set Metricool `providers` per post, never all four by default. **A queue item with a `"platforms"` list (per-view campaigns: KreekCraft, AsianJeff, Bobby VanRiper) only goes to the slot's platforms that are also in its list** — e.g. AsianJeff in the 18:10 slot = TikTok, Instagram, YouTube, X (no Facebook). Paid clips only in :10 slots. Stories separate: 6/day, 40+ min apart.
4. **Variety.** Never the same streamer twice in a row; max 2 per streamer per day; Part 2 never before Part 1.
5. **Safety.** No nudity, sexual jokes, slurs, crude humor, or cutscene-only clips. No bots, no passwords, never join campaigns without Justin.
6. **Credits.** ClipSpeed Starter = 300 credits a month (renews the 18th, ~36 credits per hour live). Since 11-19 (Justin: viral moments need to be found and posted within minutes) the **Live Hunter** uses it on whichever PAID streamer is live on GTA 6 and hottest right now, not only YourRAGE. Max 45 min per session; at most 1 session a day while under 150 credits (2 a day above that); always keep 30 in reserve; never its Generate/AI tools. Free sources first for everything else: Twitch clips, `scan` (chat-aware, also works on a VOD that's still live), `record`. Don't spend vidIQ or Metricool AI credits.
7. **Git.** `git pull --rebase` before every push; retry on conflict. Job files in `jobs/` trigger builds — never move or rewrite old ones.
8. **Chrome.** Close every tab you open. Never click Delete on posts (ask Justin).
9. **PC files — never overwrite (Justin, 11-19).** Before changing any file in `Documents\Side Business`: stage the CURRENT file fresh, copy it into `Side Business\03 Versions\<file name>\<file name>_Vers-NN` (next number), make your change on top of it keeping every other section/row (other chats edit these files too), write it to a NEW filename in outputs, commit with `expectedMtimeMs` from the stage (changed? re-stage and merge — never force), check the byte size.
10. **Paid submissions** within 30 min of posting (Submitter task runs at :18 after each :10 slot). Content Rewards auto-detects TikTok + Instagram cards only: tick them and submit first (pasting a link switches the dialog to single-link mode), then reopen Submit clip, paste the YouTube Shorts link, tick the box and submit it on its own.
11. **Log everything.** After any change (posts scheduled/moved, submissions, PC files, queue), append one line to `Side Business\Logs\Activity Log YYYY-MM.md`: `- YYYY-MM-DD HH:MM ET · <who> · <what> · <files/posts>`. Append only — never edit or delete earlier lines.


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
| KreekCraft (cam top-left, red frame; game crop cuts his on-stream captions) | 0,118,420,428 | yes | 440,180,1360,765 |
| YourRAGE | 1590,700,330,380 | yes | 240,210,1300,731 |

Rules live in the Side Business folder (`LACY Workflow 11-18.md`, Clip Style Guide).

## Pipeline upgrades (tested 11-19, Justin: "test it, see if it's better")
- **`scan` jobs now use chat too.** Twitch chat replay (no login) is counted per second against the stream's own normal rate, moved ~7 s earlier, and read for what kind of moment it was (funny KEKW/LUL, hype POG/NO WAY, fail L/F, scare monkaS, "clip it"). Giveaway/copy-paste spam, `!commands`, goodbyes, dead air, the first 2 min and the last 5 min of an ended VOD are ignored, and moments whose transcript is stream business (giveaways, subs, sponsors, signing off) are skipped. `scan.txt` lists the picks by both signals first `(both)`, then loud-only and chat-only for comparison, each with `chat xN {reactions}`. Test on KreekCraft's 11-18 VOD: 4–5 of 6 combined picks usable vs 1–2 of 4 loudness-only picks (those were mostly crude/sexual or repetitive). On quiet chats (AsianJeff's Twitch, ~7 msg/min) it adds little and falls back to loudness. Still read every transcript: the scan suggests, you decide. `"no_chat": true` is not needed; it switches itself off under 50 messages.
- **Word-by-word captions** (`scripts/wordcaps.py`, `"capstyle": "word"`): the phrase stays up and the spoken word lights up in the clip's accent colour; hand-checked caption text is kept, with real word timings from whisper when the words line up (otherwise timed by word length). Long lines now shrink to fit instead of running off the screen. **Split test running:** with no `capstyle` set, half the clips get word style and half phrase style (fixed by the clip name, written to `run-N/NAME/build.json`). Analyst: compare average watch time / finish rate of the two groups after ~40 posts, then set the winner in `DEFAULT_CAPSTYLE` (run_job.py).
- **Volume levelling** (`"level": true`, default): every HQ clip is brought to -14 LUFS with peaks under -1.5 dB (two-pass loudnorm). Before this, our clips ranged from -12 to -25 LUFS, so quiet streams sounded weak next to everything else in the feed.

## What performs (update as numbers come in)
- **11-18 launch day (Analyst, nightly 11-18 ~23:15 ET).** Sources: TikTok Studio, Metricool IG, Content Rewards view counts.
  - TikTok: LACY "can't steal cars" 248 (9.6 s avg, **37% finished**, 15 s), BP "vs traffic" 226 (10.4 s, 11%, 30 s). Every evening post (4:45–9 PM) got 0–11 views; Speed "download" 0 views after 4 h.
  - IG: BP traffic 1,316; LACY "lost all his money" PART 2 **1,452** (best clip); LACY clips 130–280; Gator P1 151.
  - Part 1 → Part 2 did not carry viewers (TT 11→5); P2 won on IG as a standalone because its hook is relatable ("dying takes ALL your money").
  - Followers: TikTok 4, IG ~4, YouTube +2, FB 0. Stories: no reply/tap data in Metricool yet.
- Winning hook = a relatable GTA 6 **mechanic surprise/frustration** in second 1 (can't steal cars, traffic, lose all money). 15–21 s clips finish 3x better than 30 s.
- Avoid: slow opens (LACY dog 1.8 s avg), cutscene dialogue, reposting a moment with a new cut (BP traffic went up twice on TikTok 11-18: 6 views, counts as a repost).
- Earlier (11-18, first ~80 min IG): BP "vs GTA 6 traffic" 646 vs LACY 127–277; "<streamer> vs GTA 6 ___" titles work.
- Skip: long cutscene dialogue, map scrolling, real-life just-chatting, anything crude/sexual/drug.

## Live route (ClipSpeed → VOD)
`"live": {"channel","vod","ref","gen_utc","back","pad"}` downloads the VOD window and finds the
ClipSpeed clip inside it by audio (match ≥0.9 is good; <0.3 means the window missed — widen `back`).
`gen_utc` = the 10-digit epoch in ClipSpeed's `captioned_<id>_<epoch-ms>.mp4` filename.
Each job gets its own runner (matrix), so push many probes at once.

## Live fast lane (Live Hunter, from 11-19)
For a moment caught live by ClipSpeed, speed beats the slot grid:
1. Build our own edit with the `live` route (campaign rules as usual: KreekCraft logo overlay + caption, #Name hashtags, no links). Check preview.jpg + caps.json.
2. Post it NOW in place of the next paid slot that hasn't gone out yet today (11:10 / 18:10 / 20:10), on that slot's platforms (+ X natively for campaigns that pay on X). Move the clip that was in that slot to the next open 9:10 slot (Scheduler's FRESH FIRST rule), with its story teaser and any one-shot submit task. Never delete posts. Same number of posts per day, so the caps hold.
3. No paid slot left today: post only on platforms still under today's cap; otherwise queue it as fresh for tomorrow's 11:10.
4. Submit it on Content Rewards within 30 minutes yourself (the Submitter only runs at :18 after slots). Register it in posted_sources.json and the tracker.
5. Max 2 fast-lane posts per session. The rest of the session's good moments go to queue.json as fresh clips.

## Posting playbook (anti-spam, 11-18)
- Caps per platform and the slot grid: see "Cap, slots, rotation, parts" above (replaces the old 4–6/day rule). Prime slots 11a–1p and 6–10p ET.
- **Originality checklist (every clip needs 3+):** our own title band, a story edit (segments / flash-forward / Part arc), our own setup or context line, hand-checked captions, a caption written in our words. A crop + auto captions alone counts as a re-upload on YouTube and Facebook.
- One post per moment per platform, ever. Check TikTok Studio for posts made by other chats before scheduling (BP "worst driver" was already up).
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

## Cap, slots, rotation, parts (from Fri 11/20)
Slot grid (ET) — each slot goes ONLY to the ✓ platforms:

| Slot | What goes here | TikTok | IG | YouTube | FB | X (native) |
|---|---|:-:|:-:|:-:|:-:|:-:|
| 9:10 | older / backlog clip | – | ✓ | ✓ | ✓ | – |
| 11:10 | paid clip | ✓ | ✓ | ✓ | – | ✓ |
| 13:20 | Speed (Speed chat, native) | – | – | ✓ | – | – |
| 15:10 | growth clip (BP, women streamers) | – | – | – | ✓ | ✓ |
| 18:10 | best fresh paid clip | ✓ | ✓ | ✓ | ✓ | ✓ |
| 20:10 | fresh paid clip | ✓ | ✓ | – | – | ✓ |
| totals | | 3 | 4 | 4 | 3 | 4 |

- Why: TikTok throttled our new account after ~13 posts on day one (1–3/day is the safe range). Instagram, YouTube (since 10/1/2026) and Facebook all cut reach for accounts that mostly re-post clips with only crops/captions, so fewer posts plus more original editing beats volume. Details and sources: Platform Playbook.
- Exceptions: SEGA #Ad keeps TikTok+IG+YouTube. A Part 1 and Part 2 go on the same platforms (18:10 + 20:10 or 11:10 + 18:10). Speed: YouTube only until TikTok reach recovers.
- Rotation: never the same streamer back-to-back (except P1→P2); max 2/streamer/day. Paid clips get 11:10, 18:10, 20:10; fresh clips (moment < 36 h) get 18:10/20:10 first.
- Part 1 / Part 2: same `style`, title accent "PART 1"/"PART 2", caption "(Part 1)"/"(Part 2)". Part 2 goes 2–6 h after Part 1 on the same platforms. No "Part 2 is up" pins or comments.
- Shared schedule doc on the PC: Documents/Side Business/Posting Schedule 11-18.md (every chat reads/updates it, never overwrite — see rule 9).

## X (@tonyandminions) — native posting (set up 11-19)
- Metricool's X add-on costs $10/month, so we don't use it. X's own composer can schedule posts on the free account.
- Make the video: `scripts/make_x_copy.sh <run-N/NAME/NAME_HQ.mp4>` → `/mnt/user-data/uploads/xposts/x/NAME_X.mp4` (720x1280, under 3.6 MB; Claude in Chrome's file_upload caps at 3.8 MB).
- Schedule it (Claude in Chrome, x.com/home):
  1. `find` the home composer's file-input and run `file_upload` to it.
  2. Click the "What's happening?" box and type the caption.
  3. JS-click the visible `[aria-label="Schedule post"]`, then set Day/Hour/Minute/AM-PM with `form_input` and click Confirm.
  4. JS-click `[data-testid="tweetButtonInline"]` (it reads "Schedule").
  5. Check x.com/compose/post/unsent/scheduled.
- Captions: first line = streamer + the moment, 1–2 hashtags (#Streamer #GTA6), **no links** (X suppresses links on free accounts; that includes twitch.tv), no "follow for part 2".
- Limits: free accounts get 50 posts + 200 replies a day, in half-hour windows. We post 4 a day. No mass follow/unfollow.
- A moment already on TT/IG/YT/FB can go on X once. Proven winners go first. Record it in `posted_sources.json` as `"x": "YYYY-MM-DD HH:MM"` and on the queue item as `x_slot`.
- Paid on X: LACY and Clix campaigns accept X — the X account is linked in Content Rewards (11-19). Submit X links on their own via "Paste a link". KreekCraft and Clix x JBL do NOT pay on X.

## Per-view campaigns (joined 11-19) — pay from the first eligible view, no pool minimum
Rules files on the PC: `Projects/2026/2026 11 NOV/<MM-DD Campaign>/01 Working Files/<Campaign> Rules.md` (KreekCraft, Clix x JBL, AsianJeff, Bobby VanRiper).

**KreekCraft GTA 6** — Content Rewards `2eaa14fb-6927-4136-897e-b096e0d907d6`. $1/1K, $3 minimum per clip (3K views), max $300/clip.
- Source: KreekCraft's own GTA 6 streams/replays only (twitch.tv/kreekcraft). Hook in the first 1–2 s, original edits only.
- **Official logo on the whole clip** — every KreekCraft job needs:
  `"overlay": {"url": "https://crusercontent.com/organizations/43893b4f-434d-549b-9037-4f1c62984ff2/campaigns/references/assets/a6688393-4374-492e-8ec3-059554a1870f.webp", "w": 640, "x": "(main_w-overlay_w)/2", "y": "1490"}`
  and `"style"` 0, 3, 4 or 7 (cam on top) so the logo sits at the bottom of the gameplay band, clear of platform UI.
- **Caption must include** `Watch KreekCraft on YouTube and Twitch` + `#GTA6 #KreekCraft #GrandTheftAutoVI`. **No links at all** (not even twitch.tv).
- Platforms: **TikTok, Instagram, YouTube only** — use the 11:10 slot without X, or 18:10 / 20:10 without FB and X. Never Facebook or X.
- Audience 40% Tier 1, engagement 0.8%+, likes visible. Same clip max 5 posts; keep public 30 days.
- Skip: sexual/suggestive bits (shoe-store ranking, nightclub "about to get banned"), slurs, crude humor.
- Queue item: `"campaign": "KreekCraft"`, streamer `kreekcraft`.

**Clix x JBL** — Content Rewards `07b7f0ce-ca55-4a2f-9e91-0d57ca6d72c5`. LOW PRIORITY (pays only from 10K views/clip). Event footage found 11-19: in-store JBL Quantum event in Miami, Clix VOD 2932204601 Just Chatting block ~36178–48000 s (JBL Quantum backdrop + JBL headsets visible). Build only a standout moment (big reaction, Clix the focus, fans/minors not the focus). GTA 6 footage does not qualify. When we do build: JBL logo overlay (`"overlay": {"url": "https://drive.google.com/file/d/1xi8baBvFsHzt4MbR4zpza2aL4ETRX9LJ/view", ...}`) for the whole clip + `#Clix` in the caption, TT/IG/YT. One clip = one campaign — never submit a clip to both this and the Clix pool.

**AsianJeff GTA 6** (Reach, joined 11-19) — Content Rewards `bbd3a963-9a23-457c-bc15-6697971d9902`. $1/1K, **$10 minimum = 10K views per clip** before it pays, max $300/clip, budget $2,500, ends 11/26. Rules: reachclipping.com/AsianJeff.
- Source: his GTA 6 playthrough **from Nov 19 on** (twitch.tv/asianjeff; first GTA 6 VOD `2933231152`, started 11/18 11:49 PM ET, gameplay from ~660 s). Older streams don't count. He's the main focus.
- **Caption must include `#AsianJeff`.** English. Never negative framing, no hate-farm / rage-bait captions, **no logos of any kind** (no overlay).
- Platforms: TikTok, Instagram, YouTube **and X** (all four pay). Never Facebook. Audience 50%+ US/CA/UK/AU/NZ.
- Many of his top Twitch clips are portrait (vertical) clips — use the VOD route (`vod` + `vod_start`/`vod_end`) for those. Cam (most of 11/19): `0,316,588,338` camfit false, game `600,170,1300,731`; smaller cam later in the stream (`0,326,484,358`, game `560,140,1300,731`) — check the probe sheet.
- Queue item: `"campaign": "AsianJeff"`, streamer `asianjeff`. Reach rule: one strike (botting/AI content) bans you from every Reach campaign.

**Bobby VanRiper GTA VI** (Clipping Nation, joined 11-19) — Content Rewards `f583b069-ced7-49e5-9ed3-2d3a13d6df0c`. $1.50/1K, **1,500 views minimum** per clip, max $150/clip, ~$973 left. Rules: Notion "Bobby Van Riper GTA VI Clipping: Requirements & Guide". LOW PRIORITY — small streamer (600 followers), first probe (5 clips) had nothing usable.
- Source: his GTA VI streams/videos only (twitch.tv/bobby_vanriper). He must be in the clip.
- **Caption: `#bobbyvanriper` + show `twitch.tv/bobby_vanriper` on screen or in the caption**, plus a CTA naming him ("follow Bobby Vanriper on Twitch"). English. Overlay optional.
- Platforms: TikTok, Instagram, YouTube only. Likes visible, keep up 30 days, 1% engagement, no AI content.
- **Payout needs Justin:** join the Clipping Nation Discord, and once a clip passes 1,500 views open a "Submit Demographics" ticket with a screen recording of the post's country breakdown (40%+ Tier 1).
- Cam: top-left `0,300,400,288` area (check the probe sheet), under his "SUB COUNT" label.

**Checked and skipped (11-19):**
- Lauren Hamden GTA 6 — needs a dedicated Lauren-branded account + her bio link, 10K/clip minimum.
- BenDaDonnn x Puffco — clips must show him using Puffco (cannabis vape) products: wrong fit for our accounts and against TikTok/IG ad rules.
- TOMO GTA VI — already joined earlier, but the budget is 98% spent ($21 left). Don't build.
- Boeshi, DiegoLoveless — not playing GTA 6 in their recent streams (Just Chatting / Marvel Rivals). Recheck if they switch.
- Dylan Page GTA VI Marathon ($5K, $1/1K, 10K/clip) — source is a YouTube live marathon; our pipeline has never pulled from YouTube on GitHub Actions. Revisit if a YouTube test works.
- Dasgasd3m x RUCKUS ($2/1K, TikTok + YT, "GTA 6-specific accounts") — streams outside Twitch; brief not checked yet.
- GATTOUZ x 1WIN — gambling sponsor. Never.

## Ready queue (queue.json)
Clip Finder appends finished clips; Scheduler pops them into open slots. Each item:
`{"name","streamer","campaign":"LACY|Clix|JasonTheWeen|YourRAGE|KreekCraft|growth","media":"https://raw.githubusercontent.com/tonyandminions/clip-factory/out/run-N/NAME/NAME_HQ.mp4","caption","yt_title","cover_ms","part":null|{"series","n"},"vod","start","end","clip","status":"ready|scheduled","slot":null,"added"}`
- Part 2 is never scheduled before its Part 1. Same series = same style.
- Metricool payload: providers = the slot's platforms from the grid (not all four); include networkData only for those providers; youtubeData short/GAMING/madeForKids false; facebookData REEL; instagramData REEL (TRIAL_REEL for BP growth tests); paid captions must include the streamer name + hashtag (#LACY, #Clix, #JasonTheWeen, #YourRAGE); KreekCraft captions need the exact line in "Per-view campaigns".

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

## Growth best practices (profiles + every post, set up 11-18)
- **Profiles (keep them matching):** TikTok + IG bio "Daily GTA 6 streamer clips 🎮 / LACY • Burnt Peanut • Clix & more 👀"; FB Page bio says the same. YouTube channel description is a keyword paragraph (GTA 6, Grand Theft Auto VI, Vice City, Lucia, streamer names). Justin does NOT want "Part 2s on our page" (or similar plugs) in bios.
- **Pins:** TikTok pins = LACY "can't steal cars" (247 views) + BP "vs traffic" (223). When a newer clip clearly beats them, re-pin it: TikTok Studio → Posts → ⋯ → Pin to top (max 3).
- **YouTube playlists:** one per streamer, "<Name> GTA 6 Moments" (LACY, Burnt Peanut, Speed so far). The Engagement Crew adds new public Shorts and creates a playlist when a new streamer gets their first Short. Never add #Ad/SEGA posts.
- **Captions:** first line = streamer + what happens (works as a search hook), one emoji, 2–4 specific hashtags (#streamer #gta6 + one topical). No links, no "follow for part 2" bait.
- **No first comments.** We don't comment on our own posts — Justin finds it cheesy (decided 11-19). Leave `firstCommentText` empty everywhere. Real viewer comments are handled by the Engagement Crew.
- **Covers:** `cover_ms` on the clearest reaction frame with the title band readable; never a sexualized frame.
- **Reply window:** the first hour after posting decides reach. Engagement Crew (2:23, 7:23, 9:23 PM ET) likes and replies to real comments; skips trolls/spam (never deletes, hides or blocks); no DMs; flags brand/streamer/copyright messages to Justin.
