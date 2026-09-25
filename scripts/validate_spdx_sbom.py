#!/usr/bin/env python3
"""Validate the release SPDX SBOM contract."""

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


def validate_spdx_sbom(path: Path, expected_version: str) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError("SBOM document must be a JSON object")
    if document.get("spdxVersion") != "SPDX-2.3":
        raise AssertionError("SBOM must use SPDX 2.3")
    if document.get("dataLicense") != "CC0-1.0":
        raise AssertionError("SBOM must use the SPDX CC0-1.0 data license")
    if document.get("SPDXID") != "SPDXRef-DOCUMENT":
        raise AssertionError("SBOM must identify the SPDX document")
    if document.get("name") != "resume-builder":
        raise AssertionError("SBOM source name must be resume-builder")
    if not str(document.get("documentNamespace", "")).startswith("https://"):
        raise AssertionError("SBOM must include a globally unique HTTPS namespace")

    creation = document.get("creationInfo")
    if not isinstance(creation, dict) or not creation.get("created") or not creation.get("creators"):
        raise AssertionError("SBOM must include author and creation timestamp metadata")

    packages = document.get("packages")
    if not isinstance(packages, list) or not packages:
        raise AssertionError("SBOM must contain package components")
    incomplete = [
        package.get("name", "<unnamed>") if isinstance(package, dict) else "<non-object>"
        for package in packages
        if not isinstance(package, dict)
        or not all(
            isinstance(package.get(field), str) and package[field].strip()
            for field in ("name", "SPDXID", "supplier")
        )
    ]
    if incomplete:
        raise AssertionError(f"SBOM packages must include identifiers and suppliers: {incomplete}")
    package_ids = [package["SPDXID"] for package in packages if isinstance(package, dict)]
    duplicate_ids = sorted(
        spdx_id for spdx_id in set(package_ids) if package_ids.count(spdx_id) > 1
    )
    document_id = document["SPDXID"]
    if document_id in package_ids:
        duplicate_ids.append(document_id)
    if duplicate_ids:
        raise AssertionError(
            f"SBOM element identifiers must be unique: {sorted(set(duplicate_ids))}"
        )
    observed_packages = {
        normalized_name(package["name"]): package
        for package in packages
        if isinstance(package, dict) and package.get("name")
    }
    source_package = observed_packages.get("resume-builder", {})
    source_version = str(source_package.get("versionInfo", ""))
    if source_version != expected_version:
        raise AssertionError(
            f"SBOM source version must be {expected_version}, found {source_version or 'missing'}"
        )
    if source_package.get("supplier") != SOURCE_SUPPLIER:
        raise AssertionError("SBOM source package must identify the benarculus supplier")
    misattributed = [
        package["name"]
        for name, package in observed_packages.items()
        if name != "resume-builder" and package.get("supplier") == SOURCE_SUPPLIER
    ]
    if misattributed:
        raise AssertionError(f"SBOM must not attribute dependencies to benarculus: {misattributed}")
    missing = {
        name: version
        for name, version in expected_runtime_packages().items()
        if str(observed_packages.get(name, {}).get("versionInfo", "")) != version
    }
    if missing:
        raise AssertionError(f"SBOM is missing exact runtime package versions: {missing}")

    source_id = source_package["SPDXID"]
    relationships = document.get("relationships")
    if not isinstance(relationships, list) or not any(
        relationship.get("spdxElementId") == document["SPDXID"]
        and relationship.get("relationshipType") == "DESCRIBES"
        and relationship.get("relatedSpdxElement") == source_id
        for relationship in relationships
        if isinstance(relationship, dict)
    ):
        raise AssertionError("SBOM must describe its source package")
    runtime_ids = {
        observed_packages[name]["SPDXID"] for name in expected_runtime_packages()
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
        raise SystemExit("usage: validate_spdx_sbom.py <sbom.spdx.json> <release-version>")
    validate_spdx_sbom(Path(sys.argv[1]), sys.argv[2])
    print(f"Validated SPDX SBOM for resume-builder {sys.argv[2]}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError) as error:
        print(f"SPDX SBOM validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
