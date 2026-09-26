from __future__ import annotations

import importlib.util
import json
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


def test_release_please_workflow_uses_hardened_app_token() -> None:
    validator = load_validator()
    validator.validate_release_please_workflow()


def test_release_please_workflow_rejects_long_lived_token(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "release-please.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/release-please.yml")
        .read_text(encoding="utf-8")
        .replace(
            "token: ${{ steps.app-token.outputs.token }}",
            "token: ${{ secrets.RELEASE_PLEASE_TOKEN }}",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "RELEASE_PLEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="ephemeral GitHub App token"):
        validator.validate_release_please_workflow()


def test_release_please_workflow_rejects_broad_app_scope(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "release-please.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/release-please.yml")
        .read_text(encoding="utf-8")
        .replace("          repositories: ${{ github.event.repository.name }}\n", ""),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "RELEASE_PLEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="scoped to this repository"):
        validator.validate_release_please_workflow()


def test_release_please_config_requires_draft_release_publication() -> None:
    validator = load_validator()
    validator.validate_release_please_config()


def test_release_please_config_rejects_immediate_publication(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "release-please-config.json"
    weakened.write_text(
        (ROOT / "release-please-config.json")
        .read_text(encoding="utf-8")
        .replace('"draft": true', '"draft": false'),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "RELEASE_PLEASE_CONFIG", weakened)

    with pytest.raises(AssertionError, match="draft releases"):
        validator.validate_release_please_config()


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('"release-type": "simple"', '"release-type": "node"', "simple release type"),
        ('{ "type": "json", "path": "plugin.json", "jsonpath": "$.version" },\n', "", "updater"),
        ('"jsonpath": "$.plugins[0].version"', '"jsonpath": "$.plugins[1].version"', "updater"),
    ],
)
def test_release_please_config_rejects_version_contract_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    old: str,
    new: str,
    message: str,
) -> None:
    validator = load_validator()
    weakened = tmp_path / "release-please-config.json"
    weakened.write_text(
        (ROOT / "release-please-config.json").read_text(encoding="utf-8").replace(old, new),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "RELEASE_PLEASE_CONFIG", weakened)

    with pytest.raises(AssertionError, match=message):
        validator.validate_release_please_config()


def test_release_please_config_rejects_version_seed_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    drifted_version = tmp_path / "version.txt"
    drifted_version.write_text("0.2.0\n", encoding="utf-8")
    monkeypatch.setattr(validator, "VERSION_FILE", drifted_version)

    with pytest.raises(AssertionError, match="manifest and version.txt"):
        validator.validate_release_please_config()


@pytest.mark.parametrize(
    ("target", "path", "field"),
    [
        ("PLUGIN", "plugin.json", "plugin"),
        ("MANIFEST", "marketplace-metadata.json", "metadata"),
        ("MANIFEST", "marketplace-plugin.json", "marketplace-plugin"),
    ],
)
def test_release_please_config_rejects_consumer_version_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    target: str,
    path: str,
    field: str,
) -> None:
    validator = load_validator()
    source = getattr(validator, target)
    drifted = tmp_path / path
    document = json.loads(source.read_text(encoding="utf-8"))
    if field == "plugin":
        document["version"] = "0.2.0"
    elif field == "metadata":
        document["metadata"]["version"] = "0.2.0"
    else:
        document["plugins"][0]["version"] = "0.2.0"
    drifted.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(validator, target, drifted)

    with pytest.raises(AssertionError, match="consumer versions"):
        validator.validate_release_please_config()


def test_publish_release_workflow_uses_validated_spdx_boundary() -> None:
    validator = load_validator()
    validator.validate_publish_release_workflow()


def test_publish_release_workflow_rejects_write_access_during_generation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/publish-release.yml")
        .read_text(encoding="utf-8")
        .replace("      contents: read", "      contents: write"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="read-only"):
        validator.validate_publish_release_workflow()


def test_publish_release_workflow_rejects_read_only_draft_resolution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/publish-release.yml")
        .read_text(encoding="utf-8")
        .replace("      contents: write", "      contents: read", 1),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="resolution.*contents write"):
        validator.validate_publish_release_workflow()


