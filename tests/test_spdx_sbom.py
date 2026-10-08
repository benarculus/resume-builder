from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
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


def test_runtime_package_parser_returns_independent_normalized_pins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    validator = load_contract_validator()
    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        "# Runtime dependencies\n"
        "Python_DOCX==1.2.0\n"
        "Some.pkg_name==4.5.6\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "REQUIREMENTS", requirements)

    assert validator.expected_runtime_packages() == {
        "python-docx": "1.2.0",
        "some-pkg-name": "4.5.6",
    }


def test_runtime_package_parser_rejects_non_exact_pins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    validator = load_contract_validator()
    requirements = tmp_path / "requirements.txt"
    monkeypatch.setattr(validator, "REQUIREMENTS", requirements)
    invalid_lines = (
        "pillow",
        "pillow>=12.3.0",
        "pillow==12.3.0 # inline comment",
    )
    for invalid_line in invalid_lines:
        requirements.write_text(f"{invalid_line}\n", encoding="utf-8")
        with pytest.raises(
            AssertionError, match="runtime requirement must be exactly pinned"
        ):
            validator.expected_runtime_packages()


def test_release_contract_rejects_sbom_missing_independent_pillow_requirement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    validator = load_contract_validator()
    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        "python-docx==1.2.0\n"
        "pytesseract==0.3.13\n"
        "pymupdf==1.26.7\n"
        "pillow==12.3.0\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "REQUIREMENTS", requirements)

    expected_packages = {
        "python-docx": "1.2.0",
        "pytesseract": "0.3.13",
        "pymupdf": "1.26.7",
        "pillow": "12.3.0",
    }
    source_id = "SPDXRef-Package-resume-builder"
    packages = [
        {
            "name": "resume-builder",
            "SPDXID": source_id,
            "versionInfo": "0.2.0",
            "supplier": "Organization: benarculus",
            "originator": "Organization: benarculus",
        }
    ]
    packages.extend(
        {
            "name": name,
            "SPDXID": f"SPDXRef-Package-{name}",
            "versionInfo": version,
        }
        for name, version in expected_packages.items()
    )
    relationships = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": source_id,
        },
        *(
            {
                "spdxElementId": source_id,
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": package["SPDXID"],
            }
            for package in packages[1:]
        ),
    ]
    document = {
        "SPDXID": "SPDXRef-DOCUMENT",
        "packages": packages,
        "relationships": relationships,
    }
    assert {package["name"] for package in packages[1:]} == set(expected_packages)
    document["packages"] = [
        package for package in document["packages"] if package["name"] != "pillow"
    ]
    path = tmp_path / "missing-pillow.spdx.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(
        AssertionError, match="exactly one package at each exact runtime version"
    ):
        validator.validate_release_sbom_contract(path, "0.2.0")


@pytest.mark.parametrize(
    "scenario",
    ("missing", "duplicate", "wrong-version"),
    ids=("missing-root", "duplicate-root", "wrong-root-version"),
)
def test_preparer_rejects_invalid_source_metadata_without_changing_input(
    tmp_path: Path, scenario: str
) -> None:
    document = spdx_document()
    if scenario == "missing":
        document["packages"] = [
            package
            for package in document["packages"]
            if package["name"] != "resume-builder"
        ]
    elif scenario == "duplicate":
        document["packages"].append(dict(document["packages"][0]))
    else:
        document["packages"][0]["versionInfo"] = "0.3.0"
    path = tmp_path / "invalid-source.spdx.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    original_content = path.read_bytes()

    with pytest.raises(
        AssertionError,
        match="SBOM must contain exactly one matching resume-builder source package",
    ):
        load_preparer().prepare_spdx_sbom(path, "0.2.0")

    assert path.read_bytes() == original_content


def test_preparer_cli_reports_invalid_arguments_and_inputs(
    tmp_path: Path,
) -> None:
    malformed_json = tmp_path / "malformed.spdx.json"
    malformed_json.write_text("{", encoding="utf-8")
    missing_input = tmp_path / "missing.spdx.json"
    scenarios = (
        ([sys.executable, str(PREPARER)], "usage: prepare_spdx_sbom.py"),
        (
            [sys.executable, str(PREPARER), str(malformed_json), "0.2.0"],
            "SPDX SBOM preparation failed:",
        ),
        (
            [sys.executable, str(PREPARER), str(missing_input), "0.2.0"],
            "SPDX SBOM preparation failed:",
        ),
    )
    for command, diagnostic in scenarios:
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        assert result.returncode != 0
        assert diagnostic in result.stderr
        assert not result.stdout.strip()
        assert "Prepared SPDX SBOM metadata" not in result.stderr


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


@pytest.mark.parametrize("alias", ["resume_builder", "Resume.Builder", "RESUME-BUILDER"])
def test_release_contract_rejects_root_alias_supplier_misattribution(
    tmp_path: Path, alias: str
) -> None:
    path = write_prepared_document(tmp_path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["packages"].append(
        {
            "name": alias,
            "SPDXID": f"SPDXRef-Package-{alias}",
            "versionInfo": "9.9.9",
            "supplier": "Organization: benarculus",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
        }
    )
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
