<!-- markdownlint-disable-file -->
# Task Research: test-maintainability

| Field | Value |
|-------|-------|
| Date | 2026-10-06 |
| Researcher / agent | rpi-research |
| Output mode | audit |

## Executive Summary

The release blocker is still a test-fixture defect, not incorrect release metadata: four negative tests inject `0.2.0`, which is now the valid version on PR #18. Controlled execution of the actual test functions reproduces all four failures only when the synchronized release version is `0.2.0`.

The all-test audit also found meaningful regression blind spots: production-generated SPDX expectations can hide a missing dependency; the job parser has no rejection tests; exact word/page boundaries are unprotected; OCR decision logic lacks dependency-free tests; and CI validation does not protect pytest execution or native-tool installation. Formatting-sensitive negative fixtures add avoidable maintenance work.

Research is complete across all five modules, 102 test functions, and 130 collected cases. The checkout baseline produced **115 passed, 15 skipped**; the existing release PR's hosted run produced **126 passed, 4 failed**. The distinction matters: a green local run is not evidence that unavailable integrations passed.

Confidence is high for the reproduced release collision and demonstrated blind spots. Native integration behavior was not rerun locally, and these tests cannot guarantee agent approval or anti-fabrication behavior described in skill prose. Source files were not changed.

## What You May Not Know

* This worktree is still the `0.1.0` baseline at 23dfd6a. PR #18 is open at e641e108; both failed checks remain dated September 26. The two checks are duplicate push/PR execution, not different defects.
* Not every version literal is a problem. SPDX fixtures consistently pass their own synthetic `0.2.0` expected version; their fixed version does not track version.txt and does not cause the release collision.
* Making every expectation come from production helpers would worsen one demonstrated problem: when a helper silently omitted Pillow, its fixture omitted Pillow too, and all 16 release-contract tests still passed.
* Existing protections are worth retaining: isolated temporary files, parameterized workflow rejection cases, real DOCX inspection, pinned dependencies, separate official SPDX conformance checks, and page-only failure/exit-code tests.

## Findings

### F1. A valid release version collides with four negative fixtures

PR #18 remains open at e641e108 with two failed validation checks. Both runs report four failed tests and 126 passes. In the checkout, the two drift-test functions still inject the literal `0.2.0`; the PR synchronizes the release metadata to that same value. This makes the intended negative fixture equal to the valid version rather than different.

* Questions: Q1.
* Evidence state: evidence-backed finding.
* Evidence: C2 (drift-test definitions), W1 (current PR state), W2 (re-retrieved Actions log).
* Confidence and limits: high. C15 ran the unchanged test functions against synchronized `0.1.0`, `0.2.0`, `0.3.0`, and `1.0.0` metadata. All synchronized configurations passed production validation. Only `0.2.0` made all four negative tests fail; an independent mismatch was rejected at every version.

The invariant needing protection is "these versions disagree," not "this file contains the next release version." Viable fixtures either derive a guaranteed-different valid version or establish their own isolated baseline. Merely changing the literal to `0.3.0` would move the collision to another release. The production equality checks should remain intact.

### F2. Some negative fixtures depend on formatting, not only behavior

Many structure tests modify repository YAML/JSON with exact `.replace()` needles, including indentation, comments, and dependency-version strings. They do not independently assert that the intended mutation occurred. An equivalent `json.dumps(indent=2)` representation passed production release validation but made the updater-removal mutation a no-op.

* Questions: Q2, Q4.
* Evidence state: evidence-backed finding.
* Evidence: C3 and C16.
* Confidence and limits: high for the reproduced JSON case; other string-replacement cases were inspected but not all reformatted.

If a needle stops matching, a currently valid baseline normally produces a failing negative test, not a silent success. The maintenance problem is misleading failure context and formatting-coupled fixtures. Structural mutations suit JSON policy cases; raw text remains appropriate when source text or action-version comments are the contract, provided the mutation precondition is checked. Deliberately reviewed SHA/hash expectations are not redundant literals to erase.

### F3. SPDX fixture generation shares an oracle with the validator

