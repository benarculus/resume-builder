<!-- markdownlint-disable-file -->
# Review: Dependabot hardening

## Executive Summary

* Assessment: The full-task implementation meets the Dependabot, pinning, Dependency Review, and most advisory-check contracts, but the advisory workflow supplies a token that the checker serializes as the literal invalid value `******`; any changed direct Python dependency consequently receives an authentication failure rather than a reliable advisory result.
* Why this matters: The malformed authorization causes false-blocking dependency pull requests and prevents the intended malware-advisory gate from operating against GitHub data.
* Builder execution: Complete
* Proposed review execution: Complete
* Proposed outcome: Defects found
* Validation coverage: Recorded structural validation, 16-test pytest suite, Ruby YAML parsing, advisory-checker no-change path, and `git diff --check` passed; this review did not execute validation.
* Confidence and limitations: High confidence in the two identified implementation/test gaps from direct source comparison. The review is bounded to repository artifacts and recorded validation; it cannot establish live GitHub branch-protection settings, Dependabot-generated PR behavior, or GitHub Advisory API availability.

The assessment above is the builder's proposal. Parent Decision Record contains the current final decision and next actions, or states that decisions are pending.

## What You May Not Know

The passing local validations do not exercise the workflow path that exports `GITHUB_TOKEN` and queries an advisory for a changed dependency. The existing token test asserts the literal masked value, so it cannot expose the malformed Authorization header.

## Findings and Proposed Routes

<!-- rpi:review id=RV-001 -->
### RV-001 [High]: Advisory checker sends an invalid Authorization value

The advisory-malware workflow always exports `GITHUB_TOKEN`, but `fetch_malware_advisories` replaces that token with the literal string `******` in the `Authorization` header. GitHub treats that header as invalid credentials, so a pull request with a changed direct Python dependency fails on an API authentication error instead of receiving the intended malware-advisory evaluation.

* Related scope: FR-005; NFR-001; P02-T02; P03-T02; D3; PC-001
* Expected behavior: The checker queries GitHub Advisory Database malware records for each changed direct Python package and fails only for a match or explicit request/response failure, using supported authentication when a workflow token is supplied.
* Observed behavior and evidence: `.github/workflows/advisory-malware.yml` exports `GITHUB_TOKEN`; `scripts/check_malware_advisories.py` sets `headers["Authorization"] = f"******"` rather than a valid token scheme/value. `tests/test_check_malware_advisories.py` asserts that same literal header.
* Impact: Every relevant workflow run is likely fail-closed for the wrong reason, blocking safe dependency updates and providing no reliable match result.
* Resolution condition: A changed-dependency workflow request carries either valid supported GitHub authentication derived from the provided token or intentionally omits the header for unauthenticated access; fixture tests assert the valid request shape and successful no-match behavior without exposing a token.
* Proposed destination: rpi-implement
* Smallest useful next action: Correct the Authorization-header construction and update the focused request test to assert the supported authentication scheme without asserting a secret.

<!-- rpi:review id=RV-002 -->
### RV-002 [Medium]: No regression test covers a changed dependency with no advisory match

The matcher has tests for changed-pin discovery, malformed data, request failure, and a simulated match, but no test drives `main()` through a changed dependency whose advisory query returns an empty result. The recorded advisory-checker no-change validation covers only the early return with no changed dependencies.

* Related scope: FR-006; NFR-001; P03-T02; D3
* Expected behavior: Fixture-based tests demonstrate the checker exits `0` when a changed direct Python dependency has no known malware advisory, without live network access.
* Observed behavior and evidence: `tests/test_check_malware_advisories.py` has no test that combines a nonempty `changed_dependencies` result, an empty advisory response, and `main() == 0`; `.copilot-tracking/changes/2026-09-19/dependabot-hardening-changes.md` records only an advisory-checker no-change path.
* Impact: The safe changed-dependency path required by P03-T02 can regress without focused detection, reducing confidence in the gate's normal allow behavior.
* Resolution condition: A deterministic fixture/mocked test executes `main()` with at least one changed direct pin and no returned malware advisories, then asserts exit `0` and the bounded no-match message.
* Proposed destination: rpi-implement
* Smallest useful next action: Add one focused no-match `main()` test adjacent to the current match test.

## Parent Decision Record

### Current Disposition

* Based on events: RD-001 through RD-008
* Review execution: Complete
* Final outcome: Defects found. The review completed its full evidence boundary, and two accepted implementation defects remain to be remediated.
* Finding decisions and next actions: RV-001 and RV-002 are accepted for `rpi-implement`; correct the advisory Authorization header and add the changed-dependency no-match regression test.
* Decisions still needed: none.

This summary is derived from Decision History, not a second decision record. The latest event for each subject governs; refresh this summary after appending decisions and on recovery.

### Decision History

