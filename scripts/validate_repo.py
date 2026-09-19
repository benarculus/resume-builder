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
WORKFLOWS = tuple(sorted((ROOT / ".github" / "workflows").glob("*.yml")))
REQUIREMENTS = (ROOT / "requirements.txt", ROOT / "requirements-dev.txt")
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
DEPENDENCY_REVIEW_WORKFLOW = ROOT / ".github" / "workflows" / "dependency-review.yml"
MALWARE_WORKFLOW = ROOT / ".github" / "workflows" / "advisory-malware.yml"
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


def validate_dependabot_policy() -> None:
    config = yaml.safe_load(DEPENDABOT.read_text(encoding="utf-8"))
    updates = {
        update["package-ecosystem"]: update
        for update in config["updates"]
        if isinstance(update, dict) and "package-ecosystem" in update
    }
    pip = updates.get("pip")
    actions = updates.get("github-actions")
    if pip is None or actions is None:
        raise AssertionError("Dependabot must configure pip and github-actions updates")
    if pip.get("schedule", {}).get("interval") != "weekly":
        raise AssertionError("pip Dependabot updates must remain weekly")
    if "target-branch" in pip or "target-branch" in actions:
        raise AssertionError("Dependabot updates must use the default branch")

    expected_cooldown = {
        "default-days": 14,
        "semver-patch-days": 14,
        "semver-minor-days": 14,
        "semver-major-days": 30,
    }
    if pip.get("cooldown") != expected_cooldown:
        raise AssertionError("pip Dependabot cooldown must match the approved release-age policy")

    for ecosystem, update in updates.items():
        groups = update.get("groups", {})
        expected = {
            f"{ecosystem}-version-updates": "version-updates",
            f"{ecosystem}-security-updates": "security-updates",
        }
        for name, applies_to in expected.items():
            group = groups.get(name)
            if group != {"applies-to": applies_to, "patterns": ["*"]}:
                raise AssertionError(f"{ecosystem} Dependabot group {name} must match the approved policy")


def validate_dependency_check_workflows() -> None:
    review = yaml.load(DEPENDENCY_REVIEW_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    malware = yaml.load(MALWARE_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    for name, workflow in (("dependency review", review), ("malware advisory", malware)):
        if not isinstance(workflow, dict) or "pull_request" not in workflow.get("on", {}):
            raise AssertionError(f"{name} workflow must run on pull_request")
        if workflow.get("permissions") != {"contents": "read"}:
            raise AssertionError(f"{name} workflow must use contents: read permissions")
        if any(isinstance(job, dict) and "permissions" in job for job in workflow.get("jobs", {}).values()):
            raise AssertionError(f"{name} workflow must not override permissions at job scope")

    review_steps = review["jobs"]["dependency-review"]["steps"]
    review_action = next(
        (step for step in review_steps if step.get("uses", "").startswith("actions/dependency-review-action@")),
        None,
    )
    if not isinstance(review_action, dict) or review_action.get("with") != {
        "fail-on-severity": "low",
        "fail-on-scopes": "runtime,development,unknown",
    }:
        raise AssertionError("dependency review workflow must enforce the approved action policy")

    malware_steps = malware["jobs"]["advisory-malware"]["steps"]
    checkout = next(
        (step for step in malware_steps if step.get("uses", "").startswith("actions/checkout@")),
        None,
    )
    command = next((step.get("run") for step in malware_steps if isinstance(step, dict) and "run" in step), "")
    if not isinstance(checkout, dict) or checkout.get("with", {}).get("persist-credentials") != "false":
        raise AssertionError("malware advisory checkout must not persist credentials")
    if not isinstance(command, str) or not all(
        fragment in command
        for fragment in ("scripts/check_malware_advisories.py", "--base-ref", "--head-ref")
    ):
        raise AssertionError("malware advisory workflow must run the repository-owned checker")
    if "GITHUB_TOKEN" in MALWARE_WORKFLOW.read_text(encoding="utf-8"):
        raise AssertionError("malware advisory workflow must not expose GITHUB_TOKEN")


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
    validate_dependabot_policy()
    validate_dependency_check_workflows()
    validate_job_requirements_contract()
    print(
        f"Validated {len(skill_files)} skills, plugin and marketplace JSON, "
        "workflow SHA pins, Dependabot policy, dependency gates, exact dependency pins, "
        "and job-requirements round-trip."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, yaml.YAMLError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
