<!-- markdownlint-disable-file -->
# Task Research: resume-builder-repeatability

| Field              | Value                                                                             |
|--------------------|-----------------------------------------------------------------------------------|
| Date               | 2026-09-20                                                                        |
| Researcher / agent | rpi-research                                                                     |
| Output mode        | convergence                                                                       |

**Sanitization note:** This artifact documents *workflow behavior* (tool calls, skill flow, word/page counts, section lists) from the user's first end-to-end run of the `benarculus/resume-builder` skills against their real career data. No employer names, dates, titles, certifications, award names, contact details, or other personal career content are reproduced here — findings cite the session log's mechanics (tool names, counts, file structure) rather than its content.

## Executive Summary

* Bottom line: The first real-world run surfaced five concrete, fixable repeatability gaps in the `resume-builder` plugin: (1) OCR for scanned award/review sources was improvised ad hoc with a macOS-only framework and no pinned dependency; (2) the resume-drafter's 475–600-word target was never enforced and produced a ~1,086-word, 4-page document; (3) there is no page-count target or validation at all; (4) unmet requirements are written directly into the delivered `.docx` instead of being surfaced only in the chat/summary step; (5) `resume-drafter` never asks which optional sections (Skills, Awards, etc.) to include before drafting.
* Why this matters: These gaps mean the plugin's output quality and predictability depend on what the agent improvises in the moment (a random OCR path, an unenforced word budget) rather than on the plugin's own documented, testable rules — the opposite of the "repeatable, evidence-based" goal stated in the repo's `README.md` and `SKILL.md` files.
* Research status: Complete for the five requested points. All five are reproducible from direct evidence (session log tool calls, the delivered `.docx`, and the current skill/script source) rather than inference.
* Confidence and uncertainty: High confidence on all five findings — each is grounded in either an exact word count computed from the delivered file, an exact line in `build_docx.py`/`SKILL.md`, or an exact sequence of tool calls in the session log. The only open items are implementation choices (which OCR dependency, which page-count validation mechanism), flagged as decisions below.

## What You May Not Know

