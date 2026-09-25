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
SPDX_VALIDATION_REQUIREMENTS = ROOT / "requirements-spdx-validation.txt"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
DEPENDENCY_REVIEW_WORKFLOW = ROOT / ".github" / "workflows" / "dependency-review.yml"
MALWARE_WORKFLOW = ROOT / ".github" / "workflows" / "advisory-malware.yml"
RELEASE_PLEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release-please.yml"
PUBLISH_RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "publish-release.yml"
OBSOLETE_SPDX_VALIDATOR = ROOT / "scripts" / "validate_spdx_sbom.py"
SCORECARD_WORKFLOW = ROOT / ".github" / "workflows" / "scorecard.yml"
RELEASE_PLEASE_CONFIG = ROOT / "release-please-config.json"
RELEASE_PLEASE_MANIFEST = ROOT / ".release-please-manifest.json"
VERSION_FILE = ROOT / "version.txt"
SYFT_CONFIG = ROOT / ".syft.yaml"
CREATE_APP_TOKEN_SHA = "bcd2ba49218906704ab6c1aa796996da409d3eb1"
CREATE_APP_TOKEN_VERSION = "v3.2.0"
RELEASE_PLEASE_ACTION_SHA = "45996ed1f6d02564a971a2fa1b5860e934307cf7"
RELEASE_PLEASE_ACTION_VERSION = "v5.0.0"
SCORECARD_ACTION_SHA = "2d1146689b8cda280b9bc96326124645441f03bc"
SCORECARD_ACTION_VERSION = "v2.4.4"
UPLOAD_ARTIFACT_SHA = "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
UPLOAD_ARTIFACT_VERSION = "v7.0.1"
DOWNLOAD_ARTIFACT_SHA = "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c"
DOWNLOAD_ARTIFACT_VERSION = "v8.0.1"
SBOM_ACTION_SHA = "3ad7283483fc7af8ff2b4ea19663c2d5ca935e26"
SBOM_ACTION_VERSION = "v0.24.2"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"
SETUP_PYTHON_VERSION = "v7.0.0"
CODEQL_ACTION_SHA = "1c5b675653bb5c22dbe9b12b556ec555138e09fd"
CODEQL_ACTION_VERSION = "v4.38.1"
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
LOCKED_REQUIREMENT = re.compile(
    r"^([A-Za-z0-9_.-]+)==([^<>=!~\s]+)\s+--hash=sha256:([0-9a-f]{64})$"
)
EXPECTED_SPDX_VALIDATION_LOCK = {
    "beartype": (
        "0.22.9",
        "d16c9bbc61ea14637596c5f6fbff2ee99cbe3573e46a716401734ef50c3060c2",
    ),
    "boolean.py": (
        "5.0",
        "ef28a70bd43115208441b53a045d1549e2f0ec6e3d08a9d142cbc41c1938e8d9",
    ),
    "click": (
        "8.5.0",
        "255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360",
    ),
    "isodate": (
        "0.7.2",
        "28009937d8031054830160fce6d409ed342816b543597cece116d966c6d99e15",
    ),
    "license-expression": (
        "30.4.4",
        "421788fdcadb41f049d2dc934ce666626265aeccefddd25e162a26f23bcbf8a4",
    ),
    "ply": (
        "3.11",
        "096f9b8350b65ebd2fd1346b12452efe5b9607f7482813ffca50c22722a807ce",
    ),
    "pyparsing": (
        "3.3.3",
        "ece8c00a69cf01b45d0b1dedabb469c90d8caf996d4fda40f147627a122849a4",
    ),
    "pyyaml": (
        "6.0.3",
        "ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc",
    ),
    "rdflib": (
        "7.6.0",
        "30c0a3ebf4c0e09215f066be7246794b6492e054e782d7ac2a34c9f70a15e0dd",
    ),
    "semantic-version": (
        "2.10.0",
        "de78a3b8e0feda74cabc54aab2da702113e33ac9d9eb9d2389bcf1f58b7d9177",
    ),
    "spdx-tools": (
        "0.8.5",
        "7c2d5865941be9d2e898f5b084e8d5422dd298dc5a29320ddb198fec304f59c4",
    ),
    "uritools": (
        "6.1.3",
        "136f113e76e53f85bf2d9cce0c3d40ceec775d0409e7d6de9b28f046a7d42838",
    ),
    "xmltodict": (
        "1.0.4",
        "a4a00d300b0e1c59fc2bfccb53d7b2e88c32f200df138a0dd2229f842497026a",
    ),
}
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


