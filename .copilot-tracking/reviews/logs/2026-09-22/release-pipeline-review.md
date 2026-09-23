<!-- markdownlint-disable-file -->
# Review: Release pipeline for resume-builder

## Executive Summary

* Assessment: The full plan (P01–P03) was implemented as specified and every binding requirement checked against direct evidence holds. No implementation defects were found. One Low-severity informational observation was identified about how the new linear-history ruleset interacts with a pre-existing repository ruleset; it does not violate any binding requirement, but the user chose to act on it as accepted follow-up work.
* Why this matters: This confirms the release pipeline's static configuration (config/manifest/version file, workflow, ruleset) is correctly in place to give `resume-builder` automated, evidence-based SemVer tracking from Conventional Commits, as the user requested. The accepted follow-up (consolidating the two rulesets governing `main`) reduces future confusion without changing any delivered behavior.
* Review execution: Complete
* Assessed outcome: Residual work
* Validation coverage: All structural/static checks (JSON validity, YAML validity, live `gh api` verification of the ruleset and merge-strategy settings, `bootstrap-sha`/action-tag currency) passed. The behavioral requirements that only manifest on a real Release PR (`FR-002`, `FR-004`) are Not assessed — they require an actual push/merge to `main`, which is outside what this review can exercise, and the plan itself already recorded this as an open confidence caveat rather than a completed validation.
* Confidence and limitations: High confidence in the static/configuration correctness of everything created. The one genuine limitation is that this review cannot exercise the pipeline's first real run; that remains the practical acceptance check the plan always intended to leave for the first live Release PR.

The assessment above is the reviewer's proposal. Parent Decision Record contains the final decisions and next actions, or states that decisions are pending.

## What You May Not Know

* The new "Require linear history on main" ruleset (ID `23850509`) has `bypass_actors: []` and `current_user_can_bypass: never` — nobody, including repository admins, can override it without first editing the ruleset itself. This matches GitHub's default when a ruleset is created without explicit bypass actors and was not a binding requirement in the plan, but it is a real behavior change worth knowing before the first real merge to `main`.
* A pre-existing, unrelated ruleset ("Protect main", created 2026-09-19, before this plan existed) still lists `"merge"` in its own `allowed_merge_methods`. That listing is now misleading in practice: the new linear-history ruleset will block any actual merge commit regardless of what "Protect main" allows, because GitHub applies all active rulesets as a union and the most restrictive rule wins. Functionally this is correct and matches the confirmed decision (enforce linear history via ruleset), but a maintainer skimming only "Protect main" could be surprised that merge commits are rejected. See `RV-001`.

## Findings and Proposed Routes

<!-- rpi:review id=RV-001 -->
### RV-001 [Low]: Pre-existing "Protect main" ruleset still advertises `"merge"` as an allowed method

The repository already had an unrelated ruleset named "Protect main" (created 2026-09-19, before this task) whose `pull_request` rule lists `allowed_merge_methods: ["merge", "squash", "rebase"]`. This plan's new "Require linear history on main" ruleset (P03-T01) is additive and correct on its own, but the two rulesets together mean a maintainer who merges via `merge` will now be blocked by the new rule even though "Protect main" nominally still allows it.

* Related scope: P03-T01
* Expected behavior: not a binding requirement of this plan — P03-T01 only required a new, active, `required_linear_history` ruleset on `main` while squash/rebase remained enabled at the repository-settings level, which is satisfied.
* Observed behavior and evidence: `gh api repos/benarculus/resume-builder/rulesets/23698833` shows `"Protect main"`'s `pull_request` rule still includes `"merge"` in `allowed_merge_methods`; `gh api repos/benarculus/resume-builder/rulesets/23850509` shows the new ruleset's `required_linear_history` rule is `active` and targets `refs/heads/main`.
* Impact: Low — no functional break (the stricter rule wins), but it is a source of future confusion for anyone auditing repository rules and expecting "Protect main"'s allowed-methods list to reflect what will actually succeed.
* Resolution condition: either update "Protect main"'s `allowed_merge_methods` to drop `"merge"` for clarity, or accept the current state and note the union behavior somewhere a maintainer would see it (e.g. a short comment in repository documentation).
* Proposed destination: follow-up
* Smallest useful next action: a maintainer decides whether to edit the pre-existing "Protect main" ruleset's `allowed_merge_methods`; this is outside this plan's declared scope (which only added a new ruleset, not modified existing ones).

This is not a defect in what P03-T01 delivered; it is a discovered interaction between the new ruleset and an unrelated, pre-existing one that this plan did not create and was not asked to reconcile.

## Parent Decision Record

