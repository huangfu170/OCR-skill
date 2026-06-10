#!/usr/bin/env python3
"""render_ocr.py — 将一条 OCR 标注结果渲染为图片，供与原图做视觉对比。

用法:
    python render_ocr.py --type text  --text-file resp.txt --out render.png
    python render_ocr.py --type table --text-file resp.html --out render.png
    # 也可用 --text "<table>...</table>" 直接传入（注意 shell 转义）

设计要点:
  * 仅依赖 matplotlib + Pillow（项目环境已确认可用，无需 HTML 渲染器）。
  * 表格输入必须是只含 <table>/<tr>/<td> 的 HTML，按行列渲染为网格。
  * 文本输入按段落自动换行渲染。
  * 自动选用 CJK 字体以正确显示中文。
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
    """返回一个可用的 CJK 字体名，找不到返回 None。"""
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
    """从只含 <table>/<tr>/<td> 的 HTML 解析出二维单元格数组。"""
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
        raise ValueError("未解析到任何表格行；请确认输入是 <table><tr><td> 结构")
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
    # 估算高度：按字符数粗略折行
    lines = max(1, len(text) // 40 + text.count("\n") + 1)
    fig_h = max(2.0, lines * 0.35)
    fig, ax = plt.subplots(figsize=(8.5, fig_h), dpi=150)
    ax.axis("off")
    ax.text(0.01, 0.99, text, va="top", ha="left", wrap=True,
            fontsize=11, transform=ax.transAxes)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def main() -> int:
    ap = argparse.ArgumentParser(description="渲染 OCR 标注结果为图片")
    ap.add_argument("--type", required=True, choices=["text", "table"],
                    help="标注类型：text 或 table")
    ap.add_argument("--text", help="直接传入的标注内容")
    ap.add_argument("--text-file", help="从文件读取标注内容（优先于 --text）")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    args = ap.parse_args()

    if args.text_file:
        content = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text is not None:
        content = args.text
    else:
        print("错误：需提供 --text 或 --text-file", file=sys.stderr)
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
