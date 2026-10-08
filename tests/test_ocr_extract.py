from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import fitz
import pytest
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/career-document-builder/scripts/ocr_extract.py"
KNOWN_TEXT = "PERFORMANCE AWARD 2024"


def _load_ocr_extract() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ocr_extract", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OCR_EXTRACT: ModuleType = _load_ocr_extract()


def _tsv_report(*confidences: int) -> str:
    rows = ["level\tconf\ttext"]
    rows.extend(f"5\t{confidence}\tword" for confidence in confidences)
    return "\n".join(rows) + "\n"


def _assert_rotation_calls(
    image: Image.Image, calls: list[tuple[Image.Image, list[str]]]
) -> None:
    assert len(calls) == 4
    for degrees, (called_image, extensions) in zip((0, 90, 180, 270), calls):
        expected_image = image if degrees == 0 else image.rotate(-degrees, expand=True)
        assert called_image.size == expected_image.size
        assert called_image.tobytes() == expected_image.tobytes()
        assert extensions == ["txt", "tsv"]


@pytest.mark.parametrize(
    ("report", "expected"),
    [
        (_tsv_report(80, 100), 90.0),
        (_tsv_report(-1, 80, 100), 90.0),
        ("level\tconf\ttext\n", -1.0),
    ],
)
def test_mean_confidence_averages_words_and_ignores_missing_confidence(
    report: str, expected: float
) -> None:
    assert OCR_EXTRACT._mean_confidence(report) == expected


def test_ocr_best_rotation_prefers_confidence_over_longer_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = Image.new("RGB", (2, 3), color="white")
    responses = [
        ("this is a much longer low-confidence reading", _tsv_report(40)),
        ("short confident reading", _tsv_report(95)),
        ("middle reading", _tsv_report(70)),
        ("another reading", _tsv_report(80)),
    ]
    calls: list[tuple[Image.Image, list[str]]] = []

    def fake_ocr(
        candidate: Image.Image, *, extensions: list[str]
    ) -> tuple[str, str]:
        calls.append((candidate, extensions))
        return responses[len(calls) - 1]

    monkeypatch.setattr(
        OCR_EXTRACT.pytesseract, "run_and_get_multiple_output", fake_ocr
    )

    assert OCR_EXTRACT.ocr_best_rotation(image) == "short confident reading"
    _assert_rotation_calls(image, calls)


def test_ocr_best_rotation_uses_longest_text_when_no_words_are_recognized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = Image.new("RGB", (2, 3), color="white")
    no_words = "level\tconf\ttext\n"
    responses = [
        ("first", no_words),
        ("   longer unrecognized text   ", no_words),
        ("middle", no_words),
        ("last", no_words),
    ]
    calls: list[tuple[Image.Image, list[str]]] = []

    def fake_ocr(
        candidate: Image.Image, *, extensions: list[str]
    ) -> tuple[str, str]:
        calls.append((candidate, extensions))
        return responses[len(calls) - 1]

    monkeypatch.setattr(
        OCR_EXTRACT.pytesseract, "run_and_get_multiple_output", fake_ocr
    )

    assert (
        OCR_EXTRACT.ocr_best_rotation(image)
        == "   longer unrecognized text   "
    )
    _assert_rotation_calls(image, calls)


def test_ocr_best_rotation_selects_the_180_degree_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = Image.new("RGB", (2, 3), color="white")
    responses = [
        ("zero degrees", _tsv_report(30)),
        ("ninety degrees", _tsv_report(50)),
        ("one hundred eighty degrees", _tsv_report(99)),
        ("two hundred seventy degrees", _tsv_report(60)),
    ]
    calls: list[tuple[Image.Image, list[str]]] = []

    def fake_ocr(
        candidate: Image.Image, *, extensions: list[str]
    ) -> tuple[str, str]:
        calls.append((candidate, extensions))
        return responses[len(calls) - 1]

    monkeypatch.setattr(
        OCR_EXTRACT.pytesseract, "run_and_get_multiple_output", fake_ocr
    )

    assert OCR_EXTRACT.ocr_best_rotation(image) == "one hundred eighty degrees"
    _assert_rotation_calls(image, calls)


