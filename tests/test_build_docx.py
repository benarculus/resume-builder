from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/resume-drafter/scripts/build_docx.py"
FIXTURE = ROOT / "skills/resume-drafter/scripts/fixtures/sample-resume.json"


def test_build_docx_creates_expected_sections(tmp_path: Path) -> None:
    output = tmp_path / "resume.docx"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(FIXTURE), "--output", str(output)],
        check=True,
    )
    assert output.exists()
    assert output.stat().st_size > 0
    document = Document(output)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    for section in ("Summary", "Experience", "Education", "Skills", "Awards", "Requirements not addressed"):
        assert section in text


def test_job_requirements_parser_accepts_shared_fixture() -> None:
    parser_path = ROOT / "skills/resume-drafter/scripts/parse_job_requirements.py"
    spec = importlib.util.spec_from_file_location("job_requirements_parser", parser_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    artifact = module.parse_job_requirements(
        ROOT / "skills/resume-drafter/scripts/fixtures/sample-job-requirements.json"
    )
    assert artifact["requiredQualifications"][0]["id"] == "RQ-001"


def load_renderer():
    spec = importlib.util.spec_from_file_location("build_docx", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_docx_applies_resume_top_matter_formatting_and_order() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {
                "name": "Jordan Example",
                "email": "jordan@example.com",
                "location": {"city": "Austin", "region": "TX"},
                "securityClearance": "Active Secret",
            },
            "experience": [],
        }
    )

    assert [paragraph.text for paragraph in document.paragraphs[:2]] == [
        "Jordan Example",
        "jordan@example.com | Austin, TX | Active Secret",
    ]
    assert document.paragraphs[0].alignment == 0
    assert document.paragraphs[1].alignment == 0
    assert document.sections[0].top_margin.inches == 0.5
    assert document.sections[0].bottom_margin.inches == 0.5
    assert document.sections[0].left_margin.inches == 0.5
    assert document.sections[0].right_margin.inches == 0.5
    assert document.paragraphs[0].runs[0].font.size.pt == 20
    assert document.styles["Normal"].font.size.pt == 11


def test_build_docx_omits_unapproved_clearance_from_top_matter() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {
                "name": "Jordan Example",
                "email": "jordan@example.com",
                "location": {"city": "Austin", "region": "TX"},
            },
            "experience": [],
        }
    )

    assert document.paragraphs[1].text == "jordan@example.com | Austin, TX"
    assert "Clearance" not in document.paragraphs[1].text


def test_build_docx_sorts_experience_and_renders_complete_education() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {"name": "Jordan Example"},
            "experience": [
                {"company": "Older Co", "title": "Analyst", "dates": "2018-2020"},
                {"company": "Current Co", "title": "Manager", "dates": "2022-2024"},
            ],
            "education": [
                {
                    "institution": "Example University",
                    "degree": "Bachelor of Science",
                    "major": "Computer Science",
                    "abbreviation": "BSCS",
                    "completionDate": "2024-05",
                }
            ],
        }
    )

    text = [paragraph.text for paragraph in document.paragraphs]
    assert text.index("Manager — Current Co 2022-2024") < text.index(
        "Analyst — Older Co 2018-2020"
    )
    assert (
        "Bachelor of Science in Computer Science (BSCS) — Example University — 2024-05"
        in text
    )


def test_build_docx_renders_start_and_end_dates_when_dates_field_is_absent() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {"name": "Jordan Example"},
            "experience": [
                {
                    "company": "Current Co",
                    "title": "Manager",
                    "startDate": "2022-01",
                    "endDate": "2024-06",
                }
            ],
        }
    )

    assert "Manager — Current Co 2022-01–2024-06" in [
        paragraph.text for paragraph in document.paragraphs
    ]


def test_build_docx_preserves_missing_role_end_date_and_sorts_by_recency() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {"name": "Jordan Example"},
            "experience": [
                {
                    "company": "Older Co",
                    "title": "Analyst",
                    "startDate": "2018-01",
                },
                {
                    "company": "Current Co",
                    "title": "Manager",
                    "dates": "2018-01–Present",
                },
                {
                    "company": "Recent Co",
                    "title": "Lead",
                    "startDate": "2023-01",
                    "endDate": "2024-06",
                },
            ],
        }
    )

    text = [paragraph.text for paragraph in document.paragraphs]
    assert text.index("Manager — Current Co 2018-01–Present") < text.index(
        "Lead — Recent Co 2023-01–2024-06"
    )
    assert "Analyst — Older Co 2018-01" in text


