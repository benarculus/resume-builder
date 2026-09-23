## Summary

Adds an automated `release-please` pipeline so `resume-builder` tracks version updates semantically instead of by hand. On a push to `main`, once `ci.yml` ("Validate resume-builder") passes, release-please opens or updates a standing release PR that bumps the version based on Conventional Commit messages and keeps `plugin.json` and `.github/plugin/marketplace.json` in sync.

- `release-please-config.json` — `simple` release strategy, with `extra-files` updaters for `plugin.json` (`$.version`) and `.github/plugin/marketplace.json` (`$.metadata.version`, `$.plugins[0].version`)
- `version.txt` — release-please's own primary version file (separate from the JSON updaters, since `simple` always writes there), seeded at `0.1.0` to continue existing pre-1.0 numbering
- `.release-please-manifest.json` — tracks the current released version (`0.1.0`)
- `.github/workflows/release-please.yml` — triggers via `workflow_run`, chained after `ci.yml` ("Validate resume-builder") completes successfully on a push to `main`; pinned to `googleapis/release-please-action@v5.0.0` (commit-SHA pinned per repository convention)

Also enforces linear history on `main`, a prerequisite for release-please's commit-based version bumping to stay reliable: `required_linear_history` was folded into the repository's existing "Protect main" ruleset rather than adding a second ruleset, so `main` continues to be governed by one ruleset.

Includes the full research → plan → critique → implementation → review tracking record for this task under `.copilot-tracking/`.

## Validation

- [x] `python scripts/validate_repo.py` — passed (validates plugin/marketplace JSON and workflow SHA pins, among other checks)
- [ ] `pytest -q` — not run; this change touches only pipeline configuration and tracking docs, no Python source under test

## Anti-fabrication and privacy

- [x] No personal, confidential, or real resume data is included.
- [x] Any new skill behavior preserves source pointers and clarifying questions.
- [x] Unmet job requirements remain visible rather than being filled with invented claims.

## Checklist

- [ ] README or shared contracts updated when behavior changed.
- [ ] Tests added or updated for executable behavior.
- [x] Security-sensitive changes are called out in the description.
