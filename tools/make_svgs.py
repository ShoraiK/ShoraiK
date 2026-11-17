"""Generate the profile README and its pixel-art SVGs (SMIL animation) in three designs.

Usage: python tools/make_svgs.py [PREVIEW_DIR]
       python tools/make_svgs.py --report OUT_SVG
Each design goes to designs/<name>/; the one named in PICK also goes to the root, which is what GitHub shows.
With PREVIEW_DIR, it also writes there an HTML page that shows every design.
With --report, it only draws the nightshift shift report from the live GitHub numbers (it needs a token in
GITHUB_TOKEN); .github/workflows/report.yml runs it every night.
"""
import json
import os
import pathlib
import random
import re
import sys
import urllib.request

OUT = pathlib.Path(__file__).resolve().parents[1]

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "@": [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."],
    ">": ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "|": ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "─": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "◆": [".....", "..#..", ".###.", "#####", ".###.", "..#..", "....."],
    "▼": ["#####", ".###.", "..#..", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "✦": ["..#..", "..#..", ".###.", "#####", ".###.", "..#..", "..#.."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "%": ["##...", "##..#", "...#.", "..#..", ".#...", "#..##", "...##"],
    "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    "c": [".....", ".....", ".###.", "#....", "#....", "#...#", ".###."],
    "f": ["..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."],
    "g": [".....", ".....", ".####", "#...#", ".####", "....#", ".###."],
    "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
    "n": [".....", ".....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "t": [".#...", ".#...", "###..", ".#...", ".#...", ".#..#", "..##."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "y": [".....", ".....", "#...#", "#...#", ".####", "....#", ".###."],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", "..#.."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "★": ["..#..", "..#..", "#####", ".###.", ".#.#.", "#...#", "....."],
    "♥": [".....", ".#.#.", "#####", "#####", ".###.", "..#..", "....."],
    "▶": ["#....", "##...", "###..", "####.", "###..", "##...", "#...."],
    "h": ["#....", "#....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "r": [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    "p": [".....", ".....", "####.", "#...#", "####.", "#....", "#...."],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
}
# The sober designs draw p, g, y and j with descenders, and a colon that does not read as "!" in small text;
# the synthwave one keeps the font as it was.
LOW = dict(FONT, p=[".....", ".....", "####.", "#...#", "#...#", "#...#", "####.", "#....", "#...."],
           g=[".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
           y=[".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
           j=["...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."])
LOW[":"] = [".....", ".....", "..#..", ".....", ".....", ".....", "..#.."]


def width(text, s):
    return sum(4 * s if c == " " else 6 * s for c in text) - s


def text_path(text, x, y, s, anchor="start", font=FONT):
    if anchor == "middle":
        x -= width(text, s) / 2
    elif anchor == "end":
        x -= width(text, s)
    parts = []
    for char in text:
        if char == " ":
            x += 4 * s
            continue
        for row, line in enumerate(font[char]):
            for col, bit in enumerate(line):
                if bit == "#":
                    parts.append("M%g %gh%gv%gh-%gz" % (x + col * s, y + row * s, s, s, s))
        x += 6 * s
    return "".join(parts)


def sprite(rows, palette, x, y, s):
    out = []
    for key, color in palette.items():
        d = "".join("M%g %gh%gv%gh-%gz" % (x + c * s, y + r * s, s, s, s)
                    for r, line in enumerate(rows) for c, ch in enumerate(line) if ch == key)
        if d:
            out.append('<path fill="%s" d="%s"/>' % (color, d))
    return "".join(out)


def blink(dur, values="1;1;0;0", begin="0s"):
    return ('<animate attributeName="opacity" values="%s" dur="%s" begin="%s" calcMode="discrete" '
            'repeatCount="indefinite"/>' % (values, dur, begin))


HERO_TOP = ["....WWWW....", "..WWWWWWWW..", ".WWWWWWWWWW.", "WWwWWWWWWWw.", ".WSSSSSSSW..",
            ".WSKSSSKSS..", "..SKSSSKSS.."]
HERO_A = HERO_TOP + ["MM.SSSSSS...", "MMMMMMMMM...", "..HHHHHHHH..", "..HhHHHHHHS.", "..HHHHHHHH..",
                     "...PP..PP...", "..PP....PP..", ".BB......BB.", "............"]
HERO_B = HERO_TOP + [".M.SSSSSS...", "MMMMMMMMM...", "..HHHHHHHH..", "..HhHHHHHHS.", "..HHHHHHHH..",
                     "....PPPP....", "....PP.PP...", "...BB..BB...", "............"]
HERO_COLORS = {"W": "#f4f1ff", "w": "#c9c2ff", "S": "#ffd9b8", "K": "#2a2350", "M": "#ff4f8b",
               "H": "#7c5cff", "h": "#5a3fd6", "P": "#2b2f5e", "B": "#14142b"}
SLIME = ["...GGGG...", ".GGGGGGGG.", "GGWKGGWKGG", "GGWKGGWKGG", "GGGGGGGGGG", "GDGGGGGGDG", ".DDDDDDDD."]
SLIME_COLORS = {"G": "#5ee6a0", "D": "#2fb37a", "W": "#ffffff", "K": "#1b1b2f"}
COIN = [
    ["..OOOO..", ".OYYYYO.", "OYLYYYYO", "OYLYYYYO", "OYLYYYYO", "OYYYYYYO", ".OYYYYO.", "..OOOO.."],
    ["...OO...", "..OYYO..", "..OLYO..", "..OLYO..", "..OLYO..", "..OYYO..", "..OYYO..", "...OO..."],
    ["...OO...", "...OO...", "...OO...", "...OO...", "...OO...", "...OO...", "...OO...", "...OO..."],
]
COIN_COLORS = {"O": "#c77d1a", "Y": "#ffd76a", "L": "#fff3b0"}


def banner():
    random.seed(7)
    W, H, GROUND = 1200, 300, 246
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'shape-rendering="crispEdges" role="img" aria-label="ShoraiK">' % (W, H, W, H)]
    o.append('<defs>'
             '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#120b2e"/><stop offset=".55" stop-color="#2a1458"/>'
             '<stop offset=".8" stop-color="#6b1f6e"/><stop offset="1" stop-color="#ff5e8a"/></linearGradient>'
             '<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#ffe66d"/><stop offset="1" stop-color="#ff4f8b"/></linearGradient>'
             '<mask id="stripes"><rect width="%d" height="%d" fill="#fff"/>' % (W, H) +
             "".join('<rect y="%d" width="%d" height="%d" fill="#000"/>' % (y, W, h)
                     for y, h in ((198, 2), (210, 3), (221, 4), (233, 6))) +
             '</mask>'
             '<linearGradient id="kara" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#ffd76a"/>'
             '<stop offset="0" stop-color="#ffd76a"><animate attributeName="offset" values="0;1;1" '
             'keyTimes="0;.7;1" dur="4s" repeatCount="indefinite"/></stop>'
             '<stop offset="0" stop-color="#ff7eb6"><animate attributeName="offset" values="0;1;1" '
             'keyTimes="0;.7;1" dur="4s" repeatCount="indefinite"/></stop>'
             '<stop offset="1" stop-color="#c77dff"/></linearGradient>'
             '</defs>')
    o.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H))
    for _ in range(46):
        x, y = random.randrange(10, W - 10), random.randrange(8, 175)
        size = random.choice((2, 2, 3, 4))
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fff">'
                 '<animate attributeName="opacity" values=".15;1;.15" dur="%.1fs" begin="%.1fs" '
                 'repeatCount="indefinite"/></rect>' % (x, y, size, size, random.uniform(1.6, 4.2),
                                                       random.uniform(0, 3)))
    o.append('<circle cx="960" cy="222" r="76" fill="url(#sun)" mask="url(#stripes)"/>')
    for speed, color, low, high, step in ((70, "#3d1c6e", 18, 66, 40), (38, "#26114a", 10, 42, 30)):
        d = []
        for copy in (0, W):
            x = copy
            d.append("M%d %d" % (x, GROUND))
            while x < copy + W:
                h = random.randrange(low, high, 6)
                d.append("V%dH%d" % (GROUND - h, x + step))
                x += step
            d.append("V%dZ" % GROUND)
        o.append('<g><path fill="%s" d="%s"/><animateTransform attributeName="transform" type="translate" '
                 'from="0 0" to="-%d 0" dur="%ds" repeatCount="indefinite"/></g>' % (color, "".join(d), W, speed))
    o.append('<rect y="%d" width="%d" height="%d" fill="#1a0f33"/>' % (GROUND, W, H - GROUND))
    tiles = "".join('<rect x="%d" y="%d" width="38" height="16" fill="%s"/>' % (
        x + (20 if r % 2 else 0), GROUND + 6 + r * 18, "#241446" if (x // 40 + r) % 2 else "#1f1140")
        for r in range(3) for x in range(-40, W + 40, 40))
    o.append('<g>%s<animateTransform attributeName="transform" type="translate" from="0 0" to="-40 0" '
             'dur=".45s" repeatCount="indefinite"/></g>' % tiles)
    o.append('<rect y="%d" width="%d" height="4" fill="#ff4f8b"/>' % (GROUND, W))

    # Slime with a coin above it, crossing the screen every 4 s.
    coin = "".join('<g opacity="0">%s%s</g>' % (sprite(frame, COIN_COLORS, 9, -50, 4), blink(
        ".8s", values)) for frame, values in zip(COIN, ("1;0;0;0", "0;1;0;1", "0;0;1;0")))
    o.append('<g><g>%s<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.8;.805;1" dur="4s" '
             'repeatCount="indefinite"/></g><g>%s<animateTransform attributeName="transform" type="translate" '
             'values="0 0;0 -4;0 0" dur=".4s" repeatCount="indefinite"/></g>'
             '<animateTransform attributeName="transform" type="translate" from="1260 211" to="-60 211" '
             'dur="4s" repeatCount="indefinite"/></g>' % (coin, sprite(SLIME, SLIME_COLORS, 0, 0, 5)))

    # Hero: two run frames, and a jump over the slime that grabs the coin.
    frames = "".join('<g opacity="%d">%s%s</g>' % (1 - i, sprite(rows, HERO_COLORS, 170, 166, 5), blink(
        ".3s", "1;0" if i == 0 else "0;1")) for i, rows in enumerate((HERO_A, HERO_B)))
    o.append('<g>%s<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -72;0 0;0 0" '
             'keyTimes="0;.73;.81;.89;1" calcMode="spline" keySplines="0 0 1 1;.2 .8 .4 1;.6 0 .8 .2;0 0 1 1" '
             'dur="4s" repeatCount="indefinite"/></g>' % frames)
    o.append('<g opacity="0"><path fill="#ffd76a" d="%s"/>'
             '<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.8;.805;.9;.92;1" dur="4s" '
             'repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" '
             'values="0 0;0 0;0 -24;0 -24" keyTimes="0;.8;.92;1" dur="4s" repeatCount="indefinite"/></g>'
             % text_path("+1", 205, 70, 3))

    # Title with a karaoke wipe, tagline, HUD and a blinking prompt.
    title = text_path("ShoraiK", 600, 34, 10, "middle")
    o.append('<path fill="#2a0f45" transform="translate(6 6)" d="%s"/><path fill="url(#kara)" d="%s"/>'
             % (title, title))
    o.append('<path fill="#e8e3ff" d="%s"/>' % text_path("BACKEND DEV BY DAY · NAS TINKERER BY NIGHT",
                                                          600, 122, 3, "middle"))
    o.append('<path fill="#ffffff" d="%s"/>' % text_path("P1", 24, 20, 3))
    o.append('<path fill="#ff4f8b" d="%s"/>' % text_path("♥♥♥", 70, 20, 3))
    o.append('<path fill="#ffd76a" d="%s"/>' % text_path("LV 99", W - 24, 20, 3, "end"))
    o.append('<g><path fill="#ffffff" d="%s"/>%s</g>' % (text_path("PRESS START", 600, 166, 3, "middle"),
                                                         blink("1.2s")))
    o.append("</svg>")
    return "".join(o)


def card(mark="★", header="FEATURED QUEST", cta="▶ OPEN QUEST"):
    W, H = 1200, 240
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'shape-rendering="crispEdges" role="img" aria-label="NASpeed">' % (W, H, W, H)]
    o.append('<defs><linearGradient id="t" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#ffd76a"/><stop offset="1" stop-color="#ff7eb6"/></linearGradient>')
    bars = (("DOWN", 300, "#5ee6a0", "0s"), ("UP", 230, "#7cc6ff", ".5s"), ("PING", 120, "#ffd76a", "1s"))
    for i, (_, full, _, begin) in enumerate(bars):
        o.append('<clipPath id="b%d"><rect x="830" y="%d" width="0" height="20"><animate attributeName="width" '
                 'values="0;%d;%d;0" keyTimes="0;.55;.9;1" dur="4s" begin="%s" repeatCount="indefinite"/>'
                 '</rect></clipPath>' % (i, 70 + i * 44, full, full, begin))
    o.append('</defs>')
    o.append('<rect width="%d" height="%d" fill="#160d2e"/>' % (W, H))
    o.append('<rect x="4" y="4" width="%d" height="%d" fill="none" stroke="#ff4f8b" stroke-width="8"/>' % (W - 8, H - 8))
    o.append('<rect x="16" y="16" width="%d" height="%d" fill="none" stroke="#7c5cff" stroke-width="4"/>'
             % (W - 32, H - 32))
    o.append('<g><path fill="#ffd76a" d="%s"/>%s</g>' % (text_path(mark, 44, 40, 3), blink("1.6s", ".3;1")))
    o.append('<path fill="#ffd76a" d="%s"/>' % text_path(header, 68, 40, 3))
    title = text_path("NASpeed", 44, 74, 8)
    o.append('<path fill="#2a0f45" transform="translate(5 5)" d="%s"/><path fill="url(#t)" d="%s"/>' % (title, title))
    o.append('<path fill="#e8e3ff" d="%s"/>' % text_path("SPEED TEST FOR TERRAMASTER TOS 7", 44, 146, 3))
    o.append('<path fill="#a99bff" d="%s"/>' % text_path("CLOUDFLARE · OOKLA · M-LAB · LIBRESPEED", 44, 180, 3))
    for i, (label, full, color, _) in enumerate(bars):
        y = 70 + i * 44
        o.append('<path fill="#e8e3ff" d="%s"/>' % text_path(label, 812, y + 1, 3, "end"))
        o.append('<rect x="830" y="%d" width="320" height="20" fill="#2a1d52"/>' % y)
        blocks = "".join('<rect x="%d" y="%d" width="16" height="20"/>' % (830 + k * 20, y) for k in range(16))
        o.append('<g fill="%s" clip-path="url(#b%d)">%s</g>' % (color, i, blocks))
    o.append('<g><path fill="#ffffff" d="%s"/>%s</g>' % (text_path(cta, 1150, 196, 3, "end"),
                                                         blink("1.2s")))
    o.append("</svg>")
    return "".join(o)


MUG = ["RRRRRRRRR...", "RcccccccR...", "BWBBBBBBBHH.", "BWBBBBBBB..H", "BWBBBBBBB..H", "BBBBBBBBBHH.",
       "DBBBBBBBD...", ".DDDDDDD...."]
MUG_COLORS = {"R": "#ffd1e3", "c": "#6b3b1f", "B": "#ff7eb6", "W": "#ffe3ef", "H": "#ff7eb6", "D": "#c23a6c"}


def stats(mark="★", header="PLAYER STATS", labels=("CLASS", "MAIN", "SIDE"), mug=True):
    W, H = 1200, 230
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'shape-rendering="crispEdges" role="img" aria-label="Player stats">' % (W, H, W, H)]
    o.append('<rect width="%d" height="%d" fill="#160d2e"/>' % (W, H))
    o.append('<rect x="4" y="4" width="%d" height="%d" fill="none" stroke="#ff4f8b" stroke-width="8"/>' % (W - 8, H - 8))
    o.append('<rect x="16" y="16" width="%d" height="%d" fill="none" stroke="#7c5cff" stroke-width="4"/>'
             % (W - 32, H - 32))
    o.append('<g><path fill="#ffd76a" d="%s"/>%s</g>' % (text_path(mark, 44, 40, 3), blink("1.6s", ".3;1")))
    o.append('<path fill="#ffd76a" d="%s"/>' % text_path(header, 68, 40, 3))
    for label, y in zip(labels, (84, 124, 170)):
        o.append('<path fill="#a99bff" d="%s"/>' % text_path(label, 44, y, 3))
    o.append('<path fill="#ffffff" d="%s"/>' % text_path("BACKEND DEVELOPER", 230, 84, 3))
    slots = []
    for labels, y, border in ((("JAVA", "SPRING", "HIBERNATE"), 118, "#ffd76a"),
                              (("PYTHON", "JAVASCRIPT", "LINUX", "SELF-HOSTING"), 164, "#7c5cff")):
        x = 230
        for label in labels:
            w = width(label, 3) + 28
            o.append('<rect x="%d" y="%d" width="%d" height="32" fill="%s"/><rect x="%d" y="%d" width="%d" '
                     'height="24" fill="#2a1d52"/>' % (x, y, w, border, x + 4, y + 4, w - 8))
            o.append('<path fill="#ffffff" d="%s"/>' % text_path(label, x + 14, y + 6, 3))
            slots.append((x, y, w))
            x += w + 16
    anim = "".join('<animate attributeName="%s" values="%s" dur="%ds" calcMode="discrete" repeatCount="indefinite"/>'
                   % (attr, ";".join(str(v) for v in values), len(slots))
                   for attr, values in (("x", [sx - 6 for sx, _, _ in slots]), ("y", [sy - 6 for _, sy, _ in slots]),
                                        ("width", [sw + 12 for _, _, sw in slots])))
    x, y, w = slots[0]
    o.append('<rect x="%d" y="%d" width="%d" height="44" fill="none" stroke="#ffffff" stroke-width="4">%s</rect>'
             % (x - 6, y - 6, w + 12, anim))
    o.append(sprite(MUG, MUG_COLORS, 1030, 118, 6) if mug else "")
    for i, x in enumerate((1040, 1058, 1076) if mug else ()):
        o.append('<g opacity="0"><path fill="#e8e3ff" d="M%d 106h6v6h-6zM%d 100h6v6h-6zM%d 94h6v6h-6zM%d 88h6v6h-6z"/>'
                 '<animate attributeName="opacity" values="0;.8;0" dur="2s" begin="%.2fs" repeatCount="indefinite"/>'
                 '<animateTransform attributeName="transform" type="translate" values="0 0;0 -18" dur="2s" '
                 'begin="%.2fs" repeatCount="indefinite"/></g>' % (x, x + 6, x + 6, x, i * .66, i * .66))
    o.append("</svg>")
    return "".join(o)


PLANT = ["..l.l..", ".lLlLl.", "l.LLL.l", "..LLL..", "...L...", ".PPPPP.", ".PPPPP.", "..ppp.."]
PLANT_COLORS = {"L": "#4f8a6b", "l": "#6fae86", "P": "#3a3170", "p": "#2b2550"}


def svg_open(W=1200, H=300):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'shape-rendering="crispEdges" role="img" aria-label="ShoraiK">' % (W, H, W, H))


def typewriter(cid, text, x, y, s, start, end, step):
    """Clip path that reveals `text` one character at a time from `start` and hides it at `end` (fractions of 8 s)."""
    widths, total = [0], 0
    for char in text:
        total += 4 * s if char == " " else 6 * s
        widths.append(total)
    times = [0] + [start + k * step for k in range(len(text))] + [end]
    return ('<clipPath id="%s"><rect x="%d" y="%d" width="0" height="%d"><animate attributeName="width" values="%s" '
            'keyTimes="%s" dur="8s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
            % (cid, x, y - 2, 9 * s + 4, ";".join(map(str, widths + [0])), ";".join("%.3f" % t for t in times)))


def dither(pid, a, b):
    """Pattern that mixes two colours in a checkerboard of 2 px squares."""
    return ('<pattern id="%s" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="%s"/>'
            '<rect width="2" height="2" fill="%s"/><rect x="2" y="2" width="2" height="2" fill="%s"/></pattern>'
            % (pid, a, b, b))


def banner_dungeon():
    """Terminal roguelike: the name with a block cursor, and a small dungeon that the @ crosses to the stairs."""
    W, H, S, CW, CH, X0, Y0 = 1200, 300, 2, 12, 18, 600, 84
    grid = [[" "] * 46 for _ in range(7)]

    def room(x, y, w, h):
        for c in range(x, x + w):
            grid[y][c] = grid[y + h - 1][c] = "─"
        for r in range(y + 1, y + h - 1):
            grid[r][x] = grid[r][x + w - 1] = "|"
            for c in range(x + 1, x + w - 1):
                grid[r][c] = "."

    def cell(r, c):
        return X0 + c * CW, Y0 + r * CH

    room(0, 0, 10, 6)
    room(20, 0, 15, 6)
    room(37, 2, 9, 5)
    for c in range(10, 20):
        grid[2][c] = "#"
    grid[3][35] = grid[3][36] = "#"
    grid[2][9] = grid[2][20] = grid[3][34] = grid[3][37] = "+"
    grid[2][27], grid[4][41] = "$", ">"
    colors = {"─": "#5d636d", "|": "#5d636d", ".": "#353a42", "+": "#b07d3a", "#": "#4a4f57", ">": "#e8e6e3"}
    path = [(2, c) for c in range(3, 34)] + [(3, 33), (3, 34), (3, 35), (3, 36), (3, 37), (3, 38), (3, 39), (4, 40),
                                             (4, 41)]
    pick = "%.2f" % (path.index((2, 27)) * .02)

    o = [svg_open(W, H), '<rect width="%d" height="%d" fill="#0d0f12"/>' % (W, H)]
    o.append('<path fill="#e8e6e3" d="%s"/>' % text_path("ShoraiK", 48, 64, 8))
    o.append('<rect x="%d" y="64" width="40" height="56" fill="#d7a54a">%s</rect>'
             % (48 + width("ShoraiK", 8) + 16, blink("1.1s")))
    o.append('<path fill="#c9ccd1" d="%s"/>' % (text_path("Backend developer by day.", 48, 146, 3, font=LOW)
                                                + text_path("NAS tinkerer by night.", 48, 182, 3, font=LOW)))
    o.append('<path fill="#c9ccd1" d="%s"/>' % text_path("You hear the hum of a distant NAS.", X0, 48, S))
    parts = {}
    for r, line in enumerate(grid):
        for c, char in enumerate(line):
            if char in colors:
                parts.setdefault(colors[char], []).append(text_path(char, *cell(r, c), S))
    o.extend('<path fill="%s" d="%s"/>' % (color, "".join(d)) for color, d in parts.items())
    # The gold lies on the floor until the @ walks over it.
    o.append('<g><path fill="#d7a54a" d="%s"/><animate attributeName="opacity" values="1;0;1" keyTimes="0;%s;.98" '
             'dur="8s" calcMode="discrete" repeatCount="indefinite"/></g>' % (text_path("$", *cell(2, 27), S), pick))
    o.append('<g opacity="0"><path fill="#353a42" d="%s"/><animate attributeName="opacity" values="0;1;0" '
             'keyTimes="0;%s;.98" dur="8s" calcMode="discrete" repeatCount="indefinite"/></g>'
             % (text_path(".", *cell(2, 27), S), pick))
    x0, y0 = cell(0, 0)
    o.append('<g><rect x="%d" y="%d" width="%d" height="%d" fill="#0d0f12"/><path fill="#f2f2f2" d="%s"/>'
             '<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="8s" '
             'calcMode="discrete" repeatCount="indefinite"/></g>'
             % (x0 - 1, y0 - 2, CW, CH, text_path("@", x0, y0, S),
                ";".join("%d %d" % (c * CW, r * CH) for r, c in path),
                ";".join("%.2f" % (k * .02) for k in range(len(path)))))
    o.append('<rect x="48" y="226" width="1104" height="2" fill="#23272e"/>')
    o.append('<path fill="#c9ccd1" d="%s"/>' % text_path("ShoraiK the Tinkerer", 48, 244, S))
    o.append('<path fill="#6f7680" d="%s"/>' % text_path("Dlvl:2  HP:42(42)", 1152, 244, S, "end"))
    o.append("</svg>")
    return "".join(o)


def banner_nightshift():
    """Late-80s Japanese computer look: a dark room at night, rain on the window, a monitor scrolling logs, a NAS."""
    random.seed(5)
    W, H = 1200, 300
    line = "Still up. The NAS is humming."
    o = [svg_open(W, H)]
    o.append('<defs>' + dither("dw", "#141129", "#1d1838") + dither("ds1", "#1b1740", "#2b2260")
             + dither("ds2", "#2b2260", "#4a2f73")
             + '<clipPath id="glass"><rect x="652" y="40" width="476" height="152"/></clipPath>'
             '<clipPath id="screen"><rect x="312" y="120" width="144" height="72"/></clipPath>'
             '<radialGradient id="glow"><stop offset="0" stop-color="#7cc4a8" stop-opacity=".22"/>'
             '<stop offset="1" stop-color="#7cc4a8" stop-opacity="0"/></radialGradient>'
             + typewriter("say", line, 64, 252, 3, .05, .95, .02) + '</defs>')
    o.append('<rect width="%d" height="%d" fill="#141129"/><rect y="110" width="%d" height="60" fill="url(#dw)"/>'
             '<rect y="170" width="%d" height="%d" fill="#1d1838"/>' % (W, H, W, W, H - 170))
    o.append('<ellipse cx="384" cy="156" rx="250" ry="150" fill="url(#glow)"/>')

    # Window: dithered sky, moon, city lights and rain.
    o.append('<rect x="640" y="28" width="500" height="176" fill="#2e2858"/><g clip-path="url(#glass)">'
             '<rect x="652" y="40" width="476" height="152" fill="#1b1740"/>'
             '<rect x="652" y="90" width="476" height="30" fill="url(#ds1)"/>'
             '<rect x="652" y="120" width="476" height="30" fill="#2b2260"/>'
             '<rect x="652" y="150" width="476" height="42" fill="url(#ds2)"/>'
             '<circle cx="1062" cy="72" r="16" fill="#efe6cc"/><circle cx="1070" cy="66" r="14" fill="#1b1740"/>')
    x = 652
    while x < 1128:
        w, h = random.randrange(24, 60, 4), random.randrange(36, 112, 4)
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#100d22"/>' % (x, 192 - h, w, h))
        for wy in range(200 - h, 186, 10):
            for wx in range(x + 6, x + w - 8, 10):
                if random.random() < .22:
                    flicker = ('<animate attributeName="opacity" values="1;.2;1" dur="%.1fs" begin="%.1fs" '
                               'repeatCount="indefinite"/>' % (random.uniform(3, 9), random.uniform(0, 6))
                               if random.random() < .3 else "")
                    o.append('<rect x="%d" y="%d" width="4" height="4" fill="%s">%s</rect>'
                             % (wx, wy, random.choice(("#e7c07a", "#e7c07a", "#7cc4a8")), flicker))
        x += w + random.randrange(0, 12, 4)
    for _ in range(36):
        dur = random.uniform(.6, 1.1)
        o.append('<rect x="%d" y="0" width="2" height="12" fill="#a9a1d6" fill-opacity=".45"><animateTransform '
                 'attributeName="transform" type="translate" from="0 20" to="0 200" dur="%.2fs" begin="-%.2fs" '
                 'repeatCount="indefinite"/></rect>' % (random.randrange(654, 1126, 2), dur, random.uniform(0, dur)))
    o.append('</g><rect x="887" y="40" width="6" height="152" fill="#2e2858"/>'
             '<rect x="652" y="104" width="476" height="6" fill="#2e2858"/>'
             '<rect x="630" y="204" width="520" height="8" fill="#3a3170"/>')

    # Desk: a plant, a monitor scrolling logs one line at a time, and a NAS with its LEDs.
    o.append('<rect x="40" y="206" width="560" height="10" fill="#3a3170"/>'
             '<rect x="40" y="216" width="560" height="84" fill="#221c44"/>')
    o.append(sprite(PLANT, PLANT_COLORS, 200, 174, 4))
    o.append('<rect x="300" y="110" width="168" height="96" fill="#3b3466"/>'
             '<rect x="306" y="114" width="156" height="86" fill="#2e2858"/>'
             '<rect x="312" y="120" width="144" height="72" fill="#0f2a2a"/>')
    widths = [random.choice((40, 56, 72, 88, 104, 120)) for _ in range(12)]
    logs = "".join("M320 %dh%dv4h-%dz" % (126 + k * 9, w, w) for k, w in enumerate(widths * 2))
    o.append('<g clip-path="url(#screen)"><path fill="#7cc4a8" d="%s"><animateTransform attributeName="transform" '
             'type="translate" values="%s" dur="7.2s" calcMode="discrete" repeatCount="indefinite"/></path></g>'
             % (logs, ";".join("0 -%d" % (9 * k) for k in range(12))))
    o.append('<rect x="488" y="146" width="60" height="60" fill="#2b2550"/>'
             '<rect x="496" y="154" width="44" height="14" fill="#1a1633"/>'
             '<rect x="496" y="174" width="44" height="14" fill="#1a1633"/>'
             '<rect x="496" y="196" width="4" height="4" fill="#7cc4a8"/>')
    for y, values, dur in ((159, "1;.15;1;1;.15;1;1", "1.3s"), (179, "1;1;.15;1;.15;1", ".9s")):
        o.append('<rect x="530" y="%d" width="4" height="4" fill="#7ee08a"><animate attributeName="opacity" '
                 'values="%s" dur="%s" calcMode="discrete" repeatCount="indefinite"/></rect>' % (y, values, dur))

    # Title, and a dialogue box with the line typed out.
    title = text_path("ShoraiK", 48, 30, 6)
    o.append('<path fill="#0a0918" transform="translate(4 4)" d="%s"/><path fill="#e7c07a" d="%s"/>' % (title, title))
    o.append('<path fill="#8e86b3" d="%s"/>' % text_path("backend developer by day · NAS tinkerer by night", 48, 84, 2,
                                                          font=LOW))
    o.append('<rect x="40" y="232" width="1120" height="56" fill="#0a0918" fill-opacity=".9" stroke="#8e86b3" '
             'stroke-width="2"/><rect x="60" y="218" width="128" height="26" fill="#2b2550" stroke="#8e86b3" '
             'stroke-width="2"/>')
    o.append('<path fill="#e7c07a" d="%s"/>' % text_path("ShoraiK", 124, 224, 2, "middle"))
    o.append('<path fill="#e2dcf2" clip-path="url(#say)" d="%s"/>' % text_path(line, 64, 252, 3, font=LOW))
    o.append('<g opacity="0"><g><path fill="#e7c07a" d="%s"/>%s</g><animate attributeName="opacity" values="0;1;0" '
             'keyTimes="0;.62;.95" dur="8s" calcMode="discrete" repeatCount="indefinite"/></g>'
             % (text_path("▼", 64 + width(line, 3) + 14, 260, 2), blink(".9s")))
    o.append("</svg>")
    return "".join(o)


# The cards are drawn in the synthwave palette; the other designs swap its colours.
CARD_COLORS = {
    "2-dungeon": {"#160d2e": "#0d0f12", "#ff4f8b": "#2a2e35", "#7c5cff": "#4a4f57", "#ffd76a": "#d7a54a",
                  "#ff7eb6": "#e8e6e3", "#2a0f45": "#000000", "#e8e3ff": "#c9ccd1", "#a99bff": "#6f7680",
                  "#2a1d52": "#171a1f", "#5ee6a0": "#7fb069", "#7cc6ff": "#6c9bd2", "#ffffff": "#e8e6e3"},
    "3-nightshift": {"#160d2e": "#14122b", "#ff4f8b": "#3a3170", "#7c5cff": "#6a5fa0", "#ffd76a": "#e7c07a",
                     "#ff7eb6": "#d98fa3", "#2a0f45": "#0a0918", "#e8e3ff": "#d8d3e8", "#a99bff": "#8e86b3",
                     "#2a1d52": "#1e1a3a", "#5ee6a0": "#7cc4a8", "#7cc6ff": "#8fb3e0", "#ffffff": "#f1ecff"},
}


def themed(svg, colors):
    """Recolour a card drawn in the synthwave palette."""
    return re.sub(r"#[0-9a-f]{6}", lambda m: colors.get(m.group(0), m.group(0)), svg)


def card_open(W, H, label):
    """Start a nightshift card: its frame, and the gradient its buttons glow with."""
    return ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'shape-rendering="crispEdges" role="img" aria-label="%s">' % (W, H, W, H, label),
            '<defs><linearGradient id="t" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd76a"/>'
            '<stop offset="1" stop-color="#ff7eb6"/></linearGradient></defs>',
            '<rect width="%d" height="%d" fill="#160d2e"/>' % (W, H),
            '<rect x="4" y="4" width="%d" height="%d" fill="none" stroke="#ff4f8b" stroke-width="8"/>' % (W - 8, H - 8),
            '<rect x="16" y="16" width="%d" height="%d" fill="none" stroke="#7c5cff" stroke-width="4"/>'
            % (W - 32, H - 32)]