<!-- Decisions live here. Append events; never rewrite the evidence body above to fit a decision. -->

### Current Disposition

* Based on events: RD-001, RD-002, RD-003, RD-004, RD-005, RD-006
* Review execution: Complete
* Final outcome: Residual work
* Finding decisions and next actions: RV-001 — changed; final destination `rpi-implement`; owner implementer; smallest next action: fold the `required_linear_history` rule into the existing "Protect main" ruleset (ID `23698833`) and delete the standalone "Require linear history on main" ruleset (ID `23850509`)
* Decisions still needed: none

### Decision History

| Event  | Subject                    | Decision source | Status or value    | Proposed destination | Final destination | Owner | More information needed | Smallest next action                                             | Rationale                                                                                 |
|--------|-----------------------------|------------------|---------------------|-----------------------|--------------------|-------|---------------------------|--------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| RD-001 | participation               | user             | user-owned          | none                  | none               | user  | none                       | none                                                                | Standalone `/hve-core:rpi-review` invocation; no active automatic RPI Agent parent detected |
| RD-002 | execution                  | agent            | Complete            | none                  | none               | agent | none                       | none                                                                | Full comparison pass finished across all supplied evidence and plan markers                 |
| RD-003 | walkthrough                | system           | started             | none                  | none               | user  | none                       | Walk through RV-001 with the user before recording final outcome   | RV-001 is the only actionable finding and requires a user-owned decision per participation   |
| RD-004 | RV-001                     | user             | changed             | follow-up             | rpi-implement      | implementer | none                  | Fold `required_linear_history` into "Protect main" (ID `23698833`); delete the standalone ruleset (ID `23850509`) | User asked "can we merge the rulesets?", then chose to fold the new rule into "Protect main" and delete the separate one rather than leave the two rulesets side by side |
| RD-005 | walkthrough                | system           | finished            | none                  | none               | user  | none                       | none                                                                | RV-001 was the only actionable finding; its decision is recorded, no items remain undecided  |
| RD-006 | outcome                    | agent            | Residual work        | none                  | none               | agent | none                       | none                                                                | No implementation defects found; the only actionable item is accepted non-blocking follow-up work (ruleset consolidation), which fits Residual work rather than Defects found or Conformant |

## Validation Evidence

| Command | Scope | Status | Summary |
|---------|-------|--------|---------|
| `python3 -m json.tool release-please-config.json` | `release-please-config.json` | Passed | Valid JSON; shape matches P01-T01's binding contract exactly |
| `python3 -c "json.load(open('.release-please-manifest.json'))"` | `.release-please-manifest.json` | Passed | Valid JSON; value `{".": "0.1.0"}` matches P01-T03's binding contract |
| Manual content check | `version.txt` | Passed | Contains exactly `0.1.0` plus one trailing newline, matching P01-T02's binding contract |
| `python3 -c "yaml.safe_load(...)"` | `.github/workflows/release-please.yml` | Passed | Valid YAML; permissions (`contents`, `pull-requests`, `issues` only), trigger, action pin, and `with:` inputs all match P02-T01's binding contract as reviewed at the time. **Correction (post-CCR follow-up):** the trigger was later changed from `push: branches: [main]` to `workflow_run` chained after `ci.yml` ("Validate resume-builder") completes successfully, gated on `head_branch == 'main'` and `event == 'push'` — see the changes record's post-review correction entry and PR commit `094bf94` for the current, superseding validation. |
| `gh api repos/googleapis/release-please-action/git/refs/tags/v5.0.0` | P02-T01 SHA pin | Passed | Confirms `45996ed1f6d02564a971a2fa1b5860e934307cf7` is the exact commit the `v5.0.0` tag points to |
| `gh api repos/benarculus/resume-builder/rulesets/23850509` | P03-T01 | Passed | `enforcement: active`, `rules: [required_linear_history]`, `conditions.ref_name.include: [refs/heads/main]` |
| `gh api repos/benarculus/resume-builder` | P03-T01 prerequisite | Passed | `allow_squash_merge: true`, `allow_rebase_merge: true` |
| `actionlint` / `yamllint` | `.github/workflows/release-please.yml` | Unavailable | Neither tool is installed in this environment; no repository-level lint config exists to substitute (same limitation the changes record already recorded) |
| Live pipeline run (Release PR opened/merged) | FR-002, FR-004 | Unavailable | Requires an actual push/merge to `main` after this change is committed; not exercisable during review, consistent with the plan's own stated confidence caveat |

## Risks, Blockers, and Residual Work

