<!-- markdownlint-disable-file -->
# Review: SPDX tools migration

## Executive Summary

* Assessment: The implementation establishes the intended official SPDX 2.3 gate, reduced repository contract, deterministic dependency lock, hosted execution, and safe release ordering. Two acceptance gaps remain in the required regression and structural protection coverage.
* Why this matters: The current release workflow is fail-closed, but its repository guard does not reject a future `continue-on-error` bypass on either validator, and the official integration suite omits two explicitly required invalid-document classes.
* Review execution: Complete
* Assessed outcome: Defects found
* Validation coverage: The changes record supplies a verified Linux/Python 3.12 hash resolution, focused official/structural tests, local suites, a checksum-verified real Syft chain, diff hygiene, and hosted Python 3.12 CI with 100 tests and no skips.
* Confidence and limitations: High confidence in the two findings from direct comparison of the binding task requirements with current validator and test code. The review did not rerun validation and relies on the recorded hosted and implementation evidence for execution results.

The assessment above is the reviewer's proposal. Parent Decision Record contains the final decisions and next actions, or states that decisions are pending.

## What You May Not Know

The active `.github/workflows/publish-release.yml` contains no `continue-on-error`, so the implemented release path currently stops on validator failure. RV-001 concerns the required repository protection against a later weakening of that boundary, not an active bypass in the workflow.

## Findings and Proposed Routes

<!-- rpi:review id=RV-001 -->
### RV-001 [High]: Structural validation does not reject validator bypass or dependency-boundary drift

The repository validator protects exact validator commands and their order, but it does not reject `continue-on-error: true` on the official or repository-contract step. It also does not enforce the planned absence of `spdx-tools` from the general requirement files. Both protections were binding parts of P01-T02 and P03-T02.

* Related scope: FR-006, NFR-001, NFR-002, P01-T02, P03-T02
* Expected behavior: `scripts/validate_repo.py` and `tests/test_structure.py` must detect removal, weakening, reordering, or bypass of either validation gate, including `continue-on-error` on official validation, and must preserve the isolated validation dependency boundary.
* Observed behavior and evidence: `scripts/validate_repo.py` `validate_publish_release_workflow()` checks the exact `run` values for `official` and `contract` but never checks either step's `continue-on-error` field. A step can therefore retain the accepted command while allowing artifact upload after failure. `validate_spdx_validation_lock()` checks the lock and CI command but never reads `requirements.txt` or `requirements-dev.txt` to reject `spdx-tools` there. `tests/test_structure.py` has mutations for version/hash drift, removal of `--require-hashes`, ordering, and obsolete-script restoration, but none for validator `continue-on-error`, `--only-binary=:all:` removal, Python-version drift, contract bypass, upload-before-gate variants, or moving `spdx-tools` into a general requirements file.
* Impact: A future workflow edit could make official or repository validation advisory while repository validation and required CI still pass, allowing an invalid SBOM to reach artifact transfer. General dependency drift could also weaken the intended isolated, reproducible validator environment without a focused regression identifying it.
* Resolution condition: Repository validation fails when either validator has any truthy `continue-on-error` setting and when `spdx-tools` appears in either general requirements file; mutation tests demonstrate these cases and the other explicitly listed P01-T02/P03-T02 weakening classes.
* Proposed destination: `rpi-implement`
* Smallest useful next action: Extend the existing workflow/dependency checks and add focused mutations in `tests/test_structure.py`; do not change the current release architecture.

<!-- rpi:review id=RV-002 -->
### RV-002 [Medium]: Official conformance tests omit required version and creator-shape mutations

The official integration tests cover the original CCR type defect and several important SPDX failures, but the matrix does not contain all invalid classes required by P02-T02.

* Related scope: FR-007, NFR-004, P02-T02
* Expected behavior: Official CLI integration must reject an SPDX version other than 2.3 and both a non-array and an invalid `creationInfo.creators` value, while accepting the synthetic fixture in hosted Python 3.12.
* Observed behavior and evidence: `tests/test_spdx_sbom.py` exercises integer `created`, string `creators`, duplicate identifiers, and missing `downloadLocation`. It has no mutation changing `spdxVersion` away from `SPDX-2.3` and no invalid creator-array element case. The release workflow correctly passes `--version SPDX-2.3`, and hosted evidence confirms the existing cases ran, but the explicit acceptance matrix is incomplete.
* Impact: The selected official CLI contract is present, but regressions in its version constraint or creator-array semantic validation would not be detected by the repository's required focused suite.
* Resolution condition: The existing official subprocess parameterization includes a non-2.3 document and an invalid creator array, and hosted Python 3.12 evidence shows both fail nonzero without skips.
* Proposed destination: `rpi-implement`
* Smallest useful next action: Add the two missing mutations to `tests/test_spdx_sbom.py` and confirm them in the required hosted check.

## Parent Decision Record

<!-- Decisions live here. Append events; never rewrite the evidence body above to fit a decision. -->

### Current Disposition

