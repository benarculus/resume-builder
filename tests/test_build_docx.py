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
