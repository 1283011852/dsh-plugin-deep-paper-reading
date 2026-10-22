#!/usr/bin/env python3
"""Render a structured diagram spec to PNG (and optionally to Mermaid source).

Why this script exists
----------------------
A reading report whose logic chain is only text is not a visual report. Mermaid
is the source of truth for every diagram, but Mermaid does not render inside a
`.docx`, and `mermaid-cli` needs Node + a headless Chromium download. This
script is the offline fallback: one JSON spec -> one PNG that can be dropped
into Word, plus the same spec emitted as Mermaid source so the report keeps the
text version.

Design rules that are enforced (not advisory)
---------------------------------------------
* Every diagram carries a `source` line. A diagram whose numbers cannot be
  traced to a figure panel, a table, or a Results paragraph is not allowed
  into the report; the renderer refuses to draw one without `source`.
* Nothing is synthesised: the renderer only draws what is in the spec. It does
  not compute statistics, infer categories, or fill missing cells.
* Status colours are paired with a glyph, so the figure survives greyscale
  printing and colour-vision deficiency.

Usage
-----
    python render-diagram.py spec.json --out fig.png [--mermaid fig.mmd]
    python render-diagram.py spec.json --out fig.png --scale 2
    python render-diagram.py --selftest [--tmp DIR]

Kinds
-----
    flow      layered flowchart: the full-paper logic chain, claim trees,
              alternative-hypothesis trees, main-text <-> figure mapping
    matrix    verdict grid: figure/text consistency, method evaluation,
              experiment inventory
    scatter   two-axis risk / gap map: limitation severity x conclusion impact
    timeline  phase bars: experimental chronology, cohort flow

Requires Pillow only. No network access, no browser, no LaTeX.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - environment check
    sys.stderr.write(
        "render-diagram.py needs Pillow. Install it (pip install pillow) or use\n"
        "mermaid-cli instead; do not hand-draw the figure and call it rendered.\n"
    )
    raise SystemExit(2)


# --------------------------------------------------------------------------
# palette — one place, so the report, the figures and the Word export agree
# --------------------------------------------------------------------------

INK = "#1F2937"
MUTED = "#6B7280"
LINE = "#94A3B8"
CANVAS = "#FFFFFF"
PANEL = "#F8FAFC"

# node roles -> (fill, stroke, text)
ROLE_STYLE = {
    "context":      ("#F1F5F9", "#64748B", "#1F2937"),
    "gap":          ("#FEF3C7", "#B45309", "#7C2D12"),
    "hypothesis":   ("#DBEAFE", "#1D4ED8", "#1E3A5F"),
    "experiment":   ("#CCFBF1", "#0F766E", "#134E4A"),
    "result":       ("#EDE9FE", "#6D28D9", "#3B0764"),
    "interpretation": ("#FCE7F3", "#BE185D", "#831843"),
    "conclusion":   ("#DCFCE7", "#16A34A", "#14532D"),
    "implication":  ("#E0F2FE", "#0284C7", "#0C4A6E"),
    "risk":         ("#FEE2E2", "#DC2626", "#7F1D1D"),
    "supplementary": ("#F5F5F4", "#78716C", "#292524"),
}

# edge types -> (colour, dashed)
EDGE_STYLE = {
    "support":       ("#94A3B8", False),
    "elimination":   ("#DC2626", False),
    "extension":     ("#2563EB", False),
    "mechanism":     ("#7C3AED", False),
    "application":   ("#059669", False),
    "validation":    ("#0891B2", False),
    "leap":          ("#DC2626", True),
    "contradiction": ("#EA580C", True),
    "neutral":       ("#94A3B8", False),
}

EDGE_LABEL_ZH = {
    "support": "支撑",
    "elimination": "排除",
    "extension": "扩展",
    "mechanism": "机制",
    "application": "应用",
    "validation": "验证",
    "leap": "跳跃",
    "contradiction": "矛盾",
    "neutral": "承接",
}

# status -> (fill, stroke, glyph, default zh label)
STATUS_STYLE = {
    "ok":   ("#DCFCE7", "#16A34A", "○", "一致"),
    "warn": ("#FEF3C7", "#D97706", "△", "存疑"),
    "bad":  ("#FEE2E2", "#DC2626", "×", "矛盾"),
    "na":   ("#F1F5F9", "#CBD5E1", "–", "不适用"),
    "":     ("#FFFFFF", "#E2E8F0", "", ""),
}

FONT_CANDIDATES = [
    # Windows
    ("C:/Windows/Fonts/msyh.ttc", 0),
    ("C:/Windows/Fonts/msyhbd.ttc", 0),
    ("C:/Windows/Fonts/simhei.ttf", 0),
    ("C:/Windows/Fonts/Deng.ttf", 0),
    ("C:/Windows/Fonts/simsun.ttc", 0),
    # Linux
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf", 0),
    ("/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
    # macOS
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
    # last resort: Pillow's bundled font (no CJK coverage)
    ("__pillow_default__", 0),
]


class Fonts:
    """CJK-capable font family, discovered once and reused."""

    def __init__(self) -> None:
        self.path, self.index, self.cjk_ok = self._discover()
        self._cache: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}

    @staticmethod
    def _discover() -> tuple[str, int, bool]:
        for path, index in FONT_CANDIDATES:
            if path == "__pillow_default__":
                continue
            if os.path.isfile(path):
                return path, index, True
        return "__pillow_default__", 0, False

    def get(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        key = (size, bold)
        if key in self._cache:
            return self._cache[key]
        size = max(6, int(size))
        if self.path == "__pillow_default__":
            font = ImageFont.load_default(size=size)
        else:
            path = self.path
            if bold and self.cjk_ok:
                bold_path = path.replace("msyh.ttc", "msyhbd.ttc").replace("Deng.ttf", "Dengb.ttf")
                if bold_path != path and os.path.isfile(bold_path):
                    path = bold_path
            font = ImageFont.truetype(path, size=size, index=self.index)
        self._cache[key] = font
        return font


FONTS = Fonts()


# --------------------------------------------------------------------------
# text helpers
# --------------------------------------------------------------------------

# Superscript/subscript characters are common in biomedical labels (10⁻⁹ M,
# CD8⁺) and routinely missing from CJK fonts — they come out as tofu boxes.
# Rewrite them into plain notation rather than shipping boxes.
SUPER_SUB = {
    "\u207b": "-", "\u207a": "+", "\u2070": "^0", "\u00b9": "^1", "\u00b2": "^2",
    "\u00b3": "^3", "\u2074": "^4", "\u2075": "^5", "\u2076": "^6", "\u2077": "^7",
    "\u2078": "^8", "\u2079": "^9",
    "\u2080": "_0", "\u2081": "_1", "\u2082": "_2", "\u2083": "_3", "\u2084": "_4",
    "\u2085": "_5", "\u2086": "_6", "\u2087": "_7", "\u2088": "_8", "\u2089": "_9",
    # arrows and relations that CJK fonts routinely lack (these come out as tofu
    # boxes exactly like the superscripts did)
    "\u2194": "<->", "\u21c4": "<->", "\u21d2": "=>", "\u21d4": "<=>",
}
_replaced_chars: set[str] = set()


def sanitize(text: str) -> str:
    """Replace font-hostile super/subscript characters; report what was changed."""
    if not text:
        return text
    out = []
    for ch in text:
        if ch in SUPER_SUB:
            _replaced_chars.add(ch)
            out.append(SUPER_SUB[ch])
        else:
            out.append(ch)
    return "".join(out)


def sanitize_report():
    if _replaced_chars:
        shown = " ".join(sorted(_replaced_chars))
        sys.stderr.write(
            f"note: rewrote super/subscript characters to plain notation ({shown}); "
            "CJK fonts usually lack these glyphs\n"
        )


def tokenise(text: str) -> list[str]:
    """Split into wrap units: CJK per character, Latin per word, spaces kept."""
    out: list[str] = []
    buf = ""
    for ch in text:
        if ch.isspace():
            if buf:
                out.append(buf)
                buf = ""
            out.append(" ")
        elif ord(ch) > 0x2E7F or ch in "，。；：、！？（）【】《》—…·":
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def wrap(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> list[str]:
    lines: list[str] = []
    line = ""
    for token in tokenise(text):
        candidate = line + token
        if font.getlength(candidate) <= max_width or not line:
            line = candidate
        else:
            lines.append(line.rstrip())
            line = "" if token == " " else token
    if line.strip():
        lines.append(line.rstrip())
    return lines or [""]


def text_block(draw, xy, text, font, fill, max_width=None, align="left", line_gap=1.28):
    """Draw (optionally wrapped) text; returns consumed height."""
    x, y = xy
    lines = wrap(text, font, max_width) if max_width else [text]
    step = font.size * line_gap
    for i, line in enumerate(lines):
        width = font.getlength(line)
        dx = 0
        if align == "center":
            dx = -width / 2
        elif align == "right":
            dx = -width
        draw.text((x + dx, y + i * step), line, font=font, fill=fill)
    return len(lines) * step


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def arrow(draw, start, end, colour, dashed=False, width=2.0, head=11.0):
    x0, y0 = start
    x1, y1 = end
    if dashed:
        _dashed_line(draw, (x0, y0), (x1, y1), colour, width)
    else:
        draw.line((x0, y0, x1, y1), fill=colour, width=int(round(width)))
    # arrowhead
    import math
    angle = math.atan2(y1 - y0, x1 - x0)
    a1 = angle + math.radians(152)
    a2 = angle - math.radians(152)
    p1 = (x1 + head * math.cos(a1), y1 + head * math.sin(a1))
    p2 = (x1 + head * math.cos(a2), y1 + head * math.sin(a2))
    draw.polygon([(x1, y1), p1, p2], fill=colour)


def _dashed_line(draw, a, b, colour, width, dash=9, gap=6):
    import math
    x0, y0 = a
    x1, y1 = b
    total = math.hypot(x1 - x0, y1 - y0)
    if total == 0:
        return
    ux, uy = (x1 - x0) / total, (y1 - y0) / total
    pos = 0.0
    while pos < total:
        end = min(pos + dash, total)
        draw.line(
            (x0 + ux * pos, y0 + uy * pos, x0 + ux * end, y0 + uy * end),
            fill=colour,
            width=int(round(width)),
        )
        pos = end + gap


def pill(draw, cx, cy, text, font, fg=INK, bg="#FFFFFF", border=None, pad=(6, 3)):
    w = font.getlength(text)
    h = font.size
    x0 = cx - w / 2 - pad[0]
    y0 = cy - h / 2 - pad[1]
    x1 = cx + w / 2 + pad[0]
    y1 = cy + h / 2 + pad[1]
    draw.rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) / 2, fill=bg,
                           outline=border or bg, width=1)
    draw.text((x0 + pad[0], y0 + pad[1] - 0.5), text, font=font, fill=fg)
    return (x0, y0, x1, y1)


# --------------------------------------------------------------------------
# spec validation
# --------------------------------------------------------------------------

class SpecError(Exception):
    pass


def require(spec: dict, key: str):
    if key not in spec or spec[key] in (None, "", [], {}):
        raise SpecError(f"spec is missing required field: {key}")
    return spec[key]


def check_source(spec: dict):
    """No diagram without a traceable source line."""
    source = (spec.get("source") or "").strip()
    if not source:
        raise SpecError(
            "spec.source is required: state where every drawn fact comes from "
            "(e.g. 'Fig 2A-C; Results §2.1 第 2-3 段; Table S1'). A diagram without a "
            "source line cannot be traced back to the paper, so it is not admissible."
        )
    return source


# --------------------------------------------------------------------------
# kind: flow
# --------------------------------------------------------------------------

def render_flow(spec: dict, scale: float) -> Image.Image:
    layers = require(spec, "layers")
    nodes = require(spec, "nodes")
    edges = spec.get("edges") or []
    zh = spec.get("lang", "zh") != "en"

    title_font = FONTS.get(25 * scale, bold=True)
    sub_font = FONTS.get(14 * scale)
    node_font = FONTS.get(13.5 * scale)
    role_font = FONTS.get(10.5 * scale)
    edge_font = FONTS.get(11 * scale)
    src_font = FONTS.get(11 * scale)
    layer_font = FONTS.get(11.5 * scale, bold=True)

    margin = 46 * scale
    gap_x = 30 * scale
    gap_y = 62 * scale
    max_box = 250 * scale
    min_box = 118 * scale
    pad_x = 12 * scale
    pad_y = 10 * scale
    # left column reserved for layer names — sized from the labels, not guessed,
    # otherwise a two-character Chinese label lands on top of the first box
    layer_labels = [layer.get("name", "") if isinstance(layer, dict) else "" for layer in layers]
    widest = max([layer_font.getlength(name) for name in layer_labels if name] or [0])
    rail = max(30 * scale, min(widest, 130 * scale) + 18 * scale)

    # ---- measure nodes -------------------------------------------------
    boxes: dict[str, dict] = {}
    for layer in layers:
        names = layer.get("nodes") if isinstance(layer, dict) else layer
        for name in names or []:
            node = nodes.get(name)
            if node is None:
                raise SpecError(f"layers reference unknown node: {name}")
            label = node.get("label", name)
            lines = wrap(label, node_font, max_box - 2 * pad_x)
            text_w = max(node_font.getlength(line) for line in lines)
            role = node.get("role", "context")
            if role not in ROLE_STYLE:
                raise SpecError(f"node {name}: unknown role {role!r}")
            role_label = node.get("tag") or ""
            # The tag (figure numbers, "Exp 1") is drawn inside the box too, so the
            # box has to be wide enough for it — otherwise it spills over the
            # neighbouring box, which is what the first render of Fig V1 did.
            tag_w = role_font.getlength(role_label) if role_label else 0
            width = max(min_box, min(max_box, max(text_w, tag_w) + 2 * pad_x))
            tag_lines = wrap(role_label, role_font, width - 2 * pad_x) if role_label else []
            boxes[name] = {
                "lines": lines,
                "w": width,
                "text_h": len(lines) * node_font.size * 1.28,
                "tag_lines": tag_lines,
                "tag_h": len(tag_lines) * role_font.size * 1.4,
                "role": role,
                "role_label": role_label,
            }

    for name, box in boxes.items():
        box["h"] = box["text_h"] + 2 * pad_y + box["tag_h"]
        box["h"] = max(box["h"], 46 * scale)

    # ---- place nodes ---------------------------------------------------
    rows = []
    for layer in layers:
        names = layer.get("nodes") if isinstance(layer, dict) else layer
        label = layer.get("name", "") if isinstance(layer, dict) else ""
        names = names or []
        width = sum(boxes[n]["w"] for n in names) + gap_x * max(0, len(names) - 1)
        rows.append({"names": names, "label": label, "width": width,
                     "height": max([boxes[n]["h"] for n in names] or [0])})

    content_w = max([row["width"] for row in rows] + [200 * scale])
    # Corridor edges (layer-skipping or backwards) are drawn to the right of the
    # box area, so their room and their labels have to be reserved up front.
    layer_of = {}
    for index, layer in enumerate(layers):
        for name in (layer.get("nodes") if isinstance(layer, dict) else layer) or []:
            layer_of[name] = index
    skips = [e for e in edges
             if e.get("from") in layer_of and e.get("to") in layer_of
             and layer_of[e["to"]] != layer_of[e["from"]] + 1]
    skip_pad = 0.0
    if skips:
        widest_label = max(edge_font.getlength(
            e.get("label") or EDGE_LABEL_ZH.get(e.get("type", "neutral"), "")) for e in skips)
        skip_pad = 18 * scale + 12 * scale * len(skips) + min(widest_label, 150 * scale) + 24 * scale
    width = int(margin * 2 + rail + content_w + 24 * scale + skip_pad)
    header_h = 0
    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    if title:
        header_h += 40 * scale
    if subtitle:
        header_h += 26 * scale
    header_h += 12 * scale if header_h else 12 * scale

    source = (spec.get("source") or "").strip()
    footer_lines = _source_lines(spec, source, src_font, width - 2 * margin)
    legend_h = 30 * scale if edges else 0
    footer_h = len(footer_lines) * src_font.size * 1.2 + 14 * scale if footer_lines else 6 * scale
    body_h = sum(row["height"] for row in rows) + gap_y * max(0, len(rows) - 1)
    height = int(margin * 2 + header_h + body_h + legend_h + footer_h)

    img = Image.new("RGB", (width, height), CANVAS)
    draw = ImageDraw.Draw(img)

    y = margin
    if title:
        text_block(draw, (margin + rail, y), title, title_font, INK,
                   max_width=width - 2 * margin - rail)
        y += 40 * scale
    if subtitle:
        text_block(draw, (margin + rail, y), subtitle, sub_font, MUTED,
                   max_width=width - 2 * margin - rail)
        y += 26 * scale
    y += 12 * scale

    # rows
    for row in rows:
        row["top"] = y
        row["left"] = margin + rail + (content_w - row["width"]) / 2
        x = row["left"]
        for name in row["names"]:
            box = boxes[name]
            box["x0"] = x
            box["x1"] = x + box["w"]
            box["y0"] = y + (row["height"] - box["h"]) / 2
            box["y1"] = box["y0"] + box["h"]
            x += box["w"] + gap_x
        if row["label"]:
            layer_font_ = layer_font
            lines = wrap(row["label"], layer_font_, rail - 12 * scale)
            ly = y + row["height"] / 2 - len(lines) * layer_font_.size * 0.7
            for i, line in enumerate(lines):
                draw.text((margin, ly + i * layer_font_.size * 1.2), line,
                          font=layer_font_, fill=MUTED)
        y += row["height"] + gap_y

    # boxes
    for name, box in boxes.items():
        fill, stroke, ink = ROLE_STYLE[box["role"]]
        draw.rounded_rectangle((box["x0"], box["y0"], box["x1"], box["y1"]),
                               radius=8 * scale, fill=fill, outline=stroke,
                               width=int(round(1.6 * scale)))
        ty = box["y0"] + pad_y
        if box["tag_lines"]:
            for index, line in enumerate(box["tag_lines"]):
                draw.text((box["x0"] + pad_x, ty + index * role_font.size * 1.4),
                          line, font=role_font, fill=stroke)
            ty += box["tag_h"]
        for i, line in enumerate(box["lines"]):
            draw.text((box["x0"] + pad_x, ty + i * node_font.size * 1.28),
                      line, font=node_font, fill=ink)

    # edges
    corridor = 0
    row_index = {}
    for index, row in enumerate(rows):
        for name in row["names"]:
            row_index[name] = index
    drawn_labels = []
    for edge in edges:
        src, dst = edge.get("from"), edge.get("to")
        if src not in boxes or dst not in boxes:
            raise SpecError(f"edge references unknown node: {src} -> {dst}")
        etype = edge.get("type", "neutral")
        colour, dashed = EDGE_STYLE.get(etype, EDGE_STYLE["neutral"])
        a, b = boxes[src], boxes[dst]
        si, ti = row_index[src], row_index[dst]
        label = edge.get("label") or (EDGE_LABEL_ZH.get(etype, "") if zh else etype)

        if si == ti:
            # Same row: a short horizontal arrow between the facing sides. Drawing
            # these through the corridor (as an earlier version did) leaves the
            # reader with no way to tell which box a line belongs to.
            if a["x1"] <= b["x0"]:
                start = (a["x1"], (a["y0"] + a["y1"]) / 2)
                end = (b["x0"], (b["y0"] + b["y1"]) / 2)
            else:
                start = (a["x0"], (a["y0"] + a["y1"]) / 2)
                end = (b["x1"], (b["y0"] + b["y1"]) / 2)
            arrow(draw, start, end, colour, dashed, width=1.8 * scale, head=11 * scale)
            # the gap between two boxes in a row is narrower than most labels, so
            # the label goes just below the row instead of on top of the gap
            mid = ((start[0] + end[0]) / 2, max(a["y1"], b["y1"]) + 13 * scale)
        elif abs(ti - si) == 1:
            # One layer apart (either direction): a direct segment between the two
            # facing edges. Short, unambiguous, and the arrowhead touches the box
            # it points at.
            if ti > si:
                start = ((a["x0"] + a["x1"]) / 2, a["y1"])
                end = ((b["x0"] + b["x1"]) / 2, b["y0"])
            else:
                start = ((a["x0"] + a["x1"]) / 2, a["y0"])
                end = ((b["x0"] + b["x1"]) / 2, b["y1"])
            arrow(draw, start, end, colour, dashed, width=1.8 * scale, head=11 * scale)
            # label sits 62% of the way toward the target, so it reads as the
            # target's transition rather than floating in empty space
            mid = (start[0] + (end[0] - start[0]) * 0.62,
                   start[1] + (end[1] - start[1]) * 0.62)
        else:
            # Spanning two or more layers: corridor on the right. The horizontal
            # runs sit in inter-row gaps (never at box mid-height), the final run
            # drops into the target's own column, and each label is staggered
            # along the channel so parallel edges cannot share a label slot.
            corridor += 1
            off = 18 * scale + corridor * 18 * scale
            right = margin + rail + content_w + off
            src_row, dst_row = rows[si], rows[ti]
            if ti > si:
                exit_y = src_row["top"] + src_row["height"] + gap_y * 0.42
            else:
                exit_y = src_row["top"] - gap_y * 0.42
            entry_y = dst_row["top"] - gap_y * 0.42
            exit_y = max(exit_y, margin + 6 * scale)
            entry_y = max(entry_y, margin + 6 * scale)
            start = ((a["x0"] + a["x1"]) / 2, exit_y)
            cx_b = (b["x0"] + b["x1"]) / 2
            end = (cx_b, b["y0"])
            legs = [
                (start, (right, exit_y)),
                ((right, exit_y), (right, entry_y)),
                ((right, entry_y), (cx_b, entry_y)),
                ((cx_b, entry_y), end),
            ]
            for p, q in legs:
                arrow(draw, p, q, colour, dashed, width=1.8 * scale,
                      head=11 * scale if q == end else 0.1)
            mid = (right + 4 * scale, entry_y - corridor * 13 * scale)
        # a filled dot marks the origin of every edge, so "where does this line
        # start" is answered without tracing it backwards
        r = 3.6 * scale
        draw.ellipse((start[0] - r, start[1] - r, start[0] + r, start[1] + r),
                     fill=colour, outline=colour)
        if label:
            drawn_labels.append((mid, label, colour))

    for mid, label, colour in drawn_labels:
        pill(draw, mid[0], mid[1], label, edge_font, fg=INK, bg="#FFFFFF", border=colour)

    # legend, above the source line so the two never collide
    if edges:
        used = []
        for edge in edges:
            t = edge.get("type", "neutral")
            if t not in used:
                used.append(t)
        lx = margin
        ly = height - margin - footer_h - 10 * scale - src_font.size
        head = "过渡类型" if zh else "transitions"
        draw.text((lx, ly), head, font=src_font, fill=MUTED)
        lx += src_font.getlength(head) + 12 * scale
        for t in used:
            colour, dashed = EDGE_STYLE.get(t, EDGE_STYLE["neutral"])
            if dashed:
                _dashed_line(draw, (lx, ly + src_font.size * 0.6),
                             (lx + 22 * scale, ly + src_font.size * 0.6), colour,
                             1.6 * scale, dash=6 * scale, gap=4 * scale)
            else:
                draw.line((lx, ly + src_font.size * 0.6, lx + 22 * scale,
                           ly + src_font.size * 0.6), fill=colour, width=int(1.6 * scale))
            lx += 28 * scale
            text = EDGE_LABEL_ZH.get(t, t) if zh else t
            draw.text((lx, ly), text, font=src_font, fill=INK)
            lx += src_font.getlength(text) + 16 * scale

    _footer(draw, spec, margin, height - margin - footer_h + 6 * scale,
            src_font, width)
    return img


# --------------------------------------------------------------------------
# kind: matrix
# --------------------------------------------------------------------------

def render_matrix(spec: dict, scale: float) -> Image.Image:
    rows = require(spec, "rows")
    cols = require(spec, "cols")
    cells = require(spec, "cells")
    if len(cells) != len(rows):
        raise SpecError(f"cells has {len(cells)} rows but rows has {len(rows)}")
    for index, line in enumerate(cells):
        if len(line) != len(cols):
            raise SpecError(f"cells row {index} has {len(line)} entries, expected {len(cols)}")

    zh = spec.get("lang", "zh") != "en"
    title_font = FONTS.get(25 * scale, bold=True)
    sub_font = FONTS.get(14 * scale)
    head_font = FONTS.get(12.5 * scale, bold=True)
    row_font = FONTS.get(12.5 * scale)
    cell_font = FONTS.get(11.5 * scale)
    src_font = FONTS.get(11 * scale)

    margin = 44 * scale
    row_label_w = max(row_font.getlength(str(r)) for r in rows) + 26 * scale
    row_label_w = min(max(row_label_w, 120 * scale), 260 * scale)
    cell_w = max(96 * scale, min(150 * scale, 118 * scale))
    head_h = max(head_font.size * 2.9, 40 * scale)
    cell_h = max(cell_font.size * 3.4, 52 * scale)

    width = int(margin * 2 + row_label_w + cell_w * len(cols))
    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    header_h = (40 * scale if title else 0) + (26 * scale if subtitle else 0) + 14 * scale
    legend_h = 40 * scale
    height = int(margin * 2 + header_h + head_h + cell_h * len(rows) + legend_h + 30 * scale)

    img = Image.new("RGB", (width, height), CANVAS)
    draw = ImageDraw.Draw(img)
    y = margin
    if title:
        text_block(draw, (margin, y), title, title_font, INK, max_width=width - 2 * margin)
        y += 40 * scale
    if subtitle:
        text_block(draw, (margin, y), subtitle, sub_font, MUTED, max_width=width - 2 * margin)
        y += 26 * scale
    y += 14 * scale

    x0 = margin
    # header
    for j, col in enumerate(cols):
        cx0 = x0 + row_label_w + j * cell_w
        draw.rectangle((cx0, y, cx0 + cell_w, y + head_h), fill=PANEL, outline="#E2E8F0")
        lines = wrap(str(col), head_font, cell_w - 10 * scale)
        ty = y + (head_h - len(lines) * head_font.size * 1.2) / 2
        for i, line in enumerate(lines):
            draw.text((cx0 + cell_w / 2 - head_font.getlength(line) / 2,
                       ty + i * head_font.size * 1.2), line, font=head_font, fill=INK)
    y += head_h

    for i, row in enumerate(rows):
        draw.rectangle((x0, y, x0 + row_label_w, y + cell_h), fill=PANEL, outline="#E2E8F0")
        lines = wrap(str(row), row_font, row_label_w - 14 * scale)
        ty = y + (cell_h - len(lines) * row_font.size * 1.2) / 2
        for k, line in enumerate(lines):
            draw.text((x0 + 8 * scale, ty + k * row_font.size * 1.2), line, font=row_font, fill=INK)

        for j in range(len(cols)):
            value = cells[i][j]
            note = ""
            if isinstance(value, dict):
                status = value.get("s", "")
                note = value.get("note", "")
            else:
                status = "" if value is None else str(value)
            status = status.strip()
            if status not in STATUS_STYLE:
                raise SpecError(f"cell [{i}][{j}]: unknown status {status!r}")
            fill, stroke, glyph, _ = STATUS_STYLE[status]
            cx0 = x0 + row_label_w + j * cell_w
            draw.rectangle((cx0, y, cx0 + cell_w, y + cell_h), fill=fill, outline="#E2E8F0")
            gy = y + cell_h / 2 - cell_font.size * (0.9 if note else 0.6)
            if glyph:
                draw.text((cx0 + cell_w / 2 - cell_font.getlength(glyph) / 2, gy),
                          glyph, font=cell_font, fill=stroke)
            if note:
                for k, line in enumerate(wrap(note, cell_font, cell_w - 10 * scale)[:2]):
                    draw.text((cx0 + cell_w / 2 - cell_font.getlength(line) / 2,
                               gy + cell_font.size * 1.25 + k * cell_font.size * 1.15),
                              line, font=cell_font, fill=INK)
        y += cell_h

    # legend
    legend = spec.get("legend")
    if legend:
        lx = margin
        ly = y + 14 * scale
        for key, label in legend.items():
            fill, stroke, glyph, _ = STATUS_STYLE.get(key, STATUS_STYLE[""])
            draw.rectangle((lx, ly, lx + 16 * scale, ly + 16 * scale), fill=fill,
                           outline=stroke, width=int(1.2 * scale))
            if glyph:
                draw.text((lx + 8 * scale - cell_font.getlength(glyph) / 2, ly + 1 * scale),
                          glyph, font=cell_font, fill=stroke)
            lx += 22 * scale
            draw.text((lx, ly + 1 * scale), str(label), font=src_font, fill=INK)
            lx += src_font.getlength(str(label)) + 22 * scale
            if lx > width - margin - 90 * scale:
                lx = margin
                ly += 20 * scale

    _footer(draw, spec, margin, _footer_y(height, margin, src_font), src_font, width)
    return img


# --------------------------------------------------------------------------
# kind: scatter
# --------------------------------------------------------------------------

def render_scatter(spec: dict, scale: float) -> Image.Image:
    points = require(spec, "points")
    zh = spec.get("lang", "zh") != "en"
    title_font = FONTS.get(25 * scale, bold=True)
    sub_font = FONTS.get(14 * scale)
    axis_font = FONTS.get(12.5 * scale, bold=True)
    tick_font = FONTS.get(10.5 * scale)
    point_font = FONTS.get(11.5 * scale)
    src_font = FONTS.get(11 * scale)

    margin = 46 * scale
    plot_w = 470 * scale
    plot_h = 330 * scale
    left_pad = 108 * scale
    bottom_pad = 78 * scale
    top_pad = (40 * scale if spec.get("title") else 0) + (26 * scale if spec.get("subtitle") else 0) + 20 * scale
    right_pad = 210 * scale  # room for point labels
    width = int(margin * 2 + left_pad + plot_w + right_pad)
    height = int(margin * 2 + top_pad + plot_h + bottom_pad + 30 * scale)

    img = Image.new("RGB", (width, height), CANVAS)
    draw = ImageDraw.Draw(img)
    y = margin
    if spec.get("title"):
        text_block(draw, (margin, y), spec["title"], title_font, INK, max_width=width - 2 * margin)
        y += 40 * scale
    if spec.get("subtitle"):
        text_block(draw, (margin, y), spec["subtitle"], sub_font, MUTED, max_width=width - 2 * margin)
        y += 26 * scale
    y += 20 * scale

    px0 = margin + left_pad
    py0 = y
    px1 = px0 + plot_w
    py1 = py0 + plot_h

    draw.rectangle((px0, py0, px1, py1), fill="#FFFFFF", outline=LINE, width=int(1.4 * scale))
    # mid gridlines
    draw.line((px0 + plot_w / 2, py0, px0 + plot_w / 2, py1), fill="#E2E8F0", width=1)
    draw.line((px0, py1 - plot_h / 2, px1, py1 - plot_h / 2), fill="#E2E8F0", width=1)

    def to_px(x, yv):
        return (px0 + x * plot_w, py1 - yv * plot_h)

    quadrant_labels = spec.get("quadrants") or {}
    # corners, not centres: a centred label always ends up under a point
    for key, text, qx, qy, anchor in (
        ("tl", quadrant_labels.get("tl"), 0.035, 0.945, "left"),
        ("tr", quadrant_labels.get("tr"), 0.965, 0.945, "right"),
        ("bl", quadrant_labels.get("bl"), 0.035, 0.055, "left"),
        ("br", quadrant_labels.get("br"), 0.965, 0.055, "right"),
    ):
        if not text:
            continue
        line = wrap(str(text), tick_font, plot_w * 0.42)[0]
        dx = 0 if anchor == "left" else -tick_font.getlength(line)
        draw.text((px0 + qx * plot_w + dx, py1 - qy * plot_h - tick_font.size / 2),
                  line, font=tick_font, fill="#B6C2D1")

    status_colour = {
        "fatal": ("#7F1D1D", "#FEE2E2"),
        "major": ("#B91C1C", "#FEE2E2"),
        "moderate": ("#B45309", "#FEF3C7"),
        "minor": ("#0F766E", "#CCFBF1"),
        "strength": ("#15803D", "#DCFCE7"),
    }

    placed = []
    for point in points:
        x = float(point.get("x", 0.5))
        yv = float(point.get("y", 0.5))
        if not (0 <= x <= 1 and 0 <= yv <= 1):
            raise SpecError(f"point {point.get('label')!r}: x/y must be within 0..1")
        status = point.get("status", "moderate")
        stroke, fill = status_colour.get(status, ("#334155", "#E2E8F0"))
        cx, cy = to_px(x, yv)
        r = 9 * scale
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=stroke,
                     width=int(1.6 * scale))
        label = point.get("label", "")
        placed.append((cx, cy, label, stroke))

    # labels to the right, with simple vertical de-overlap — the advance has to
    # account for labels actually taking two lines, or the second line lands on
    # the next label
    placed.sort(key=lambda item: item[1])
    last_y = -1e9
    for cx, cy, label, colour in placed:
        lines = wrap(label, point_font, right_pad - 26 * scale)[:2]
        ty = max(cy - point_font.size * 0.6, last_y)
        draw.line((cx + 9 * scale, cy, px1 + 12 * scale, ty + point_font.size * 0.55),
                  fill="#CBD5E1", width=1)
        for k, line in enumerate(lines):
            draw.text((px1 + 16 * scale, ty + k * point_font.size * 1.15), line,
                      font=point_font, fill=INK)
        last_y = ty + len(lines) * point_font.size * 1.15 + 3 * scale

    # axes
    xlabel = spec.get("x_label", "")
    ylabel = spec.get("y_label", "")
    if xlabel:
        lw = axis_font.getlength(xlabel)
        draw.text((px0 + plot_w / 2 - lw / 2, py1 + 22 * scale), xlabel, font=axis_font, fill=INK)
    if ylabel:
        tmp = Image.new("RGBA", (int(plot_h), int(axis_font.size * 2.4)), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(tmp)
        tdraw.text((0, 0), ylabel, font=axis_font, fill=INK)
        rotated = tmp.rotate(90, expand=True)
        img.paste(rotated, (int(px0 - 46 * scale), int(py0 + plot_h / 2 - rotated.height / 2)),
                  rotated)

    ticks = [
        (spec.get("x_min", "低"), px0, py1 + 4 * scale, "center"),
        (spec.get("x_max", "高"), px1, py1 + 4 * scale, "center"),
        (spec.get("y_min", "低"), px0 - 10 * scale, py1 - tick_font.size, "right"),
        (spec.get("y_max", "高"), px0 - 10 * scale, py0, "right"),
    ]
    for text, tx, ty_, anchor in ticks:
        if not text:
            continue
        dx = -tick_font.getlength(text) / 2 if anchor == "center" else -tick_font.getlength(text)
        draw.text((tx + dx, ty_), text, font=tick_font, fill=MUTED)

    _footer(draw, spec, margin, _footer_y(height, margin, src_font), src_font, width)
    return img


# --------------------------------------------------------------------------
# kind: timeline
# --------------------------------------------------------------------------

def render_timeline(spec: dict, scale: float) -> Image.Image:
    phases = require(spec, "phases")
    zh = spec.get("lang", "zh") != "en"
    title_font = FONTS.get(25 * scale, bold=True)
    sub_font = FONTS.get(14 * scale)
    label_font = FONTS.get(12.5 * scale, bold=True)
    note_font = FONTS.get(11 * scale)
    axis_font = FONTS.get(11.5 * scale, bold=True)
    src_font = FONTS.get(11 * scale)

    margin = 46 * scale
    label_w = max(label_font.getlength(str(p.get("label", ""))) for p in phases) + 24 * scale
    label_w = min(max(label_w, 130 * scale), 260 * scale)
    plot_w = 470 * scale
    note_w = 300 * scale
    row_h = max(note_font.size * 3.6, 54 * scale)

    end_max = max(float(p.get("end", 1)) for p in phases) or 1.0
    width = int(margin * 2 + label_w + plot_w + note_w)
    header_h = (40 * scale if spec.get("title") else 0) + (26 * scale if spec.get("subtitle") else 0) + 18 * scale
    height = int(margin * 2 + header_h + row_h * len(phases) + 42 * scale + 30 * scale)

    img = Image.new("RGB", (width, height), CANVAS)
    draw = ImageDraw.Draw(img)
    y = margin
    if spec.get("title"):
        text_block(draw, (margin, y), spec["title"], title_font, INK, max_width=width - 2 * margin)
        y += 40 * scale
    if spec.get("subtitle"):
        text_block(draw, (margin, y), spec["subtitle"], sub_font, MUTED, max_width=width - 2 * margin)
        y += 26 * scale
    y += 18 * scale

    px0 = margin + label_w
    note_x = px0 + plot_w + 22 * scale
    for phase in phases:
        start = float(phase.get("start", 0))
        end = float(phase.get("end", 1))
        status = phase.get("status", "experiment")
        fill, stroke, ink = ROLE_STYLE.get(status, ROLE_STYLE["experiment"])
        bx0 = px0 + (start / end_max) * plot_w
        bx1 = px0 + (end / end_max) * plot_w
        draw.rounded_rectangle((bx0, y + 4 * scale, bx1, y + row_h - 8 * scale),
                               radius=6 * scale, fill=fill, outline=stroke,
                               width=int(1.4 * scale))
        # The bar keeps its exact extent; the note lives in a fixed column on the
        # right, so a short phase does not squeeze its own description.
        lines = wrap(str(phase.get("label", "")), label_font, label_w - 16 * scale)
        ty = y + (row_h - len(lines) * label_font.size * 1.2) / 2
        for i, line in enumerate(lines):
            draw.text((margin, ty + i * label_font.size * 1.2), line, font=label_font, fill=INK)
        note = str(phase.get("note", ""))
        ref = phase.get("ref")
        head = f"{ref}｜{note}" if ref and note else (str(ref) if ref else note)
        if head:
            for i, line in enumerate(wrap(head, note_font, note_w - 10 * scale)[:3]):
                draw.text((note_x, y + 10 * scale + i * note_font.size * 1.18),
                          line, font=note_font, fill=INK if note else MUTED)
        y += row_h

    # axis
    draw.line((px0, y + 6 * scale, px0 + plot_w, y + 6 * scale), fill=LINE, width=int(1.2 * scale))
    xlabel = spec.get("x_label", "")
    if xlabel:
        draw.text((px0 + plot_w / 2 - axis_font.getlength(xlabel) / 2, y + 12 * scale),
                  xlabel, font=axis_font, fill=INK)

    _footer(draw, spec, margin, _footer_y(height, margin, src_font), src_font, width)
    return img


# --------------------------------------------------------------------------
# footer / mermaid
# --------------------------------------------------------------------------

def _footer_y(height, margin, font):
    """Top of the one-line source block that sits on the bottom margin."""
    return height - margin - font.size * 1.2 + 2


def _source_lines(spec, source, font, max_width):
    if not source:
        return []
    prefix = "来源：" if spec.get("lang", "zh") != "en" else "Source: "
    return wrap(prefix + source, font, max_width)


def _footer(draw, spec, margin, y, font, width):
    """Draw the mandatory source line at `y` (top of the block)."""
    source = (spec.get("source") or "").strip()
    lines = _source_lines(spec, source, font, width - 2 * margin)
    for i, line in enumerate(lines):
        draw.text((margin, y + i * font.size * 1.2), line, font=font, fill=MUTED)


def to_mermaid(spec: dict) -> str:
    kind = spec.get("kind")
    title = spec.get("title", "diagram")
    acc = spec.get("source", "")
    out = ["```mermaid"]
    if kind == "flow":
        out.append("flowchart TD")
        out.append(f"    accTitle: {title}")
        out.append(f"    accDescr: {acc}")
        for layer in spec.get("layers", []):
            names = layer.get("nodes") if isinstance(layer, dict) else layer
            for name in names or []:
                node = spec["nodes"][name]
                label = str(node.get("label", name)).replace('"', "'")
                out.append(f'    {name}["{label}"]')
        for edge in spec.get("edges", []):
            a, b = edge["from"], edge["to"]
            label = edge.get("label") or EDGE_LABEL_ZH.get(edge.get("type", "neutral"), "")
            arrow = "-.->" if edge.get("type") in ("leap", "contradiction") else "-->"
            if label:
                out.append(f'    {a} {arrow}|"{label}"| {b}')
            else:
                out.append(f"    {a} {arrow} {b}")
        roles = sorted({spec["nodes"][n].get("role", "context")
                        for layer in spec.get("layers", [])
                        for n in (layer.get("nodes") if isinstance(layer, dict) else layer) or []})
        for role in roles:
            fill, stroke, ink = ROLE_STYLE.get(role, ROLE_STYLE["context"])
            out.append(f"    classDef {role} fill:{fill},stroke:{stroke},color:{ink}")
            members = [n for layer in spec.get("layers", [])
                       for n in (layer.get("nodes") if isinstance(layer, dict) else layer) or []
                       if spec["nodes"][n].get("role", "context") == role]
            out.append(f"    class {','.join(members)} {role}")
    elif kind == "timeline":
        out.append("gantt")
        out.append(f"    accTitle: {title}")
        out.append("    dateFormat X")
        out.append("    axisFormat %s")
        for phase in spec.get("phases", []):
            name = str(phase.get("label", "")).replace(":", " ")
            out.append(f"    {name} :{int(phase.get('start', 0))}, {int(phase.get('end', 1))}")
    elif kind == "matrix":
        rows, cols, cells = spec["rows"], spec["cols"], spec["cells"]
        out.append("flowchart LR")
        out.append(f"    accTitle: {title}")
        header = "| |" + "|".join(str(c) for c in cols) + "|"
        sep = "|---|" + "|".join(":-:" for _ in cols) + "|"
        out.append("")
        out.append("<!-- matrix kind has no faithful Mermaid equivalent; the verdict grid is")
        out.append("     kept as a Markdown table (source of truth) and the PNG carries colour. -->")
        out.append("")
        out.append(header)
        out.append(sep)
        for row, line in zip(rows, cells):
            cells_txt = "|".join(
                (STATUS_STYLE.get((c.get("s") if isinstance(c, dict) else str(c)) or "", STATUS_STYLE[""])[2]
                 + (f" {c.get('note')}" if isinstance(c, dict) and c.get("note") else ""))
                for c in line)
            out.append(f"| {row} |{cells_txt}|")
    elif kind == "scatter":
        out.append("quadrantChart")
        out.append(f"    accTitle: {title}")
        names = {0.25: "低", 0.75: "高"}
        out.append("    x-axis 低影响 --> 高影响")
        out.append("    y-axis 低严重 --> 高严重")
        out.append("    quadrant-1 高危")
        out.append("    quadrant-2 需解释")
        out.append("    quadrant-3 次要")
        out.append("    quadrant-4 值得写")
        for point in spec.get("points", []):
            label = str(point.get("label", "")).replace(":", "：").replace("[", "(").replace("]", ")")
            out.append(f"    {label}: [{float(point.get('x', .5)):.2f}, {float(point.get('y', .5)):.2f}]")
    out.append("```")
    return "\n".join(out)


# --------------------------------------------------------------------------
# selftest + CLI
# --------------------------------------------------------------------------

SAMPLE_FLOW = {
    "kind": "flow", "lang": "zh",
    "title": "示例：全文逻辑链主图",
    "subtitle": "分层 + 过渡类型 + 断裂点标注（虚线红）",
    "source": "示例数据，仅用于自检；真实报告中必须写 Fig X / Results §Y / Table Z",
    "layers": [
        {"name": "背景", "nodes": ["bg"]},
        {"name": "空白", "nodes": ["gap"]},
        {"name": "假说", "nodes": ["hyp"]},
        {"name": "实验", "nodes": ["e1", "e2"]},
        {"name": "结果", "nodes": ["r1", "r2"]},
        {"name": "结论", "nodes": ["con"]},
    ],
    "nodes": {
        "bg": {"label": "uPAR 在多种实体瘤高表达", "role": "context"},
        "gap": {"label": "缺乏原位功能证据", "role": "gap"},
        "hyp": {"label": "uPAR 驱动侵袭", "role": "hypothesis"},
        "e1": {"label": "类器官敲除", "role": "experiment", "tag": "Exp 1"},
        "e2": {"label": "原位移植", "role": "experiment", "tag": "Exp 2"},
        "r1": {"label": "侵袭下降", "role": "result"},
        "r2": {"label": "转移灶减少", "role": "result"},
        "con": {"label": "uPAR 为可干预靶点", "role": "conclusion"},
    },
    "edges": [
        {"from": "bg", "to": "gap", "type": "neutral"},
        {"from": "gap", "to": "hyp", "type": "neutral"},
        {"from": "hyp", "to": "e1", "type": "mechanism", "label": "机制型"},
        {"from": "e1", "to": "r1", "type": "support"},
        {"from": "r1", "to": "e2", "type": "extension", "label": "扩展型"},
        {"from": "e2", "to": "r2", "type": "support"},
        {"from": "r2", "to": "con", "type": "leap", "label": "跳跃：缺人体证据"},
    ],
}

SAMPLE_MATRIX = {
    "kind": "matrix", "lang": "zh",
    "title": "示例：图注-正文一致性矩阵",
    "source": "示例数据；真实报告须逐格标注 Fig 编号与正文段落",
    "rows": ["Fig 1A WB", "Fig 1B IF", "Fig 2C 生存曲线"],
    "cols": ["图注自洽", "正文一致", "统计可查", "图像可辨"],
    "cells": [
        ["ok", "warn", "ok", "ok"],
        ["ok", "ok", "na", "warn"],
        ["warn", "bad", "ok", "ok"],
    ],
    "legend": {"ok": "一致", "warn": "过度解读", "bad": "矛盾", "na": "不适用"},
}

SAMPLE_SCATTER = {
    "kind": "scatter", "lang": "zh",
    "title": "示例：局限风险矩阵",
    "subtitle": "横轴 = 对核心结论的影响；纵轴 = 方法学严重程度",
    "source": "示例数据；真实报告须把每个点对应到具体实验编号",
    "x_label": "对结论的影响 →", "y_label": "方法学严重程度 →",
    "quadrants": {"tl": "需正面回应", "tr": "致命", "bl": "次要", "br": "值得写进 limitation"},
    "points": [
        {"x": 0.82, "y": 0.88, "label": "无原位敲除验证", "status": "fatal"},
        {"x": 0.55, "y": 0.45, "label": "抗体未做 KO 验证", "status": "moderate"},
        {"x": 0.28, "y": 0.22, "label": "仅单一细胞系", "status": "minor"},
        {"x": 0.74, "y": 0.32, "label": "统计未校正多重比较", "status": "major"},
    ],
}

SAMPLE_TIMELINE = {
    "kind": "timeline", "lang": "zh",
    "title": "示例：实验推进时间线",
    "source": "示例数据；真实报告须标注每个阶段对应的图号",
    "x_label": "实验推进顺序 →",
    "phases": [
        {"label": "发现阶段", "start": 0, "end": 2.2, "status": "experiment",
         "note": "表达谱 + 临床队列相关性", "ref": "Fig 1"},
        {"label": "功能阶段", "start": 2.2, "end": 4.6, "status": "result",
         "note": "类器官敲除 / 回复实验", "ref": "Fig 2-3"},
        {"label": "在体阶段", "start": 4.6, "end": 6.8, "status": "experiment",
         "note": "原位移植 + 生存分析", "ref": "Fig 4"},
        {"label": "转化阶段", "start": 6.8, "end": 8.0, "status": "application",
         "note": "CAR-T 靶向验证", "ref": "Fig 5"},
    ],
}


def sanitize_spec(value):
    """Recursively rewrite font-hostile characters in every string of a spec."""
    if isinstance(value, str):
        return sanitize(value)
    if isinstance(value, list):
        return [sanitize_spec(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_spec(item) for key, item in value.items()}
    return value


def selftest(tmp: str) -> int:
    os.makedirs(tmp, exist_ok=True)
    failures = []
    for name, spec in (
        ("flow", SAMPLE_FLOW),
        ("matrix", SAMPLE_MATRIX),
        ("scatter", SAMPLE_SCATTER),
        ("timeline", SAMPLE_TIMELINE),
    ):
        path = os.path.join(tmp, f"selftest-{name}.png")
        try:
            img = RENDERERS[spec["kind"]](spec, 2.0)
            img.save(path, format="PNG", dpi=(300, 300))
            mmd = to_mermaid(spec)
            if "```mermaid" not in mmd:
                failures.append(f"{name}: mermaid emitter produced no code fence")
            print(f"ok: {name} -> {path} ({os.path.getsize(path)} bytes)")
        except Exception as error:  # noqa: BLE001 - selftest reports, never hides
            failures.append(f"{name}: {error}")

    # the source rule must actually bite
    try:
        check_source({"title": "no source"})
        failures.append("source guard did not fire on a spec without source")
    except SpecError:
        print("ok: source guard rejects a spec without source")

    if not FONTS.cjk_ok:
        print("WARN: no CJK font found; Chinese labels will render as boxes. "
              "Prefer mermaid-cli in this environment.", file=sys.stderr)

    if failures:
        print("\nselftest failed:", file=sys.stderr)
        for failure in failures:
            print("  - " + failure, file=sys.stderr)
        return 1
    print("selftest ok")
    return 0


RENDERERS = {
    "flow": render_flow,
    "matrix": render_matrix,
    "scatter": render_scatter,
    "timeline": render_timeline,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a diagram spec to PNG (offline) and optionally to Mermaid.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("spec", nargs="?", help="path to the JSON diagram spec")
    parser.add_argument("--out", help="PNG output path")
    parser.add_argument("--mermaid", help="also write the Mermaid source to this path")
    parser.add_argument("--scale", type=float, default=2.0,
                        help="pixel scale (2.0 ≈ 300 dpi for a 16 cm wide Word figure)")
    parser.add_argument("--selftest", action="store_true", help="render the built-in samples")
    parser.add_argument("--tmp", default=None, help="directory for --selftest output")
    args = parser.parse_args(argv)

    if args.selftest:
        tmp = args.tmp or tempfile.mkdtemp(prefix="diagram-selftest-")
        return selftest(tmp)

    if not args.spec or not args.out:
        parser.error("spec and --out are required unless --selftest is used")

    with open(args.spec, encoding="utf-8") as handle:
        spec = json.load(handle)

    kind = spec.get("kind")
    if kind == "tree":
        kind = spec["kind"] = "flow"
    if kind not in RENDERERS:
        raise SystemExit(f"unknown kind {spec.get('kind')!r}; expected one of {sorted(RENDERERS)}")

    check_source(spec)
    spec = sanitize_spec(spec)
    img = RENDERERS[kind](spec, args.scale)
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    img.save(args.out, format="PNG", dpi=(300, 300))
    print(f"wrote {args.out} ({img.width}x{img.height}px)")
    sanitize_report()

    if args.mermaid:
        with open(args.mermaid, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(to_mermaid(spec) + "\n")
        print(f"wrote {args.mermaid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
