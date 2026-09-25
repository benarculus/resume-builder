<!-- markdownlint-disable-file -->
# Task Research: release-pipeline

| Field              | Value                    |
|--------------------|--------------------------|
| Date               | 2026-09-22               |
| Researcher / agent | rpi-research             |
| Output mode        | convergence              |

## Executive Summary

* Bottom line: Adopt **release-please** (manifest-driven, `release-type: simple`) as a GitHub Actions workflow that watches `main`, opens a standing Release PR from Conventional Commit history, and — once merged — bumps `plugin.json` and `.github/plugin/marketplace.json`, updates `CHANGELOG.md`, tags the commit, and publishes a GitHub Release.
* Why this matters: resume-builder has no release workflow, no tags, no CHANGELOG, and two separate `"version"` fields (`plugin.json`, `marketplace.json`) that are both still `0.1.0` and would otherwise need manual, error-prone syncing on every change.
* Research status: complete. All three material decisions (tool choice, starting version, merge-history hygiene) were presented to the user with evidence and confirmed during this session — see Decisions and Feedback.
* Confidence and uncertainty: high confidence in the tool choice and mechanics (primary vendor docs plus direct repo inspection); the one lower-confidence item (semantic-release's plugin requirements, based on general prior knowledge rather than freshly re-verified sources) is disclosed inline and does not affect the confirmed recommendation.

## What You May Not Know

* Commit history already leans on Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`, `perf:`, `test:` — see C4) even though nothing enforces it today. That is exactly the input release-please needs, so no new commit-message discipline has to be invented — it mostly needs to be made consistent.
* The repo is **not** an npm or PyPI package (no `package.json`, `setup.py`, or `pyproject.toml` — see C5). This rules out release-type presets like `node` or `python` and rules out `semantic-release`'s natural npm-native flow without extra plumbing; it also means there is nothing to "publish" beyond the Git tag/GitHub Release/CHANGELOG themselves, which simplifies the token/permissions story.
* Two files independently carry a `version` field that must move together (C2, C3) — `plugin.json` at the repo root and `.github/plugin/marketplace.json`, which itself nests a second copy at `plugins[0].version`. Any pipeline choice must update three JSON locations atomically, not one.
* The repo currently allows all three merge strategies and has no branch protection (C6). release-please's changelog quality depends on linear, one-commit-per-PR history (squash merge recommended by its own docs, W1); mixed merge-commit history would still work but could pollute changelog entries with noisy sub-commits from a feature branch.

## Findings

### A GitHub-native, PR-gated release tool fits this repo better than a CI-side auto-commit tool

release-please opens and continuously updates a standing "Release PR" containing the next CHANGELOG entry and version bump; a human merges it to cut the release (W1). semantic-release, by contrast, computes the next version and publishes on every push to `main` inside the CI job itself, typically committing the version bump directly back to the branch via `@semantic-release/git` — no human-reviewed diff before the tag is cut.

* Questions: Q1, Q2
* Evidence state: evidence-backed finding
* Evidence: W1 (release-please opens/merges Release PRs, tags on merge, creates GitHub Release), C1 (repo has no release/versioning automation today), C6 (no branch protection, all merge strategies allowed — i.e., nothing currently prevents an unreviewed auto-commit pipeline, which is itself a reason to prefer the PR-gated model for a solo-maintained repo where the PR is the existing review point)
* Confidence and limits: high. The trade-off is a matter of maintainer preference, not a technical constraint; semantic-release remains viable if the user wants same-merge releases (see Alternatives).

Every existing merge to `main` in this repo's history went through a pull request (`git log` shows `Merge pull request #N` entries interleaved with `feat:`/`fix:` commits). A Release-PR model keeps that same human-approval shape for the one additional artifact type (the version bump/changelog) instead of introducing a second, unreviewed write path to `main`.

### release-please can update all three version locations and generate a CHANGELOG without repo-specific scripting

release-please's `simple` release type expects a `version.txt` + `CHANGELOG.md` pair as its "primary" version source, and its `extra-files` configuration (JSON updater) can additionally patch arbitrary `version` fields in other JSON files by JSONPath (W2).

* Questions: Q3
* Evidence state: evidence-backed finding
* Evidence: W2 (documented `extra-files` JSON updater with `jsonpath`), C2 (`plugin.json` → `$.version`), C3 (`marketplace.json` → `$.metadata.version` and `$.plugins[0].version`, two separate JSONPath targets in the same file)
* Confidence and limits: high for the mechanism; the exact config has not been dry-run in this repo (no code was written during research — research is read-only), so first execution should be validated against a fork or a draft PR before trusting the automation unattended.

Concrete config shape (for the eventual implementation phase, not applied during research):

```json
// release-please-config.json
{
  "packages": {
    ".": {
      "release-type": "simple",
      "extra-files": [
        { "type": "json", "path": "plugin.json", "jsonpath": "$.version" },
        { "type": "json", "path": ".github/plugin/marketplace.json", "jsonpath": "$.metadata.version" },
        { "type": "json", "path": ".github/plugin/marketplace.json", "jsonpath": "$.plugins[0].version" }
      ]
    }
  }
}
```

```json
// .release-please-manifest.json
{ ".": "0.1.0" }
```

### GitHub Actions permissions and token choice are simple here because there is nothing to publish

release-please-action's own quick-start recommends a PAT specifically so that the release event (or the Release PR merge) can retrigger *other* workflows, e.g., a downstream "publish to npm" job (W3). This repo has no publish target — the Git tag and GitHub Release are the deliverable — so the default `secrets.GITHUB_TOKEN` with `contents: write`, `pull-requests: write`, and `issues: write` is sufficient and keeps the pipeline inside the existing least-privilege posture the repo already uses (every current workflow scopes `permissions: contents: read` explicitly, C7).

* Questions: Q4
* Evidence state: evidence-backed finding
* Evidence: W3 (release-please-action README: default `GITHUB_TOKEN`, PAT only needed to chain workflows), C7 (`ci.yml` explicit `permissions: contents: read`)
* Confidence and limits: superseded by implementation evidence. The source correctly explains GitHub's `GITHUB_TOKEN` anti-recursion behavior, but the original disposition considered only downstream tag/release workflows. The generated Release PR must also trigger ordinary `pull_request` CI, so a PAT or GitHub App identity is required for this repository's selected branch-gated design.

## Recommendation and Alternatives

* Recommendation or decision state: Adopt **release-please** with `release-type: simple`, a manifest config (`release-please-config.json` / `.release-please-manifest.json`), and JSON `extra-files` updaters for `plugin.json` and both version fields in `marketplace.json`. Run it via `googleapis/release-please-action@v5.0.0` on push to `main`. **Post-CCR correction:** the implemented workflow now uses a repository-scoped, short-lived GitHub App installation token rather than the default `GITHUB_TOKEN`, because GitHub's anti-recursion rule otherwise prevents the generated Release PR from triggering the normal PR CI gate. See the implementation changes record for the final hardened token flow.
* Rationale: Matches the repo's non-npm, non-PyPI, single-artifact shape (C5); needs no new language runtime in CI beyond the Actions themselves; preserves the PR-gated review habit already used for every change (C1, C6); handles the two-file, three-field version-sync problem natively (C2, C3, W2); and uses a down-scoped GitHub App installation token so the generated Release PR can trigger that gate (post-CCR correction to W3).
* What could change this result: if the user later wants same-push (no human release-PR step) releases, or wants releases to also trigger a marketplace/registry publish step requiring a second workflow trigger.

| Option                              | Benefits                                                                                                          | Costs and risks                                                                                                                                       | Evidence      | Disposition |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|---------------|-------------|
| release-please (manifest, `simple`) | PR-gated review of every version bump; native multi-file JSON version sync; no new runtime; matches existing PR habit | Changelog quality degrades if PRs aren't squash-merged (W1); first-release bootstrap version is a manual decision                                    | W1, W2, W3, C1–C7 | selected    |
| semantic-release + replace plugin    | Very mature, huge plugin ecosystem, works for any file type                                                        | Node/npm-native tool bolted onto a Python-only repo; typically auto-commits the version bump on every push with no PR review; needs 2+ extra plugins (`@semantic-release/changelog`, `@semantic-release/git`, `semantic-release-replace-plugin`) just to reach parity with release-please's built-in behavior | prior knowledge of semantic-release's plugin model (not independently re-verified this cycle; treat as lower-confidence) | rejected — heavier toolchain and weaker review gate for no added capability here |
| Manual git tag + GitHub "auto-generate release notes" | Zero new tooling or config; uses a GitHub-native button/API                                                         | No automatic version bump in `plugin.json`/`marketplace.json`; no CHANGELOG.md file; semver decision is entirely manual and easy to get inconsistent over time | C1–C3 (files exist and would still need manual edits) | rejected — doesn't satisfy "semantically track" automation goal |
| Keep no release pipeline             | No effort                                                                                                            | Version drift between `plugin.json` and `marketplace.json` already exists (both `0.1.0` with no history of being bumped, C2/C3); no discoverable release history for consumers of the plugin | C1, C2, C3    | rejected — is the status quo the user asked to change |

## Scope and Questions

* Goal: choose and specify a release pipeline that lets the maintainer semantically (SemVer, via commit intent) track versioned updates to the `resume-builder` Copilot CLI plugin.
* Audience and use: repo maintainer (solo), to be implemented in a follow-on planning/implementation phase.
* In scope: repository-native versioning/release automation (tooling choice, config shape, token/permissions, version-file sync, changelog generation).
* Out of scope: publishing to any external marketplace/registry beyond this GitHub repo; CI test/validation pipeline changes unrelated to releases; retroactively rewriting past commit history.
* Decision and evidence criteria: fits the repo's actual artifact shape (no npm/PyPI package); minimal new runtime/toolchain; preserves or improves the existing PR-review posture; automatically keeps `plugin.json` and `marketplace.json` versions in sync; produces a durable, dated changelog.
* Requested output: recommendation (convergence) with alternatives and evidence.

| ID | Question                                                                                     | Source   | Status   |
|----|-----------------------------------------------------------------------------------------------|----------|----------|
| Q1 | Should the release pipeline gate releases behind a human-reviewed PR, or auto-release on every merge to `main`? | inferred from repo's existing PR-only workflow | answered |
| Q2 | Does the repo's current commit/merge hygiene support automated Conventional-Commit parsing?    | inferred | answered (yes, with a caveat — see Risks) |
| Q3 | How can one pipeline update version fields in two separate JSON files (three fields total)?    | explicit (task implies multi-file plugin repo) | answered |
| Q4 | What GitHub Actions token/permissions does the chosen tool need, and does it fit the repo's least-privilege posture? | inferred from repo's existing workflow permissions blocks | answered |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|-------|---------------------------|--------|-------|----------------------------|----------|-------------------|
| D1 | Adopt release-please (manifest, `release-type: simple`) as the release pipeline | confirmed | user | Confirms the recommended tool before any implementation phase begins | W1, W2, W3 | Determines whether planning proceeds with release-please or an alternative |
| D2 | Starting version for the first automated release: keep `0.1.0` (continue current pre-1.0 numbering) vs. bump to `1.0.0` (declare the plugin stable) | confirmed — keep `0.1.0` | user | release-please needs an explicit starting point in `.release-please-manifest.json`; this is a product decision (is the plugin "stable" today?), not a technical one | C2, C3 | Sets the first tag/release number and whether pre-1.0 SemVer rules (any `feat:` can be a breaking minor) apply going forward |
| D3 | Enforce linear history via a **repository ruleset** ("Require linear history" rule) rather than disabling merge strategies at the repo-settings level, since the user manages branch protection through rulesets | confirmed | user | Repo currently allows all three merge strategies with no branch protection (C6); release-please's own guidance recommends squash-merge for clean changelogs (W1); GitHub's ruleset "Require linear history" rule blocks merge commits while still permitting squash or rebase merges (W5) | W1, W5, C6 | Blocks the noisy "Merge pull request #N" commits release-please would otherwise have to skip/misparse; still allows rebase merges (multiple Conventional Commits per PR), which release-please parses fine — only true merge commits are the problem |

## Risks and Open Questions

| Priority | Type            | Risk, question, or research item                                                                 | Impact                                                              | Smallest action or evidence needed                                   | Owner      |
|----------|-----------------|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------|------------|
| L        | risk (resolved) | Mixed merge strategies (no squash-only enforcement) could add noisy changelog entries               | Cosmetic — CHANGELOG.md readability, not correctness of version numbers | Add a "Require linear history" ruleset on `main` (D3, confirmed)          | user       |
| L        | further research | If a future marketplace/registry publish step is added, GITHUB_TOKEN may not retrigger that workflow off the release event | Would require a PAT or GitHub App token at that time, not now           | Re-research token scoping only if/when a publish-on-release step is added | downstream |
| L        | further research | Whether to enforce Conventional Commits at commit-time (e.g., a commit-msg hook or PR-title lint) so release-please never sees a malformed commit | Prevents a mis-typed commit from being silently skipped/misclassified   | Evaluate a lightweight PR-title lint (e.g., a GitHub Action) in the implementation phase | downstream |

## Planning Readiness and Next Step

| Field                            | Record                                                                                                                   |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Research disposition              | executed                                                                                                                   |
| Decision participation            | user-owned; standalone `/hve-core:rpi-research` invocation, no active RPI Agent or `rpi-quick` parent detected            |
| Planning Readiness                | Ready — D1 (release-please), D2 (start at 0.1.0), and D3 (enforce via a "Require linear history" ruleset on `main`) are all confirmed |
| Research depth and lanes          | One executed cycle, all three waves completed inline (no subagent dispatch — lanes were low-volume and tightly coupled: one repo inspection lane, one external-tooling lane) |
| Blockers                          | none                                                                                                                       |
| Output mode and planning support  | convergence; supports planning directly                                                                                    |
| Continuation owner                | user (standalone research; no active `rpi-quick` or automatic RPI Agent parent to hand off to)                            |
| Required gates or confirmations   | D1, D2, D3 all confirmed during this research session (see Direction and Participation Log)                              |
| Next action                       | Invoke `/hve-core:rpi-plan` (or a manual implementation) using this artifact as input to draft the release-please workflow, config, and the `main` ruleset |
| Primary evidence file             | .copilot-tracking/research/2026-09-22/release-pipeline-research.md                                                        |

## Research Record

### Method and Boundaries

| Field                            | Record                                                                                                    |
|------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Research posture and provenance    | balanced; default (bounded internal task — a well-defined tool choice — but with a real, evidence-affecting alternatives space worth surveying) |
| Completion basis                   | Both waves' candidate sources (repo files/history and the two leading external tools) were exhausted for this decision; contrarian wave found no evidence that would change the recommendation, only two hygiene-level caveats already captured as Decisions/Risks |
| Explicit limits or deadline        | none stated by caller                                                                                        |
| Codebase and external scope        | workspace scope: root config files, `.github/workflows/*`, `.github/dependabot.yml`, `.github/plugin/marketplace.json`, `plugin.json`, git history/tags/releases; external scope: release-please and release-please-action documentation, Conventional Commits spec |
| Initial candidate areas            | release-please, semantic-release, changesets/standard-version family, manual git-tag + GitHub auto-notes  |
| Evidence root                      | .copilot-tracking/research/2026-09-22/ (default resolved root)                                                |
| Constraints and excluded sources   | research-only — no source files, workflows, or config were created or modified during this research           |
| Prior knowledge                    | No prior research artifact existed for this topic in `.copilot-tracking/research/`; general working knowledge of `semantic-release`'s plugin architecture was used for the Alternatives row but was not independently re-verified this cycle (flagged as lower-confidence in that row) |

### Extensions and Participation

#### Extension Registry

| Kind        | Candidate                                  | Provenance and scoped contract                                                                 | Selected or skipped reason                                                                 |
|-------------|---------------------------------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| instruction | `copilot-tracking.instructions.md`          | Shared RPI tracking-artifact conventions (path, format)                                            | selected — governs artifact location and structure                                        |
| skill       | `pr-reference`                              | Listed as an available skill; description concerns PR referencing conventions, not release tooling | skipped — no material fit for this research topic                                          |
| skill       | `supply-chain-security`                     | Listed as an available skill; concerns dependency/supply-chain posture, not release/version tooling | skipped — no material fit; release pipeline choice does not touch dependency provenance    |
| specialist  | `hve-core:rpi-researcher`                   | Sub-agent usable for independent delegated lanes                                                   | skipped — both lanes (repo inspection, external tooling) were low-volume and tightly coupled to parent synthesis; handled inline per the flow's delegation criteria |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|-----------------------|--------------------------------------|--------------------------------------|-------------------------------------|
| intake | Topic given as "research a release pipeline, so I can semantically track updates to the resume-builder" — no explicit scope/output-mode/posture supplied | No-interaction: request is unambiguous (tool selection + config for SemVer-based release automation on this specific repo); proceeded without an intake question and inferred `convergence` output mode from the clearly decision-seeking phrasing | Proceeded directly to Cycle 1 |
| convergence | D1: confirm release-please as the recommended tool over semantic-release/manual tagging | User selected "Yes, use release-please (Recommended)" | D1 confirmed; unblocks planning on the recommended tool |
| convergence | D2: confirm first-release bootstrap version (0.1.0 vs 1.0.0) | User selected "Continue pre-1.0 (start from 0.1.0)" | D2 confirmed; `.release-please-manifest.json` should seed `{ ".": "0.1.0" }` |
| convergence | D3: confirm merge-history hygiene approach; user noted branch protection is managed via repository rulesets rather than repo-settings merge toggles, prompting a targeted re-check of GitHub's ruleset rule catalog (W5) | User confirmed enforcing linear history via a "Require linear history" ruleset rule on `main` | D3 confirmed with the ruleset-native mechanism; Risks table row updated from open risk to resolved |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: balanced; no caller-imposed limits or deadline.

##### Wave 1: Wider

* Focus and lanes: (a) inline — inventory the repo's current release/versioning surface (CI workflows, dependabot, version-bearing files, commit/tag/release history); (b) inline — survey the release-automation tool landscape for a Conventional-Commits-driven, non-npm-native repo (release-please, semantic-release, changesets/standard-version, manual tag + GitHub auto-notes).
* Evidence or worker pointers: C1–C7 (repo inventory); initial identification of release-please and semantic-release as the two leading Conventional-Commits-driven tools, plus manual tagging as a baseline.
* Reflection: Confirmed no existing release automation (C1) and found two independent JSON version fields needing synchronized updates (C2, C3) — this became the deciding technical constraint for Wave 2.

##### Wave 2: Deeper

* Focus and lanes: inline — read release-please's primary README and manifest-releaser docs for mechanics (Release PR lifecycle, versioning strategies, release types) and its `customizing.md` for the JSON `extra-files`/`jsonpath` updater needed for `plugin.json`/`marketplace.json`; read the Conventional Commits v1.0.0 spec to confirm the `feat`/`fix`/`!`/`BREAKING CHANGE` rules already visible in this repo's commit history (C4) map cleanly onto release-please's parsing.
* Evidence or worker pointers: W1 (release-please README — Release PR model, `autorelease:*` labels, `Release-As:` override), W2 (customizing.md — `extra-files` JSON/YAML/XML/TOML updaters with `jsonpath`), W4 (Conventional Commits v1.0.0 spec).
* Reflection: The JSON `extra-files` updater directly solves the two-file/three-field version-sync requirement (C2, C3) without custom scripting — this became the strongest technical evidence for the recommendation.

##### Wave 3: Contrarian

* Focus and lanes: inline — actively looked for reasons release-please would be the wrong choice: checked whether the repo's merge/branch-protection settings would defeat its clean-changelog assumption (C6), checked release-please-action's own token/permission guidance to see whether a PAT is unavoidable (it is not, for this repo's no-publish shape) (W3), and weighed semantic-release/manual-tag as genuine alternatives rather than strawmen.
* Evidence or worker pointers: C6 (no branch protection, all merge strategies allowed) weakens — but does not disprove — the "clean changelog" assumption; W3 shows the PAT recommendation is conditional on needing to retrigger a second workflow, which does not apply here. No evidence found that would favor semantic-release or manual tagging over release-please for this specific repo.
* Reflection: Contrarian wave produced two hygiene-level caveats (squash-merge enforcement, PAT-only-if-publishing-later) rather than a reason to change the recommendation; both were captured as Decisions/Risks rather than silently dropped.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence or worker pointers | Disposition | Rationale | User-facing effect |
|--------------------|-------------------------------|----------------|--------------|------------------------|
| release-please fits this repo's non-npm/non-PyPI, PR-gated, multi-JSON-version shape | W1, W2, W3, C1–C7 | accepted | Directly matches every constraint found in Waves 1–2 with no contrary evidence in Wave 3 | Drove the Recommendation section |
| semantic-release is a viable but heavier alternative | prior knowledge (not independently re-verified this cycle) | deferred | Lower-confidence source; recorded as an alternative rather than dismissed, and flagged as such | Alternatives table, disposition "rejected" with the confidence caveat stated |
| Manual git tag + GitHub auto-notes is a valid low-effort baseline | C1–C3 | rejected | Does not satisfy the "semantically track" automation the user explicitly asked for | Alternatives table |
| Mixed merge strategies could reduce changelog quality | W1, C6 | deferred to user decision | Not a blocker, but material enough to flag before adoption | Decisions D3, Risks |
| First-release bootstrap version is undetermined | C2, C3 | accepted — user confirmed `0.1.0` | Purely a product/versioning-policy choice, resolved directly by the user | Decisions D2 |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: scope coverage — the caller's task (choose and specify a release pipeline) is fully covered; material claims are evidence-backed; remaining open items (D2, D3) are user-policy decisions, not evidence gaps that a further cycle could resolve.
* Readiness or revalidation effect: Planning Readiness set to Ready pending the two flagged, non-blocking user decisions.

### Evidence Log

* Delegation: inline: both waves' lanes (repo inventory, external tooling) were low-volume and tightly coupled to parent synthesis; no subagent dispatch was warranted per the flow's delegation criteria.

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|----|--------------------|------------------------|----------------------------|-------------|--------------|-----------|
| C1 | No release/versioning workflow exists; no git tags; no `gh release list` output; no `CHANGELOG.md` in the repo | workspace root — `.github/workflows/` (ci.yml, codeql-analysis.yml, dependency-review.yml, advisory-malware.yml), `git tag -l`, `gh release list`, `find . -iname CHANGELOG*` | not applicable | search/read | high | Confirms status quo has zero release automation |
| C2 | `plugin.json` carries `"version": "0.1.0"` at `$.version` | `plugin.json` (repo root) | not applicable | read | high | One of three version fields needing sync |
| C3 | `.github/plugin/marketplace.json` carries `"version": "0.1.0"` at both `$.metadata.version` and `$.plugins[0].version` | `.github/plugin/marketplace.json` | not applicable | read | high | Two of three version fields needing sync, in one file |
| C4 | Recent 100 commits already use Conventional-Commit-style prefixes (`fix:` ×9, `docs:` ×5, `feat:` ×3, `chore(deps):` ×3, `chore:` ×2, `test:`, `perf:`, `docs(research):`, `docs(plan):`, `chore(deps-dev):`) | `git log --oneline -100` (prefix frequency count) | not applicable | search | high | Confirms release-please's Conventional-Commits parsing has real input to work with today |
| C5 | No `package.json`, `setup.py`, or `pyproject.toml` exists; repo ships as a Copilot CLI "Agent Plugins" plugin (schema `agent-plugins.org/schemas/1.0.0`), not an npm or PyPI package | `plugin.json`, `requirements.txt`/`requirements-dev.txt` present but no packaging manifest, `find` for setup.py/pyproject.toml | not applicable | search/read | high | Rules out `node`/`python` release-please presets; favors `simple` + `extra-files` |
| C6 | Repo allows `allow_merge_commit`, `allow_rebase_merge`, and `allow_squash_merge` all `true`; branch `main` has no branch protection | `gh api repos/benarculus/resume-builder`, `gh api repos/benarculus/resume-builder/branches/main/protection` (404 "Branch not protected") | not applicable | gh api | high | Basis for Decision D3 and the squash-merge risk |
| C7 | Existing workflows (e.g. `ci.yml`) explicitly scope `permissions: contents: read` | `.github/workflows/ci.yml` | not applicable | read | high | Establishes the repo's existing least-privilege convention that the release workflow's token/permissions should match |
| W1 | release-please parses Conventional Commits, opens/keeps-updated a Release PR, and on merge updates the changelog, tags the commit, and creates a GitHub Release; recommends squash-merge for clean history | release-please README, https://github.com/googleapis/release-please | 2026-09-22, main branch docs | web_fetch | high | Core mechanics evidence for the recommendation |
| W2 | `extra-files` supports a `json` updater type with a `jsonpath` field to patch arbitrary `version`-bearing JSON fields; also documents `simple` release type (`version.txt` + `CHANGELOG.md`) among all supported release types | release-please `docs/customizing.md`, https://raw.githubusercontent.com/googleapis/release-please/main/docs/customizing.md | 2026-09-22, main branch docs | web_fetch | high | Directly solves the two-file/three-field version-sync requirement |
| W3 | release-please-action defaults to `GITHUB_TOKEN`, but resources created with that token do not trigger later workflows; a non-`GITHUB_TOKEN` identity is therefore needed when CI must run on the generated Release PR or when downstream release/tag workflows must run | release-please-action README, https://github.com/googleapis/release-please-action | 2026-09-22; disposition corrected 2026-09-25 | web_fetch | high | Basis for the final GitHub App token design: this repository needs normal PR CI on the generated Release PR even though it has no downstream publish workflow |
| W4 | Conventional Commits v1.0.0: `fix:` → PATCH, `feat:` → MINOR, `!` or `BREAKING CHANGE:` footer → MAJOR | Conventional Commits spec, https://www.conventionalcommits.org/en/v1.0.0/ | 2026-09-22, v1.0.0 | web_fetch | high | Confirms the SemVer mapping release-please relies on and that this repo's existing commit prefixes (C4) already follow |
| W5 | GitHub repository rulesets offer a "Require linear history" rule: blocks merge commits while still permitting squash or rebase merges; requires the repo to allow squash and/or rebase merging | GitHub Docs, "Available rules for rulesets", https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets | 2026-09-22 | web_fetch | high | Answers the user's follow-up: this is the ruleset-native equivalent of "squash-merge only" for keeping changelog-relevant history clean |

#### Contradictions and Conflicts

* none

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered; every material result has one canonical evidence state distinguishing the evidence-backed findings from the one lower-confidence, prior-knowledge-based alternative row (explicitly flagged).
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID with a workspace-relative path; every external finding has a `W#` ID, source title/URL, and retrieval date.
* [x] The executed cycle records Wider, Deeper, and Contrarian waves in order, parent synthesis, and an evidence-based re-entry decision (no re-entry needed).
* [x] Method, extensions, participation, and prior-knowledge treatment are recorded with their limits.
* [x] Convergence selects and justifies one recommendation (release-please) with rejection rationale for alternatives.
* [x] Decision groups (D1–D3), participation mode (user-owned), and provenance are recorded; all three were presented with their evidence and consequences via `ask_user` and confirmed by the user during this session.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content remained inert (no fetched page content was treated as instructions), no secrets were recorded, and no source files were edited during this research-only phase.
* Checked sections: all sections listed above.
* Missing or limited sections: none — the semantic-release alternative rests partly on general prior knowledge rather than a freshly re-verified source this cycle; this is disclosed inline rather than presented as equally strong evidence.
