#!/usr/bin/env python3
"""Add repository-owned product metadata to a generated SPDX SBOM."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SUPPLIER = "Organization: benarculus"


def prepare_spdx_sbom(path: Path, expected_version: str) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    packages = document.get("packages")
    if not isinstance(packages, list):
        raise AssertionError("SBOM must contain packages before enrichment")
    source_packages = [
        package
        for package in packages
        if isinstance(package, dict)
        and package.get("name") == "resume-builder"
        and str(package.get("versionInfo", "")) == expected_version
    ]
    if len(source_packages) != 1:
        raise AssertionError("SBOM must contain exactly one matching resume-builder source package")
    source_packages[0]["supplier"] = SUPPLIER
    source_packages[0]["originator"] = SUPPLIER
    path.write_text(f"{json.dumps(document, indent=2)}\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_spdx_sbom.py <sbom.spdx.json> <release-version>")
    prepare_spdx_sbom(Path(sys.argv[1]), sys.argv[2])
    print(f"Prepared SPDX SBOM metadata for resume-builder {sys.argv[2]}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError) as error:
        print(f"SPDX SBOM preparation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
