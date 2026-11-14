"""GitHub profile artwork — "Moonlit Sage" (dark) / "Morning Sage" (light).

Calm by design: cool, low-saturation colours; slow, gentle motion.
Edit the content blocks (HEADER, ROLES, PROJECTS, ACHIEVEMENTS) and run:
    python tools/build.py
"""
import math
import os
import random
from engine import T, measure, wrap, text_path, THEMES, BASE_CSS

# ─── CONTENT ───────────────────────────────────────────────────────────────
HEADER = dict(
    hello="Hey there, I\u2019m",
    name="Aditya Soran",
    monogram="AS",
    role="AI/ML Engineer",
    company="at Recklabs",
    chips=["Agentic AI", "RAG pipelines", "LLM systems", "Full-stack products"],
)

ROLES = [
    dict(
        when="2026 \u2014 Present", current=True, company="Recklabs", role="AI/ML Engineer",
        line="Building aisockt, an enterprise AI platform that connects live business data from ads, marketing, finance, sales and SEO tools to LLMs that answer questions and produce reports.",
        tags=["Data connectors", "Model-agnostic UI layer", "Branded reports", "AWS + Cloudflare"],
    ),
    dict(
        when="Before Recklabs", current=False, company="Diglip7 Tech", role="AI Engineer",
        line="Built KAKA, a multi-tenant WhatsApp AI agent that books appointments for ZEVA, a clinic management platform.",
        tags=["LangGraph", "FastAPI", "PostgreSQL", "Redis + BullMQ", "WhatsApp API"],
    ),
]

# accent per project: (dark, light)
PROJECTS = [
    dict(id="curalink", title="CuraLink", kind="AI medical research assistant", accent=("#9DB7E0", "#4F6FA8"),
         status="Live", award="Certificate of Distinction", motif="rings",
         line="Agentic AI that queries PubMed, OpenAlex and ClinicalTrials.gov in parallel, ranks results with FAISS semantic search and answers with sources and multi-turn memory.",
         tags=["LangChain", "FAISS", "FastAPI", "React"]),
    dict(id="vibeai", title="VibeAI", kind="Personal AI agent", accent=("#B7A7E6", "#7562B8"),
         status="Live", award=None, motif="graph",
         line="A LangGraph agent with RAG, MCP server integration through FastMCP, persistent SQLite memory and a custom streaming chat UI.",
         tags=["LangGraph", "FastMCP", "RAG", "FastAPI"]),
    dict(id="ayursutra", title="AyurSutra", kind="Ayurveda therapy platform", accent=("#8CC7A9", "#2F8A60"),
         status="Live", award="Smart India Hackathon 2024", motif="leaf",
         line="Built for the Ministry of AYUSH: therapy booking with role-based access, automated scheduling and an NLP layer that classifies patient feedback.",
         tags=["MERN", "FastAPI", "NLP", "JWT"]),
    dict(id="youtube", title="YouTube Chatbot", kind="Chat with any video", accent=("#E3A8A1", "#B5574D"),
         status="Source", award=None, motif="play",
         line="Paste a YouTube link and ask questions. Transcripts go into a ChromaDB vector store and GPT-4o answers in context, including Hindi videos.",
         tags=["RAG", "LangChain", "ChromaDB", "GPT-4o"]),
]

ACHIEVEMENTS = [
    ("trophy", "sage", "Smart India Hackathon", "2024 \u00b7 AyurSutra, Ministry of AYUSH"),
    ("medal", "mist", "Certificate of Distinction", "CuraLink Hackathon v2.0"),
    ("paper", "lilac", "Scopus-indexed paper", "I3CSET-2025 \u00b7 Taylor & Francis"),
    ("chip", "sand", "AI/ML training", "80 hours \u00b7 GI Ventures, NVIDIA partner"),
]

FOOTER_LINE = "Thanks for stopping by \u2014 let\u2019s build something thoughtful."


# ─── HELPERS ───────────────────────────────────────────────────────────────
def svg(W, H, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{title}"><title>{title}</title><style>{BASE_CSS}</style>{body}</svg>'
    )


