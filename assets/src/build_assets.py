"""Generate the animated SVG assets used by the profile README.

Run from anywhere:  python assets/src/build_assets.py
Every SVG is self-contained (no external fonts/scripts) so GitHub renders it
inside an <img> tag. Animations use SMIL, which GitHub's image proxy keeps.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent

# ── palette ────────────────────────────────────────────────────────────────
INK = "#12000C"
BG0 = "#1D0014"
BG1 = "#2C001E"
AUB = "#5E2750"
AUB2 = "#77216F"
ORG = "#E95420"
PEACH = "#F2A47F"
CREAM = "#F5F1EA"
GREY = "#AEA79F"

SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"


def svg(w: int, h: int, body: str, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(label)}">\n<title>{escape(label)}</title>\n{body}\n</svg>\n'
    )


def common_defs() -> str:
    return f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{INK}"/><stop offset=".5" stop-color="{BG1}"/><stop offset="1" stop-color="#3D0F33"/>
</linearGradient>
<linearGradient id="hot" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{ORG}"/><stop offset=".55" stop-color="{PEACH}"/><stop offset="1" stop-color="{CREAM}"/>
</linearGradient>
<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{ORG}"/><stop offset=".6" stop-color="{AUB}"/><stop offset="1" stop-color="{AUB}" stop-opacity="0"/>
</linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{ORG}" stop-opacity=".35"/><stop offset="1" stop-color="{ORG}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glowA" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{AUB2}" stop-opacity=".45"/><stop offset="1" stop-color="{AUB2}" stop-opacity="0"/>
</radialGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
  <circle cx="1.5" cy="1.5" r="1.1" fill="{GREY}" fill-opacity=".13"/>
</pattern>
<filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="blur3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
"""


def frame(w: int, h: int, r: int = 18) -> str:
    """Opaque rounded card with dot grid, so assets read well in light and dark GitHub themes."""
    return (
        f'<clipPath id="card"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>\n'
        f'<g clip-path="url(#card)">\n<rect width="{w}" height="{h}" fill="url(#bg)"/>\n'
        f'<rect width="{w}" height="{h}" fill="url(#dots)"/>\n'
    )


def frame_end(w: int, h: int, r: int = 18) -> str:
    return f'</g>\n<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{r}" fill="none" stroke="{AUB}" stroke-width="1.5"/>'


