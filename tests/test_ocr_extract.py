from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import fitz
import pytest
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/career-document-builder/scripts/ocr_extract.py"
KNOWN_TEXT = "PERFORMANCE AWARD 2024"


def _draw_known_text_image(size: tuple[int, int] = (600, 200)) -> Image.Image:
    image = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Arial.ttf", 36)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 70), KNOWN_TEXT, fill="black", font=font)
    return image


def _tesseract_available() -> bool:
    try:
        subprocess.run(
            ["tesseract", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


requires_tesseract = pytest.mark.skipif(
    not _tesseract_available(),
    reason="tesseract-ocr system binary is not installed in this environment",
)


@requires_tesseract
def test_ocr_extract_reads_text_from_an_image(tmp_path: Path) -> None:
    image_path = tmp_path / "award.png"
    _draw_known_text_image().save(image_path)
    output_path = tmp_path / "award.txt"

    subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(image_path), "--output", str(output_path)],
        check=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert text.strip()
    assert "AWARD" in text.upper()


@requires_tesseract
def test_ocr_extract_reads_text_from_a_scanned_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "scanned-award.pdf"
    image_path = tmp_path / "award-page.png"
    _draw_known_text_image().save(image_path)

    # Build a single-page PDF containing only a rasterized image (no text layer),
    # matching the image-based scanned-PDF case the first run needed to handle.
    document = fitz.open()
    page = document.new_page()
    page.insert_image(page.rect, filename=str(image_path))
    document.save(pdf_path)
    document.close()

    output_path = tmp_path / "scanned-award.txt"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(pdf_path), "--output", str(output_path)],
        check=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert text.strip()
    assert "AWARD" in text.upper()
