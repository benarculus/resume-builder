from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_VALIDATOR = ROOT / "scripts/validate_release_sbom_contract.py"
PREPARER = ROOT / "scripts/prepare_spdx_sbom.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract_validator():
    return load_module("validate_release_sbom_contract", CONTRACT_VALIDATOR)


def load_preparer():
    return load_module("prepare_spdx_sbom", PREPARER)


def official_validator() -> str:
    executable = shutil.which("pyspdxtools")
    if executable:
        return executable
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pytest.fail("hosted CI must install and run the official SPDX validator")
    pytest.skip("official SPDX integration requires the Python 3.12 validation environment")


def spdx_document() -> dict:
    packages = [
        {
            "name": "resume-builder",
            "SPDXID": "SPDXRef-Package-resume-builder",
            "versionInfo": "0.2.0",
            "supplier": "NOASSERTION",
            "originator": "NOASSERTION",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
        }
    ]
    packages.extend(
        {
            "name": name,
            "SPDXID": f"SPDXRef-Package-{name}",
            "versionInfo": version,
            "supplier": "NOASSERTION",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
        }
        for name, version in load_contract_validator().expected_runtime_packages().items()
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
        "documentNamespace": (
            "https://github.com/benarculus/resume-builder/releases/tag/v0.2.0"
        ),
        "creationInfo": {
            "created": "2026-09-25T14:00:00Z",
            "creators": ["Tool: syft"],
        },
        "packages": packages,
        "relationships": relationships,
    }


def write_prepared_document(tmp_path: Path, document: dict | None = None) -> Path:
    path = tmp_path / "resume-builder.spdx.json"
    path.write_text(json.dumps(document or spdx_document()), encoding="utf-8")
    load_preparer().prepare_spdx_sbom(path, "0.2.0")
    return path


def run_official_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [official_validator(), "-i", str(path), "--version", "SPDX-2.3"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_official_spdx_validator_accepts_release_fixture(tmp_path: Path) -> None:
    result = run_official_validator(write_prepared_document(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "mutate",
    [
        lambda document: document["creationInfo"].update({"created": 42}),
        lambda document: document["creationInfo"].update({"creators": "Tool: syft"}),
        lambda document: document["creationInfo"].update({"creators": [42]}),
        lambda document: document.update({"spdxVersion": "SPDX-2.2"}),
        lambda document: document["packages"][1].update(
            {"SPDXID": "SPDXRef-Package-resume-builder"}
        ),
        lambda document: document["packages"][1].pop("downloadLocation"),
    ],
    ids=[
        "integer-created",
        "string-creators",
        "invalid-creator-array",
        "wrong-spdx-version",
        "duplicate-spdxid",
        "missing-download-location",
    ],
)
def test_official_spdx_validator_rejects_specification_violations(
    tmp_path: Path, mutate
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    path.write_text(json.dumps(document), encoding="utf-8")

    assert run_official_validator(path).returncode != 0


def test_release_contract_accepts_prepared_sbom(tmp_path: Path) -> None:
    load_contract_validator().validate_release_sbom_contract(
        write_prepared_document(tmp_path), "0.2.0"
    )


def test_release_contract_rejects_wrong_release_version(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="source version"):
        load_contract_validator().validate_release_sbom_contract(
            write_prepared_document(tmp_path), "0.3.0"
        )


def test_release_contract_rejects_duplicate_root_package(tmp_path: Path) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    duplicate = dict(document["packages"][0])
    duplicate["SPDXID"] = "SPDXRef-Package-resume-builder-duplicate"
    duplicate["versionInfo"] = "9.9.9"
    document["packages"].append(duplicate)
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="exactly one resume-builder"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


@pytest.mark.parametrize("field", ["supplier", "originator"])
def test_release_contract_rejects_invalid_root_attribution(
    tmp_path: Path, field: str
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["packages"][0][field] = "NOASSERTION"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="supplier and originator"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


def test_release_contract_rejects_dependency_supplier_misattribution(
    tmp_path: Path,
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["packages"][1]["supplier"] = "Organization: benarculus"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="must not attribute dependencies"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


@pytest.mark.parametrize("conflicting_first", [True, False])
def test_release_contract_rejects_duplicate_runtime_version(
    tmp_path: Path, conflicting_first: bool
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    runtime_package = document["packages"][1]
    duplicate = dict(runtime_package)
    duplicate["SPDXID"] = f"{runtime_package['SPDXID']}-duplicate"
    duplicate["versionInfo"] = "999.0"
    insert_at = 1 if conflicting_first else 2
    document["packages"].insert(insert_at, duplicate)
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="exactly one package"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


@pytest.mark.parametrize("misattributed_first", [True, False])
def test_release_contract_rejects_duplicate_runtime_supplier_misattribution(
    tmp_path: Path, misattributed_first: bool
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    runtime_package = document["packages"][1]
    duplicate = dict(runtime_package)
    duplicate["SPDXID"] = f"{runtime_package['SPDXID']}-duplicate"
    duplicate["supplier"] = "Organization: benarculus"
    insert_at = 1 if misattributed_first else 2
    document["packages"].insert(insert_at, duplicate)
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="must not attribute dependencies"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


def test_release_contract_rejects_missing_runtime_package(tmp_path: Path) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["packages"] = [
        package for package in document["packages"] if package["name"] != "pymupdf"
    ]
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="exact runtime version"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


def test_release_contract_rejects_missing_runtime_relationship(tmp_path: Path) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["relationships"] = [
        relationship
        for relationship in document["relationships"]
        if relationship.get("relatedSpdxElement") != "SPDXRef-Package-pymupdf"
    ]
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="relate every runtime package"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")


def test_release_contract_requires_one_document_root_relationship(
    tmp_path: Path,
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["relationships"].append(dict(document["relationships"][0]))
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(AssertionError, match="describe exactly one"):
        load_contract_validator().validate_release_sbom_contract(path, "0.2.0")