def test_publish_release_workflow_requires_complete_main_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/publish-release.yml")
        .read_text(encoding="utf-8")
        .replace("          fetch-depth: 0\n", "")
        .replace(
            'git fetch --no-tags origin \\\n            "+refs/heads/main:refs/remotes/origin/main"',
            "git fetch --no-tags origin main",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="release checkouts|ancestry"):
        validator.validate_publish_release_workflow()


def test_publish_release_workflow_rejects_ambiguous_tag_checkout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/publish-release.yml")
        .read_text(encoding="utf-8")
        .replace("          ref: ${{ github.sha }}", "          ref: ${{ github.ref_name }}"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="triggering commit"):
        validator.validate_publish_release_workflow()


def test_publish_release_workflow_rejects_published_asset_name_bypass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    original = (ROOT / ".github/workflows/publish-release.yml").read_text(
        encoding="utf-8"
    )
    fail_closed = (
        "          if not release[\"draft\"]:\n"
        "              raise SystemExit(\n"
        "                  \"release is already published; refusing to infer "
        "validated provenance \"\n"
        "                  \"from immutable release assets\"\n"
        "              )\n"
    )
    filename_bypass = (
        "          asset_names = {asset[\"name\"] for asset in release.get(\"assets\", [])}\n"
        "          if not release[\"draft\"]:\n"
        "              if \"resume-builder.spdx.json\" not in asset_names:\n"
        "                  raise SystemExit(\"published release is missing the SBOM\")\n"
        "              with open(output_path, \"a\", encoding=\"utf-8\") as output:\n"
        "                  output.write(\"state=published\\n\")\n"
        "              print(\"published\")\n"
        "              raise SystemExit\n"
    )
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        original.replace(fail_closed, filename_bypass).replace(
            'if [ "$state" = "draft" ]; then',
            'if [ "$state" = "draft" ] || [ "$state" = "published" ]; then',
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="published-release failure|asset-name presence"):
        validator.validate_publish_release_workflow()


def test_scorecard_workflow_uses_hardened_published_results() -> None:
    validator = load_validator()
    validator.validate_scorecard_workflow()


def test_scorecard_workflow_rejects_repository_secrets(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "scorecard.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/scorecard.yml").read_text(encoding="utf-8")
        + "\n# secrets: must-not-be-added\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "SCORECARD_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="repository secrets"):
        validator.validate_scorecard_workflow()


def test_scorecard_workflow_rejects_credential_persistence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "scorecard.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/scorecard.yml")
        .read_text(encoding="utf-8")
        .replace("persist-credentials: false", "persist-credentials: true"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "SCORECARD_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="must not persist credentials"):
        validator.validate_scorecard_workflow()


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


def test_spdx_validation_lock_uses_reviewed_hashes_and_hosted_python() -> None:
    validator = load_validator()
    validator.validate_spdx_validation_lock()


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            "spdx-tools==0.8.5",
            "spdx-tools==0.8.4",
            "reviewed wheel resolution",
        ),
        (
            "7c2d5865941be9d2e898f5b084e8d5422dd298dc5a29320ddb198fec304f59c4",
            "0" * 64,
            "reviewed wheel resolution",
        ),
    ],
)
def test_spdx_validation_lock_rejects_dependency_or_hash_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    old: str,
    new: str,
    message: str,
) -> None:
    validator = load_validator()
    weakened = tmp_path / "requirements-spdx-validation.txt"
    weakened.write_text(
        (ROOT / "requirements-spdx-validation.txt")
        .read_text(encoding="utf-8")
        .replace(old, new),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "SPDX_VALIDATION_REQUIREMENTS", weakened)

    with pytest.raises(AssertionError, match=message):
        validator.validate_spdx_validation_lock()


def test_ci_requires_hash_locked_spdx_validator_install(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "ci.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/ci.yml")
        .read_text(encoding="utf-8")
        .replace("--require-hashes ", ""),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "CI_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="hash-locked SPDX validator"):
        validator.validate_spdx_validation_lock()


