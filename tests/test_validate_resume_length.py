from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/resume-drafter/scripts/validate_resume_length.py"
BUILD_SCRIPT = ROOT / "skills/resume-drafter/scripts/build_docx.py"
WITHIN_BUDGET_FIXTURE = ROOT / "skills/resume-drafter/scripts/fixtures/sample-resume.json"
OVER_BUDGET_FIXTURE = ROOT / "skills/resume-drafter/scripts/fixtures/sample-resume-over-budget.json"

requires_soffice = pytest.mark.skipif(
    shutil.which("soffice") is None,
    reason="LibreOffice (soffice) system binary is not installed in this environment",
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_resume_length", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_count_words_uses_only_body_fields_and_excludes_contact_metadata() -> None:
    validator = load_validator()
    payload = {
        "basics": {"name": "Name With Many Words", "email": "name@example.com", "location": "City, Region"},
        "summary": "one two three",
        "experience": [{"title": "Role", "company": "Co", "bullets": ["four five six seven"]}],
        "education": [{"degree": "Degree", "institution": "School"}],
        "skills": ["eight", "nine"],
        "awards": [{"title": "Award", "details": "ten eleven"}],
        "unmetRequirements": ["twelve thirteen fourteen should not be counted"],
    }

    # "Award" (the award's `title`) is never rendered by build_docx.py, which
    # renders only `details` when present, so it must not be counted.
    assert validator.count_words(payload) == 15


def test_count_words_excludes_award_title_when_details_is_rendered() -> None:
    validator = load_validator()
    payload = {
        "basics": {"name": "Name"},
        "awards": [{"title": "unrendered title words here", "details": "one"}],
    }

    assert validator.count_words(payload) == 1


def test_within_budget_fixture_reports_pass_by_contract() -> None:
    validator = load_validator()
    payload = json.loads(WITHIN_BUDGET_FIXTURE.read_text(encoding="utf-8"))
    word_count = validator.count_words(payload)

    assert validator.WORD_BUDGET_MIN <= word_count <= validator.WORD_BUDGET_MAX


def test_over_budget_fixture_exceeds_the_word_budget() -> None:
    validator = load_validator()
    payload = json.loads(OVER_BUDGET_FIXTURE.read_text(encoding="utf-8"))
    word_count = validator.count_words(payload)

    assert word_count > validator.WORD_BUDGET_MAX


@requires_soffice
def test_validate_length_script_reports_contract_for_within_budget_resume(tmp_path: Path) -> None:
    docx_path = tmp_path / "within-budget.docx"
    subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--input", str(WITHIN_BUDGET_FIXTURE), "--output", str(docx_path)],
        check=True,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--docx", str(docx_path), "--payload", str(WITHIN_BUDGET_FIXTURE)],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)

    assert set(report) == {"wordCount", "wordBudget", "pageCount", "pageCap", "withinWordBudget", "withinPageCap"}
    assert report["withinWordBudget"] is True
    assert report["withinPageCap"] is True


@requires_soffice
def test_validate_length_script_flags_an_over_budget_resume(tmp_path: Path) -> None:
    docx_path = tmp_path / "over-budget.docx"
    subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--input", str(OVER_BUDGET_FIXTURE), "--output", str(docx_path)],
        check=True,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--docx", str(docx_path), "--payload", str(OVER_BUDGET_FIXTURE)],
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)

    assert report["withinWordBudget"] is False
    assert result.returncode != 0


def test_validate_length_flags_an_over_page_cap_resume_even_when_within_word_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A within-budget payload with a page count over PAGE_CAP must fail
    `withinPageCap` (and the overall exit code) even though `withinWordBudget`
    is true, so a silently-always-true `withinPageCap` would be caught."""
    validator = load_validator()
    monkeypatch.setattr(validator, "count_rendered_pages", lambda docx_path: 3)

    fake_docx = tmp_path / "within-budget.docx"
    fake_docx.touch()

    result = validator.validate_length(fake_docx, WITHIN_BUDGET_FIXTURE)

    assert result["withinWordBudget"] is True
    assert result["pageCount"] == 3
    assert result["withinPageCap"] is False
