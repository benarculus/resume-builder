<!-- markdownlint-disable-file -->
# Review: Test maintainability

## Executive Summary

* Assessment: the full source implementation satisfies the accepted test-maintainability boundary; no substantive defects were identified.
* Why this matters: unblock release-safe fixtures without weakening existing product and CI contracts.
* Review execution: Complete.
* Assessed outcome: Conformant within the accepted source-review boundary, with hosted integration acceptance explicitly pending.
* Validation coverage: implementation reports 182 passed, 15 local integration skips, structural validation and bounded regression probes passed.
* Confidence and limitations: source comparison supports the fixture and regression contracts. Hosted Python 3.12/native/official SPDX results are unavailable for this candidate; supplied local results were assessed, not rerun.

The assessment above is the reviewer's proposal. Parent Decision Record contains the final decisions and next actions, or states that decisions are pending.

## What You May Not Know

Local skips are not integration success. The accepted P04-T01 contract expressly permits a documented pending hosted gate; this source verdict does not certify the 15 unexecuted integrations or PR #18's checks. Review does not authorize remote operations or applying this branch to PR #18.

Native-tool availability is now evaluated per integration test, not at import time. Missing binaries fail on GitHub Actions; a discovered but broken executable proceeds to the actual integration and fails there rather than being silently skipped.

## Findings and Proposed Routes

No substantive RV findings were identified within the assessed boundary. The hosted validation gate and separate application to PR #18 remain explicit external actions, not demonstrated source defects or newly invented active-plan tasks.

## Parent Decision Record

### Current Disposition

* Based on events: RD-001 through RD-005.
* Decision participation: user-owned.
* Review execution: Complete (RD-003).
* Final outcome: Conformant for the accepted source-review boundary (RD-004); hosted integration, merge and release acceptance are not certified.
* Walkthrough: not required; no actionable RV findings (RD-002).
* Finding decisions and next actions: none; no remediation route. Existing external hosted/delivery gate remains maintainer-owned (RD-005).
* Decisions still needed: none within Review. Remote delivery authorization remains separate.

This summary is derived from Decision History. The latest event for each subject governs.

### Decision History

| Event | Subject | Decision source | Status or value | Proposed destination | Final destination | Owner | More information needed | Smallest next action | Rationale |
|-------|---------|-----------------|-----------------|----------------------|-------------------|-------|-------------------------|----------------------|-----------|
| RD-001 | participation | user invocation / contract default | user-owned | none | none | user | none | Compare supplied boundary | Standalone manual /hve-core:rpi-review; no automatic parent state |
| RD-002 | walkthrough | review parent | not-required-no-findings | none | none | user | none | No item questions | No actionable RV findings; do not request acknowledgment |
| RD-003 | execution | review parent | Complete | none | none | review parent | none | Close out record | One full marker-driven comparison completed with supplied validation limits |
| RD-004 | outcome | review parent | Conformant | none | none | review parent | Same-candidate hosted execution remains unavailable | Preserve source-only verdict | All material source contracts satisfied; P04-T01 permits explicitly pending hosted evidence and no defect/decision gap was identified |
| RD-005 | continuation | review parent | no-rpi-handoff; existing external gate retained | none | maintainer-authorized delivery and hosted validation | maintainer | Provisioned Python 3.12 results for all 197 cases | Authorize delivery and obtain same-candidate CI without missing-tool skips | No RV remediation or new follow-up task; PR #18 is unchanged and remote operations were not authorized |

## Validation Evidence

All execution evidence below is supplied by the implementation changes record, not newly executed during Review.

