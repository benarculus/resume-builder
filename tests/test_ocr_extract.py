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


def _load_deterministic_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a scalable font at a fixed, legible size without depending on any
    particular system font (for example `Arial.ttf`, which is not installed on
    the Ubuntu CI runner). Pillow's bundled default font supports a `size`
    argument since 10.1; `ImageFont.load_default()` without a size falls back
    to a tiny bitmap font that Tesseract cannot reliably recognize.
    """
    return ImageFont.load_default(size=size)


def _draw_known_text_image(size: tuple[int, int] = (600, 200)) -> Image.Image:
    image = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(image)
    font = _load_deterministic_font(36)
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
@pytest.mark.parametrize("physical_rotation_degrees", [90, 270])
def test_ocr_extract_finds_best_rotation_for_a_sideways_image(
    tmp_path: Path, physical_rotation_degrees: int
) -> None:
    """Regression coverage for automatic rotation selection.

    Physically rotates the source image before OCR so the script must try
    every supported rotation and pick the one that yields recognizable text,
    exercising both the rotation loop and the confidence-based selection
    logic (rather than only the upright, no-rotation-needed case).
    """
    upright_image = _draw_known_text_image()
    sideways_image = upright_image.rotate(physical_rotation_degrees, expand=True)
    image_path = tmp_path / f"award-{physical_rotation_degrees}.png"
    sideways_image.save(image_path)
    output_path = tmp_path / f"award-{physical_rotation_degrees}.txt"

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
    # Size the page to the image's own aspect ratio so `insert_image` does not
    # stretch/distort the text, which otherwise degrades OCR accuracy.
    with Image.open(image_path) as source_image:
        image_size = source_image.size
    document = fitz.open()
    page = document.new_page(width=image_size[0], height=image_size[1])
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
