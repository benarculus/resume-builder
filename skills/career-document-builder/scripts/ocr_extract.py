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
import csv
import io
from pathlib import Path

import fitz  # pymupdf
import pytesseract
from PIL import Image

PDF_SUFFIXES = {".pdf"}
ROTATIONS = (0, 90, 180, 270)
RENDER_DPI = 300


def _mean_confidence(tsv_report: str) -> float:
    """Return the mean word-level OCR confidence from a Tesseract TSV report, or -1.0 if no words were recognized.

    Tesseract reports -1 confidence for entries with no recognized text (for
    example whitespace-only regions); those are excluded from the mean.
    """
    rows = csv.DictReader(io.StringIO(tsv_report), delimiter="\t")
    confidences = [float(row["conf"]) for row in rows if float(row["conf"]) >= 0]
    if not confidences:
        return -1.0
    return sum(confidences) / len(confidences)


def ocr_best_rotation(image: Image.Image) -> str:
    """Try each supported rotation and return the text from the most confident reading.

    Automates the manual rotation trial-and-error the first run needed by hand.
    Selecting purely by output length is unreliable: OCR of an upside-down or
    sideways page can still produce plausible-looking (but wrong) characters
    that happen to be as long as, or longer than, the correctly oriented
    reading. Mean per-word confidence is a far more reliable signal of which
    rotation is actually correct, so it is used instead, with non-empty text
    length only as a tiebreaker when no candidate rotation has any recognized
    words. Both the text and the confidence report come from a single
    Tesseract invocation per rotation (`run_and_get_multiple_output`) rather
    than separate `image_to_string`/`image_to_data` passes, to avoid doubling
    the OCR work per rotation.
    """
    best_text = ""
    best_confidence = -1.0
    for degrees in ROTATIONS:
        rotated = image if degrees == 0 else image.rotate(-degrees, expand=True)
        text, tsv_report = pytesseract.run_and_get_multiple_output(rotated, extensions=["txt", "tsv"])
        confidence = _mean_confidence(tsv_report)
        is_more_confident = confidence > best_confidence
        is_tiebreak_candidate = confidence == best_confidence == -1.0 and len(text.strip()) > len(best_text.strip())
        if is_more_confident or is_tiebreak_candidate:
            best_confidence = confidence
            best_text = text
    return best_text


def extract_from_image(path: Path) -> str:
    with Image.open(path) as image:
        return ocr_best_rotation(image.convert("RGB"))


def extract_from_pdf(path: Path, page: int | None = None) -> str:
    """OCR a PDF.

    With `page` unset, OCRs every page and labels each result with a
    `--- Page N ---` marker so a caller merging this output with other
    per-page text can still attribute each block to its source page. With
    `page` set (1-based), OCRs only that page and returns its raw text with
    no marker, for targeted re-OCR of a single page in an otherwise
    normally-readable PDF.
    """
    with fitz.open(path) as document:
        if page is not None:
            if not 1 <= page <= document.page_count:
                raise ValueError(f"page {page} is out of range for a {document.page_count}-page PDF")
            return _ocr_pdf_page(document[page - 1])
        page_texts = [f"--- Page {index} ---\n{_ocr_pdf_page(pdf_page)}" for index, pdf_page in enumerate(document, start=1)]
    return "\n\n".join(page_texts)


def _ocr_pdf_page(page: "fitz.Page") -> str:
    pixmap = page.get_pixmap(dpi=RENDER_DPI)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    return ocr_best_rotation(image)


def extract_text(path: Path, page: int | None = None) -> str:
    if path.suffix.lower() in PDF_SUFFIXES:
        return extract_from_pdf(path, page=page)
    if page is not None:
        raise ValueError("--page is only supported for PDF input")
    return extract_from_image(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Image or image-based PDF to OCR")
    parser.add_argument("--output", required=True, type=Path, help="Path to write extracted text")
    parser.add_argument(
        "--page",
        type=int,
        default=None,
        help=(
            "1-based PDF page number to OCR only that page (PDF input only). "
            "Use this to re-OCR a single image-only page in a mixed PDF that has other "
            "normally-readable pages, so the readable pages are not re-OCR'd and the "
            "result can be merged back in at the correct page position, preserving "
            "per-page source pointers."
        ),
    )
    args = parser.parse_args()

    text = extract_text(args.input, page=args.page)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
