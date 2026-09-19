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


def test_dependabot_policy_requires_schema_version_two(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependabot.yml"
    weakened.write_text(
        (ROOT / ".github/dependabot.yml")
        .read_text(encoding="utf-8")
        .replace("version: 2", "version: 1"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDABOT", weakened)

    with pytest.raises(AssertionError, match="schema version 2"):
        validator.validate_dependabot_policy()


def test_dependabot_policy_rejects_duplicate_ecosystems(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependabot.yml"
    original = (ROOT / ".github/dependabot.yml").read_text(encoding="utf-8")
    pip_update = original[
        original.index("  - package-ecosystem: pip") : original.index(
            "  - package-ecosystem: github-actions"
        )
    ]
    weakened.write_text(f"{original}\n{pip_update}", encoding="utf-8")
    monkeypatch.setattr(validator, "DEPENDABOT", weakened)

    with pytest.raises(AssertionError, match="duplicate package ecosystems"):
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
            "        env:\n          TOKEN: ${{ toJSON(secrets) }}\n        run: >-",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="workflow tokens"):
        validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_filtered_pull_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace("  pull_request:\n", "  pull_request:\n    types: [closed]\n"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="pull_request"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_second_credential_persisting_checkout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "      - name: Check changed Python dependencies",
            "      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4\n"
            "      - name: Check changed Python dependencies",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="checkouts"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_checker_command_substitution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            '          && python "$RUNNER_TEMP/check_malware_advisories.py"',
            '          && echo "$RUNNER_TEMP/check_malware_advisories.py"',
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="repository-owned checker"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_requires_trusted_checker_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            '&& git show "$CHECKER_REF:scripts/check_malware_advisories.py"\n'
            '          > "$RUNNER_TEMP/check_malware_advisories.py"\n'
            '          && python "$RUNNER_TEMP/check_malware_advisories.py"',
            "python scripts/check_malware_advisories.py",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="repository-owned checker"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_custom_checker_shell(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace("        shell: bash\n", "        shell: bash -c 'true {0}'\n"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="must use bash"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_default_shell_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace("permissions:\n", "defaults:\n  run:\n    shell: bash -c 'true {0}'\n\npermissions:\n"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="default shell"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_job_default_shell_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  advisory-malware:\n",
            "  advisory-malware:\n    defaults:\n      run:\n        shell: bash -c 'true {0}'\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="default shell"):
        validator.validate_dependency_check_workflows()


def test_dependency_workflows_reject_conditional_job(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependency-review.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/dependency-review.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  dependency-review:\n",
            "  dependency-review:\n    if: ${{ false }}\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDENCY_REVIEW_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="must not be conditional"):
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