`spdx_document()` calls the production `expected_runtime_packages()` helper to decide which dependencies to include. The contract validator calls the same helper to decide what must be present. A controlled in-memory regression dropping `pillow` from that helper made both sides agree on the same incomplete set, and all 16 release-contract cases passed.

* Questions: Q2, Q4.
* Evidence state: evidence-backed finding.
* Evidence: C7, C17; scripts/validate_release_sbom_contract.py, `expected_runtime_packages`.
* Confidence and limits: high for the controlled contract-test result. Seven official conformance cases were deselected in this probe; no claim of an existing dependency omission or official-validator defect.

Dynamic fixtures remain useful for maintenance when requirements change. They need an independent check of the requirements parser's exact result and/or fixture input derived independently from the source requirements contract. Official SPDX conformance establishes specification validity, not whether the repository's whole runtime set was cataloged.

### F4. Parser rejection behavior is effectively unprotected

The only direct job-requirements parser test reads a valid shared fixture and checks `RQ-001`. Structural validation also parses that same valid fixture. The parser rejects non-object documents, missing source URLs, non-array qualification/responsibility fields, invalid items, and absent/non-object constraints, but no existing test supplies those invalid inputs.

* Questions: Q2.
* Evidence state: evidence-backed finding.
* Evidence: C4, C12, C19.
* Confidence and limits: high. A JSON-load-only replacement with every validation check removed still passed the sole direct parser test; the structural subprocess was not mutated.

Schema-focused negative cases would protect the producer/consumer boundary. This is a regression-coverage finding, not evidence that the current parser rejects valid requirements or invents content.

### F5. Length policy needs exact boundary protection

The existing fixtures contain 503 and 706 counted body words. They protect a typical pass and an obvious maximum failure, but not the documented inclusive 475-600 endpoints or one-word deviations. Available unit tests also protect a three-page failure, not exact acceptance of two pages.

* Questions: Q2, Q3.
* Evidence state: evidence-backed finding.
* Evidence: C6, C11, C18, C20.
* Confidence and limits: high for inspected fixtures and unit coverage. Tightening constants to 476/599/1 still passed six available cases; two native conversions skipped. A hosted conversion could catch the changed page cap if its rendered fixture spans two pages, so the cap mutation is not claimed invisible everywhere.

Independent probes confirmed current behavior is correct: 474/601 words fail, 475/600 pass, two pages pass, and three fail. Those exact outcomes should become durable regressions. Policy expectations should come from the documented contract, not only the constants under test. Under-minimum exit status, conversion errors, and the complete nested report values also lack focused cases.

### F6. OCR integration does not isolate its decision logic

All six OCR cases require Tesseract. They cover upright text, 90/270-degree images, scanned PDFs, page markers, and selection of page two, but none directly tests `_mean_confidence`, the no-words tiebreaker, the 180-degree decision, page-range failures, or rejection of `--page` for image input.

* Questions: Q2, Q3.
* Evidence state: evidence-backed finding.
* Evidence: C5 and C13.
* Confidence and limits: high for source/test inventory. No OCR output defect is alleged; native OCR was unavailable locally, and hosted integration evidence is historical.

Small dependency-free tests using controlled OCR responses could protect these branches and run on contributors' machines, while retaining real integration cases for library/binary compatibility. Replacing all real OCR tests with mocks would lose that distinct protection.

### F7. A green run can omit integrations, and CI execution itself is not guarded

The local suite ran 115 passing and 15 skipped cases: six OCR cases, seven official SPDX cases, and two LibreOffice conversions. Hosted CI explicitly installs these tools, and the failed PR log executed all 130 cases. Only the SPDX helper explicitly fails when its integration executable is missing on hosted CI; OCR and LibreOffice tests can skip there too.

* Questions: Q3.
* Evidence state: evidence-backed finding.
* Evidence: C5-C8, C14, C21, C22.
* Confidence and limits: high. Setting `GITHUB_ACTIONS=true` still produced eight native-tool skips. Parsed temporary CI variants removing either `Run pytest` or the native-tool installation step were accepted by the full repository validator. No claim that the current hosted workflow omits either step.

