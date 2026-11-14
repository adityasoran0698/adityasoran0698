"""Turns text into SVG path outlines so README artwork renders in the exact
brand fonts on GitHub (which blocks web fonts inside SVG images)."""
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

import os
_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILES = {
    "display": os.path.join(_HERE, "fonts", "Fraunces.woff2"),
    "body": os.path.join(_HERE, "fonts", "Manrope.woff2"),
}
# fixed axis settings per family: soft, rounded serifs; no quirky alternates
FIXED_AXES = {"display": {"SOFT": 100, "WONK": 0}}


@lru_cache(maxsize=None)
def font(kind, wght=None, opsz=None):
    f = TTFont(FONT_FILES[kind])
    if "fvar" in f:
        loc = {}
        fixed = FIXED_AXES.get(kind, {})
        for ax in f["fvar"].axes:
            if ax.axisTag == "wght" and wght:
                loc["wght"] = wght
            elif ax.axisTag == "opsz":
                loc["opsz"] = opsz or ax.maxValue
            elif ax.axisTag in fixed:
                loc[ax.axisTag] = fixed[ax.axisTag]
        f = instancer.instantiateVariableFont(f, loc)
    return f


def _kern_table(f):
    """Pair kerning from GPOS PairPos format 1 (glyph pairs). Good enough for display text."""
    pairs = {}
    if "GPOS" not in f:
        return pairs
    for lookup in f["GPOS"].table.LookupList.Lookup:
        subs = lookup.SubTable
        if lookup.LookupType == 9:
            subs = [s.ExtSubTable for s in subs]
        for st in subs:
            if getattr(st, "LookupType", 2) != 2 and lookup.LookupType != 9:
                continue
            if getattr(st, "Format", None) == 1 and hasattr(st, "PairSet"):
                cov = st.Coverage.glyphs
                for g1, ps in zip(cov, st.PairSet):
                    for rec in ps.PairValueRecord:
                        v = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                        if v:
                            pairs[(g1, rec.SecondGlyph)] = v
            elif getattr(st, "Format", None) == 2 and hasattr(st, "Class1Record"):
                cov = set(st.Coverage.glyphs)
                c1 = st.ClassDef1.classDefs
                c2 = st.ClassDef2.classDefs
                st._cls = (cov, c1, c2)
                pairs.setdefault("__class__", []).append(st)
    return pairs


@lru_cache(maxsize=None)
def kerns(kind, wght, opsz):
    return _kern_table(font(kind, wght, opsz))


def kern_value(k, g1, g2):
    v = k.get((g1, g2))
    if v is not None:
        return v
    for st in k.get("__class__", []):
        cov, c1, c2 = st._cls
        if g1 not in cov:
            continue
        a = c1.get(g1, 0)
        b = c2.get(g2, 0)
        try:
            rec = st.Class1Record[a].Class2Record[b]
        except IndexError:
            continue
        val = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
        if val:
            return val
    return 0


def text_path(text, size, x=0, y=0, kind="display", wght=800, opsz=None, track=0.0, anchor="start"):
    """Return (path_d, width). track is extra spacing in em (negative = tighter)."""
    f = font(kind, wght, opsz)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    upm = f["head"].unitsPerEm
    s = size / upm
    k = kerns(kind, wght, opsz)
    names = [cmap.get(ord(c), cmap.get(ord("?"))) for c in text]
    # measure
    adv = []
    for i, g in enumerate(names):
        a = hmtx[g][0]
        if i + 1 < len(names):
            a += kern_value(k, g, names[i + 1])
        adv.append(a * s + (track * size if i + 1 < len(names) else 0))
    width = sum(adv)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pen = SVGPathPen(gs)
    cx = x
    for g, a in zip(names, adv):
        tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
        gs[g].draw(tp)
        cx += a
    d = pen.getCommands()
    # trim float noise
    import re
    d = re.sub(r"(\d+\.\d)\d*", r"\1", d)
    return d, width


def measure(text, size, kind="display", wght=800, opsz=None, track=0.0):
    return text_path(text, size, 0, 0, kind, wght, opsz, track)[1]


def T(text, size, x, y, fill, kind="body", wght=500, opsz=None, track=0.0, anchor="start", extra=""):
    d, w = text_path(text, size, x, y, kind, wght, opsz, track, anchor)
    return f'<path d="{d}" fill="{fill}" {extra}/>', w


def wrap(text, size, max_w, kind="body", wght=400, track=0.0):
    """Greedy word wrap using real glyph widths."""
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if measure(trial, size, kind, wght, None, track) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ─── Design tokens: "Moonlit Sage" (dark) / "Morning Sage" (light) ──────────
# Low-saturation, cool, soothing. Separate identity from the portfolio.
THEMES = {
    "dark": dict(
        bg="#0B1416", surface="#112126", surface2="#17292E",
        line="rgba(140,199,169,.20)", line2="rgba(231,239,236,.07)",
        sage="#8CC7A9", mist="#9DB7E0", lilac="#B7A7E6", sand="#E3C79A",
        text="#E7EFEC", muted="#93A8A5", faint="#5E7471",
        chip_bg="rgba(140,199,169,.08)", chip_line="rgba(140,199,169,.30)", chip_text="#A9D6BE",
        accent_text="#9DB7E0", aurora=".34",
    ),
    "light": dict(
        bg="#F5F8F6", surface="#FFFFFF", surface2="#EEF4F1",
        line="rgba(63,143,110,.22)", line2="rgba(28,43,42,.08)",
        sage="#3F8F6E", mist="#4F6FA8", lilac="#7562B8", sand="#A8762B",
        text="#1C2B2A", muted="#566B67", faint="#8A9B97",
        chip_bg="rgba(63,143,110,.07)", chip_line="rgba(63,143,110,.28)", chip_text="#2F7A5B",
        accent_text="#4F6FA8", aurora=".20",
    ),
}

BASE_CSS = """
@keyframes rise{from{transform:translateY(8px)}to{transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes ping{0%{transform:scale(.7);opacity:.7}100%{transform:scale(2.3);opacity:0}}
@keyframes bob{50%{transform:translateY(-4px)}}
.rise{animation:rise 1.4s cubic-bezier(.22,1,.36,1) both}
.fade{animation:fade 2s ease both}
.ping{transform-box:fill-box;transform-origin:center;animation:ping 3.2s ease-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def chip(label, x, y, th, h=34, size=14.5, pad=16, kind="body", wght=600, fill=None, stroke=None, color=None):
    w = measure(label, size, kind, wght) + pad * 2
    t, _ = T(label, size, x + pad, y + h / 2 + size * 0.36, color or th["chip_text"], kind, wght)
    rect = (
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" '
        f'fill="{fill or th["chip_bg"]}" stroke="{stroke or th["chip_line"]}"/>'
    )
    return rect + t, w