def border_runner(w: int, h: int, r: int = 18, dur: float = 7, begin: float = 0) -> str:
    """A bright segment that races around the card border."""
    return (
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{r}" fill="none" stroke="url(#hot)" '
        f'stroke-width="2" pathLength="1000" stroke-dasharray="140 860" stroke-linecap="round">'
        f'<animate attributeName="stroke-dashoffset" from="1000" to="0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></rect>'
    )


def hud_corners(w: int, h: int, pad: int = 18, size: int = 22) -> str:
    s = []
    for x, y, dx, dy in [(pad, pad, 1, 1), (w - pad, pad, -1, 1), (pad, h - pad, 1, -1), (w - pad, h - pad, -1, -1)]:
        s.append(
            f'<path d="M{x},{y + dy*size} V{y} H{x + dx*size}" fill="none" stroke="{ORG}" stroke-width="2" stroke-opacity=".8"/>'
        )
    return "\n".join(s)


# ── HERO ───────────────────────────────────────────────────────────────────
def hero() -> str:
    W, H = 1200, 440
    rnd = random.Random(7)
    layers = [4, 6, 7, 6, 3]
    x0, x1, y0, y1 = 760, 1120, 92, 352
    nodes: list[list[tuple[float, float]]] = []
    for li, n in enumerate(layers):
        x = x0 + (x1 - x0) * li / (len(layers) - 1)
        gap = (y1 - y0) / (max(layers) - 1)
        top = (y0 + y1) / 2 - gap * (n - 1) / 2
        nodes.append([(x, top + gap * k) for k in range(n)])

    edges = []
    for li in range(len(layers) - 1):
        for a in nodes[li]:
            for b in nodes[li + 1]:
                op = rnd.uniform(0.06, 0.22)
                edges.append(
                    f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GREY}" stroke-opacity="{op:.2f}" stroke-width="1"/>'
                )

    # signal pulses travelling input → output along random paths
    pulses = []
    for i in range(16):
        pts = [rnd.choice(layer) for layer in nodes]
        d = "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        dur = 2.6
        begin = i * 0.42
        col = ORG if i % 3 else PEACH
        pulses.append(
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.6" stroke-opacity="0" stroke-linecap="round">'
            f'<animate attributeName="stroke-opacity" values="0;.55;0" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/></path>'
            f'<circle r="3.6" fill="{CREAM}" opacity="0"><animateMotion path="{d}" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>'
        )

    node_svg = []
    for li, layer in enumerate(nodes):
        for k, (x, y) in enumerate(layer):
            b = li * 0.35 + k * 0.05
            node_svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{ORG}" opacity="0" filter="url(#blur3)">'
                f'<animate attributeName="opacity" values="0;.55;0" dur="2.6s" begin="{b:.2f}s" repeatCount="indefinite"/></circle>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="{BG1}" stroke="{ORG}" stroke-width="2"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PEACH}">'
                f'<animate attributeName="r" values="2;4;2" dur="2.6s" begin="{b:.2f}s" repeatCount="indefinite"/></circle>'
            )
    labels = ["INPUT", "EMBED", "HIDDEN", "ATTN", "OUTPUT"]
    for li, lab in enumerate(labels):
        x = nodes[li][0][0]
        node_svg.append(
            f'<text x="{x:.1f}" y="392" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{GREY}" fill-opacity=".7">{lab}</text>'
        )

    cmd = "$ python evaluate.py --bootstrap 10000 --ci 0.95"
    body = f"""<defs>{common_defs()}
<clipPath id="type"><rect x="80" y="296" height="30" width="0">
  <animate attributeName="width" values="0;0;560;560" keyTimes="0;.08;.45;1" dur="9s" repeatCount="indefinite"/></rect></clipPath>
</defs>
{frame(W, H, 22)}
<circle cx="940" cy="220" r="330" fill="url(#glow)"><animate attributeName="r" values="300;350;300" dur="7s" repeatCount="indefinite"/></circle>
<circle cx="120" cy="40" r="300" fill="url(#glowA)"/>
<g>{''.join(edges)}</g>
<g>{''.join(pulses)}</g>
<g>{''.join(node_svg)}</g>

<!-- status line -->
<g font-family="{MONO}" font-size="12" letter-spacing="1.2">
  <circle cx="86" cy="62" r="5" fill="{ORG}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
  <text x="100" y="66" fill="{PEACH}">SYSTEM ONLINE</text>
  <text x="222" y="66" fill="{GREY}" fill-opacity=".75">·  MACHINE LEARNING ENGINEERING PORTFOLIO</text>
</g>

<!-- identity -->
<text x="78" y="168" font-family="{SANS}" font-size="82" font-weight="800" letter-spacing="-1.5" fill="{CREAM}">Blevis</text>
<text x="78" y="246" font-family="{SANS}" font-size="82" font-weight="800" letter-spacing="-1.5" fill="url(#hot)">Allushi</text>
<text x="82" y="282" font-family="{SANS}" font-size="20" fill="{CREAM}" fill-opacity=".82">Artificial Intelligence student  ·  Machine Learning  ·  NLP  ·  Deep Learning</text>

<!-- typed command -->
<g font-family="{MONO}" font-size="16">
  <text x="82" y="318" fill="{PEACH}" clip-path="url(#type)">{escape(cmd)}</text>
</g>
<!-- training progress -->
<g font-family="{MONO}" font-size="13" fill="{GREY}">
  <text x="82" y="352">resample</text>
  <rect x="158" y="341" width="280" height="12" rx="6" fill="{AUB}" fill-opacity=".55"/>
  <rect x="158" y="341" width="0" height="12" rx="6" fill="url(#hot)">
    <animate attributeName="width" values="0;0;280;280" keyTimes="0;.45;.85;1" dur="9s" repeatCount="indefinite"/></rect>
  <text x="452" y="352" fill="{ORG}" opacity="0">
    <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;.84;.86;1" dur="9s" repeatCount="indefinite"/>10000/10000 ✓ 95% CI ready</text>
</g>

{hud_corners(W, H)}
<rect x="0" y="{H-3}" width="{W}" height="3" fill="url(#rule)"/>
<circle cy="{H-1.5}" r="10" fill="{ORG}" filter="url(#blur8)"><animate attributeName="cx" values="-40;{W+40}" dur="6s" repeatCount="indefinite"/></circle>
{frame_end(W, H, 22)}"""
    return svg(W, H, body, "Blevis Allushi — Artificial Intelligence student focused on machine learning, NLP and deep learning")