| Event | Subject | Decision source | Status or value | Proposed destination | Final destination | Owner | More information needed | Smallest next action | Rationale |
|-------|---------|-----------------|-----------------|----------------------|-------------------|-------|-------------------------|----------------------|-----------|
| RD-001 | participation | system | user-owned | none | none | user | none | Present each actionable finding after builder completion | Standalone manual RPI Review retains route decisions for the user. |
| RD-002 | RV-001 | system | pending walkthrough | rpi-implement | pending | user | none | Decide whether to route the authentication defect to implementation | The high-severity finding requires a user-owned route decision before final outcome. |
| RD-003 | RV-001 | user | accepted | rpi-implement | rpi-implement | implementation owner | none | Correct the Authorization header and test supported authentication | User accepted the evidence-backed remediation route. |
| RD-004 | RV-002 | system | pending walkthrough | rpi-implement | pending | user | none | Decide whether to route the no-match regression gap to implementation | The remaining medium-severity finding requires a user-owned route decision. |
| RD-005 | RV-002 | user | accepted | rpi-implement | rpi-implement | implementation owner | none | Add a changed-dependency no-match `main()` regression test | User accepted the evidence-backed remediation route. |
| RD-006 | walkthrough | system | complete | none | none | user | none | Close the user-owned finding walkthrough | Both actionable findings received explicit route decisions. |
| RD-007 | review execution | parent | Complete | none | none | parent | none | Publish the completed review record | The selected builder completed the full standard-depth evidence comparison. |
| RD-008 | outcome | parent | Defects found | rpi-implement | rpi-implement | implementation owner | none | Implement accepted RV-001 and RV-002 remediation | Two accepted implementation defects prevent a conformant outcome until corrected. |

## Validation Evidence

| Command | Scope | Status | Summary |
|---------|-------|--------|---------|
| `python3 scripts/validate_repo.py` | Structural policy, pins, and gate configuration | Passed (recorded) | Changes record reports Dependabot, workflow, pin, and repository-contract validation passed. |
| `python3 -m pytest -q` | Full Python suite | Passed (recorded) | Changes record reports 16 tests passed. |
| Ruby `YAML.load_file` | Dependabot and added workflow YAML | Passed (recorded) | Changes record reports all three YAML files parsed. |
| Advisory checker no-change path | Checker early-return behavior | Passed (recorded) | Does not cover a changed dependency querying the workflow's token-bearing API path. |
| `git diff --check` | Full change set | Passed (recorded) | Changes record reports no whitespace errors. |

## Risks, Blockers, and Residual Work

* Blockers: None for the evidence comparison. RV-001 prevents accepting the malware gate as functioning for changed dependency pull requests.
* Remaining active work: No active plan markers remain; remediation for RV-001 and RV-002 is proposed follow-on implementation work.
* Residual work: Branch-protection required-check enablement remains explicitly outside scope and user-approval-gated; it is not an implementation defect or active plan item.

## Review Record

### Scope and Evidence

* Task ID: dependabot-hardening
* Review date: 2026-09-19
* Review scope: full task
* Assessed boundary: All P01–P03 acceptance requirements, confirmed decisions D1–D4, critique dispositions PC-001 and PC-002, implementation evidence, validation, blockers, remaining work, and follow-up items.
* Review depth and provenance: standard; default.
* Review worker: hve-core:rpi-review-builder; selected because it builds the canonical RPI review record from bounded planning and implementation evidence.
* Builder candidate identity: `dependabot-hardening/full-task/0cfb6b859020b554adecf86a926cc55e9cb1c43545f73333e175a529fcbfe4d5/72a19280d2402a132989ec78c8b0ef8a1d4438d26e7e46c57e2ccc3af8bf9e94`
* Builder execution: Complete
* Plan: .copilot-tracking/plans/2026-09-19/dependabot-hardening-plan.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-19/dependabot-hardening-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-19/dependabot-hardening-changes.md
* Other evidence considered: .copilot-tracking/research/2026-09-19/dependabot-hardening-research.md; current source, workflows, checker, and tests named by the implementation record.

### Opening Review State

