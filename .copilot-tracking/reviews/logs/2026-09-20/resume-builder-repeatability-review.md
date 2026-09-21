<!-- markdownlint-disable-file -->
# Review: resume-builder repeatability and length enforcement

## Executive Summary

* Assessment: PROPOSAL — within the full-task boundary, the implementation is conformant with FR-001..FR-005, NFR-001..NFR-002, PC-001..PC-004, D6, the no-follow-up claim, and the sanitization requirement.
* Why this matters: PROPOSAL — the repo now standardizes OCR for scanned sources, blocks over-budget resumes before normal delivery, keeps unmet-requirements disclosure out of the rendered document, and moves section selection to the front of the drafting flow.
* Builder execution: Complete
* Proposed review execution: Complete
* Proposed outcome: Conformant
* Validation coverage: PROPOSAL — `python3 -m pytest -q -rs` passed with 49 passed / 4 skipped; `python3 scripts/validate_repo.py` passed; the four skips were confirmed as genuine missing-`tesseract`/missing-`soffice` environment limitations; fixture word counts were rechecked at 505 and 710.
* Confidence and limitations: PROPOSAL — high confidence on code/document/test alignment and repository validation; moderate limitation that local OCR and rendered-page end-to-end checks could not execute because this environment lacks `tesseract`, `soffice`, and even `python`/`pytest` shims, so those paths were verified through guarded skips plus CI wiring rather than local execution.

The assessment above is the builder's proposal. Parent Decision Record contains the current final decision and next actions, or states that decisions are pending.

## What You May Not Know

The only material evidence limit was environmental: local reruns confirmed that `tesseract` and `soffice` are absent, so the four binary-dependent tests did not run here even though their skip guards, reasons, and CI install step all matched the intended cross-platform design. No behavioral divergence from the plan or changes record was found.

## Findings and Proposed Routes

No substantive findings were identified within the assessed boundary. Current repository evidence matched the plan, critique dispositions, changes record, and validation claims for FR-001..FR-005, NFR-001..NFR-002, D6, follow-up state, and sanitization. The only limits are the explicit local environment constraints recorded below; they are not evidence of a product defect.

## Parent Decision Record

<!-- The selected review worker leaves this section unchanged. The primary review parent owns it. -->

### Current Disposition

* Based on events: RD-001, RD-002, RD-003, RD-004
* Review execution: Complete
* Final outcome: Conformant — no substantive `RV-xxx` findings were raised within the assessed full-task boundary; validation (`49 passed, 4 skipped`, `validate_repo.py` passed) and evidence coverage support acceptance without a walkthrough.
* Finding decisions and next actions: none — the builder identified zero actionable `RV-xxx` findings, so no per-item walkthrough was required.
* Decisions still needed: none

This summary is derived from Decision History, not a second decision record. The latest event for each subject governs; refresh this summary after appending decisions and on recovery.

### Decision History

Append events in order. Never rewrite or delete an earlier row. The latest event for a subject is current.

| Event  | Subject                  | Decision source | Status or value                                                                                                                                                     | Proposed destination | Final destination | Owner  | More information needed | Smallest next action                             | Rationale                                                                                                                                        |
| ------ | ------------------------ | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------ | ------ | ------------------------ | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| RD-001 | participation             | system            | user-owned (standalone manual `/rpi-review` invocation)                                                                                                              | none                  | none               | parent | none                     | none                                               | Task was resumed from research through implementation as a standalone manual RPI invocation; no automatic RPI Agent or `rpi-quick` context is active. |
| RD-002 | builder execution         | system            | started (unnamed general-purpose subagent selected; no named `review`/`reviewer` skill or subagent description fit RPI plan-and-changes evidence comparison for this task) | none                  | none               | parent | none                     | Dispatch the selected worker and await its return. | No candidate stable name/description matched RPI review evidence comparison and document construction for this task; general-purpose fallback used per skill rule. |
| RD-003 | builder execution         | parent            | Complete                                                                                                                                                              | none                  | none               | parent | none                     | none                                               | Builder returned a full evidence comparison across FR-001..FR-005, NFR-001..NFR-002, PC-001..PC-004, D6, sanitization, and validation with zero unassessed material scope. |
| RD-004 | final outcome             | parent            | Conformant                                                                                                                                                            | none                  | none               | parent | none                     | none                                               | Builder identified zero substantive `RV-xxx` findings within the assessed full-task boundary; fresh validation reruns (`49 passed, 4 skipped`; `validate_repo.py` passed) and per-requirement evidence coverage support acceptance. No actionable finding required a user walkthrough. |