# ── SECTION HEADERS ────────────────────────────────────────────────────────
def header(num: str, title: str, sub: str) -> str:
    W, H = 1200, 84
    tx = 150
    body = f"""<defs>{common_defs()}
<linearGradient id="ruleR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AUB}" stop-opacity="0"/><stop offset=".5" stop-color="{AUB}"/><stop offset="1" stop-color="{ORG}"/></linearGradient>
</defs>
{frame(W, H, 14)}
<text x="34" y="54" font-family="{MONO}" font-size="30" font-weight="700" fill="url(#hot)">{num}</text>
<rect x="104" y="22" width="2" height="40" fill="{AUB}"/>
<text x="{tx-22}" y="47" font-family="{SANS}" font-size="26" font-weight="800" letter-spacing="3" fill="{CREAM}">{escape(title)}</text>
<text x="{tx-21}" y="68" font-family="{MONO}" font-size="12.5" fill="{GREY}" fill-opacity=".85">{escape(sub)}</text>
<rect x="640" y="41" width="520" height="2" fill="url(#ruleR)"/>
<circle cy="42" r="3.5" fill="{CREAM}"><animate attributeName="cx" values="1160;640;1160" dur="8s" repeatCount="indefinite"/></circle>
<circle cy="42" r="9" fill="{ORG}" filter="url(#blur3)"><animate attributeName="cx" values="1160;640;1160" dur="8s" repeatCount="indefinite"/></circle>
{frame_end(W, H, 14)}"""
    return svg(W, H, body, f"{num} {title}")


# ── TERMINAL / ABOUT ───────────────────────────────────────────────────────
def terminal() -> str:
    W, H = 600, 420
    P, K, V, C, G = PEACH, ORG, CREAM, GREY, "#9BD18B"
    lines = [
        [(P, "❯ "), (V, "whoami")],
        [(V, "Blevis Allushi — AI student, ML builder")],
        [],
        [(P, "❯ "), (V, "cat profile.yaml")],
        [(K, "focus:    "), (V, "[ml, nlp, deep-learning]")],
        [(K, "toolkit:  "), (V, "[python, scikit-learn, spacy,")],
        [(K, "          "), (V, " pandas, numpy, jupyter]")],
        [(K, "values:   "), (V, "reproducible > impressive")],
        [(K, "          "), (V, "honest evals > leaderboard luck")],
        [(K, "now:      "), (V, "statistical ML + NLP")],
        [],
        [(P, "❯ "), (V, "pytest -q")],
        [(G, "✓ all checks passed"), (C, "  # ship it")],
    ]
    rows = []
    y = 92
    for i, segs in enumerate(lines):
        if segs:
            spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for c, t in segs)
            rows.append(
                f'<text x="30" y="{y}" opacity="0" xml:space="preserve">{spans}'
                f'<animate attributeName="opacity" from="0" to="1" dur=".25s" begin="{0.3 + i*0.28:.2f}s" fill="freeze"/></text>'
            )
        y += 23
    end = 0.3 + len(lines) * 0.28
    rows.append(
        f'<text x="30" y="{y}" xml:space="preserve"><tspan fill="{P}">❯ </tspan></text>'
        f'<rect x="50" y="{y-14}" width="9" height="18" fill="{ORG}" opacity="0">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" begin="{end:.2f}s" repeatCount="indefinite"/></rect>'
    )
    body = f"""<defs>{common_defs()}</defs>
{frame(W, H)}
<rect width="{W}" height="44" fill="{INK}" fill-opacity=".65"/>
<circle cx="26" cy="22" r="6" fill="#FF5F57"/><circle cx="46" cy="22" r="6" fill="#FEBC2E"/><circle cx="66" cy="22" r="6" fill="#28C840"/>
<text x="{W/2}" y="27" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{GREY}">blevis@ml-lab: ~/profile</text>
<g font-family="{MONO}" font-size="14.5">{''.join(rows)}</g>
{frame_end(W, H)}
{border_runner(W, H, dur=8)}"""
    return svg(W, H, body, "Terminal: Blevis Allushi profile — focus ML, NLP, deep learning; toolkit Python, scikit-learn, spaCy, pandas, NumPy, Jupyter")


