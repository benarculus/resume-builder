<!-- markdownlint-disable-file -->
<!-- Decisions-and-changes ledger for the rpi-walkthrough skill. AI-consumed; references use plain workspace-relative paths with a heading, symbol, or block description instead of line numbers. -->

# Walkthrough decisions and changes: issue-6-7-planning-recovery

* Created: 2026-09-18
* Target: Blocked RPI planning sequence for GitHub issues #6 and #7

## Reconciliation

Resolve each open entry with the user as applied now, handed off to an RPI follow-on, deferred for later, or declined. Record the selected disposition and any outcome or evidence pointer in the matching entry.

## Material decisions

Capture only material user decisions that need later action or accountability.

| # | Date       | Target | References | Decision | User rationale | Reconciliation | Outcome or handoff evidence |
|---|------------|--------|------------|----------|----------------|----------------|-----------------------------|
| 1 | 2026-09-18 | #6/#7 RPI planning recovery | .copilot-tracking/plans/2026-09-18/issue-6-7-release-readiness-plan.md `## Planning Readiness and Next Step`; .copilot-tracking/reviews/plans/2026-09-18/issue-6-7-release-readiness-plan-critique.md `## Verdict`; .copilot-tracking/research/2026-09-18/issue-6-copilot-cli-plugin-reference-research.md `## Decisions and Feedback` | Rerun a clean `/rpi-plan` for issues #6 and #7 before implementation, carrying forward the settled Agent Plugins 1.0 and exact direct Python pinning decisions. | User selected the recommended path after walkthrough explained that the blocker is RPI critique provenance, not product implementation content. | handed off | Use this decision as input to the next `/rpi-plan https://github.com/benarculus/resume-builder/issues/7 https://github.com/benarculus/resume-builder/issues/6`; do not run `/rpi-implement` from the blocked plan artifacts. |

## Requested changes

Capture only user-requested changes that need later action or accountability.

| # | Date | Target | References | Requested change | User rationale | Reconciliation | Outcome or handoff evidence |
|---|------|--------|------------|------------------|----------------|----------------|-----------------------------|
