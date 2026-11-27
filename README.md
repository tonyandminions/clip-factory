# clip-factory — Tony & Minions

> **⛔ INSTAGRAM IS GONE (11-19, 9:51 PM ET).** Meta permanently disabled @tonyandminions after review ("doesn't follow our Community Standards"). Until Justin says otherwise: no crew member posts, schedules, stories, submits, replies or logs in to Instagram. Scheduler: drop "instagram" from every scheduled Metricool post (updateScheduledPost, full payload; never delete) and from IG stories (Story Crew: Facebook stories only). Submitter/Live Hunter: never submit Instagram. Analyst: drop Instagram from the numbers. **Do NOT create a new Instagram account** — that counts as evading enforcement under Meta's rules and can take the Facebook Page down with it. Facebook is the same company, so treat it gently until Justin decides (see STATUS).


> **⛔ NO BROWSER AUTOMATION ON PLATFORM SITES (11-20, Justin: "read fully through the terms for each platform and do not violate them").** Every platform's terms ban bots and AI agents clicking or typing on their sites outside the official API. This beats every task prompt: if your prompt tells you to use Claude in Chrome on any site in rule T below, skip that step and tell Justin which step you skipped. See rule T.

## READ FIRST — hard rules (every chat and scheduled task)
**Strategy source of truth:** `Documents\Side Business\Platform Playbook.md` on the PC (per-platform caps, slot grid, originality rules, 2026 research + sources). The schedule lives in `Posting Schedule 11-18.md` next to it.

