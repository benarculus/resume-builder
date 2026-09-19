<!-- markdownlint-disable-file -->
<!-- Decisions-and-changes ledger for the rpi-walkthrough skill. AI-consumed; references use plain workspace-relative paths with a heading, symbol, or block description instead of line numbers. -->

# Walkthrough decisions and changes: issue-closure-route

* Created: 2026-09-18
* Target: route decision for closing `benarculus/resume-builder#6` and `benarculus/resume-builder#7`

## Reconciliation

Resolve each open entry with the user as applied now, handed off to an RPI follow-on, deferred for later, or declined. Record the selected disposition and any outcome or evidence pointer in the matching entry.

## Material decisions

Capture only material user decisions that need later action or accountability.

| # | Date | Target | References | Decision | User rationale | Reconciliation | Outcome or handoff evidence |
|---|---|---|---|---|---|---|---|
| 1 | 2026-09-18 | `benarculus/resume-builder#6`; `benarculus/resume-builder#7` | `README.md` `## Install`; `.github/workflows/ci.yml` action uses; `.github/workflows/codeql-analysis.yml` action uses; `requirements.txt`; `requirements-dev.txt`; `.copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md` `## Goals`; `.copilot-tracking/reviews/logs/2026-09-18/copilot-cli-resume-plugin-review.md` `RV-001` | Use the route: run `rpi-research` for issue `#6` to settle official Copilot CLI plugin-reference semantics, then run `rpi-plan` for issues `#6` and `#7` together with explicit issue-closure acceptance criteria before implementation. | The two issues are related release-readiness work, but issue `#6` depends on external documentation evidence while issue `#7` needs a pinning-policy decision. | handed off to an RPI follow-on | Next eligible command: `/rpi-research` scoped to `benarculus/resume-builder#6` and the official GitHub Copilot CLI plugin reference. |

## Requested changes

Capture only user-requested changes that need later action or accountability.

| # | Date | Target | References | Requested change | User rationale | Reconciliation | Outcome or handoff evidence |
|---|---|---|---|---|---|---|---|