| Command or evidence | Scope | Status | Summary |
|---------------------|-------|--------|---------|
| Release selector including release_please_versions | P01-T01 | Passed | 17 cases; synchronized/drifted 0.1.0, 0.2.0, 0.3.0 and 1.0.0 |
| Structural module | P01-T02, P03-T01 | Passed | 96 cases after CI additions; checked mutation and formatting coverage |
| DOCX/parser + SPDX | P02-T01 | Passed with skips | 47 passed, seven official SPDX skips |
| DOCX/parser + length | P02-T02 | Passed with skips | 50 passed, two LibreOffice skips |
| OCR module before gating additions | P02-T03 | Passed with skips | Nine deterministic cases passed, six native skips |
| Structure/OCR/length | P03-T01 | Passed with skips | 127 passed, eight native skips; direct hosted/local missing-tool cases |
| python3 -B scripts/validate_repo.py | Full task | Passed | Includes new CI execution contract through main |
| python3 -B -m pytest -q -rs -p no:cacheprovider | Full task | Passed with skips | 182 passed, 15 skipped; five existing PyMuPDF deprecation warnings |
| Collection and original-function inventory | NFR-001, P04-T01 | Passed | Reported 197 cases: 130 retained plus 67 additions; all 102 original test functions retained |
| Bounded dependency/policy counterfactuals | P02-T01, P02-T02, P04-T01 | Passed | Missing-Pillow oracle regression produced expected failure; 476/599/one-page policy regression produced seven expected failures |
| git diff --check; artifact reconciliation | Full task | Passed | Supplied whitespace result and corrected four-phase/seven-task reconciliation |
| Fully provisioned hosted Python 3.12 | External integration gate | Unavailable | Six OCR, seven official SPDX and two LibreOffice cases not exercised locally on this candidate |

## Risks, Blockers, and Residual Work

* Blockers: none for source comparison.
* Remaining active work: none according to reconciled plan and changes record.
* External gate: fully provisioned hosted execution remains pending before integration/merge/release acceptance.
* Distinct follow-up: no new backlog work identified. Maintainer must authorize delivery and a same-candidate provisioned CI run; applying fixes to PR #18 is separate from this review.

## Review Record

### Scope and Evidence

* Task ID: test-maintainability-2026-10-06.
* Review date: 2026-10-07.
* Review scope: full task; four phases and seven tasks.
* Assessed boundary: FR-001 through FR-009, NFR-001 through NFR-004, all completed markers, critique PC-001, implementation updates and supplied validation.
* Review depth and provenance: standard; default, no explicit deep request.
* Candidate identity: working diff from HEAD 23dfd6a168fb5b74850539c3d953ea84fca29e04; seven modified tracked targets plus tests/conftest.py and task artifacts.
* Review execution: Complete.
* Helper use: none.
* Parent orchestration state: none; canonical decisions live only in this record.
* Plan: .copilot-tracking/plans/2026-10-06/test-maintainability-plan.md.
* Plan critique: .copilot-tracking/reviews/plans/2026-10-06/test-maintainability-plan-critique.md.
* Changes: .copilot-tracking/changes/2026-10-06/test-maintainability-changes.md.
* Research: .copilot-tracking/research/2026-10-06/test-maintainability-research.md.
* Source evidence: README.md, scripts/validate_repo.py, all five tests/test_*.py modules, tests/conftest.py, directly relevant unchanged product scripts and .github/workflows/ci.yml.
* Scoped criteria: code-review functional/standards/readiness lenses and retained python-foundational guidance; not a separate code-review workflow or security audit.

### Opening Review State

