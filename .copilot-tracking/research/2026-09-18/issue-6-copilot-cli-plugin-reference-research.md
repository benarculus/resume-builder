<!-- markdownlint-disable-file -->
# Task Research: issue-6-copilot-cli-plugin-reference

| Field | Value |
|---|---|
| Date | 2026-09-18 |
| Researcher / agent | rpi-research |
| Output mode | convergence |

## Executive Summary

* Bottom line: issue `benarculus/resume-builder#6` is valid. GitHub's current Copilot CLI docs treat `marketplace.json` as an official marketplace manifest, not an unofficial host convention, and treat `plugin.json` as the plugin manifest. The current repo has `.github/plugin/marketplace.json` but no root `plugin.json`, so the README and packaging are not aligned with the official plugin reference yet.
* Why this matters: closing #6 requires more than a wording change. A user following the official CLI plugin path should be able to add the marketplace or install the repository using documented `copilot plugin` commands, and the repository should contain the manifest files those commands expect.
* Research status: complete for the issue #6 planning question.
* Confidence and uncertainty: high confidence on the official command and manifest model because the evidence comes from GitHub Docs retrieved on 2026-09-18. High confidence on the selected planning direction because the user chose the Agent Plugins 1.0 migration after reviewing the trade-off.

## What You May Not Know

`marketplace.json` is official, but it is not the plugin's own manifest. GitHub's docs say a marketplace repository uses `.github/plugin/marketplace.json` to list plugins, while each plugin directory needs a `plugin.json` manifest. With the current marketplace entry pointing `"source": "."`, the repository root is the plugin directory and should contain `plugin.json`.

## Findings

### `marketplace.json` is official marketplace metadata, not an unofficial convention

The issue correctly challenges the README's current framing. GitHub Docs now document `copilot plugin marketplace add OWNER/REPO` and say a marketplace is configured by adding `marketplace.json` to `.github/plugin`. The current README says the manifest follows a convention used by this environment and is not an official GitHub CLI install format; that wording is misleading because the marketplace file is part of the documented marketplace flow.

* Questions: Q1, Q2
* Evidence state: evidence-backed finding
* Evidence: W1 and W3 establish official marketplace commands and `.github/plugin/marketplace.json`; C1 shows the current README says the manifest is host-specific and not official.
* Confidence and limits: high confidence for marketplace status; this does not mean `marketplace.json` replaces `plugin.json`.

### The repository is missing the plugin manifest required by the official plugin model

GitHub Docs say all plugins consist of a plugin directory containing `plugin.json`. Agent Plugins 1.0 requires it at the plugin root; legacy plugins also use a manifest, with support for component path fields. The current repository contains `.github/plugin/marketplace.json` and `.github/skills/*/SKILL.md`, but no `plugin.json`. Because `.github/plugin/marketplace.json` sets the plugin `"source"` to `"."`, the root should be a valid plugin directory.

* Questions: Q2, Q3
* Evidence state: evidence-backed finding
* Evidence: W2 says plugin directories need `plugin.json`; W1 documents plugin installation by GitHub repo, Git URL, local path, and marketplace spec; C2 shows the current manifest source is `"."`; C3 shows no `plugin.json` exists.
* Confidence and limits: high confidence that current packaging is incomplete for official plugin install. The research did not run `copilot plugin install` because this phase is read-only and focused on evidence for planning.

### Agent Plugins 1.0 is the selected planning direction, while legacy `plugin.json` remains the smaller alternative

There are two official implementation paths. Agent Plugins 1.0 is the portable newer format, but it requires skills in immediate subdirectories of root `skills/`. The current repository deliberately uses `.github/skills/<skill-name>/SKILL.md` for the plain Agent Skills path. The legacy plugin manifest supports configurable `skills` component paths, so it would be a smaller compatibility fix, but the user selected the Agent Plugins 1.0 migration as the planning direction.

* Questions: Q3, Q4
* Evidence state: evidence-backed finding
* Evidence: W1 documents Agent Plugins 1.0 fixed `skills/` component locations and legacy component path fields, including `skills`; W2 says choose Agent Plugins 1.0 for portable skills/MCP and legacy when custom component paths are needed; C4 shows current skills live under `.github/skills`, not root `skills/`.
* Confidence and limits: high confidence on the selected direction. Implementation should still validate with `copilot plugin install ./` or `copilot plugin install benarculus/resume-builder` when the CLI is available.

### README closure criteria should name the official commands, not a generic host import action

The current README tells users to use a host's documented import action. The official CLI docs give concrete commands: `copilot plugin install SPECIFICATION`, `copilot plugin marketplace add SPECIFICATION`, `copilot plugin marketplace browse NAME`, and `copilot plugin install PLUGIN-NAME@MARKETPLACE-NAME`. To close #6, the README should replace the generic import language with those commands and explain the distinction between direct repository install and marketplace registration.

