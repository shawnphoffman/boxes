from __future__ import annotations

import os
import platform
import warnings
from functools import lru_cache

try:
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.ttLib import TTFont

    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False


FONT_SEARCH_PATHS = {
    "Darwin": [
        "/System/Library/Fonts",
        "/System/Library/Fonts/Supplemental",
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ],
    "Linux": [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
    ],
    "Windows": [
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    ],
}

FONT_MAP = {
    ("sans-serif", False, False): [
        "Arial.ttf", "Helvetica.ttc", "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf", "FreeSans.ttf",
    ],
    ("sans-serif", True, False): [
        "Arial Bold.ttf", "Helvetica Bold.ttc", "DejaVuSans-Bold.ttf",
        "LiberationSans-Bold.ttf", "FreeSansBold.ttf",
    ],
    ("sans-serif", False, True): [
        "Arial Italic.ttf", "Helvetica Oblique.ttc", "DejaVuSans-Oblique.ttf",
        "LiberationSans-Italic.ttf", "FreeSansOblique.ttf",
    ],
    ("sans-serif", True, True): [
        "Arial Bold Italic.ttf", "Helvetica Bold Oblique.ttc",
        "DejaVuSans-BoldOblique.ttf", "LiberationSans-BoldItalic.ttf",
    ],
    ("serif", False, False): [
        "Times New Roman.ttf", "Times.ttc", "DejaVuSerif.ttf",
        "LiberationSerif-Regular.ttf", "FreeSerif.ttf",
    ],
    ("serif", True, False): [
        "Times New Roman Bold.ttf", "DejaVuSerif-Bold.ttf",
        "LiberationSerif-Bold.ttf", "FreeSerifBold.ttf",
    ],
    ("serif", False, True): [
        "Times New Roman Italic.ttf", "DejaVuSerif-Italic.ttf",
        "LiberationSerif-Italic.ttf", "FreeSerifItalic.ttf",
    ],
    ("serif", True, True): [
        "Times New Roman Bold Italic.ttf", "DejaVuSerif-BoldItalic.ttf",
        "LiberationSerif-BoldItalic.ttf",
    ],
    ("monospaced", False, False): [
        "Courier New.ttf", "DejaVuSansMono.ttf",
        "LiberationMono-Regular.ttf", "FreeMono.ttf",
    ],
    ("monospaced", True, False): [
        "Courier New Bold.ttf", "DejaVuSansMono-Bold.ttf",
        "LiberationMono-Bold.ttf", "FreeMonoBold.ttf",
    ],
    ("monospaced", False, True): [
        "Courier New Italic.ttf", "DejaVuSansMono-Oblique.ttf",
        "LiberationMono-Italic.ttf", "FreeMonoOblique.ttf",
    ],
    ("monospaced", True, True): [
        "Courier New Bold Italic.ttf", "DejaVuSansMono-BoldOblique.ttf",
        "LiberationMono-BoldItalic.ttf",
    ],
}


def _find_font_file(style, bold, italic):
    candidates = FONT_MAP.get((style, bool(bold), bool(italic)), [])
    system = platform.system()
    search_dirs = FONT_SEARCH_PATHS.get(system, [])

    for font_name in candidates:
        for search_dir in search_dirs:
            path = os.path.join(search_dir, font_name)
            if os.path.isfile(path):
                return path

    if bold or italic:
        return _find_font_file(style, False, False)
    if style != "sans-serif":
        return _find_font_file("sans-serif", False, False)
    return None


@lru_cache(maxsize=32)
def _load_font(path, font_index=0):
    return TTFont(path, fontNumber=font_index)


def _fmt(v):
    return f"{v:.3f}"


def _glyph_to_path_d(glyph, glyph_set, scale, x_offset, y_baseline):
    """Convert a single glyph to SVG path commands, scaled and positioned."""
    rec = RecordingPen()
    glyph.draw(rec)

    parts = []
    for op, args in rec.value:
        if op == "moveTo":
            (x, y), = args
            parts.append(f"M {_fmt(x * scale + x_offset)} {_fmt(y_baseline - y * scale)}")
        elif op == "lineTo":
            (x, y), = args
            parts.append(f"L {_fmt(x * scale + x_offset)} {_fmt(y_baseline - y * scale)}")
        elif op == "curveTo":
            coords = []
            for x, y in args:
                coords.extend([_fmt(x * scale + x_offset), _fmt(y_baseline - y * scale)])
            parts.append(f"C {' '.join(coords)}")
        elif op == "qCurveTo":
            coords = []
            for x, y in args:
                coords.extend([_fmt(x * scale + x_offset), _fmt(y_baseline - y * scale)])
            parts.append(f"Q {' '.join(coords)}")
        elif op == "closePath":
            parts.append("Z")
        elif op == "endPath":
            pass

    return " ".join(parts)


def text_to_svg_path_d(text, style="sans-serif", bold=False, italic=False,
                       font_size=10, align="left"):
    """Convert a text string to a single SVG path 'd' attribute value.

    The path is positioned at origin (0, 0) being the top-left of the text,
    with Y increasing downward (matching SVG coordinate convention).

    align controls horizontal positioning:
      "left"/"start" - origin is left edge
      "middle"/"center" - origin is horizontal center
      "end"/"right" - origin is right edge

    Returns (path_d, total_width, total_height) scaled to font_size in px.
    Returns (None, 0, 0) if conversion is not possible.
    """
    if not HAS_FONTTOOLS:
        return None, 0, 0

    font_path = _find_font_file(style, bold, italic)
    if not font_path:
        warnings.warn(f"No font file found for {style} bold={bold} italic={italic}")
        return None, 0, 0

    font = _load_font(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font['head'].unitsPerEm
    scale = font_size / upem

    ascender = font['OS/2'].sTypoAscender * scale
    descender = font['OS/2'].sTypoDescender * scale

    all_parts = []
    x_cursor = 0.0

    for char in text:
        code = ord(char)
        glyph_name = cmap.get(code)
        if glyph_name is None:
            glyph_name = cmap.get(ord(' '), '.notdef')
            if glyph_name is None:
                continue

        glyph = glyph_set[glyph_name]
        path_d = _glyph_to_path_d(glyph, glyph_set, scale, x_cursor, ascender)
        if path_d:
            all_parts.append(path_d)
        x_cursor += glyph.width * scale

    total_width = x_cursor
    total_height = ascender - descender

    if not all_parts:
        return None, total_width, total_height

    combined = " ".join(all_parts)
    return combined, total_width, total_height
