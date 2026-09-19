#!/usr/bin/env python3
"""Validate and load the shared job-requirements artifact contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_ARRAYS = ("requiredQualifications", "preferredQualifications", "responsibilities")


def parse_job_requirements(path: Path | str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    if not isinstance(artifact, dict):
        raise ValueError("job requirements must be a JSON object")
    source = artifact.get("source")
    if not isinstance(source, dict) or not source.get("url"):
        raise ValueError("job requirements must include source.url")
    for key in REQUIRED_ARRAYS:
        items = artifact.get(key)
        if not isinstance(items, list):
            raise ValueError(f"{key} must be an array")
        for item in items:
            if not isinstance(item, dict) or not item.get("id") or not item.get("text") or not item.get("source"):
                raise ValueError(f"{key} items require id, text, and source")
    if not isinstance(artifact.get("constraints"), dict):
        raise ValueError("constraints must be an object")
    return artifact