@pytest.mark.parametrize("requirements_name", ["requirements.txt", "requirements-dev.txt"])
def test_spdx_validation_lock_rejects_general_dependency_misattribution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, requirements_name: str
) -> None:
    validator = load_validator()
    general = tmp_path / requirements_name
    general.write_text("spdx-tools==0.8.5\n", encoding="utf-8")
    unchanged = ROOT / (
        "requirements-dev.txt"
        if requirements_name == "requirements.txt"
        else "requirements.txt"
    )
    monkeypatch.setattr(validator, "REQUIREMENTS", (general, unchanged))

    with pytest.raises(AssertionError, match="isolated from general requirement files"):
        validator.validate_spdx_validation_lock()


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('python-version: "3.12"', 'python-version: "3.11"', "Python 3.12"),
        ("--only-binary=:all:", "", "hash-locked SPDX validator"),
    ],
)
def test_ci_rejects_spdx_runtime_or_install_weakening(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    old: str,
    new: str,
    message: str,
) -> None:
    validator = load_validator()
    weakened = tmp_path / "ci.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/ci.yml")
        .read_text(encoding="utf-8")
        .replace(old, new),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "CI_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match=message):
        validator.validate_spdx_validation_lock()


def test_publish_release_workflow_requires_official_gate_before_contract(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    original = (ROOT / ".github/workflows/publish-release.yml").read_text(
        encoding="utf-8"
    )
    official = (
        "      - name: Validate SPDX 2.3 conformance\n"
        "        run: pyspdxtools -i resume-builder.spdx.json --version SPDX-2.3\n"
    )
    contract = (
        "      - name: Validate release SBOM contract\n"
        "        env:\n"
        "          RELEASE_VERSION: ${{ needs.resolve.outputs.version }}\n"
        "        run: >-\n"
        "          python3 scripts/validate_release_sbom_contract.py\n"
        '          resume-builder.spdx.json "$RELEASE_VERSION"\n'
    )
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        original.replace(f"{official}{contract}", f"{contract}{official}"),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="official SPDX 2.3"):
        validator.validate_publish_release_workflow()


@pytest.mark.parametrize(
    "step_name",
    [
        "Set up Python",
        "Install SPDX validation dependencies",
        "Validate SPDX 2.3 conformance",
        "Validate release SBOM contract",
    ],
)
def test_publish_release_workflow_rejects_required_step_removal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, step_name: str
) -> None:
    validator = load_validator()
    original = (ROOT / ".github/workflows/publish-release.yml").read_text(
        encoding="utf-8"
    )
    step_start = original.index(f"      - name: {step_name}\n")
    next_step = original.find("\n      - name:", step_start + 1)
    if next_step == -1:
        next_step = original.index("\n\n  publish:", step_start)
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        f"{original[:step_start]}{original[next_step + 1:]}",
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="unexpected step contract"):
        validator.validate_publish_release_workflow()


@pytest.mark.parametrize(
    "step_name",
    ["Validate SPDX 2.3 conformance", "Validate release SBOM contract"],
)
def test_publish_release_workflow_rejects_validator_continue_on_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, step_name: str
) -> None:
    validator = load_validator()
    original = (ROOT / ".github/workflows/publish-release.yml").read_text(
        encoding="utf-8"
    )
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        original.replace(
            f"      - name: {step_name}\n",
            f"      - name: {step_name}\n        continue-on-error: true\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="fail-closed"):
        validator.validate_publish_release_workflow()


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            "pyspdxtools -i resume-builder.spdx.json --version SPDX-2.3",
            "pyspdxtools -i resume-builder.spdx.json",
            "official SPDX 2.3",
        ),
        (
            "python3 scripts/validate_release_sbom_contract.py",
            "python3 -c 'print(\"contract bypassed\")'",
            "release contract",
        ),
        (
            "--require-hashes --only-binary=:all:",
            "--require-hashes",
            "hash-locked SPDX validator",
        ),
        (
            'python-version: "3.12"',
            'python-version: "3.11"',
            "Python 3.12",
        ),
        (
            "syft-version: v1.52.0",
            "syft-version: v1.51.1",
            "local-only configuration",
        ),
    ],
)
def test_publish_release_workflow_rejects_validation_boundary_weakening(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    old: str,
    new: str,
    message: str,
) -> None:
    validator = load_validator()
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/publish-release.yml")
        .read_text(encoding="utf-8")
        .replace(old, new),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match=message):
        validator.validate_publish_release_workflow()


