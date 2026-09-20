<!-- markdownlint-disable-file -->
# RPI Plan Critique: resume-builder-repeatability

## Metadata

* Task ID: resume-builder-repeatability
* Critique date: 2026-09-20
* Plan: .copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md
* Critique execution status: Complete
* Critique depth: standard
* Depth provenance: default (no explicit user request for deep critique)
* Invocation consumed: yes
* Attempt ID and kind: resume-builder-repeatability-critique-initial-01 (initial)
* Candidate identity and saved hash boundary: resume-builder-repeatability; sha256 `3612063be5f2aab429bde457c876b6db87cc6fb1b361154f182b6b5d79262bc0` for the saved plan bytes before the parent's reservation metadata update
* Current-dispatch provenance: Parent-dispatched current initial worker; reservation persisted in the plan's `## Critique Disposition` section and dispatched in the same uninterrupted parent execution at 2026-09-20T21:09:21Z
* Original attempt and recovery approval: not applicable

## Inputs and Criterion Boundary

* Task context and caller requirements: Assess the current four-phase implementation plan for repeatable OCR, enforced resume length, chat-only unmet-requirement disclosure, and an upfront section-selection checkpoint; prioritize blockers, contradictions, missing dependency or acceptance coverage, unsupported claims, and material risks without re-litigating user-confirmed decisions D1-D5.
* Research and evidence considered: `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md`, `.copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md`, `skills/career-document-builder/SKILL.md`, `skills/resume-drafter/SKILL.md`, `skills/resume-drafter/scripts/build_docx.py`, `tests/test_build_docx.py`, `skills/resume-drafter/scripts/fixtures/sample-resume.json`, `requirements.txt`, `requirements-dev.txt`, `.github/workflows/ci.yml`, `README.md`, `scripts/validate_repo.py`, and `docs/shared/anti-fabrication-contract.md`.
* Decisions, dependencies, task Goals, and task Requirements considered: D1-D6; FR-001..FR-005; NFR-001..NFR-002; shared dependency files (`requirements.txt`, `.github/workflows/ci.yml`, `README.md`); task-local Requirements, Details, References, and Dependencies across P01-P04.
* Assessment boundary: This critique evaluates the supplied plan and listed repo evidence only. It does not perform external research, implementation, or additional repository discovery beyond the supplied boundary, and it treats the user-confirmed decisions as authoritative unless the plan fails to implement them.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| FR-001, P01, P01-T01..T04 | Partial | The OCR direction is coherent for image OCR and dependency/documentation updates, but the plan requires image-or-PDF input while acceptance coverage only proves an image fixture and leaves the scanned-PDF path unverified. |
| FR-002, FR-003, P02, P02-T01..T04 | Partial | The render-based enforcement goal matches D2/D5, but P02-T02 allows a warned-over-budget resume to escape the gate and P02-T01/P02-T02 do not pin one stable counting interface. |
| FR-004, P03, P03-T01..T03 | Covered | Code removal, skill-flow change, and regression-test updates are all named and aligned with the current `build_docx.py` and `tests/test_build_docx.py` evidence. |
| FR-005, P04, P04-T01 | Partial | The new upfront checkpoint correctly moves the choice earlier and distinguishes mandatory sections, but it overstates existing support for Certifications in the current renderer evidence. |
| NFR-001, P01-T01, P02-T01, P02-T03 | Partial | Cross-platform intent is stated, but the plan's objective evidence path is still Ubuntu CI-centric and does not yet prove the chosen PDF-rendering/page-count path on macOS. |
| NFR-002, P01-T03, P02-T03 | Covered | Exact-pin and shared-file coordination requirements are explicit and grounded in `scripts/validate_repo.py`, `requirements.txt`, `.github/workflows/ci.yml`, and `README.md`. |
| Before/After + phase diagrams | Covered | The diagrams remain internally consistent with the four phases and shared-file impacts; no material diagram contradiction was found. |

## Verdict