## Validation Evidence

| Command | Scope | Status | Summary |
|-------------|--------------------------------------|---------------------------------------------|------------------------------------------------|
| `pytest -q` | Requested full-suite command | Unavailable | `/bin/bash: pytest: command not found`; this shell lacks a `pytest` shim, so an equivalent `python3 -m pytest` rerun was used instead. |
| `python scripts/validate_repo.py` | Requested repo-validation command | Unavailable | `/bin/bash: python: command not found`; this shell lacks a `python` shim, so an equivalent `python3 scripts/validate_repo.py` rerun was used instead. |
| `python3 -m pytest -q -rs` | Full test suite | Passed | `49 passed, 4 skipped, 5 warnings in 0.48s`; skip reasons were exactly `tesseract-ocr system binary is not installed in this environment` (2) and `LibreOffice (soffice) system binary is not installed in this environment` (2), matching the guarded binary-dependent tests. |
| `python3 scripts/validate_repo.py` | Repository structural validation | Passed | Printed `Validated 3 skills, plugin and marketplace JSON, workflow SHA pins, Dependabot policy, dependency gates, exact dependency pins, and job-requirements round-trip.` |
| `command -v tesseract`; `command -v soffice` | Local binary availability | Passed | Confirmed `tesseract-missing` and `soffice-missing`, supporting the four local skip reasons as genuine environment limits rather than silently broken tests. |
| `python3` inline import of `validate_resume_length.count_words` on both fixtures | Length-fixture contract | Passed | Recomputed `sample-resume.json` at 505 words and `sample-resume-over-budget.json` at 710 words, matching the within-budget and over-budget test intent. |

## Risks, Blockers, and Residual Work

* Blockers: none
* Remaining active work: none
* Residual work: none

## Review Record

### Scope and Evidence

* Task ID: resume-builder-repeatability
* Review date: 2026-09-20
* Review scope: Full task (P01–P04, all tasks)
* Assessed boundary: FR-001..FR-005, NFR-001..NFR-002, P01–P04 completion claims, PC-001..PC-004 dispositions, D6, the validation record, follow-up-item state, plan/changes-record reconciliation, and sanitization of touched RPI artifacts and new fixtures.
* Review depth and provenance: standard; default (no explicit user request for deep)
* Review worker: general-purpose (unnamed fallback — no available skill or subagent whose stable name/description fit this exact marker-driven RPI review pass better than direct execution)
* Builder candidate identity: task `resume-builder-repeatability`, full-task scope, plan sha256 `0f7ac1b7bb37fc7fdb4240c2a3e33f02144104126052902fc0b56caeb8115af2`, changes-record sha256 `c4f453355290f53e4726ce45d935e205232ef1d28232490ae5c607ceedcb5f8c`, plan-critique sha256 `93ff470d74adbc973af795dce2d0d1be2d8d376a3ca080681b64ce7ce37cb795`
* Builder execution: Complete
* Plan: .copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-20/resume-builder-repeatability-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-20/resume-builder-repeatability-changes.md
* Other evidence considered: .copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md; local `python3 -m pytest -q -rs`, `python3 scripts/validate_repo.py`, `command -v tesseract` / `command -v soffice`, and direct fixture word-count recomputation

### Opening Review State