* Based on events: RD-001, RD-002, RD-003, RD-004, RD-005, RD-006, RD-007
* Review execution: Complete
* Final outcome: Defects found; both accepted defects route to one targeted `rpi-implement` continuation.
* Finding decisions and next actions: RV-001 accepted for structural bypass/dependency-boundary protection; RV-002 accepted for the missing official mutation cases.
* Decisions still needed: None.

This summary is derived from Decision History, not a second decision record. The latest event for each subject governs; refresh this summary after appending decisions and on recovery.

### Decision History

| Event | Subject | Decision source | Status or value | Proposed destination | Final destination | Owner | More information needed | Smallest next action | Rationale |
|-------|---------|-----------------|-----------------|----------------------|-------------------|-------|-------------------------|----------------------|-----------|
| RD-001 | participation | user | user-owned | none | none | review parent | none | Complete the evidence comparison, then ask about each actionable finding separately | This is a standalone manual `/rpi-review` invocation, so final route decisions remain user-owned |
| RD-002 | review execution | review parent | Complete | none | none | review parent | none | Resolve finding routes | The full supplied acceptance boundary was compared once and the record contains the complete supported finding set |
| RD-003 | outcome | review parent | Defects found | none | pending finding decisions | user | none | Decide RV-001, then RV-002 | Two implementation defects remain in binding structural and test coverage requirements |
| RD-004 | RV-001 | user | accepted | `rpi-implement` | `rpi-implement` | implementation stage | none | Add validator-bypass, dependency-boundary, and required structural mutation protections | User selected the suggested targeted implementation route |
| RD-005 | RV-002 | user | accepted | `rpi-implement` | `rpi-implement` | implementation stage | none | Add non-2.3 and invalid creator-array official subprocess mutations and obtain hosted evidence | User selected the suggested targeted implementation route |
| RD-006 | walkthrough | user | completed | none | none | review parent | none | Finalize the review route projection | Both actionable findings were presented and decided separately |
| RD-007 | continuation | review parent | targeted correction required | `rpi-implement` | `rpi-implement` | user / implementation stage | none | Run `/rpi-implement` with `.copilot-tracking/changes/2026-09-25/spdx-tools-migration-changes.md` for RV-001 and RV-002 | Both accepted findings fit the current architecture and require no new planning or research |

## Validation Evidence

| Command | Scope | Status | Summary |
|---------|-------|--------|---------|
| `pip download --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp --abi cp312 --only-binary=:all: --require-hashes -r requirements-spdx-validation.txt` | P01 dependency lock | Passed | Changes record reports all 13 reviewed artifacts verified |
| Python 3.12 focused suite with `pyspdxtools` on `PATH` | P01-P03 | Passed | Changes record reports 73 passed with no skips |
| `python3 scripts/validate_repo.py` | Repository structural contract | Passed | Changes record reports successful repository validation |
| Full suites | P02-P03 | Passed with explicit local limitations | Python 3.12: 92 passed and 8 system-binary skips; Python 3.9: 87 passed and 13 expected skips |
| Checksummed Syft 1.52.0 generate → prepare → official validate → contract validate | Real release artifact compatibility | Passed | Changes record reports all four stages succeeded |
| GitHub Actions run `36183317898` | Hosted Python 3.12 required check | Passed | Hash-locked install succeeded and pytest reported 100 passed with no skips |
| `git diff --check` | Full implementation | Passed | Changes record reports no whitespace errors |

## Risks, Blockers, and Residual Work

* Blockers: None; the review completed credibly.
* Remaining active work: None in the completed implementation record; accepted review findings would become later targeted implementation work rather than reopening this Review.
* Residual work: None distinct from RV-001 and RV-002.

## Review Record

### Scope and Evidence

* Task ID: SPDX-TOOLS-MIGRATION-2026-09-25
* Review date: 2026-09-25
* Review scope: Full task
* Assessed boundary: P01 through P03 and P01-T01 through P03-T03, including the deterministic validator environment, conformance/policy separation, release-workflow integration, structural protection, documentation, and recorded validation.
* Review depth and provenance: standard; default because the user did not request deep review
* Candidate identity: SPDX-TOOLS-MIGRATION-2026-09-25 full-task implementation at PR #16 head after commits `260f98a` and `3bf98ac`
* Review execution: Complete
* Helper use: None
* Plan: .copilot-tracking/plans/2026-09-25/spdx-tools-migration-plan.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-25/spdx-tools-migration-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-25/spdx-tools-migration-changes.md
* Other evidence considered: .copilot-tracking/research/2026-09-25/spdx-tools-migration-research.md, requirements-spdx-validation.txt, scripts/validate_release_sbom_contract.py, scripts/validate_repo.py, tests/test_spdx_sbom.py, tests/test_structure.py, .github/workflows/ci.yml, .github/workflows/publish-release.yml, README.md, and recorded hosted-check evidence

### Opening Review State