* The repo is a **public, marketplace-installable plugin** (`plugin.json`, `.github/plugin/marketplace.json`, `README.md` install instructions), and its CI runs on `ubuntu-latest` (`.github/workflows/ci.yml`). Any OCR fix that only works on macOS (as the first run's improvised approach did) can never run in this repo's own CI and would silently fail for any non-macOS user of the plugin.
* `skills/resume-drafter/SKILL.md` already states a 475–600-word body target and already warns that "line count depends on the selected font, margins, and available width; do not claim that a word or character count guarantees two lines" — the same logic applies to page count, but no equivalent page-level check exists anywhere in the code or tests.
* The `unmetRequirements` payload field is rendered directly into the `.docx` by `build_docx.py` (a "Requirements not addressed" heading + bullets) by design — this is not a bug in the current spec, it is the current spec, and changing it is a deliberate scope decision the user is now making.
* `career-document-builder/SKILL.md` never mentions PDFs, scanned images, or OCR at all; it assumes text-extractable sources. The first run needed OCR only because the user's real award/review sources included scanned images/PDFs, which is a foreseeable input for future users too.

## Findings

### Finding 1 — OCR handling is undocumented, ad hoc, and platform-locked

The session's `career-document-builder` invocation hit non-text-extractable sources (scanned award/review images and image-only PDFs) partway through source inventory. Because neither `career-document-builder/SKILL.md` nor any repo dependency file names an OCR tool, the agent improvised a solution live: it probed for `pdftotext`/`poppler` (absent), tried `pypdf`/`PyPDF2` (text-layer only, useless for scanned images), then installed `pyobjc-framework-Vision` and `pyobjc-framework-Quartz` and wrote a one-off script calling Apple's Vision framework, including manual trial-and-error image rotation (0°, ±90°, 180°) to get usable OCR text.

* Questions: Q1 (repeatability — OCR dependency)
* Evidence state: evidence-backed finding
* Evidence: C1 (session log tool calls — dependency probes and Vision-framework OCR script), C2 (`skills/career-document-builder/SKILL.md` — no image/PDF/OCR handling mentioned), C3 (`.github/workflows/ci.yml:12` — CI runs on `ubuntu-latest`, so a macOS-only OCR path is untestable in this repo's own pipeline and unusable for non-macOS installers of the plugin), W1 (Tesseract OCR ships officially for Linux, Windows, and macOS)
* Confidence and limits: High. The tool-call sequence is directly observable in the session log; the CI platform and skill content are directly observable in the repo. The only uncertainty is which specific cross-platform OCR dependency to standardize on — recorded as Decision D1.

This is exactly the kind of "worked once, by luck of the local machine" behavior that breaks repeatability: a fresh run on Linux/Windows, or a fresh macOS machine without `pyobjc` pre-approved, would either fail outright or re-derive a different ad hoc script.

### Finding 2 — The resume's word target exists in prose but is never enforced, and the actual result was ~1,086 words

`skills/resume-drafter/SKILL.md` states: "Target 475–600 words for the tailored resume body, excluding contact metadata." No code path, script, or test in the repo computes a word count against this target. Counting all paragraph and table text in the delivered `Resume - Principal TPM FDE - Microsoft.docx` gives **1,086 words** across 55 paragraphs — roughly 1.8–2.3x the documented target, with no checkpoint in the session log where the agent computed or checked this number before or after delivery.

* Questions: Q2 (word/page-target enforcement)
* Evidence state: evidence-backed finding
* Evidence: C4 (`skills/resume-drafter/SKILL.md:56` — "Target 475–600 words..."), C5 (delivered `.docx` word count = 1,086, computed directly with `python-docx`), C6 (`tests/test_build_docx.py` — no word/page-count assertions exist)
* Confidence and limits: High — the word count is an exact, reproducible measurement of the attached file, not an estimate.

### Finding 3 — No page-count target or validation exists anywhere in the workflow

The user's stated 4-page outcome is consistent with Finding 2 (roughly 2x the word target plus 10 experience entries, 4 education entries, 9 certifications, 4 awards, and a "Requirements not addressed" section all rendered at once). Neither `SKILL.md` nor `build_docx.py` references a page count, a page-break check, or any rendering pass that would let the agent know how many pages the `.docx` occupies before declaring it delivered. `SKILL.md` already contains the reasoning needed to justify adding one: it acknowledges line/page length depends on font, margin, and width choices baked into the renderer, so only an actual rendered check (not a word-count guess) can confirm page count.

* Questions: Q3 (introducing an explicit 2-page standard)
* Evidence state: evidence-backed finding
* Evidence: C7 (`skills/resume-drafter/SKILL.md:67` — explicit renderer-dependent-length caveat, with no corresponding page check), C5 (delivered doc word/paragraph count), W2 (Tesseract/LibreOffice-class tools are the common cross-platform way to render `.docx`→PDF headlessly and count pages — noted as a candidate mechanism, not independently verified against an authoritative LibreOffice CLI reference in this session; flagged for planning-time confirmation)
* Confidence and limits: High on the gap existing; medium on the exact validation mechanism, which is recorded as Decision D2 rather than asserted as fact.

### Finding 4 — Unmet requirements are written into the delivered resume file itself

`build_docx.py` lines 221–223 render `payload["unmetRequirements"]` as a "Requirements not addressed" heading with bullets directly inside the output `.docx`. This is not accidental: `SKILL.md` step 7 says to "Deliver the `.docx` and the visible unmet-requirements note together." In the observed run, this produced a resume file containing a section listing which job-posting requirements were *not* met (e.g., "PQ-003... unmet") — content a candidate would not want to hand to an employer inside the resume document itself, even though the underlying anti-fabrication intent (never hide a mapping gap from the user) is sound.

* Questions: Q4 (unmet-requirement disclosure location)
* Evidence state: evidence-backed finding
* Evidence: C8 (`skills/resume-drafter/scripts/build_docx.py:221-223`), C9 (`skills/resume-drafter/SKILL.md` step 7), C10 (session log assistant message: "1 unmet requirement flagged in the doc's 'Requirements not addressed' section")
* Confidence and limits: High — this is the current, intentional design, not a bug; the user is asking to change the design, which the evidence fully supports as feasible (the same information already exists in the payload and in the chat-delivered summary before rendering).

### Finding 5 — Section inclusion (Skills, Awards, etc.) is decided by the agent, not asked upfront

`SKILL.md` step 4 says to "Present proposed summary, experience, education, skills, awards, and certifications sections to the user in checkpoints," but in the observed run this happened as a single end-of-flow "approve this draft" question that already listed a synthesized Skills section and 3 selected awards — the user was never asked, before drafting, which optional sections they wanted included at all. The user's stated preference ("I would normally exclude the skills or awards") only surfaces after the fact, as an edit request, rather than as an upfront scoping choice.

* Questions: Q5 (upfront section-selection prompt)
* Evidence state: evidence-backed finding
* Evidence: C11 (session log — final draft-approval question already contains synthesized Skills list and 3 selected awards, asked as one combined yes/no rather than a section-inclusion checklist), C9 (`SKILL.md` step 4 wording, which is satisfied literally but not in the spirit of an upfront choice)
* Confidence and limits: High on the observed behavior; the fix (an explicit multiple-choice checkpoint before drafting begins, e.g. "Which of these sections do you want in this resume: Summary, Experience, Education, Skills, Certifications, Awards?") is a direct, low-risk addition to the existing `SKILL.md` flow.

## Recommendation and Alternatives

* Recommendation or decision state: Implement all five fixes as scoped, additive changes to the existing `SKILL.md` files, `build_docx.py`, and `requirements*.txt` — no architectural change needed. All five decisions (D1–D5) are now confirmed by the user; the artifact is ready for planning.
* Rationale: Every finding traces to a specific, small piece of the current spec or code (C1–C11) rather than a systemic design flaw, so each is independently fixable without destabilizing the anti-fabrication contract or the rest of the pipeline.
* What could change this result: If the user wants OCR/page-validation to depend on an external service instead of local tooling, or wants section selection to be remembered per-user instead of asked every time, the specific mechanism would change but not the underlying finding.

| Option                                                                                     | Benefits                                                                 | Costs and risks                                                                 | Evidence  | Disposition |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------|-----------|-------------|
| Pin a cross-platform OCR dependency (`pytesseract` + system `tesseract`) for scanned sources | Works in `ubuntu-latest` CI and for any installer's OS; matches existing exact-pin convention in `requirements.txt` | Requires a system binary (`tesseract`) beyond pure `pip install`, so install docs/CI need an OS package step | C3, W1    | selected (Decision D1, user-confirmed) |
| Keep macOS-only Vision framework as the default OCR path                                    | Zero extra system binary on macOS; was already proven to work in this session | Cannot run in this repo's own CI; fails silently or not at all for non-macOS plugin users | C1, C3    | rejected |
| Add a render-then-count page-count gate (convert `.docx`→PDF headlessly, count pages, fail/trim over 2) | Directly validates the thing the user cares about (page count), matching `SKILL.md`'s own "don't trust word count for length" caveat | Adds a new dependency/tool to the build step; needs a documented, pinned conversion tool | C7        | selected (Decision D2, user-confirmed) |
| Recalibrate the word budget only (e.g., lower target derived from observed ~271 words/page in the current renderer) without a render-time check | No new dependency | Still a proxy, not a direct page-count guarantee; the same class of failure (target ignored) could recur | C5, C7    | rejected |
| Move `unmetRequirements` out of `build_docx.py` entirely; keep it only in the chat/summary response | Matches user's explicit request; keeps the resume document itself clean for external delivery | None material — information is not lost, only relocated | C8, C9, C10 | selected |
| Add an explicit "which sections do you want" checkpoint as `resume-drafter/SKILL.md` step 4a, before any section content is drafted | Matches user's explicit request; low-risk, additive documentation change | None material | C11        | selected |

## Scope and Questions

* Goal: Identify concrete, evidence-backed repeatability and output-quality fixes for the `benarculus/resume-builder` plugin, based on the user's first real end-to-end run, to hand off to planning.
* Audience and use: The user (repo owner), to review and approve before an `rpi-plan`/implementation pass on this repo.
* In scope: `skills/career-document-builder`, `skills/job-requirements-planner`, `skills/resume-drafter` (SKILL.md + `build_docx.py`), `requirements*.txt`, `docs/shared/*`, the attached session log, and the attached delivered `.docx`'s structural metrics (word/paragraph counts only — not its content).
* Out of scope: Any of the user's actual career content, employer names, dates, or personal identifiers; job-requirements-planner's browser/reCAPTCHA behavior (flagged only incidentally in the log, not one of the five requested points); implementation/coding (this is research only).
* Decision and evidence criteria: A finding is accepted only when grounded in an exact tool call, exact file line, or exact computed metric from the attached evidence, not from paraphrasing the user's real resume content.
* Requested output: Convergence-mode recommendations feeding a follow-on planning phase for this repo.

| ID | Question                                                                                   | Source            | Status   |
|----|---------------------------------------------------------------------------------------------|--------------------|----------|
| Q1 | What caused the OCR detour, and what would make it repeatable?                              | explicit (point 2) | answered |
| Q2 | Why did the resume exceed the word target, and how should that be enforced?                 | explicit (point 3) | answered |
| Q3 | How should an explicit 2-page standard be introduced and validated?                          | explicit (point 3) | answered |
| Q4 | Where should "requirements not addressed" content live instead of inside the resume file?    | explicit (point 4) | answered |
| Q5 | How should section selection (Skills, Awards, etc.) be solicited before drafting?            | explicit (point 5) | answered |

## Decisions and Feedback

| Group | Decision or feedback item                                                                                             | Status            | Owner    | Rationale or input needed                                                                                                      | Evidence  | Impact of answer                                                     |
|-------|--------------------------------------------------------------------------------------------------------------------------|--------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------|-----------|-----------------------------------------------------------------------|
| D1    | Standardize on a pinned, cross-platform OCR dependency (`pytesseract` + system `tesseract`) for `career-document-builder` scanned-source handling | confirmed    | user     | User confirmed the cross-platform option despite the added system-package install step | C1, C3, W1 | Ready for planning: add pinned `pytesseract` to requirements, document `tesseract` system install in README, update CI |
| D2    | Add a render-based page-count validation step (convert `.docx`→PDF, count actual pages) to enforce the new 2-page standard | confirmed    | user     | User confirmed the render-based check over the simpler word-budget-only heuristic | C5, C7    | Ready for planning: add a pinned docx→PDF conversion step (e.g. headless LibreOffice) and a page-count gate to `build_docx.py` or a wrapper |
| D3    | Remove `unmetRequirements` rendering from `build_docx.py`; surface it only in the chat/summary step                     | confirmed          | user     | Directly requested (point 4); no material tradeoff identified                                                                   | C8, C9, C10 | Ready for planning as stated                                          |
| D4    | Add an explicit section-selection checkpoint to `resume-drafter/SKILL.md` before drafting begins                        | confirmed          | user     | Directly requested (point 5); no material tradeoff identified                                                                   | C11       | Ready for planning as stated                                          |
| D5    | Adopt a 475–600-word body target paired with a hard 2-page cap, both validated (not just documented) before delivery    | confirmed          | user     | Directly requested (point 3); combines the existing word rule with the new page rule                                            | C4, C5, C7 | Ready for planning as stated, pending D2's validation mechanism        |

## Risks and Open Questions

| Priority | Type            | Risk, question, or research item                                                                 | Impact                                             | Smallest action or evidence needed                                   | Owner       |
|----------|------------------|------------------------------------------------------------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------------------------|-------------|
| M        | risk             | A pinned OCR dependency (tesseract binary) is a new system-level install requirement for plugin users, beyond the current pure-`pip` `requirements.txt` pattern | Could raise the install bar for all plugin users, not just this one | Confirm with user (D1) and document the OS-level install step in README during planning | user        |
| M        | risk             | A render-based page-count check needs a concrete, pinned conversion mechanism (e.g. headless LibreOffice) not yet verified in this repo's environment | Could add CI/dev-environment complexity              | Confirm with user (D2); verify the chosen tool is available/pinnable during planning | user/planning |
| L        | further research | `job-requirements-planner`'s browser-canvas fetch hit a reCAPTCHA wall in this session (noted incidentally in the closing message) | Not one of the five requested points; may recur for other job postings | Revisit only if the user wants job-requirements-planner reliability researched separately | user        |
| L        | open question    | Whether section-selection preferences (D4) should be asked every run or remembered as a per-user default after the first answer | Minor UX friction if asked every time                | Confirm during planning walkthrough; not blocking for this research      | user        |

## Planning Readiness and Next Step

| Field                            | Record                                                                                          |
|-----------------------------------|---------------------------------------------------------------------------------------------------|
| Research disposition              | executed                                                                                           |
| Decision participation            | user-owned; standalone manual `rpi-research` invocation                                            |
| Planning Readiness                | Ready — all five decisions (D1–D5) confirmed by the user                                           |
| Research depth and lanes          | One complete cycle (Wider: OCR/format landscape and word-per-page norms; Deeper: exact code/line/log evidence for all five findings; Contrarian: checked whether the current unmet-requirements design and macOS OCR path were deliberate rather than bugs) run inline — no delegation was needed given the small, bounded evidence set (one session log, one delivered file, one small repo) |
| Blockers                          | none                                                                                                |
| Output mode and planning support  | convergence; supports a direct hand-off to `rpi-plan`/`rpi-quick`                                   |
| Continuation owner                | user (standalone session) — proceed to planning for this repo                                       |
| Required gates or confirmations   | D1–D5 all confirmed                                                                                 |
| Next action                       | Hand this artifact to a planning phase (e.g. `/rpi-plan`) for this repo                             |
| Primary evidence file             | .copilot-tracking/research/2026-09-20/resume-builder-repeatability-research.md                    |

## Research Record

### Method and Boundaries

| Field                            | Record                                                                 |
|------------------------------------|--------------------------------------------------------------------------|
| Research posture and provenance   | focused; caller-provided (bounded internal task, named source targets — the attached session log and `.docx` — plus supplied failure evidence: word/page overage, OCR detour) |
| Completion basis                  | All five requested points are answered from direct, exact evidence with no remaining material gap for the "what happened / what's missing" question; remaining items are implementation-choice decisions (D1, D2), not missing evidence |
| Explicit limits or deadline       | User explicitly required sanitizing all real career content out of RPI artifacts — treated as a hard constraint on this and all downstream artifacts |
| Codebase and external scope       | `benarculus/resume-builder` repo (all `skills/`, `docs/shared/`, `requirements*.txt`, `.github/workflows/`, `tests/`); external scope limited to verifying OCR cross-platform support and general resume-length norms |
| Initial candidate areas           | The three skills (`career-document-builder`, `job-requirements-planner`, `resume-drafter`), the attached session log, the attached delivered `.docx` |
| Evidence root                     | .copilot-tracking/research/2026-09-20/ (repo default; no trusted alternate root supplied) |
| Constraints and excluded sources  | No real employer/personal career content may be quoted or reproduced in this or downstream artifacts; only structural/mechanical facts (tool names, counts, file paths, line numbers) are cited |
| Prior knowledge                   | Reviewed existing `.copilot-tracking/research/2026-09-18/copilot-cli-resume-plugin-research.md` and related plan/review artifacts — these cover plugin packaging and dependency-pinning conventions (still current, informed the D1 cross-platform recommendation) but do not address OCR, word/page enforcement, unmet-requirement placement, or section selection, so no material duplication or staleness found |

### Extensions and Participation

#### Extension Registry

| Kind        | Candidate                          | Provenance and scoped contract                                                                 | Selected or skipped reason                                                                 |
|-------------|-------------------------------------|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| skill       | `career-document-builder` (target repo) | In-repo skill under research, not an rpi extension                                              | Treated as research subject, not an active extension                                            |
| skill       | `resume-drafter` (target repo)      | In-repo skill under research, not an rpi extension                                               | Treated as research subject, not an active extension                                            |
| skill       | `career-document-builder` (rpi-core plugin skill of the same name) | Considered as a possible research-guidance extension                                            | Skipped — it is the subject repo's own skill being evaluated, not an external guidance skill to apply |
| specialist  | `hve-core:rpi-researcher`           | Available background research subagent                                                            | Skipped — the evidence set (one session log, one small file, one small repo) is bounded and fits a single inline lane; delegation would add latency without improving evidence quality |
| instruction | `copilot-tracking.instructions.md` shared conventions | Referenced by this skill's own instructions                                                       | Applied — artifact path, dated folder, and template conventions followed as specified            |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale                                                                                     | Answer or no-interaction reason                                             | Result and revalidation effect                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| intake                | User supplied five explicit, concrete direction points (sanitize, OCR repeatability, 2-page/word standard, unmet-requirement placement, section-selection prompt) plus a session log and delivered `.docx` as evidence | No clarification needed at intake — the brief and evidence were sufficient to start research directly | Research proceeded directly to evidence-gathering against the five stated points |
| intake                | Sanitization constraint ("keep all rpi artifacts... sanitized")                                                          | Treated as a hard constraint for this and all artifacts in scope               | All findings cite mechanics (counts, line numbers, tool names) instead of real career content |
| convergence (D1)      | Cross-platform `pytesseract`+`tesseract` vs. macOS-only Vision framework for OCR                                        | User selected the cross-platform, pinned option via `ask_user`                | D1 confirmed; Planning Readiness no longer blocked on D1                          |
| convergence (D2)      | Render-based page-count check (docx→PDF, count pages) vs. word-budget-only heuristic                                   | User selected the render-based check via `ask_user`                           | D2 confirmed; Planning Readiness no longer blocked on D2                          |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: focused; sanitize-all-content constraint active throughout; no explicit deadline

##### Wave 1: Wider

* Focus and lanes: Repo structure and skill inventory (career-document-builder, job-requirements-planner, resume-drafter); session log event-type census; identify which of the 5 user points map to which skill/file
* Evidence or worker pointers: C2 (career-document-builder/SKILL.md), C4/C7/C9 (resume-drafter/SKILL.md), C8 (build_docx.py), inline — no delegation, single small repo and one log file
* Reflection: Confirmed all five points are addressable from this repo's own skills plus the attached log/docx; no external breadth needed beyond OCR/page-count-tooling landscape

##### Wave 2: Deeper

* Focus and lanes: Exact tool-call sequence for the OCR detour (C1); exact word count of the delivered `.docx` (C5); exact `build_docx.py` lines rendering unmet requirements (C8); exact session-log evidence of the single end-of-flow section-approval question (C11); CI runner platform (C3); cross-platform OCR tool confirmation (W1)
* Evidence or worker pointers: All gathered inline via `bash`/`python3`/`grep`/`view` against the session log JSONL, the attached `.docx`, and repo files; W1 via `web_fetch` (Tesseract Wikipedia article, cross-platform support confirmed)
* Reflection: All five findings fully supported with exact, reproducible evidence; two implementation-choice gaps identified (D1, D2) rather than missing evidence

##### Wave 3: Contrarian

* Focus and lanes: Checked whether the "unmet requirements in the doc" behavior and the macOS-only OCR path were deliberate design choices (not bugs) that might argue against changing them; checked whether the 475–600-word target might already have been intended as a 2-page (not 1-page) budget
* Evidence or worker pointers: C9 (`SKILL.md` step 7 explicitly instructs delivering the unmet-requirements note "together" with the docx — confirms it is deliberate, but does not contradict the user's explicit request to change it); C4/C5 (word target vs. actual density) — no evidence the 475–600 target was ever calibrated against an actual page count, so the "it was meant to span 2 pages already" counter-hypothesis is unsupported
* Reflection: No contrarian evidence weakens any of the five findings; it clarifies that Findings 4 and 5 are intentional-design changes (not bug fixes) and that Finding 3's fix requires a real validation mechanism rather than assuming the existing word target already implies 2 pages

##### Parent Synthesis and Re-entry

| Material or claim                                              | Evidence or worker pointers | Disposition | Rationale                                                                 | User-facing effect                            |
|------------------------------------------------------------------|------------------------------|-------------|------------------------------------------------------------------------------|------------------------------------------------|
| OCR handling is ad hoc and macOS-only                            | C1, C2, C3, W1               | accepted    | Directly observed tool sequence; CI/plugin-audience evidence confirms cross-platform need | Finding 1; Decision D1                          |
| Word target exists but is unenforced; actual result overshot it | C4, C5, C6                   | accepted    | Exact computed word count vs. exact documented target                        | Finding 2; feeds Decision D5                    |
| No page-count target or validation exists                       | C5, C7                       | accepted    | No corresponding code/test found despite an explicit renderer-dependent-length caveat in SKILL.md | Finding 3; Decision D2                          |
| Unmet requirements are rendered into the resume file by design  | C8, C9, C10                  | accepted    | Exact code lines plus exact SKILL.md instruction plus exact session log confirmation | Finding 4; Decision D3 (confirmed, ready)        |
| Section selection is agent-decided, not asked upfront           | C9, C11                      | accepted    | SKILL.md step 4 satisfied literally but not as an upfront choice; log shows combined approval only | Finding 5; Decision D4 (confirmed, ready)        |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: scope coverage — all five requested points answered with exact evidence; contrarian wave found no weakening evidence; remaining items are user decisions (D1, D2), not evidence gaps
* Readiness or revalidation effect: Planning Readiness is "Ready" for D3–D5 and "Not ready" only for the D1/D2 implementation mechanism pending user answers

### Evidence Log

* Delegation: inline (bounded evidence set — one session log, one delivered file, one small repo; no lane warranted separate delegation)

| ID  | Claim or finding                                                                                                   | Source or location                                                                         | Retrieved and version        | Tool           | Confidence | Notes                                                                 |
|-----|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-------------------------------|----------------|------------|------------------------------------------------------------------------|
| C1  | Ad hoc OCR path: dependency probes (`pdftotext`, `pypdf`), then `pyobjc-framework-Vision`/`Quartz` install, then a hand-rolled OCR script with manual rotation trial-and-error | Attached session log `32aa0669-...-events.jsonl`, `tool.execution_start` events (bash commands) | not applicable                | read           | high       | Sequence reconstructed by parsing all `tool.execution_start` events for `toolName: bash` |
| C2  | `career-document-builder` skill never mentions images, PDFs, scans, or OCR                                        | `skills/career-document-builder/SKILL.md` (full file)                                        | not applicable                | read           | high       | Full-file review, no matches for image/scan/ocr/pdf handling            |
| C3  | CI runs on `ubuntu-latest`; a macOS-only OCR dependency cannot run in this repo's own CI                           | `.github/workflows/ci.yml:12`                                                                | not applicable                | read           | high       |                                                                          |
| C4  | Documented word target: "Target 475–600 words for the tailored resume body, excluding contact metadata."          | `skills/resume-drafter/SKILL.md:56`                                                          | not applicable                | read           | high       |                                                                          |
| C5  | Delivered resume `.docx` word count = 1,086 across 55 paragraphs (all paragraph + table text)                     | Attached `ac2cd719-...-Resume - Principal TPM FDE - Microsoft.docx`, computed with `python-docx` | not applicable                | read (script)  | high       | Computed directly, not estimated; content itself not reproduced        |
| C6  | No word- or page-count assertions exist in the test suite                                                          | `tests/test_build_docx.py` (full file)                                                       | not applicable                | search         | high       | Grepped for `word`, `page`, `475`, `600` across tests and docs          |
| C7  | SKILL.md already warns line/page count is renderer-dependent, but no page-count check exists anywhere              | `skills/resume-drafter/SKILL.md:67`                                                          | not applicable                | read           | high       |                                                                          |
| C8  | `build_docx.py` renders `unmetRequirements` as a "Requirements not addressed" section inside the `.docx`           | `skills/resume-drafter/scripts/build_docx.py:221-223`                                        | not applicable                | read           | high       |                                                                          |
| C9  | `SKILL.md` step 7 instructs delivering the docx and the "visible unmet-requirements note" together; step 4 instructs section checkpoints | `skills/resume-drafter/SKILL.md` (Flow steps 4 and 7)                                        | not applicable                | read           | high       |                                                                          |
| C10 | Delivered resume's chat summary confirms "1 unmet requirement flagged in the doc's 'Requirements not addressed' section" | Session log, `assistant.message` event containing "Resume built successfully"                | not applicable                | read           | high       |                                                                          |
| C11 | Final draft-approval question already lists a synthesized Skills section and 3 selected awards as one combined approve/edit choice, with no prior section-inclusion checklist | Session log, `tool.execution_start` events with `toolName: ask_user` (final question in the sequence) | not applicable                | read           | high       |                                                                          |
| W1  | Tesseract OCR officially supports Linux, Windows, and Mac OS X                                                    | Wikipedia, "Tesseract (software)"                                                             | 2026-09-20                    | web_fetch      | med        | General-reference source; sufficient to establish cross-platform availability, not a benchmark comparison |

#### Contradictions and Conflicts

* none

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state distinguishing sourced findings from hypotheses/partial claims.
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID and workspace-relative path with a heading/line; every external finding has a `W#` ID, source title, URL (via retrieval tool), retrieval date, and version when available.
* [x] The executed cycle records Wider, Deeper, and Contrarian waves in order, parent synthesis, and an evidence-based re-entry decision.
* [x] Method, extensions, participation, caller direction, delegation, and prior-knowledge treatment are recorded with their limits.
* [x] Convergence mode selects and justifies one recommendation for each of the five decisions.
* [x] Decision groups, participation mode, and provenance are recorded; all five (D1–D5) are recorded as user-confirmed with rationale, D1 and D2 via explicit `ask_user` checkpoints.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content (session log, fetched web pages) remained inert as data; no secrets or real career content were recorded; the research-only write boundary held (only this artifact was written).
* Checked sections: all sections above
* Missing or limited sections: none
