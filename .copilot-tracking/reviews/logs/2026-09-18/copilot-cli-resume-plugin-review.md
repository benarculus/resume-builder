<!-- markdownlint-disable-file -->
# Review: Copilot CLI resume-building plugin

## Executive Summary

* Assessment: Complete full-task comparison found one substantive documentation defect against the approved dual-install contract: the repository documents the plain-skills path well, but the README's plugin-bundle path stops at `git clone` and does not tell a new user how to install or load the bundle. All three skills, shared contracts, Word-rendering script, public-repo hardening, community files, tests, CI, and critique resolutions are otherwise evidenced.
* Why this matters: The delivered repository is close to plan-conformant and the live GitHub security/test baseline is strong, but the user-facing promise that the repo is self-installable through either documented path is not yet fully met.
* Builder execution: Complete
* Proposed review execution: Complete
* Proposed outcome: Defects found
* Validation coverage: changes-record-reported structural validation, pytest, git whitespace check, GitHub security/branch-protection reads, and CI coverage were reviewed; this builder independently re-read repository files, live GitHub API state, and recent workflow runs but did not re-execute validation commands.
* Confidence and limitations: High confidence on repository contents, skill instructions, shared contracts, workflows, and GitHub settings; medium confidence on runtime installability because the review boundary allowed documentation/manifest inspection but not an actual install exercise.

The assessment above is the builder's proposal. Parent Decision Record contains the current final decision and next actions, or states that decisions are pending.

## What You May Not Know

* Live GitHub-side hardening is present, not just claimed in the changes record: `gh api repos/benarculus/resume-builder` reported `visibility: public`, `license: MIT`, `secret_scanning: enabled`, `secret_scanning_push_protection: enabled`, and `dependabot_security_updates: enabled`; `gh api repos/benarculus/resume-builder/vulnerability-alerts -i` returned `204 No Content`; and `gh api repos/benarculus/resume-builder/branches/main/protection` showed one approving review, code-owner review, and conversation resolution on `main`.
* The substantive nonconformance found is concentrated in onboarding/documentation for the bundle-install path, not in the anti-fabrication flow, parser/renderer code, GitHub hardening, or CI/test assets.
* Low-impact scaffold divergence remains: the approved `P01-T01` tree included placeholder `templates/` directories under each skill, but `.github/skills/career-document-builder/` and `.github/skills/job-requirements-planner/` contain only `SKILL.md`, and `.github/skills/resume-drafter/` contains `SKILL.md` plus `scripts/`. This is recorded as residual divergence rather than a routed `RV-xxx` finding because no delivered behavior currently depends on those directories.

## Findings and Proposed Routes

<!-- rpi:review id=RV-001 -->
### RV-001 [Medium]: The README does not give a usable plugin-bundle installation procedure

The repository still falls short of its approved dual-install onboarding contract. A new user can follow the plain Agent Skills path from the README, but the bundle path is not actually actionable from the same document.

* Related scope: `FR-005`, `NFR-004`, `P01-T02`, `P05-T01`
* Expected behavior: `README.md` documents both supported install paths side by side, including how to install or load the whole repository as a plugin bundle through the host convention represented by `.github/plugin/marketplace.json`, so a new user can install either path from the repository alone.
* Observed behavior and evidence: `README.md` under `## Install` → `### Plain Agent Skills (portable path)` provides concrete copy commands for `.github/skills/<skill-name>/`. Under `### Plugin bundle`, the file states that the repo includes `.github/plugin/marketplace.json` and shows only `git clone https://github.com/benarculus/resume-builder.git`, followed by a warning that the format is host-specific. Unlike the plain-skills section, it gives no bundle-specific installation step, target location, or host loading action, even though `.github/plugin/marketplace.json` exists and declares the bundle metadata.
* Impact: The portable install path is documented, but the claimed second install mode is not credibly self-service. That leaves `FR-005` and `NFR-004` only partially satisfied and makes the README weaker than the approved onboarding contract.
* Resolution condition: The repository documents one complete, supported plugin-bundle installation procedure that a new user can follow from `README.md`, or the repository narrows its claims so only the evidenced plain-skills path is presented as supported/self-service.
* Proposed destination: `rpi-implement`
* Smallest useful next action: Update `README.md`'s `### Plugin bundle` section with the exact supported install/load steps for the target host convention, or explicitly downgrade the bundle path from a documented install mode to an advanced/manual convention.

