#!/usr/bin/env python3
"""Word-by-word captions: the phrase stays on screen and the word being said lights up.

Used by build_split.py and build_talk.py with --capstyle word. Renders an ASS file that
ffmpeg's `ass` filter burns in (libass, same font as the rest of the edit).

Inputs
  phrases: [[start, end, "TEXT"], ...] (caps.json or a hand-checked list; "*" prefix ignored)
  words:   [[start, end, "word", is_swear], ...] from transcribe.py (words.json), same clock
Each phrase's words get real timings when the transcript words line up with the phrase text;
otherwise the phrase's time is shared out by word length, so hand-fixed text still works.

make_ass(phrases, words, out_path, y=937, size=62, accent="0xB8FF3B", maxw=960)
"""
import json, re

def _ass_color(hexrgb):
    h = hexrgb.lower().replace("0x", "").replace("#", "")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}&".upper()

def _ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"

def _clean(t):
    return re.sub(r"[{}\\]", "", t)

def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())

def _time_words(s, e, tokens, words):
    """Give each token (start, end). Match transcript words inside the phrase window by text."""
    inside = [w for w in words if not (len(w) > 3 and w[3]) and w[1] > s - 0.25 and w[0] < e + 0.25
              and s - 0.25 <= (w[0] + w[1]) / 2 <= e + 0.25]
    if len(inside) == len(tokens) and sum(_norm(a) == _norm(b[2]) for a, b in zip(tokens, inside)) >= len(tokens) * 0.5:
        st = [max(s, w[0]) for w in inside]
    else:  # share the phrase time out by word length (hand-edited text, merged/split words)
        lens = [len(t) + 1 for t in tokens]; tot = sum(lens); st = []; acc = s
        for L in lens:
            st.append(acc); acc += (e - s) * L / tot
    st[0] = s
    out = []
    for i, t0 in enumerate(st):
        t1 = st[i + 1] if i + 1 < len(st) else e
        out.append((t0, max(t1, t0 + 0.05)))
    return out

def make_ass(phrases, words, out_path, y=937, size=62, accent="0xB8FF3B", maxw=960,
             font="Poppins", outline=5, shadow=0, upper=True):
    acc = _ass_color(accent)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{round(size * 1.65)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},{shadow},5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    size = round(size * 1.65)  # libass sizes by line height; x1.65 matches drawtext's em size for Poppins
    for s, e, text in phrases:
        text = _clean(text.lstrip("*").strip()).replace("'", "’")
        if upper:
            text = text.upper()
        tokens = text.split()
        if not tokens or e <= s:
            continue
        # shrink long phrases so they stay on one line inside the band
        est = len(text) * size * 0.32
        fs = size if est <= maxw else max(int(size * 0.62), int(size * maxw / est))
        timing = _time_words(s, e, tokens, words)
        for i, (t0, t1) in enumerate(timing):
            parts = [(f"{{\\c{acc}}}{tok}{{\\c&H00FFFFFF&}}" if j == i else tok) for j, tok in enumerate(tokens)]
            ev.append(f"Dialogue: 0,{_ts(t0)},{_ts(t1)},Cap,,0,0,0,,{{\\pos(540,{y})\\fs{fs}}}" + " ".join(parts))
    open(out_path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
    return len(ev)

def ass_filter(path, fontsdir):
    esc = lambda p: p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    return f"ass='{esc(path)}':fontsdir='{esc(fontsdir)}'"

if __name__ == "__main__":
    import sys
    ph = json.load(open(sys.argv[1])); wd = json.load(open(sys.argv[2])) if len(sys.argv) > 3 else []
    print(make_ass(ph, wd, sys.argv[-1]), "events")
