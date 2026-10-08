from __future__ import annotations

import os
import shutil
from collections.abc import Callable

import pytest


def _require_native_tool(executable: str, package: str) -> None:
    if shutil.which(executable) is not None:
        return
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pytest.fail(f"hosted CI must install {package}; missing executable: {executable}")
    pytest.skip(f"{package} integration requires the {executable} system executable")


@pytest.fixture
def native_tool_gate() -> Callable[[str, str], None]:
    return _require_native_tool


@pytest.fixture
def requires_tesseract() -> None:
    _require_native_tool("tesseract", "tesseract-ocr")


@pytest.fixture
def requires_soffice() -> None:
    _require_native_tool("soffice", "LibreOffice")