No other substantive findings were identified within the assessed boundary. The remaining gaps are limited to the README bundle-install contract above and a low-impact scaffold-parity divergence recorded outside the routed findings.

## Parent Decision Record

<!-- The selected review worker leaves this section unchanged. The primary review parent owns it. -->

### Current Disposition

* Based on events: RD-001, RD-002, RD-003, RD-004, RD-005
* Review execution: Complete
* Final outcome: Defects found — one Medium defect (`RV-001`) accepted for routing to `rpi-implement`; all other assessed requirements and tasks are conformant
* Finding decisions and next actions: `RV-001` accepted; route `rpi-implement` to add a usable plugin-bundle installation procedure to `README.md` (or explicitly narrow the README to only claim the evidenced plain-skills path)
* Decisions still needed: none

This summary is derived from Decision History, not a second decision record. The latest event for each subject governs; refresh this summary after appending decisions and on recovery.

### Decision History

Append events in order. Never rewrite or delete an earlier row. The latest event for a subject is current.

| Event  | Subject       | Decision source | Status or value                                  | Proposed destination | Final destination | Owner   | More information needed | Smallest next action                                                                       | Rationale                                                                                                                                                                         |
| ------ | ------------- | ---------------- | ------------------------------------------------- | --------------------- | ------------------- | ------- | ------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RD-001 | participation | system            | user-owned (standalone `rpi-review` invocation)    | none                   | none                 | parent  | none                       | proceed to builder dispatch                                                                    | Standalone user-invoked review; no automatic RPI Agent or `rpi-quick` context, and no parent orchestration state overrides participation.                                        |
| RD-002 | execution     | parent            | Complete                                           | none                   | none                 | parent  | none                       | none                                                                                            | Builder performed a full-boundary comparison across all `Pxx-Txx` tasks, `FR`/`NFR` items, critique dispositions, and live GitHub state; parent independently re-verified `RV-001` against `README.md` and confirms Complete. |
| RD-003 | outcome       | parent            | Defects found                                      | none                   | none                 | parent  | none                       | none                                                                                            | One accepted Medium defect (`RV-001`) exists against an approved requirement (`FR-005`/`NFR-004`); all other `FR`/`NFR` and task rows are Met, so Defects found applies rather than Conformant, Residual work, or Not accepted. |
| RD-004 | walkthrough   | user              | completed                                          | none                   | none                 | parent  | none                       | none                                                                                            | User-owned walkthrough presented `RV-001` with plain-language context, evidence links, and the suggested/gather/skip/finish choice set via `ask_user`; user selected the suggested action for the sole finding, so the walkthrough is complete. |
| RD-005 | `RV-001`      | user              | accepted                                           | `rpi-implement`        | `rpi-implement`      | user    | none                       | Update `README.md`'s `### Plugin bundle` section with a usable install/load procedure, or narrow the README's claim to the evidenced plain-skills path only | User selected "Use suggested action" for the README bundle-install gap; the fix fits the current accepted direction (no scope, architecture, or requirement change), so it routes to a later `rpi-implement` invocation rather than back to `rpi-plan`. |

## Validation Evidence

