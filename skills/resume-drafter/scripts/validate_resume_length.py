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
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import fitz  # pymupdf

WORD_BUDGET_MIN = 475
WORD_BUDGET_MAX = 600
PAGE_CAP = 2

_BUILD_DOCX_PATH = Path(__file__).resolve().parent / "build_docx.py"


def _load_build_docx():
    """Load build_docx.py's rendering helpers so word counting stays in lockstep
    with what is actually rendered, instead of duplicating field-selection rules.
    """
    spec = importlib.util.spec_from_file_location("build_docx", _BUILD_DOCX_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_build_docx = _load_build_docx()


def _count_words(text: str) -> int:
    """Count words in rendered text, ignoring decorative separator tokens
    (e.g. the standalone em-dash `build_docx.py` joins fields with) that
    contain no alphanumeric characters and are not real words.
    """
    return sum(1 for token in str(text).split() if any(char.isalnum() for char in token))


def _rendered_experience_text(role: dict[str, Any]) -> list[str]:
    """Return only the text build_docx.py renders for one experience entry."""
    texts = [str(role[key]) for key in ("title", "company") if role.get(key)]
    dates = _build_docx.role_dates(role)
    if dates:
        texts.append(dates)
    texts.extend(str(item) for item in role.get("bullets", []))
    return texts


def _rendered_award_text(item: dict[str, Any]) -> list[str]:
    """Return only the text build_docx.py renders for one award entry.

    build_docx.py renders `details`, falling back to `title` only when
    `details` is absent; it never renders both.
    """
    details = item.get("details") or item.get("title") or ""
    return [str(details)] if details else []


def count_words(payload: dict[str, Any]) -> int:
    """Count words only from the text build_docx.py actually renders.

    Only `summary`, `experience`, `education`, `skills`, and `awards` are
    counted, and only their renderer-selected fields, so validation cannot
    reject or accept a resume based on text that never appears in the
    delivered document. `basics` (name, email, location, clearance) and
    `unmetRequirements` are excluded, matching resume-drafter's documented
    word-target boundary.
    """
    words = 0

    summary = payload.get("summary")
    if summary:
        words += _count_words(summary)

    for role in payload.get("experience", []) or []:
        for text in _rendered_experience_text(role):
            words += _count_words(text)

    for item in payload.get("education", []) or []:
        words += _count_words(_build_docx.education_details(item))

    for skill in payload.get("skills", []) or []:
        words += _count_words(str(skill))

    for item in payload.get("awards", []) or []:
        for text in _rendered_award_text(item):
            words += _count_words(text)

    return words


def convert_docx_to_pdf(docx_path: Path, output_dir: Path) -> Path:
    # Give this conversion its own LibreOffice user profile so it never contends
    # with an already-running or concurrent `soffice` process (profile locking
    # or command forwarding to another instance can otherwise leave this
    # invocation without the expected PDF). `--norestore` also disables the
    # crash-recovery dialog that would otherwise block headless conversion.
    profile_dir = output_dir / "lo-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "soffice",
            "--headless",
            "--norestore",
            f"-env:UserInstallation={profile_dir.as_uri()}",
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
