<!-- markdownlint-disable-file -->
# RPI Plan Critique: test-maintainability

## Metadata

* Task ID: `test-maintainability-2026-10-06`
* Critique date: 2026-10-06
* Plan: `.copilot-tracking/plans/2026-10-06/test-maintainability-plan.md`
* Critique execution status: Complete
* Critique depth: standard
* Depth provenance: default
* Invocation consumed: yes
* Attempt ID and kind: `test-maintainability-20261006-initial-01` (initial)
* Candidate identity and saved hash boundary: `candidate-1`; saved full-plan SHA256 before reservation metadata: `933479f39142eaa64e26d0ef0a14a83fb8f0363f3591289b8f93916cccf5349d`; only Critique Disposition reservation metadata changed after this boundary
* Current-run provenance: immediate activation of the persisted/read-back initial reservation in uninterrupted planner session `f9571e87-e6b8-41ac-aabd-9b6aba0eec53`; no parent state
* Original attempt and recovery approval: not applicable; initial attempt, no recovery

## Inputs and Criterion Boundary

* Task context and caller requirements: Address the reported release-test failure and assess all existing tests for maintainability and continued improvement. This is a plan critique only; no production implementation, product-behavior change, dependency addition, or automatic remote action is authorized.
* Research and evidence considered: `.copilot-tracking/research/2026-10-06/test-maintainability-research.md` (F1-F8, C1-C22, W1-W2 and the all-test coverage map).
* Decisions, dependencies, task Goals, and task Requirements considered: Confirmed all-test scope; preserve behavior and tests; four phases/eight tasks; task ownership, no removals, a maximum of 74 added collected cases, canonical/generated targets, validation evidence, and dependencies as recorded in the plan.
* Assessment boundary: Assess the candidate against the supplied research and directly relevant source contracts. Do not treat unavailable hosted/native integration runs as completed evidence or perform open-ended research.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| F1, P01-T01, FR-001 | Covered | Release-version collision is addressed with guaranteed-different or isolated fixtures and synchronized-version scenarios. |
| F2, P01-T02, FR-002 | Covered | Mutation preconditions and semantic JSON versus intentional raw-text policy checks are distinguished. |
| F3-F4, P02-T01, FR-003, FR-004 | Partial | Independent parser/SPDX oracles and preparation preconditions are included. The research coverage map also identifies SPDX CLI errors, but the task does not include CLI failure-path coverage. |
| F5, P02-T02, FR-005, FR-006 | Covered | Exact inclusive word/page endpoints, independent body-word expectations, reports, conversion failures, rendered parity, and unmet-content exclusion are specified. |
| F6, P02-T03, FR-007 | Covered | Deterministic dependency-free OCR decision/error tests complement retained real integrations. |
| F7, P03-T01, FR-008, NFR-003 | Covered | Hosted test/tool requirements and local optional skips are explicitly distinguished and tested. |
| F8, P02-T02 | Covered | Actual unmet IDs, invalid payload shape, experience ordering, and rendered-body parity are addressed without a renderer rewrite. |
| P04-T01, FR-009, NFR-001-NFR-004 | Covered | Scope, test retention, case ceiling, temporary artifacts, actual execution evidence, and pending hosted gate are recorded. |

## Verdict

* Verdict: Revise
* Rationale: The plan credibly addresses the material F1-F8 findings and preserves the confirmed behavior/scope constraints. One research-identified test gap remains outside its acceptance coverage: the SPDX preparer's CLI failure contract. A small planner-owned correction can fit within the existing P02-T01 case ceiling.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [Medium]: SPDX preparation CLI failures are not in the acceptance coverage

* Related IDs: F3, P02-T01, FR-004, NFR-001
* Evidence: `.copilot-tracking/research/2026-10-06/test-maintainability-research.md` identifies “preparation/CLI errors” in the SPDX module coverage map. In `scripts/prepare_spdx_sbom.py`, `main()` handles invalid argument count and the executable entry point translates assertion, JSON-decoding, and filesystem failures into a diagnostic and nonzero exit. `tests/test_spdx_sbom.py` directly exercises the preparer and release contract but does not exercise that CLI failure behavior. P02-T01 currently specifies parser/preparer/contract coverage without CLI error cases.
* Concern: A regression that suppresses or misreports an invalid invocation, malformed input, or unreadable input could leave the existing command-line contract unprotected, despite the research's identified CLI-error coverage opportunity.
* Impact: Maintainers could lose clear failure signaling at the preparation command boundary while the newly added unit-level preparation checks remain green.
* Smallest useful change: Add bounded P02-T01 acceptance coverage for CLI invalid-argument and representative malformed/unreadable-input failures, asserting nonzero exit and the established diagnostic behavior. Keep it within the task's existing SPDX allowance and the aggregate 74-case ceiling; do not broaden production behavior.
* Action owner: planning parent
* Exact resolving evidence: Revised P02-T01 Requirements/Details name the CLI failure cases and expected exit/diagnostic contract, and keep the total additions within the existing per-task and aggregate ceilings.
* Decision route: direct planner correction

## Strengths and Residual Risk

* The plan maps the release collision and all eight research findings to scoped work, preserves the distinction between semantic and raw-text mutations and independent versus production-derived oracles, and does not claim that local skips constitute integration success. The fully provisioned hosted Python 3.12 run remains an explicit implementation gate.

## Questions or Blocking Evidence Gaps

* None decision-critical. PC-001 is resolvable by a direct plan correction and requires no user decision.

## Limitations

* Native integrations and the hosted Python 3.12 gate were not rerun for this critique; the plan correctly reserves those results for implementation.
* Assessment was limited to the supplied research and directly relevant SPDX CLI/test sources; no broader research was performed.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning parent
* Smallest next action: Add bounded SPDX CLI failure-path acceptance coverage to P02-T01 without increasing its or the plan's existing case ceilings.
* User response required: no

| [.copilot-tracking/plans/2026-10-06/test-maintainability-plan.md](.copilot-tracking/plans/2026-10-06/test-maintainability-plan.md) | Critiqued candidate plan |
| [.copilot-tracking/research/2026-10-06/test-maintainability-research.md](.copilot-tracking/research/2026-10-06/test-maintainability-research.md) | Supplied audit evidence and coverage map |

## Next Steps

The active planning parent should revise P02-T01 for PC-001 and then finalize the plan without another critique. No user response is required.