| Command | Scope | Status | Summary |
|---|---|---|---|
| `changes-record-reported: python3 scripts/validate_repo.py` | `P01`–`P05`, `P07-T02` | Passed | Reported as passed in `.copilot-tracking/changes/2026-09-18/copilot-cli-resume-plugin-changes.md` `## Validation Record`; this review also inspected `scripts/validate_repo.py` and confirmed it checks all `SKILL.md` frontmatter, `.github/plugin/marketplace.json`, and the shared job-requirements parser fixture. |
| `changes-record-reported: python3 -m pytest -q` | `P04`, `P07` | Passed | Reported as `3 passed`; this review inspected `tests/test_build_docx.py` and `tests/test_structure.py`, which cover `.docx` creation/opening, job-requirements parsing, and the structural validation script. |
| `changes-record-reported: git diff --check` | full diff | Passed | Reported as passed in the changes record; not independently re-run by this builder. |
| `changes-record-reported: GitHub security settings API reads` | `P06-T01` | Passed | Changes record reported public visibility, secret scanning, push protection, and Dependabot security updates enabled; this review independently re-read `gh api repos/benarculus/resume-builder` and `gh api repos/benarculus/resume-builder/vulnerability-alerts -i`, which remained consistent with that report. |
| `changes-record-reported: branch protection API read` | `P06-T01` | Passed | Changes record reported pull-request review, code-owner review, conversation resolution, and force-push/deletion blocks on `main`; this review independently re-read `gh api repos/benarculus/resume-builder/branches/main/protection`, which remained consistent with that report. |
| `changes-record-reported: CI configuration inspection` | `P07-T02` | Passed | Changes record reported push/PR CI coverage; this review inspected `.github/workflows/ci.yml`, `.github/workflows/codeql-analysis.yml`, and `gh run list -R benarculus/resume-builder --limit 10`, which showed recent successful `Validate resume-builder` and `CodeQL` runs. |

## Risks, Blockers, and Residual Work

* Blockers: none within the review evidence boundary.
* Remaining active work: none in the approved active-plan scope; any remaining action depends on parent disposition of `RV-001`.
* Residual work: the plan's scenario-based behavior eval suite remains correctly outside active completion claims; exact `P01-T01` scaffold parity would also require adding the planned placeholder `templates/` directories or recording that divergence explicitly.

## Review Record

### Scope and Evidence

* Task ID: `copilot-cli-resume-plugin`
* Review date: `2026-09-18`
* Review scope: full task (`P01`–`P07`)
* Assessed boundary: all seven plan phases and their tasks (`P01-T01`–`P07-T02`); every `FR-001`–`FR-008` and `NFR-001`–`NFR-006`; the plan's `## Follow-Up Items`; the plan critique's `PC-001`–`PC-003` dispositions; and the changes record's Completed Work, Implementation-Time Plan Updates, Validation Record, Pre-Review Reconciliation, Follow-Up Items, and Return-to-Caller State
* Review depth and provenance: standard; default (no explicit user request for deep)
* Review worker: general-purpose (unnamed fallback; this invocation was already reserved as the selected builder)
* Builder candidate identity: task `copilot-cli-resume-plugin`, full-plan scope, plan sha256 `6ed52f71b8afabaa86e97a37ae482204dea0964d6b034025b399a52b4a3624a2`, changes-record sha256 `1321ae4030284e8721ac1f1eb53d9af39269a3107f8079f0303dc4439a3e52f7`
* Builder execution: Complete
* Plan: `.copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md`
* Plan critique: `.copilot-tracking/reviews/plans/2026-09-18/copilot-cli-resume-plugin-plan-critique.md`
* Changes: `.copilot-tracking/changes/2026-09-18/copilot-cli-resume-plugin-changes.md`
* Other evidence considered: live repository files under `resume-builder/`; `gh api repos/benarculus/resume-builder`; `gh api repos/benarculus/resume-builder/branches/main/protection`; `gh api repos/benarculus/resume-builder/vulnerability-alerts -i`; `gh api repos/benarculus/resume-builder/community/profile`; `gh run list -R benarculus/resume-builder --limit 10`; research was not needed to close an evidence gap in this comparison

### Opening Review State

