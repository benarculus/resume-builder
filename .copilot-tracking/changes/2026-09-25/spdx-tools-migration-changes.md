<!-- markdownlint-disable-file -->
# RPI Changes: SPDX tools migration

## Metadata

* Task ID: SPDX-TOOLS-MIGRATION-2026-09-25
* Related plan: [.copilot-tracking/plans/2026-09-25/spdx-tools-migration-plan.md](../../plans/2026-09-25/spdx-tools-migration-plan.md)
* Implementation date: 2026-09-25

## Execution Status

* Status: Complete
* Declared invocation scope: Full plan
* Completed scope markers: P01, P01-T01, P01-T02, P02, P02-T01, P02-T02, P03, P03-T01, P03-T02, P03-T03
* All remaining active-plan markers: None
* Status basis: The original full plan and both accepted review corrections are implemented, pushed, and confirmed by hosted Python 3.12 CI with no skips.

## Execution Summary

The release pipeline now installs official `spdx-tools==0.8.5` from a complete Python 3.12/Linux wheel hash lock, validates generated SBOMs for SPDX 2.3 conformance, and then applies a smaller stdlib-only repository release contract before artifact upload.

## Completed Work

### P01: Established the deterministic official validator environment

* Added `requirements-spdx-validation.txt` with exact versions and reviewed SHA-256 hashes for all 13 Python 3.12/Linux artifacts.
* Added semantic repository validation for the complete lock, exact hashes, Python 3.12 setup, and the required binary-only hash-enforcing install command in hosted CI.
* Confirmed the lock with a cross-platform Linux CPython 3.12 wheel download using pip's hash enforcement.

### P02: Separated SPDX conformance from release policy

* Replaced `scripts/validate_spdx_sbom.py` with `scripts/validate_release_sbom_contract.py`.
* Moved creation metadata, package field/type, identifier uniqueness, URI/license, and other specification checks to official `pyspdxtools`.
* Retained exactly one root package, release version, supplier/originator, dependency attribution, exact runtime pins, one document-to-root `DESCRIBES`, and root-to-runtime relationships in repository code.
* Partitioned `tests/test_spdx_sbom.py` into five official CLI integration cases and focused repository-contract unit mutations.

### P03: Wired and protected the two-gate publication boundary

* Added SHA-pinned Python 3.12 setup and the exact locked install to the read-only release generation job.
* Ordered generation → preparation → official SPDX 2.3 validation → repository contract validation → upload.
* Extended structural mutations for dependency/version/hash drift, CI install weakening, gate reordering, and obsolete validator restoration.
* Updated README, historical release-pipeline evidence, and the PR body source.

## Implementation-Time Plan Updates

* None

## Accepted Review Finding Implementation

### Addressing round-three CR-001: Reject ambiguous duplicate runtime packages

* Related scope: P02-T02, P03-T02
* Planned behavior: the release contract will preserve every package entry per normalized name, reject missing or duplicate required runtime names, require the exact pinned version, and inspect supplier attribution across every entry.
* Affected files: [scripts/validate_release_sbom_contract.py](../../../scripts/validate_release_sbom_contract.py), [tests/test_spdx_sbom.py](../../../tests/test_spdx_sbom.py)
* Behavior or functionality changed: required runtime packages must now appear exactly once at the pinned version. Duplicate version and supplier-attribution mutations cover both orders so a valid later entry cannot hide a conflicting earlier entry.
* Validation: Focused suite passed with 89 tests and 7 expected local official-validator skips; the full local suite passed with 108 tests and 15 environment skips.
* Status: Implemented locally; hosted Python 3.12/Linux confirmation remains pending.

### Addressing round-three CR-002: Fail closed for already-published releases

* Related scope: P03-T02, P03-T03
* Planned behavior: a workflow rerun may reuse a draft, but must not infer validated publication from the presence of a same-name immutable release asset.
* Affected files: [.github/workflows/publish-release.yml](../../../.github/workflows/publish-release.yml), [scripts/validate_repo.py](../../../scripts/validate_repo.py), [tests/test_structure.py](../../../tests/test_structure.py), [README.md](../../../README.md)
* Behavior or functionality changed: the resolver now fails when the release is already public. Repository validation rejects restoration of `state=published` or asset-name-based success, and a structural mutation recreates the forged same-name asset bypass.
* Validation: Repository validation and diff hygiene passed; the focused and full local suites passed.
* Status: Implemented locally; hosted workflow confirmation remains pending.

### Addressing RV-001: Protect validator failure and dependency isolation