* Verdict: Revise
* Rationale: The plan is close to implementation-ready, but three material credibility gaps remain: P02 does not yet enforce failure as a true delivery gate, its validation interface is ambiguous, and P01 does not prove the scanned-PDF OCR path that motivated the work. P04 also overstates existing certification rendering support. These are planner-owned corrections, not new research or user-decision blockers.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: P02 still permits over-budget delivery after warning instead of enforcing the gate

* Related IDs: FR-002, FR-003, D2, D5, P02, P02-T02
* Evidence: `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md` (P02-T02 Goals, Requirements, and Details); `.copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md` (Decision D2, Decision D5)
* Concern: P02-T02 says a failing resume should be "trimmed and re-rendered, or explicitly flag the overage to the user with the reason." That second branch allows the plan to satisfy itself by warning about an overage instead of actually preventing over-budget delivery, which conflicts with FR-002/FR-003's promise that the word and page limits are enforced before delivery.
* Impact: An implementer could preserve the current failure mode—shipping a too-long resume with an explanation—while still claiming the plan was followed.
* Smallest useful change: Rewrite P02-T02 so a failed validation blocks delivery until the resume is revised and re-rendered, or require an explicit user override checkpoint before any exception delivery.
* Action owner: planning parent
* Exact resolving evidence: Revised P02-T02 text, plus any affected executive-summary/readiness language, showing that `withinWordBudget=false` or `withinPageCap=false` cannot pass the normal delivery path.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [Medium]: P02's validation contract does not define one stable source of truth for the word count

* Related IDs: FR-002, FR-003, D2, D5, P02-T01, P02-T02, P02-T04
* Evidence: `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md` (P02-T01 Requirements/Details and P02-T02 Details); `skills/resume-drafter/SKILL.md` (Flow step 6 and word-budget rule)
* Concern: P02-T01 allows word counting from either the rendered `.docx` body text or the intermediate JSON payload, but P02-T02 only adds a post-render validation step and never defines whether the JSON must also be preserved and passed. The result contract is well-formed as output JSON, but the input/CLI contract is not pinned tightly enough to make the count reproducible or to unambiguously exclude contact metadata.
* Impact: Different implementations can count different text while still claiming compliance, and P02-T04 cannot write deterministic regression coverage against an unfixed counting boundary.
* Smallest useful change: Pin one concrete validation interface and counting boundary—for example, require both `--docx` and `--payload`, or require a docx-only counting rule that explicitly excludes top matter/headings—and align P02-T02/P02-T04 to the same interface.
* Action owner: planning parent
* Exact resolving evidence: Revised P02-T01 contract and synchronized P02-T02/P02-T04 task text that name the required inputs, counting boundary, and failure semantics consistently.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-003 -->
### PC-003 [Medium]: P01 does not yet prove the scanned-PDF OCR path it claims to standardize

* Related IDs: FR-001, NFR-001, D1, P01-T01, P01-T03, P01-T04
* Evidence: `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md` (P01-T01 Requirements/Details and P01-T04 Requirements/Details); `.copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md` (Finding 1); `skills/career-document-builder/SKILL.md`
* Concern: P01-T01 requires the OCR script to accept an image or a PDF and specifically calls out avoiding a Poppler-style system dependency through a wheel-bundled PDF renderer, but P01-T04 only requires an image fixture. The real-world failure that motivated the phase included image-only PDFs, yet the plan does not require a PDF test or any acceptance evidence that the chosen rasterization dependency actually works in CI without Poppler.
* Impact: Implementation could ship a working image OCR path while leaving the original scanned-PDF gap unresolved or accidentally adding a second undocumented system prerequisite.
* Smallest useful change: Extend P01-T04 to cover a generated or checked-in image-only PDF fixture and require P01-T03/P01-T04 to prove that only pinned pip dependencies plus CI-installed `tesseract-ocr` are needed for that path.
* Action owner: planning parent
* Exact resolving evidence: Revised P01-T03/P01-T04 text naming a scanned-PDF regression case and the validation evidence that no extra system PDF dependency is required.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-004 -->
### PC-004 [Medium]: P04 offers Certifications as an optional section without supplied evidence that the renderer supports it