def card_title(mark, title, x, y):
    """The blinking mark and the title of a card."""
    return ('<g><path fill="#ffd76a" d="%s"/>%s</g><path fill="#ffd76a" d="%s"/>'
            % (text_path(mark, x, y, 3), blink("1.6s", ".3;1"), text_path(title, x + 24, y, 3)))


def button_width(icon, label, s):
    return width(icon + " " + label, s) + 36


def button(icon, label, x, y, s, font=FONT):
    """A button with a glowing border: the icon in gold, then the label in white."""
    w = button_width(icon, label, s)
    return ('<rect x="%d" y="%d" width="%d" height="36" fill="url(#t)"><animate attributeName="opacity" '
            'values="1;.35;1" dur="2s" repeatCount="indefinite"/></rect><rect x="%d" y="%d" width="%d" height="28" '
            'fill="#2a1d52"/><path fill="#ffd76a" d="%s"/><path fill="#ffffff" d="%s"/>'
            % (x, y, w, x + 4, y + 4, w - 8, text_path(icon, x + 18, y + 11, s),
               text_path(label, x + 18 + 10 * s, y + 11, s, font=font)))


def stack_trace(mark="◆"):
    """The stack as a joke Java stack trace: the AI could not replace the developer, and offers to fix its own bug."""
    W, H, S = 1200, 250, 2
    dim, text, error, link = "#a99bff", "#e8e3ff", "#ff7eb6", "#7cc6ff"
    o = card_open(W, H, "Stack trace")
    o.append(card_title(mark, "STACK TRACE", 44, 40))
    # The AI's own button, eager to fix what the AI broke.
    o.append(button("✦", "FIX WITH AI", 1150 - button_width("✦", "FIX WITH AI", S), 32, S))
    lines =[[('Exception in thread "main" ai.ReplacementException: could not replace developer - no Session', error)]]
    for where, source in (("backend.Java.spring", "Hibernate.java:42"), ("side.Python.javaScript", "Linux.java:7"),
                          ("home.SelfHosting.nas", "Uptime.java:247")):
        lines.append([("    at ", dim), (where, text), ("(", dim), (source, link), (")", dim)])
    lines += [[("Caused by: ai.HallucinationException: Spring.makeItWork() does not exist", error)],
              [("    ... 3 more", dim)]]
    for k, line in enumerate(lines):
        x, y = 44, 80 + 24 * k
        o.append("<g>")
        for part, color in line:
            o.append('<path fill="%s" d="%s"/>' % (color, text_path(part, x, y, S, font=LOW)))
            if color == link:  # file names are underlined links, as in an IDE console
                o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (x, y + 16, width(part, S), S, link))
            x += width(part, S) + S
        # The trace prints one line at a time when the image loads.
        o.append('<set attributeName="opacity" to="0" dur="%.1fs"/></g>' % (.4 + .3 * k))
    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#ffffff">%s<set attributeName="opacity" to="0" '
             'dur="%.1fs"/></rect>' % (x + 4 * S, y, 5 * S, 7 * S, blink("1s"), .4 + .3 * len(lines)))
    o.append("</svg>")
    return "".join(o)


