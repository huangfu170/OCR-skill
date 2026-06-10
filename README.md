# OCR-skill

[English](#english) | [中文](#中文)

Use Codex / Claude Code to perform precise OCR on images, with a built-in visual feedback loop that verifies the result against the original image.

借助 Codex / Claude Code 对图片做精确 OCR，内置「视觉回环」验证机制，将识别结果与原图反复比对修正。

---

## English

### Overview

This project packages an **OCR annotation & validation skill** for use with agentic coding tools (Claude Code / Codex). Instead of trusting a single OCR pass, it runs a loop:

**Annotate → Render → Compare with original → Re-annotate if needed**

Plain text is output as plain text; tables are output as HTML using only `<table>` / `<tr>` / `<td>` tags. Each round renders the current result back into an image so it can be visually compared against the source, and any content-level differences trigger another round (up to 4).

### Repository layout

| Path | Description |
| --- | --- |
| `ocr-skill-en/` | English version of the skill (`SKILL.md` + `render_ocr.py`) |
| `ocr-skill-zh/` | Chinese version of the skill |
| `render_ocr.py` | Renders one OCR result (text or table) into a PNG for comparison |

### Requirements

- Python 3
- `matplotlib` + `Pillow`
- A CJK font (e.g. Noto Sans CJK) for rendering Chinese; auto-detected.

### Usage

```bash
# Render a table result
echo "<table>...</table>" > ./ocr_resp.html
python render_ocr.py --type table --text-file ./ocr_resp.html --out ./render.png

# Render a text result
echo "..." > ./ocr_resp.txt
python render_ocr.py --type text --text-file ./ocr_resp.txt --out ./render.png
```

In practice you let the agent drive the loop: it reads the source image, produces an annotation, renders it, compares, and stops once only presentational (font / spacing / border) differences remain.


---

## 中文

### 简介

本项目封装了一个用于智能编码工具（Claude Code / Codex）的 **OCR 标注与验证 skill**。它不依赖单次 OCR 结果，而是运行一个循环：

**标注 → 渲染 → 与原图对比 → 必要时重标注**

普通文本按纯文本输出；表格仅用 `<table>` / `<tr>` / `<td>` 三种标签输出为 HTML。每轮都会把当前结果重新渲染成图片，与原图做视觉对比；只要存在内容层面的差异就进入下一轮（最多 4 轮）。

### 目录结构

| 路径 | 说明 |
| --- | --- |
| `ocr-skill-en/` | 英文版 skill（`SKILL.md` + `render_ocr.py`） |
| `ocr-skill-zh/` | 中文版 skill |
| `render_ocr.py` | 将单条 OCR 结果（文本或表格）渲染为 PNG，供比对 |

### 环境依赖

- Python 3
- `matplotlib` + `Pillow`
- 渲染中文需 CJK 字体（如 Noto Sans CJK），脚本会自动探测。

### 用法

```bash
# 渲染表格结果
echo "<table>...</table>" > ./ocr_resp.html
python render_ocr.py --type table --text-file ./ocr_resp.html --out ./render.png

# 渲染文本结果
echo "..." > ./ocr_resp.txt
python render_ocr.py --type text --text-file ./ocr_resp.txt --out ./render.png
```

实际使用中由 agent 驱动整个循环：读取原图、产出标注、渲染、对比，直到只剩表现层（字体 / 间距 / 边框）差异时停止。