def card(th, W, H, cid="c", r=24):
    return (
        f'<clipPath id="{cid}"><rect width="{W}" height="{H}" rx="{r}"/></clipPath>',
        f'<rect width="{W}" height="{H}" rx="{r}" fill="{th["bg"]}"/>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="{r-.5}" fill="none" stroke="{th["line"]}"/>',
    )


SOFT = ('<filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
HAZE = '<filter id="haze" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="55"/></filter>'
EASE = 'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"'


def aurora(th, blobs):
    """Slowly drifting, heavily blurred colour fields."""
    out = []
    for (cx, cy, r, col, dx, dy, dur) in blobs:
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{th[col]}" opacity="{th["aurora"]}" filter="url(#haze)">'
            f'<animate attributeName="cx" values="{cx};{cx+dx};{cx}" dur="{dur}s" repeatCount="indefinite" {EASE}/>'
            f'<animate attributeName="cy" values="{cy};{cy+dy};{cy}" dur="{dur*1.3:.0f}s" repeatCount="indefinite" {EASE}/>'
            f"</circle>"
        )
    return "".join(out)


def stars(th, rng, x0, x1, y0, y1, n):
    out = []
    for i in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.choice([0.7, 0.9, 1.1, 1.4])
        op = rng.uniform(0.18, 0.55)
        tw = (
            f'<animate attributeName="opacity" values="{op:.2f};{op*0.25:.2f};{op:.2f}" dur="{rng.uniform(4, 8):.1f}s" '
            f'begin="{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/>' if i % 3 == 0 else ""
        )
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{th["text"]}" opacity="{op:.2f}">{tw}</circle>')
    return "".join(out)


def pill(label, x, y, th, h=32, size=14, pad=15, fill=None, stroke=None, color=None, wght=600):
    w = measure(label, size, "body", wght) + pad * 2
    t, _ = T(label, size, x + pad, y + h / 2 + size * 0.35, color or th["chip_text"], "body", wght)
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{fill or th["chip_bg"]}" '
            f'stroke="{stroke or th["chip_line"]}"/>' + t), w


def soft_gradient(gid, th, x1, x2, stops, dur=12):
    """Text gradient with a slow, gentle drift."""
    span = x2 - x1
    s = "".join(f'<stop offset="{o}" stop-color="{th[c] if c in th else c}"/>' for o, c in stops)
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="0" x2="{x2}" y2="0" spreadMethod="reflect">{s}'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{span*0.5:.0f} 0;0 0" dur="{dur}s" '
        f'repeatCount="indefinite" {EASE}/></linearGradient>'
    )


def star(cx, cy, r1=6, r2=2.6):
    return "M" + "L".join(
        f"{cx + (r1 if k % 2 == 0 else r2) * math.sin(k * math.pi / 5):.1f} {cy - (r1 if k % 2 == 0 else r2) * math.cos(k * math.pi / 5):.1f}"
        for k in range(10)) + "Z"


