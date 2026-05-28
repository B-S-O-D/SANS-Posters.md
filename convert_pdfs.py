#!/usr/bin/env python3
import fitz  # PyMuPDF
import os
import re
import sys

PDF_DIR = "/home/user/SANS-Posters.md"

def clean_text(text):
    # Normalize whitespace within lines but preserve intentional newlines
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    return text

def blocks_to_markdown(page):
    """Extract text blocks from a page and format as markdown."""
    lines = []
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if block["type"] != 0:  # skip images
            continue
        block_lines = []
        for line in block["lines"]:
            spans = line["spans"]
            if not spans:
                continue
            # Determine dominant font size for this line
            sizes = [s["size"] for s in spans if s["text"].strip()]
            text = "".join(s["text"] for s in spans).strip()
            if not text:
                continue
            avg_size = sum(sizes) / len(sizes) if sizes else 10
            # Heuristic heading detection by font size
            if avg_size >= 18:
                block_lines.append(f"## {text}")
            elif avg_size >= 14:
                block_lines.append(f"### {text}")
            else:
                block_lines.append(text)
        if block_lines:
            lines.append("\n".join(block_lines))
    return "\n\n".join(lines)

def pdf_to_markdown(pdf_path):
    doc = fitz.open(pdf_path)
    title = os.path.splitext(os.path.basename(pdf_path))[0]
    parts = [f"# {title}\n"]
    for page_num, page in enumerate(doc, 1):
        if len(doc) > 1:
            parts.append(f"---\n*Page {page_num}*\n")
        md = blocks_to_markdown(page)
        if md.strip():
            parts.append(md)
    doc.close()
    return "\n\n".join(parts)

def main():
    pdfs = sorted([f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")])
    total = len(pdfs)
    print(f"Converting {total} PDFs...")
    errors = []
    for i, pdf_name in enumerate(pdfs, 1):
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        md_name = os.path.splitext(pdf_name)[0] + ".md"
        md_path = os.path.join(PDF_DIR, md_name)
        try:
            md_content = pdf_to_markdown(pdf_path)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"[{i}/{total}] OK: {md_name}")
        except Exception as e:
            print(f"[{i}/{total}] ERROR: {pdf_name}: {e}", file=sys.stderr)
            errors.append((pdf_name, str(e)))
    print(f"\nDone. {total - len(errors)}/{total} converted successfully.")
    if errors:
        print("Errors:")
        for name, err in errors:
            print(f"  {name}: {err}")

if __name__ == "__main__":
    main()
