<!-- markdownlint-disable-file -->
# RPI Changes: resume-builder repeatability and length enforcement

## Metadata

* Task ID: resume-builder-repeatability
* Related plan: [.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md](../../plans/2026-09-20/resume-builder-repeatability-plan.md)
* Implementation date: 2026-09-20

## Execution Status

* Status: Complete
* Declared invocation scope: Full plan (P01–P04)
* Completed scope markers: P01, P01-T01, P01-T02, P01-T03, P01-T04, P02, P02-T01, P02-T02, P02-T03, P02-T04, P03, P03-T01, P03-T02, P03-T03, P04, P04-T01
* All remaining active-plan markers: none
* Status basis: Every task's `Requirements:` hold and its evidence is recorded below; `pytest -q` and `python scripts/validate_repo.py` both pass locally, and all four phases and their tasks are checked in the plan.

## Execution Summary

Implemented all four phases in plan order. Added a pinned, cross-platform OCR extraction script (`ocr_extract.py`, `pytesseract` + `pymupdf`) and wired it into `career-document-builder`'s source-inventory flow (P01). Added a resume length-validation script (`validate_resume_length.py`) enforcing the fixed `--docx`/`--payload` word-and-page contract, wired it as a hard delivery gate in `resume-drafter/SKILL.md`, and pinned the shared `pymupdf` dependency plus a LibreOffice CI/README prerequisite (P02). Removed the `.docx`-rendered "Requirements not addressed" section from `build_docx.py` while preserving the `unmetRequirements` payload field for chat-only disclosure, and updated the delivery flow wording and tests accordingly (P03). Added an upfront Skills/Awards section-selection question to `resume-drafter/SKILL.md`'s flow, ahead of content drafting (P04). All new and existing tests pass; system-binary-dependent tests (`tesseract`, `soffice`) are guarded to skip in this sandbox (neither binary is installable here) and are designed to run in CI, which now installs both.

## Completed Work

### P01-T01: Bundled OCR extraction script

* Related phase or task: P01-T01
* Files:
  * [skills/career-document-builder/scripts/ocr_extract.py](../../../skills/career-document-builder/scripts/ocr_extract.py)
* What changed and why: New script accepting `--input` (image or PDF) and `--output` (text file), using `pytesseract` (wrapping system `tesseract-ocr`) for OCR and `pymupdf` to rasterize PDF pages so no second system-level PDF dependency (e.g. Poppler) is required. Automates the first run's manual rotation trial-and-error by trying 0/90/180/270 degrees and keeping the result with the highest mean word-level OCR confidence, falling back to text length only when no candidate rotation has any recognized words (post-review, after the initial text-length-only heuristic was found to be unreliable — see commit `fc2f3c1` and the addendum below). Replaces the macOS-only `pyobjc-framework-Vision`/`Quartz` improvisation with a cross-platform path usable in this repo's `ubuntu-latest` CI.
* Completion evidence: File created; imports verified (`python3 -c "import ocr_extract"`); FR-001 and NFR-001 satisfied per the script's argument shape and dependency choice.
* Validation: Import/syntax check passed locally; end-to-end OCR behavior validated by P01-T04's tests (skipped locally, designed to run in CI where `tesseract-ocr` is installed).

### P01-T02: Documented the OCR flow in career-document-builder

* Related phase or task: P01-T02
* Files:
  * [skills/career-document-builder/SKILL.md](../../../skills/career-document-builder/SKILL.md)
* What changed and why: Inserted the OCR invocation into `Flow` step 2 (source inventory), naming the script's path and invocation shape and stating it applies to sources with no extractable text. Preserved the anti-fabrication posture: OCR output is treated as raw extracted text subject to the same ambiguity/clarifying-question rules as any other source. Post-review, added `shell` to this skill's `allowed-tools` frontmatter (commit follows this update): the skill invokes the bundled OCR script via a shell command, which is unavailable when `allowed-tools: []` is enforced.
* Completion evidence: Diff shows the new script invocation and OCR-output caveat inside step 2, plus the corrected `allowed-tools: [shell]` frontmatter.
* Validation: `python scripts/validate_repo.py` (skill frontmatter/structure checks) passed.

### P01-T03 and P02-T03 (coordinated): Pinned OCR/page-count dependencies across requirements, CI, and README

