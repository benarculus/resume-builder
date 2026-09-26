<!-- markdownlint-disable-file -->
# RPI Plan Critique: SPDX tools migration

## Metadata

* Task ID: SPDX-TOOLS-MIGRATION-2026-09-25
* Critique date: 2026-09-25
* Plan: `.copilot-tracking/plans/2026-09-25/spdx-tools-migration-plan.md`
* Critique execution status: Complete
* Critique depth: standard
* Depth provenance: default
* Invocation consumed: yes
* Attempt ID and kind: `SPDX-TOOLS-MIGRATION-2026-09-25-INITIAL-01`, initial
* Candidate identity and saved hash boundary: SHA-256 `af6fe56c5b01fe6c420f498294133bfb6af47b40584704941afb5ab6ca20b629` before reservation metadata
* Current-run provenance: immediate uninterrupted planner reservation-to-activation
* Original attempt and recovery approval: Not applicable

## Inputs and Criterion Boundary

* Task context and caller requirements: Migrate SPDX 2.3 conformance to pinned official `spdx-tools`, reduce the custom validator to repository release policy, and preserve the hardened release-publication boundary in PR #16.
* Research and evidence considered: `.copilot-tracking/research/2026-09-25/spdx-tools-migration-research.md`, `.github/workflows/publish-release.yml`, `.github/workflows/ci.yml`, `scripts/validate_spdx_sbom.py`, `scripts/prepare_spdx_sbom.py`, `tests/test_spdx_sbom.py`, `scripts/validate_repo.py`, `tests/test_structure.py`, `requirements.txt`, `requirements-dev.txt`, and `.github/dependabot.yml`.
* Decisions, dependencies, task Goals, and task Requirements considered: D1-D3; FR-001 through FR-008; NFR-001 through NFR-005; P01-T01 through P03-T03; Python 3.12, `spdx-tools==0.8.5`, the binary-only hash lock, existing Syft generation, and the retained release permission/job boundary.
* Assessment boundary: This critique assesses whether the supplied plan is credible and complete enough to implement the selected migration. It does not select a different architecture, regenerate dependency hashes, or perform additional research.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| D1-D3, FR-003 through FR-006, NFR-001 through NFR-003, P01-T01, P02-T01, P03-T01, P03-T02 | Covered | The plan fixes the responsibility boundary, exact removal, lock contract, job permissions, validation ordering, and structural mutation ownership. |
| FR-001, FR-002, FR-007, NFR-004, P01-T02, P02-T02 | Partial | The plan requires official integration tests under Python 3.12 but does not require `.github/workflows/ci.yml` to install the validation lock, so the ordinary hosted test job can skip the new gate rather than exercise it. |
| FR-007, NFR-004, P02-T02, P03-T03 | Partial | The plan requires acceptance of a generated/enriched Syft artifact but does not identify whether this is a checked fixture or an on-demand generation lane, nor how Syft 1.52.0 is made available to that test owner. |
| FR-008, NFR-005, P03-T03 | Covered | Documentation, changes evidence, PR body synchronization, CCR resolution, local checks, real-output evidence, and hosted checks are named. |

## Verdict

* Verdict: Revise
* Rationale: The architecture and release boundary are credible, but the plan leaves the official-validation tests optional in the normal hosted CI lane and leaves the real Syft compatibility artifact without a concrete owner. Both gaps can be corrected directly without changing the selected architecture or requiring user input.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: Hosted CI can pass while skipping official SPDX integration tests

* Related IDs: FR-001, FR-002, FR-007, NFR-004, P01-T02, P02-T02
* Evidence: `.copilot-tracking/plans/2026-09-25/spdx-tools-migration-plan.md` keeps `spdx-tools` out of `requirements-dev.txt`, permits the official integration cases to skip when the tool is unavailable, and adds the lock installation only to the release `generate` job under P03-T01. The existing `.github/workflows/ci.yml` installs only `requirements-dev.txt` before running the full tests.
* Concern: Nothing requires the ordinary hosted Python 3.12 CI job to install `requirements-spdx-validation.txt`. The test suite can therefore report success with all official conformance mutations skipped, leaving the new gate exercised only by a tag-triggered release workflow or manual evidence.
* Impact: PRs could merge changes that break official-validator invocation, fixture compatibility, or CCR mutation rejection even though the required `validate` branch check passes.
* Smallest useful change: Add a binding P01-T02 or P02-T02 requirement that `.github/workflows/ci.yml` installs the validation lock with the same hash/binary-only command before pytest, and add structural mutation coverage that removal or weakening of this CI install causes failure.
* Action owner: Planning parent
* Exact resolving evidence: The plan explicitly assigns `.github/workflows/ci.yml` lock installation and corresponding structural mutation coverage to a task, while preserving `requirements-dev.txt` isolation and Python 3.12.
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [Medium]: Real Syft compatibility lacks an implementation-owned test form

* Related IDs: FR-007, NFR-004, P02-T02, P03-T03
* Evidence: P02-T02 requires official validation to accept “a generated/enriched Syft artifact,” while P03-T03 requires a real checksum-verified Syft 1.52.0 validation run. No task states whether the automated test consumes a committed sanitized fixture, generates an artifact during CI, or relies only on the implementation evidence run.
* Concern: The implementer cannot tell whether Syft must be provisioned in ordinary CI, whether a generated fixture may be committed, or whether the real-output run is intentionally separate from regression tests.
* Impact: Implementation may either add an unnecessary tool download to every PR, omit durable compatibility regression coverage, or create a fixture without a refresh/provenance contract.
* Smallest useful change: Define the split explicitly: keep focused official CLI mutations in ordinary CI using the synthetic valid fixture, and make the checksum-verified Syft 1.52.0 generate → prepare → official validate → contract validate command an implementation/preflight evidence requirement rather than an automated pytest requirement; alternatively, specify a sanitized committed fixture and its refresh owner. The first option is smaller and matches the current plan's no-new-test-file boundary.
* Action owner: Planning parent
* Exact resolving evidence: P02-T02 and P03-T03 unambiguously assign synthetic integration coverage to hosted CI and real Syft generation to implementation evidence, with no unsupported Syft dependency implied for `.github/workflows/ci.yml`.
* Decision route: Direct planner correction

## Strengths and Residual Risk

* The plan correctly separates standards ownership from repository policy, preserves least privilege, forbids compatibility aliases, identifies exact file additions/removals, and protects validation ordering.
* Residual upstream-validator defects are appropriately treated as versioned dependency risk with focused mutations rather than a reason to duplicate the SPDX specification.

## Questions or Blocking Evidence Gaps

* None. Both findings are planner-owned corrections supported by the supplied evidence.

## Limitations

* Dependency hashes were not regenerated during critique; the plan appropriately assigns that evidence to implementation.
* Mermaid diagrams were assessed as plan structure, not rendered in light and dark UI themes.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: Planning parent
* Smallest next action: Revise P01-T02/P02-T02 to require hash-locked validator installation in hosted CI, then clarify P02-T02/P03-T03 ownership of synthetic versus real Syft compatibility evidence.
* User response required: No
