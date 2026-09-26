<!-- markdownlint-disable-file -->
# RPI Plan Critique: Release pipeline for resume-builder

## Metadata

* Task ID: release-pipeline
* Critique date: 2026-09-22
* Plan: .copilot-tracking/plans/2026-09-22/release-pipeline-plan.md
* Critique execution status: Complete
* Critique depth: standard
* Depth provenance: default (no explicit user request for deep)
* Invocation consumed: yes
* Attempt ID and kind: release-pipeline-critique-001, initial
* Candidate identity and saved hash boundary: `.copilot-tracking/plans/2026-09-22/release-pipeline-plan.md`, SHA-256 `a2305084d7d936cedce36864172239fabe79e1fdf8dacb782ca31f5ae1f4e74b` of all plan content preceding its `## Critique Disposition` section, as reserved by the planning parent
* Current-run provenance: immediate planner activation — this critique was invoked in the same uninterrupted planning execution immediately after the plan reserved this attempt
* Original attempt and recovery approval: not applicable — this is the initial attempt, no prior attempt exists for this task

## Inputs and Criterion Boundary

* Task context and caller requirements: Add a release pipeline (`release-please`) to `resume-builder` so version updates to `plugin.json` and `.github/plugin/marketplace.json` are tracked semantically via Conventional Commits, per confirmed user decisions D1 (tool = release-please), D2 (start at `0.1.0`), and D3 (enforce linear history via a repository ruleset).
* Research and evidence considered: .copilot-tracking/research/2026-09-22/release-pipeline-research.md (evidence C1–C7, W1–W5); the plan's own directly-read sources (plugin.json, .github/plugin/marketplace.json, .github/workflows/ci.yml, .github/dependabot.yml); the plan's cited external tags/SHAs for `googleapis/release-please-action`.
* Decisions, dependencies, task Goals, and task Requirements considered: all three confirmed decisions (D1–D3) and the one agent-owned decision (D4, `bootstrap-sha` pinning); all phase/task Goals, Requirements, Details, References, and Dependencies for P01-T01, P01-T02, P02-T01, P03-T01; FR-001–FR-005 and NFR-001.
* Assessment boundary: This critique reads the plan text and its cited research/repository evidence only. It does not execute the workflow, does not create a live GitHub ruleset, and does not run `release-please` against this repository's actual commit history. Any conclusion about the runtime behavior of `release-please`'s `simple` strategy rests on the strategy's published source (`src/strategies/simple.ts`) rather than an observed run in this repository.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|---|---|---|
| FR-001 (manifest + config at root) | Covered | P01-T01, P01-T02 define both files with a concrete, checkable JSON contract. |
| FR-002 (sync plugin.json + marketplace.json) | Partial | The `extra-files` mechanism is correctly evidenced (research W2), but see PC-001: the plan does not address the `simple` strategy's own primary `version.txt` file, which is a separate, undocumented write target not covered by FR-002's stated scope. |
| FR-003 (workflow runs on push to main) | Covered | P02-T01 specifies the trigger, permissions, and action pin precisely. |
| FR-004 (changelog, tag, release on merge) | Partial | Covered for `CHANGELOG.md`/tag/release generically, but tied to the same PC-001 concern about the `simple` strategy's primary-file update path. |
| FR-005 (linear history ruleset) | Covered | P03-T01 states the binding outcome (active `required_linear_history` rule on `refs/heads/main`) independent of the specific `gh api` invocation shown, which is explicitly marked illustrative. |
| NFR-001 (minimal permissions) | Covered | P02-T01's binding contract matches the vendor's documented minimum and the repository's existing least-privilege convention (evidence C7). |
| D1–D4 (confirmed/agent-owned decisions) | Covered | All four are traced from research or stated with an explicit, evidence-based rationale (D4); no decision is asserted without a source. |
| P01-T01 (`release-please-config.json`) | Partial | See PC-001 — the `release-type: simple` choice needs one additional piece of resolved evidence before implementation. |
| P02-T01 (workflow file) | Covered | Action pin, trigger, permissions, and default-token rationale are all evidence-backed and internally consistent with research W3/C7. |
| P03-T01 (ruleset) | Covered | Binding requirement is separated from the illustrative command; no blocker. |
| Diagrams (Before/After/phase) | Covered | Consistent Mermaid init line across all 5 diagrams (verified directly); stable node IDs reused; dashed `new` class and phase highlight both use explicit text colors. |

## Verdict