* Related phase or task: P01-T03, P02-T03
* Files:
  * [requirements.txt](../../../requirements.txt)
  * [.github/workflows/ci.yml](../../../.github/workflows/ci.yml)
  * [README.md](../../../README.md)
* What changed and why: Added `pytesseract==0.3.13`, `pymupdf==1.26.7`, and `pillow==12.3.0` to `requirements.txt` using the existing exact-pin style. `pymupdf` is shared by both P01 (PDF rasterization for OCR) and P02 (PDF page counting), avoiding a duplicated pinned PDF library per PC-002/P02-T03's coordination requirement. Added one CI step installing `tesseract-ocr` and `libreoffice` via `apt-get` before dependency install and tests. Added a README "System prerequisites" section documenting both system binaries and example install commands for Debian/Ubuntu and macOS. `pymupdf` and `pillow` were later bumped from the originally selected `1.26.5`/`11.3.0` to `1.26.7`/`12.3.0` in post-review commits `5dbac2b` and `fc2f3c1` to resolve dependency-review CVE findings (see the Implementation-Time Plan Updates entry below).
* Completion evidence: `git diff` shows one coherent, non-duplicated set of new lines across all three files; NFR-002 satisfied (exact-pin regex match).
* Validation: `python scripts/validate_repo.py` passed (`REQUIREMENT_PIN` check covers the new lines); CI YAML is valid (reviewed manually; GitHub Actions syntax).

### P01-T04: Tests for the OCR extraction script

* Related phase or task: P01-T04
* Files:
  * [tests/test_ocr_extract.py](../../../tests/test_ocr_extract.py)
* What changed and why: Added tests generating synthetic fixtures at test time (a PNG image with known text via `PIL.ImageDraw`, and a single-page image-based PDF built by embedding that same image into a `pymupdf` document with no text layer) and asserting the script returns non-empty, recognizable text for each. Post-review, added a parametrized regression test that physically rotates the source image 90° and 270° before OCR, so the rotation-selection loop and its confidence-based best-rotation logic (fixed in commit `fc2f3c1` after the CCR-reported font/orientation flakiness) has explicit coverage rather than only the already-upright case. All tests are guarded with `pytest.mark.skipif` keyed on `tesseract --version` succeeding, since this sandbox has no package manager (`brew`/`apt`) to install `tesseract-ocr`; the tests are written to actually execute in CI, which installs it.
* Completion evidence: `pytest tests/test_ocr_extract.py -q` → `4 skipped` locally (expected, no `tesseract` binary here) with no import or collection errors.
* Validation: Skipped locally with an explicit reason (`tesseract-ocr system binary is not installed in this environment`); designed to run and pass in CI's `ubuntu-latest` job, which now installs `tesseract-ocr`.

### P02-T01: Resume length-validation script

* Related phase or task: P02-T01
* Files:
  * [skills/resume-drafter/scripts/validate_resume_length.py](../../../skills/resume-drafter/scripts/validate_resume_length.py)
* What changed and why: New script implementing the fixed `--docx` (page count only, via `soffice --headless --convert-to pdf` + `pymupdf` page count) / `--payload` (word count only, via `count_words()` walking only `summary`, `experience`, `education`, `skills`, `awards`) contract from PC-002. Prints the exact JSON contract fields (`wordCount`, `wordBudget`, `pageCount`, `pageCap`, `withinWordBudget`, `withinPageCap`) and exits non-zero when either check fails, so a calling flow can gate on it.
* Completion evidence: Local unit test confirms `count_words()` returns 15 for a payload mixing `basics`/`unmetRequirements` (excluded) with summary/experience/education/skills/awards content (counted, restricted to the fields `build_docx.py` actually renders) — see `tests/test_validate_resume_length.py::test_count_words_uses_only_body_fields_and_excludes_contact_metadata`.
* Validation: Word-count logic unit-tested and passing locally; end-to-end page-count behavior requires `soffice`, unavailable in this sandbox — validated by P02-T04's guarded tests, designed for CI.

### P02-T02: Wired length validation into resume-drafter's delivery flow

* Related phase or task: P02-T02
* Files:
  * [skills/resume-drafter/SKILL.md](../../../skills/resume-drafter/SKILL.md)