* Blockers: none
* Remaining active work: none — full plan scope (P01–P03, all tasks) is checked and implemented
* Residual work: RV-001 — accepted follow-up: fold the `required_linear_history` rule from the new "Require linear history on main" ruleset (ID `23850509`) into the existing "Protect main" ruleset (ID `23698833`), then delete the standalone ruleset, so one ruleset governs `main`; routed to `rpi-implement`. The plan's own unimplemented follow-up item (optional Conventional-Commit PR-title lint) also remains open and correctly recorded as distinct follow-up, not a defect.

## Review Record

### Scope and Evidence

* Task ID: release-pipeline
* Review date: 2026-09-22
* Review scope: full task (P01, P02, P03 and all their tasks)
* Assessed boundary: all binding `Requirements:` in P01-T01, P01-T02, P01-T03, P02-T01, P03-T01; FR-001–FR-005 and NFR-001; the plan's Critique Disposition (`PC-001`); the plan's implementation-time updates recorded in the changes record; the plan's `## Follow-Up Items`; all validation results recorded in the changes record, re-verified live where practical
* Review depth and provenance: standard; default (no explicit user request for deep)
* Candidate identity: `release-pipeline`; plan, changes record, and critique as they stood after implementation completed on 2026-09-22
* Review execution: Complete
* Helper use: none — the review parent compared all evidence directly; task size did not warrant a subagent
* Plan: .copilot-tracking/plans/2026-09-22/release-pipeline-plan.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-22/release-pipeline-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-22/release-pipeline-changes.md
* Other evidence considered: .copilot-tracking/research/2026-09-22/release-pipeline-research.md; live `gh api` calls against `benarculus/resume-builder` and `googleapis/release-please-action` to re-verify ruleset state, repository merge-strategy settings, and the `v5.0.0` tag's commit SHA

### Opening Review State

* Interpreted review goal: confirm the implemented release-please pipeline (config/manifest/version file, workflow, ruleset) matches the plan's binding requirements and confirmed user decisions, with no unresolved implementation defects.
* Review scope: full task
* Evidence readiness: plan fully checked ([x] on all P01–P03 markers), changes record Complete with all validation recorded, critique's one finding (`PC-001`) resolved and recorded
* Acceptance basis: plan `Requirements:` blocks (citing FR-001–FR-005, NFR-001) for each task, plus the plan's Confirmed User Direction (D1–D3) and agent-owned decisions (D4 bootstrap-sha, D5 version.txt)
* First comparison boundary: compare each task's binding contract against the corresponding created file/workflow/ruleset; re-verify the two facts most likely to have drifted since planning (`bootstrap-sha` currency, `release-please-action` tag currency); check the plan's one implementation-time update (P03 phase-heading fix) for correctness
* Active read-only boundaries: this review reads the plan, critique, changes record, research, and live repository state only; it does not modify the plan, critique, research, changes record, or source
* Authority: the review parent compares evidence and writes findings; final outcome, route dispositions, and continuation are recorded in Parent Decision Record
* Initial blockers: none

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|-----------------------|------------------------------------------|-------------|------------------------|
| FR-001 (config/manifest/version-file rooted at `.`) | `release-please-config.json`, `.release-please-manifest.json`, `version.txt` all present at repository root with contents matching each task's binding contract | Met | Direct file inspection and JSON/content validation |
| FR-002 (updates `plugin.json`/`marketplace.json` on merge) | `extra-files` entries configured in `release-please-config.json` targeting the correct `jsonpath`s; no live Release PR has been merged yet | Not assessed | Requires an actual merge to `main`; configuration is in place but the behavior itself is unexercised, consistent with the plan's stated confidence caveat |
| FR-003 (workflow runs on push to `main`) | `.github/workflows/release-please.yml` trigger was `push: branches: [main]` only at review time. **Correction (post-CCR follow-up):** the trigger was later changed to `workflow_run` chained after `ci.yml` ("Validate resume-builder") completes successfully on a push to `main` — release-please still only acts on pushes to `main`, now gated on CI having already passed; see the changes record's post-review correction entry and PR commit `094bf94` | Met | Direct file inspection at review time; superseded trigger mechanism recorded here for traceability, requirement intent still satisfied |
| FR-004 (merge updates `CHANGELOG.md`, tags, creates Release) | Workflow correctly invokes `release-please-action@v5.0.0`; behavior is internal to the action and only observable on a real merge | Not assessed | Same limitation as FR-002 |
| FR-005 (ruleset enforces linear history) | `gh api repos/benarculus/resume-builder/rulesets/23850509` confirms `active` `required_linear_history` targeting `refs/heads/main` | Met | Live API verification |
| NFR-001 (minimum workflow permissions) | Workflow declares exactly `contents: write`, `pull-requests: write`, `issues: write` — no other keys | Met | Direct file inspection matches the objective threshold exactly |
| P01-T01 (`release-please-config.json`) | File content matches the binding contract exactly, including `bootstrap-sha` re-verified as still current | Met | JSON validation plus live `git rev-parse` re-check |
| P01-T02 (`version.txt`) | File contains exactly `0.1.0` plus trailing newline, matching the binding contract | Met | Manual content check |
| P01-T03 (`.release-please-manifest.json`) | File is semantically `{".": "0.1.0"}`, matching the binding contract (pretty-printed, not single-line, but JSON-equivalent) | Met | JSON validation |
| P02-T01 (workflow) | All binding-contract clauses (permissions, SHA pin with tag comment, no explicit `token:`, explicit `config-file`/`manifest-file`) verified present | Met | Direct file inspection; SHA re-verified live against the `v5.0.0` tag |
| P03-T01 (ruleset) | Ruleset created, active, correct rule and target; squash/rebase merge still enabled repository-wide | Met | Live `gh api` verification of both the new ruleset and repository merge-strategy settings |
| Implementation-time update: missing P03 phase heading | Changes record documents the discovery and fix; plan file now shows `<!-- rpi:phase id=P03 -->` and its heading immediately before P03's `Goals:` | Met | Direct plan-file inspection confirms the fix is in place and no other P03 content was altered |
| Critique disposition `PC-001` | Plan's `## Critique Disposition` records `PC-001` as resolved via new task P01-T02; P01-T02 exists with matching content | Met | Cross-check between critique file, plan's disposition table, and the created `version.txt` |
| Plan `## Follow-Up Items` (Conventional-Commit PR-title lint) | Not implemented; correctly recorded as distinct follow-up in both the plan and the changes record, with no implementation or acceptance claim made against it | Met (as follow-up, not a task) | Confirms it was kept out of active scope as required |

