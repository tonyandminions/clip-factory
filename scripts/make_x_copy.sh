#!/usr/bin/env bash
# Make an X-ready copy of a built clip (720x1280, 2-pass H.264, under 3.6 MB).
# Why: Claude in Chrome's file_upload takes at most 3.8 MB per call, and X re-encodes anyway.
# Usage: scripts/make_x_copy.sh run-61/RAGE_BrushTeeth_v2/RAGE_BrushTeeth_v2_HQ.mp4 [more paths...]
# Output: /mnt/user-data/uploads/xposts/x/<NAME>_X.mp4  (upload it from that path with file_upload)
set -euo pipefail
OUT=/mnt/user-data/uploads/xposts
mkdir -p "$OUT/x"
for p in "$@"; do
  f=$(basename "$p")
  name=${f%_HQ.mp4}
  [ -s "$OUT/$f" ] || gh api "repos/tonyandminions/clip-factory/contents/$p?ref=out" \
      -H "Accept: application/vnd.github.raw" > "$OUT/$f"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$f")
  o="$OUT/x/${name}_X.mp4"
  for mb in 3.55 3.40 3.25 3.10; do
    vb=$(python3 -c "print(int(($mb*8*1024*1024/$d - 96000)/1000))")
    ffmpeg -y -v error -i "$OUT/$f" -vf scale=720:1280:flags=lanczos -c:v libx264 -preset medium \
        -b:v ${vb}k -pass 1 -passlogfile "/tmp/xp_$name" -an -f mp4 /dev/null
    ffmpeg -y -v error -i "$OUT/$f" -vf scale=720:1280:flags=lanczos -c:v libx264 -preset medium \
        -b:v ${vb}k -maxrate $((vb*2))k -bufsize $((vb*2))k -pass 2 -passlogfile "/tmp/xp_$name" \
        -c:a aac -b:a 96k -ar 44100 -movflags +faststart -pix_fmt yuv420p "$o"
    s=$(stat -c %s "$o")
    [ "$s" -le 3780000 ] && break
  done
  if [ "$s" -gt 3780000 ]; then echo "TOO BIG: $o ($s bytes)"; exit 1; fi
  echo "$o ${d}s ${vb}k ${s} bytes"
done
