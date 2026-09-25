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
* Status basis: The full plan is implemented, locally validated, pushed, and confirmed by hosted Python 3.12 CI with no test skips.

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

## Pre-Review Reconciliation

* Plan markers and task-local context: Current; all phases and tasks are complete.
* Completed-work entries and handoff prose: Current for the full declared scope.
* Validation, blockers, remaining work, and follow-up items: Validation is complete; no blockers, remaining work, or follow-up items.
* Review readiness: Ready for `/rpi-review`.

## Blockers

* None

## Remaining Work

* None

## Follow-Up Items

* Canonical plan list: [.copilot-tracking/plans/2026-09-25/spdx-tools-migration-plan.md](../../plans/2026-09-25/spdx-tools-migration-plan.md), `## Follow-Up Items`
* None

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: Full plan; P01 through P03 and all seven tasks complete
* Validation coverage: Hash-locked Linux resolution, focused official/contract/structural tests, repository validation, both local full-suite environments, real Syft output, diff hygiene, and hosted Python 3.12 CI
* Blockers: None
* Current plan updates: None
* Planning and critique state: Ready; `PC-001` and `PC-002` were resolved before implementation
* Follow-up items: None
* Review readiness or no-handoff reason: Ready for `/rpi-review`
* Continuation owner: Review stage