def validate_spdx_validation_lock() -> None:
    for requirements in REQUIREMENTS:
        if re.search(
            r"(?im)^\s*spdx[-_.]tools(?:\s|[<>=!~])",
            requirements.read_text(encoding="utf-8"),
        ):
            raise AssertionError(
                "spdx-tools must remain isolated from general requirement files"
            )

    physical_lines = SPDX_VALIDATION_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    logical_lines = []
    for index in range(0, len(physical_lines), 2):
        if index + 1 >= len(physical_lines) or not physical_lines[index].endswith("\\"):
            raise AssertionError("SPDX validation lock entries must contain one pinned hash")
        logical_lines.append(
            f"{physical_lines[index][:-1].strip()} {physical_lines[index + 1].strip()}"
        )
    observed = {}
    for line in logical_lines:
        match = LOCKED_REQUIREMENT.fullmatch(line)
        if match is None:
            raise AssertionError(f"invalid SPDX validation lock entry: {line}")
        observed[match.group(1).lower()] = (match.group(2), match.group(3))
    if observed != EXPECTED_SPDX_VALIDATION_LOCK:
        raise AssertionError("SPDX validation lock must match the reviewed wheel resolution")

    install_command = (
        "python -m pip install --require-hashes --only-binary=:all: "
        "-r requirements-spdx-validation.txt"
    )
    ci = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    ci_job = ci["jobs"]["validate"]
    setup_steps = [
        step
        for step in ci_job.get("steps", [])
        if isinstance(step, dict)
        and step.get("uses") == f"actions/setup-python@{SETUP_PYTHON_SHA}"
    ]
    if len(setup_steps) != 1 or setup_steps[0].get("with") != {
        "python-version": "3.12"
    }:
        raise AssertionError("hosted CI must run the official SPDX validator on Python 3.12")
    ci_runs = [
        " ".join(str(step.get("run", "")).split())
        for step in ci_job.get("steps", [])
        if isinstance(step, dict)
    ]
    if install_command not in ci_runs:
        raise AssertionError("hosted CI must install the hash-locked SPDX validator environment")


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
        "client-id": "${{ secrets.RELEASE_PLEASE_APP_CLIENT_ID }}",
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


def validate_release_please_config() -> None:
    config = json.loads(RELEASE_PLEASE_CONFIG.read_text(encoding="utf-8"))
    if config.get("draft") is not True:
        raise AssertionError("release-please must create draft releases before SBOM publication")
    if config.get("force-tag-creation") is not True:
        raise AssertionError("release-please must create the release tag to trigger SBOM publication")
    packages = config.get("packages")
    if not isinstance(packages, dict) or set(packages) != {"."}:
        raise AssertionError("release-please must configure exactly the root package")
    root_package = packages["."]
    if root_package.get("release-type") != "simple":
        raise AssertionError("release-please root package must use the simple release type")
    expected_updaters = {
        ("json", "plugin.json", "$.version"),
        ("json", ".github/plugin/marketplace.json", "$.metadata.version"),
        ("json", ".github/plugin/marketplace.json", "$.plugins[0].version"),
    }
    extra_files = root_package.get("extra-files")
    if not isinstance(extra_files, list):
        raise AssertionError("release-please must configure the required version updaters")
    observed_updaters = {
        (updater.get("type"), updater.get("path"), updater.get("jsonpath"))
        for updater in extra_files
        if isinstance(updater, dict)
    }
    if observed_updaters != expected_updaters or len(extra_files) != len(expected_updaters):
        raise AssertionError("release-please must configure the exact version updater set")

    manifest = json.loads(RELEASE_PLEASE_MANIFEST.read_text(encoding="utf-8"))
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not isinstance(manifest, dict) or set(manifest) != {"."} or manifest["."] != version:
        raise AssertionError("release-please manifest and version.txt must contain the same root version")
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    marketplace = json.loads(MANIFEST.read_text(encoding="utf-8"))
    consumer_versions = {
        "plugin.json $.version": plugin.get("version"),
        "marketplace $.metadata.version": marketplace.get("metadata", {}).get("version"),
        "marketplace $.plugins[0].version": (
            marketplace.get("plugins", [{}])[0].get("version")
            if marketplace.get("plugins")
            else None
        ),
    }
    drifted_versions = {
        field: observed
        for field, observed in consumer_versions.items()
        if observed != version
    }
    if drifted_versions:
        raise AssertionError(
            f"release consumer versions must match the root version {version}: {drifted_versions}"
        )


