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

def workflow_paths(root: Path) -> tuple[Path, ...]:
    """Return every GitHub Actions workflow, including both supported extensions."""
    return tuple(
        sorted(
            path
            for pattern in ("*.yml", "*.yaml")
            for path in (root / ".github" / "workflows").glob(pattern)
        )
    )


WORKFLOWS = workflow_paths(ROOT)
REQUIREMENTS = (ROOT / "requirements.txt", ROOT / "requirements-dev.txt")
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
DEPENDENCY_REVIEW_WORKFLOW = ROOT / ".github" / "workflows" / "dependency-review.yml"
MALWARE_WORKFLOW = ROOT / ".github" / "workflows" / "advisory-malware.yml"
RELEASE_PLEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release-please.yml"
CREATE_APP_TOKEN_SHA = "bcd2ba49218906704ab6c1aa796996da409d3eb1"
CREATE_APP_TOKEN_VERSION = "v3.2.0"
RELEASE_PLEASE_ACTION_SHA = "45996ed1f6d02564a971a2fa1b5860e934307cf7"
RELEASE_PLEASE_ACTION_VERSION = "v5.0.0"
MALWARE_REUSABLE_OWNER_REPO = "benarculus/malware-advisory-check"
MALWARE_REUSABLE_WORKFLOW = (
    f"{MALWARE_REUSABLE_OWNER_REPO}/.github/workflows/reusable-malware-advisory-check.yml"
)
MALWARE_REUSABLE_SHA = "733acbdf20304f70ac0c9a763921cac4c23882ef"
MALWARE_REUSABLE_VERSION = "v1.0.2"
MALWARE_REUSABLE_USES = f"{MALWARE_REUSABLE_WORKFLOW}@{MALWARE_REUSABLE_SHA}"
EXPECTED_SKILLS = {
    "career-document-builder",
    "job-requirements-planner",
    "resume-drafter",
}
SHA_PINNED_ACTION = re.compile(r"uses:\s+[\w.-]+/[\w./-]+@[0-9a-f]{40}\s+#\s+v\d+(?:\.\d+)*\b")
REQUIREMENT_PIN = re.compile(r"^[A-Za-z0-9_.-]+==[^<>=!~\s]+$")
WORKFLOW_TOKEN_REFERENCE = re.compile(
    r"(?:github\s*\.\s*token|github\s*\[\s*['\"]token['\"]\s*\]|secrets(?:\s*\.|\s*\[)|tojson\s*\(\s*(?:secrets|github)\s*\))",
    re.IGNORECASE,
)
LOCAL_MALWARE_CHECKER_REFERENCES = (
    "check_malware_advisories.py",
    "CHECKER_REF",
    "git cat-file",
    "git show",
    "python scripts/check_malware_advisories.py",
    "$RUNNER_TEMP/check_malware_advisories.py",
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
    if ecosystems.count("pip") != 1 or ecosystems.count("github-actions") != 1:
        raise AssertionError("Dependabot configuration must define one pip and one github-actions entry")
    if set(ecosystems) != {"pip", "github-actions"}:
        raise AssertionError("Dependabot configuration must only configure pip and github-actions")
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
            f"{ecosystem}-version-updates": {"applies-to": "version-updates", "patterns": ["*"]},
            f"{ecosystem}-security-updates": {"applies-to": "security-updates", "patterns": ["*"]},
        }
        if groups != expected:
            raise AssertionError(f"{ecosystem} Dependabot groups must match the approved policy")