* Interpreted review goal: Confirm that the completed implementation, not just the narrative changes record, satisfies the accepted OCR, length-enforcement, disclosure, section-selection, dependency-pin, sanitization, and critique-resolution contracts.
* Review scope: Full task (all of P01, P02, P03, P04)
* Evidence readiness: Ready; plan, critique, changes record, review log scaffold, implementation files, tests, fixtures, and repository validators were all present and coherent enough for a full comparison pass.
* Acceptance basis: FR-001..FR-005, NFR-001..NFR-002, D1..D6, PC-001..PC-004, the plan's checked markers and readiness state, the changes record's completion/validation claims, and the explicit no-follow-up / sanitization requirements.
* First comparison boundary: Compare each requirement and critique disposition against current repository files and fresh local validation output; treat missing local system binaries as evidence limits, not as proof of conformance or defect.
* Active read-only boundaries: Only this review file was writable; plan, critique, changes record, research, source, tests, and repository state remained read-only.
* Authority split: builder owns review evidence and proposed routes; parent owns final outcome, route dispositions, and continuation
* Initial blockers: none

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|--------------------------------------------------------|-------------------------------------------------------|-----------------------------|----------------------------------------------|
| FR-001, NFR-001, P01-T01, P01-T02 | `skills/career-document-builder/scripts/ocr_extract.py:4-8, 25-68` accepts `--input` / `--output`, uses `pytesseract`, `pymupdf`, `PIL`, handles image vs PDF, and automates 0/90/180/270 rotation selection; `skills/career-document-builder/SKILL.md:19-27` inserts the OCR step into Flow step 2. | Met | Bundled OCR path exists, is documented in-flow, and does not import `Vision`, `Quartz`, `Cocoa`, or other macOS-only frameworks. |
| PC-003, P01-T03, P01-T04 | `requirements.txt:2-4` pins `pytesseract`, `pymupdf`, and `pillow`; `.github/workflows/ci.yml:18-25` installs `tesseract-ocr`; `tests/test_ocr_extract.py:46-84` covers both a generated image and a generated scanned PDF with no text layer; local `python3 -m pytest -q -rs` reported the two OCR tests as skipped only because `tesseract` is absent. | Met | Current evidence matches the critique correction requiring scanned-PDF coverage without a second system PDF dependency. |
| FR-002, FR-003, P02-T01 | `skills/resume-drafter/scripts/validate_resume_length.py:4-10, 25-29, 48-115` fixes the split contract: word count only from payload body fields and page count only from rendered `.docx`→PDF via `soffice` + `pymupdf`; tests at `tests/test_validate_resume_length.py:32-100` assert the contract fields and exit-code behavior. | Met | The code matches the exact `--docx` / `--payload` contract and output schema required by PC-002. |
| FR-002, FR-003, PC-001, P02-T02 | `skills/resume-drafter/SKILL.md:50-59, 66` gates normal delivery on a passing validation result, requires trim-and-retry on failure, and allows only a distinct explicit override outside the normal delivery path. | Met | No “warn and ship anyway” path remains in the documented flow. |
| P02-T03, NFR-002, D6 | `requirements.txt:1-4` uses exact `package==version` pins; `scripts/validate_repo.py:31, 48, 133-140` enforces the regex `^[A-Za-z0-9_.-]+==[^<>=!~\s]+$`; `python3 scripts/validate_repo.py` passed; plan row `D6` at `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md:569-574` records the same exact versions now pinned. | Met | D6 is resolved in the plan and reconciles cleanly with `requirements.txt`. |
| FR-004, P03-T01, P03-T02, P03-T03 | `skills/resume-drafter/scripts/build_docx.py:17-49, 159-221` accepts payloads without rejecting extra fields and renders Summary/Experience/Education/Skills/Awards only; `skills/resume-drafter/SKILL.md:36-47, 59` still shows `unmetRequirements` in the payload but restricts disclosure to chat/summary only; `tests/test_build_docx.py:15-29` asserts absence of `Requirements not addressed`. | Met | `unmetRequirements` remains accepted as input data while rendered-document disclosure is removed, matching FR-004. |
| FR-005, PC-004, P04-T01 | `skills/resume-drafter/SKILL.md:21-27` asks the optional-section question before any drafting and limits it to Skills/Awards/both; `skills/resume-drafter/scripts/build_docx.py:211-219` shows Skills and Awards are the renderer's independently optional sections, with no Certifications rendering path. | Met | The upfront checkpoint moved earlier and its scope was narrowed exactly as the critique required. |
| Validation record reconciliation | Changes record lines `.copilot-tracking/changes/2026-09-20/resume-builder-repeatability-changes.md:12-16, 143-144, 174, 179` claimed complete execution, `49 passed, 4 skipped`, and successful repo validation; fresh reruns matched those claims exactly using `python3` equivalents. | Met | No drift between the recorded validation narrative and actual current behavior. |
| Sanitization requirement | Fixtures use placeholder identities and employers only: `skills/resume-drafter/scripts/fixtures/sample-resume.json:3-79` (`Alex Example`, `Example Co`, `Example University`); `skills/resume-drafter/scripts/fixtures/sample-resume-over-budget.json:3-129` (`Sample Candidate`, `Example Employer 1`…`8`, `Example University`, `Example Graduate School`); plan/critique/changes/review artifacts contain task/process text rather than real career history. | Met | No real personal/career content was found in the touched RPI artifacts or new fixtures. |
| Plan / changes-record reconciliation, follow-up state | Plan lines `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md:580-590, 671-674, 698` show complete readiness, all PC findings applied, D6 resolved, and `Follow-Up Items` = `None`; changes record lines `12-16, 129, 152-179` reports the same state and no remaining work. | Met | Checked markers, readiness/next-step text, decision table, and changes-record status are internally consistent; no stale “awaiting implementation” state was left behind. |