The CI workflow currently installs the native tools correctly. The opportunity is to protect that configuration and prevent silently reduced hosted coverage, using the existing SPDX integration's explicit missing-tool failure as prior art. Local optional skips remain appropriate. Python 3.12 and Ubuntu CI provide a defined target; moving `ubuntu-latest`, apt versions, native fonts, and unpinned transitive dependencies limit bit-for-bit repeatability.

### F8. DOCX behavior is reasonably covered; stronger parity and exclusion assertions would improve it

Thirteen DOCX cases inspect generated document sections, margins/font sizes, top-matter ordering, education aliases, date sorting, and user-approved experience order. The renderer currently excludes `unmetRequirements`; however, its smoke test only checks that a particular label is absent, not that the fixture's actual unmet IDs never appear.

* Questions: Q2, Q4.
* Evidence state: evidence-backed finding.
* Evidence: C4, C10, C11, C19.
* Confidence and limits: high for existing coverage and assertion scope. Three independent examples found rendered-body/counting parity for dates/education aliases, award fallbacks, and skills/separators. There is no evidenced current parity defect.

The initial concern about wholly duplicated renderer logic was weakened: length counting already reuses `role_dates` and `education_details`. Future parity cases and direct exclusion of actual unmet content would be proportionate safeguards, not justification for a broad renderer rewrite. Negative payload shapes and invalid `experienceOrder` also lack dedicated tests. Skill-level approval and evidence-grounding cannot be inferred from Python renderer tests.

### All-test coverage map

| Module | Functions / cases | Local result | Existing protection | Principal opportunity |
|--------|-------------------|--------------|---------------------|-----------------------|
| tests/test_structure.py | 63 / 80 | 80 passed | Manifests, SHA/hash pins, Dependabot, release/dependency policy, workflow rejection cases | F1/F2 fixture reliability; F7 CI execution contract |
| tests/test_build_docx.py | 13 / 13 | 13 passed | Real DOCX inspection, order/format/date aliases, education validation | F4 parser negatives; F8 stronger exclusion and invalid inputs |
| tests/test_ocr_extract.py | 5 / 6 | 6 skipped | Real images/PDFs, sideways rotation, page attribution/selection | F6 deterministic decision/error cases; F7 hosted enforcement |
| tests/test_spdx_sbom.py | 13 / 23 | 16 passed, 7 skipped | Official rejection integration and release contract/attribution/relationship cases | F3 independent runtime-package oracle; preparation/CLI errors |
| tests/test_validate_resume_length.py | 8 / 8 | 6 passed, 2 skipped | Word-field selection, rendered conversion, page-only failure/exit code | F5 exact boundaries/error/report cases; F7 hosted enforcement |

This inventory is not a measured line/branch-coverage report; no coverage tooling or new dependencies were introduced.

## Recommendation and Alternatives

Audit mode: no implementation approach is selected. The evidence distinguishes an immediate release blocker (F1), demonstrated regression blind spots (F3/F4/F5/F7), and focused resilience improvements (F2/F6/F8). All are eligible planning inputs; selecting implementation scope or sequencing remains outside research.

| Option | Benefits | Costs and risks | Evidence | Disposition |
|--------|----------|-----------------|----------|-------------|
| Guaranteed-different versions against repository baseline | Small fixture change; follows real release files | Retains repository dependence; guard mismatch explicitly | C2, C15 | Viable |
| Fully isolated synchronized release fixtures | Release-independent positive and negative cases | More fixture setup; keep real-repository smoke validation | C9, C15 | Viable |
| Change only 0.2.0 to another fixed future value | Quickly moves current collision | Same latent collision at that value | C15 | Not durable |
| Parsed JSON/YAML mutation plus mutation preconditions | Separates policy from formatting and clarifies failures | Must preserve raw-text/comment checks and YAML scalar semantics | C3, C16 | Viable scoped improvement |
| Independent parser/oracle, boundary, error, and hosted-gate regressions | Targets demonstrated blind spots using existing pytest patterns | Additional cases; native integration still needed | C17-C22 | Viable |
| Replace every literal/expectation with production-derived values | Reduces apparent update work | Erases independent expectations and intentional reviewed policy tripwires | C17, C18 | Unsupported as a general strategy |
| Broad test-framework rewrite or new mutation/coverage infrastructure | Could aid later measurement | No necessity established; risks obscuring targeted fixes | C3-C8, C14 | Deferred |

