#!/usr/bin/env python3
"""render_ocr.py — Render a single OCR annotation result into an image for visual comparison with the original.

Usage:
    python render_ocr.py --type text  --text-file resp.txt --out render.png
    python render_ocr.py --type table --text-file resp.html --out render.png
    # You can also pass it directly via --text "<table>...</table>" (mind shell escaping)

Design notes:
  * Depends only on matplotlib + Pillow (confirmed available in the project environment; no HTML renderer needed).
  * Table input must be HTML containing only <table>/<tr>/<td>, rendered as a grid by rows and columns.
  * Text input is rendered with automatic line wrapping by paragraph.
  * Automatically selects a CJK font to correctly display Chinese.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt


def pick_cjk_font() -> str | None:
    """Return an available CJK font name, or None if not found."""
    prefer = [
        "Noto Sans CJK", "WenQuanYi", "Source Han Sans",
        "Microsoft YaHei", "SimHei", "Droid Sans Fallback",
        "AR PL UMing", "Noto Serif CJK",
    ]
    available = {f.name: f.fname for f in fm.fontManager.ttflist}
    for p in prefer:
        for name in available:
            if p.lower() in name.lower():
                return name
    return None

def parse_table(html: str) -> list[list[str]]:
    """Parse a 2D cell array from HTML containing only <table>/<tr>/<td>."""
    rows = re.findall(r"<tr>(.*?)</tr>", html, flags=re.S | re.I)
    grid: list[list[str]] = []
    for row in rows:
        cells = re.findall(r"<td.*?>(.*?)</td>", row, flags=re.S | re.I)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        grid.append(cells)
    return grid


def render_table(html: str, out: Path, font: str | None) -> None:
    grid = parse_table(html)
    if not grid:
        raise ValueError("No table rows parsed; please confirm the input is a <table><tr><td> structure")
    ncols = max(len(r) for r in grid)
    nrows = len(grid)
    grid = [r + [""] * (ncols - len(r)) for r in grid]

    fig_w = max(6.0, ncols * 1.0)
    fig_h = max(2.0, nrows * 0.45)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
    ax.axis("off")
    tbl = ax.table(cellText=grid, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.3)
    if font:
        for cell in tbl.get_celld().values():
            cell.get_text().set_fontfamily(font)
    fig.tight_layout(pad=0.3)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_text(text: str, out: Path, font: str | None) -> None:
    if font:
        plt.rcParams["font.family"] = font
    # Estimate height: roughly wrap by character count
    lines = max(1, len(text) // 40 + text.count("\n") + 1)
    fig_h = max(2.0, lines * 0.35)
    fig, ax = plt.subplots(figsize=(8.5, fig_h), dpi=150)
    ax.axis("off")
    ax.text(0.01, 0.99, text, va="top", ha="left", wrap=True,
            fontsize=11, transform=ax.transAxes)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def main() -> int:
    ap = argparse.ArgumentParser(description="Render an OCR annotation result into an image")
    ap.add_argument("--type", required=True, choices=["text", "table"],
                    help="Annotation type: text or table")
    ap.add_argument("--text", help="Annotation content passed directly")
    ap.add_argument("--text-file", help="Read annotation content from a file (takes precedence over --text)")
    ap.add_argument("--out", required=True, help="Output PNG path")
    args = ap.parse_args()

    if args.text_file:
        content = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text is not None:
        content = args.text
    else:
        print("Error: --text or --text-file is required", file=sys.stderr)
        return 2

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    font = pick_cjk_font()

    if args.type == "table":
        render_table(content, out, font)
    else:
        render_text(content, out, font)

    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
