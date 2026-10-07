<!-- markdownlint-disable-file -->
# RPI Changes: Test maintainability

## Metadata

* Task ID: `test-maintainability-2026-10-06`
* Related plan: [.copilot-tracking/plans/2026-10-06/test-maintainability-plan.md](../../plans/2026-10-06/test-maintainability-plan.md)
* Implementation date: `2026-10-06`

## Execution Status

* Status: Complete for full-plan source implementation and available local validation; hosted integration evidence remains pending.
* Declared invocation scope: full plan.
* Completed scope markers: `P01`, `P01-T01`, `P01-T02`, `P02`, `P02-T01`, `P02-T02`, `P02-T03`, `P03`, `P03-T01`, `P04`, `P04-T01`.
* All remaining active-plan markers: none.
* Status basis: every task has completed-work evidence; 197 cases collected, 182 passed and 15 explicit local skips; plan permits a documented pending hosted gate.

## Execution Summary

Release fixtures now represent true mismatches at current/future version baselines. Semantic/configuration and raw-source mutations establish their preconditions; independent parser/SPDX, exact length/report, rendered-content, and OCR regressions protect demonstrated gaps. CI policy guards required execution and native provisioning, while missing native tools fail on hosted runs rather than silently skipping.

All 130 original cases remain represented, with 67 additions below the 74-case ceiling. No product runtime script, manifest version, dependency pin, or workflow changed. The optional shared test helper and contributor documentation are included. No remote operation or commit was performed.

## Completed Work

### Release-independent version drift

* Related task: `P01-T01`.
* Files: [tests/test_structure.py](../../../tests/test_structure.py).
* Behavior: negative fixtures compute a guaranteed-different valid version; eight new synchronized/drift scenarios exercise the existing four field-specific negatives at four release baselines.
* Validation: `python3 -B -m pytest -q -p no:cacheprovider tests/test_structure.py -k 'release_please_config or release_please_versions'` passed 17 cases. Initial narrower plan selector passed nine cases but omitted the newly named scenarios; expanded selector covers all.
* Added cases: eight; no removals.

### Deliberate policy fixture mutations

* Related task: `P01-T02`.
* Files: [tests/test_structure.py](../../../tests/test_structure.py).
* Behavior: release configuration changes mutate parsed JSON with explicit preconditions; every remaining exact-text mutation uses `checked_replace` with declared one/all-match intent and missing-target checks. Equivalent compact/expanded JSON retains semantic negative coverage.
* Validation: full structural module passed 92 cases; four additional helper/format cases and all existing cases retained. Scoped AST codemod converted 43 raw mutations; the helper alone retains standard string replacement.
* Added cases: four; no removals.

### Independent parser and SPDX failure contracts

* Related task: `P02-T01`.
* Files: [tests/test_build_docx.py](../../../tests/test_build_docx.py), [tests/test_spdx_sbom.py](../../../tests/test_spdx_sbom.py).
* Behavior: invalid requirements now have explicit rejection tests; synthetic runtime pins have independent expected maps; missing runtime dependencies, preparation preconditions, and CLI failures have observable regression checks.
* Validation: delegated implementation ran `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -rs -p no:cacheprovider tests/test_build_docx.py tests/test_spdx_sbom.py`: 47 passed, seven official SPDX integrations skipped due to unavailable local validator. `git diff --check` passed.
* Added cases: 11 parser and seven SPDX, within 12/eight ceilings; no removals.

### Exact length policy and actual rendered-content protection

* Related task: `P02-T02`.
* Files: [tests/test_validate_resume_length.py](../../../tests/test_validate_resume_length.py), [tests/test_build_docx.py](../../../tests/test_build_docx.py).
* Behavior: independently specified word/page endpoints and report/status contracts are protected; conversion failures surface; rendered-body parity and actual unmet content exclusion have direct checks; invalid payload/order cases are retained or added.
* Validation: delegated implementation ran the combined DOCX/length modules: 50 passed, two LibreOffice integrations skipped, five existing dependency warnings. No product bugs found.
* Added cases: 12 length and eight renderer; ceilings met exactly, no removals.

### Deterministic OCR decisions and errors