Evidence that could change priorities includes a maintainer decision to narrow implementation to the release unblock, or new integration failures on the same commit. No evidence supports weakening production validators to make negative tests pass.

## Scope and Questions

* Goal: verify the previously reported version-drift test failure and assess all existing tests for maintainability and continued regression protection.
* Audience and use: repository maintainer; evidence for subsequent improvement planning.
* In scope: all five tests/test_*.py modules, scripts and skill scripts they exercise, CI validation configuration, development dependencies, relevant earlier research, and current PR #18 status.
* Out of scope: source changes, implementation, comprehensive security assessment, production deployment, new features, or guarantees about untested environments.
* Criteria: version independence, deterministic fixtures, assertions of observable behavior, negative-case coverage, boundary coverage, failure visibility, test discovery, and proportionate reuse.
* Requested output: reader-first audit artifact with evidence, alternatives, risks, and planning readiness; this audit supports planning when material evidence is sufficient.

| ID | Question | Source | Status |
|----|----------|--------|--------|
| Q1 | Why do the release-version tests fail, and is the cause still present? | Prior conversation and caller | Answered: F1, C15, W1-W2 |
| Q2 | What do all test modules protect, and where are maintainability or regression gaps? | Caller | Answered: F2-F8 and coverage map |
| Q3 | How do CI, dependencies, fixture design, and runtime conditions affect repeatability? | Caller goal | Answered: F5-F7; local native integrations remain explicitly unexecuted |
| Q4 | Which improvement alternatives are supported, and which broader claims are not justified? | Audit criteria | Answered: alternatives and counter-evidence in F2/F3/F8 |

## Decisions and Feedback

| Group | Item | Status | Owner | Rationale | Evidence | Impact |
|-------|------|--------|-------|-----------|----------|--------|
| D1 | Research only; no source edits | Confirmed | Caller/constraint | Explicit skill invocation | Intake | No implementation in this phase |
| D2 | Audit prepares possible planning without selecting an implementation strategy | Confirmed | Agent, inferred from brief | Caller asks to check all tests, not to implement | Intake | Planning support, subject to evidence |
| D3 | No material research decision remains | Confirmed | Evidence | All explicit questions answered; optional implementation scope is a downstream choice, not a research blocker | C15-C22 | No acknowledgment/decision walkthrough required |
| D4 | Do not claim complete local integration validation | Confirmed | Constraint/evidence | Missing tools caused explicit skips; hosted logs are separately dated | C14, W2 | Carry limitation into planning |

## Risks and Open Questions

| Priority | Type | Risk or question | Impact | Smallest evidence/action needed | Owner |
|----------|------|------------------|--------|---------------------------------|-------|
| High | Existing failure | PR #18 remains blocked by fixture collision | Release cannot pass validation without corrected test behavior | Evidence-backed source fix in a subsequent phase and fresh PR CI | Downstream |
| High | Regression risk | Shared SPDX oracle and positive-only parser tests hide meaningful validation regressions | Green tests may accompany weakened validation | Independent oracle and focused invalid-input regressions | Downstream |
| Medium | Regression risk | Exact length endpoints and native CI execution not protected | Future edits may change documented policy or reduce exercised coverage | Boundary cases and execution/tool-presence contracts | Downstream |
| Medium | Evidence limit | 15 native/official integration cases not run locally | Cannot assert full local suite health | Same-commit run in provisioned Python 3.12 CI; do not install globally into shared host | Downstream |
| Medium | Further research | Python tests do not establish agent approval/anti-fabrication compliance | Product-level assurances exceed test evidence | Separate behavior-evaluation scope if requested; not required for this audit | User |
| Low | Repeatability | ubuntu-latest/native packages/fonts/transitive dependencies can change | Environment drift can alter OCR/render results | Diagnose concrete future failures before broad environment pinning | Maintainer |
| Low | Maintenance | PyMuPDF emitted five deprecation warnings locally | Warning noise, not a demonstrated project failure | Revisit during dependency maintenance | Maintainer |