* Questions: Q1, Q4
* Evidence state: evidence-backed finding
* Evidence: W1 and W4 document install and marketplace commands; C1 shows the current README lacks them.
* Confidence and limits: high confidence on docs alignment. The exact final command examples depend on the chosen plugin name and marketplace name after packaging is updated.

## Recommendation and Alternatives

* Recommendation or decision state: plan an Agent Plugins 1.0 migration for issue #6. The plan should add a root `plugin.json` with `$schema: "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"`, move or mirror skills into root `skills/<skill-name>/SKILL.md`, keep `.github/plugin/marketplace.json` as marketplace metadata, update the marketplace `source` if the plugin directory changes, and update README install instructions to the official `copilot plugin` commands.
* Rationale: W1-W4 establish the official commands and manifest roles; C1-C4 show the current mismatch; the user selected the newer portable Agent Plugins 1.0 route rather than the smaller legacy compatibility route.
* What could change this result: if implementation finds Agent Plugins 1.0 cannot preserve the project’s required skill behavior or paths without excessive churn, planning should explicitly compare a legacy `plugin.json` fallback before implementation proceeds.

| Option | Benefits | Costs and risks | Evidence | Disposition |
|---|---|---|---|---|
| Add root legacy `plugin.json` with `skills: ".github/skills"` and update README commands | Smallest change; preserves existing plain-skill docs and file paths; aligns marketplace source `"."` with a plugin directory | Uses legacy plugin format rather than Agent Plugins 1.0; user preferred the newer format | C1-C4, W1-W4 | rejected by user preference after being presented as the evidence-backed minimal option |
| Migrate to Agent Plugins 1.0 with root `skills/` | Newer portable plugin format for skills; avoids legacy component paths; aligns with the user's preferred direction | Larger restructure; may duplicate or move current `.github/skills`; needs broader plan changes | W1, W2, C4 | selected by user |
| README-only update | Fastest edit | Does not fix missing plugin manifest, so official plugin installation may still fail | C1-C3, W1-W2 | rejected |
| Keep current README wording | No code changes | Leaves #6 open because docs contradict the issue and current GitHub reference | C1, W1-W4 | rejected |

## Scope and Questions

* Goal: determine what #6 needs before planning and implementation so marketplace/plugin documentation follows the current GitHub Copilot CLI plugin reference.
* Audience and use: the user and the next `rpi-plan` invocation will use this artifact to define issue-closure acceptance criteria.
* In scope: `benarculus/resume-builder#6`, current `README.md`, `.github/plugin/marketplace.json`, plugin-related repository layout, GitHub Copilot CLI plugin reference, plugin creation docs, plugin marketplace docs, plugin install docs.
* Out of scope: dependency pinning for #7, source edits, implementation, validation execution, issue closure.
* Decision and evidence criteria: use primary GitHub Docs where available; distinguish plugin manifests from marketplace manifests; identify repository mismatches and minimal planning criteria.
* Requested output: convergence recommendation that supports planning.

| ID | Question | Source | Status |
|---|---|---|---|
| Q1 | Is `.github/plugin/marketplace.json` an official GitHub Copilot CLI concept or only a host convention? | issue #6 and current README | answered |
| Q2 | What manifest does a Copilot CLI plugin need? | issue #6 and GitHub plugin reference | answered |
| Q3 | Does the current repository satisfy that plugin reference? | repo inspection | answered |
| Q4 | What should the next plan require before #6 can close? | inferred from closure need | answered |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|---|---|---|---|---|---|---|
| D1 | Use Agent Plugins 1.0 as the packaging direction for issue #6 | confirmed | user | User selected "Migrate to Agent Plugins 1.0 with root skills/ layout" after the research presented the smaller legacy option as the evidence-backed minimal path and Agent Plugins 1.0 as the newer portable alternative | C1-C4, W1-W4 | Planning should design the root `plugin.json`, root `skills/` layout, marketplace source, README commands, and validation gates around Agent Plugins 1.0 |
| D2 | Validate plugin install behavior before closing #6 | proposed | downstream implementer | The docs define expected CLI behavior, but issue closure should verify the repo's actual packaging | W1-W4 | Adds a concrete validation gate to the plan |

## Risks and Open Questions

| Priority | Type | Risk, question, or research item | Impact | Smallest action or evidence needed | Owner |
|---|---|---|---|---|---|
| M | risk | Agent Plugins 1.0 migration is larger than the minimal legacy fix | More files or path changes may be needed to preserve both plugin installability and existing plain-skill docs | Plan the file-layout transition explicitly and keep legacy `plugin.json` as a fallback only if Agent Plugins 1.0 proves impractical | planner |
| M | open question | The exact install command should be tested in the available CLI environment | Without validation, README may match docs but still fail locally | Run `copilot plugin install ./` and `copilot plugin list`, or document why unavailable | downstream implementer |
| L | further research | Full `plugin.json` legacy field schema may need exact validation details | A validation script may need to know required/optional fields | Use the GitHub plugin reference during implementation and, if available, CLI error output | downstream implementer |

