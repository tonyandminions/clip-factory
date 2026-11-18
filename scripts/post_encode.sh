#!/bin/bash
# usage: post_encode.sh IN OUT [MB]
# Re-encodes to fit the browser upload cap (default 3.55 MiB): x264 2-pass up to 15 s, HEVC 2-pass above.
set -e
IN="$(realpath "$1")"; OUT="$(realpath -m "$2")"; MB="${3:-3.55}"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
VB=$(python3 -c "print(int($MB*8*1024*1024/$D/1000 - 100))")
WORK=$(mktemp -d); cd "$WORK"
if python3 -c "import sys; sys.exit(0 if $D<=15 else 1)"; then
  ffmpeg -v error -y -i "$IN" -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -an -f mp4 /dev/null
  ffmpeg -v error -y -i "$IN" -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT"
else
  ffmpeg -v error -y -i "$IN" -c:v libx265 -preset fast -b:v ${VB}k -x265-params pass=1:log-level=error -an -f mp4 /dev/null
  ffmpeg -v error -y -i "$IN" -c:v libx265 -preset fast -b:v ${VB}k -x265-params pass=2:log-level=error -tag:v hvc1 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT"
fi
rm -rf "$WORK"
echo "post: $OUT $(stat -c %s "$OUT") bytes, ${D}s @ ${VB}k"