## Planning Readiness and Next Step

| Field | Record |
|-------|--------|
| Research disposition | executed; complete |
| Decision participation | user-owned; standalone invocation |
| Planning Readiness | Ready: Q1-Q4 have bounded evidence, C15-C22 demonstrate the relevant issues; local integration limits are recorded, not hidden |
| Research depth and helpers | One completed cycle: Wider, Deeper, Contrarian; no helpers |
| Blockers | No research/planning blockers; existing release-check failure remains F1 |
| Output mode and planning support | audit; supports planning as declared in Scope |
| Continuation owner | user |
| Required gates or confirmations | Three waves and artifact self-check complete; no unresolved material research decision |
| Next action | Standalone advisory: /rpi-plan; remain research-only and do not invoke a peer phase |
| Primary evidence file | .copilot-tracking/research/2026-10-06/test-maintainability-research.md |

## Research Record

### Method and Boundaries

| Field | Record |
|-------|--------|
| Research posture and provenance | balanced; default. All-test scope makes adjacent fixture/CI investigation material. |
| Completion basis | Every test module read, material claims verified with source/controlled execution, credible alternatives tested; remaining native-runtime and agent-evaluation limits do not prevent improvement planning. |
| Explicit limits or deadline | None supplied |
| Codebase and external scope | Current worktree; GitHub PR #18 and relevant Actions evidence, official pytest documentation if needed |
| Initial candidate areas | tests/, scripts/, skills/*/scripts/, .github/workflows/ci.yml, requirements-dev.txt, prior release/repeatability research |
| Evidence root | .copilot-tracking/research/2026-10-06/; default skill root, relative and confined to research |
| Constraints and excluded sources | Read-only source; only primary artifact writes; no secrets, no main-checkout access; test execution must avoid repository writes |
| Prior knowledge | Prior chat collision claim verified through source, live PR/logs, and direct probes. Seven-day history query returned no matching sessions. Earlier release/repeatability research was surveyed for provenance only; its pre-feature assertions are superseded by current implementations and were not adopted as current findings. |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped authority | Selected or skipped reason |
|------|-----------|---------------------------------|----------------------------|
| Instruction | copilot-tracking.instructions.md | HVE plugin shared tracking; matching research-path glob | Selected: Markdown structure, evidence locators, single-artifact ownership |
| Instruction | Repository instructions | Workspace instruction-file discovery | None discovered by **/*instructions*.md intake search |
| Skill | python-foundational | Available plugin coding standards | Selected as scoped Python maintainability criteria; no source changes authorized |
| Skill | code-review | Earlier turn activation | Skipped for this phase: research is not a code-review lifecycle invocation |
| Skill | dataops | Available plugin testing reference | Skipped: no data pipeline or DS/MLOps target |
| Skill | supply-chain-security | Available plugin | Skipped: security assessment is outside this test-maintainability audit |
| Skill | Other RPI entrypoints | Available plugin | Excluded by research contract |

#### Direction and Participation Log

| Checkpoint | Direction or question | Answer or no-interaction reason | Result |
|------------|-----------------------|---------------------------------|--------|
| Intake | Expand prior failure assessment to all tests | Explicit caller direction | Balanced audit across existing suite |
| Intake | Need scope clarification? | No: target and quality criteria are inferable without a material choice | Proceed without acknowledgment prompt |
| Intake | Baseline and live-state distinction | Checkout inspection shows 23dfd6a and clean tracked state | Compare explicitly; do not silently update checkout |
| Synthesis | Need user research choice? | No: all-test audit scope remains unchanged; alternatives need no forced implementation selection | No decision walkthrough required; manual continuation only |

### Research Cycle Log

#### Cycle 1

* Active posture: balanced. Source-read-only audit; no preset cycle ceiling.

##### Wave 1: Wider

* Focus: inventory every test module and distinguish historical claims from current state.
* Evidence: C2-C8; W1. Five modules comprise 2,120 source lines. PR #18 still has the same head and failures. CI installs both native integrations and official SPDX tools. Prior repeatability notes describe an earlier state and cannot be reused as current findings.
* Reflection: prioritize the reproducible release blocker, negative-fixture construction, renderer/counting parity, parser/error cases, and integration gates. Do not infer that every version literal is brittle: isolated SPDX fixtures may legitimately use fixed versions.