### Critique and Follow-Up Assessment

* Latest critique dispositions: one finding, `PC-001 [High]` (missing `version.txt` for `release-please`'s `simple`-strategy primary-file update path). Disposition: resolved directly by the planning parent via new task P01-T02, without a second critique run, matching the "Revise" handling contract.
* Material revisions: the `version.txt` task (P01-T02) and the resulting renumbering of the manifest task to P01-T03 were correctly threaded through the plan's diagrams, requirements, dependencies, decision log (`D5`), and risks. No dependent work was left unreconciled.
* Dependent-work pause assessment: no early resumption occurred; the critique's finding was resolved before any implementation began, so no in-flight work needed pausing.
* Justification assessment: supported — evidence cited (`release-please`'s own `simple.ts`/`default.ts` source) directly grounds both the finding and its resolution; the resolution does not conflict with any confirmed user decision (D1–D3).

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|------------------|-----------------------------|--------------------------|-----------------------------|
| Conventional-Commit PR-title lint | Not part of this plan's confirmed scope; changelog quality only, not version-bump correctness | user/downstream, to be planned separately if desired | Resolved as a distinct, non-blocking follow-up — no route change needed |

### Reviewer Self-Check

* [x] Every supplied requirement, acceptance criterion, in-scope marker, material update, critique disposition, validation result, blocker, remaining item, and plan follow-up has an assessment or explicit gap.
* [x] Findings are substantive, evidence-grounded, severity-graded, and use stable `RV-xxx` IDs with expected and observed behavior, a resolution condition, and one proposed route each.
* [x] Execution status, assessed outcome, validation coverage, limitations, and proposed routes are complete and internally consistent.
* [x] The summary is scoped and advisory, findings keep their supporting context together, and acceptance coverage distinguishes demonstrated gaps (none) from unassessed behavior (FR-002, FR-004 pending a live run).
* [x] Standard review completely assessed the material boundary while omitting restatement, cosmetic feedback, exhaustive strengths, low-impact suggestions, and continual narration.
* [x] The review did not mutate source, the plan, critique, research, or changes record, did not execute validation beyond read-only re-verification, and confirmed the one candidate observation (RV-001) directly at its cited evidence before recording it.
* Checked boundary: FR-001–FR-005, NFR-001, P01-T01, P01-T02, P01-T03, P02-T01, P03-T01, the P03 phase-heading fix, `PC-001` disposition, and the plan's one follow-up item.
* Missing or limited evidence: FR-002 and FR-004's actual runtime behavior (updating `plugin.json`/`marketplace.json`, creating `CHANGELOG.md`/tag/Release) is not assessed pending a real push/merge to `main`; this is an evidence limit, not a demonstrated defect.
