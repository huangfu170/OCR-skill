---
name: ocr-validate
description: Triggered when the user asks to validate/proofread OCR results, or asks the model to OCR an image. Iteratively corrects OCR results through an "annotate → render → compare with original → re-annotate if needed" loop. Plain text is output as plain text; tables are output as HTML containing only table/tr/td.
---

# OCR Annotation and Validation Loop

OCR-annotate an image and verify, via a visual feedback loop, that the result is faithful to the original.

## When to use

- The user asks to validate, proofread, or check whether OCR results are correct.
- The user asks you to OCR / recognize text or tables in an image.

## Core loop

For each image to process, run the following loop (at most 4 rounds, to prevent infinite loops):

1. **Annotate**: Read the original image and produce an OCR result.
   - If the content is plain text: output plain text, preserving the original line breaks and paragraphs.
   - If the content is a table: determine the table's alignment structure and output HTML, **allowing only the three tags `<table>` `<tr>` `<td>`**. No other tags or attributes are permitted, such as `<th>`, `<thead>`, `<tbody>`, `colspan`, `rowspan`, `style`, `class`, etc. Each row should have a consistent number of cells. If the original image has a clear column-alignment structure (e.g., index columns, numeric columns, code columns), you **must** split it into separate `<td>` cells and must not simulate alignment with spaces.


2. **Render**: Write this round's annotation result to a temporary file (`./ocr_resp.html` or `./ocr_resp.txt`) and use `render_ocr.py` to render it into an image (`./ocr_render_roundN.png`). After each round except the last, use `rm -f` to delete the temporary files and rendered images produced in that round.

3. **Compare**: Place the rendered image and the original side by side and analyze the differences item by item.

4. **Decision**:
   - If the differences are **purely presentational** (font, font size, color, cell border thickness, row height, alignment, whitespace, anti-aliasing, etc.), the content is faithful → **end the loop**.
   - If there are **content differences** (missing/extra characters, wrong characters, wrong numbers/IDs, misaligned cells, mismatched row/column counts, missing rows/columns, wrong text order, etc.) → proceed to the next round, providing [rendered image + original image + previous OCR result] together as input for re-annotation, focusing on fixing the content differences found in the previous round.

## Render tool usage

`render_ocr.py` is located in the same directory as the skill. When calling it, first determine the skill's directory, then call it with a relative path:

```bash
# SKILL_DIR points to the directory containing this SKILL.md (i.e., ocr-validate/)
# Temporary files are written to the project working directory; render output uses an incrementing round number (round1, round2, ...)

# Table
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "<table>...</table>" > ./ocr_resp.html
python "$SKILL_DIR/render_ocr.py" --type table --text-file ./ocr_resp.html --out ./ocr_render_round1.png

# Text
echo "..." > ./ocr_resp.txt
python "$SKILL_DIR/render_ocr.py" --type text --text-file ./ocr_resp.txt --out ./ocr_render_round1.png

# After each round, delete the round's temporary files and rendered image
rm -f ./ocr_resp.html ./ocr_resp.txt ./ocr_render_round1.png
```

The script depends only on matplotlib + Pillow and automatically picks a CJK font to render Chinese. The output PNG path is printed to stdout.

## Comparison checklist

After reading the original and rendered images, verify in the following order. Any single mismatch counts as a content difference:

- **Tables**: whether the number of rows and the number of columns per row match the original; compare cell contents cell by cell; whether the positions of empty cells correspond; whether numbers and IDs are correct with no duplication/misalignment.
- **Text**: compare sentence by sentence for wrong/missing/extra characters; whether paragraph and line-break order match; whether any punctuation is missing.

Differences in the rendered image's font, grid-line style, and whitespace versus the original are normal and **are not grounds for re-annotation**.

## Conclusion and output

After the loop ends, report to the user: the final OCR result, how many rounds were iterated, which content differences were fixed in each round, and the basis for judging the last round as "purely presentational differences".

> Note: The rendering script serves the human/model visual feedback loop. The rendering style does not aim for pixel-level fidelity to the original layout; it is only used to expose content-level differences.