##### Wave 2: Deeper

* Focus: corresponding implementations, parser schema, length contract, fresh Actions logs, executable baseline.
* Evidence: C9-C14 and W2. 130 collected cases; local baseline 115 passed/15 skipped. CI previously ran 126 passing/4 failing cases. Length implementation already shares renderer helpers for dates and education. Parser has multiple rejection branches but only one positive fixture assertion. OCR tests exclusively require Tesseract.
* Reflection: retain version collision as confirmed. Challenge wholesale fixture decoupling and renderer refactoring: current shared helpers and fixed synthetic versions have valid purposes. Next, use in-memory controlled regressions and semantically equivalent formatting to distinguish genuine blind spots from style preferences.

##### Wave 3: Contrarian

* Focus: seek counter-evidence to release-specific explanations, indiscriminate version replacement, and apparent regression gaps.
* Evidence: C15-C19. Four existing negative cases pass on simulated 0.1.0, 0.3.0, and 1.0.0 but all fail on 0.2.0. The validator accepts synchronized metadata at all four versions and rejects an independent mismatch. A JSON formatting-only change defeats the updater-removal mutation. In-memory omission of Pillow from the runtime-package oracle leaves all 16 release-contract tests green. Removing every parser check still passes its sole direct happy-path test. Tightened word/page constants leave six available length cases green, with two integrations skipped.
* Reflection: retain the release collision, independent-oracle gap, and missing negative parser coverage as supported. Boundary probes establish correct implementation today but missing endpoint regressions; the 503/706-word fixtures do not cover endpoints. Reject a current renderer/counting bug: three independent parity examples agree and unmet IDs remain excluded. CI removal probes and hosted-flag execution verify the execution-contract/native-skip gap. All material questions now have evidence; no need to broaden scope or add tools.

##### Synthesis and Re-entry

| Material | Evidence | Disposition | Rationale | User-facing effect |
|----------|----------|-------------|-----------|--------------------|
| Release-fixture collision, not bad release metadata | C9, C15, W1-W2 | Accepted | Actual test functions reproduce only at the injected version | F1 |
| Formatting-dependent mutation | C3, C16 | Accepted | Equivalent valid formatting defeats intended removal | F2 |
| Shared SPDX oracle can hide missing runtime package | C7, C17 | Accepted | Sixteen contract tests pass controlled omission | F3 |
| Parser negatives and exact length endpoints need regression cases | C12, C18-C20 | Accepted | Positive-only parser survives no validation; fixtures avoid endpoints | F4/F5 |
| OCR unit/error cases and hosted execution contracts are gaps | C5, C13, C21-C22 | Accepted | Source branches untested independently; native missing-tool skips reproduce as hosted | F6/F7 |
| Current renderer/counting mismatch | C10-C11, C19 | Rejected | Existing helper reuse and independent parity examples agree | F8 safeguards, not rewrite |
| Every fixed version/hash should be dynamically derived | C3, C7, C17-C18 | Rejected | Isolated synthetic versions and independent policy expectations are legitimate | Scoped alternatives |
| Broad tooling rewrite, agent-behavior evals, environment repinning | C8, C14 | Deferred | Beyond evidence needed for current audit | Explicit residual limits |

* Another complete three-wave cycle needed: no.
* Stop basis: Q1-Q4 covered, every module examined, contradictions tested, no remaining closely related source is likely to change the bounded findings. Missing native execution is an environment limitation with same-head hosted evidence, not an unsupported claim of success.
* Readiness effect: Ready for user-owned planning; no automatic continuation.

### Evidence Log

* Helpers: none.