# ── RADAR / FOCUS MAP ──────────────────────────────────────────────────────
def radar() -> str:
    W, H = 600, 420
    cx, cy, R = 300, 232, 132
    axes = [
        ("Machine Learning", 0.92),
        ("NLP", 0.86),
        ("Statistics", 0.88),
        ("Algorithms", 0.76),
        ("Software Eng.", 0.72),
        ("Deep Learning", 0.78),
    ]
    n = len(axes)
    ang = [(-90 + 360 * i / n) * math.pi / 180 for i in range(n)]

    def pt(i, r):
        return cx + r * math.cos(ang[i]), cy + r * math.sin(ang[i])

    rings = []
    for f in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{pt(i, R*f)[0]:.1f},{pt(i, R*f)[1]:.1f}" for i in range(n))
        rings.append(f'<polygon points="{pts}" fill="none" stroke="{AUB}" stroke-width="1" stroke-opacity="{0.5 + f*0.5:.2f}"/>')
    spokes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{pt(i, R)[0]:.1f}" y2="{pt(i, R)[1]:.1f}" stroke="{AUB}" stroke-width="1"/>' for i in range(n)
    )
    data = " ".join(f"{pt(i, R*v)[0] - cx:.1f},{pt(i, R*v)[1] - cy:.1f}" for i, (_, v) in enumerate(axes))
    dots = "".join(
        f'<circle cx="{pt(i, R*v)[0]-cx:.1f}" cy="{pt(i, R*v)[1]-cy:.1f}" r="4.5" fill="{CREAM}" stroke="{ORG}" stroke-width="2"/>'
        for i, (_, v) in enumerate(axes)
    )
    labels = []
    for i, (name, _) in enumerate(axes):
        x, y = pt(i, R + 26)
        c = math.cos(ang[i])
        anchor = "middle" if abs(c) < 0.2 else ("start" if c > 0 else "end")
        labels.append(
            f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="{anchor}" font-family="{SANS}" font-size="14" font-weight="600" fill="{CREAM}">{escape(name)}</text>'
        )
    body = f"""<defs>{common_defs()}
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ORG}" stop-opacity="0"/><stop offset="1" stop-color="{ORG}" stop-opacity=".35"/></linearGradient>
</defs>
{frame(W, H)}
<circle cx="{cx}" cy="{cy}" r="{R+40}" fill="url(#glow)"/>
<text x="28" y="40" font-family="{MONO}" font-size="12.5" letter-spacing="2" fill="{PEACH}">FOCUS MAP</text>
<text x="28" y="58" font-family="{MONO}" font-size="11" fill="{GREY}" fill-opacity=".8">where my hours go</text>
{''.join(rings)}{spokes}
<g transform="translate({cx} {cy})">
  <path d="M0,0 L{R},0 A{R},{R} 0 0,0 {R*math.cos(-0.6):.1f},{R*math.sin(-0.6):.1f} Z" fill="url(#sweep)">
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="5s" repeatCount="indefinite"/></path>
  <g>
    <animateTransform attributeName="transform" type="scale" values="0;1.04;1" keyTimes="0;.8;1" dur="1.4s" fill="freeze"/>
    <polygon points="{data}" fill="{ORG}" fill-opacity=".28" stroke="{ORG}" stroke-width="2.5" stroke-linejoin="round"/>
    {dots}
  </g>
</g>
{''.join(labels)}
{frame_end(W, H)}
{border_runner(W, H, dur=8, begin=4)}"""
    return svg(W, H, body, "Focus map radar: machine learning, NLP, statistics, algorithms, software engineering, deep learning")