# ─── HEADER ────────────────────────────────────────────────────────────────
def header(mode):
    th = THEMES[mode]
    W, H = 1200, 400
    rng = random.Random(11)
    clip, bg, border = card(th, W, H)
    cx, cy = 935, 200
    name_d, name_w = text_path(HEADER["name"], 94, 66, 214, "display", 560, None, -0.015)
    mono_d, _ = text_path(HEADER["monogram"], 58, cx, cy + 20, "display", 520, None, -0.01, "middle")
    defs = (
        "<defs>" + clip + SOFT + HAZE
        + soft_gradient("nm", th, 66, 66 + name_w, [(0, "text"), (".55", "text"), (".8", "sage"), (1, "mist")])
        + soft_gradient("mg", th, cx - 40, cx + 40, [(0, "sage"), (1, "mist")], dur=10)
        + f'<radialGradient id="disc" cx=".5" cy=".4" r=".65"><stop offset="0" stop-color="{th["surface2"]}"/>'
        f'<stop offset="1" stop-color="{th["surface"]}"/></radialGradient>'
        f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{th["sage"]}" stop-opacity=".7"/>'
        f'<stop offset=".5" stop-color="{th["mist"]}" stop-opacity=".15"/><stop offset="1" stop-color="{th["lilac"]}" stop-opacity=".55"/></linearGradient>'
        "</defs>"
    )
    g = [bg, '<g clip-path="url(#c)">']
    g.append(aurora(th, [(980, 90, 170, "sage", -60, 40, 22), (1080, 300, 150, "mist", -80, -40, 26),
                         (760, 330, 130, "lilac", 70, -30, 30), (300, -40, 140, "mist", 90, 30, 34)]))
    g.append(f'<g class="fade">{stars(th, rng, 20, 1180, 14, 386, 70)}</g>')
    # constellation
    pts = [(rng.uniform(640, 1180), rng.uniform(30, 370)) for _ in range(16)]
    segs = []
    for i, a in enumerate(pts):
        for d, j in sorted((math.dist(a, b), j) for j, b in enumerate(pts) if j > i)[:2]:
            if d < 150:
                segs.append((a, pts[j]))
    g.append('<path d="' + "".join(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" for a, b in segs)
             + f'" stroke="{th["mist"]}" stroke-opacity=".22" fill="none"/>')
    for x, y in pts:
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{th["mist"]}" opacity=".6"/>')
    for k, (a, b) in enumerate(rng.sample(segs, min(4, len(segs)))):
        g.append(f'<circle r="2.6" fill="{th["sage"]}" filter="url(#soft)"><animateMotion path="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" '
                 f'dur="{4.5 + k:.1f}s" begin="{k*1.3:.1f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".45 0 .55 1"/></circle>')
    # emblem
    g.append('<g class="fade" style="animation-delay:.3s">')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="132" fill="none" stroke="url(#ring)" stroke-width="1.2"/>')
    g.append(f'<g><circle cx="{cx}" cy="{cy-132}" r="4.5" fill="{th["sand"]}" filter="url(#soft)"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></g>')
    g.append(f'<g><circle cx="{cx}" cy="{cy}" r="100" fill="none" stroke="{th["mist"]}" stroke-opacity=".35" stroke-dasharray="1.5 7"/>'
             f'<circle cx="{cx+100}" cy="{cy}" r="3.6" fill="{th["lilac"]}" filter="url(#soft)"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="55s" repeatCount="indefinite"/></g>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="68" fill="url(#disc)" stroke="{th["sage"]}" stroke-opacity=".45"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="68" fill="none" stroke="{th["sage"]}" stroke-opacity=".5" class="ping" style="animation-duration:5s"/>')
    g.append(f'<path d="{mono_d}" fill="url(#mg)"/>')
    g.append("</g>")
    # copy
    g.append(f'<g class="rise">{T(HEADER["hello"], 20, 70, 112, th["muted"], "body", 500)[0]}</g>')
    g.append(f'<g class="rise" style="animation-delay:.1s"><path d="{name_d}" fill="url(#nm)"/></g>')
    r1, w1 = T(HEADER["role"], 25, 96, 268, th["text"], "body", 700, track=-0.01)
    r2, _ = T(HEADER["company"], 25, 96 + w1 + 9, 268, th["accent_text"], "body", 700, track=-0.01)
    dot = (f'<circle cx="78" cy="259" r="5.5" fill="{th["sage"]}"/>'
           f'<circle cx="78" cy="259" r="5.5" fill="none" stroke="{th["sage"]}" stroke-width="1.4" class="ping"/>')
    g.append(f'<g class="rise" style="animation-delay:.2s">{dot}{r1}{r2}</g>')
    x, chips = 70, []
    for label in HEADER["chips"]:
        c, w = pill(label, x, 298, th)
        chips.append(c)
        x += w + 10
    g.append(f'<g class="rise" style="animation-delay:.3s">{"".join(chips)}</g>')
    g.append("</g>")
    g.append(border)
    return svg(W, H, defs + "".join(g), "Aditya Soran, AI/ML Engineer at Recklabs")


# ─── DIVIDER ───────────────────────────────────────────────────────────────
def divider(mode):
    th = THEMES[mode]
    W, H = 1200, 30
    body = (
        "<defs>" + SOFT
        + f'<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{th["sage"]}" stop-opacity="0"/>'
        f'<stop offset=".3" stop-color="{th["sage"]}" stop-opacity=".5"/><stop offset=".7" stop-color="{th["mist"]}" stop-opacity=".5"/>'
        f'<stop offset="1" stop-color="{th["lilac"]}" stop-opacity="0"/></linearGradient></defs>'
        f'<rect y="14.5" width="{W}" height="1" fill="url(#l)"/>'
        f'<path d="M600 9l5 6-5 6-5-6z" fill="{th["bg"]}" stroke="{th["sage"]}"/>'
        f'<circle r="2.6" cy="15" fill="{th["mist"]}" filter="url(#soft)"><animate attributeName="cx" values="160;1040;160" dur="14s" repeatCount="indefinite" {EASE}/></circle>'
    )
    return svg(W, H, body, "divider")


# ─── EXPERIENCE ────────────────────────────────────────────────────────────
def experience(mode):
    th = THEMES[mode]
    W, LH, GAP = 1200, 26, 64
    lines = [wrap(r["line"], 16, 800, "body", 400) for r in ROLES]
    heights = [104 + len(l) * LH + 8 + 30 for l in lines]
    tops = [50]
    for h in heights[:-1]:
        tops.append(tops[-1] + h + GAP)
    H = tops[-1] + heights[-1] + 46
    clip, bg, border = card(th, W, H)
    g = [bg, '<g clip-path="url(#c)">',
         aurora(th, [(1150, 40, 120, "sage", -40, 30, 26), (60, H, 110, "mist", 40, -20, 30)]), "</g>"]
    rx = 58
    g.append(f'<line x1="{rx}" y1="{tops[0]+20}" x2="{rx}" y2="{tops[-1]+20}" stroke="{th["line"]}" stroke-width="1.5"/>')
    for top in tops[1:]:
        g.append(f'<line x1="94" y1="{top-GAP/2}" x2="{W-48}" y2="{top-GAP/2}" stroke="{th["line2"]}"/>')
    for r, top, ls in zip(ROLES, tops, lines):
        p = []
        if r["current"]:
            p.append(f'<circle cx="{rx}" cy="{top+20}" r="8" fill="{th["sage"]}"/>'
                     f'<circle cx="{rx}" cy="{top+20}" r="8" fill="none" stroke="{th["sage"]}" stroke-width="1.4" class="ping"/>')
        else:
            p.append(f'<circle cx="{rx}" cy="{top+20}" r="7" fill="{th["bg"]}" stroke="{th["mist"]}" stroke-width="2"/>')
        p.append(T(r["when"], 15.5, 94, top + 26, th["muted"], "body", 600)[0])
        if r["current"]:
            p.append(pill("Current", 94, top + 42, th, h=26, size=12.5, pad=12, color=th["sage"])[0])
        p.append(T(r["company"], 36, 330, top + 32, th["text"], "display", 560, None, -0.01)[0])
        p.append(T(r["role"], 17.5, 332, top + 64, th["accent_text"], "body", 700)[0])
        for k, ln in enumerate(ls):
            p.append(T(ln, 16, 332, top + 100 + k * LH, th["muted"], "body", 400)[0])
        x, ty = 332, top + 104 + len(ls) * LH + 4
        for tag in r["tags"]:
            c, w = pill(tag, x, ty, th, h=30, size=13, pad=13)
            p.append(c)
            x += w + 8
        g.append(f'<g class="rise">{"".join(p)}</g>')
    g.append(border)
    return svg(W, H, "<defs>" + clip + HAZE + "</defs>" + "".join(g),
               "Experience: AI/ML Engineer at Recklabs (current); AI Engineer at Diglip7 Tech")


# ─── PROJECT CARDS ─────────────────────────────────────────────────────────
def motif(kind, cx, cy, c):
    if kind == "rings":
        s = "".join(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-opacity="{op}" stroke-dasharray="{da}">'
            f'<animateTransform attributeName="transform" type="rotate" from="{0 if i%2 else 360} {cx} {cy}" '
            f'to="{360 if i%2 else 0} {cx} {cy}" dur="{40+i*15}s" repeatCount="indefinite"/></circle>'
            for i, (r, op, da) in enumerate([(28, ".45", "2 6"), (46, ".28", "36 20"), (64, ".16", "1.5 7")])
        )
        return s + f'<circle cx="{cx}" cy="{cy}" r="5" fill="{c}"><animate attributeName="opacity" values="1;.4;1" dur="4s" repeatCount="indefinite"/></circle>'
    if kind == "graph":
        pts = [(cx - 44, cy + 10), (cx + 2, cy - 36), (cx + 46, cy + 6), (cx + 4, cy + 44)]
        s = "".join(f'<line x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}" stroke="{c}" stroke-opacity=".35"/>'
                    for a, b in [(0, 1), (1, 2), (0, 3), (3, 2), (1, 3)])
        return s + "".join(
            f'<circle cx="{x}" cy="{y}" r="10" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".6">'
            f'<animate attributeName="fill-opacity" values=".08;.08;.45;.08;.08" keyTimes="0;.2;.35;.5;1" dur="7s" begin="{i*1.6}s" repeatCount="indefinite"/></circle>'
            for i, (x, y) in enumerate(pts))
    if kind == "leaf":
        return "".join(
            f'<path d="M{cx} {cy+40} C{cx-22} {cy+14} {cx-16} {cy-22} {cx} {cy-38} C{cx+16} {cy-22} {cx+22} {cy+14} {cx} {cy+40}Z" '
            f'fill="{c}" fill-opacity="{.10+i*.05:.2f}" stroke="{c}" stroke-opacity=".5" transform="rotate({rot} {cx} {cy+40})">'
            f'<animateTransform attributeName="transform" type="rotate" values="{rot} {cx} {cy+40};{rot+4} {cx} {cy+40};{rot} {cx} {cy+40}" '
            f'dur="{7+i*1.5}s" repeatCount="indefinite" {EASE}/></path>'
            for i, rot in enumerate([-38, 0, 38]))
    if kind == "play":
        s = "".join(
            f'<rect x="{cx-44+i*12}" y="{cy-36+i*12}" width="76" height="52" rx="12" fill="{c}" fill-opacity="{.06+i*.05:.2f}" stroke="{c}" stroke-opacity="{.25+i*.18:.2f}">'
            f'<animate attributeName="y" values="{cy-36+i*12};{cy-40+i*12};{cy-36+i*12}" dur="{6+i:.0f}s" repeatCount="indefinite" {EASE}/></rect>'
            for i in range(3))
        return s + f'<path d="M{cx+2} {cy+4} l0 24 l20 -12z" fill="{c}" fill-opacity=".85"/>'
    return ""


def project_card(p, mode):
    th = THEMES[mode]
    acc = p["accent"][0 if mode == "dark" else 1]
    W, H = 600, 320
    clip, bg, _ = card(th, W, H, "pc")
    border = f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="23.5" fill="none" stroke="{acc}" stroke-opacity=".3"/>'
    defs = (
        "<defs>" + clip + HAZE
        + f'<linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">'
        f'<stop offset=".44" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity="{.04 if mode=="dark" else .3}"/>'
        f'<stop offset=".56" stop-color="#fff" stop-opacity="0"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="-900 0;-900 0;900 0" keyTimes="0;.7;1" dur="12s" repeatCount="indefinite"/>'
        "</linearGradient></defs>"
    )
    g = [bg, '<g clip-path="url(#pc)">',
         f'<circle cx="520" cy="60" r="150" fill="{acc}" opacity="{.20 if mode=="dark" else .14}" filter="url(#haze)">'
         f'<animate attributeName="cy" values="60;90;60" dur="18s" repeatCount="indefinite" {EASE}/></circle>',
         f'<g class="fade">{motif(p["motif"], 520, 82, acc)}</g>']
    top = 52
    if p["award"]:
        tw = measure(p["award"], 12.5, "body", 700)
        g.append(
            f'<g class="rise"><rect x="36" y="30" width="{tw+46:.1f}" height="28" rx="14" fill="{acc}" fill-opacity=".14" stroke="{acc}" stroke-opacity=".55"/>'
            f'<path d="{star(52, 44)}" fill="{acc}"/>' + T(p["award"], 12.5, 64, 48.5, acc, "body", 700)[0] + "</g>")
        top = 84
    g.append(f'<g class="rise">{T(p["kind"], 14.5, 38, top + 8, th["muted"], "body", 600)[0]}'
             f'{T(p["title"], 42, 35, top + 58, th["text"], "display", 560, None, -0.015)[0]}</g>')
    lines = wrap(p["line"], 15, 470, "body", 400)
    g.append('<g class="rise">' + "".join(T(ln, 15, 38, top + 92 + i * 24, th["muted"], "body", 400)[0] for i, ln in enumerate(lines)) + "</g>")
    x, chips = 36, []
    for t in p["tags"]:
        c, w = pill(t, x, H - 56, th, h=30, size=12.5, pad=12, fill="none", stroke=acc, color=acc)
        chips.append(c)
        x += w + 8
    live = p["status"] == "Live"
    sc = th["sage"] if live else th["muted"]
    sw = measure(p["status"], 12.5, "body", 700) + 34
    sx = W - 36 - sw
    st = (f'<rect x="{sx:.1f}" y="{H-55}" width="{sw:.1f}" height="28" rx="14" fill="none" stroke="{sc}" stroke-opacity=".55"/>'
          + (f'<circle cx="{sx+14:.1f}" cy="{H-41}" r="3.8" fill="{sc}"/><circle cx="{sx+14:.1f}" cy="{H-41}" r="3.8" fill="none" stroke="{sc}" class="ping"/>'
             if live else f'<circle cx="{sx+14:.1f}" cy="{H-41}" r="3.8" fill="none" stroke="{sc}"/>')
          + T(p["status"], 12.5, sx + 24, H - 36.5, sc, "body", 700)[0])
    g.append(f'<g class="rise">{"".join(chips)}{st}</g>')
    g.append(f'<rect width="{W}" height="{H}" fill="url(#sh)"/></g>')
    g.append(border)
    return svg(W, H, defs + "".join(g), f'{p["title"]}: {p["kind"]}')


# ─── ACHIEVEMENTS ──────────────────────────────────────────────────────────
def icon(kind, x, y, c):
    s = f'stroke="{c}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "trophy":
        return (f'<path d="M{x-11} {y-13}h22v9a11 11 0 0 1-22 0z" {s}/><path d="M{x-11} {y-9}h-5a5.5 5.5 0 0 0 5.5 8M{x+11} {y-9}h5a5.5 5.5 0 0 1-5.5 8" {s}/>'
                f'<path d="M{x} {y+7}v6M{x-7} {y+15}h14" {s}/>')
    if kind == "medal":
        return (f'<path d="M{x-9} {y-17}l5.5 11M{x+9} {y-17}l-5.5 11" {s}/><circle cx="{x}" cy="{y+4}" r="10" {s}/>'
                f'<path d="{star(x, y+4, 4.6, 2)}" fill="{c}"/>')
    if kind == "paper":
        return f'<path d="M{x-10} {y-16}h14l7 7v24h-21z" {s}/><path d="M{x+4} {y-16}v7h7M{x-5} {y-2}h11M{x-5} {y+4}h11M{x-5} {y+10}h7" {s}/>'
    if kind == "chip":
        return (f'<rect x="{x-11}" y="{y-11}" width="22" height="22" rx="4" {s}/><rect x="{x-4.5}" y="{y-4.5}" width="9" height="9" rx="1.5" fill="{c}"/>'
                f'<path d="M{x-5} {y-11}v-5M{x+5} {y-11}v-5M{x-5} {y+11}v5M{x+5} {y+11}v5M{x-11} {y-5}h-5M{x-11} {y+5}h-5M{x+11} {y-5}h5M{x+11} {y+5}h5" {s}/>')
    return ""


def achievements(mode):
    th = THEMES[mode]
    W, H = 1200, 176
    clip, bg, border = card(th, W, H)
    tw = (W - 48 - 3 * 16) / 4
    g = [bg, '<g clip-path="url(#c)">', aurora(th, [(600, 200, 160, "sage", 120, -20, 28)]), "</g>"]
    for i, (ic, col, title, sub) in enumerate(ACHIEVEMENTS):
        x, y = 24 + i * (tw + 16), 24
        c = th[col]
        p = [f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="128" rx="18" fill="{th["surface"]}" fill-opacity=".85" stroke="{th["line2"]}"/>',
             f'<circle cx="{x+44:.1f}" cy="{y+46}" r="24" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".4"/>',
             f'<g style="transform-box:fill-box;transform-origin:center;animation:bob {5+i*0.6:.1f}s ease-in-out infinite;animation-delay:{i*0.5:.1f}s">{icon(ic, x+44, y+46, c)}</g>',
             T(title, 19, x + 22, y + 96, th["text"], "display", 560, None, -0.01)[0]]
        sz = 13
        while measure(sub, sz, "body", 500) > tw - 40 and sz > 11:
            sz -= 0.5
        p.append(T(sub, sz, x + 22, y + 116, th["muted"], "body", 500)[0])
        g.append(f'<g class="rise">{"".join(p)}</g>')
    g.append(border)
    return svg(W, H, "<defs>" + clip + HAZE + "</defs>" + "".join(g),
               "Achievements: Smart India Hackathon 2024, Certificate of Distinction at CuraLink Hackathon v2.0, Scopus-indexed paper at I3CSET-2025, 80-hour AI/ML training with GI Ventures")


# ─── FOOTER ────────────────────────────────────────────────────────────────
def footer(mode):
    th = THEMES[mode]
    W, H = 1200, 250
    clip, bg, border = card(th, W, H)
    d, w = text_path(HEADER["name"], 146, W / 2, 204, "display", 560, None, -0.02, "middle")
    defs = (
        "<defs>" + clip + HAZE + SOFT
        + f'<linearGradient id="fw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{th["text"]}" stop-opacity=".9"/>'
        f'<stop offset=".55" stop-color="{th["sage"]}" stop-opacity=".75"/><stop offset="1" stop-color="{th["mist"]}" stop-opacity=".5"/></linearGradient>'
        f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity=".15"/></linearGradient>'
        f'<mask id="fm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>'
    )
    msg, _ = T(FOOTER_LINE, 18, W / 2, 60, th["muted"], "body", 500, anchor="middle")
    g = [bg, '<g clip-path="url(#c)">',
         aurora(th, [(300, 260, 150, "sage", 80, -20, 26), (900, 260, 150, "mist", -80, -20, 30), (600, 300, 140, "lilac", 0, -30, 34)]),
         f'<g class="rise">{msg}</g>',
         f'<rect x="120" y="89.5" width="960" height="1" fill="{th["sage"]}" opacity=".18"/>',
         f'<circle r="2.6" cy="90" fill="{th["mist"]}" filter="url(#soft)"><animate attributeName="cx" values="140;1060;140" dur="16s" repeatCount="indefinite" {EASE}/></circle>',
         f'<g class="rise" style="animation-delay:.2s" mask="url(#fm)"><path d="{d}" fill="url(#fw)"/></g>',
         "</g>", border]
    return svg(W, H, defs + "".join(g), "Thanks for stopping by")


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    for mode in ("dark", "light"):
        files = {
            f"header-{mode}.svg": header(mode),
            f"divider-{mode}.svg": divider(mode),
            f"experience-{mode}.svg": experience(mode),
            f"achievements-{mode}.svg": achievements(mode),
            f"footer-{mode}.svg": footer(mode),
        }
        for p in PROJECTS:
            files[f'project-{p["id"]}-{mode}.svg'] = project_card(p, mode)
        for name, content in files.items():
            with open(os.path.join(OUT, name), "w") as fh:
                fh.write(content)
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")