* Related scope: P01-T02, P03-T02
* Planned behavior: repository validation will reject truthy `continue-on-error` on either release SBOM validator, reject `spdx-tools` in general requirement files, and exercise every required structural weakening class through focused mutations.
* Affected files: [scripts/validate_repo.py](../../../scripts/validate_repo.py), [tests/test_structure.py](../../../tests/test_structure.py)
* Behavior or functionality changed: repository validation now rejects any `continue-on-error` field on either release SBOM validator and rejects `spdx-tools` in `requirements.txt` or `requirements-dev.txt`. Structural mutations now cover required-step removal, Python runtime drift, hash/binary install weakening, official-version relaxation, contract bypass, upload-before-gate ordering, and both validator bypass cases.
* Validation: Passed locally with the repository validator and the focused Python 3.12 suite.
* Status: Complete

### Addressing RV-002: Complete official conformance mutations

* Related scope: P02-T02
* Planned behavior: official CLI integration will reject a non-2.3 document and an invalid creator array in addition to the existing creation metadata and package mutations.
* Affected file: [tests/test_spdx_sbom.py](../../../tests/test_spdx_sbom.py)
* Behavior or functionality changed: the official CLI mutation matrix now also rejects an SPDX 2.2 document under the required SPDX 2.3 command and rejects a creator array containing a non-string entry.
* Validation: Passed under Python 3.12 with official `spdx-tools==0.8.5`; hosted Python 3.12 CI confirmed all cases without skips.
* Status: Complete

## Validation Record

| Check | Scope | Status | Evidence or reason |
|-------|-------|--------|--------------------|
| Baseline workspace review | Full plan | Passed | Existing source is unchanged since the last pushed CCR remediation; only the approved research, plan, and critique artifacts are untracked |
| Linux wheel lock | P01 | Passed | `pip download --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp --abi cp312 --only-binary=:all: --require-hashes -r requirements-spdx-validation.txt` verified all 13 artifacts |
| Focused official and structural suite | P01-P03 | Passed | Python 3.12 with `pyspdxtools` on `PATH`: 73 passed, no skips |
| Repository validator | P01-P03 | Passed | `python3 scripts/validate_repo.py` |
| Local full suite | P02-P03 | Passed | Python 3.12: 92 passed, 8 system-binary skips; Python 3.9: 87 passed, 13 expected skips |
| Real generated SBOM | P02-P03 | Passed | Checksummed Syft `v1.52.0` generated the repository SBOM; preparation, official SPDX 2.3 validation, and the release contract all passed |
| Hosted required check | P01-P03 | Passed | GitHub Actions run `36183317898`: hash-locked install succeeded and pytest reported 100 passed with no skips |
| Diff hygiene | Full plan | Passed | `git diff --check` |
| Accepted review corrections | RV-001 and RV-002 | Passed locally | `python3 scripts/validate_repo.py`; focused Python 3.12 suite: 91 passed with no skips; full Python 3.12 suite: 110 passed, 8 system-binary skips; `git diff --check` |
| Hosted correction confirmation | RV-001 and RV-002 | Passed | GitHub Actions run `36185010191`: hash-locked `spdx-tools==0.8.5` install succeeded and pytest reported 118 passed with no skips |
| Round-three finding remediation | CR-001 and CR-002 | Passed locally | Repository validator; focused suite: 89 passed with 7 expected local official-validator skips; full suite: 108 passed with 15 environment skips; Python compilation; diff hygiene |
| Local Python 3.12 official-validator attempt | CR-001 | Correctly blocked by platform lock | The reviewed lock is Linux-only; pip rejected the macOS ARM PyYAML wheel hash rather than weakening `--require-hashes`. Hosted Linux remains authoritative. |

## Pre-Review Reconciliation

* Plan markers and task-local context: Current; all phases and tasks are complete.
* Completed-work entries and handoff prose: Current for the full declared scope.
* Validation, blockers, remaining work, and follow-up items: Round-three findings pass targeted and full local validation. Hosted Python 3.12/Linux confirmation and the first production release lifecycle remain pending.
* Review readiness: The two round-three findings are resolved in the working tree and need refreshed hosted checks after the changes are pushed.

## Blockers

* Refreshed hosted Python 3.12/Linux CI for the round-three remediation.

## Remaining Work

* Treat the first production tag-to-draft-to-immutable lifecycle as operational acceptance; this cannot execute before the workflow is merged to `main`.

## Follow-Up Items

* Canonical plan list: [.copilot-tracking/plans/2026-09-25/spdx-tools-migration-plan.md](../../plans/2026-09-25/spdx-tools-migration-plan.md), `## Follow-Up Items`
* None

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: Full plan; P01 through P03 and all seven tasks complete
* Validation coverage: Prior hosted validation remains green; round-three remediation passed repository validation, 89 focused tests with 7 expected local official-validator skips, 108 full-suite tests with 15 environment skips, Python compilation, and diff hygiene
* Blockers: None
* Current plan updates: None
* Planning and critique state: Ready; `PC-001` and `PC-002` were resolved before implementation
* Follow-up items: Refreshed hosted Linux CI and the first production release operational acceptance
* Review readiness or no-handoff reason: Ready to push and refresh hosted checks; both review findings are resolved locally
* Continuation owner: User