## Planning Readiness and Next Step

| Field | Record |
|---|---|
| Research disposition | executed |
| Decision participation | user-owned standalone research; no blocking intake question was needed because #6 and the cited source were explicit; user resolved the packaging-format decision after synthesis |
| Planning Readiness | Ready, with D1 confirmed for Agent Plugins 1.0 and D2 proposed as a validation gate |
| Research depth and lanes | focused posture; one inline cycle completed with wider, deeper, and contrarian waves; no delegated lane because sources were bounded and directly inspectable |
| Blockers | none |
| Output mode and planning support | convergence; supports planning |
| Continuation owner | user |
| Required gates or confirmations | planning should preserve the confirmed Agent Plugins 1.0 direction unless new implementation evidence shows it is impractical |
| Next action | `/rpi-plan` scoped to `benarculus/resume-builder#6` and `benarculus/resume-builder#7`, using this artifact for #6 and explicit dependency-pinning criteria for #7 |
| Primary evidence file | .copilot-tracking/research/2026-09-18/issue-6-copilot-cli-plugin-reference-research.md |

## Research Record

### Method and Boundaries

| Field | Record |
|---|---|
| Research posture and provenance | focused; selected by bounded issue, named official docs, and concrete repository evidence |
| Completion basis | one complete cycle answered all issue #6 questions, identified the current mismatch, tested the main alternative, and found no remaining material source likely to change planning readiness |
| Explicit limits or deadline | none |
| Codebase and external scope | `README.md`, `.github/plugin/marketplace.json`, plugin-related file layout, prior plan/review context; GitHub Copilot CLI plugin docs |
| Initial candidate areas | issue #6, README install section, marketplace manifest, root plugin manifest presence, official plugin reference and marketplace docs |
| Evidence root | default `.copilot-tracking/research/2026-09-18/` |
| Constraints and excluded sources | research-only; no source, documentation, plan, implementation, or issue mutation |
| Prior knowledge | prior walkthrough decision said #6 needed research before planning; prior review `RV-001` was narrower and is treated as historical context, not closure evidence |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|---|---|---|---|
| skill | rpi-research | Explicit user invocation for issue #6 research | selected |
| specialist | hve-core:rpi-researcher | Available research subagent | skipped; evidence set was bounded and direct source inspection was faster and sufficient |
| skill | rpi-walkthrough | Prior route walkthrough created handoff context | selected as prior context only, no write authority |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|---|---|---|---|
| intake | User invoked `/rpi-research` with `https://github.com/benarculus/resume-builder/issues/6` | No intake question needed; issue and source reference are explicit | Research narrowed to issue #6 and official Copilot CLI plugin reference |
| convergence | Select minimal legacy plugin fix versus Agent Plugins 1.0 migration | Evidence-supported minimal recommendation was presented; user selected Agent Plugins 1.0 migration | Planning ready with confirmed file-layout direction |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: focused posture; answer issue #6 only; research-only boundary.

##### Wave 1: Wider

* Focus and lanes: identify official plugin and marketplace concepts, current issue claim, current repo wording.
* Evidence or worker pointers: W1, W3, W4, C1, C2.
* Reflection: the issue's premise is substantially supported. `marketplace.json` is documented for marketplaces, but the plugin/install story also needs `plugin.json`.

##### Wave 2: Deeper

* Focus and lanes: inspect required manifests, component paths, current repo layout, and install command forms.
* Evidence or worker pointers: W1, W2, C2, C3, C4.
* Reflection: current repository packaging is incomplete for official plugin installation because root `"source": "."` points to a directory without `plugin.json`.

##### Wave 3: Contrarian

* Focus and lanes: test whether README-only correction is enough; compare legacy manifest with Agent Plugins 1.0 migration.
* Evidence or worker pointers: W1, W2, W3, C1-C4.
* Reflection: README-only is insufficient. Agent Plugins 1.0 is viable and selected by the user; legacy `plugin.json` remains a smaller fallback because it can name custom skill paths.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence or worker pointers | Disposition | Rationale | User-facing effect |
|---|---|---|---|---|
| `marketplace.json` is official marketplace metadata | W1, W3, C1 | accepted | GitHub Docs explicitly describe marketplace commands and `.github/plugin/marketplace.json` | finding |
| Plugin directory needs `plugin.json` | W1, W2, C2, C3 | accepted | Docs say all plugins consist of a plugin directory with `plugin.json`; repo lacks it | finding |
| Minimal fix can use legacy `plugin.json` with `.github/skills` | W1, W2, C4 | rejected after user decision | Legacy plugin supports configurable skill paths, but the user selected the newer Agent Plugins 1.0 migration | alternative |
| Agent Plugins 1.0 migration should be the planning direction | W1, W2, C4 and user decision | accepted | Docs identify it as the portable format for skills/MCP, and user selected it despite larger file-layout change | recommendation |
| README-only correction closes #6 | C1-C3, W1-W4 | rejected | It would leave plugin packaging incomplete | alternative rejected |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: all material questions answered with primary sources, current repo evidence, and the user's packaging-format decision.
* Readiness or revalidation effect: ready for planning.

