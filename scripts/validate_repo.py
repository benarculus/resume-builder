#!/usr/bin/env python3
"""Run structural checks for the resume-builder repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".github" / "skills"
MANIFEST = ROOT / ".github" / "plugin" / "marketplace.json"
JOB_FIXTURE = ROOT / ".github" / "skills" / "resume-drafter" / "scripts" / "fixtures" / "sample-job-requirements.json"


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"{path}: missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict) or not data.get("name") or not data.get("description"):
        raise AssertionError(f"{path}: name and description are required")
    if data["name"] != path.parent.name:
        raise AssertionError(f"{path}: name does not match directory")
    return data


def main() -> int:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if {path.parent.name for path in skill_files} != {
        "career-document-builder",
        "job-requirements-planner",
        "resume-drafter",
    }:
        raise AssertionError("expected exactly the three bundled skills")
    for path in skill_files:
        frontmatter(path)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    required = {"name", "metadata", "owner", "plugins"}
    if not required <= manifest.keys() or not manifest["plugins"]:
        raise AssertionError("marketplace manifest is missing required fields")
    plugin = manifest["plugins"][0]
    if not {"name", "source", "description", "version", "author", "license", "keywords"} <= plugin.keys():
        raise AssertionError("marketplace plugin entry is incomplete")

    from importlib.util import module_from_spec, spec_from_file_location

    parser_path = SKILLS / "resume-drafter" / "scripts" / "parse_job_requirements.py"
    spec = spec_from_file_location("parse_job_requirements", parser_path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load job requirements parser")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.parse_job_requirements(JOB_FIXTURE)
    print(f"Validated {len(skill_files)} skills, manifest JSON, and job-requirements round-trip.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, yaml.YAMLError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