* Interpreted review goal: Compare the completed dependency-hardening implementation with the approved plan and evidence, then provide a human-readable assessment and proposed routes for any substantive gaps.
* Review scope: full task.
* Evidence readiness: Plan, critique, changes record, research, source changes, and recorded validation are available; all P01–P03 markers are checked.
* Acceptance basis: FR-001 through FR-006, NFR-001 through NFR-004, confirmed decisions D1–D4, and critique dispositions PC-001 and PC-002.
* First comparison boundary: Repository content and recorded test/validator results only; no live GitHub branch-protection state, Dependabot execution, or live advisory query is in scope.
* Active read-only boundaries: The selected worker may edit this review record except `## Parent Decision Record`; it may not edit source, plan, critique, research, changes record, or parent state.
* Authority split: builder owns review evidence and proposed routes; parent owns final outcome, route dispositions, and continuation.
* Initial blockers: None.

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|----------------------|----------------------------------------|------------|----------------------|
| FR-001, D1, P01 / P01-T01 | `.github/dependabot.yml` defines separate `pip` and `github-actions` version/security groups; recorded validator and YAML parsing passed. | Met | Per-ecosystem groups are distinct and all-dependency patterns remain inside each ecosystem. |
| FR-002, D2, P01 / P01-T01 | `.github/dependabot.yml` defines pip default/patch/minor 14 days and major 30 days; security groups are distinct; validator passed. | Met | The committed cooldown matches the approved policy and does not configure a security cooldown. |
| FR-003, P01-T01 / P03-T01 | `scripts/validate_repo.py` validates exact direct pins and all workflow SHA pins; requirements and workflows retain required forms; recorded tests passed. | Met | Full-SHA action and exact `==` direct-Python pin invariants remain enforced. |
| FR-004, D4, P02 / P02-T01 / P03-T01 | `.github/workflows/dependency-review.yml` uses `pull_request`, `contents: read`, SHA-pinned action, low severity, and runtime/development/unknown scopes; validator and tests passed. | Met | No warning-only, allowlist, write permission, or `pull_request_target` weakening is present. |
| FR-005, D3, P02 / P02-T02 | Advisory workflow, checker, and fixtures implement direct-pin diffing, malware query construction, match messaging, and nonzero error handling. | Gap | RV-001: the token-bearing request uses a literal invalid Authorization value. |
| FR-006, P03 / P03-T01 / P03-T02 | Validator covers Dependabot and workflow policy; structural weakening tests, matcher fixtures, and recorded 16-test suite passed. | Gap | RV-002: no changed-dependency/no-advisory `main()` regression case. |
| NFR-001 | Checker fixture tests use mocks; no recorded live advisory test; validator is committed-content only. | Met | Deterministic test design is maintained; RV-002 is coverage, not a live-network defect. |
| NFR-002 | Both new workflows use `pull_request` and read-scoped permissions; validator checks prohibited weakening. | Met | Least-privilege event and permissions contract is present. |
| NFR-003 | Recorded `python3` validation and pytest passed; CI uses setup-python then `python`/`pytest`. | Met | Setup-python makes the CI interpreter path available; no parity gap is evidenced in supplied artifacts. |
| NFR-004 | Checker match output uses the required exact fragment and says results are not a comprehensive malware verdict. | Met | PC-001's human-facing output boundary is implemented and fixture-asserted. |
| PC-001 disposition | Plan requires named checker/workflow, exact output fragment, package, advisory ID, and exit behavior; implementation supplies each. | Met | Resolved as planned; RV-001 concerns request authentication, not the output contract. |
| PC-002 disposition | Plan and changes record distinguish workflow validation from branch-protection enforcement. | Met | Branch protection remains a separate approval-gated repository-setting action. |
| Implementation-time updates, blockers, remaining work, follow-ups | Changes record reports no plan updates, blockers, remaining work, or follow-ups. | Met | Reconciled with the plan's empty follow-up list; RV findings are review-proposed remediation, not a retroactive active marker. |

### Critique and Follow-Up Assessment

* Latest critique dispositions: PC-001 and PC-002 are both resolved by the approved plan and evidenced in the implementation record.
* Material revisions: None were recorded during implementation; the current changes record is consistent with the plan's tasks and confirmed D1–D4 decisions.
* Dependent-work pause assessment: P02 and P03 completion evidence is consistent with their declared dependencies; no early-resumption evidence appears.
* Justification assessment: The code-level validation / branch-protection separation is preserved. Advisory coverage remains intentionally limited to known GitHub Advisory Database records.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|----------------|-----------------------------|----------------------|----------------------|
| Required branch-protection enablement | Repository-setting enforcement was expressly excluded and requires explicit user approval. | User-approved repository-settings action, if later selected. | Distinct residual work; no active route proposed by this review. |

### Builder Self-Check

* [x] Every supplied requirement, acceptance criterion, in-scope marker, material update, critique disposition, validation result, blocker, remaining item, and plan follow-up has an assessment or explicit gap.
* [x] Findings are substantive, evidence-grounded, severity-graded, and use stable `RV-xxx` IDs with expected and observed behavior, a resolution condition, and one proposed route each.
* [x] Execution status, proposed outcome, validation coverage, limitations, and proposed routes are complete and internally consistent.
* [x] The summary is scoped and advisory, findings keep their supporting context together, and acceptance coverage distinguishes demonstrated gaps from unassessed behavior.
* [x] Standard review completely assessed the material boundary while omitting restatement, cosmetic feedback, exhaustive strengths, low-impact suggestions, and continual narration.
* [x] The selected review worker did not edit Parent Decision Record, ask the user, mutate source or parent state, dispatch another worker, execute validation, or invoke a destination.
* Checked boundary: FR-001–FR-006, NFR-001–NFR-004, P01–P03 and task markers, D1–D4, PC-001/PC-002, current implementation files, changes reconciliation, recorded validation, blockers, remaining work, and follow-ups.
* Missing or limited evidence: No live Dependabot-generated PR, GitHub Advisory API execution, or GitHub branch-protection state was supplied; recorded validation was assessed but not rerun.