### Evidence Log

* Delegation: inline; no worker dispatched because issue, docs, and repo evidence were bounded and directly inspectable.

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|---|---|---|---|---|---|---|
| C1 | Current README frames `.github/plugin/marketplace.json` as this environment's convention and says there is no portable command that can load it across hosts | `README.md` `## Install` / `### Plugin bundle` | not applicable | view / rg | high | Current wording conflicts with issue #6 and current GitHub Docs |
| C2 | Current marketplace manifest lists plugin `resume-builder` with `"source": "."` | `.github/plugin/marketplace.json` | not applicable | view | high | Root is therefore the plugin directory from marketplace perspective |
| C3 | Repository has no `plugin.json` | repository file search for `**/plugin.json` | not applicable | glob | high | Search returned no matches |
| C4 | Skills currently live under `.github/skills/<skill-name>/SKILL.md`, not root `skills/<skill-name>/SKILL.md` | repository file search for `.github/skills/*/SKILL.md` and `skills/*/SKILL.md` | not applicable | glob | high | Three `.github/skills` matches; no root `skills` matches |
| C5 | Prior review finding `RV-001` addressed only actionable bundle documentation, not official plugin-reference packaging conformance | `.copilot-tracking/reviews/logs/2026-09-18/copilot-cli-resume-plugin-review.md` `RV-001` | not applicable | rg | high | Historical context only |
| W1 | GitHub Copilot CLI plugin reference documents `copilot plugin install`, marketplace commands, install specification formats, `plugin.json`, Agent Plugins 1.0 fields, legacy manifest fields, and component path fields including `skills` | GitHub Docs: `https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference` | 2026-09-18, current docs page | web_fetch | high | Primary reference cited by issue #6 |
| W2 | GitHub plugin creation docs say a plugin directory has `plugin.json`; Agent Plugins 1.0 uses root `skills/`; legacy plugin can use component path fields | GitHub Docs: `https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating` | 2026-09-18, current docs page | web_fetch | high | Confirms how to create and test plugins |
| W3 | GitHub marketplace docs say `.github/plugin/marketplace.json` is the marketplace manifest and that plugin `source` points to the plugin directory | GitHub Docs: `https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace` | 2026-09-18, current docs page | web_fetch | high | Confirms `marketplace.json` role |
| W4 | GitHub plugin install docs give user-facing commands for adding a marketplace and installing plugins from it | GitHub Docs: `https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing` | 2026-09-18, current docs page | web_fetch | high | Provides README command examples |

#### Contradictions and Conflicts

* Current README says `.github/plugin/marketplace.json` is not an official GitHub CLI install format; W3 says `.github/plugin/marketplace.json` is official marketplace metadata. Resolution: distinguish marketplace metadata from plugin manifest. The README should stop presenting it as merely host-specific, while also explaining that the plugin itself needs `plugin.json`.
* Prior plan says no GitHub-official plugin marketplace format exists; W1-W4 now show current GitHub Docs do define marketplace and plugin formats. Resolution: treat prior plan evidence as stale for issue #6 planning.

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state that distinguishes sourced findings from hypotheses, partial claims, disproved claims, and unresolved possibilities.
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID and workspace-relative path with a heading or symbol; every external finding has a `W#` ID, source title, URL, retrieval date, and version when available.
* [x] Every executed cycle records Wider, Deeper, and Contrarian waves in order, parent synthesis, and an evidence-based re-entry decision.
* [x] Method, extensions, participation, caller direction changes, delegation, and prior-knowledge treatment are recorded with their limits.
* [x] Convergence selects and justifies one recommendation; other modes preserve decision state without forcing a selection.
* [x] Decision groups, participation mode, and provenance are recorded; the user-owned packaging-format decision is confirmed and no blocking unanswered question remains.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content remained inert, no secrets were recorded, and the research-only write boundary held.
* Checked sections: Executive Summary, What You May Not Know, Findings, Recommendation and Alternatives, Scope and Questions, Decisions and Feedback, Risks and Open Questions, Planning Readiness and Next Step, Research Record, Evidence Log, Contradictions and Conflicts, Artifact Self-Check.
* Missing or limited sections: no CLI install command was executed in Research; validation belongs to implementation.