* Related IDs: FR-005, P04-T01
* Evidence: `.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md` (P04-T01 Details); `skills/resume-drafter/SKILL.md` (Flow step 4); `skills/resume-drafter/scripts/build_docx.py`
* Concern: P04-T01 says Summary/Experience/Education remain mandatory while optional sections include Skills, Awards, Certifications, and similar, and it further says the existing schema and rendering already treat them as independently optional based on payload presence. The supplied renderer evidence shows support for Summary, Experience, Education, Skills, Awards, and `unmetRequirements`, but no certification rendering path.
* Impact: The planner can ask implementers to add an upfront prompt for a section the current resume renderer cannot demonstrably honor, or falsely treat existing certification support as proven.
* Smallest useful change: Narrow the upfront-choice scope to sections the current renderer evidence supports, or add explicit implementation work if Certifications must be offered now.
* Action owner: planning parent
* Exact resolving evidence: Revised P04-T01 text that either limits the prompt to currently supported optional sections or adds a task/reference covering certification rendering support.
* Decision route: direct planner correction

## Strengths and Residual Risk

* P03 is fully and credibly scoped: the plan covers the code removal in `build_docx.py`, the corresponding flow change in `skills/resume-drafter/SKILL.md`, and the negative regression in `tests/test_build_docx.py` without conflicting with the anti-fabrication contract.
* The shared dependency/CI/README coordination risk is already recognized in P02-T03 and is manageable once the planner resolves the higher-priority enforcement and acceptance gaps above.

## Questions or Blocking Evidence Gaps

* none

## Limitations

* This critique intentionally did not perform external compatibility research or implementation experiments; cross-platform claims were assessed only against the supplied plan, research artifact, and current repository files.
* The saved candidate hash boundary refers to the pre-reservation plan bytes recorded by the planning parent; the current on-disk plan also contains critique-reservation metadata added after that boundary.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning parent
* Smallest next action: Revise P02 so validation failure blocks normal delivery, then tighten P02's input contract and P01's scanned-PDF acceptance coverage in the same planner-owned update batch.
* User response required: no

## Relevant Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md](.copilot-tracking/plans/2026-09-20/resume-builder-repeatability-plan.md) | Plan under critique |
| [.copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md](.copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md) | Research artifact supplying findings and confirmed decisions |
| [skills/career-document-builder/SKILL.md](skills/career-document-builder/SKILL.md) | Current career-document-builder flow lacking an OCR step |
| [skills/resume-drafter/SKILL.md](skills/resume-drafter/SKILL.md) | Current resume-drafter flow, section checkpoints, and word-budget rule |
| [skills/resume-drafter/scripts/build_docx.py](skills/resume-drafter/scripts/build_docx.py) | Current renderer behavior for sections and unmet requirements |
| [tests/test_build_docx.py](tests/test_build_docx.py) | Existing regression coverage for rendered document sections |
| [skills/resume-drafter/scripts/fixtures/sample-resume.json](skills/resume-drafter/scripts/fixtures/sample-resume.json) | Existing fixture referenced by P02/P03 tasks |
| [requirements.txt](requirements.txt) | Direct pinned Python dependencies |
| [requirements-dev.txt](requirements-dev.txt) | Development dependency entrypoint used by CI |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Current Ubuntu CI workflow and dependency-install point |
| [README.md](README.md) | Plugin install and validation documentation |
| [scripts/validate_repo.py](scripts/validate_repo.py) | Repository validator enforcing exact dependency pins |
| [docs/shared/anti-fabrication-contract.md](docs/shared/anti-fabrication-contract.md) | Shared contract constraining disclosure behavior |
| [.copilot-tracking/reviews/plans/2026-09-20/resume-builder-repeatability-plan-critique.md](.copilot-tracking/reviews/plans/2026-09-20/resume-builder-repeatability-plan-critique.md) | This critique artifact |

## Next Steps

Planning parent: apply the four direct planner corrections above in one revision batch, then finalize readiness without requesting another critique.