* Interpreted review goal: confirm that the implemented `resume-builder` repository satisfies the approved plan's task requirements, FR/NFR boundary, critique resolutions, and declared follow-up separation, and that the changes record's claims are grounded in the actual repository and live GitHub state.
* Review scope: full task (`P01`–`P07`)
* Evidence readiness: plan, critique, changes record, live repository files, and GitHub live-state reads were all available and sufficient for a credible full-task comparison.
* Acceptance basis: each task's `Requirements:` block, `FR-001`–`FR-008`, `NFR-001`–`NFR-006`, the resolved `PC-001`–`PC-003` critique findings, the implementation-time MIT license decision, and the plan's explicit follow-up boundary.
* First comparison boundary: compare every in-scope marker against repository files and GitHub read APIs, using changes-record validation results only as reported evidence rather than re-executing them.
* Active read-only boundaries: builder writes only this review record body (all sections except Parent Decision Record); no plan, critique, research, changes-record, source, or parent-state edits.
* Authority split: builder owns review evidence and proposed routes; parent owns final outcome, route dispositions, and continuation
* Initial blockers: none

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|---|---|---|---|
| `FR-001` | `.github/skills/career-document-builder/SKILL.md`; `docs/shared/career-document-schema.md`; `docs/shared/anti-fabrication-contract.md` | Met | Career-document skill accepts the required evidence types, asks clarifying questions, preserves source pointers, and targets the shared schema. |
| `FR-002` | `.github/skills/job-requirements-planner/SKILL.md`; `docs/shared/job-requirements-schema.md`; `docs/shared/anti-fabrication-contract.md` | Met | Job planner is constrained to one user-supplied posting plus optional supplementary links, browser/computer-use reads, and structured source-linked output. |
| `FR-003` | `.github/skills/resume-drafter/SKILL.md`; `docs/shared/anti-fabrication-contract.md`; `docs/shared/job-requirements-schema.md` | Met | Resume drafter requires mapping/question/unmet handling per requirement and an interactive clarification flow. |
| `FR-004` | `.github/skills/resume-drafter/scripts/build_docx.py`; `tests/test_build_docx.py`; changes-record-reported `python3 -m pytest -q` | Met | `.docx` rendering script exists, is invoked from the skill, and is covered by tests that open the generated file. |
| `FR-005` | `.github/skills/*/SKILL.md`; `.github/plugin/marketplace.json`; `README.md` `## Install` | Gap | Plain-skills install path is documented and the manifest exists, but the bundle-install path is not documented as a usable install flow (`RV-001`). |
| `FR-006` | `README.md` `## How the skills fit together`; all three `SKILL.md` files; `docs/shared/career-document-schema.md`; `docs/shared/job-requirements-schema.md`; `.github/skills/resume-drafter/scripts/parse_job_requirements.py` | Met | The repository implements the intended career-document → job-requirements → resume pipeline with shared producer/consumer contracts. |
| `FR-007` | `LICENSE`; `CODE_OF_CONDUCT.md`; `CONTRIBUTING.md`; `SECURITY.md`; `.github/ISSUE_TEMPLATE/bug_report.yml`; `.github/ISSUE_TEMPLATE/feature_request.yml`; `.github/PULL_REQUEST_TEMPLATE.md`; `gh api repos/benarculus/resume-builder/community/profile` | Met | Required community-health files exist and GitHub community profile reports 100% health. |
| `FR-008` | `tests/test_build_docx.py`; `tests/test_structure.py`; `.github/workflows/ci.yml`; changes-record-reported pytest/validation; `gh run list -R benarculus/resume-builder --limit 10` | Met | Automated tests and CI cover `.docx` generation plus structural validation on push and pull request. |
| `NFR-001` | all three `SKILL.md` files; `docs/shared/anti-fabrication-contract.md` | Met | Anti-fabrication behavior is centralized and each skill instructs clarifying questions instead of invention. |
| `NFR-002` | `.github/skills/job-requirements-planner/SKILL.md`; frontmatter `allowed-tools: [computer-use]` | Met | Job-posting acquisition is explicitly single-link, browser-mediated, and non-crawling. |
| `NFR-003` | all three `SKILL.md` frontmatters; `scripts/validate_repo.py`; changes-record-reported structural validation | Met | `name`, `description`, `license`, and `allowed-tools` handling are structurally validated and names match directory names. |
| `NFR-004` | `README.md` `## Install`, `## Quickstart`, skill links | Gap | Quickstart and anti-fabrication guidance are present, but the README does not fully document the bundle-install path for self-service use (`RV-001`). |
| `NFR-005` | `.github/workflows/codeql-analysis.yml`; `.github/dependabot.yml`; `.github/CODEOWNERS`; `gh api repos/benarculus/resume-builder`; `gh api repos/benarculus/resume-builder/vulnerability-alerts -i`; `gh api repos/benarculus/resume-builder/branches/main/protection` | Met | Required public-repo hardening is committed and live GitHub state shows the expected protections enabled. |
| `NFR-006` | `.github/workflows/ci.yml`; `tests/test_build_docx.py`; `tests/test_structure.py`; `scripts/validate_repo.py`; `gh run list -R benarculus/resume-builder --limit 10` | Met | Ongoing automated validation is present in CI, not only as a one-time manual check. |
| `P01-T01` | `.github/skills/career-document-builder/`; `.github/skills/job-requirements-planner/`; `.github/skills/resume-drafter/`; `docs/shared/`; `LICENSE` | Gap | Flat skill layout and shared-doc placement match the critique-corrected design, but the planned placeholder `templates/` directories are absent; recorded as low-impact scaffold divergence. |
| `P01-T02` | `.github/plugin/marketplace.json`; `README.md` `## Install`, `## How the skills fit together` | Gap | Manifest fields and pipeline framing are present, but the bundle-install instructions are not actionable (`RV-001`). |
| `P01-T03` | `docs/shared/career-document-schema.md`; `docs/shared/job-requirements-schema.md`; `docs/shared/anti-fabrication-contract.md`; links from all three `SKILL.md` files | Met | Shared career-document, job-requirements, and anti-fabrication contracts exist once and are referenced by consuming skills. |
| `P02-T01` | `.github/skills/career-document-builder/SKILL.md` | Met | Frontmatter, accepted input mix, clarifying-question behavior, LinkedIn-export constraint, and structural validation expectations are all present. |
| `P03-T01` | `.github/skills/job-requirements-planner/SKILL.md`; `docs/shared/job-requirements-schema.md` | Met | Planner skill enforces one primary posting, optional supplementary links, visible-text capture, no bypass, and the shared deterministic output contract. |
| `P04-T01` | `.github/skills/resume-drafter/SKILL.md`; `docs/shared/anti-fabrication-contract.md`; `docs/shared/job-requirements-schema.md` | Met | Resume drafter explicitly maps each requirement to evidence/question/unmet status and runs through user checkpoints before finalizing. |
| `P04-T02` | `.github/skills/resume-drafter/SKILL.md`; `.github/skills/resume-drafter/scripts/build_docx.py`; `requirements.txt` | Met | The skill documents the script invocation and input shape, and the script emits `.docx` using `python-docx`. |
| `P05-T01` | `README.md` `## Install`, `## How the skills fit together`, `## Quickstart`; links to each `SKILL.md` | Gap | Quickstart order, skill cross-links, and anti-fabrication statement are present, but install documentation still does not fully cover both promised paths (`RV-001`). |
| `P05-T02` | `scripts/validate_repo.py`; `.github/skills/resume-drafter/scripts/parse_job_requirements.py`; `.github/skills/resume-drafter/scripts/fixtures/sample-resume.json`; `.github/skills/resume-drafter/scripts/fixtures/sample-job-requirements.json`; changes-record-reported structural validation/pytest | Met | Structural validation covers frontmatter, manifest JSON, and parser round-trip; representative fixtures are committed alongside the script area. |
| `P06-T01` | `.github/workflows/codeql-analysis.yml`; `.github/dependabot.yml`; `.github/CODEOWNERS`; live GitHub API metadata, vulnerability-alerts status, and branch protection | Met | CodeQL, Dependabot config, CODEOWNERS, secret scanning, push protection, and baseline branch protection are all evidenced. |
| `P06-T02` | `LICENSE`; `CODE_OF_CONDUCT.md`; `CONTRIBUTING.md`; `SECURITY.md`; `.github/ISSUE_TEMPLATE/bug_report.yml`; `.github/ISSUE_TEMPLATE/feature_request.yml`; `.github/PULL_REQUEST_TEMPLATE.md`; `gh api repos/benarculus/resume-builder/community/profile` | Met | Required community/security files exist; `SECURITY.md` gives a private reporting path; `CONTRIBUTING.md` references the flattened skill layout. |
| `P07-T01` | `tests/test_build_docx.py`; `.github/workflows/ci.yml`; changes-record-reported `3 passed`; `gh run list -R benarculus/resume-builder --limit 10` | Met | Pytest exercises `.docx` creation/opening and parser acceptance, and CI runs pytest on push and pull request. |
| `P07-T02` | `scripts/validate_repo.py`; `tests/test_structure.py`; `.github/workflows/ci.yml`; changes-record-reported structural validation; `gh run list -R benarculus/resume-builder --limit 10` | Met | Structural validation is automated in CI and includes frontmatter, manifest, and job-requirements round-trip checks. |
| Implementation-time plan update: MIT license selection | `LICENSE`; `.github/plugin/marketplace.json`; all three `SKILL.md` frontmatters; changes record `## Implementation-Time Plan Updates` | Met | The only implementation-time judgment was applied consistently across license-bearing artifacts. |

