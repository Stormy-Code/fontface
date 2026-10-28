#!/usr/bin/env python3
"""Build redistributable neon COLRv1 and monochrome TrueType display fonts."""
from __future__ import annotations

import copy
import hashlib
import math
from pathlib import Path

from fontTools import subset
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import PaintFormat as F
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
SOURCE = ROOT / "sources" / "Montserrat-Italic.ttf"
SOURCE_SHA256 = "51607f316bc020e59f03cbf51543eecffbea501c0b31d73e5b82927c5cca442c"

# Palette stops run bottom to top, including a sharp mid-height chrome reflection.
THEMES = {
    "pink": ["fff4ff", "ff4bdc", "ef00ab", "f000ce", "ff39ef", "ff9af8"],
    "cyan": ["e3ffff", "00eaff", "1561fa", "2855ff", "00ddf5", "71ffff"],
    "gold": ["ffffe9", "ffe268", "ff8300", "ff9b00", "ffe546", "fff797"],
    "violet": ["fff1ff", "c58aff", "7025ef", "8c24fb", "c15aff", "efb3ff"],
}
STOPS = [0, .10, .40, .43, .72, 1]
PALETTE = []


def index(hex_color):
    rgb = tuple(int(hex_color[n:n + 2], 16) / 255 for n in (0, 2, 4)) + (1.0,)
    if rgb not in PALETTE:
        PALETTE.append(rgb)
    return PALETTE.index(rgb)


def solid(color, alpha=1):
    return {"Format": F.PaintSolid, "PaletteIndex": index(color), "Alpha": alpha}


def gradient(colors, bottom, top):
    # x2/y2 controls the perpendicular direction, making this a vertical gradient.
    return {
        "Format": F.PaintLinearGradient,
        "ColorLine": {"Extend": "pad", "ColorStop": [
            {"StopOffset": pos, "PaletteIndex": index(c), "Alpha": 1}
            for pos, c in zip(STOPS, colors)
        ]},
        "x0": 0, "y0": bottom, "x1": 0, "y1": top,
        "x2": 1000, "y2": bottom,
    }


def painted(glyph, paint, dx=0, dy=0):
    p = {"Format": F.PaintGlyph, "Glyph": glyph, "Paint": paint}
    if dx or dy:
        p = {"Format": F.PaintTranslate, "dx": dx, "dy": dy, "Paint": p}
    return p


def surround(glyph, color, radius, alpha=1):
    # Overlapping translated silhouettes form an entirely vector, scalable rim.
    return [painted(glyph, solid(color, alpha),
                    round(radius * math.cos(i * math.tau / 12), 2),
                    round(radius * math.sin(i * math.tau / 12), 2))
            for i in range(12)]


def theme_for(char):
    if char.isdigit():
        return "pink"
    if char.upper() == "G":
        return "cyan"
    if char.upper() == "B":
        return "gold"
    return ("pink", "cyan", "gold", "violet")[ord(char.upper()[0]) % 4]


def rename(font, family):
    # Remove upstream family/style/variable instance names; retain copyright/license.
    font["name"].names = [n for n in font["name"].names if n.nameID in (0, 13, 14)]
    names = {
        1: family, 2: "Regular", 3: f"1.000;NRIV;{family.replace(' ', '')}",
        4: family, 5: "Version 1.000", 6: family.replace(" ", ""),
        7: "Neon Riviera is a modified Montserrat font.",
        8: "Montserrat Project Authors; Neon Riviera contributors",
        9: "Montserrat Project Authors; neon treatment by Neon Riviera contributors",
        10: "Heavy italic neon display face inspired by a colorful 210GB reference. "
            "Derived from Montserrat Black Italic under SIL OFL 1.1.",
        16: family, 17: "Regular",
    }
    for nid, value in names.items():
        for platform, encoding, lang in [(3, 1, 0x409), (1, 0, 0)]:
            font["name"].setName(value, nid, platform, encoding, lang)
    # Each appearance is a standalone display family, not an application style link.
    font["OS/2"].fsSelection &= ~((1 << 0) | (1 << 5))
    font["OS/2"].fsSelection |= (1 << 6)
    font["head"].macStyle = 0