# ── IMPACT NUMBERS ─────────────────────────────────────────────────────────
def impact() -> str:
    W, H = 1200, 190
    tiles = [
        ("836K", "rated chess games", "analysed for first-move advantage"),
        ("10K", "bootstrap replicates", "behind every reported interval"),
        ("21K", "word German corpus", "parsed with spaCy NER + deps"),
        ("90%", "fare-quote coverage", "target for NYC taxi pricing model"),
    ]
    tw = W / 4
    parts = []
    for i, (big, l1, l2) in enumerate(tiles):
        x = i * tw
        b = 0.2 + i * 0.25
        if i:
            parts.append(f'<rect x="{x:.0f}" y="36" width="1" height="118" fill="{AUB}"/>')
        parts.append(f"""<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".6s" begin="{b:.2f}s" fill="freeze"/>
<animateTransform attributeName="transform" type="translate" from="0 14" to="0 0" dur=".6s" begin="{b:.2f}s" fill="freeze"/>
<text x="{x+40:.0f}" y="92" font-family="{SANS}" font-size="58" font-weight="800" letter-spacing="-1" fill="url(#hot)">{big}</text>
<text x="{x+42:.0f}" y="124" font-family="{SANS}" font-size="16" font-weight="700" fill="{CREAM}">{escape(l1)}</text>
<text x="{x+42:.0f}" y="146" font-family="{MONO}" font-size="11.5" fill="{GREY}">{escape(l2)}</text>
</g>
<rect x="{x+42:.0f}" y="160" height="3" rx="1.5" width="0" fill="{ORG}"><animate attributeName="width" from="0" to="{tw-90:.0f}" dur="1.2s" begin="{b+0.3:.2f}s" fill="freeze"/></rect>""")
    body = f"""<defs>{common_defs()}</defs>
{frame(W, H)}
<circle cx="600" cy="95" r="420" fill="url(#glowA)"/>
{''.join(parts)}
{frame_end(W, H)}"""
    return svg(W, H, body, "By the numbers: 836K chess games analysed, 10K bootstrap replicates, 21K-word German NLP corpus, 90% fare-quote coverage")