* Interpreted review goal: Determine whether the completed migration satisfies the approved official-SPDX-tooling architecture and all material acceptance requirements without introducing release-boundary regressions.
* Review scope: Full task
* Evidence readiness: The completed plan, critique, changes record, research, implementation, tests, documentation, and hosted validation evidence were available and reconciled.
* Acceptance basis: D1-D3, FR-001 through FR-008, NFR-001 through NFR-005, all task Requirements blocks, and resolved critique findings PC-001 and PC-002.
* First comparison boundary: Compare the supplied requirements and completion claims once against current source, tests, workflows, documentation, and validation evidence; do not perform open-ended research or rerun validation.
* Active read-only boundaries: Review may create or update only this canonical review record and must not mutate implementation, plan, critique, research, or changes evidence.
* Authority: the review parent compares evidence and writes findings; final outcome, route dispositions, and continuation are recorded in Parent Decision Record
* Initial blockers: None

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|----------------------|-----------------------------------------|------------|----------------------|
| P01-T01, FR-001, NFR-001, NFR-004 | `requirements-spdx-validation.txt` contains the selected 13 exact versions with one SHA-256 hash each; recorded Linux/Python 3.12 hash-enforced binary download passed | Met | Dedicated lock and isolation match the approved architecture |
| P01-T02, FR-006, NFR-001 | `scripts/validate_repo.py` verifies the reviewed lock, Python 3.12 CI setup, and exact install command; structural mutation coverage is incomplete and the general requirement-file boundary is not enforced | Gap | RV-001 |
| P02-T01, FR-003-FR-005, NFR-003 | `scripts/validate_release_sbom_contract.py` is stdlib-only, old path removed, and retained logic is limited to root identity/version/attribution, exact runtime packages, and required topology | Met | The generic SPDX field/type/license/URI/identifier checks were removed |
| P02-T02, FR-002, FR-007, NFR-003, NFR-004 | `tests/test_spdx_sbom.py` runs official CLI subprocesses and fails hosted CI if the tool is unavailable; repository-policy tests remain local-compatible | Gap | RV-002 for the incomplete official mutation matrix; the implemented synthetic fixture and current policy cases otherwise align |
| P03-T01, FR-001-FR-002, NFR-001-NFR-002, NFR-004-NFR-005 | `.github/workflows/publish-release.yml` preserves read-only generation and immutable checkout, installs the lock, prepares metadata, runs official then contract validation, and uploads afterward | Met | Current release workflow is correctly ordered and fail-closed |
| P03-T02, FR-006-FR-007, NFR-001-NFR-002, NFR-005 | `validate_publish_release_workflow()` protects step count/order, exact commands, setup pin, install command, Syft configuration, uploader/downloader, checksum, publication, permissions, and no release API in generation | Gap | RV-001 because required bypass and mutation classes remain unprotected |
| P03-T03, FR-008, NFR-005 | README, changes records, PR body source, hosted evidence, real Syft evidence, and CCR resolution are synchronized | Met | No implementation-time plan updates or open follow-up items were recorded |
| PC-001 | CI installs the hash lock before pytest; hosted evidence reports 100 passed with no skips | Met | Critique concern resolved as planned |
| PC-002 | Synthetic official mutations run in CI; real Syft compatibility is implementation evidence rather than a CI dependency | Met | Critique concern resolved as planned |
| Implementation-time plan updates | Changes record states none | Met | No contradictory scope change was identified |
| Blockers, remaining work, follow-ups | Changes record states none | Met with review defects | No stale implementation item exists; RV findings are later correction routes |

### Critique and Follow-Up Assessment

* Latest critique dispositions: PC-001 and PC-002 are supported by the implemented CI install, hosted no-skip evidence, synthetic test ownership, and separate real-Syft evidence.
* Material revisions: The implementation followed the revised plan without a divergent architecture or undocumented implementation-time decision.
* Dependent-work pause assessment: No evidence indicates work resumed before the planner resolved the critique findings.
* Justification assessment: The official-tooling and reduced-contract split remains supported by research and implementation evidence.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|----------------|-----------------------------|----------------------|----------------------|
| None | The plan and changes record contain no follow-up items | None | No distinct residual-work route |

### Reviewer Self-Check

* [x] Every supplied requirement, acceptance criterion, in-scope marker, material update, critique disposition, validation result, blocker, remaining item, and plan follow-up has an assessment or explicit gap.
* [x] Findings are substantive, evidence-grounded, severity-graded, and use stable `RV-xxx` IDs with expected and observed behavior, a resolution condition, and one proposed route each.
* [x] Execution status, assessed outcome, validation coverage, limitations, and proposed routes are complete and internally consistent.
* [x] The summary is scoped and advisory, findings keep their supporting context together, and acceptance coverage distinguishes demonstrated gaps from unassessed behavior.
* [x] Standard review completely assessed the material boundary while omitting restatement, cosmetic feedback, exhaustive strengths, low-impact suggestions, and continual narration; deep review remained inside the supplied boundary.
* [x] The review did not mutate source, the plan, critique, research, or changes record, did not execute validation, and verified any helper candidate at its cited evidence before recording it as a finding.
* Checked boundary: D1-D3; FR-001-FR-008; NFR-001-NFR-005; P01-P03 and all seven task Requirements blocks; PC-001/PC-002; validation, blockers, remaining work, documentation, and follow-up state.
* Missing or limited evidence: Review relied on the changes record and hosted log summary for command execution and did not independently rerun validation; no material acceptance boundary was unassessed.