def validate_publish_release_workflow() -> None:
    workflow = yaml.load(PUBLISH_RELEASE_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(workflow, dict):
        raise AssertionError("release publication workflow must be a mapping")
    if workflow.get("on") != {"create": ""}:
        raise AssertionError("release publication workflow must run only for created refs")
    if workflow.get("permissions") != {}:
        raise AssertionError("release publication workflow must disable ambient permissions")

    jobs = workflow.get("jobs", {})
    if set(jobs) != {"resolve", "generate", "publish"}:
        raise AssertionError(
            "release publication workflow must separate resolution, generation, and publication"
        )
    resolve = jobs["resolve"]
    generate = jobs["generate"]
    publish = jobs["publish"]
    expected_tag_guard = "github.ref_type == 'tag' && startsWith(github.ref_name, 'v')"
    if resolve.get("if") != expected_tag_guard:
        raise AssertionError("release resolution must be restricted to version tags")
    if resolve.get("permissions") != {"contents": "write"}:
        raise AssertionError("draft release resolution must receive contents write")
    if generate.get("permissions") != {"contents": "read"}:
        raise AssertionError("SBOM generation must receive read-only repository access")
    if generate.get("needs") != "resolve" or generate.get("if") != (
        "needs.resolve.outputs.state == 'draft'"
    ):
        raise AssertionError("SBOM generation must consume only resolved draft metadata")
    if publish.get("permissions") != {"contents": "write"}:
        raise AssertionError("release publication must receive contents write")
    if publish.get("needs") != ["resolve", "generate"] or publish.get("if") != (
        "needs.resolve.outputs.state == 'draft'"
    ):
        raise AssertionError("release publication must consume only a validated draft SBOM")

    resolve_steps = resolve.get("steps", [])
    generate_steps = generate.get("steps", [])
    publish_steps = publish.get("steps", [])
    if len(resolve_steps) != 2 or len(generate_steps) != 8 or len(publish_steps) != 3:
        raise AssertionError("release publication workflow has an unexpected step contract")
    resolve_checkout, release = resolve_steps
    checkout, setup_python, install, sbom, prepare, official, contract, upload = (
        generate_steps
    )
    download, attach, finalize = publish_steps
    expected_resolve_checkout = {
        "ref": "${{ github.sha }}",
        "fetch-depth": "0",
        "persist-credentials": "false",
    }
    expected_generate_checkout = {
        "ref": "${{ github.sha }}",
        "persist-credentials": "false",
    }
    if (
        resolve_checkout.get("with") != expected_resolve_checkout
        or checkout.get("with") != expected_generate_checkout
    ):
        raise AssertionError(
            "release checkouts must use the triggering commit without persisted credentials"
        )
    if release.get("id") != "release":
        raise AssertionError("release resolution must expose draft metadata")
    resolve_script = str(release.get("run", ""))
    required_resolution_checks = (
        "+refs/heads/main:refs/remotes/origin/main",
        "git merge-base --is-ancestor HEAD origin/main",
        "release is already published; refusing to infer validated provenance",
        "release_id=",
        "state=draft",
    )
    if any(value not in resolve_script for value in required_resolution_checks):
        raise AssertionError(
            "release resolution must enforce ancestry, draft retries, and published-release failure"
        )
    if "state=published" in resolve_script or "asset_names" in resolve_script:
        raise AssertionError(
            "release resolution must not infer validated publication from asset-name presence"
        )
    if "gh api" in "\n".join(str(step.get("run", "")) for step in generate_steps):
        raise AssertionError("read-only SBOM generation must not query draft releases")
    if sbom.get("uses") != f"anchore/sbom-action@{SBOM_ACTION_SHA}":
        raise AssertionError("SPDX generation must use the approved pinned SBOM action")
    if setup_python.get("uses") != f"actions/setup-python@{SETUP_PYTHON_SHA}" or (
        setup_python.get("with") != {"python-version": "3.12"}
    ):
        raise AssertionError("SPDX validation must use the approved Python 3.12 action")
    expected_install = (
        "python -m pip install --require-hashes --only-binary=:all: "
        "-r requirements-spdx-validation.txt"
    )
    if " ".join(str(install.get("run", "")).split()) != expected_install:
        raise AssertionError("release generation must install the hash-locked SPDX validator")
    if sbom.get("with") != {
        "path": ".",
        "config": ".syft.yaml",
        "format": "spdx-json",
        "output-file": "resume-builder.spdx.json",
        "upload-artifact": "false",
        "upload-release-assets": "false",
    }:
        raise AssertionError("SPDX generation must use the approved local-only configuration")
    if prepare.get("run") != (
        'python3 scripts/prepare_spdx_sbom.py resume-builder.spdx.json "$RELEASE_VERSION"'
    ):
        raise AssertionError("generated SPDX output must receive repository-owned product metadata")
    if official.get("run") != (
        "pyspdxtools -i resume-builder.spdx.json --version SPDX-2.3"
    ):
        raise AssertionError("generated SPDX output must pass official SPDX 2.3 validation")
    if "continue-on-error" in official:
        raise AssertionError("official SPDX validation must remain fail-closed")
    expected_contract = (
        'python3 scripts/validate_release_sbom_contract.py '
        'resume-builder.spdx.json "$RELEASE_VERSION"'
    )
    if " ".join(str(contract.get("run", "")).split()) != expected_contract:
        raise AssertionError("officially valid SPDX output must pass the release contract")
    if "continue-on-error" in contract:
        raise AssertionError("release SBOM contract validation must remain fail-closed")
    if upload.get("uses") != f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}":
        raise AssertionError("validated SPDX artifact must use the approved pinned uploader")
    if download.get("uses") != f"actions/download-artifact@{DOWNLOAD_ARTIFACT_SHA}":
        raise AssertionError("release publication must use the approved pinned downloader")
    attach_script = str(attach.get("run", ""))
    if "gh release upload" not in attach_script or "shasum -a 256" not in attach_script:
        raise AssertionError("release publication must upload and checksum-verify the SPDX asset")
    finalize_script = str(finalize.get("run", ""))
    if "--method PATCH" not in finalize_script or "-F draft=false" not in finalize_script:
        raise AssertionError("release publication must publish only after the SPDX asset is verified")

    syft = yaml.safe_load(SYFT_CONFIG.read_text(encoding="utf-8"))
    if syft.get("source") != {"name": "resume-builder"}:
        raise AssertionError("Syft must identify the released product without misattributing suppliers")
    excludes = set(syft.get("exclude", []))
    if not {"./requirements-dev.txt", "./tests/**", "./.copilot-tracking/**"} <= excludes:
        raise AssertionError("Syft must exclude development-only and tracking content")

    raw_text = PUBLISH_RELEASE_WORKFLOW.read_text(encoding="utf-8")
    expected_pins = (
        (SETUP_PYTHON_SHA, SETUP_PYTHON_VERSION),
        (SBOM_ACTION_SHA, SBOM_ACTION_VERSION),
        (UPLOAD_ARTIFACT_SHA, UPLOAD_ARTIFACT_VERSION),
        (DOWNLOAD_ARTIFACT_SHA, DOWNLOAD_ARTIFACT_VERSION),
    )
    for sha, version in expected_pins:
        if not re.search(rf"@{sha}\s+#\s+{re.escape(version)}\b", raw_text):
            raise AssertionError(f"release publication must document pinned action version {version}")
    forbidden = ("pull_request_target", "secrets:", "RELEASE_PLEASE_APP_PRIVATE_KEY")
    if any(value in raw_text for value in forbidden):
        raise AssertionError("release publication must not expose privileged triggers or repository secrets")
    if OBSOLETE_SPDX_VALIDATOR.exists():
        raise AssertionError("obsolete mixed SPDX validator must not be restored")