# ── PIPELINE ───────────────────────────────────────────────────────────────
def pipeline() -> str:
    W, H = 1200, 270
    stages = [
        ("COLLECT", "MediaWiki · REST APIs", "web scraping"),
        ("CLEAN", "pandas · regex rules", "quality checks"),
        ("ENGINEER", "target encoding", "feature design"),
        ("TRAIN", "scikit-learn · GBMs", "spaCy pipelines"),
        ("EVALUATE", "bootstrap CIs · MAE", "BH correction"),
        ("SHIP", "React port · Streamlit", "MkDocs · LaTeX"),
    ]
    n = len(stages)
    bw, bh, gap = 168, 128, 26
    total = n * bw + (n - 1) * gap
    sx = (W - total) / 2
    by = 92
    cyc = 7.2
    parts = []
    line_y = by + bh / 2
    parts.append(
        f'<line x1="{sx}" y1="{line_y}" x2="{sx+total}" y2="{line_y}" stroke="{AUB}" stroke-width="2" stroke-dasharray="6 6">'
        f'<animate attributeName="stroke-dashoffset" from="24" to="0" dur="1s" repeatCount="indefinite"/></line>'
    )
    for k in range(3):
        parts.append(
            f'<circle cy="{line_y}" r="5" fill="{PEACH}"><animate attributeName="cx" from="{sx}" to="{sx+total}" dur="{cyc}s" begin="{k*cyc/3:.2f}s" repeatCount="indefinite"/></circle>'
        )
    for i, (name, t1, t2) in enumerate(stages):
        x = sx + i * (bw + gap)
        on0 = i / n
        on1 = (i + 1) / n
        kt = f"0;{max(on0-0.001,0):.3f};{on0:.3f};{on1:.3f};{min(on1+0.001,1):.3f};1"
        parts.append(f"""<g>
<rect x="{x:.1f}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="{INK}" fill-opacity=".85" stroke="{AUB}" stroke-width="1.5"/>
<rect x="{x:.1f}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="{ORG}" fill-opacity="0" stroke="{ORG}" stroke-width="2" stroke-opacity="0">
  <animate attributeName="stroke-opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{cyc}s" repeatCount="indefinite"/>
  <animate attributeName="fill-opacity" values="0;0;.12;.12;0;0" keyTimes="{kt}" dur="{cyc}s" repeatCount="indefinite"/>
</rect>
<text x="{x+18:.1f}" y="{by+32}" font-family="{MONO}" font-size="13" font-weight="700" fill="{ORG}">{i+1:02d}</text>
<text x="{x+18:.1f}" y="{by+62}" font-family="{SANS}" font-size="19" font-weight="800" letter-spacing="1.5" fill="{CREAM}">{name}</text>
<text x="{x+18:.1f}" y="{by+90}" font-family="{MONO}" font-size="11" fill="{GREY}">{escape(t1)}</text>
<text x="{x+18:.1f}" y="{by+108}" font-family="{MONO}" font-size="11" fill="{GREY}">{escape(t2)}</text>
</g>""")
        if i < n - 1:
            ax = x + bw + gap / 2
            parts.append(f'<path d="M{ax-5:.1f},{line_y-6} L{ax+3:.1f},{line_y} L{ax-5:.1f},{line_y+6}" fill="none" stroke="{ORG}" stroke-width="2"/>')
    body = f"""<defs>{common_defs()}</defs>
{frame(W, H)}
<text x="{sx}" y="46" font-family="{MONO}" font-size="12.5" letter-spacing="2" fill="{PEACH}">END-TO-END ML WORKFLOW</text>
<text x="{sx}" y="66" font-family="{SANS}" font-size="15" fill="{CREAM}" fill-opacity=".85">From raw data to something people can use — every stage tested, every number with an interval.</text>
{''.join(parts)}
{frame_end(W, H)}"""
    return svg(W, H, body, "ML workflow: collect, clean, engineer, train, evaluate, ship")


# ── PROJECT CARDS ──────────────────────────────────────────────────────────
PROJECTS = [
    ("white-lies", "01", "STATISTICAL ML", "White Lies",
     ["Is the first-move advantage in chess real? Tested on", "836,070 rated Lichess games with bootstrap CIs,", "exact binomial tests and spline regression."],
     ["Python", "Statistics", "Jupyter", "MkDocs"]),
    ("fairfare", "02", "PREDICTIVE MODELLING", "Fairfare",
     ["Prices NYC yellow-taxi trips at booking time with", "gradient boosting + target-encoded zones, then", "ports the model to the browser with parity tests."],
     ["scikit-learn", "GBM", "React", "TypeScript"]),
    ("sprachenlp", "03", "NATURAL LANGUAGE", "SpracheNLP",
     ["A frozen 100-article German Wikipedia corpus", "(~21K words), cleaned and analysed with spaCy:", "lemmas, dependency parses and named entities."],
     ["spaCy", "NLP", "MediaWiki API", "pytest"]),
    ("routeforge", "04", "ALGORITHMS", "RouteForge",
     ["Interactive weighted-graph editor that animates", "BFS, DFS, Dijkstra, Prim and Kruskal step by", "step for teaching and debugging."],
     ["Python", "pygame", "Graphs", "pytest"]),
    ("zigziggy", "05", "PERFORMANCE", "ZigZiggy",
     ["Benchmarking harness and analysis of classic", "sorting and searching algorithms — measured,", "plotted and compared against theory."],
     ["Java", "Benchmarks", "Big-O", "Analysis"]),
    ("playops", "06", "SOFTWARE DESIGN", "PlayOps",
     ["Video-game and hardware retail system built", "around clean object-oriented design: inventory,", "orders and customers as composable domains."],
     ["Java", "OOP", "Design", "Systems"]),
]


