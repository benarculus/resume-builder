from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_spdx_sbom.py"
PREPARER = ROOT / "scripts/prepare_spdx_sbom.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_validator():
    return load_module("validate_spdx_sbom", VALIDATOR)


def load_preparer():
    return load_module("prepare_spdx_sbom", PREPARER)


def spdx_document() -> dict:
    packages = [
        {
            "name": "resume-builder",
            "SPDXID": "SPDXRef-Package-resume-builder",
            "versionInfo": "0.2.0",
            "supplier": "NOASSERTION",
        }
    ]
    packages.extend(
        {
            "name": name,
            "SPDXID": f"SPDXRef-Package-{name}",
            "versionInfo": version,
            "supplier": "NOASSERTION",
        }
        for name, version in load_validator().expected_runtime_packages().items()
    )
    relationships = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": "SPDXRef-Package-resume-builder",
        }
    ]
    relationships.extend(
        {
            "spdxElementId": "SPDXRef-Package-resume-builder",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": package["SPDXID"],
        }
        for package in packages
        if package["name"] != "resume-builder"
    )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "resume-builder",
        "documentNamespace": "https://github.com/benarculus/resume-builder/releases/tag/v0.2.0",
        "creationInfo": {
            "created": "2026-09-25T14:00:00Z",
            "creators": ["Tool: syft"],
        },
        "packages": packages,
        "relationships": relationships,
    }


def test_spdx_validator_accepts_release_contract(tmp_path: Path) -> None:
    validator = load_validator()
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(spdx_document()), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")

    validator.validate_spdx_sbom(path, "0.2.0")


def test_spdx_validator_rejects_missing_runtime_package(tmp_path: Path) -> None:
    validator = load_validator()
    document = spdx_document()
    document["packages"] = [
        package for package in document["packages"] if package["name"] != "pymupdf"
    ]
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")

    with pytest.raises(AssertionError, match="runtime package versions"):
        validator.validate_spdx_sbom(path, "0.2.0")


def test_spdx_validator_rejects_wrong_release_version(tmp_path: Path) -> None:
    validator = load_validator()
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(spdx_document()), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")

    with pytest.raises(AssertionError, match="source version"):
        validator.validate_spdx_sbom(path, "0.3.0")


def test_spdx_validator_rejects_dependency_supplier_misattribution(tmp_path: Path) -> None:
    validator = load_validator()
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(spdx_document()), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")
    document = json.loads(path.read_text(encoding="utf-8"))
    dependency = next(
        package for package in document["packages"] if package["name"] == "python-docx"
    )
    dependency["supplier"] = "Organization: benarculus"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="must not attribute dependencies"):
        validator.validate_spdx_sbom(path, "0.2.0")


def test_spdx_validator_rejects_missing_runtime_relationship(tmp_path: Path) -> None:
    validator = load_validator()
    document = spdx_document()
    document["relationships"] = [
        relationship
        for relationship in document["relationships"]
        if relationship.get("relatedSpdxElement") != "SPDXRef-Package-pymupdf"
    ]
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")

    with pytest.raises(AssertionError, match="relate every runtime package"):
        validator.validate_spdx_sbom(path, "0.2.0")


def test_spdx_validator_rejects_document_describing_dependency(tmp_path: Path) -> None:
    validator = load_validator()
    document = spdx_document()
    describes = next(
        relationship
        for relationship in document["relationships"]
        if relationship["relationshipType"] == "DESCRIBES"
    )
    describes["relatedSpdxElement"] = "SPDXRef-Package-python-docx"
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")

    with pytest.raises(AssertionError, match="describe its source package"):
        validator.validate_spdx_sbom(path, "0.2.0")