* Verdict: Revise
* Rationale: One material, evidence-based gap (PC-001) affects the plan's core mechanism (P01-T01, FR-002, FR-004) and is resolvable with a small, targeted plan correction rather than a new planning cycle. No other finding rises to blocking severity.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: `release-type: simple` writes a primary `version.txt` file that this plan never creates

* Related IDs: FR-001, FR-002, FR-004, P01-T01, P01-T02
* Evidence: `release-please`'s `Simple` strategy (`src/strategies/simple.ts` on the `googleapis/release-please` `main` branch, retrieved 2026-09-22) unconditionally pushes an `Update` for `this.versionFile` (default `'version.txt'`) on every release, with `createIfMissing: false` — distinct from and in addition to whatever `extra-files` updaters are configured. The plan's P01-T01 only configures `extra-files` for `plugin.json` and `marketplace.json`; it does not create a `version.txt`, does not set a custom `versionFile` option, and does not otherwise address this primary-file update path.
* Impact: With `createIfMissing: false` and no `version.txt` present, the first Release PR's version-file update is at best a silent no-op the maintainer never asked for and at worst causes the release process to surface an error trying to update a file that does not exist — either way this was not evidenced, decided, or accounted for anywhere in the plan, even though it is a direct mechanical consequence of the confirmed `release-type: simple` choice (research D1) that P01-T01 implements. This sits squarely inside the plan's core deliverable (FR-002/FR-004), not a peripheral concern.
* Smallest useful change: Before implementation, resolve this with the smallest evidence needed — either (a) confirm whether `release-please` silently creates `version.txt` on first run despite `createIfMissing: false` reading as it does in source (re-check the file-update application path, not just the strategy definition, since `createIfMissing` semantics may differ between "apply an update" and "the update exists"), or (b) explicitly add a tracked `version.txt` (seeded to `0.1.0`, matching D2) as a new P01 task so the strategy's primary file exists before the first workflow run, and add it to the plan's Before/After diagrams and Sources. Do not proceed to implementation with this open.
* Action owner: planning parent
* Exact resolving evidence: either a corrected P01-T01/new P01-T03 task creating `version.txt` with its own Goals/Requirements/Details/References, or a plan annotation citing specific evidence (e.g., the file-update applier code, or a `release-please` maintainer-documented behavior) that `version.txt` is auto-created regardless of `createIfMissing: false`, with the plan's Risks table updated to note the resulting extra tracked file if one appears.
* Decision route: direct planner correction — this is an evidence gap the planning parent can close by reading slightly more of `release-please`'s source or by adding one small task; it does not require a new user decision unless resolving it reveals that an unwanted `version.txt` file is unavoidable, in which case the planner should surface that specific trade-off to the user before finalizing.

## Strengths and Residual Risk

* P02-T01's action-pin, permissions, and default-token reasoning is precise, internally consistent with the repository's existing `ci.yml` convention, and independently verified against the pinned action's own `action.yml` (retrieved 2026-09-22) during this critique — no discrepancy found.
* P03-T01 correctly separates the binding outcome (an active `required_linear_history` ruleset rule) from the illustrative `gh api` command, so a syntax quibble in the example cannot block implementation.
* The plan's own `Risks and Open Questions` and `What You May Not Know` sections already surface two smaller residual risks (HEAD-SHA drift for `bootstrap-sha`, inconsistent historical commit prefixes) transparently and with proportionate, low-severity dispositions; both remain accepted residual risk and needed no further critique action.
* All five Mermaid diagrams use the exact prescribed `themeVariables` initialization string, and node/edge additions are distinguishable by the dashed `new` class and `Added:` labels, not color alone.

## Questions or Blocking Evidence Gaps

* None that require a user decision at this time. PC-001 is a planner-resolvable evidence gap, not a question for the user, unless resolution shows an unwanted file must be created (see PC-001's decision route).

## Limitations

* This critique did not execute `release-please` or its action against a real repository or fork, so PC-001's precise runtime failure mode (silent no-op vs. hard error vs. auto-create) is asserted from the strategy's source definition, not an observed run. The planning parent's resolving action should close this precisely rather than assume the more benign outcome.
* GitHub repository ruleset creation semantics (P03-T01) were not exercised against a live repository during this critique; the plan's own text already treats the exact API/CLI syntax as illustrative, so this was not raised as a separate finding.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning parent
* Smallest next action: Resolve whether `release-type: simple` requires a pre-created `version.txt`, and revise P01 accordingly (either add a small task creating it, or cite specific evidence that none is needed), then finalize without another critique.
* User response required: no — resolvable directly by the planning parent from evidence; escalate to the user only if resolution shows an unwanted file is unavoidable.
