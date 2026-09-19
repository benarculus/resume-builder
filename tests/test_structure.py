from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_repo.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_repo", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repository_validation_script() -> None:
    subprocess.run([sys.executable, str(VALIDATOR)], check=True)


def test_workflow_action_pin_pattern_requires_sha_and_version_comment() -> None:
    validator = load_validator()
    assert validator.SHA_PINNED_ACTION.search(
        "uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4"
    )
    assert not validator.SHA_PINNED_ACTION.search("uses: actions/checkout@v4")
    assert not validator.SHA_PINNED_ACTION.search("uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262")


def test_requirement_pin_pattern_allows_exact_direct_pins_only() -> None:
    validator = load_validator()
    assert validator.REQUIREMENT_PIN.match("PyYAML==6.0.3")
    assert not validator.REQUIREMENT_PIN.match("PyYAML>=6,<7")
    assert not validator.REQUIREMENT_PIN.match("pytest~=8.4")


def test_dependabot_policy_requires_approved_groups_and_cooldown() -> None:
    validator = load_validator()
    validator.validate_dependabot_policy()


def test_dependabot_policy_rejects_weakened_cooldown(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependabot.yml"
    weakened.write_text(
        (ROOT / ".github/dependabot.yml")
        .read_text(encoding="utf-8")
        .replace("default-days: 14", "default-days: 1"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDABOT", weakened)

    with pytest.raises(AssertionError, match="cooldown"):
        validator.validate_dependabot_policy()


def test_dependabot_policy_requires_weekly_actions_updates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependabot.yml"
    weakened.write_text(
        (ROOT / ".github/dependabot.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  - package-ecosystem: github-actions\n    directory: /\n    schedule:\n      interval: weekly",
            "  - package-ecosystem: github-actions\n    directory: /\n    schedule:\n      interval: monthly",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDABOT", weakened)

    with pytest.raises(AssertionError, match="github-actions.*weekly"):
        validator.validate_dependabot_policy()


def test_dependency_workflows_require_approved_security_policy() -> None:
    validator = load_validator()
    validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_weakened_severity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace("fail-on-severity: low", "fail-on-severity: high"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="approved action policy"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_token_exposure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "        run: >-",
            "        env:\n          GITHUB_TOKEN: ${{ github.token }}\n        run: >-",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="must not expose workflow tokens"):
        validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_job_permission_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  dependency-review:\n",
            "  dependency-review:\n    permissions: write-all\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="job scope"):
        validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_pull_request_target(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace("  pull_request:\n", "  pull_request:\n  pull_request_target:\n"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="pull_request"):
        validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_continue_on_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  dependency-review:\n",
            "  dependency-review:\n    continue-on-error: true\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="continue on error"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_any_token_alias(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "        run: >-",
            "        env:\n          TOKEN: ${{ secrets.GITHUB_TOKEN }}\n        run: >-",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="workflow tokens"):
        validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_expression_continue_on_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  dependency-review:\n",
            "  dependency-review:\n    continue-on-error: ${{ true }}\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="continue on error"):
        validator.validate_dependency_check_workflows()


def test_workflow_discovery_includes_yaml_extension(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    workflow = tmp_path / "unpinned.yaml"
    workflow.write_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n", encoding="utf-8")
    monkeypatch.setattr(validator, "WORKFLOWS", (workflow,))

    with pytest.raises(AssertionError, match="full SHA"):
        validator.validate_workflow_pins()
