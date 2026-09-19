#!/usr/bin/env python3
"""Run structural checks for the resume-builder repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
PLUGIN = ROOT / "plugin.json"
MANIFEST = ROOT / ".github" / "plugin" / "marketplace.json"
JOB_FIXTURE = ROOT / "skills" / "resume-drafter" / "scripts" / "fixtures" / "sample-job-requirements.json"
WORKFLOWS = (ROOT / ".github" / "workflows" / "ci.yml", ROOT / ".github" / "workflows" / "codeql-analysis.yml")
REQUIREMENTS = (ROOT / "requirements.txt", ROOT / "requirements-dev.txt")
EXPECTED_SKILLS = {
    "career-document-builder",
    "job-requirements-planner",
    "resume-drafter",
}
SHA_PINNED_ACTION = re.compile(r"uses:\s+[\w.-]+/[\w./-]+@[0-9a-f]{40}\s+#\s+v\d+\b")
REQUIREMENT_PIN = re.compile(r"^[A-Za-z0-9_.-]+==[^<>=!~\s]+$")


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


def validate_skills() -> list[Path]:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if {path.parent.name for path in skill_files} != EXPECTED_SKILLS:
        raise AssertionError("expected exactly the three bundled root skills")
    for path in skill_files:
        frontmatter(path)
    return skill_files


def validate_plugin_manifest() -> dict:
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    required = {
        "$schema",
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
    }
    if not required <= plugin.keys():
        raise AssertionError("plugin manifest is missing required fields")
    if plugin["$schema"] != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        raise AssertionError("plugin manifest must use the Agent Plugins 1.0 schema")
    if plugin["name"] != "resume-builder":
        raise AssertionError("plugin manifest name must be resume-builder")
    if not isinstance(plugin["author"], dict) or not {"name", "url"} <= plugin["author"].keys():
        raise AssertionError("plugin manifest author is incomplete")
    return plugin


def validate_marketplace_manifest(plugin_manifest: dict) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    required = {"name", "metadata", "owner", "plugins"}
    if not required <= manifest.keys() or not manifest["plugins"]:
        raise AssertionError("marketplace manifest is missing required fields")
    plugin = manifest["plugins"][0]
    if not {"name", "source", "description", "version", "author", "license", "keywords"} <= plugin.keys():
        raise AssertionError("marketplace plugin entry is incomplete")
    source = (ROOT / plugin["source"]).resolve()
    if not (source / "plugin.json").is_file():
        raise AssertionError("marketplace plugin source must contain plugin.json")
    if plugin["name"] != plugin_manifest["name"] or plugin["version"] != plugin_manifest["version"]:
        raise AssertionError("marketplace plugin metadata must match plugin.json")


def validate_workflow_pins() -> None:
    for workflow in WORKFLOWS:
        for line in workflow.read_text(encoding="utf-8").splitlines():
            if "uses:" not in line:
                continue
            if not SHA_PINNED_ACTION.search(line):
                raise AssertionError(f"{workflow}: workflow action must be pinned to a full SHA with version comment: {line.strip()}")


def validate_requirement_pins() -> None:
    for requirements in REQUIREMENTS:
        for line in requirements.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-r "):
                continue
            if not REQUIREMENT_PIN.match(stripped):
                raise AssertionError(f"{requirements}: direct dependency must use an exact == pin: {stripped}")


def validate_job_requirements_contract() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    parser_path = SKILLS / "resume-drafter" / "scripts" / "parse_job_requirements.py"
    spec = spec_from_file_location("parse_job_requirements", parser_path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load job requirements parser")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.parse_job_requirements(JOB_FIXTURE)


def main() -> int:
    skill_files = validate_skills()
    plugin_manifest = validate_plugin_manifest()
    validate_marketplace_manifest(plugin_manifest)
    validate_workflow_pins()
    validate_requirement_pins()
    validate_job_requirements_contract()
    print(
        f"Validated {len(skill_files)} skills, plugin and marketplace JSON, "
        "workflow SHA pins, exact dependency pins, and job-requirements round-trip."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, yaml.YAMLError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