def card(slug, num, cat, title, desc, tags, idx) -> str:
    W, H = 600, 240
    chips = []
    cx = 28
    for t in tags:
        w = len(t) * 7.4 + 24
        chips.append(
            f'<rect x="{cx:.1f}" y="186" width="{w:.1f}" height="28" rx="14" fill="{AUB}" fill-opacity=".45" stroke="{AUB}"/>'
            f'<text x="{cx + w/2:.1f}" y="204.5" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{CREAM}">{escape(t)}</text>'
        )
        cx += w + 8
    dlines = "".join(
        f'<text x="28" y="{112 + i*22}" font-family="{SANS}" font-size="15" fill="{CREAM}" fill-opacity=".78">{escape(l)}</text>'
        for i, l in enumerate(desc)
    )
    body = f"""<defs>{common_defs()}</defs>
{frame(W, H)}
<circle cx="560" cy="20" r="170" fill="url(#glow)" opacity=".7"/>
<text x="28" y="40" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{ORG}">◆ {num}  ·  {escape(cat)}</text>
<text x="28" y="80" font-family="{SANS}" font-size="30" font-weight="800" letter-spacing="-.5" fill="{CREAM}">{escape(title)}</text>
<g transform="translate(548 30)">
  <circle r="18" fill="{INK}" stroke="{AUB}"/>
  <path d="M-5,5 L5,-5 M-3,-5 H5 V3" fill="none" stroke="{PEACH}" stroke-width="2" stroke-linecap="round"/>
</g>
{dlines}
{''.join(chips)}
{frame_end(W, H)}
{border_runner(W, H, dur=9, begin=idx*1.5)}"""
    return svg(W, H, body, f"{title} — {' '.join(desc)}")


# ── FOOTER ─────────────────────────────────────────────────────────────────
def footer() -> str:
    W, H = 1200, 170

    def wave(amp, off, y):
        pts = []
        for x in range(0, W + 41, 40):
            pts.append(f"{x},{y + amp*math.sin((x/W)*4*math.pi + off):.1f}")
        return "M0,170 L" + " L".join(pts) + f" L{W},170 Z"

    waves = []
    for i, (col, op, amp, y) in enumerate([(AUB, 0.55, 12, 112), (AUB2, 0.45, 9, 124), (ORG, 0.35, 7, 138)]):
        a, b = wave(amp, 0, y), wave(amp, math.pi, y)
        waves.append(
            f'<path d="{a}" fill="{col}" fill-opacity="{op}"><animate attributeName="d" values="{a};{b};{a}" dur="{6+i*1.5}s" repeatCount="indefinite"/></path>'
        )
    body = f"""<defs>{common_defs()}</defs>
{frame(W, H)}
{''.join(waves)}
<text x="600" y="72" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="800" fill="url(#hot)">Let's build something intelligent.</text>
{frame_end(W, H)}"""
    return svg(W, H, body, "Let's build something intelligent.")


def main() -> None:
    files = {
        "hero.svg": hero(),
        "terminal.svg": terminal(),
        "radar.svg": radar(),
        "impact.svg": impact(),
        "pipeline.svg": pipeline(),
        "footer.svg": footer(),
    }
    sections = [
        ("01", "ABOUT", "whoami --verbose"),
        ("02", "BY THE NUMBERS", "evidence over adjectives"),
        ("03", "FEATURED WORK", "selected repositories · click a card to open it"),
        ("04", "HOW I WORK", "the pipeline behind the projects"),
        ("05", "TOOLKIT", "languages · ML & data · tooling"),
        ("06", "GITHUB TELEMETRY", "live stats, refreshed automatically"),
        ("07", "CONNECT", "open a channel"),
    ]
    for num, title, sub in sections:
        files[f"headers/{num}-{title.lower().replace(' ', '-')}.svg"] = header(num, title, sub)
    for i, p in enumerate(PROJECTS):
        files[f"projects/{p[0]}.svg"] = card(*p, idx=i)
    for name, content in files.items():
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(OUT.parent)}")


if __name__ == "__main__":
    main()