* What changed and why: Added `Flow` step 8, running `validate_resume_length.py` against the rendered `.docx` and the same approved payload, immediately after the existing build step (step 7) and before delivery (step 9). States the hard-gate behavior required by PC-001: a failing result blocks the normal delivery path; the resume must be trimmed and re-rendered (repeating steps 7–8), or delivered only through a distinct, explicit user-approved override checkpoint with the reason disclosed in the chat/summary. Also updated the word-target formatting-rules bullet to state the 2-page cap alongside the word target and reference the validation script by name.
* Completion evidence: `Flow` step 8 and the updated formatting-rules bullet are present in the diff; no "warn and ship anyway" language remains (grep-verified).
* Validation: Documentation-only change; validated by review of the rendered flow text and by P02-T04's script-level tests for the underlying script it invokes.

### P02-T04: Tests for length validation

* Related phase or task: P02-T04
* Files:
  * [tests/test_validate_resume_length.py](../../../tests/test_validate_resume_length.py)
  * [skills/resume-drafter/scripts/fixtures/sample-resume.json](../../../skills/resume-drafter/scripts/fixtures/sample-resume.json)
  * [skills/resume-drafter/scripts/fixtures/sample-resume-over-budget.json](../../../skills/resume-drafter/scripts/fixtures/sample-resume-over-budget.json)
* What changed and why: Extended the existing `sample-resume.json` fixture's content (more experience bullets and detail, still sanitized/generic) so its body word count falls within the 475–600 budget (505 words), making it usable as the within-budget case without breaking `test_build_docx.py`'s section-presence assertions. Added a new `sample-resume-over-budget.json` fixture (710 words) as the deliberately over-budget case. Added unit tests for `count_words()` against both fixtures (no system binary required) plus two full script-invocation tests (build `.docx`, then run `validate_resume_length.py` against it) guarded with `pytest.mark.skipif` on `soffice` availability, matching the OCR tests' pattern.
* Completion evidence: `pytest tests/test_validate_resume_length.py -q` → `4 passed, 2 skipped` locally; the two unit tests (word-count-only, no `soffice` needed) pass unconditionally.
* Validation: Word-count assertions passed locally; full script contract assertions are skipped locally (no `soffice`) with an explicit reason and are designed to run in CI, which now installs LibreOffice.

### P03-T01: Removed the "Requirements not addressed" section from the rendered resume

* Related phase or task: P03-T01
* Files:
  * [skills/resume-drafter/scripts/build_docx.py](../../../skills/resume-drafter/scripts/build_docx.py)
* What changed and why: Removed the `if payload.get("unmetRequirements"):` rendering block from `build_document()`. The `unmetRequirements` field remains accepted by `load_payload()` and the payload schema — only its `.docx` rendering was removed — so it stays available as the data source for chat-only disclosure (P03-T02).
* Completion evidence: `grep -rn "unmetRequirements"` shows the field still referenced only in the `SKILL.md` payload-shape example and test fixtures/tests, never in a `build_docx.py` rendering call.
* Validation: `pytest tests/test_build_docx.py -q` passes with the new negative assertion (see P03-T03).

### P03-T02: Updated resume-drafter's delivery instructions for chat-only disclosure

* Related phase or task: P03-T02
* Files:
  * [skills/resume-drafter/SKILL.md](../../../skills/resume-drafter/SKILL.md)
* What changed and why: Updated the former `Flow` step 7 (now step 9) to state explicitly that the unmet-requirements note is delivered "in the chat/summary response only (never inside the document itself)", replacing the ambiguous "visible" wording.
* Completion evidence: Diff shows the updated step 9 wording.
* Validation: Documentation-only change; consistent with P03-T01's rendering removal.

### P03-T03: Updated tests and fixtures affected by the removal

* Related phase or task: P03-T03
* Files:
  * [tests/test_build_docx.py](../../../tests/test_build_docx.py)
* What changed and why: `test_build_docx_creates_expected_sections` no longer includes `"Requirements not addressed"` in its list of expected present sections; added a negative assertion that the literal text does not appear anywhere in the rendered document, using the existing fixture (which still includes an `unmetRequirements` entry), proving the field is accepted but no longer rendered.
* Completion evidence: `pytest tests/test_build_docx.py -q` → `13 passed`.
* Validation: Run, passed.

### P04-T01: Added an explicit section-selection question to the resume-drafter flow

* Related phase or task: P04-T01
* Files:
  * [skills/resume-drafter/SKILL.md](../../../skills/resume-drafter/SKILL.md)