def validate_scorecard_workflow() -> None:
    workflow = yaml.load(SCORECARD_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(workflow, dict):
        raise AssertionError("Scorecard workflow must be a mapping")
    if workflow.get("on") != {
        "branch_protection_rule": "",
        "schedule": [{"cron": "19 6 * * 1"}],
        "push": {"branches": ["main"]},
    }:
        raise AssertionError("Scorecard workflow must monitor main, branch rules, and a weekly schedule")
    if workflow.get("permissions") != "read-all":
        raise AssertionError("Scorecard workflow must default to read-only permissions")

    jobs = workflow.get("jobs", {})
    if set(jobs) != {"analysis"}:
        raise AssertionError("Scorecard workflow must keep one analysis job")
    job = jobs["analysis"]
    if job.get("runs-on") != "ubuntu-latest":
        raise AssertionError("Scorecard must run on a GitHub-hosted Ubuntu runner")
    if job.get("permissions") != {
        "contents": "read",
        "security-events": "write",
        "id-token": "write",
    }:
        raise AssertionError("Scorecard job permissions must be limited to source, SARIF, and OIDC")

    steps = job.get("steps", [])
    if len(steps) != 4:
        raise AssertionError("Scorecard workflow must contain checkout, analysis, artifact, and SARIF steps")
    checkout, analysis, artifact, sarif = steps
    if checkout.get("with") != {"persist-credentials": "false"}:
        raise AssertionError("Scorecard checkout must not persist credentials")
    if analysis.get("uses") != f"ossf/scorecard-action@{SCORECARD_ACTION_SHA}":
        raise AssertionError("Scorecard analysis must use the approved pinned release")
    if analysis.get("with") != {
        "results_file": "results.sarif",
        "results_format": "sarif",
        "publish_results": "true",
    }:
        raise AssertionError("Scorecard must publish SARIF results with OIDC")
    if artifact.get("uses") != f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}":
        raise AssertionError("Scorecard artifact upload must use the approved pinned release")
    if artifact.get("with") != {
        "name": "scorecard-results",
        "path": "results.sarif",
        "retention-days": "5",
    }:
        raise AssertionError("Scorecard SARIF artifact must use the approved retention policy")
    if sarif.get("uses") != f"github/codeql-action/upload-sarif@{CODEQL_ACTION_SHA}":
        raise AssertionError("Scorecard SARIF upload must use the approved pinned CodeQL release")
    if sarif.get("with") != {"sarif_file": "results.sarif"}:
        raise AssertionError("Scorecard SARIF upload must publish the generated results")

    raw_text = SCORECARD_WORKFLOW.read_text(encoding="utf-8")
    expected_pins = (
        (SCORECARD_ACTION_SHA, SCORECARD_ACTION_VERSION),
        (UPLOAD_ARTIFACT_SHA, UPLOAD_ARTIFACT_VERSION),
        (CODEQL_ACTION_SHA, CODEQL_ACTION_VERSION),
    )
    for sha, version in expected_pins:
        if not re.search(rf"@{sha}\s+#\s+{re.escape(version)}\b", raw_text):
            raise AssertionError(f"Scorecard workflow must document pinned action version {version}")
    if "pull_request_target" in raw_text or "secrets:" in raw_text:
        raise AssertionError("Scorecard workflow must not use privileged PR triggers or repository secrets")


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
    validate_spdx_validation_lock()
    validate_dependabot_policy()
    validate_dependency_check_workflows()
    validate_release_please_workflow()
    validate_release_please_config()
    validate_publish_release_workflow()
    validate_scorecard_workflow()
    validate_job_requirements_contract()
    print(
        f"Validated {len(skill_files)} skills, plugin and marketplace JSON, "
        "workflow SHA pins, release-token, SPDX publication, and Scorecard hardening, Dependabot policy, "
        "dependency gates, exact dependency pins, and job-requirements round-trip."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, yaml.YAMLError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
