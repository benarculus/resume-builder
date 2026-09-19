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
WORKFLOWS = tuple(
    sorted(
        path
        for pattern in ("*.yml", "*.yaml")
        for path in (ROOT / ".github" / "workflows").glob(pattern)
    )
)
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
WORKFLOW_TOKEN_REFERENCE = re.compile(
    r"(?:github\s*\.\s*token|github\s*\[\s*['\"]token['\"]\s*\]|secrets(?:\s*\.|\s*\[)|tojson\s*\(\s*(?:secrets|github)\s*\))",
    re.IGNORECASE,
)


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
    if not isinstance(config, dict) or config.get("version") != 2:
        raise AssertionError("Dependabot configuration must use schema version 2")
    if not isinstance(config.get("updates"), list):
        raise AssertionError("Dependabot configuration must define update entries")
    ecosystems = [
        update.get("package-ecosystem")
        for update in config["updates"]
        if isinstance(update, dict)
    ]
    if len(ecosystems) != len(set(ecosystems)):
        raise AssertionError("Dependabot configuration must not duplicate package ecosystems")
    updates = {
        update["package-ecosystem"]: update
        for update in config["updates"]
        if isinstance(update, dict) and "package-ecosystem" in update
    }
    pip = updates.get("pip")
    actions = updates.get("github-actions")
    if pip is None or actions is None:
        raise AssertionError("Dependabot must configure pip and github-actions updates")
    for ecosystem, update in (("pip", pip), ("github-actions", actions)):
        if update.get("schedule", {}).get("interval") != "weekly":
            raise AssertionError(f"{ecosystem} Dependabot updates must remain weekly")
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
        triggers = workflow.get("on", {}) if isinstance(workflow, dict) else {}
        if triggers.get("pull_request") != "" or "pull_request_target" in triggers:
            raise AssertionError(f"{name} workflow must run on pull_request")
        if workflow.get("permissions") != {"contents": "read"}:
            raise AssertionError(f"{name} workflow must use contents: read permissions")
        for job in workflow.get("jobs", {}).values():
            if not isinstance(job, dict):
                continue
            if "permissions" in job:
                raise AssertionError(f"{name} workflow must not override permissions at job scope")
            if "if" in job:
                raise AssertionError(f"{name} workflow job must not be conditional")
            if job.get("continue-on-error") not in (None, "false"):
                raise AssertionError(f"{name} workflow job must not continue on error")

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
    if review_action.get("continue-on-error") not in (None, "false"):
        raise AssertionError("dependency review action must not continue on error")
    if "if" in review_action:
        raise AssertionError("dependency review action must not be conditional")

    malware_steps = malware["jobs"]["advisory-malware"]["steps"]
    checkouts = [
        step
        for step in malware_steps
        if isinstance(step, dict) and step.get("uses", "").startswith("actions/checkout@")
    ]
    command = next(
        (step.get("run") for step in malware_steps if isinstance(step, dict) and "run" in step),
        "",
    )
    if not checkouts or any(
        checkout.get("with", {}).get("persist-credentials") != "false"
        for checkout in checkouts
    ):
        raise AssertionError("malware advisory checkouts must not persist credentials")
    expected_command = (
        'CHECKER_REF="${{ github.event.pull_request.base.sha }}" '
        '&& if ! git cat-file -e "$CHECKER_REF:scripts/check_malware_advisories.py"; '
        'then CHECKER_REF="f907faf8ad98c56629b9ee9d7265f4f288de7da7"; fi '
        '&& git show "$CHECKER_REF:scripts/check_malware_advisories.py" '
        '> "$RUNNER_TEMP/check_malware_advisories.py" '
        '&& python "$RUNNER_TEMP/check_malware_advisories.py" '
        '--base-ref "${{ github.event.pull_request.base.sha }}" '
        '--head-ref "${{ github.event.pull_request.head.sha }}"'
    )
    if not isinstance(command, str) or " ".join(command.split()) != expected_command:
        raise AssertionError("malware advisory workflow must run the repository-owned checker")
    if any(
        isinstance(step, dict) and step.get("continue-on-error") not in (None, "false")
        for step in malware_steps
    ):
        raise AssertionError("malware advisory steps must not continue on error")
    if any(isinstance(step, dict) and "if" in step for step in malware_steps):
        raise AssertionError("malware advisory steps must not be conditional")
    if WORKFLOW_TOKEN_REFERENCE.search(MALWARE_WORKFLOW.read_text(encoding="utf-8")):
        raise AssertionError("malware advisory workflow must not expose workflow tokens")


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