def leader(label, value, x0, x1, y, s, color):
    """A report line: the label, a dotted leader and the value flush right."""
    start, end = x0 + width(label, s) + 3 * s, x1 - width(value, s) - 3 * s
    dots = "".join("M%d %dh%dv%dh-%dz" % (x, y + 6 * s, s, s, s) for x in range(start, end - s + 1, 3 * s))
    return ('<path fill="#e8e3ff" d="%s"/><path fill="#a99bff" d="%s"/><path fill="%s" d="%s"/>'
            % (text_path(label, x0, y, s, font=LOW), dots, color, text_path(value, x1, y, s, "end", LOW)))


def report(data, mark="◆"):
    """The GitHub numbers as a shift report; .github/workflows/report.yml redraws it every night."""
    W, H, S, gold = 1200, 250, 2, "#ffd76a"
    o = card_open(W, H, "Shift report")
    o.append(card_title(mark, "SHIFT REPORT", 44, 40))
    o.append('<path fill="#a99bff" d="%s"/>'
             % text_path("// github stats · updated nightly by cron", 1150, 44, S, "end", LOW))
    left = [leader(label, str(value), 44, 560, 80 + 24 * k, S, gold) for k, (label, value) in enumerate((
        ("COMMITS (LAST YEAR)", data["commits"]), ("CONTRIBUTIONS (LAST YEAR)", data["contributions"]),
        ("PUBLIC REPOS", data["repos"]), ("STARS EARNED", data["stars"]), ("ON GITHUB SINCE", data["since"])))]
    # The languages: a bar that fills up when its line prints (one segment per top language, then the rest),
    # and the top three under it.
    total = sum(size for _, size in data["languages"]) or 1
    top = list(zip(data["languages"][:3], ("#ff7eb6", "#7cc6ff", "#5ee6a0")))
    rest = total - sum(size for (_, size), _ in top)
    bar, done = ['<rect x="640" y="104" width="510" height="14" fill="#2a1d52"/><g clip-path="url(#fill)">'], 0
    for size, color in [(size, color) for (_, size), color in top] + [(rest, "#a99bff")]:
        x0, done = 640 + round(510 * done / total), done + size
        x1 = 640 + round(510 * done / total) - (S if done < total else 0)
        if x1 > x0:
            bar.append('<rect x="%d" y="104" width="%d" height="14" fill="%s"/>' % (x0, x1 - x0, color))
    bar.append("</g>")
    right = ['<path fill="#e8e3ff" d="%s"/>' % text_path("LANGUAGES BY CODE SIZE", 640, 80, S, font=LOW), "".join(bar)]
    for k, ((name, size), color) in enumerate(top):
        name = "".join(c for c in name.upper() if c in LOW or c == " ")
        right.append('<rect x="640" y="%d" width="10" height="10" fill="%s"/>%s'
                     % (130 + 24 * k, color, leader(name, "%d%%" % round(100 * size / total), 658, 1150,
                                                    128 + 24 * k, S, gold)))
    o.append('<defs><clipPath id="fill"><rect x="640" y="104" width="0" height="14"><animate attributeName="width" '
             'from="0" to="510" begin=".65s" dur="1s" fill="freeze"/></rect></clipPath></defs>')
    # The report prints one line at a time when the image loads, both columns together.
    for k in range(5):
        o.append('<g>%s%s<set attributeName="opacity" to="0" dur="%gs"/></g>'
                 % (left[k], right[k] if k < len(right) else "", .4 + .25 * k))
    o.append("</svg>")
    return "".join(o)