T. **TERMS OF SERVICE FIRST (Justin 11-20; Phillip flagged it in Discord). Beats every other rule, section and task prompt.**
   - **What the terms say (read 11-20):**
     - X: never "use non-API-based forms of automation, such as scripting the X website" — it "may result in the permanent suspension of your account". Also no automated likes.
     - YouTube: you may not "access the Service using any automated means (such as robots, botnets or scrapers)" without YouTube's prior written permission. Downloading is also limited to what the Service itself allows.
     - TikTok: no extracting data or content "using any automated system or software, including automated bots, except as approved in writing".
     - Meta/Facebook (Terms 3.2.3): you "may not access or collect data from our Products using automated means (without our prior permission)", "regardless of whether such automated access or collection is undertaken while logged-in".
     - Discord: "Automating normal user accounts (generally called self-bots) outside of the OAuth2/bot API is forbidden, and can result in an account termination".
     - Twitch: no accessing its services "by means of any robot, spider, scraper, crawler, or other automated means", and no "downloading (except page caching)".
     - Fiverr: no "using any automated system, including robots, spiders, offline readers".
     - Whop (Content Rewards runs on it): no "using bots, scrapers, crawlers, or other automated tools to access or collect data". Content Rewards' own clipper terms also make us promise every post follows the platform's terms. Treat Content Rewards as no-automation until Justin confirms otherwise.
   - **Allowed tools:**
     - Metricool (official APIs) for posting, scheduling, Facebook stories and analytics;
     - GitHub (our repos, and Actions that edit footage we already have);
     - the vidIQ connector (YouTube's official API) - **Justin cancelled vidIQ 11-24; it won't renew. ~660 credits stay usable until ~Dec 20, then it's gone.** Only use left: the Live Clipper's Speed live check (5 credits). Don't spend vidIQ credits on anything else without asking Justin;
     - **the ClipSpeed connector (ClipSpeed's official MCP server, api.clipspeed.ai/mcp, Justin connected it 11-24).** ClipSpeed publishes it for AI agents; its terms only ban automated tools that "abuse, scrape, or overload the Service". ClipSpeed fetches the stream on its own servers, so live clipping through it is not us touching Twitch. Use: `clip_livestream`, `check_livestream`, `stop_livestream`, `check_clips`, `get_account`. NEVER its `publish_to_youtube`/`schedule_post` (posting stays on Metricool) and never its paid AI creation tools (generate_*, *_ad, influencer, morphaze) without Justin's OK;
     - the Twitch Helix API with our own app keys (`fresh.yml`, from 11-24);
     - Claude Docs/Drive, the PC files, and messages/push to Justin.
   - **Never use Claude in Chrome or scripts, not even read-only, on:** x.com, tiktok.com (incl. TikTok Studio), youtube.com / studio.youtube.com, facebook.com / Meta Business Suite, instagram.com, discord.com, twitch.tv / gql.twitch.tv, fiverr.com, contentrewards.com / whop.com, clipspeed.ai (the website; the ClipSpeed **connector** is allowed).
   - **Paused until Justin decides:**
     - **Clip sourcing:** no new jobs that fetch from Twitch or YouTube (GQL queries, VOD/clip downloads, `scan`, `record`, `live`, `url` routes); build only from footage already on the out branch or files Justin provides.
     - **X posting:** Justin posts by hand, or we turn on Metricool's X add-on.
     - **Discord updates:** need a webhook or bot account; until then everything goes to Justin as a message.
     - **Content Rewards:** Justin submits by hand from the Submitter's reminder.
     - **Comment replies:** YouTube only, through the vidIQ API, and only if it's connected to our channel; the rest Justin answers.
     - **Account health checks:** Justin checks by hand, or a Gmail connector reads the warning emails.
     - **Fiverr:** Justin works his inbox and orders in the app; we build order clips only from links he gives us.
   - **Allowed replacements (found 11-20; each one goes live when Justin connects it):**
     - **Discord updates:** official webhook through the PRIVATE repo's `notify` workflow: `gh workflow run notify.yml -R tonyandminions/flyte-orders -f text="..."`. Works once Justin adds the secret `DISCORD_WEBHOOK_GENERAL`.
     - **X posting and X numbers:** Metricool's X add-on ($10/mo; then the Scheduler posts X like the other platforms), or the Typefully connector.
     - **YouTube comments and stats:** vidIQ connector (official YouTube API). Needs Justin to link the channel; then replies use `vidiq_reply_to_comment`.
     - **Facebook, TikTok and YouTube comments:** Windsor.ai for Social Media connector (official APIs), optional.
     - **Platform warnings and Fiverr messages:** Gmail connector on tony.and.minions@gmail.com (reads warning and notification emails through Google's API).
     - **Fiverr gig live/reviews:** Fiverr connector (official, public seller data).
     - **Twitch who's-live and top clips:** Twitch's official API (free developer app; Client ID + secret as GitHub secrets). Clip downloads through the official API only work for the streamer or their editors.
     - **Content Rewards:** no confirmed clipper API, so Justin submits from the Submitter's reminder.
   - Posts already scheduled inside X's, TikTok's or YouTube's own schedulers publish on their own: leave them, and don't open those sites to check.
0. **ACCOUNT SAFETY FIRST (Justin 11-19, after Instagram was banned: "make sure this doesn't happen again"). These limits beat every other number in this README, the Playbook and any task prompt.** All our accounts are brand new, and new accounts that post a lot of other people's footage with bot-like activity get throttled (TikTok, day 1) or banned (Instagram, day 2).
   - **Ramp, don't blast.** Until **Dec 3** (first 2 weeks): max **2 posts a day** on YouTube, Facebook and X, and on TikTok **2** from 11-25 (Justin: "tiktok 2", after two organic posts in a row reached For You 0.94 and 0.99; it was 1 while throttled). TikTok posts stay 3+ h apart and still only take clips that fit the TikTok rules (mechanic clip with explainer card, or Speed action). If two organic TikToks in a row fall under For You 0.6, go back to 1 and tell Justin. Task prompts that still say "TikTok 1" are out of date; this line wins. Then +1 per platform per week, only while that platform's health is clean, up to the normal caps. Live Hunter fast-lane posts count.
   - **Spacing:** at least **3 hours** between posts on the same platform. Never two posts of the same streamer in a row on one platform.
   - **Stories:** Facebook only, max **2 a day**, until Dec 3.
   - **Engagement:** **no automated likes** at all. Replies only to real viewer comments, max **5 per platform per run**, spaced out (at least a minute apart), never copy-paste the same reply. **No replies on Facebook until Nov 27.** No follows, no DMs, ever.
   - **Every clip must be clearly ours:** title band + real edit + context line + hand-checked captions + caption in our words (originality checklist). Credit the streamer. No raw re-uploads, no duplicates (one upload per moment per platform, ever), skip clips with copyrighted music playing, skip anything a platform could read as sexual, violent-real-world, or hateful. **(11-21: TikTok restricted an in-game Lucia scene for 'Body Exposure and Sexualized Behaviors' — revealing in-game outfits, swimwear and club-dancing scenes count too. And it called 3 of our launch-day edits 'Unoriginal' even with title band + captions: TikTok posts need a voice line, an explainer edit or a multi-streamer story on top — platform_strategy tiktok.restricted_posts.)**
   - **Daily account health check (Ops Lead, every morning):** TikTok Studio (account status / violations), YouTube Studio (channel violations, "Potential limitation", copyright claims), Facebook (Page "Account status" / Support Inbox), X (notices, locked features), plus the tony.and.minions@gmail.com inbox for warnings from any platform. **Any warning, strike, claim or restriction = that platform pauses ALL posting for 48 h** (Scheduler moves its posts, never deletes) and Justin gets told right away (push + Discord #general).
   - **Never** log in/out repeatedly, change account settings, or connect new apps to an account without Justin. **Never** create a new account to replace a banned or limited one.
   - **Facebook is our only Meta account now — protect it (Justin 11-20: "make sure we don't get banned from there").** Page: Tony & Minions, `facebook.com/profile.php?id=61596397363823`. Status on 11-20: no violations, no restrictions, Recommendations active, Monetization not eligible.
     - **Daily check (Ops Lead):** `facebook.com/page_status/61596397363823` must say "Page has no issues" with Recommendations "Active". Anything else (violation, restriction, "not recommendable", a muted/blocked/removed reel, any IP or copyright notice) = the 48 h pause above + tell Justin.
     - **No engagement bait** in captions, stories or replies: no "like if…", "share this", "tag a friend", "comment X", "follow for Part 2". Facebook demotes posts and whole Pages that ask for engagement. Max 3 hashtags.
     - **Credit every clip** (streamer name + #Name in the caption) and keep the originality checklist. Meta pushes down reposts with only small edits (borders, captions, speed) and can mark repeat offenders non-recommendable.
     - **Copyright:** skip clips with music playing (Facebook matches audio). Never dispute a claim, never re-upload a removed reel. Repeated IP violations can get the whole Page taken down.
     - **Never** share our posts into Groups, cross-post to other Pages, create another Page or profile, boost or run ads, or use "Boost Instagram post". Never touch Meta Accounts Center, Page access/admins, Page name/username or linked accounts — Justin only.
     - **Moderation Assist is ON** (auto-hides comments with links, profanity, or from accounts with no friends/followers). Leave it on; the Engagement Crew may unhide a real viewer's comment by hand.
     - Facebook pays $0 on Content Rewards: a paid clip must also go on at least one paying platform (TikTok, YouTube, X) — Facebook alone is growth only.
1. **No reposts.** Check `posted_sources.json` with `scripts/dedupe_check.py` before building or scheduling; register every clip you schedule. "rejected" entries are banned forever.
2. **QUALITY GATE (Justin 11-25: "make sure clips make sense and are funny or tell something to the viewer. We need success"). Beats every slot, cap-filling and schedule rule: an empty slot is better than a weak clip.** Before a clip is built, queued or scheduled, all 6 must be a clear yes. If you have to argue for one, it's a no.
   1. **Point.** One sentence says why a stranger would care, and it is one of: **funny** (name the joke), **tip** (the true GTA 6 fact the clip shows), **wow** (the event: chase, crash, fight, rare find). Save it in queue.json as `"point": {"type": "funny|tip|wow", "line": "..."}`. Can't write the line = skip the clip.
   2. **Stands alone.** Someone who has never seen this streamer or stream gets it with zero context. No reactions to things that are off screen or cut out, no "like I said", no inside jokes with chat.
   3. **Setup + payoff inside the clip.** The punchline / fail / discovery lands on screen, and the clip ends within ~1.5 s after it. Never end mid-sentence. No "Part 1" that stops before the payoff (YouTube: payoff clip only, see `platform_strategy.json` youtube.avoid).
   4. **Hook.** Action or the best line inside the first 1.5 s (cut walk-ups, loading, talking with `segments`). The title band says what is about to happen. 12-30 s total.
   5. **Captions read like real sentences.** `"captions": "auto"` is probe-only (the build refuses it). Probe, read transcript.txt and caps_review.txt (words Whisper wasn't sure of), fix the words, pass the list. A line you can't make out gets no caption - never a guess. Read the finished captions top to bottom once: if they don't tell the story, fix or skip.
   6. **Title + caption name the thing that happens** and match what's shown. Not a non-event ("trying to", "can't", "first seconds", "playing GTA 6"). **The title band tells the whole story in one sentence** - who, what happened, and the surprising GTA 6 part - so a viewer with the sound off already wants the payoff (Justin's example 11-25, 150.7K likes on another channel: "Kai Cenat was SHOCKED that NPCs he FOUGHT earlier REMEMBERED him & tried to JUMP him in GTA 6"; ours were labels like "MissMikkaa found a tracker"). Use the lines the band fits, accent the 2-3 words that carry the story. Justin 11-25: "you guys are just posting streamers and they do nothing, and then nothing happens in the video" - if you can't write that sentence, nothing happens in the clip: skip it. Don't start every title with "<Name> Found Out You Can": for big names (Speed, LACY) lead with the name + event; for smaller streamers lead with the GTA 6 fact or event.
   **Order of use (Scheduler, Live Clipper):** rank ready clips by (a) passes the gate, (b) paid streamer or Speed, (c) point type the platform wants (YouTube: wow from a big name; TikTok: tip with explainer; Facebook: funny/wow), (d) freshest. Run `python3 scripts/quality_gate.py` before scheduling; never schedule an item it fails. Also: best line in the first second, cut dead air with `segments`. Every build now writes `gate.txt` next to the clip on the out branch (slow open, length, ends mid-sentence, long tail, dead air): read it, and fix or have a reason for every WARN before scheduling.
3. **Per-platform caps (from Fri 11/20, Justin 11-19 "do what's right for each one").** TikTok 3 · Instagram 4 · YouTube 4 · Facebook 3 · X 4 per day, counting every post incl. native Speed ones. Each slot only goes to its platforms (grid below) — set Metricool `providers` per post, never all four by default. **A queue item with a `"platforms"` list (per-view campaigns: KreekCraft, AsianJeff, Bobby VanRiper) only goes to the slot's platforms that are also in its list** — e.g. AsianJeff in the 18:10 slot = TikTok, Instagram, YouTube, X (no Facebook). Paid clips only in :10 slots. Stories separate: 6/day, 40+ min apart.
4. **Variety.** Never the same streamer twice in a row; max 2 per streamer per day; Part 2 never before Part 1.
5. **Safety + cleanup (Justin 11-24: "we could use some of the inappropriate content if we blur... or no bleeps just cut audio").** A strong moment with a problem in it can be fixed instead of thrown away:
   - **Swears:** `"mute": "auto"` silences every swear Whisper finds (no bleep tone, just a short silent gap; mild words damn/goddamn stay). Add `[[s,e],...]` windows for anything Whisper missed - listen against ClipSpeed's captions too. Captions never show the word (transcribe.py drops swears; write manual captions without it). A muted swear may be the hook.
   - **Slurs:** never mute-and-post a slur - viewers can read lips and the platforms' hate-speech checks still flag it. CUT the whole line out with `segments`; if the moment doesn't work without it, skip the clip. The build FAILS if Whisper finds a slur in the finished clip (SLUR_FOUND.txt). Whisper can mishear slurs (11-24: the N-word came out as "going to wank it"), so always compare with ClipSpeed's captions or the contact sheet before building.
   - **Revealing in-game outfits / suggestive shots:** `"blur": [{"t0","t1","x","y","w","h"}]` (finished 1080x1920 frame) on that part, YouTube and Facebook only. Never TikTok (TikTok already flagged "Body Exposure" on 11-21).
   - **Still always skip:** nudity, sexual acts/jokes as the point of the clip, crude humor as the point, copyrighted music, cutscene-only clips, stream business (sub/donation reading - cut it out with `segments`).
   No bots, no passwords, never join campaigns without Justin.
6. **Credits.** ClipSpeed Starter = 300 credits a month (renews the 18th, ~36 credits per hour live). Since 11-19 (Justin: viral moments need to be found and posted within minutes) the **Live Hunter** uses it on whichever PAID streamer is live on GTA 6 and hottest right now, not only YourRAGE. Max 45 min per session; at most 1 session a day while under 150 credits (2 a day above that); always keep 30 in reserve; never its Generate/AI tools. Free sources first for everything else: Twitch clips, `scan` (chat-aware, also works on a VOD that's still live), `record`. Don't spend vidIQ or Metricool AI credits.
7. **Git.** `git pull --rebase` before every push; retry on conflict. Job files in `jobs/` trigger builds — never move or rewrite old ones.
8. **Chrome.** Close every tab you open. Never click Delete on posts (ask Justin).
9. **PC files — never overwrite (Justin, 11-19).** Before changing any file in `Documents\Side Business`: stage the CURRENT file fresh, copy it into `Side Business\03 Versions\<file name>\<file name>_Vers-NN` (next number), make your change on top of it keeping every other section/row (other chats edit these files too), write it to a NEW filename in outputs, commit with `expectedMtimeMs` from the stage (changed? re-stage and merge — never force), check the byte size.
10. **Paid submissions** within 30 min of posting (Submitter task runs at :18 after each :10 slot). Content Rewards auto-detects TikTok + Instagram cards only: tick them and submit first (pasting a link switches the dialog to single-link mode), then reopen Submit clip, paste the YouTube Shorts link, tick the box and submit it on its own.
11. **Log everything.** After any change (posts scheduled/moved, submissions, PC files, queue), append one line to `Side Business\Logs\Activity Log YYYY-MM.md`: `- YYYY-MM-DD HH:MM ET · <who> · <what> · <files/posts>`. Append only — never edit or delete earlier lines.
12. **Each platform is its own game (Justin 11-19: learn after every post, adjust per platform until it's mastered).** `platform_strategy.json` holds what works and what to avoid on TikTok, Instagram, Facebook, YouTube and X, with each platform's health metric and current experiment. Analyst: update it every night from the numbers. Scheduler: route clips by it (which clip goes to which platform; a slot may carry two clips split by platform; caps still hold). Clip Finder: hunt for what it says each platform wants. See "Per-platform learning loop" below.


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

## Per-platform learning loop (from 11-19)
- **Quality (11-24, Justin: "make sure all the videos are high res as much as possible").** build_split now keeps 60 fps when the source has it, scales with lanczos, lightly sharpens the upscaled facecam, and encodes slow/CRF 16; later passes (explainer, logo, blur) re-encode at CRF 14. `"yt1440": true` also writes NAME_YT1440.mp4 (1440x2560) for Justin's direct YouTube uploads. The facecam is still the softest part: it's a small corner of the stream blown up - prefer streams/clips at 1080p and avoid zooming the cam crop tighter than needed.
- **YouTube direct-upload test (11-24..11-26, Justin: "let's just try doing the fix now").** Every Metricool-uploaded Short since 11-19 got 0-79 views (newest 0-4, JasonTheWeen 0 after 8 h = not shown at all); all 3 YouTube hits (Speed P2 22,327, Speed download 1,409, LACY Lucia 222) were uploaded straight to YouTube. Test: one Short a day goes up from Justin's YouTube app instead of Metricool (11-24 LACY stray dog 6:10 PM - YouTube removed from the Metricool post; 11-25 + 11-26 handled by scheduled check-ins at 5:45 PM). Day 1: LACY stray dog uploaded directly 11-24 ~6:14 PM -> https://youtube.com/shorts/urAJKiWZRmo (video id urAJKiWZRmo); Justin also posted it to TikTok directly (https://www.tiktok.com/t/ZPNSBghSM/), so that day's Metricool TikTok (Burnt Peanut sell stolen cars) moved to 11-26 18:10 to keep TikTok at 1/day. Day 2 (11-25): AJ_NotScared sent to Justin at 5:46 PM as a 1440p file for a ~6:10 PM direct upload; its Metricool post was YouTube-only, so it was set to draft (not deleted) instead of having YouTube removed. Justin skipped it 11-26 ("I don't think he performs very well"), so day 2 has NO direct upload: the verdict compares day 1 (LACY stray dog) and day 3 only. Day 3 (11-26): CLIX_HouseRobbery sent to Justin at 5:46 PM as a 1440p file for a ~6:10 PM direct upload (Metricool YouTube-only post set to draft). **Verdict 11-26: not callable yet** - Metricool's YTVV data stopped at 11-22, so the direct uploads (urAJKiWZRmo and later) are not in it; asked Justin for the view counts from the YouTube app. Metricool-uploaded Shorts 11-20..11-22 for comparison: 4, 49, 1 views. **TEST ENDED 11-27 (Justin: "let's do the scheduler for YouTube again, I don't have time right now to post manually"). YouTube is back on Metricool for every Short; no more files or upload reminders to Justin.** Result: the one direct upload (LACY stray dog) has 4 views after 3 days, the same as Metricool uploads (0-4), so the upload method is not the cause; the channel itself is not being shown (see platform_strategy youtube.status). Clix house robbery was never uploaded by hand (not on the channel 11-27) -> its Metricool post is live again for 11-29 16:10. (Old plan: Compare after 48 h. If direct uploads clearly win, YouTube becomes a once-a-day upload Justin does from his phone (crew pushes him the file + title) and Metricool keeps the other platforms.
- **YouTube per-Short numbers (11-24):** Metricool's "all videos" connector works: metrics YTVV02 (date), YTVV17 (title), YTVV06 (views), YTVV08 (avg view s), YTVV09 (likes), YTVV05 (url); traffic sources YTTS01/YTTS02. The "published in range" YTVP fields came back null - don't rely on them. vidIQ (live YouTube numbers) needs Justin to connect the channel.
- **Every night (Analyst):** pull per-post numbers for each platform (Metricool: TikTok TKPO07 views / TKPO15 avg watch / TKPO16 For You share; Instagram IGRE23 views / IGRE30 skip rate / IGRE21 shares / IGRE24 avg watch; Facebook FBRE10 views / FBRE13 avg watch; YouTube from YouTube Studio views + "Potential limitation" labels, because Metricool's YouTube numbers lag ~2 days; X from the profile). Tag each post with streamer, hook_type, length, slot and caption style. For every platform: compare against its baseline, update `what_works` / `avoid` / `route` / `status` in `platform_strategy.json` with dated evidence, and move its `experiment` forward (one change at a time, decide after the sample size in the plan, keep the winner as the new rule, start the next test). Small samples stay marked as small.
- **Health first:** if a platform's health metric goes bad (TikTok For You under 0.3, Instagram skip rate over 45% on most Reels, a YouTube "Potential limitation", Facebook views dropping by half for 3 days), cut that platform to its throttled amount and tell Justin in the nightly summary.
- **Scheduler:** for each slot, pick per platform the clip that best fits that platform's `route` (hook type, length, streamer); split a slot into two posts by platform when that fits better. Never break caps, rotation or campaign platform rules.
- **Clip Finder:** each run, read `platform_strategy.json` and favour moments that match what the strongest platforms want (and what a throttled platform needs to recover).
- **Weekly (Sunday Analyst):** one line per platform in Platform Playbook.md ("Platform scorecard"), what changed this week and why.

## What performs (update as numbers come in)

**YouTube flop review 11-24:** 13 of 19 Shorts got under 15 views. Flops share: a Part 1 with no payoff, a title where nothing happens ('can't', 'trying to', 'first seconds'), a small streamer, a duplicate upload, or a slow first second. YouTube gets the payoff clip only, big name, event in the title, action in second 1. Flops stay up: never delete (see `youtube.flop_rule`).
- **11-24 (main chat, Justin: "KreekCraft doesn't perform, Burnt Peanut and Speed do").** Data agrees: KreekCraft best 101 views (TikTok, 11-19 mom), croc bet 2/1, and his campaign needs 3K per clip and bans Facebook, so he can't use our best platform -> fresh weight 1.3 -> 0.6; post the 2 ready KreekCraft clips (CCTV_v2, TowerEasterEgg_v2) only when nothing stronger is ready, and build new KreekCraft only for an exceptional mechanic moment. Burnt Peanut 'vs GTA 6 traffic' 1,316 IG / 226 TT on launch day -> fresh weight 0.8 -> 1.1 (growth: Facebook 15:10 slot first). Speed: best YouTube Short (download 1,406) + organic For You 1.0 on scooter P2 - handled by the Speed chat, not the Twitch scan. Money still comes from LACY/Clix/YourRAGE/JasonTheWeen pools (TikTok/YouTube/X views), so keep them on the paying platforms.
- **11-26 night (Analyst, ~23:25 ET).** Source: Metricool + vidIQ channel totals (rule T); TikTok/FB through 11-25, YouTube through 11-24. PC folder connected: tracker views + Activity Log written.
  - Best: realkatieb FB 1,637 still #1; best new growth = LACY stray dog FB **323 -> 1,115** at ~76 h (FB Reels keep growing for 3 days: judge them at 72 h).
  - TikTok healthy-recovering: **3 organic For You hits in a row** (Speed P2 0.995, AJ_Plane 0.88 at 197, MissMikkaa tracker 0.88 at 112). Tip-first caption + explainer card works. Cap 2 holds.
  - Facebook: watch cleared (no 3-day halving), but 3rd dead Reel (BP tolls 3 views, posted 23:10) -> no FB Reels after 20:00; Justin checks page_status. Followers 1.
  - **YouTube THROTTLED:** +25 channel views in 2 days (vidIQ 24,155 -> 24,180); every Short since 11-22 1-4 views, the direct upload too (LACY stray dog 4). Recommend 2 -> 1 Short/day + Justin checks YouTube Studio. Subs 17 flat.
  - Caption split test: 3 tagged posted clips (Tracker_v2 phrase, CLIX_HouseRobbery word, KREEK_MomGTA6 word) - too few. AsianJeff ended 11/26 at 197 / 10K; KreekCraft best 112 / 3K; $0.
  - Change: platform_strategy youtube status -> throttled, facebook watch -> healthy (72 h rule), tiktok healthy-recovering; LACY fresh weight 1.3 -> 1.4.
- **11-25 night (Analyst, ~23:30 ET).** Source: Metricool only (rule T); TikTok through 11-23, FB through 11-24, YouTube through 11-22. PC folder connected: tracker views + Activity Log written.
  - Best: Speed scooter P2 still compounding (TikTok 615 -> 800; YouTube 22,327). Best new: AJ_Plane TikTok 105 -> **194**, For You held **0.90** (tip line + explainer card).
  - TikTok: recovering, cap 2. Next check = LACY stray dog (11-24 native) + MissMikkaa tracker (11-25) once Metricool has them (two < 0.6 in a row -> back to 1).
  - **Facebook WATCH (day 2 of 3):** 11-23/24 Reels ~200 avg (264 / 1 / 217 / 323) vs ~1,100 for 11-21/22. If 11-25's Reels also stay under ~500 -> throttled (1 Reel/day) + Justin checks page_status. Followers 1.
  - YouTube: nothing new in Metricool; subs 17 flat; direct-upload test is Justin's read. Caption split test: 2 tagged posted clips. AsianJeff plane 194 / 10K (ends 11/26); KreekCraft best 109 / 3K; $0.
  - Change: tiktok.route.caption_rule now leads with a TIP line when the clip shows one; fresh story hook words + self-roast (worst, terrible, so bad, fail).
- **11-24 night (Analyst, ~23:30 ET).** Source: Metricool only (rule T); TikTok/FB through 11-23 ingested, YouTube through 11-22, 11-24 not yet. PC folder connected: tracker views + Activity Log written.
  - Best: realkatieb "worst GTA 6 gameplay" FB **1,633** (was 1,195) = best FB Reel ever, from the 15:10 growth slot. Seaplane P1 1,453 / P2 1,020.
  - TikTok **recovering**: AJ_Plane (explainer card, tip line "hold L2 to land a seaplane") For You **0.94**, 105 views, 8 s avg - 2nd organic For You hit in a row after Speed P2 (0.99, now 615). Recovery rule met -> recommend TikTok 1 -> 2/day (Justin decides; Scheduler not touched).
  - Facebook: MissMikkaa WomanDriver 214 (MissMikkaa stays on FB), but LACY "texting Lucia" **1 view** after ~38 h = 2nd dead Reel -> Justin checks page status; no Lucia-relationship clips on FB until then.
  - YouTube: nothing new from Metricool; subs 17 flat; vidIQ channel now linked but reads cost credits (ask Justin). AsianJeff plane 105 / 10K min (ends 11/26). Caption split test: 2 tagged posted clips. $0.
  - Change: platform_strategy tiktok status throttled -> recovering; realkatieb fresh weight 0.9 -> 1.0.
- **11-23 night (Analyst, ~23:20 ET).** Source: Metricool only (rule T); posts through 11-22 ingested, 11-23 not yet. PC folder not connected -> tracker views + Activity Log line in `docs/pc_pending/2026-11-23_analyst.md`.
  - Best: LACY seaplane PART 1 FB **1,448** (best FB Reel ever); P2 1,017 (70% carry). realkatieb "worst GTA 6 gameplay" FB **1,195** day one - growth slot works. FB Reel views/day 770 -> 1,448 -> 2,212.
  - TikTok: still throttled, no new organic post read (SEGA #Ad 47, paid partnership). Search long tail: YourRAGE teeth 94 -> 142 in a day. AJ_Plane (11-23) decides the recovery check.
  - YouTube: subs **8 -> 17** (+9 on 11-23). Per-Short views in for 11-18..20 only (LACY P2 72). MissMikkaa gains FB still 0 after 4 days.
  - Change: realkatieb fresh weight 0.7 -> 0.9. Caption split test still <10 tagged posts. Campaigns: KreekCraft best 101 / 3K; $0.
- **11-22 night (Analyst + Sunday review, ~23:20 ET).** Source: Metricool only (rule T); posts through 11-21 ingested, 11-22 not yet. PC folder not connected → weekly review + tracker views are in `docs/pc_pending/2026-11-22_analyst.md` for the next run that can reach the PC.
  - Best: LACY seaplane PART 1 FB **1,062** on day one (8 s avg) - best first-day Reel. YourRAGE teeth FB 1,160, LACY missions 769 (11 s).
  - TikTok: **first recovery signal** - Speed P2 (native, not promoted) For You **1.0**, 210 views, 11 s avg. Caveat: it followed the paid P1. Search earners still compounding with no new posts (teeth 53→94, mom 94, LACY P2 294).
  - Facebook: MissMikkaa gains still 0 views after 3 days (others 220+) → Justin check before MissMikkaa 11-23.
  - YouTube subs 8 (+2); per-Short views still null; vidIQ 0 channels. X: not in Metricool, Justin reads it in the app.
  - Caption split test: still 1 tagged posted clip (KreekCraft mom, word). Campaigns: KreekCraft best 94 / 3K; AsianJeff first post 11-23; $0.
- **11-21 night (Analyst, ~23:15 ET).** Source: Metricool only (rule T). No 11-21 post ingested yet; numbers are 11-18 to 11-20 posts.
  - Best: YourRAGE teeth FB **1,156** (8 s avg); LACY "ran out of missions, thought he beat GTA 6" FB **728** with **11 s avg** (best watch time yet). MissMikkaa gains FB shows 0 (lag or not distributed - Justin check).
  - TikTok still throttled: no organic For You >= 0.3 since 11-18 (Speed P1 0.99 = paid). Search earners all read like a typed question: "dying in GTA 6 takes ALL your money" 284, "what GTA 6 is about" 78, "brushing your teeth in GTA 6" 53; "first time"/bet/robbery openers 2-14. → caption_rule tightened.
  - YouTube: Metricool null per Short; subs 6. vidIQ: no channel linked. X: not in Metricool, Justin reads it in the app.
  - Caption split test: 1 posted clip with a tagged capstyle (KreekCraft mom, word) - too few. Campaigns: KreekCraft best 78 / 3K, AsianJeff none posted; $0.
- **11-21 (main chat, learning pass for Justin: "learn and adjust to make everything better").** Source: Metricool traffic sources (TKPO16 For You, TKPO21 search).
  - **TikTok's For You feed shut off after the 11-18 burst** (13 posts in one day). The first 3 posts that day got 77-91% For You; every post since gets ~0%.
  - **Search is TikTok's only working channel:** ~95% of organic views now come from search, and they keep coming for days (LACY P2 "dying takes ALL your money" 284, KreekCraft mom 78, YourRAGE teeth 53). → TikTok gets only mechanic clips with the searchable GTA 6 fact as the first caption line (platform_strategy tiktok.route.caption_rule).
  - **Promote test failed:** Speed P1 45.8K paid views, 5 s avg watch, 0 comments; Part 2 got 210 with no carry-over. Same night a LACY post was rejected for "potential fake engagement". No more Promote while in Reach campaigns.
  - **Facebook is the best platform now:** 200-1,150 views per Reel, 7-11 s avg watch (YourRAGE teeth 1,156, LACY missions 728). Strongest clip of the day goes to Facebook first.
- **11-20 (Analyst, nightly ~23:15 ET).** Source: Metricool only (rule T). Metricool hadn't ingested any 11-20 post yet; numbers below are 11-19 posts.
  - Best: YourRAGE "brushing teeth gives a Focus buff" FB **923** (9 s avg) - a mechanic surprise won on FB, ahead of LACY story Reels 358-596. Clix plane FB 217 (the 0 was lag).
  - TikTok still throttled: For You 0.0-0.018 on all 11-19 posts; KreekCraft mom 55 (best organic), rest 1-11. Promote test (Speed P1 7,089, mostly paid) - organic effect not readable yet.
  - YouTube: Metricool per-Short views null since 11-19; vidIQ has no channel linked. X not in Metricool.
  - Caption split test: too few tagged posts with watch data (<10 of ~40). Campaigns: no clip near a minimum (KreekCraft best 55 / 3K), $0.
- **11-19 (Analyst, nightly ~23:45 ET).** Sources: TikTok Studio, YouTube Studio, x.com, Metricool FB, Content Rewards.
  - Best fresh clip: KreekCraft "viewer's mom asked what GTA 6 is" — IG 336 (before the ban), TikTok 41 (best since the throttle). Funny "explaining GTA 6" story beats plain fails.
  - TikTok still throttled (4 posts today vs ramp cap 1; others 1–5 views). YouTube: 5 new Shorts all 0–2 views; no new "Potential limitation". FB: Clix plane 0 (lag?). X: proven winners 232/72 vs fresh 39/1.
  - Content Rewards: 33 pending, 0 approved/rejected, $0 earned; no KreekCraft clip near its 3K minimum.
- **11-18 launch day (Analyst, nightly 11-18 ~23:15 ET).** Sources: TikTok Studio, Metricool IG, Content Rewards view counts.
  - TikTok: LACY "can't steal cars" 248 (9.6 s avg, **37% finished**, 15 s), BP "vs traffic" 226 (10.4 s, 11%, 30 s). Every evening post (4:45–9 PM) got 0–11 views; Speed "download" 0 views after 4 h.
  - IG: BP traffic 1,316; LACY "lost all his money" PART 2 **1,452** (best clip); LACY clips 130–280; Gator P1 151.
  - Part 1 → Part 2 did not carry viewers (TT 11→5); P2 won on IG as a standalone because its hook is relatable ("dying takes ALL your money").
  - Followers: TikTok 4, IG ~4, YouTube +2, FB 0. Stories: no reply/tap data in Metricool yet.
- Winning hook = a relatable GTA 6 **mechanic surprise/frustration** in second 1 (can't steal cars, traffic, lose all money). 15–21 s clips finish 3x better than 30 s.
- Avoid: slow opens (LACY dog 1.8 s avg), cutscene dialogue, reposting a moment with a new cut (BP traffic went up twice on TikTok 11-18: 6 views, counts as a repost).
- Earlier (11-18, first ~80 min IG): BP "vs GTA 6 traffic" 646 vs LACY 127–277; "<streamer> vs GTA 6 ___" titles work.
- Skip: long cutscene dialogue, map scrolling, real-life just-chatting, anything crude/sexual/drug.

## Fresh pick — one brand-new moment in the best slot every day (route A, Justin 11-20)
Justin: "we need a system to pull something brand new and post it right away for each day, and make sure it's the one most likely to go viral." Route A keeps rule T: bots only use official APIs, and **Justin grabs the video himself**.
1. **Scout (8:44 AM ET, task "T&M Crew — Fresh Pick"):** `gh workflow run fresh.yml` runs `scripts/fresh_scan.py` with Twitch's OFFICIAL Helix API (secrets `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET`, free dev app). It ranks the roster's GTA 6 clips from the last 24 h and writes `fresh/latest.md` + `latest.json` on the `out` branch. No video is downloaded.
   Score (weights in `fresh_config.json`, the Analyst tunes them): views per hour + how many viewers clipped the same moment + hook (mechanic discovery > story/reaction, from our own numbers) + streamer live now + clip length 20–60 s, × campaign weight × freshness. Already-posted moments (`posted_sources.json`) and skip words (nudity, giveaways, music, cutscenes) are dropped.
   The task reads the top 5, drops anything that breaks a campaign rule, and pushes Justin the top 2–3 with Twitch links: "Grab #1".
2. **Justin grabs it (≈2 min):** open the Twitch link on the phone, Do Not Disturb on, full screen (landscape), screen-record from start to end, upload to Google Drive folder **"T&M Fresh Drop"** (tony.and.minions Drive, folder id `1dE2LmM4BtakH6snIdBlCRzT13iJMULCw`). A ClipSpeed download works too. The folder must be set to "Anyone with the link can view" (Justin sets it once) so the build runner can fetch it.
3. **Build (3:44 PM ET, same task):** newest video in the drop folder since the scout → job with `"url": "https://drive.google.com/file/d/<id>/view"`, `"fit1080": true` (crops the phone's black bars, scales to 1920x1080 so the crop presets work), `"probe": true` first, then the real build (title band, hook in second 1, 15–30 s, hand-checked captions, campaign rules: KreekCraft logo overlay + caption line, AsianJeff no logos/never Facebook, etc.). Match the video to the shortlist by transcript + sheet; unsure → ask Justin, don't post.
4. **Post at 6:10 PM** on the platforms the campaign allows, within the safety caps. Native TikTok posts from the Speed chat (Posting Schedule 11-18.md) count toward the TikTok cap: **Sat 11-21 TikTok belongs to Speed scooter Part 2 (1:20 PM, native) — Part 1 was promoted 11-20 and is moving — so that day's fresh pick goes to YouTube/Facebook only.** The fresh pick takes that day's TikTok post; whatever held the 6:10 slot (or that day's TikTok slot) moves to a later day (never deleted). Never move SEGA #Ad posts, and never put a Part 2 before its Part 1. Register it in `posted_sources.json`; the Submitter pushes Justin the links at 6:18.
5. **Nothing grabbed / no good moment:** the day runs on the normal schedule. Never post a weak clip just to fill the fresh slot.

**Weights log:** 11-26 night (Analyst): LACY 1.3 -> 1.4 (stray dog FB 323 -> 1,115; LACY holds 5 of the top 8 FB Reels). 11-25 night (Analyst): no streamer weight change (no new TikTok/YouTube data); story hook words + 'worst', 'terrible', 'so bad', 'fail' (realkatieb 'worst GTA 6 gameplay' self-roast = best FB Reel 1,634). 11-24 night (Analyst): realkatieb 0.9 -> 1.0 ('worst GTA 6 gameplay' grew to 1,633 FB = best Reel ever). 11-23 night (Analyst): realkatieb 0.7 -> 0.9 ('worst GTA 6 gameplay' FB 1,195 on day one, 9 s avg - growth streamer matching our best Reels). 11-22 night (Analyst): LACY 1.25 -> 1.3 (LACY holds 4 of the top 6 FB Reels: seaplane P1 1,062, missions 769, Lucia bank 599, P2 money 511). 11-21 night (Analyst): YourRAGE 1.15 -> 1.2 (teeth = best FB Reel 1,156 + 97%-search TikTok); mechanic hook words + everyday-life words (teeth, brush, shower, sleep, dying/died, lose all/lost all, real life, beat the game, run out/ran out) - our search earners are everyday actions 'in GTA 6'. Earlier 11-21: hook score mechanic 4 -> 6 (fresh_scan.py).

**Staleness rule (Scheduler, from 11-20):** a reaction/story clip (hook_type reaction/story/other) whose moment is more than 5 days old doesn't go on TikTok; more than 7 days old it is held back (Metricool `draft: true`, never deleted). Mechanic clips (people keep searching them) stay usable up to 14 days. SEGA #Ad dates are fixed.

## TikTok explainer card (Justin chose 11-21, after TikTok called 3 launch edits "unoriginal")
Every TikTok post gets an `"explain"` freeze card on top of the normal edit (run_job: picture freezes with a slight punch-in for `dur` s at `t` while the audio keeps playing; dark card, lime header, 1-2 short lines).
- `"explain": {"t": 2.0, "dur": 1.8, "head": "GTA 6 tip" | "GTA 6 mechanic" | "GTA 6 NPCs are insane" | "GTA 6 random event", "text": "<the fact, max ~70 chars>"}` — t right after the hook line (1.5-3 s), never over the payoff.
- The text must be TRUE and shown in the clip (never invent a mechanic). Plain words people search (TikTok Inspiration 11-21: 'gta 6 gameplay' 3.1M searches, game guides 265K, 'GTA 6 AI/NPCs are insane' 1.4M-like post).
- New builds: add `explain` to the job. Already-built clips: a `restyle` job `{"name":"X_TT","restyle":{"src":"<our HQ url>"},"explain":{...}}` makes the TikTok version; queue item gets `tiktok_media`.
- TikTok only gets queue items that have `tiktok_media` (or a fresh pick built with `explain`). YouTube/Facebook keep the normal version.
- Campaign logos (KreekCraft) stay visible: the card is added before the logo overlay, and restyles freeze a frame that already has the logo.

## ClipSpeed live route (official connector, from 11-24) — the automated way to get fresh footage
**WHO GETS CREDITS, updated 11-25 (Justin: "let's not forget about Kai Cenat too if he posts, and Burnt Peanut gets views"; growth comes before paid campaigns). This replaces step 2 "who to clip" in the Live Clipper's prompt and the "paid streamers only" line in step 3 below; the credit gate, 10-minute limit and 1 session per 2 days stay.**
Pick the first one who is live on GTA 6 right now, in this order: **1. Speed** (YouTube) · **2. Kai Cenat** (twitch.tv/kaicenat) · **3. LACY** · **4. Burnt Peanut** (twitch.tv/theburntpeanut) · 5. Clix · 6. YourRAGE · 7. JasonTheWeen. Don't clip the same streamer two sessions in a row if another one on the list is live. Still never: KreekCraft, MissMikkaa, realkatieb, AsianJeff (Justin 11-26: doesn't perform; campaign over 11/26). No new AsianJeff clips on any platform. Kai, Speed and Burnt Peanut clips are growth posts (credit line + link like other growth streamers, never submitted); push Justin one line when one is posted.

Justin 11-24: "we want it to be automated, that's why I have the speedclip software." Tested end to end 11-24 (MissMikkaa, run-101/102).
1. **Who's live:** run `fresh.yml` (Twitch official API) and read `live_on_gta6` in out/fresh/latest.json.
2. **Clip:** `clip_livestream` {streamUrl: "https://www.twitch.tv/<login>", layout "rectangle", maxMinutes 15-30}. ClipSpeed starts producing clips within ~3 minutes. Poll `check_livestream` every few minutes; a clip is done when hasCaptions is true. Each clip has a title, a viral score (0-100) and a cdn.clipspeed.ai mp4 link.
3. **Budget (Justin 11-24: "work with the credits we have... we don't need to invest more, we still need to make up the amount we put in"):** a live session costs about **1.5 credits per minute** (the 11-24 test: 15 min, 16 clips, 101 -> 77). So a 10-minute session is ~15 credits. Rules: PAID campaign streamers only (growth streamers earn $0 and KreekCraft underperforms - never spend credits on them), `maxMinutes` 10, stop as soon as 2 clips pass, at most 1 session every 2 days, only start when credits >= 30 (15 kept in reserve). With 77 credits that's ~4 sessions until the Dec 18 renewal. Never buy credits or change the plan. The 16 MissMikkaa clips from the test are already paid for - use them (growth posts) before they go stale.
4. **Rebuild in our style (never post ClipSpeed's file as is - originality):** job `{"name", "url": "<cdn mp4>", "csband": true, "title": [...], "captions": "auto" or manual list, "style", "explain"?, "overlay"?}`. `csband` finds ClipSpeed's cam+game band (1080x1920, cam on top, 16:9 game below, between black bars), drops ClipSpeed's burned title/captions, and rebuilds with OUR title band + hand-checked captions (crops in source pixels, `--native`). `out/<name>/csband.json` says `confident`. When ClipSpeed made a full-frame clip (16:9 game with a small webcam inside, not a split), csband is not confident: pass `cam` and `game` yourself in SOURCE pixels (read sheet.jpg) - explicit cam/game win over csband. Probe first (`"probe": true`) to read the transcript: ClipSpeed's auto-picks can contain swears/slurs and outfit shots - apply rule 5 (mute swears, cut slurs out with segments, blur outfits for YT/FB, cut sub-reading).
5. **Post** through Metricool like the fast lane below (replace the next scheduled post on that platform, keep the caps), then push Justin the Content Rewards links the moment TikTok/YouTube show PUBLISHED (30-minute window).
Note: `submit_to_clipspeed` rejects Twitch clip URLs (`invalid_video_url`, 11-24) - live only for Twitch.

## Live route (ClipSpeed → VOD) — old browser route, PAUSED (rule T)
`"live": {"channel","vod","ref","gen_utc","back","pad"}` downloads the VOD window and finds the
ClipSpeed clip inside it by audio (match ≥0.9 is good; <0.3 means the window missed — widen `back`).
`gen_utc` = the 10-digit epoch in ClipSpeed's `captioned_<id>_<epoch-ms>.mp4` filename.
Each job gets its own runner (matrix), so push many probes at once.

## Live fast lane (Live Hunter, from 11-19)
**PAUSED 11-20 (rule T): the Live Hunter used the browser on Twitch/ClipSpeed/Content Rewards. Replaced by "Fresh pick" above.**
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
**BEST TIMES PER PLATFORM (Justin 11-25: "we need to post at best times for each platform"). These times replace the clock times in the grid below; the grid still says WHAT goes WHERE.** Source: Metricool best-time heat map for each of our accounts, pulled 11-25 for the week 11-25..12-01 (ET). It is Metricool's audience-activity estimate, not proof from our own posts (too few yet), so the Analyst checks it against our views by posting hour.

| Platform | 1st choice | 2nd choice | Avoid | Old slot -> new slot |
|---|---|---|---|---|
| TikTok (2/day) | **18:10** | **10:10** or 12:10 | after 20:00, before 8:00 | 20:10 is last resort only |
| YouTube (2/day) | **16:10** | **10:10** | after 19:00 | 15:10 -> 16:10; a direct upload by Justin stays ~18:10 (he uploads by hand) |
| Facebook (2/day) | **10:10** or 12:10 | **16:10-18:10** | after 20:00 | 9:10 -> 10:10, 11:10 -> 12:10, 15:10 -> 16:10 |

- Slot times are now **10:10 · 12:10 · 16:10 · 18:10** (20:10 only when a cap forces it). Same platform stays 3+ h apart.
- One clip going to several platforms: use the time that is best for the platform that PAYS for that clip (TikTok/YouTube for paid clips; Facebook for growth clips). Split into two Metricool posts when the best times differ by 3+ h and the cap allows.
- Weekdays beat weekends on every platform (Sat/Sun are roughly 55-60% of weekday activity): the strongest clip of the week goes Tue-Thu; weekends get the second-tier clips.
- Story teasers still go ~50 min after their Reel.
- Analyst: once 10+ posts per platform have run at the new times, compare median views by posting hour against the old 9:10/11:10/15:10/20:10 posts and record the result in `platform_strategy.json` <platform>.route.best_times.

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
**GROWTH FIRST (Justin 11-25: "we need to focus on the growth of the channel before doing paid promotions like the SEGA one").**
- **No new brand #Ad posts (SEGA or any other sponsor) until Justin says so.** The 11-25 SEGA post was the last one scheduled. Reasons: #Ad posts got ~47 views (For You 0.46) and SEGA pays nothing under $5 = 1,000 paid-country views per post.
- If brand ads come back: on YouTube the handle goes in the DESCRIPTION too (Metricool `text`), not only the title. The SEGA brief wants @sega_west on TikTok and YouTube; our YouTube description said @sega (the Instagram handle).
- Streamer clips: pick by the quality gate (rule 2), not by which campaign pays. Submit a clip when it qualifies, but never post a weaker clip because it is "paid". Views are what is missing, not submissions: LACY's pool needs 750,000 approved views in total before it pays a share; AsianJeff 10K per clip; KreekCraft 3K per clip.
- Approvals so far (Gmail, 11-25): 0 approved, 1 not approved (LACY, 11-20, "potential fake engagement/views", the night of the TikTok Promote), the rest pending. Reach says to open a Discord ticket to contest it - Justin's to-do, and it matters because Reach bans across all its campaigns for botting strikes.

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

**Reach Discord** (Justin joined 11-23): use it as an info source for new Reach campaigns, rule changes, payout and review notes. Rule T applies: no bots, scripts, browser or user-token reading on discord.com — Justin forwards or screenshots what matters, or (if he sets it up) Reach announcement channels get "Followed" into his own server and our own bot reads them there via the official API. Vet any new campaign with the clip-campaign-vetting checklist before joining; joining still needs Justin's OK.

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