def test_build_docx_sorts_year_range_and_awards_by_effective_date() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {"name": "Jordan Example"},
            "experience": [
                {"company": "Later Co", "title": "Lead", "dates": "2020-2024"},
                {"company": "Older Co", "title": "Analyst", "dates": "2019-2025"},
            ],
            "awards": [
                {"title": "Older Award", "date": "2020-05"},
                {"title": "Recent Award", "date": "2024-05"},
            ],
        }
    )

    text = [paragraph.text for paragraph in document.paragraphs]
    assert text.index("Analyst — Older Co 2019-2025") < text.index(
        "Lead — Later Co 2020-2024"
    )
    assert text.index("Recent Award") < text.index("Older Award")


def test_load_payload_rejects_abbreviation_only_education(tmp_path: Path) -> None:
    renderer = load_renderer()
    payload = tmp_path / "invalid-resume.json"
    payload.write_text(
        '{"basics": {"name": "Jordan Example"}, '
        '"education": [{"institution": "Example University", "abbreviation": "BSCS"}]}',
        encoding="utf-8",
    )

    try:
        renderer.load_payload(payload)
    except ValueError as error:
        assert "full degree or credential" in str(error)
    else:
        raise AssertionError("abbreviation-only education should be rejected")


def test_load_payload_rejects_incomplete_education_fields(tmp_path: Path) -> None:
    renderer = load_renderer()
    cases = (
        '{"institution": "Example University", "degree": "Bachelor of Science"}',
        '{"degree": "Bachelor of Science", "completionDate": "2024-05"}',
        '{"institution": "Example University", "completionDate": "2024-05"}',
    )
    for education in cases:
        payload = tmp_path / "invalid-resume.json"
        payload.write_text(
            f'{{"basics": {{"name": "Jordan Example"}}, "education": [{education}]}}',
            encoding="utf-8",
        )
        try:
            renderer.load_payload(payload)
        except ValueError:
            continue
        raise AssertionError("incomplete education should be rejected")


def test_load_payload_rejects_non_object_experience_entries(tmp_path: Path) -> None:
    renderer = load_renderer()
    payload = tmp_path / "invalid-resume.json"
    payload.write_text(
        '{"basics": {"name": "Jordan Example"}, "experience": ["not a role"]}',
        encoding="utf-8",
    )

    try:
        renderer.load_payload(payload)
    except ValueError as error:
        assert "experience entry 0 must be an object" in str(error)
    else:
        raise AssertionError("non-object experience entries should be rejected")


def test_build_docx_accepts_and_sorts_standard_education_end_date_fields(
    tmp_path: Path,
) -> None:
    renderer = load_renderer()
    payload_path = tmp_path / "standard-resume.json"
    payload_path.write_text(
        '{"basics": {"name": "Jordan Example"}, "education": ['
        '{"institution": "Older University", "studyType": "Certificate", '
        '"area": "Writing", "endDate": "2020-05"},'
        '{"institution": "Example University", "studyType": "Bachelor of Science", '
        '"area": "Computer Science", "endDate": "2024-05"}]}',
        encoding="utf-8",
    )
    document = renderer.build_document(renderer.load_payload(payload_path))

    text = [paragraph.text for paragraph in document.paragraphs]
    assert text.index(
        "Bachelor of Science in Computer Science — Example University — 2024-05"
    ) < text.index(
        "Certificate in Writing — Older University — 2020-05"
    )


def test_build_docx_preserves_user_approved_experience_order() -> None:
    renderer = load_renderer()
    document = renderer.build_document(
        {
            "basics": {"name": "Jordan Example"},
            "experienceOrder": "approved",
            "experience": [
                {"company": "Older Co", "title": "Analyst", "dates": "2018-2020"},
                {"company": "Current Co", "title": "Manager", "dates": "2022-2024"},
            ],
        }
    )

    text = [paragraph.text for paragraph in document.paragraphs]
    assert text.index("Analyst — Older Co 2018-2020") < text.index(
        "Manager — Current Co 2022-2024"
    )