* Related task: `P02-T03`.
* Files: [tests/test_ocr_extract.py](../../../tests/test_ocr_extract.py).
* Behavior: confidence averaging/sentinels, selection independent of output length, no-word ties, 180-degree rotation, and page/input errors run without Tesseract; all real integration cases remain.
* Validation: delegated implementation ran the OCR module: nine passed, six existing real integrations skipped because Tesseract is unavailable.
* Added cases: nine, within ten-case ceiling; no removals.

### Mandatory hosted execution and native-tool gates

* Related task: `P03-T01`.
* Files: [scripts/validate_repo.py](../../../scripts/validate_repo.py), [tests/test_structure.py](../../../tests/test_structure.py), [tests/test_ocr_extract.py](../../../tests/test_ocr_extract.py), [tests/test_validate_resume_length.py](../../../tests/test_validate_resume_length.py), [tests/conftest.py](../../../tests/conftest.py).
* Behavior: structural validation protects full-suite pytest/native provisioning, ordering and conditional/failure bypasses; scoped runtime fixtures skip missing tools locally but fail explicitly on GitHub Actions. Dependency-free cases remain executable.
* Validation: delegated implementation ran structural validation successfully and combined structure/OCR/length suite: 127 passed, eight expected native skips; five existing PyMuPDF warnings. `git diff --check` passed.
* Added cases: four CI policy tests and four hosted/local gate cases, within eight/four ceilings; no removals or workflow/runtime-product changes.

### Integrated local evidence and contributor guidance

* Related task: `P04-T01`.
* Files: [README.md](../../../README.md), all five [tests](../../../tests) modules, [tests/conftest.py](../../../tests/conftest.py), [scripts/validate_repo.py](../../../scripts/validate_repo.py).
* Behavior: contributor guidance explains optional local skips, mandatory hosted native/official tooling, and why skipped integrations are not passed evidence.
* Validation: final structural validation and full available suite passed: 182 passed, 15 skipped, five existing PyMuPDF deprecation warnings. Collection counts: structure 96, DOCX/parser 32, OCR/gating 19, SPDX 30, length 20; 197 total. `git diff --check` passed.
* Regression sensitivity: controlled in-memory omission of Pillow now fails the independent missing-package case; tightening documented length/page constants now fails all seven endpoint/report cases. Both probes asserted that failure was expected and returned success without modifying source. CI removal/condition/failure/environment/cwd/line-boundary regressions fail the structural-policy tests.
* Preservation: AST inventory confirms all 102 original test functions remain; per-module original case counts remain represented. Changed tracked paths are only approved test modules, README, and repository validator; shared test helper is new. Runtime product scripts/manifests/workflows/dependency files remain unchanged.
* Hosted gate: unavailable without unauthorized remote actions/global native installation; six OCR, seven official SPDX, and two LibreOffice cases remain explicitly unexecuted locally. This is pending integration evidence, not a claim that those cases passed.

## Implementation-Time Plan Updates

### Full-plan implementation authorization

* Affected plan area: Confirmed User Direction and handoff.
* What changed: user explicitly invoked implementation, authorizing the full existing plan.
* Why: completed standalone planning has advanced to implementation.
* User decision: `/hve-core:rpi-implement`.
* Reconciliation: plan intent and continuation state updated; no scope change or repeat critique.

### Shared fixture preconditions for CI policy tests

* Affected marker: `P03-T01`.
* What changed: later CI mutations can reuse `checked_replace` and its explicit `count` argument.
* Why: `P01-T02` established a scoped helper rather than duplicating mutation preconditions.
* Classification: immediately relevant guidance; no scope/behavior change or user decision.

### Runtime native-tool fixture ownership

* Affected markers: `P03-T01`, `P04-T01`.
* What changed: narrowly shared [tests/conftest.py](../../../tests/conftest.py) provides `_require_native_tool`, `requires_tesseract`, and `requires_soffice`.
* Why: per-test availability decisions allow direct hosted/local enforcement checks without import-time skips masking hosted errors.
* Classification: ordinary local judgment permitted by plan; later task guidance added. No user decision or new critique.

### Prevent inherited CI options from undermining the full-suite contract

* Affected markers: `P03-T01`, `P04-T01`.
* What changed: the validator also rejects workflow/job/required-step overrides of `PYTEST_ADDOPTS` or `GITHUB_ACTIONS`, alternate working directories, and literal multiline commands that normalization would otherwise mistake for a folded command.
* Why: exact command text alone does not guarantee full-suite/hosted gating when inherited environment or command boundaries change.
* Classification: immediately relevant validation refinement within approved `FR-008`; no product change, new task, budget expansion, or critique.
* Evidence: existing CI policy cases now cover those bypasses; the structural module passed all 96 cases.
* Reconciliation: current task requirements clarified; original four-case CI allocation retained.

