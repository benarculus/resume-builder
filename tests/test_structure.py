from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repository_validation_script() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_repo.py")], check=True)