* Interpreted review goal: determine whether implementation satisfies the accepted maintainability contracts while preserving existing behavior.
* Review scope: full task.
* Evidence readiness: current plan and changes reconcile all checked markers and acknowledge hosted evidence limits; sole critique finding is recorded resolved; no earlier Review exists for this task.
* Acceptance basis: task-local Goals, Requirements, Details, References, FR/NFR contracts, PC-001 correction and scope ceilings.
* First comparison boundary: one marker-driven source/evidence comparison; no execution of tests, new research, remote operations or source remediation.
* Active read-only boundaries: only this canonical review record may be created or updated.
* Authority: review parent compares evidence and writes findings; final outcome, routes and continuation are recorded in Parent Decision Record.
* Initial blockers: none for source comparison; mandatory hosted gate remains explicitly unavailable.

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|----------------------|----------------------------------------|------------|----------------------|
| P01, P01-T01, FR-001 | tests/test_structure.py: drift_version, original four drift cases and test_release_please_versions_are_release_independent; unchanged validate_release_please_config | Met | Guaranteed-different valid versions; isolated synchronized metadata for all four baselines; original field-specific negatives reused with restored monkeypatch contexts; real-repository positive check retained |
| P01-T02, FR-002 | tests/test_structure.py: checked_replace, mutate_release_config, helper rejection and compact/expanded JSON cases; full diff of existing mutations | Met | Absent targets and unchanged inputs assert explicitly; one/all replacement intent declared; semantic JSON mutations cover the original draft/type/updater contracts; raw hashes/comments/scripts remain intentional text contracts |
| P02, P02-T01, FR-003 | tests/test_build_docx.py: parser negatives; unchanged parse_job_requirements.py | Met | Non-object root, missing/invalid source, each required array's type, non-object/incomplete items and missing/non-object constraints reject explicitly; valid fixture case retained |
| P02-T01, FR-004, PC-001 | tests/test_spdx_sbom.py: independent normalized pins, malformed pins, missing independent Pillow, preparation preservation and CLI errors; unchanged contract/preparer scripts | Met | Explicit synthetic maps remove the shared-oracle blind spot; missing/duplicate/wrong-version root leaves input unchanged; invalid args, malformed JSON and missing input assert nonzero exit, stderr category and no success output |
| P02-T02, FR-005 | tests/test_validate_resume_length.py: assert_main_report, four word boundaries, three page boundaries, conversion error/missing PDF cases; unchanged length validator | Met | Pins inclusive 475/600, rejects 474/601 and three pages, accepts one/two pages; complete nested values, exact types and exit status asserted independently |
| P02-T02, FR-006 | tests/test_validate_resume_length.py: three independent rendered-body cases; tests/test_build_docx.py: saved unmet-content exclusion, invalid payloads and unapproved ordering; unchanged renderer | Met | Literal paragraph expectations and independent token count protect aliases/dates/awards/skills; actual unmet IDs/content excluded; identity/contact and headings outside body count |
| P02-T03, FR-007 | tests/test_ocr_extract.py: confidence/sentinel/no-word cases, confidence-over-length, no-word tie, 180-degree candidate and page/input errors; unchanged OCR implementation | Met | Deterministic native-free cases exercise the accepted decisions; all six existing real integration cases retained |
| P03, P03-T01, FR-008 | scripts/validate_repo.py: validate_ci_execution_contract and main; structural CI mutation cases; tests/conftest.py and fixture wiring in OCR/length; unchanged ci.yml and validate_spdx_validation_lock | Met | Requires unique native/pytest steps and ordering; rejects condition/failure/selection/environment/cwd bypasses; accepts folded YAML without conflating shell line boundaries; hosted missing tools fail and only relevant local integrations skip |
| P04, P04-T01, FR-009 | README.md Validation; changes record Validation Record, Pre-Review Reconciliation and Return-to-Caller State | Met for declared boundary | Local results, skipped integrations, release-scenario selectors and remote non-actions distinguished; no claim that integration or release CI already passed |
| NFR-001 | Full seven-file diff plus new tests/conftest.py; supplied original inventory and case table | Met | Original assertions/cases retained; removal of import-time native skip helpers replaced by stricter runtime gates, not loss of integration coverage; 67 additions within aggregate 74 and every task ceiling; no product/dependency/version/workflow edits |
| NFR-002 | Temporary fixture ownership and pytest monkeypatch usage across five modules; independent maps/endpoints/paragraphs | Met | Isolated deterministic inputs and independent expected behavior; synthetic SPDX 0.2.0 and reviewed policy tripwires intentionally retained |
| NFR-003 | tests/conftest.py, existing official_validator, hosted/local tests and README | Met for code contract; hosted execution not assessed | Explicit GitHub Actions failures prevent missing-tool skips; actual same-candidate hosted compatibility remains unexecuted and clearly pending |
| NFR-004 | Candidate status/diff; tmp_path-based JSON/YAML/DOCX/PDF tests | Met | Changes confined to approved canonical targets and task artifacts; no new dependencies, generated tracked output or credentials |
| Implementation authorization and guidance updates | Plan Confirmed User Direction, P03/P04 Guidance; changes Implementation-Time Plan Updates | Supported | Explicit implementation invocation and scoped helper ownership do not change accepted behavior or architecture |
| Inherited CI override and shell-line refinements | Current P03-T01 Requirements, validate_ci_execution_contract and four grouped policy cases | Supported | Tightly coupled to FR-008 full-suite guarantees; no new work item or case-budget expansion |
| Checklist-count correction and handoff update | Plan Task Metadata/Critique Disposition; changes reconciliation and seven completion entries | Supported | Seven actual task IDs reconcile with all evidence; historical eight-task prose does not represent omitted work |