def validate_dependency_check_workflows() -> None:
    review = yaml.load(DEPENDENCY_REVIEW_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    malware = yaml.load(MALWARE_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    for name, workflow in (("dependency review", review), ("malware advisory", malware)):
        triggers = workflow.get("on", {}) if isinstance(workflow, dict) else {}
        if triggers.get("pull_request") != "" or "pull_request_target" in triggers:
            raise AssertionError(f"{name} workflow must run on pull_request")
        if workflow.get("permissions") != {"contents": "read"}:
            raise AssertionError(f"{name} workflow must use contents: read permissions")
        if "defaults" in workflow:
            raise AssertionError(f"{name} workflow must not override the default shell")
        for job in workflow.get("jobs", {}).values():
            if not isinstance(job, dict):
                continue
            if "permissions" in job:
                raise AssertionError(f"{name} workflow must not override permissions at job scope")
            if "defaults" in job:
                raise AssertionError(f"{name} workflow job must not override the default shell")
            if "if" in job:
                raise AssertionError(f"{name} workflow job must not be conditional")
            if job.get("continue-on-error") not in (None, "false"):
                raise AssertionError(f"{name} workflow job must not continue on error")
            if job.get("secrets") == "inherit":
                raise AssertionError(f"{name} workflow job must not inherit secrets")

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

    validate_malware_reusable_workflow(malware)


def validate_release_please_workflow() -> None:
    workflow = yaml.load(RELEASE_PLEASE_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(workflow, dict):
        raise AssertionError("release-please workflow must be a mapping")
    if workflow.get("on") != {"push": {"branches": ["main"]}}:
        raise AssertionError("release-please workflow must run only on pushes to main")
    if workflow.get("permissions") != {}:
        raise AssertionError("release-please workflow must disable the default GITHUB_TOKEN permissions")

    jobs = workflow.get("jobs", {})
    if set(jobs) != {"release-please"}:
        raise AssertionError("release-please workflow must keep one release-please job")
    job = jobs["release-please"]
    if job.get("concurrency") != {
        "group": "release-please",
        "cancel-in-progress": "false",
    }:
        raise AssertionError("release-please workflow must serialize mutations without cancelling active runs")

    steps = job.get("steps", [])
    if len(steps) != 2:
        raise AssertionError("release-please workflow must contain only token creation and release steps")
    token_step, release_step = steps
    if token_step.get("id") != "app-token":
        raise AssertionError("release-please workflow must expose the app-token step output")
    if token_step.get("uses") != f"actions/create-github-app-token@{CREATE_APP_TOKEN_SHA}":
        raise AssertionError("GitHub App token action must use the approved pinned release")
    if token_step.get("with") != {
        "client-id": "${{ vars.RELEASE_PLEASE_APP_CLIENT_ID }}",
        "private-key": "${{ secrets.RELEASE_PLEASE_APP_PRIVATE_KEY }}",
        "owner": "${{ github.repository_owner }}",
        "repositories": "${{ github.event.repository.name }}",
        "permission-contents": "write",
        "permission-pull-requests": "write",
        "permission-issues": "write",
    }:
        raise AssertionError("GitHub App token must be scoped to this repository and required permissions")

    if release_step.get("uses") != f"googleapis/release-please-action@{RELEASE_PLEASE_ACTION_SHA}":
        raise AssertionError("release-please action must use the approved pinned release")
    if release_step.get("with") != {
        "token": "${{ steps.app-token.outputs.token }}",
        "config-file": "release-please-config.json",
        "manifest-file": ".release-please-manifest.json",
    }:
        raise AssertionError("release-please must consume only the ephemeral GitHub App token")

    raw_text = RELEASE_PLEASE_WORKFLOW.read_text(encoding="utf-8")
    expected_pins = (
        (CREATE_APP_TOKEN_SHA, CREATE_APP_TOKEN_VERSION),
        (RELEASE_PLEASE_ACTION_SHA, RELEASE_PLEASE_ACTION_VERSION),
    )
    for sha, version in expected_pins:
        if not re.search(rf"@{sha}\s+#\s+{re.escape(version)}\b", raw_text):
            raise AssertionError(f"release-please workflow must document pinned action version {version}")
    forbidden = ("RELEASE_PLEASE_TOKEN", "pull_request_target", "secrets: inherit")
    if any(value in raw_text for value in forbidden):
        raise AssertionError("release-please workflow contains a forbidden broad or long-lived token pattern")


def recursively_find_key(value: object, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(recursively_find_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(recursively_find_key(child, key) for child in value)
    return False


def recursively_find_string(value: object, pattern: re.Pattern[str]) -> bool:
    if isinstance(value, str):
        return bool(pattern.search(value))
    if isinstance(value, dict):
        return any(recursively_find_string(child, pattern) for child in value.values())
    if isinstance(value, list):
        return any(recursively_find_string(child, pattern) for child in value)
    return False


def validate_malware_reusable_workflow(malware: dict) -> None:
    jobs = malware.get("jobs", {}) if isinstance(malware, dict) else {}
    if set(jobs) != {"advisory-malware"}:
        raise AssertionError("malware advisory workflow must keep the advisory-malware job identity")

    job = jobs["advisory-malware"]
    if not isinstance(job, dict):
        raise AssertionError("malware advisory job must be a reusable workflow call")

    raw_text = MALWARE_WORKFLOW.read_text(encoding="utf-8")
    expected_uses_line = (
        f"uses: {MALWARE_REUSABLE_USES} # {MALWARE_REUSABLE_VERSION}"
    )
    if expected_uses_line not in raw_text:
        raise AssertionError(
            "malware advisory reusable workflow must be pinned to the approved v1.0.2 release SHA"
        )
    if job.get("uses") != MALWARE_REUSABLE_USES:
        raise AssertionError("malware advisory workflow must call the approved reusable workflow path")
    if not re.search(rf"@{MALWARE_REUSABLE_SHA}\s+#\s+{re.escape(MALWARE_REUSABLE_VERSION)}", raw_text):
        raise AssertionError("malware advisory workflow must include the v1.0.2 release comment")

    if len(MALWARE_REUSABLE_SHA) != 40 or not re.fullmatch(r"[0-9a-f]{40}", MALWARE_REUSABLE_SHA):
        raise AssertionError("malware advisory reusable workflow release SHA must be exactly 40 hex characters")
    uses_ref = str(job.get("uses", "")).rsplit("@", maxsplit=1)[-1]
    if uses_ref != MALWARE_REUSABLE_SHA or not re.fullmatch(r"[0-9a-f]{40}", uses_ref):
        raise AssertionError("malware advisory reusable workflow must use the exact approved 40-character release SHA")

    if "runs-on" in job or "steps" in job:
        raise AssertionError("malware advisory workflow must not execute the local checker")
    if job.get("with") != {
        "base-ref": "${{ github.event.pull_request.base.sha }}",
        "head-ref": "${{ github.event.pull_request.head.sha }}",
    }:
        raise AssertionError("malware advisory workflow must map explicit PR base/head SHA inputs")
    if job.get("secrets") != {"github-token": "${{ secrets.GITHUB_TOKEN }}"}:
        raise AssertionError("malware advisory workflow must map only the named github-token secret")

    if "if" in job or recursively_find_key(job, "if"):
        raise AssertionError("malware advisory workflow job must not be conditional")
    if job.get("continue-on-error") not in (None, "false") or recursively_find_key(job, "continue-on-error"):
        raise AssertionError("malware advisory workflow must not continue on error")
    if job.get("secrets") == "inherit" or "secrets: inherit" in raw_text:
        raise AssertionError("malware advisory workflow must not inherit secrets")
    if "persist-credentials" in raw_text:
        raise AssertionError("malware advisory workflow must not configure credential persistence")
    if any(reference in raw_text for reference in LOCAL_MALWARE_CHECKER_REFERENCES):
        raise AssertionError("malware advisory workflow must not execute the local checker")

    token_safe_job = dict(job)
    token_safe_job["secrets"] = {}
    if recursively_find_string(token_safe_job, WORKFLOW_TOKEN_REFERENCE):
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
    validate_release_please_workflow()
    validate_job_requirements_contract()
    print(
        f"Validated {len(skill_files)} skills, plugin and marketplace JSON, "
        "workflow SHA pins, release-token hardening, Dependabot policy, dependency gates, exact dependency pins, "
        "and job-requirements round-trip."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, yaml.YAMLError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
