## Summary

Adds an automated `release-please` pipeline so `resume-builder` tracks version updates semantically instead of by hand. On a push to `main`, release-please opens or updates a standing Release PR that bumps the version from Conventional Commit history and keeps `plugin.json` and `.github/plugin/marketplace.json` in sync.

- `release-please-config.json` — `simple` release strategy, with `extra-files` updaters for `plugin.json` (`$.version`) and `.github/plugin/marketplace.json` (`$.metadata.version`, `$.plugins[0].version`)
- `version.txt` — release-please's own primary version file (separate from the JSON updaters, since `simple` always writes there), seeded at `0.1.0` to continue existing pre-1.0 numbering
- `.release-please-manifest.json` — tracks the current released version (`0.1.0`)
- `.github/workflows/release-please.yml` — triggers on pushes to `main`, mints a one-hour installation token from `RELEASE_PLEASE_APP_CLIENT_ID` and `RELEASE_PLEASE_APP_PRIVATE_KEY`, explicitly scopes it to this repository and only Contents/Pull requests/Issues write access, disables the workflow's default `GITHUB_TOKEN` permissions, and SHA-pins both token creation and release-please actions
- `.github/workflows/publish-release.yml` — reacts to the App-created version tag, resolves release-please's draft in a small write-capable job, generates and validates an SPDX 2.3 SBOM in a separate read-only job, transfers only the validated SBOM into the publication job, checksum-verifies the uploaded asset, and publishes the immutable release
- `.github/workflows/scorecard.yml` — runs OpenSSF Scorecard on main, branch-rule changes, and a weekly schedule; publishes OIDC-authenticated results, stores short-lived SARIF evidence, and uploads findings to code scanning using SHA-pinned actions

Also enforces linear history on `main`, a prerequisite for release-please's commit-based version bumping to stay reliable: `required_linear_history` was folded into the repository's existing "Protect main" ruleset rather than adding a separate linear-history ruleset. `main` is still governed by two rulesets overall ("Protect main" and "Require advisory malware check"), which this change leaves intact.

The existing "Protect main" ruleset now requires the GitHub Actions `validate` check from `ci.yml`, a fresh approving code-owner review, approval from someone other than the last pusher, resolved review threads, and an up-to-date branch. It has no bypass actors. The GitHub App therefore cannot merge or push around CI or human review; its generated Release PR must pass the same gates as other PRs. Release-please creates a draft release and its version tag; active tag ruleset `24008744` restricts creation, update, and deletion of `v*` tags to the release GitHub App. The tag workflow adds `resume-builder.spdx.json` before publishing. Immutable releases then lock the tag and assets and generate GitHub's cryptographic release attestation.

Includes the full research → plan → critique → implementation → review tracking record for this task under `.copilot-tracking/`.

## Validation

- [x] `python scripts/validate_repo.py` — passed (includes hardened GitHub App token, SPDX publication, Scorecard, and workflow SHA-pin contracts)
- [x] Real SPDX generation with checksummed Syft `v1.52.0` — passed; source metadata, exact runtime pins, suppliers, unique identifiers, and relationships validated
- [x] `python3 -m pytest -q` — 111 passed, 8 skipped using the local Python 3.9 environment; hosted CI remains authoritative for the repository-pinned Python 3.12 dependency set

## Anti-fabrication and privacy

- [x] No personal, confidential, or real resume data is included.
- [x] Any new skill behavior preserves source pointers and clarifying questions.
- [x] Unmet job requirements remain visible rather than being filled with invented claims.

## Checklist

- [x] README or shared contracts updated when behavior changed.
- [x] Tests added or updated for executable behavior.
- [x] Security-sensitive changes are called out in the description.