Task case-budget evidence: P01 adds 8 + 4; P02 adds 18 parser/SPDX + 20 renderer/length + 9 OCR; P03 adds 8, for 67 total. All per-task ceilings remain satisfied. Source diff retains existing assertion intent; inventory totals remain supplied execution evidence rather than a new collection run.

The one comparison included the complete tracked diff and new helper, directly relevant unchanged implementations and CI, and all supplied task artifacts. No validation, second comparison, independent helper or separate review execution was performed.

### Critique and Follow-Up Assessment

* Latest critique dispositions: PC-001 is resolved by candidate-2's explicit CLI acceptance and test_preparer_cli_reports_invalid_arguments_and_inputs; no unresolved critique finding.
* Material revisions: none requiring a different accepted plan. Shared helper choices and inherited CI/shell-line protections stay within approved requirements; count correction is factual metadata reconciliation.
* Dependent-work pause assessment: supplied implementation records no newly discovered product defect or divergent decision that required pausing; source diff does not introduce one.
* Justification assessment: scope and behavior preservation are supported; all checked completion markers reconcile with evidence. Hosted acceptance is expressly conditional under P04-T01, not silently waived.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|----------------|-----------------------------|----------------------|----------------------|
| Plan Follow-Up Items: None | No distinct unresolved plan follow-up | none | Changes record matches; no route needed |
| Hosted execution and delivery to PR #18 | Requires separately authorized remote actions; unavailable local tools are an accepted evidence limit | Maintainer: deliver candidate and obtain provisioned hosted CI | Existing external gate retained; no RPI remediation destination proposed |

### Reviewer Self-Check

* [x] Every supplied requirement, acceptance criterion, in-scope marker, material update, critique disposition, validation result, blocker, remaining item and plan follow-up has an assessment or explicit limit.
* [x] No substantive evidence-grounded finding warrants an RV entry; limitations are not presented as demonstrated defects.
* [x] Execution status, assessed outcome, validation coverage, limitations and proposed routes are internally consistent.
* [x] Summary is scoped; acceptance coverage distinguishes source conformance from unexecuted hosted behavior.
* [x] Standard review covered the material boundary once and omitted cosmetic feedback, speculative bypass inventories and continual narration.
* [x] Review mutated only this canonical record, did not execute validation and used no helpers.
* Checked boundary: FR-001-FR-009, NFR-001-NFR-004, four phases/seven tasks, PC-001, all recorded updates and validation, no active tasks and no plan follow-ups.
* Missing or limited evidence: same-candidate fully provisioned hosted Python 3.12 run and application to PR #18. No integration, merge or release-success verdict is asserted.