def test_publish_release_workflow_rejects_validation_lock_in_product_sbom(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / ".syft.yaml"
    weakened.write_text(
        (ROOT / ".syft.yaml")
        .read_text(encoding="utf-8")
        .replace("  - ./requirements-spdx-validation.txt\n", ""),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "SYFT_CONFIG", weakened)

    with pytest.raises(AssertionError, match="validation-only"):
        validator.validate_publish_release_workflow()


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (
            '          immutable_settings="$(\n'
            '            gh api "repos/${REPOSITORY}/immutable-releases"\n'
            '          )"\n'
            '          test "$(jq -r \'.enabled\' <<<"$immutable_settings")" = "true"\n'
            '          jq \'{enabled,enforced_by_owner}\' <<<"$immutable_settings"\n',
            "",
        ),
        (
            'test "$(jq -r \'.enabled\' <<<"$immutable_settings")" = "true"',
            'test "$(jq -r \'.enabled\' <<<"$immutable_settings")" = "false"',
        ),
    ],
)
def test_publish_release_workflow_requires_immutable_release_enforcement(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, old: str, new: str
) -> None:
    validator = load_validator()
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/publish-release.yml")
        .read_text(encoding="utf-8")
        .replace(old, new),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="immutable-release enforcement"):
        validator.validate_publish_release_workflow()


@pytest.mark.parametrize(
    "gate_name",
    ["Validate SPDX 2.3 conformance", "Validate release SBOM contract"],
)
def test_publish_release_workflow_rejects_upload_before_validation_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, gate_name: str
) -> None:
    validator = load_validator()
    original = (ROOT / ".github/workflows/publish-release.yml").read_text(
        encoding="utf-8"
    )
    upload_start = original.index("      - name: Upload validated SPDX SBOM")
    upload_end = original.index("\n\n  publish:", upload_start)
    upload = original[upload_start:upload_end]
    without_upload = f"{original[:upload_start]}{original[upload_end:]}"
    gate_start = without_upload.index(f"      - name: {gate_name}")
    weakened = tmp_path / "publish-release.yml"
    weakened.write_text(
        f"{without_upload[:gate_start]}{upload}\n{without_upload[gate_start:]}",
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "PUBLISH_RELEASE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="official SPDX 2.3|release contract"):
        validator.validate_publish_release_workflow()


def test_publish_release_workflow_rejects_obsolete_mixed_validator(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    obsolete = tmp_path / "validate_spdx_sbom.py"
    obsolete.write_text("# obsolete\n", encoding="utf-8")
    monkeypatch.setattr(validator, "OBSOLETE_SPDX_VALIDATOR", obsolete)

    with pytest.raises(AssertionError, match="obsolete mixed SPDX validator"):
        validator.validate_publish_release_workflow()


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
    assert validator.MALWARE_REUSABLE_SHA == "733acbdf20304f70ac0c9a763921cac4c23882ef"
    assert len(validator.MALWARE_REUSABLE_SHA) == 40
    assert "# v1.0.2" in workflow


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

    with pytest.raises(AssertionError, match="approved v1.0.2 release SHA"):
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

    with pytest.raises(AssertionError, match="approved v1.0.2 release SHA"):
        validator.validate_dependency_check_workflows()


def test_malware_workflow_rejects_missing_release_comment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = load_validator()
    weakened = tmp_path / "advisory-malware.yml"
    weakened.write_text(
        (ROOT / ".github/workflows/advisory-malware.yml")
        .read_text(encoding="utf-8")
        .replace(" # v1.0.2", ""),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "MALWARE_WORKFLOW", weakened)

    with pytest.raises(AssertionError, match="approved v1.0.2 release SHA"):
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

    with pytest.raises(AssertionError, match="approved v1.0.2 release SHA"):
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