@pytest.mark.parametrize("page", [0, 3])
def test_extract_from_pdf_rejects_out_of_range_pages(tmp_path: Path, page: int) -> None:
    pdf_path = tmp_path / "two-pages.pdf"
    document = fitz.open()
    document.new_page()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(ValueError, match="page .* is out of range"):
        OCR_EXTRACT.extract_from_pdf(pdf_path, page=page)


def test_extract_text_rejects_page_selection_for_image_input(tmp_path: Path) -> None:
    image_path = tmp_path / "image.png"
    Image.new("RGB", (2, 3), color="white").save(image_path)

    with pytest.raises(ValueError, match="--page is only supported for PDF input"):
        OCR_EXTRACT.extract_text(image_path, page=1)


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


@pytest.mark.usefixtures("requires_tesseract")
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


@pytest.mark.usefixtures("requires_tesseract")
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


@pytest.mark.usefixtures("requires_tesseract")
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


def _build_two_page_pdf(tmp_path: Path, first_text: str, second_text: str) -> Path:
    pdf_path = tmp_path / "two-page-award.pdf"
    document = fitz.open()
    for index, page_text in enumerate((first_text, second_text)):
        image = Image.new("RGB", (600, 200), color="white")
        draw = ImageDraw.Draw(image)
        draw.text((20, 70), page_text, fill="black", font=_load_deterministic_font(36))
        image_path = tmp_path / f"page-{index}.png"
        image.save(image_path)
        page = document.new_page(width=600, height=200)
        page.insert_image(page.rect, filename=str(image_path))
    document.save(pdf_path)
    document.close()
    return pdf_path


@pytest.mark.usefixtures("requires_tesseract")
def test_ocr_extract_labels_each_page_in_default_multi_page_output(tmp_path: Path) -> None:
    pdf_path = _build_two_page_pdf(tmp_path, "PAGE ONE AWARD", "PAGE TWO AWARD")
    output_path = tmp_path / "two-page.txt"

    subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(pdf_path), "--output", str(output_path)],
        check=True,
    )

    text = output_path.read_text(encoding="utf-8")
    # Default (no --page) output labels each page so a caller merging this
    # text with other per-page text can attribute each block to its source page.
    assert "--- Page 1 ---" in text
    assert "--- Page 2 ---" in text
    assert text.index("--- Page 1 ---") < text.index("--- Page 2 ---")


@pytest.mark.usefixtures("requires_tesseract")
def test_ocr_extract_page_option_ocrs_only_the_requested_page(tmp_path: Path) -> None:
    pdf_path = _build_two_page_pdf(tmp_path, "PAGE ONE AWARD", "PAGE TWO AWARD")
    output_path = tmp_path / "page-two-only.txt"

    subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(pdf_path), "--output", str(output_path), "--page", "2"],
        check=True,
    )

    text = output_path.read_text(encoding="utf-8")
    # --page targets a single page: no page marker, and only that page's text.
    assert "--- Page" not in text
    assert "TWO" in text.upper()
    assert "ONE" not in text.upper()


@pytest.mark.parametrize(
    ("executable", "package"),
    (("tesseract", "tesseract-ocr"), ("soffice", "LibreOffice")),
)
@pytest.mark.parametrize("hosted", (False, True), ids=("local", "hosted"))
def test_missing_native_tools_skip_locally_and_fail_in_hosted_ci(
    monkeypatch: pytest.MonkeyPatch,
    native_tool_gate,
    executable: str,
    package: str,
    hosted: bool,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: None)
    if hosted:
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        with pytest.raises(pytest.fail.Exception, match="hosted CI must install"):
            native_tool_gate(executable, package)
    else:
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        with pytest.raises(pytest.skip.Exception, match=package):
            native_tool_gate(executable, package)