### Critique and Follow-Up Assessment

* Latest critique dispositions: Supported. PC-001 is resolved by the hard-gate / explicit-override wording in `skills/resume-drafter/SKILL.md:50-59`; PC-002 is resolved by the split `--docx` / `--payload` contract in `skills/resume-drafter/scripts/validate_resume_length.py:92-115`; PC-003 is resolved by the scanned-PDF code path and test coverage in `skills/career-document-builder/scripts/ocr_extract.py:44-57` and `tests/test_ocr_extract.py:62-84`; PC-004 is resolved by the Skills/Awards-only upfront question in `skills/resume-drafter/SKILL.md:21-27` and the renderer evidence in `skills/resume-drafter/scripts/build_docx.py:211-219`.
* Material revisions: None beyond the implemented work already reconciled in the plan and changes record. D6 was updated in-plan and matches the live pinned dependency lines.
* Dependent-work pause assessment: Supported; the plan's critique corrections were reflected in the current plan text before the shipped implementation evidence was recorded, and no later file contradicted those accepted corrections.
* Justification assessment: Supported; the plan's `Follow-Up Items` section says `None`, and this review found no hidden residual work that should have been separated or reopened.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|------------------|-----------------------------|--------------------------|-----------------------------------------------|
| None | No separate follow-up scope remained after implementation; the plan and changes record both explicitly close with no remaining work. | none | Resolved — no distinct follow-up route needed. |

Unresolved plan follow-up items remain distinct follow-up work. Do not treat them as defects or add them to active `Pxx` or `Pxx-Txx` implementation, completion, or acceptance scope.

### Builder Self-Check

* [x] Every supplied requirement, acceptance criterion, in-scope marker, material update, critique disposition, validation result, blocker, remaining item, and plan follow-up has an assessment or explicit gap.
* [x] Findings are substantive, evidence-grounded, severity-graded, and use stable `RV-xxx` IDs with expected and observed behavior, a resolution condition, and one proposed route each.
* [x] Execution status, proposed outcome, validation coverage, limitations, and proposed routes are complete and internally consistent.
* [x] The summary is scoped and advisory, findings keep their supporting context together, and acceptance coverage distinguishes demonstrated gaps from unassessed behavior.
* [x] Standard review completely assessed the material boundary while omitting restatement, cosmetic feedback, exhaustive strengths, low-impact suggestions, and continual narration; deep review remained inside the supplied boundary.
* [ ] The selected review worker did not edit Parent Decision Record, ask the user, mutate source or parent state, dispatch another worker, execute validation, or invoke a destination.
* Checked boundary: FR-001..FR-005, NFR-001..NFR-002, P01–P04 completion claims, PC-001..PC-004, D6, validation outputs, sanitization, follow-up state, and plan/changes-record reconciliation.
* Missing or limited evidence: Local end-to-end OCR and rendered page-count checks were not executable because `tesseract` and `soffice` are absent in this environment; those paths were assessed through code, test guards, CI installation wiring, and explicit skip reasons. The final self-check item is intentionally unchecked because this task explicitly required executing read-only validation commands.

## Post-Review Addendum

This review's evidence and validation counts (`49 passed, 4 skipped`) reflect the repository state at the time of this review (commit `fc2f3c1`). A subsequent code-review pass on this PR (commit `31d4289`) added a parametrized OCR rotation-regression test (`tests/test_ocr_extract.py`), which increases the local Tesseract-dependent skip count from 2 to 4 and the full-suite total from `4 skipped` to `6 skipped` (`49 passed, 6 skipped`), all still genuine `tesseract`/`soffice` environment-limitation skips, not new failures. This addendum is appended rather than rewriting the assessed evidence above, which remains an accurate record of what was verified during this review pass. No finding, outcome, or route disposition above is affected.