* What changed and why: Inserted a new `Flow` step 3 (before any drafting begins, immediately after career-document/job-requirements loading and validation) asking the user which optional sections — Skills, Awards, or both — to include, using a fixed-choice question. Summary, Experience, and Education remain always-included and are excluded from the question, matching `build_docx.py`'s actual rendering scope (Certifications is not offered, since `build_docx.py` does not render it — no change to that non-goal was made). Updated the former end-of-flow approval step (now step 5) so its wording no longer implies the section list itself is still open at that point; it now only reviews drafted content within the already-chosen sections.
* Completion evidence: Diff shows the new step 3 and the updated step 5 wording; renumbered `Flow` steps 4–9 remain internally consistent.
* Validation: Documentation-only change; validated by review of the full renumbered `Flow` section for consistency.

## Implementation-Time Plan Updates

### D6 resolved: exact pip dependency versions selected

* Affected plan area or markers: `## User Decisions and Requirements` → Planning Decisions and Feedback, row D6
* What changed: D6's status changed from `proposed`/agent-owned-pending to `resolved`, recording the versions initially selected during P01-T03/P02-T03 implementation: `pytesseract==0.3.13`, `pymupdf==1.26.5`, `pillow==11.3.0`. Those two PDF/image library pins were subsequently bumped post-review to `pymupdf==1.26.7` and `pillow==12.3.0` (commits `5dbac2b`, `fc2f3c1`) after the PR's `dependency-review` CI check flagged known CVEs in the originally selected versions (Pillow: `GHSA-whj4-6x5x-4v2j`, `GHSA-cfh3-3jmp-rvhc`, `GHSA-4x4j-2g7c-83w6`, `GHSA-r73j-pqj5-w3x7`, `GHSA-fj7v-r99m-22gq`, `GHSA-wjx4-4jcj-g98j`, `GHSA-5xmw-vc9v-4wf2`; PyMuPDF: `GHSA-cxqh-p2w9-fmr7`). The current, authoritative `requirements.txt` state is `pytesseract==0.3.13`, `pymupdf==1.26.7`, `pillow==12.3.0`.
* Why: This was an explicitly agent-owned, non-blocking decision reserved for implementation; the plan's own success criteria required recording the resolved detail once selected. The later version bumps were CVE remediation, not a reopened decision.
* Triggering evidence: `pip index versions` lookups for `pytesseract`, `pymupdf`, and `pillow` during P01-T03/P02-T03 implementation (see this file's Completed Work entries above); GitHub Advisory Database lookups for the flagged GHSA IDs during post-review CI triage.
* User answer or decision: None required; D6 was agent-owned per the plan's Decisions table.
* Reconciliation performed: Updated the D6 row to record the current, authoritative pinned versions; no other current-state sections needed a change since this is a fully agent-owned, non-divergent detail.
* Planning and critique state: Not needed — no new critique required; this is a direct planner-scope detail resolved during implementation, consistent with the plan's own classification of D6.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|-------|-------|--------|---------------------|
| `pytest -q` (full suite) | Full plan | Passed | 49 passed, 6 skipped locally (`tests/test_ocr_extract.py` x4 — including the post-review parametrized 90°/270° rotation regression test, `tests/test_validate_resume_length.py` x2 — both skip on explicit `tesseract`/`soffice` availability checks; this sandbox has no `brew`/`apt` to install either system binary) |
| `python scripts/validate_repo.py` | Full plan | Passed | Prints `Validated 3 skills, plugin and marketplace JSON, workflow SHA pins, Dependabot policy, dependency gates, exact dependency pins, and job-requirements round-trip.` with the new pinned dependencies present |
| OCR end-to-end (`tests/test_ocr_extract.py`) | P01-T04 | Skipped (environment limitation) | `tesseract-ocr` system binary is not installable in this sandbox (no `brew`/`apt-get`); CI installs it explicitly in `.github/workflows/ci.yml` and will execute these tests |
| Length-validation end-to-end (`tests/test_validate_resume_length.py`, script-invocation tests) | P02-T04 | Skipped (environment limitation) | LibreOffice (`soffice`) is not installable in this sandbox; CI installs it explicitly and will execute these tests |
| Word-count unit tests (`tests/test_validate_resume_length.py`, `count_words` tests) | P02-T01, P02-T04 | Passed | Run locally without any system binary dependency |
| `build_docx.py` regression suite (`tests/test_build_docx.py`) | P03 | Passed | 13 passed, including the new negative "Requirements not addressed" assertion |

## Pre-Review Reconciliation

* Plan markers and task-local context: Current — all P01–P04 phase and task markers are checked; D6 resolved.
* Completed-work evidence and handoff prose: Current — every completed-work item above has files, rationale, and evidence.
* Validation, blockers, remaining work, and follow-up items: Current — see Validation Record, Blockers, Remaining Work, and Follow-Up Items below.
* Review readiness: Ready — full plan implemented, all local validation passed or explicitly skipped with a recorded environment-limitation reason; no open decisions or blockers remain.

## Blockers

* none

## Remaining Work

* none — all four phases (P01–P04) and their tasks are complete

## Follow-Up Items

* Canonical plan list: [.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md](../../plans/2026-09-20/resume-builder-repeatability-plan.md), `## Follow-Up Items`
* none — the plan's Follow-Up Items section records `None`, and no new follow-up work was discovered during implementation

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: Full plan; completed P01 (P01-T01–T04), P02 (P02-T01–T04), P03 (P03-T01–T03), P04 (P04-T01); no remaining active-plan markers
* Validation coverage: `pytest -q` (49 passed, 6 skipped with explicit environment-limitation reasons) and `python scripts/validate_repo.py` (passed) run locally; the 6 skipped tests are designed to run in this repo's CI, which now installs `tesseract-ocr` and `libreoffice`
* Blockers: none
* Current plan updates: D6 (exact pip dependency versions) resolved during implementation and recorded in the plan's Decisions table
* Planning and critique state: Current and ready; no new critique required (D6 resolution is a direct, non-divergent implementation detail, not a plan change needing review)
* Follow-up items: none
* Review readiness: Ready for `/rpi-review`
* Continuation owner: user

## Post-Review Addendum (Copilot Code Review follow-up)

After `/rpi-review` recorded a Conformant outcome, subsequent Copilot Code Review passes on the PR identified six further findings, all addressed directly (no plan or scope change):

* `skills/resume-drafter/SKILL.md`: added a "neither" choice to the section-selection question (a user could not previously exclude both Skills and Awards); corrected the build/validate example commands to reference a shared `path/to/approved-resume.json` placeholder instead of the bundled test fixture, so the documented hard gate cannot be read as validating sample data.
* `skills/resume-drafter/scripts/validate_resume_length.py`: `count_words()` previously summed every string nested under a section, over-counting fields `build_docx.py` never renders (e.g. an award's `title` when `details` is present). Rewritten to reuse `build_docx.py`'s own field-selection helpers (`role_dates`, `education_details`) and per-entry rendered-field selection, so the word count always matches what is actually rendered; added a decorative-token filter (`_count_words`) so renderer join characters like the em-dash are not counted as words.
* `tests/test_validate_resume_length.py`: updated the existing word-count unit test's expected value (16 → 15) to reflect the corrected award-field counting, added a test asserting an award's `title` is excluded when `details` is present, and added a mocked-`count_rendered_pages` regression test proving `withinPageCap` can independently report `false` for an in-budget, over-page-cap resume (previously only the over-word-budget case was tested).
* `README.md`: added a "Python runtime dependencies" step (`pip install -r requirements.txt`) distinct from the contributor-only `requirements-dev.txt` instructions, so a fresh direct/marketplace install documents both the system binaries and the Python packages OCR/length-validation require.
* `.copilot-tracking/reviews/logs/2026-09-20/resume-builder-repeatability-review.md`: appended a Post-Review Addendum noting the local skip count moved from 4 to 6 after a later rotation-regression test was added, without rewriting the review's original assessed evidence.

Re-validated after these fixes: `pytest -q -rs` (51 passed, 6 skipped, same environment-limitation reasons) and `python scripts/validate_repo.py` (passed) run locally.

## Post-Review Addendum 2 (perf/robustness follow-up)

Two lower-priority findings from a subsequent Balanced-effort review, addressed directly:

* `skills/career-document-builder/scripts/ocr_extract.py`: `ocr_best_rotation()` previously ran Tesseract twice per rotation (`image_to_data` for confidence, `image_to_string` for text). Rewritten to use `pytesseract.run_and_get_multiple_output(..., extensions=["txt", "tsv"])`, a single Tesseract invocation per rotation that returns both the text and a parseable TSV confidence report, halving the OCR work for the multi-rotation, multi-page PDF path.
* `skills/resume-drafter/scripts/validate_resume_length.py`: `convert_docx_to_pdf()` now passes an isolated `-env:UserInstallation=<per-call tmp profile>` and `--norestore` to `soffice`, so validation no longer contends with an already-running or concurrent LibreOffice instance (profile locking/command forwarding could otherwise leave a conversion without the expected PDF).

Re-validated: `pytest -q -rs` (51 passed, 6 skipped, same environment-limitation reasons) and `python scripts/validate_repo.py` (passed) run locally. The OCR and soffice code paths themselves remain unexercised locally (no `tesseract`/`soffice` in this sandbox) and are designed to run in CI.

## Post-Review Addendum 3 (tracking-record consistency follow-up)

Four low-severity findings from a subsequent Balanced-effort review, addressed directly (no code behavior change):

* Corrected the P01-T01 completed-work summary in this changes record: it still described the obsolete text-length-only rotation heuristic; updated to describe the confidence-based selection actually implemented (commit `fc2f3c1`).
* `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md`: struck through and marked the stale "exact pip versions not yet selected" open question as resolved (it duplicated already-resolved Decision D6); corrected the Artifact Self-Check line that contradicted the Critique Disposition section immediately above it (the critique attempt is complete with a recorded Revise verdict, not "no attempt made").
* `README.md`: the Python runtime dependency install command only worked from a repository checkout (`pip install -r requirements.txt`); added an explicit pinned-package install command as an alternative for direct/marketplace installs with no local checkout.

Re-validated: `pytest -q -rs` (51 passed, 6 skipped, same environment-limitation reasons) and `python scripts/validate_repo.py` (passed) run locally.

## Post-Review Addendum 4 (functional-gap follow-up)

Three findings resurfaced from an earlier review pass as "previously missed" (code unchanged since then), addressed with real functional changes:

* `skills/career-document-builder/scripts/ocr_extract.py`: added a `--page` (1-based) option to OCR only one PDF page, so a mixed PDF's already-readable pages are not needlessly re-OCR'd and a caller can merge the OCR result back in at the correct page position, preserving per-page source pointers. Default (no `--page`) whole-document output now labels each page's OCR text with a `--- Page N ---` marker so merged output stays attributable to a source page. Added `tests/test_ocr_extract.py` coverage for both the default labeled output and the `--page`-scoped single-page output.
* `skills/resume-drafter/SKILL.md`: the length-validation hard gate previously only described a trim-and-retry path, which has no valid outcome when the failure is being *under* the word minimum (trimming moves further from the minimum, and fabricating content to reach it is forbidden). The gate now branches: over-budget failures still trim and retry; under-minimum failures first check for additional verified evidence, and only fall back to an explicit user-approved override (now covering all three failure kinds: over the word maximum, over the page cap, or under the minimum with no further evidence) when none exists.
* `tests/test_validate_resume_length.py`: added `test_main_returns_nonzero_when_only_the_page_cap_fails`, which invokes `main()` (not just `validate_length()`) with a mocked over-page-cap count, so a regression where `main()`'s exit code ignored `withinPageCap` would now be caught.

Re-validated: `pytest -q -rs` (52 passed, 8 skipped, same environment-limitation reasons — the two new OCR tests add 2 more `tesseract`-skipped cases locally) and `python scripts/validate_repo.py` (passed) run locally.

## Post-Review Addendum 5 (approval-routing and documentation-drift follow-up)

* `README.md`: fixed the macOS prerequisite command — LibreOffice is distributed by Homebrew as a cask, so `brew install tesseract libreoffice` fails; split into a formula install for `tesseract` and a cask install for `libreoffice`.
* PR description: corrected stale validation totals (49 passed, 4 skipped → 52 passed, 8 skipped) to match the current local run.
* `skills/resume-drafter/SKILL.md`: step 8's corrective-action branches (trim for over-budget, add verified evidence for under-minimum) previously repeated steps 7–8 directly after revising content, bypassing the step 5 approval checkpoint and allowing unapproved wording to reach delivery. Both branches now explicitly route the revised content back through step 5 for approval before re-rendering.
* `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md`: corrected two stale acceptance-criteria descriptions to match implemented behavior — the rotation-selection requirement now describes confidence-based selection (with length as a no-recognized-words fallback) instead of the superseded length-only heuristic, and the length-validation requirement now states that corrective revisions route back through the step 5 approval checkpoint rather than re-rendering directly.

Re-validated: `pytest -q -rs` (52 passed, 8 skipped) and `python scripts/validate_repo.py` (passed) run locally.
