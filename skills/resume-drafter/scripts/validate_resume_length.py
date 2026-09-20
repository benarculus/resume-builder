#!/usr/bin/env python3
"""Validate a tailored resume's word count and rendered page count before delivery.

Word count is computed strictly from the approved intermediate JSON payload's
body fields (summary, experience, education, skills, awards) and never from
parsing the rendered `.docx` text, so the counting boundary stays fixed and
reproducible regardless of renderer formatting. Page count comes from an
actual rendered artifact: the `.docx` is converted to PDF with headless
LibreOffice (`soffice --headless --convert-to pdf`) and the resulting pages
are counted with `pymupdf`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import fitz  # pymupdf

WORD_COUNT_FIELDS = ("summary", "experience", "education", "skills", "awards")
WORD_BUDGET_MIN = 475
WORD_BUDGET_MAX = 600
PAGE_CAP = 2


def collect_strings(value: Any) -> list[str]:
    """Recursively collect every string leaf value from a JSON-like structure."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(collect_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(collect_strings(item))
        return strings
    return []


def count_words(payload: dict[str, Any]) -> int:
    """Count words only from the payload's body fields, excluding contact metadata.

    Only `summary`, `experience`, `education`, `skills`, and `awards` are counted.
    `basics` (name, email, location, clearance) and `unmetRequirements` are
    excluded, matching resume-drafter's documented word-target boundary.
    """
    words = 0
    for field in WORD_COUNT_FIELDS:
        if field not in payload:
            continue
        for text in collect_strings(payload[field]):
            words += len(text.split())
    return words


def convert_docx_to_pdf(docx_path: Path, output_dir: Path) -> Path:
    subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pdf_path = output_dir / f"{docx_path.stem}.pdf"
    if not pdf_path.exists():
        raise RuntimeError(f"expected converted PDF at {pdf_path}, but it was not created")
    return pdf_path


def count_rendered_pages(docx_path: Path) -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = convert_docx_to_pdf(docx_path, Path(tmpdir))
        with fitz.open(pdf_path) as document:
            return document.page_count


def validate_length(docx_path: Path, payload_path: Path) -> dict[str, Any]:
    with payload_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    word_count = count_words(payload)
    page_count = count_rendered_pages(docx_path)
    return {
        "wordCount": word_count,
        "wordBudget": {"min": WORD_BUDGET_MIN, "max": WORD_BUDGET_MAX},
        "pageCount": page_count,
        "pageCap": PAGE_CAP,
        "withinWordBudget": WORD_BUDGET_MIN <= word_count <= WORD_BUDGET_MAX,
        "withinPageCap": page_count <= PAGE_CAP,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path, help="Rendered resume .docx (page count only)")
    parser.add_argument("--payload", required=True, type=Path, help="Approved intermediate JSON payload (word count only)")
    args = parser.parse_args()

    result = validate_length(args.docx, args.payload)
    print(json.dumps(result, indent=2))
    return 0 if result["withinWordBudget"] and result["withinPageCap"] else 1


if __name__ == "__main__":
    sys.exit(main())
