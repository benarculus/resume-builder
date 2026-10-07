from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/resume-drafter/scripts/build_docx.py"
FIXTURE = ROOT / "skills/resume-drafter/scripts/fixtures/sample-resume.json"
JOB_REQUIREMENTS_FIXTURE = (
    ROOT / "skills/resume-drafter/scripts/fixtures/sample-job-requirements.json"
)
JOB_REQUIREMENTS_PARSER = ROOT / "skills/resume-drafter/scripts/parse_job_requirements.py"


def load_job_requirements_parser() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "job_requirements_parser", JOB_REQUIREMENTS_PARSER
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_job_requirements(tmp_path: Path, artifact: object) -> Path:
    path = tmp_path / "job-requirements.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


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
    for section in ("Summary", "Experience", "Education", "Skills", "Awards"):
        assert section in text
    # unmetRequirements is present in the fixture payload but must never be
    # rendered into the document; it is disclosed only in the chat/summary step.
    assert "Requirements not addressed" not in text
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for unmet in payload["unmetRequirements"]:
        assert unmet not in text


def test_job_requirements_parser_accepts_shared_fixture() -> None:
    artifact = load_job_requirements_parser().parse_job_requirements(
        JOB_REQUIREMENTS_FIXTURE
    )
    assert artifact["requiredQualifications"][0]["id"] == "RQ-001"


def test_job_requirements_parser_rejects_non_object_root(tmp_path: Path) -> None:
    parser = load_job_requirements_parser()
    path = write_job_requirements(tmp_path, [])

    with pytest.raises(ValueError, match="job requirements must be a JSON object"):
        parser.parse_job_requirements(path)


def test_job_requirements_parser_rejects_missing_or_invalid_source(
    tmp_path: Path,
) -> None:
    parser = load_job_requirements_parser()
    source_variants = (
        ("missing", None),
        ("non-object", "not an object"),
        ("missing-url", {}),
        ("empty-url", {"url": ""}),
    )
    for name, source in source_variants:
        artifact = json.loads(JOB_REQUIREMENTS_FIXTURE.read_text(encoding="utf-8"))
        if name == "missing":
            artifact.pop("source")
        else:
            artifact["source"] = source
        path = write_job_requirements(tmp_path, artifact)

        with pytest.raises(ValueError, match="job requirements must include source.url"):
            parser.parse_job_requirements(path)


@pytest.mark.parametrize(
    "field",
    ("requiredQualifications", "preferredQualifications", "responsibilities"),
)
def test_job_requirements_parser_rejects_non_array_required_fields(
    tmp_path: Path, field: str
) -> None:
    parser = load_job_requirements_parser()
    artifact = json.loads(JOB_REQUIREMENTS_FIXTURE.read_text(encoding="utf-8"))
    artifact[field] = {}

    with pytest.raises(ValueError, match=f"{field} must be an array"):
        parser.parse_job_requirements(write_job_requirements(tmp_path, artifact))


@pytest.mark.parametrize(
    ("item", "case"),
    (
        ("not an object", "items require id, text, and source"),
        ({"text": "Qualification", "source": "posting#qualification"}, "items require id, text, and source"),
        ({"id": "RQ-999", "source": "posting#qualification"}, "items require id, text, and source"),
        ({"id": "RQ-999", "text": "Qualification"}, "items require id, text, and source"),
    ),
    ids=("non-object", "missing-id", "missing-text", "missing-source"),
)
def test_job_requirements_parser_rejects_invalid_items(
    tmp_path: Path, item: object, case: str
) -> None:
    parser = load_job_requirements_parser()
    artifact = json.loads(JOB_REQUIREMENTS_FIXTURE.read_text(encoding="utf-8"))
    artifact["requiredQualifications"] = [item]

    with pytest.raises(ValueError, match=case):
        parser.parse_job_requirements(write_job_requirements(tmp_path, artifact))


@pytest.mark.parametrize(
    "constraints",
    (None, []),
    ids=("missing", "non-object"),
)
def test_job_requirements_parser_rejects_missing_or_invalid_constraints(
    tmp_path: Path, constraints: object
) -> None:
    parser = load_job_requirements_parser()
    artifact = json.loads(JOB_REQUIREMENTS_FIXTURE.read_text(encoding="utf-8"))
    if constraints is None:
        artifact.pop("constraints")
    else:
        artifact["constraints"] = constraints

    with pytest.raises(ValueError, match="constraints must be an object"):
        parser.parse_job_requirements(write_job_requirements(tmp_path, artifact))


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


@pytest.mark.parametrize(
    ("payload", "message"),
    (
        ([], "resume input must be a JSON object"),
        ({}, "resume input must include a basics object"),
        ({"basics": []}, "resume input must include a basics object"),
        ({"basics": {}, "experience": {}}, "resume experience must be a list"),
        ({"basics": {}, "education": {}}, "resume education must be a list"),
        (
            {"basics": {}, "education": ["not an education object"]},
            "education entry 0 must be an object",
        ),
    ),
    ids=("root-array", "missing-basics", "basics-array", "experience-object",
         "education-object", "education-entry-string"),
)
def test_load_payload_rejects_invalid_shapes(
    tmp_path: Path, payload: object, message: str
) -> None:
    path = tmp_path / "invalid-shape.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError) as caught:
        load_renderer().load_payload(path)

    assert str(caught.value) == message


def test_build_docx_rejects_unapproved_experience_order() -> None:
    with pytest.raises(ValueError) as caught:
        load_renderer().build_document(
            {
                "basics": {"name": "Jordan Example"},
                "experienceOrder": "oldestFirst",
                "experience": [{"title": "Analyst", "company": "Example Co"}],
            }
        )

    assert str(caught.value) == "experienceOrder must be 'reverseChronological' or 'approved'"


def test_build_docx_excludes_actual_unmet_ids_and_content_from_saved_document(
    tmp_path: Path,
) -> None:
    unmet_requirements = ["RQ-UNMET-901", "Unsupported cloud certification requirement"]
    document = load_renderer().build_document(
        {
            "basics": {"name": "Jordan Example"},
            "summary": "Verified career summary",
            "experience": [{"title": "Analyst", "company": "Example Co"}],
            "unmetRequirements": unmet_requirements,
        }
    )
    output = tmp_path / "unmet-exclusion.docx"
    document.save(output)
    saved = Document(output)
    text = "\n".join(paragraph.text for paragraph in saved.paragraphs)

    assert "Verified career summary" in text
    assert "Analyst — Example Co" in text
    assert "Requirements not addressed" not in text
    for unmet in unmet_requirements:
        assert unmet not in text