Cover every material requirement and in-scope completion claim, grouping rows only when their evidence and assessment are shared. Include implementation-time plan updates and confirmed decisions. Keep detailed gaps in their findings instead of repeating them here.

### Critique and Follow-Up Assessment

* Latest critique dispositions: `PC-001` is confirmed resolved in the live repo because the skills now sit directly under `.github/skills/<skill-name>/SKILL.md` and no nested `.github/skills/resume-builder/` family layer exists; `PC-002` is confirmed resolved because `docs/shared/job-requirements-schema.md` exists and is cited by both `.github/skills/job-requirements-planner/SKILL.md` and `.github/skills/resume-drafter/SKILL.md`; `PC-003` is confirmed resolved in the plan artifact because `## Planning Readiness and Next Step` and `## Critique Disposition` now agree on a completed critique history instead of a premature pass claim.
* Material revisions: the implementation-time MIT license decision is internally consistent across `LICENSE`, `.github/plugin/marketplace.json`, and the three skill frontmatters; no additional scope drift was hidden in the live repo.
* Dependent-work pause assessment: supported. The delivered repository reflects the post-critique flat skill layout and the shared job-requirements contract, so downstream work was performed on the corrected design rather than on the rejected nested/underspecified version.
* Justification assessment: supported for the MIT default decision and for keeping the scenario-based behavior eval suite outside immediate completion; unsupported only for treating the README bundle-install path as fully documented.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|---|---|---|---|
| Scenario-based behavior eval suite for clarifying-question and anti-fabrication behavior | The plan explicitly deferred deeper scenario/eval coverage beyond the baseline pytest/CI repository checks (`D8`, plan `## Follow-Up Items`). | Distinct follow-up item after review disposition. | Still open and correctly not claimed complete by the changes record or the live repository. |