### Checklist count correction at reconciliation

* Affected area: task metadata and critique provenance.
* What changed: explicitly recorded the actual four phases/seven tasks; earlier planning/critique activation prose said eight tasks.
* Why: final marker-count check found seven, matching the candidate's actual task IDs and all completion entries.
* Classification: factual tracking correction only. No work removed, added, or reassessed; the recorded assessment covers every actual task.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|-------|-------|--------|--------------------|
| Starting worktree status | Full plan | Passed | Only prior tracking artifacts untracked; no source changes |
| Release-config targeted selector | `P01-T01` | Passed | 17 cases including all four baseline versions and true drift |
| Structural module | `P01-T02` | Passed | 92 cases before CI additions; 96 after CI safeguards |
| DOCX/parser + SPDX | `P02-T01` | Passed with skips | 47 passed, seven official-validator skips |
| DOCX/parser + length | `P02-T02` | Passed with skips | 50 passed, two native conversions skipped |
| OCR | `P02-T03` | Passed with skips | Nine deterministic cases passed; six real OCR cases skipped |
| Structure/OCR/length combined | `P03-T01` | Passed with skips | 127 passed, eight native skips; direct hosted/local gate checks passed |
| `python3 -B scripts/validate_repo.py` | Full plan | Passed | All repository checks including CI execution contract |
| `python3 -B -m pytest -q -rs -p no:cacheprovider` | Full plan | Passed with skips | 182 passed, 15 skipped, five existing dependency warnings |
| Collected inventory + original-function/source-scope audit | Full plan | Passed | 197 cases = 130 retained + 67 added; original 102 functions retained |
| Dependency omission counterfactual | `P02-T01`, `P04-T01` | Passed | New independent missing-Pillow case rejects altered oracle (one expected test failure) |
| Policy boundary counterfactual | `P02-T02`, `P04-T01` | Passed | Seven new endpoint/report cases reject changed 476/599/one-page policy (seven expected test failures) |
| `git diff --check` | Full plan | Passed | No whitespace errors |
| Artifact reconciliation | Full plan | Passed after factual correction | Initial check expected eight task markers; actual candidate has seven. Corrected expectation and metadata, preserving historical critique |
| Hosted Python 3.12/native integration | `P04-T01` | Unavailable | No remote actions authorized; missing native tools were recorded in research |

## Pre-Review Reconciliation

* Plan markers and task-local context: current; all phases/tasks checked and shared-helper guidance included.
* Completed-work entries and handoff: complete and reconciled with actual source/result evidence.
* Validation/blockers/remaining work: local checks complete; no remaining active-plan markers; hosted gate pending and not misreported.
* Review readiness: Ready for review of completed source implementation, with the explicit native/official hosted validation limit. Not fully integration-validated or ready to assert release checks have passed.

## Blockers

* No source-implementation or code-review blocker. Integration acceptance is pending: maintainer-authorized fully provisioned Python 3.12 hosted CI must exercise all native/official cases before merge/release success is asserted.

## Remaining Work

* No active-plan tasks remain.
* External validation gate: fully provisioned hosted run and eventual application to PR #18 require user-directed remote actions; none were performed.

## Follow-Up Items

* Canonical plan list: [.copilot-tracking/plans/2026-10-06/test-maintainability-plan.md](../../plans/2026-10-06/test-maintainability-plan.md), `## Follow-Up Items`.
* None.

## Return-to-Caller State

* Implementation execution status: Complete; full plan, all markers checked.
* Validation coverage: 182 passed/15 explicit local skips; collection/preservation/structural/diff checks and regression counterfactuals passed.
* Blockers: no code-review blocker; hosted runtime gate pending before integration/release success.
* Current plan updates: implementation authorization, shared-helper guidance, tightly coupled CI bypass refinement, and completed handoff state.
* Planning and critique state: Ready plan; Complete/Revise critique with PC-001 resolved.
* Follow-up items: none.
* Review readiness: Ready with recorded environment limitations; eligible standalone command `/rpi-review`.
* Continuation owner: user.