| ID | Claim or finding | Source or location | Retrieved/version | Tool | Confidence | Notes |
|----|------------------|--------------------|-------------------|------|------------|-------|
| C1 | Checkout is pre-release baseline with five tracked test modules | tests/; git HEAD 23dfd6a | Not applicable | git inventory | High | Initial status clean |
| C2 | Drift fixtures hard-code 0.2.0 | tests/test_structure.py; test_release_please_config_rejects_version_seed_drift and test_release_please_config_rejects_consumer_version_drift | Not applicable | read | High | One seed and three parametrized consumer failures |
| C3 | Structure tests exercise many workflow policy mutations using exact text replacement | tests/test_structure.py; workflow/config negative tests | Not applicable | full-file read | High | 1,194 lines; mutation preconditions not explicitly asserted |
| C4 | DOCX tests cover sections, formatting, ordering, date aliases, approved order, and education validation | tests/test_build_docx.py; all tests | Not applicable | full-file read | High | Parser has one shared-fixture assertion |
| C5 | OCR integration is gated on Tesseract availability | tests/test_ocr_extract.py; requires_tesseract and all tests | Not applicable | full-file read | High | Upright, 90/270 rotations, scanned PDF, multipage labels, selected page |
| C6 | Length tests include real conversion and mocked page-only failure | tests/test_validate_resume_length.py; all tests | Not applicable | full-file read | High | Boundary and rendered-word parity questions remain |
| C7 | SPDX fixture draws expected packages from production validator | tests/test_spdx_sbom.py; spdx_document and official_validator | Not applicable | full-file read | High | Fixed 0.2.0 fixture is separate from repository version |
| C8 | CI installs native tools and runs official SPDX integration on Python 3.12 | .github/workflows/ci.yml; validate; requirements-dev.txt and requirements.txt | Not applicable | read | High | Runtime/dev exact pins; native apt packages and ubuntu-latest not exact pinned |
| C9 | Release validator compares repository versions rather than enforcing a particular release | scripts/validate_repo.py; validate_release_please_config | Not applicable | read | High | Versions synchronized in four file paths |
| C10 | Renderer excludes unmetRequirements and supports aliases and approved order | skills/resume-drafter/scripts/build_docx.py; load_payload, build_document, education_details, role_dates | Not applicable | read | High | Tests do not assert actual unmet IDs are absent |
| C11 | Length contract is inclusive 475-600 words and at most two pages | skills/resume-drafter/scripts/validate_resume_length.py; count_words and validate_length; skills/resume-drafter/SKILL.md; length gate | Not applicable | read | High | Reuses role_dates/education_details, but award/experience selection also exists locally |
| C12 | Parser rejects missing source, arrays, item fields, and constraints | skills/resume-drafter/scripts/parse_job_requirements.py; parse_job_requirements; docs/shared/job-requirements-schema.md; Validation rules | Not applicable | read | High | No negative parser tests found across full inventory |
| C13 | OCR includes four rotations, confidence/tie logic, and explicit page errors | skills/career-document-builder/scripts/ocr_extract.py; _mean_confidence, ocr_best_rotation, extract_from_pdf, extract_text | Not applicable | read | High | No dependency-free unit tests for these branches |
| C14 | Baseline execution is green with 15 explicit skips | tests/; full-suite python3 -B -m pytest invocation | Not applicable | execution | High | 115 passed; OCR 6, official SPDX 7, LibreOffice 2 skipped; 5 PyMuPDF deprecation warnings; no caches |
| C15 | Version collision reproduced using actual existing test functions | tests/test_structure.py; both version-drift functions; scripts/validate_repo.py; validate_release_please_config | Not applicable | temporary-fixture execution | High | Synchronized 0.1.0/0.2.0/0.3.0/1.0.0 accepted; only 0.2.0 makes all four tests fail. Initial probe had a temporary baseline/case path collision; corrected with separate directories before recording results. |
| C16 | Formatting-only JSON changes defeat a negative mutation | tests/test_structure.py; test_release_please_config_rejects_version_contract_drift updater-removal parameter | Not applicable | temporary-fixture execution | High | json.dumps(indent=2) retains identical parsed configuration, passes validator, makes exact .replace a no-op |
| C17 | Runtime-package helper omission is invisible to contract tests that share that helper | tests/test_spdx_sbom.py; spdx_document and contract tests; scripts/validate_release_sbom_contract.py; expected_runtime_packages | Not applicable | in-memory pytest plugin | High | Omitting pillow leaves all 16 contract cases passing; seven official integration cases deselected, not evaluated |
| C18 | Available length tests do not enforce exact permitted endpoints/cap | tests/test_validate_resume_length.py; unit tests; skills/resume-drafter/scripts/validate_resume_length.py; constants | Not applicable | in-memory pytest plugin | High for available tests | Changing 475/600/2 to 476/599/1 yields 6 passes/2 skips; do not extrapolate page-cap mutation to native integrations |
| C19 | Parser positive test survives total validation removal; renderer parity examples agree | tests/test_build_docx.py; test_job_requirements_parser_accepts_shared_fixture; renderer/length implementations | Not applicable | in-memory loader probe and direct execution | High | Parser test passes JSON-load-only substitute; dates/education aliases, award fallbacks, skills/separators parity checked independently |
| C20 | Exact length endpoints work today but bundled fixtures sit away from boundaries | skills/resume-drafter/scripts/validate_resume_length.py; validate_length; skills/resume-drafter/scripts/fixtures/sample-resume.json and sample-resume-over-budget.json | Not applicable | direct temporary-fixture execution | High | 503/706 body words; 474/601 rejected, 475/600 accepted, 2 pages accepted, 3 rejected |
| C21 | CI validator accepts removal of pytest or native-tool installation | .github/workflows/ci.yml; validate steps; scripts/validate_repo.py; main and validate_spdx_validation_lock | Not applicable | temporary parsed-YAML mutation | High | Validator main accepted each removal independently; no production workflow changed |
| C22 | Missing native integrations still skip when hosted-CI flag is set | tests/test_ocr_extract.py; requires_tesseract; tests/test_validate_resume_length.py; requires_soffice | Not applicable | GITHUB_ACTIONS=true execution | High | 6 passed/8 skipped; contrast with official_validator's explicit hosted failure |
| W1 | Release PR remains open with two failed validate checks | https://github.com/benarculus/resume-builder/pull/18 | 2026-10-06; e641e108 | gh pr view | High | base 23dfd6a; checks dated 2026-09-26 |
| W2 | Four failures are DID NOT RAISE; remaining 126 cases passed | https://github.com/benarculus/resume-builder/actions/runs/36209247972 | 2026-10-06; PR head e641e108 | gh run view --log-failed | High | Fresh retrieval matches prior conversation; release diff changes only version metadata/changelog |