def build():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source font checksum does not match the recorded source")
    OUT.mkdir(exist_ok=True)
    font = instantiateVariableFont(TTFont(SOURCE), {"wght": 900}, inplace=False)
    options = subset.Options()
    options.name_IDs = [0, 13, 14]
    options.recalc_timestamp = False
    sub = subset.Subsetter(options=options)
    repertoire = set(range(0x20, 0x7F)) | set(range(0xA0, 0x180))
    repertoire |= {0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022,
                   0x2026, 0x20AC, 0x2122, 0x2190, 0x2191, 0x2192, 0x2193,
                   0x2212, 0x221E}
    sub.populate(unicodes=repertoire)
    sub.subset(font)
    # Space for the luminous rims, extrusion, and extended Latin accents.
    for glyph, (advance, lsb) in list(font["hmtx"].metrics.items()):
        if advance and glyph != "space":
            font["hmtx"].metrics[glyph] = (advance + 32, lsb)
    font["hhea"].ascent = max(font["hhea"].ascent, 1100)
    font["hhea"].descent = min(font["hhea"].descent, -340)
    font["OS/2"].usWinAscent = max(font["OS/2"].usWinAscent, 1150)
    font["OS/2"].usWinDescent = max(font["OS/2"].usWinDescent, 360)
    font.recalcTimestamp = False

    mono = copy.deepcopy(font)
    rename(mono, "Neon Riviera Mono")
    mono.save(OUT / "NeonRiviera-Mono.ttf")

    color = copy.deepcopy(font)
    rename(color, "Neon Riviera Color")
    cmap = color.getBestCmap()
    glyph_chars = {}
    for code, glyph in cmap.items():
        glyph_chars.setdefault(glyph, chr(code))
    paints = {}
    glyf = color["glyf"]
    for glyph in color.getGlyphOrder():
        outline = glyf[glyph]
        outline.recalcBounds(glyf)
        if not hasattr(outline, "xMin") or outline.xMin == outline.xMax:
            continue
        char = glyph_chars.get(glyph, "?")
        theme = theme_for(char)
        colors = THEMES[theme]
        glow = colors[3]
        layers = []
        for radius, opacity in [(28, .045), (18, .08), (11, .14)]:
            layers.extend(surround(glyph, glow, radius, opacity))
        # Purple 3D sides below the face, then a saturated outer bevel.
        for step in range(7, 0, -1):
            layers.append(painted(glyph, solid("3b0756"), step * 1.8, step * -2.6))
        layers.extend(surround(glyph, glow, 6))
        layers.extend(surround(glyph, "fff3ff", 3.1))
        top = max(180, min(outline.yMax, 700))
        bottom = max(outline.yMin, -30)
        layers.append(painted(glyph, gradient(colors, bottom, top)))
        paints[glyph] = {"Format": F.PaintColrLayers, "Layers": layers}
    color["COLR"] = buildCOLR(paints, version=1, glyphMap=color.getReverseGlyphMap())
    color["CPAL"] = buildCPAL([PALETTE])
    color.save(OUT / "NeonRiviera-Color.ttf")
    # Reload to verify serialization, required tables, and Croatian coverage.
    for filename in ("NeonRiviera-Mono.ttf", "NeonRiviera-Color.ttf"):
        check = TTFont(OUT / filename)
        assert all(ord(c) in check.getBestCmap() for c in "ČĆĐŠŽčćđšž210GB")
        assert len(check.getBestCmap()) > 300
        if "Color" in filename:
            assert check["COLR"].version == 1
            assert len(check["COLR"].table.BaseGlyphList.BaseGlyphPaintRecord) > 300
        print(filename, len(check.getBestCmap()), "characters,", (OUT / filename).stat().st_size, "bytes")


if __name__ == "__main__":
    build()
