<!-- markdownlint-disable-file -->
# RPI Changes: Resume writing guidance

## Metadata

* Task ID: resume-writing-guidance
* Related plan: [.copilot-tracking/plans/2026-09-19/resume-writing-guidance-plan.md](../../plans/2026-09-19/resume-writing-guidance-plan.md)
* Implementation date: 2026-09-19

## Execution Status

* Status: Complete
* Declared invocation scope: full_plan
* Completed scope markers: `P01`, `P01-T01`, `P01-T02`, `P02`, `P02-T01`, `P02-T02`, `P03`, `P03-T01`
* All remaining active-plan markers: none
* Status basis: all tasks in the full approved plan have completion evidence and passing validation

## Execution Summary

The full approved plan is implemented. Skill guidance, shared education/training rules, DOCX presentation behavior, and focused regression coverage are complete.

## Completed Work

### Evidence-preserving career-document guidance

* Related phase or task: `P01-T01`
* Files:
  * [skills/career-document-builder/SKILL.md](../../../skills/career-document-builder/SKILL.md)
* What changed and why: Added verbose STAR/What–How–Why evidence rules, complete education/training requirements, provenance-safe abbreviation handling, and clarification behavior.
* Completion evidence: The skill now explicitly separates the complete career evidence record from resume presentation constraints and forbids inferred education facts.
* Validation: Passed by review and `git diff --check`; behavioral tests remain in `P03-T01`.

### Resume drafting and formatting guidance

* Related phase or task: `P01-T02`
* Files:
  * [skills/resume-drafter/SKILL.md](../../../skills/resume-drafter/SKILL.md)
* What changed and why: Added action-verb, STAR/What–How–Why, keyword, word-count, two-line, top-matter, chronology, readability, and education/training rules.
* Completion evidence: The drafting skill now requires evidence-mapped concise bullets and preserves unmet requirements.
* Validation: Passed by review and `git diff --check`; renderer tests remain in `P03-T01`.

### Education and training contract

* Related phase or task: `P02-T01`
* Files:
  * [docs/shared/career-document-schema.md](../../../docs/shared/career-document-schema.md)
* What changed and why: Added a canonical spelled-out education/training contract with completion date, institution, optional evidence-supported abbreviation, compatibility mappings, and anti-inference rules.
* Completion evidence: The shared contract documents the required values and preserves compatibility with existing JSON Resume fields.
* Validation: Passed by review and `git diff --check`.

### DOCX resume presentation

* Related phase or task: `P02-T02`
* Files:
  * [skills/resume-drafter/scripts/build_docx.py](../../../skills/resume-drafter/scripts/build_docx.py)
* What changed and why: Added 0.5-inch margins, Arial 11 pt body styling, 20 pt left-aligned name, left-aligned headings/content, requested contact ordering with optional clearance, reverse chronological experience/education ordering, and full education rendering with optional abbreviations.
* Completion evidence: The renderer accepts legacy string locations and structured locations, preserves legacy phone/URL fields after the requested identity/location/clearance fields, and renders the requested top matter without silently dropping existing sections.
* Validation: Passed focused and full test suites; representative DOCX generation succeeded.

### Contract and renderer regression coverage

* Related phase or task: `P03-T01`
* Files:
  * [tests/test_build_docx.py](../../../tests/test_build_docx.py)
  * [skills/resume-drafter/scripts/fixtures/sample-resume.json](../../../skills/resume-drafter/scripts/fixtures/sample-resume.json)
* What changed and why: Added tests for top matter order, optional clearance, margins, name size, reverse chronology, complete education rendering, and existing parser/section behavior.
* Completion evidence: Four DOCX tests and three repository structure tests pass.
* Validation: `python3 -m pytest` passed with 7 tests.

### Implementation choices recorded

* Related phase or task: `P02-T01`, `P02-T02`
* Files:
  * [docs/shared/career-document-schema.md](../../../docs/shared/career-document-schema.md)
  * [skills/resume-drafter/scripts/build_docx.py](../../../skills/resume-drafter/scripts/build_docx.py)
* What changed and why: Resolved the plan's bounded implementation choices without changing user requirements.
* Completion evidence:
  * Completion dates preserve source precision and render from `completionDate`, `date`, or legacy `dates`; no new date normalization is inferred.
  * The requested email/location/clearance order is primary; legacy phone and URL values are retained as additional trailing contact segments for compatibility.
  * Arial was selected as a readable default, with 11 pt body text and 20 pt name text; the two-line rule remains a content/visual validation target rather than an unsupported XML-only assertion.
* Validation: Covered by renderer tests and full suite.

## Implementation-Time Plan Updates

### Completion markers and implementation state reconciled

* Affected plan area or markers: `P01`, `P01-T01`, `P01-T02`, `P02`, `P02-T01`, `P02-T02`, `P03`, `P03-T01`
* What changed: Checked all completed phase/task markers and changed the plan's next action from implementation to `/rpi-review`.
* Why: All approved work has completion evidence and passing validation.
* Triggering evidence: Contract edits, renderer changes, fixture/test updates, and the final 7-test passing run.
* User answer or decision: None; bounded implementation choices were resolved locally within the approved plan.
* Reconciliation performed: Updated execution status, completed markers, readiness, next action, remaining work, and validation references in the plan and this changes record.
* Planning and critique state: Planning remains complete; no new critique or user decision was required.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| Pre-edit repository inspection | Full plan | Passed | Approved plan, linked skill/schema/renderer/test references, and existing dependency state were read |
| `git diff --check` | `P01-T01`, `P01-T02`, `P02-T01` | Passed | No whitespace errors after contract edits |
| `python3 -m py_compile skills/resume-drafter/scripts/build_docx.py tests/test_build_docx.py` | `P02-T02`, `P03-T01` | Passed | Renderer and tests compile |
| `python3 -m pytest tests/test_build_docx.py` | `P03-T01` | Passed | 4 focused DOCX tests passed |
| `python3 -m pytest tests/test_structure.py` | `P03-T01` | Passed | 3 repository structure tests passed |
| `python3 -m pytest` | Full plan | Passed | 7 tests passed |
| Representative DOCX generation | `P02-T02` | Passed | Sample fixture rendered successfully with `python3` and `python-docx` 1.2.0 |

## Pre-Review Reconciliation

* Plan markers and task-local context: all phase and task markers checked
* Completed-work evidence and handoff prose: all contract, renderer, and test work recorded above
* Validation, blockers, remaining work, and follow-up items: all validation passed; no blockers or remaining active work
* Review readiness: Ready for `/rpi-review`

## Blockers

* None

## Remaining Work

* None

## Follow-Up Items

* Canonical plan list: [.copilot-tracking/plans/2026-09-19/resume-writing-guidance-plan.md](../../plans/2026-09-19/resume-writing-guidance-plan.md), `## Follow-Up Items`
* None

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: full plan; all phase and task markers complete
* Validation coverage: full focused and repository test coverage passed; representative DOCX generation passed
* Blockers: none
* Current plan updates: execution boundary recorded in this changes record
* Planning and critique state: plan remains implementation-ready; no new decision or critique required
* Follow-up items: none
* Review readiness or no-handoff reason: ready for `/rpi-review`
* Continuation owner: user
