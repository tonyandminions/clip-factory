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
