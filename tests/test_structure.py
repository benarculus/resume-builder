from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

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