def connect(mark="◆"):
    """The closing card: a button to the GitHub profile, and a backend promise under it."""
    W, H, S = 600, 176, 2
    o = card_open(W, H, "Let's connect")
    o.append(card_title(mark, "LET'S CONNECT", (W - 24 - width("LET'S CONNECT", 3)) // 2, 36))
    o.append(button("▶", "github.com/ShoraiK", (W - button_width("▶", "github.com/ShoraiK", S)) // 2, 74, S, LOW))
    o.append('<path fill="#a99bff" d="%s"/>'
             % text_path("replies are eventually consistent", W // 2, 126, S, "middle", LOW))
    o.append("</svg>")
    return "".join(o)


def fetch_report(login):
    """The numbers for the report, from the GitHub GraphQL API (the Action passes its token in GITHUB_TOKEN)."""
    query = """query($login: String!) { user(login: $login) { createdAt
      repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) { totalCount
        nodes { stargazerCount languages(first: 20) { edges { size node { name } } } } }
      contributionsCollection { totalCommitContributions contributionCalendar { totalContributions } } } }"""
    request = urllib.request.Request(
        "https://api.github.com/graphql", json.dumps({"query": query, "variables": {"login": login}}).encode(),
        {"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "User-Agent": "profile-report"})
    with urllib.request.urlopen(request, timeout=30) as response:
        answer = json.load(response)
    if answer.get("errors") or not (answer.get("data") or {}).get("user"):
        sys.exit("GitHub did not return the numbers: %s" % answer)
    user = answer["data"]["user"]
    repos, sizes = user["repositories"], {}
    for repo in repos["nodes"]:
        for edge in repo["languages"]["edges"]:
            sizes[edge["node"]["name"]] = sizes.get(edge["node"]["name"], 0) + edge["size"]
    contributions = user["contributionsCollection"]
    return {"commits": contributions["totalCommitContributions"],
            "contributions": contributions["contributionCalendar"]["totalContributions"],
            "repos": repos["totalCount"], "stars": sum(repo["stargazerCount"] for repo in repos["nodes"]),
            "since": user["createdAt"][:4], "languages": sorted(sizes.items(), key=lambda item: -item[1])}


# Numbers for the local preview only; the Action draws the real report.
SAMPLE = {"commits": 14, "contributions": 17, "repos": 4, "stars": 10, "since": "2015",
          "languages": [("Python", 270569), ("JavaScript", 150759), ("CSS", 31540), ("HTML", 15406)]}


README = """<p align="center">
  <img src="assets/banner.svg" width="100%" alt="Pixel-art banner: a white-haired hero runs through a synthwave night, jumps over a slime and grabs a coin under the title ShoraiK: backend dev by day, NAS tinkerer by night.">
</p>

<p align="center">
  <b>Player 1 has joined.</b> Backend developer by trade; after hours, I build my own tools for my NAS.
</p>

<p align="center">
  <img src="assets/stats.svg" width="100%" alt="Player stats. Class: backend developer. Main skills: Java, Spring, Hibernate. Side skills: Python, JavaScript, Linux, self-hosting.">
</p>

<p align="center">
  <a href="https://github.com/ShoraiK/NASpeed">
    <img src="assets/naspeed.svg" width="100%" alt="Featured quest: NASpeed, a multi-provider speed test for TerraMaster TOS 7, with Cloudflare, Ookla, M-Lab and LibreSpeed.">
  </a>
</p>
"""

SYNTH_ALT = ("Pixel-art banner: a white-haired hero runs through a synthwave night, jumps over a slime and grabs a coin "
             "under the title ShoraiK: backend dev by day, NAS tinkerer by night.")
# The sober designs drop the game wording from the README.
PLAIN_README = (("<b>Player 1 has joined.</b> ", ""),
                ("Player stats. Class: backend developer. Main skills: Java, Spring, Hibernate. Side skills: Python, "
                 "JavaScript, Linux, self-hosting.",
                 "Stack. Role: backend developer. Main: Java, Spring, Hibernate. Side: Python, JavaScript, Linux, "
                 "self-hosting."),
                ("Featured quest: NASpeed", "Project: NASpeed"))
for old in (SYNTH_ALT,) + tuple(pair[0] for pair in PLAIN_README):
    assert old in README, old
# The nightshift design swaps the stack card for a joke stack trace.
OWN_STATS = {
    "3-nightshift": (stack_trace,
                     "A joke Java stack trace. Exception in thread main: ai.ReplacementException: could not replace "
                     "developer, no Session. At backend Java, Spring and Hibernate; at side Python, JavaScript and "
                     "Linux; at home self-hosting on a NAS. Caused by ai.HallucinationException: Spring.makeItWork() "
                     "does not exist. In the corner, a Fix with AI button glows."),
}
# The nightshift design ends with the shift report and a card to connect, not the project card. The report lives
# on the report branch, where the Action redraws it every night without adding commits to main.
REPORT_URL = "https://raw.githubusercontent.com/ShoraiK/ShoraiK/report/report.svg"
NASPEED_START = '<p align="center">\n  <a href="https://github.com/ShoraiK/NASpeed">'
NIGHTSHIFT_END = """<p align="center">
  <img src="%s" width="100%%" alt="Shift report with my GitHub numbers, redrawn every night: commits and contributions in the last year, public repositories, stars earned, the year I joined, and my top languages by code size.">
</p>

<p align="center">
  <a href="https://github.com/ShoraiK">
    <img src="assets/connect.svg" width="50%%" alt="Let's connect: a button to github.com/ShoraiK. Under it: replies are eventually consistent.">
  </a>
</p>
""" % REPORT_URL
assert NASPEED_START in README
DESIGNS = {
    "1-synthwave": (banner, None, SYNTH_ALT),
    "2-dungeon": (banner_dungeon, ">",
                  "Pixel-art banner styled like a terminal roguelike: the name ShoraiK with a blinking cursor, and a "
                  "small ASCII dungeon where the @ crosses three rooms to the stairs. The message line says: You hear "
                  "the hum of a distant NAS."),
    "3-nightshift": (banner_nightshift, "◆",
                     "Pixel-art banner in the style of late-80s Japanese computers: a dark room at night with rain on "
                     "the window, a monitor scrolling logs and a NAS blinking on the desk. A dialogue box says: Still "
                     "up. The NAS is humming."),
}
PICK = "3-nightshift"  # the design written to the root, which is what GitHub shows on the profile
PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Profile designs</title><style>
body{margin:0;padding:8px 24px 24px;background:#0d1117;color:#e6edf3;
font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}
h2{max-width:830px;margin:24px auto 8px;font-size:16px}
.b{max-width:830px;margin:0 auto;border:1px solid #30363d;border-radius:6px;padding:24px}
.b img{max-width:100%}.b p{margin:0 0 16px}
</style></head><body>{sections}</body></html>"""

def main(preview):
    sections = []
    for name, (make_banner, mark, alt) in DESIGNS.items():
        if mark is None:  # the first design, exactly as it was
            readme, files = README, {"banner.svg": banner(), "stats.svg": stats(), "naspeed.svg": card()}
        else:
            readme = README.replace(SYNTH_ALT, alt)
            for old, new in PLAIN_README:
                readme = readme.replace(old, new)
            make_stats, stats_alt = OWN_STATS.get(name, (None, None))
            if make_stats:
                readme = readme.replace(PLAIN_README[1][1], stats_alt)
            stats_svg = make_stats(mark) if make_stats else stats(mark, "STACK", ("ROLE", "MAIN", "SIDE"), False)
            files = {"banner.svg": make_banner(), "stats.svg": themed(stats_svg, CARD_COLORS[name])}
            if name == "3-nightshift":
                readme = readme[:readme.index(NASPEED_START)] + NIGHTSHIFT_END
                files["connect.svg"] = themed(connect(mark), CARD_COLORS[name])
            else:
                files["naspeed.svg"] = themed(card(mark, "PROJECT", "▶ VIEW REPO"), CARD_COLORS[name])
        targets = [OUT / "designs" / name] + ([OUT] if name == PICK else []) + ([preview / name] if preview else [])
        for target in targets:
            (target / "assets").mkdir(parents=True, exist_ok=True)
            for file, svg in files.items():
                (target / "assets" / file).write_text(svg, encoding="utf-8", newline="\n")
            (target / "README.md").write_text(readme, encoding="utf-8", newline="\n")
        sections.append('<h2>%s</h2><div class="b">%s</div>'
                        % (name, readme.replace('src="assets/', 'src="%s/assets/' % name)
                           .replace(REPORT_URL, "%s/assets/report.svg" % name)))
    if preview:
        # The Action draws the real report; the preview draws it with sample numbers.
        (preview / "3-nightshift" / "assets" / "report.svg").write_text(
            themed(report(SAMPLE), CARD_COLORS["3-nightshift"]), encoding="utf-8", newline="\n")
        (preview / "index.html").write_text(PAGE.replace("{sections}", "".join(sections)), encoding="utf-8")
    for path in sorted(OUT.glob("**/*.svg")) + sorted(OUT.glob("**/README.md")):
        print(path.relative_to(OUT).as_posix(), path.stat().st_size)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--report"]:
        drawn = report(fetch_report(os.environ.get("GITHUB_REPOSITORY_OWNER", "ShoraiK")))
        pathlib.Path(sys.argv[2]).write_text(themed(drawn, CARD_COLORS["3-nightshift"]), encoding="utf-8",
                                             newline="\n")
    else:
        main(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None)
