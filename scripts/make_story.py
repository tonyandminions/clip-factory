#!/usr/bin/env python3
"""Make a 9:16 Instagram/Facebook Story from a finished clip.

Two modes:
  teaser (default): a short slice of the clip with a banner on top and a call to action at the bottom.
  --card:           a blurred still frame with 2-4 big centered lines (Part 2 countdowns, "LIVE now" alerts).

Safe zones: Stories cover ~250 px at the top (profile bar) and ~300 px at the bottom (reply bar),
so text sits at y≈270 and y≈1500.
"""
import argparse, os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Poppins-Bold.ttf")
NO_EMOJI = re.compile("[\U00010000-\U0010FFFF☀-➿️]")


def clean(t):
    return NO_EMOJI.sub("", t or "").strip()


def tf(text, d, name):
    p = os.path.join(d, name)
    open(p, "w").write(clean(text))
    return p


def dt(textfile, size, y, color="white", box=True):
    s = (f"drawtext=fontfile={FONT}:textfile={textfile}:fontsize={size}:fontcolor={color}"
         f":x=(w-text_w)/2:y={y}")
    if box:
        s += ":box=1:boxcolor=black@0.62:boxborderw=26"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ss", type=float, default=0.0)
    ap.add_argument("--to", type=float, default=12.0)
    ap.add_argument("--top", default="NEW CLIP")
    ap.add_argument("--bottom", default="full video on our page")
    ap.add_argument("--accent", default="#B8FF3B")
    ap.add_argument("--card", action="store_true")
    ap.add_argument("--lines", default="")
    ap.add_argument("--t", type=float, default=3.0, help="frame time for --card")
    ap.add_argument("--dur", type=float, default=6.0, help="card length")
    a = ap.parse_args()
    acc = "0x" + a.accent.lstrip("#")
    d = tempfile.mkdtemp()
    if a.card:
        frame = os.path.join(d, "f.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.t), "-i", a.src, "-frames:v", "1", frame], check=True)
        lines = [l for l in a.lines.split("|") if l.strip()][:4]
        y0 = 760 - (len(lines) - 1) * 70
        draws = []
        for i, l in enumerate(lines):
            draws.append(dt(tf(l, d, f"l{i}.txt"), 96 if i else 84, y0 + i * 150, acc if i == 1 else "white", box=False))
        draws.append(dt(tf(a.bottom, d, "b.txt"), 52, 1500, "white"))
        vf = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=22:2,eq=brightness=-0.28,"
              + ",".join(draws) + ",format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", frame, "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=stereo", "-t", str(a.dur), "-vf", vf, "-c:v", "libx264", "-preset",
                        "veryfast", "-crf", "18", "-r", "30", "-c:a", "aac", "-shortest", a.out], check=True)
    else:
        # clip shrunk to 82% over a blurred copy of itself, leaving a clear band for the banner (y≈205)
        # and the call to action (y≈1680), both outside Instagram's story header and reply bar.
        fc = ("[0:v]split[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2,eq=brightness=-0.3[bg];"
              "[b]scale=886:-2[fg];[bg][fg]overlay=(W-w)/2:300,"
              + dt(tf(a.top, d, "t.txt"), 70, 205, acc) + ","
              + dt(tf(a.bottom, d, "b.txt"), 52, 1680, "white") + ",format=yuv420p[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.ss), "-to", str(a.to), "-i", a.src,
                        "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "160k", a.out],
                       check=True)
    # 4-frame preview strip next to the output
    prev = os.path.join(os.path.dirname(a.out), "preview.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.out, "-vf",
                    "fps=4/" + str(a.dur if a.card else (a.to - a.ss)) + ",scale=270:-1,tile=4x1",
                    "-frames:v", "1", "-q:v", "3", prev], check=False)


if __name__ == "__main__":
    main()