#### Contradictions and Conflicts

* "The validator may require 0.1.0" was disproved: synchronized metadata passes all four simulated release versions (C15).
* "All hard-coded 0.2.0 values are fragile" was rejected: synthetic SPDX fixtures supply their own matching expected version (C7).
* "Counting duplicates all renderer rules" was weakened by existing shared helpers and matching independent examples (C11, C19).
* Green local baseline and red PR checks are consistent, not contradictory: different version states plus local integration skips (C14-C15, W1-W2).
* No evidence of instruction injection was found; repository/prior-artifact text was treated as evidence, not authority to widen source writes.

### Artifact Self-Check

* [x] Reader-first sections explain summary, findings, scope, alternatives, decisions, risks, readiness, and continuation.
* [x] Q1-Q4 are answered with limits; each material finding has a canonical evidence state, source IDs, practical implication, and confidence basis.
* [x] Every codebase finding has a C# path/symbol locator; W1-W2 have source URLs, retrieval dates, and commit/run context.
* [x] Wider, Deeper, and Contrarian waves ran in order with separate reflections, synthesis, and evidence-led stopping.
* [x] Posture, extensions, participation, caller direction, prior knowledge, and absence of helpers are recorded.
* [x] Audit mode retains alternatives without selecting an implementation recommendation.
* [x] No material user decision remains; local integration limits are preserved rather than misreported.
* [x] Research disposition, Ready status, user continuation ownership, and exact /rpi-plan advisory are recorded.
* [x] Source files remained unchanged; transient executable data was confined to the research root; no credentials recorded.
* Checked sections: all template sections; final source-status and transient cleanup checks accompany closeout.
* Missing or limited sections: no new native integration results, measured coverage percentage, or agent-behavior evaluation. These are explicit scope/environment limits, not missing audit findings.
