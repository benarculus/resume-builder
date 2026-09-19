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
* Status basis: The original full-plan tasks remain complete; RV-001's unauthenticated advisory request path and RV-002's missing deterministic allow-path test were verified.

## Execution Summary

Implemented the approved Dependabot policy, added known-vulnerability and known-malware-advisory pull-request gates, and expanded deterministic validation and fixture coverage. Accepted RV-001 and RV-002 remediation is complete: the checker makes unauthenticated public advisory requests, and focused coverage includes its changed-dependency allow path. Passing workflow definitions are code-level evidence only; enabling GitHub branch protection to require them remains a separate user-approved repository-setting action.

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
* What changed and why: Removed the workflow token injection and checker Authorization handling so the trusted checker extracted from the pull request base revision (or immutable bootstrap fallback) can only make unauthenticated public advisory requests; added the missing deterministic changed-dependency/no-advisory `main()` test.
* Completion evidence: The request test asserts no Authorization header and the new fixture verifies exit `0` plus the bounded no-match message for a changed direct pin.
* Validation: `python3 -m pytest -q tests/test_check_malware_advisories.py tests/test_structure.py` passed with 39 tests; the full suite passed with 41 tests after the final include-handling, advisory-pagination, and shell-policy regressions were added.

### Final review remediation

* Related phase or task: RV-003
* Files:
  * [scripts/check_malware_advisories.py](../../../scripts/check_malware_advisories.py)
  * [scripts/validate_repo.py](../../../scripts/validate_repo.py)
  * [tests/test_check_malware_advisories.py](../../../tests/test_check_malware_advisories.py)
  * [tests/test_structure.py](../../../tests/test_structure.py)
* What changed and why: `default_request` now wraps the whole `urlopen` call so a connection-phase timeout is translated to `RuntimeError` (explicit error status `2`) instead of escaping as `TimeoutError`; Dependabot group validation now compares the complete group mapping per ecosystem so an extra unapproved group can no longer slip in alongside the approved version/security groups; the `.yaml` workflow-discovery regression now loads a copied validator module against a temporary repository tree so the module-level glob patterns are actually exercised.
* Completion evidence: New `test_default_request_raises_for_connect_timeout` covers the connect-phase timeout path; `test_dependabot_policy_rejects_extra_dependency_group` covers an injected extra group; `test_workflow_discovery_includes_yaml_extension` now fails if `.yaml` discovery regresses to only `*.yml`.
* Validation: `python3 -m pytest -q tests/test_check_malware_advisories.py tests/test_structure.py` passed with 41 tests; `python3 -m pytest -q` passed with 43 tests; `python3 scripts/validate_repo.py` passed.

## Implementation-Time Plan Updates

* None.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|-------|-------|--------|--------------------|
| `python3 scripts/validate_repo.py` | Repository structural policy | Passed | Validated skill packaging, all workflow SHA pins, Dependabot policy, dependency-gate workflows, exact direct pins, and job-requirements contract. |
| `python3 -m pytest -q tests/test_check_malware_advisories.py tests/test_structure.py` | Accepted review remediation | Passed | 41 focused checker and workflow-policy tests passed, including unauthenticated requests, rejected unexpected includes, paginated advisory retrieval, connect-timeout classification, exact group-policy matching, and shell-policy enforcement. |
| `python3 -m pytest -q` | Full Python test suite | Passed | 43 tests passed. |
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
