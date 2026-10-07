from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/resume-drafter/scripts/validate_resume_length.py"
BUILD_SCRIPT = ROOT / "skills/resume-drafter/scripts/build_docx.py"
WITHIN_BUDGET_FIXTURE = ROOT / "skills/resume-drafter/scripts/fixtures/sample-resume.json"
OVER_BUDGET_FIXTURE = ROOT / "skills/resume-drafter/scripts/fixtures/sample-resume-over-budget.json"

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


@pytest.mark.usefixtures("requires_soffice")
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


@pytest.mark.usefixtures("requires_soffice")
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


def test_main_returns_nonzero_when_only_the_page_cap_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`main()`'s exit status must reflect a page-cap-only failure, not just
    the word-budget check, so a regression where `main()` ignores
    `withinPageCap` would not leave every test green."""
    validator = load_validator()
    monkeypatch.setattr(validator, "count_rendered_pages", lambda docx_path: 3)

    fake_docx = tmp_path / "within-budget.docx"
    fake_docx.touch()
    monkeypatch.setattr(
        sys, "argv", [str(SCRIPT), "--docx", str(fake_docx), "--payload", str(WITHIN_BUDGET_FIXTURE)]
    )

    exit_code = validator.main()

    assert exit_code != 0


def assert_main_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    word_count: int,
    page_count: int,
    within_word_budget: bool,
    within_page_cap: bool,
) -> None:
    validator = load_validator()
    payload_path = tmp_path / "boundary.json"
    payload_path.write_text(
        json.dumps({"basics": {"name": "Excluded Name"}, "summary": " ".join(["word"] * word_count)}),
        encoding="utf-8",
    )
    docx_path = tmp_path / "boundary.docx"
    docx_path.touch()

    def rendered_pages(actual_path: Path) -> int:
        assert actual_path == docx_path
        return page_count

    monkeypatch.setattr(validator, "count_rendered_pages", rendered_pages)
    monkeypatch.setattr(
        sys, "argv", [str(SCRIPT), "--docx", str(docx_path), "--payload", str(payload_path)]
    )

    assert validator.main() == (0 if within_word_budget and within_page_cap else 1)
    captured = capsys.readouterr()
    assert captured.err == ""
    report = json.loads(captured.out)
    assert report == {
        "wordCount": word_count,
        "wordBudget": {"min": 475, "max": 600},
        "pageCount": page_count,
        "pageCap": 2,
        "withinWordBudget": within_word_budget,
        "withinPageCap": within_page_cap,
    }
    assert type(report) is dict
    assert type(report["wordBudget"]) is dict
    for field in ("wordCount", "pageCount", "pageCap"):
        assert type(report[field]) is int
    for bound in ("min", "max"):
        assert type(report["wordBudget"][bound]) is int
    for field in ("withinWordBudget", "withinPageCap"):
        assert type(report[field]) is bool


@pytest.mark.parametrize(
    ("word_count", "within_word_budget"),
    ((474, False), (475, True), (600, True), (601, False)),
)
def test_main_enforces_exact_word_boundaries_and_reports_full_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    word_count: int,
    within_word_budget: bool,
) -> None:
    assert_main_report(
        tmp_path, monkeypatch, capsys,
        word_count=word_count, page_count=2,
        within_word_budget=within_word_budget, within_page_cap=True,
    )


@pytest.mark.parametrize(
    ("page_count", "within_page_cap"), ((1, True), (2, True), (3, False))
)
def test_main_enforces_page_boundaries_independently_of_word_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    page_count: int,
    within_page_cap: bool,
) -> None:
    assert_main_report(
        tmp_path, monkeypatch, capsys,
        word_count=500, page_count=page_count,
        within_word_budget=True, within_page_cap=within_page_cap,
    )


@pytest.mark.parametrize("command_fails", (True, False), ids=("subprocess-failure", "missing-pdf"))
def test_conversion_rejects_failed_command_or_missing_pdf(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command_fails: bool
) -> None:
    validator = load_validator()
    docx_path = tmp_path / "resume.docx"
    docx_path.touch()
    output_dir = tmp_path / "converted"
    calls = []
    failure = subprocess.CalledProcessError(7, ["soffice"])

    def run_conversion(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
        calls.append(command)
        assert command == [
            "soffice", "--headless", "--norestore",
            f"-env:UserInstallation={(output_dir / 'lo-profile').as_uri()}",
            "--convert-to", "pdf", "--outdir", str(output_dir), str(docx_path),
        ]
        assert kwargs == {
            "check": True, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL
        }
        if command_fails:
            raise failure
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(validator.subprocess, "run", run_conversion)
    if command_fails:
        with pytest.raises(subprocess.CalledProcessError) as caught:
            validator.convert_docx_to_pdf(docx_path, output_dir)
        assert caught.value is failure
        assert caught.value.returncode == 7
    else:
        with pytest.raises(RuntimeError) as caught:
            validator.convert_docx_to_pdf(docx_path, output_dir)
        assert str(caught.value) == (
            f"expected converted PDF at {output_dir / 'resume.pdf'}, but it was not created"
        )
    assert len(calls) == 1
    assert (output_dir / "lo-profile").is_dir()
    assert not (output_dir / "resume.pdf").exists()


def load_renderer_for_parity() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_docx_parity", BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("body", "expected_paragraphs", "expected_words"),
    (
        (
            {
                "summary": "Verified delivery — measurable impact",
                "experience": [
                    {
                        "title": "Project Lead", "company": "Example Co",
                        "dates": "2021–2024", "startDate": "1990", "endDate": "1991",
                        "bullets": ["Delivered verified outcomes"],
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science", "major": "Computer Science",
                        "abbreviation": "BSCS", "institution": "Example University",
                        "completionDate": "2024-05", "endDate": "1991",
                        "studyType": "Unrendered Credential", "area": "Unrendered Major",
                        "organization": "Unrendered Provider",
                    }
                ],
            },
            [
                "Verified delivery — measurable impact",
                "Project Lead — Example Co 2021–2024",
                "Delivered verified outcomes",
                "Bachelor of Science in Computer Science (BSCS) — Example University — 2024-05",
            ],
            22,
        ),
        (
            {
                "experience": [
                    {"title": "Lead", "startDate": "2022-01", "endDate": "2024-06"},
                    {"title": "Analyst", "startDate": "2020-01"},
                    {"title": "Consultant", "endDate": "2019-06"},
                    {"title": "Undated Role"},
                ],
                "education": [
                    {
                        "studyType": "Advanced Certificate", "area": "Technical Writing",
                        "organization": "Training Provider", "endDate": "2024-05",
                    },
                    {
                        "degree": "Diploma", "institution": "Older School",
                        "date": "2020-05",
                    },
                    {
                        "degree": "Certificate", "organization": "Early Provider",
                        "dates": "2018–2019",
                    },
                ],
            },
            [
                "Lead 2022-01–2024-06", "Analyst 2020-01", "Consultant 2019-06",
                "Undated Role",
                "Advanced Certificate in Technical Writing — Training Provider — 2024-05",
                "Diploma — Older School — 2020-05",
                "Certificate — Early Provider — 2018–2019",
            ],
            24,
        ),
        (
            {
                "skills": ["Python", "Technical writing", "C++", "分析", "—"],
                "awards": [
                    {
                        "title": "Hidden Award Title", "details": "Verified impact citation",
                        "date": "2024-05",
                    },
                    {"title": "Fallback Award", "date": "2023-05"},
                    {"title": "Empty Details Fallback", "details": "", "date": "2022-05"},
                ],
            },
            [
                "Python, Technical writing, C++, 分析, —",
                "Verified impact citation", "Fallback Award", "Empty Details Fallback",
            ],
            13,
        ),
    ),
    ids=("explicit-dates-full-education", "date-and-education-aliases", "awards-skills-separators"),
)
def test_count_words_matches_independent_rendered_body(
    body: dict[str, object], expected_paragraphs: list[str], expected_words: int
) -> None:
    payload = {
        "basics": {
            "name": "Excluded Candidate Name", "email": "excluded@example.com",
            "location": "Excluded City", "securityClearance": "Excluded Clearance",
        },
        "unmetRequirements": ["RQ-UNMET-901", "Unsupported requirement content"],
        **body,
    }
    document = load_renderer_for_parity().build_document(payload)
    paragraphs = document.paragraphs
    assert [paragraph.text for paragraph in paragraphs[:2]] == [
        "Excluded Candidate Name",
        "excluded@example.com | Excluded City | Excluded Clearance",
    ]
    # Skip identity/contact paragraphs and section headings, not arbitrary body text.
    rendered_body = [
        paragraph.text for paragraph in paragraphs[2:]
        if not paragraph.style.name.startswith("Heading")
    ]
    assert rendered_body == expected_paragraphs
    tokens = re.findall(r"\S+", "\n".join(rendered_body))
    independent_count = sum(bool(re.search(r"[^\W_]", token)) for token in tokens)
    assert independent_count == expected_words
    assert load_validator().count_words(payload) == independent_count
    all_text = "\n".join(paragraph.text for paragraph in paragraphs)
    for unmet in payload["unmetRequirements"]:
        assert unmet not in all_text
