#!/usr/bin/env python3
"""Validate repository-owned release SBOM requirements."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
PACKAGE_PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([^<>=!~\s]+)$")
SOURCE_SUPPLIER = "Organization: benarculus"


def normalized_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def expected_runtime_packages() -> dict[str, str]:
    packages: dict[str, str] = {}
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = PACKAGE_PIN.fullmatch(stripped)
        if match is None:
            raise AssertionError(f"runtime requirement must be exactly pinned: {stripped}")
        packages[normalized_name(match.group(1))] = match.group(2)
    return packages


def validate_release_sbom_contract(path: Path, expected_version: str) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError("SBOM document must be a JSON object")
    packages = document.get("packages")
    if not isinstance(packages, list) or not packages:
        raise AssertionError("SBOM must contain package components")
    if any(not isinstance(package, dict) for package in packages):
        raise AssertionError("SBOM packages must be objects")
    observed_packages: dict[str, list[dict[str, object]]] = {}
    for package in packages:
        name = package.get("name")
        if isinstance(name, str) and name:
            observed_packages.setdefault(normalized_name(name), []).append(package)
    source_packages = [
        package
        for package in packages
        if package.get("name") == "resume-builder"
    ]
    if len(source_packages) != 1:
        raise AssertionError("SBOM must contain exactly one resume-builder root package")
    source_package = source_packages[0]
    if source_package.get("versionInfo") != expected_version:
        raise AssertionError(f"SBOM source version must be {expected_version}")
    if (
        source_package.get("supplier") != SOURCE_SUPPLIER
        or source_package.get("originator") != SOURCE_SUPPLIER
    ):
        raise AssertionError("SBOM source package must identify the benarculus supplier and originator")
    misattributed = [
        package["name"]
        for name, matching_packages in observed_packages.items()
        if name != "resume-builder"
        for package in matching_packages
        if package.get("supplier") == SOURCE_SUPPLIER
    ]
    if misattributed:
        raise AssertionError(f"SBOM must not attribute dependencies to benarculus: {misattributed}")
    runtime_packages = expected_runtime_packages()
    invalid_runtime_packages = {
        name: {
            "expected_version": version,
            "observed_versions": [
                str(package.get("versionInfo", "")) for package in observed_packages.get(name, [])
            ],
        }
        for name, version in runtime_packages.items()
        if len(observed_packages.get(name, [])) != 1
        or str(observed_packages[name][0].get("versionInfo", "")) != version
    }
    if invalid_runtime_packages:
        raise AssertionError(
            "SBOM must contain exactly one package at each exact runtime version: "
            f"{invalid_runtime_packages}"
        )

    source_id = source_package.get("SPDXID")
    document_id = document.get("SPDXID")
    relationships = document.get("relationships")
    if not isinstance(relationships, list):
        raise AssertionError("SBOM must contain release relationships")
    describes = [
        relationship
        for relationship in relationships
        if isinstance(relationship, dict)
        and relationship.get("spdxElementId") == document_id
        and relationship.get("relationshipType") == "DESCRIBES"
        and relationship.get("relatedSpdxElement") == source_id
    ]
    if len(describes) != 1:
        raise AssertionError("SBOM document must describe exactly one resume-builder source package")
    unrelated_describes = [
        relationship
        for relationship in relationships
        if isinstance(relationship, dict)
        and relationship.get("spdxElementId") == document_id
        and relationship.get("relationshipType") == "DESCRIBES"
        and relationship.get("relatedSpdxElement") != source_id
    ]
    if unrelated_describes:
        raise AssertionError("SBOM document must not describe dependency packages")
    runtime_ids = {
        observed_packages[name][0]["SPDXID"] for name in runtime_packages
    }
    related_runtime_ids = {
        relationship.get("relatedSpdxElement")
        for relationship in relationships
        if isinstance(relationship, dict)
        and relationship.get("spdxElementId") == source_id
        and relationship.get("relationshipType") in {"CONTAINS", "DEPENDS_ON"}
    }
    if not runtime_ids <= related_runtime_ids:
        raise AssertionError("SBOM must relate every runtime package to resume-builder")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: validate_release_sbom_contract.py <sbom.spdx.json> <release-version>"
        )
    validate_release_sbom_contract(Path(sys.argv[1]), sys.argv[2])
    print(f"Validated release SBOM contract for resume-builder {sys.argv[2]}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError) as error:
        print(f"Release SBOM contract validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
