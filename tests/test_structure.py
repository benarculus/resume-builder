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

    with pytest.raises(AssertionError, match="one pip and one github-actions entry"):
        validator.validate_dependabot_policy()


def test_dependabot_policy_rejects_unapproved_group(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependabot.yml"
    weakened.write_text(
        (ROOT / ".github/dependabot.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    groups:\n",
            "    groups:\n      pip-exception:\n        applies-to: version-updates\n        patterns: [python-docx]\n",
            1,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDABOT", weakened)

    with pytest.raises(AssertionError, match="pip Dependabot groups"):
        validator.validate_dependabot_policy()


def test_dependabot_policy_rejects_extra_dependency_group(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "dependabot.yml"
    weakened.write_text(
        (ROOT / ".github/dependabot.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    groups:\n      pip-version-updates:",
            "    groups:\n      pip-single-package:\n"
            "        applies-to: version-updates\n"
            "        patterns:\n"
            "          - some-package\n"
            "      pip-version-updates:",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "DEPENDABOT", weakened)

    with pytest.raises(AssertionError, match="pip Dependabot groups must match the approved policy"):
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


def test_malware_workflow_requires_approved_reusable_release() -> None:
    validator = load_validator()
    validator.validate_dependency_check_workflows()
    workflow = (ROOT / ".github/workflows/advisory-malware.yml").read_text(encoding="utf-8")
    assert validator.MALWARE_REUSABLE_OWNER_REPO == "benarculus/malware-advisory-check"
    assert validator.MALWARE_REUSABLE_WORKFLOW.endswith(
        "/.github/workflows/reusable-malware-advisory-check.yml"
    )
    assert validator.MALWARE_REUSABLE_SHA == "f8392606fb92e923737bb3b4f63990346bd0644b"
    assert len(validator.MALWARE_REUSABLE_SHA) == 40
    assert "# v1.0.0" in workflow


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


def test_malware_workflow_rejects_broadened_permissions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace("  contents: read", "  contents: write"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="contents: read permissions"):
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


def test_malware_workflow_rejects_mutable_reusable_ref(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    approved = validator.MALWARE_REUSABLE_USES
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(approved, f"{validator.MALWARE_REUSABLE_WORKFLOW}@main"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="approved v1.0.0 release SHA"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_short_reusable_ref(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    approved = validator.MALWARE_REUSABLE_USES
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(approved, f"{validator.MALWARE_REUSABLE_WORKFLOW}@{validator.MALWARE_REUSABLE_SHA[:12]}"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="approved v1.0.0 release SHA"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_missing_release_comment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(" # v1.0.0", ""),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="approved v1.0.0 release SHA"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_wrong_reusable_owner(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace("benarculus/malware-advisory-check", "someone/malware-advisory-check"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="approved v1.0.0 release SHA"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_secret_inheritance(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    secrets:\n      github-token: ${{ secrets.GITHUB_TOKEN }}",
            "    secrets: inherit",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="inherit secrets"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_token_leakage_outside_named_mapping(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace("name: Advisory Malware Check", "name: ${{ github.token }}"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="workflow tokens"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_wrong_token_secret_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace("github-token: ${{ secrets.GITHUB_TOKEN }}", "token: ${{ secrets.GITHUB_TOKEN }}"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="named github-token secret"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_wrong_base_head_mapping(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "base-ref: ${{ github.event.pull_request.base.sha }}",
            "base-ref: ${{ github.base_ref }}",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="PR base/head SHA inputs"):
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


def test_malware_workflow_rejects_local_checker_execution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    with:\n",
            "    runs-on: ubuntu-latest\n    steps:\n"
            "      - run: python scripts/check_malware_advisories.py\n    with:\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="local checker"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_credential_persistence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    name: Advisory Malware Check\n",
            "    name: Advisory Malware Check\n    persist-credentials: true\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="credential persistence"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_conditional_job(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    name: Advisory Malware Check\n",
            "    name: Advisory Malware Check\n    if: ${{ false }}\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="must not be conditional"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_continue_on_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    name: Advisory Malware Check\n",
            "    name: Advisory Malware Check\n    continue-on-error: true\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="continue on error"):
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


def test_workflow_discovery_includes_yaml_extension(tmp_path: Path) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    copied_validator = scripts_dir / "validate_repo.py"
    copied_validator.write_text(VALIDATOR.read_text(encoding="utf-8"), encoding="utf-8")

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "unpinned.yaml").write_text(
        "jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n", encoding="utf-8"
    )

    spec = importlib.util.spec_from_file_location("validate_repo_yaml_glob", copied_validator)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with pytest.raises(AssertionError, match="full SHA"):
        module.validate_workflow_pins()
