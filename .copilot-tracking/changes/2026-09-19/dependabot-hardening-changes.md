<!-- markdownlint-disable-file -->
# RPI Changes: Dependabot hardening

## Metadata

* Task ID: dependabot-hardening
* Related plan: [.copilot-tracking/plans/2026-09-19/dependabot-hardening-plan.md](../../plans/2026-09-19/dependabot-hardening-plan.md)
* Implementation date: 2026-09-19

## Execution Status

* Status: Complete
* Declared invocation scope: accepted review findings RV-001 and RV-002
* Completed scope markers: P01, P01-T01, P02, P02-T01, P02-T02, P03, P03-T01, P03-T02
* All remaining active-plan markers: none
* Status basis: The original full-plan tasks remain complete; RV-001's authentication path was verified against the current checker and RV-002's missing deterministic allow-path test was added and passed.

## Execution Summary

Implemented the approved Dependabot policy, added known-vulnerability and known-malware-advisory pull-request gates, and expanded deterministic validation and fixture coverage. Accepted RV-001 and RV-002 remediation is complete: the current checker derives a supported bearer header from `GITHUB_TOKEN`, and focused coverage includes its changed-dependency allow path. Passing workflow definitions are code-level evidence only; enabling GitHub branch protection to require them remains a separate user-approved repository-setting action.

## Completed Work

### Dependabot grouping and release-age policy

* Related phase or task: P01-T01
* Files:
  * [.github/dependabot.yml](../../../.github/dependabot.yml)
* What changed and why: Added separate version and security groups for `pip` and `github-actions`; set the approved 14-day default/patch/minor and 30-day major pip cooldown while preserving weekly checks, labels, and the default target branch.
* Completion evidence: The configuration now encodes the confirmed per-ecosystem grouping and release-age policy without a `target-branch`.
* Validation: Passed `python3 scripts/validate_repo.py` and Ruby YAML parsing.

### Known-vulnerability Dependency Review gate

* Related phase or task: P02-T01
* Files:
  * [.github/workflows/dependency-review.yml](../../../.github/workflows/dependency-review.yml)
* What changed and why: Added a least-privilege `pull_request` workflow using a full-SHA `actions/dependency-review-action` v5 pin. It blocks `low` and higher known vulnerabilities across `runtime`, `development`, and `unknown` scopes.
* Completion evidence: Workflow configuration uses `contents: read`, avoids `pull_request_target`, and has no warning-only or allowlist override.
* Validation: Passed `python3 scripts/validate_repo.py` and Ruby YAML parsing.

### Fail-closed malware-advisory gate

* Related phase or task: P02-T02
* Files:
  * [.github/workflows/advisory-malware.yml](../../../.github/workflows/advisory-malware.yml)
  * [scripts/check_malware_advisories.py](../../../scripts/check_malware_advisories.py)
* What changed and why: Added a least-privilege pull-request workflow and checker that compares base/head direct Python pins, queries GitHub Advisory Database malware advisories per changed package, and exits `1` on a match. Matches include the exact `GitHub Advisory Database malware advisory match` fragment, package, and GHSA ID; request/response failures exit nonzero rather than passing.
* Completion evidence: The checker uses only the GitHub advisory API, sends package/ecosystem query data, and says that results are known-advisory evidence rather than a comprehensive malware verdict.
* Validation: Passed fixture-based tests without live advisory requests.

### Deterministic policy and matcher coverage

* Related phase or task: P03-T01, P03-T02
* Files:
  * [scripts/validate_repo.py](../../../scripts/validate_repo.py)
  * [tests/test_structure.py](../../../tests/test_structure.py)
  * [tests/test_check_malware_advisories.py](../../../tests/test_check_malware_advisories.py)
* What changed and why: Extended structural validation to cover all workflow action SHA pins, approved Dependabot group/cooldown policy, default-branch targeting, and dependency-gate events/permissions. Added positive and weakening-rejection structural tests plus fixture-based malware-check tests for changed direct pins, package-scoped query construction, package matching, malformed responses, match output/exit code, and request failure.
* Completion evidence: Policy tests have no network dependency, while the checker treats advisory API errors as explicit failures.
* Validation: `python3 scripts/validate_repo.py` passed; `python3 -m pytest -q` passed with 17 tests.

### Accepted review-finding remediation

* Related phase or task: RV-001, RV-002
* Files:
  * [scripts/check_malware_advisories.py](../../../scripts/check_malware_advisories.py)
  * [tests/test_check_malware_advisories.py](../../../tests/test_check_malware_advisories.py)
* What changed and why: Verified that the current checker uses a `Bearer` Authorization header derived from `GITHUB_TOKEN` rather than a masked placeholder, and added the missing deterministic changed-dependency/no-advisory `main()` test.
* Completion evidence: The token request test passes with a test token and the new fixture verifies exit `0` plus the bounded no-match message for a changed direct pin.
* Validation: `python3 -m pytest -q tests/test_check_malware_advisories.py` passed with 8 tests; the full suite passed with 17 tests.

## Implementation-Time Plan Updates

* None.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|-------|-------|--------|--------------------|
| `python3 scripts/validate_repo.py` | Repository structural policy | Passed | Validated skill packaging, all workflow SHA pins, Dependabot policy, dependency-gate workflows, exact direct pins, and job-requirements contract. |
| `python3 -m pytest -q tests/test_check_malware_advisories.py` | Accepted review remediation | Passed | 8 focused checker tests passed, including token-bearing requests and a changed-dependency no-match path. |
| `python3 -m pytest -q` | Full Python test suite | Passed | 17 tests passed. |
| Ruby `YAML.load_file` | Dependabot and new workflow YAML | Passed | Parsed `.github/dependabot.yml`, `.github/workflows/dependency-review.yml`, and `.github/workflows/advisory-malware.yml`. |
| `git diff --check` | Full change set | Passed | No whitespace errors. |

## Pre-Review Reconciliation

* Plan markers and task-local context: Current; all full-plan P01–P03 markers remain checked. RV-001 and RV-002 were accepted follow-on implementation inputs, not new plan markers.
* Completed-work evidence and handoff prose: Current; RV-001 authentication behavior and RV-002 coverage are recorded above.
* Validation, blockers, remaining work, and follow-up items: Current; focused and full validation passed, with no blocker or follow-up item.
* Review readiness: The accepted findings are remediated and validated. The completed review record remains historical evidence; no additional review is required for this follow-on implementation.

## Blockers

* None.

## Remaining Work

* None.

## Follow-Up Items

* Canonical plan list: [.copilot-tracking/plans/2026-09-19/dependabot-hardening-plan.md](../../plans/2026-09-19/dependabot-hardening-plan.md), `## Follow-Up Items`
* None.

## Return-to-Caller State

* Implementation execution status: Complete.
* Declared scope and markers: Accepted review findings RV-001 and RV-002 are complete; full-plan P01–P03 markers remain complete and no active plan markers remain.
* Validation coverage: Focused checker tests, structural validation, full test suite, no-change checker behavior, and `git diff --check` passed.
* Blockers: None.
* Current plan updates: None; accepted review findings were implemented without changing approved plan scope.
* Planning and critique state: Ready for implementation; standard critique passed with PC-001 and PC-002 resolved.
* Follow-up items: None.
* Review readiness or no-handoff reason: Follow-on implementation is complete; the existing review record remains the completed review evidence and no rerun is required. Passing workflows do not imply branch-protection settings have been enabled.
* Continuation owner: user.
