#!/usr/bin/env python3
"""Extract text from a scanned or image-based career-document source using OCR.

Supports a single image file or a single- or multi-page image-based PDF (a PDF
with no extractable text layer). Uses `pytesseract` bound to the system
`tesseract-ocr` binary for OCR, and `pymupdf` to rasterize PDF pages so no
second system-level PDF dependency (for example Poppler) is required. Both
`pytesseract` and `pymupdf` run on Linux, Windows, and macOS.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz  # pymupdf
import pytesseract
from PIL import Image

PDF_SUFFIXES = {".pdf"}
ROTATIONS = (0, 90, 180, 270)
RENDER_DPI = 300


def ocr_best_rotation(image: Image.Image) -> str:
    """Try each supported rotation and return the text with the most extracted content.

    Automates the manual rotation trial-and-error the first run needed by hand.
    """
    best_text = ""
    for degrees in ROTATIONS:
        rotated = image if degrees == 0 else image.rotate(-degrees, expand=True)
        text = pytesseract.image_to_string(rotated)
        if len(text.strip()) > len(best_text.strip()):
            best_text = text
    return best_text


def extract_from_image(path: Path) -> str:
    with Image.open(path) as image:
        return ocr_best_rotation(image.convert("RGB"))


def extract_from_pdf(path: Path) -> str:
    page_texts: list[str] = []
    with fitz.open(path) as document:
        for page in document:
            pixmap = page.get_pixmap(dpi=RENDER_DPI)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            page_texts.append(ocr_best_rotation(image))
    return "\n\n".join(page_texts)


def extract_text(path: Path) -> str:
    if path.suffix.lower() in PDF_SUFFIXES:
        return extract_from_pdf(path)
    return extract_from_image(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Image or image-based PDF to OCR")
    parser.add_argument("--output", required=True, type=Path, help="Path to write extracted text")
    args = parser.parse_args()

    text = extract_text(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