Unresolved plan follow-up items remain distinct follow-up work. Do not treat them as defects or add them to active `Pxx` or `Pxx-Txx` implementation, completion, or acceptance scope.

### Builder Self-Check

* [x] Every supplied requirement, acceptance criterion, in-scope marker, material update, critique disposition, validation result, blocker, remaining item, and plan follow-up has an assessment or explicit gap.
* [x] Findings are substantive, evidence-grounded, severity-graded, and use stable `RV-xxx` IDs with expected and observed behavior, a resolution condition, and one proposed route each.
* [x] Execution status, proposed outcome, validation coverage, limitations, and proposed routes are complete and internally consistent.
* [x] The summary is scoped and advisory, findings keep their supporting context together, and acceptance coverage distinguishes demonstrated gaps from unassessed behavior.
* [x] Standard review completely assessed the material boundary while omitting restatement, cosmetic feedback, exhaustive strengths, low-impact suggestions, and continual narration; deep review remained inside the supplied boundary.
* [x] The selected review worker did not edit Parent Decision Record, ask the user, mutate source or parent state, dispatch another worker, execute validation, or invoke a destination.
* Checked boundary: full-task plan requirements (`FR-001`–`FR-008`, `NFR-001`–`NFR-006`), all `P01-T01`–`P07-T02` tasks, critique dispositions `PC-001`–`PC-003`, the MIT implementation-time plan update, changes-record validation/blocker/follow-up claims, the plan follow-up boundary, live repository files, and live GitHub metadata/protection/run state.
* Missing or limited evidence: runtime skill loading and plugin-bundle installation were not exercised; validation command outcomes are recorded from the changes record rather than re-executed by this builder.
