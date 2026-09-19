<!-- markdownlint-disable-file -->
# RPI Plan Critique: dependabot-hardening

## Metadata

* Task ID: dependabot-hardening
* Critique date: 2026-09-19
* Plan: .copilot-tracking/plans/2026-09-19/dependabot-hardening-plan.md
* Critique execution status: Complete
* Critique depth: standard
* Depth provenance: default
* Invocation consumed: yes
* Attempt ID and kind: 2026-09-19-dependabot-hardening-standard-initial (initial)
* Candidate identity and saved hash boundary: SHA-256 db8f175f66d5332459809b00fe312cb76bd0c5e9b8ca241816e1cdc84aa36469; reservation metadata is non-candidate context and ignored.
* Current-dispatch provenance: uninterrupted parent reservation-to-dispatch sequence.
* Original attempt and recovery approval: not applicable

## Inputs and Criterion Boundary

* Task context and caller requirements: Confirmed user direction: per-ecosystem Dependabot groups; 14-day pip patch/minor and 30-day major cooldown; retain full Actions SHA pins and direct Python == pins; fail PR on GitHub Advisory Database malware match; block any known vulnerability in runtime/development/unknown scopes; no production/configuration changes in this planning phase.
* Research and evidence considered: .copilot-tracking/research/2026-09-19/dependabot-hardening-research.md; .github/dependabot.yml; .github/workflows/ci.yml; .github/workflows/codeql-analysis.yml; requirements.txt; requirements-dev.txt; scripts/validate_repo.py; tests/test_structure.py; tests/test_build_docx.py; planning reference at .copilot/installed-plugins/hve-core/hve-core/.github/skills/rpi/rpi-plan/references/planning.md.
* Decisions, dependencies, task Goals, and task Requirements considered: independent per-ecosystem grouping, pip cooldown policy, immutable SHA and == pin retention, advisory malware match failure, dependency review across all scopes, and validation without product change or live network calls.
* Assessment boundary: This critique can judge plan completeness, task coverage, and evidence sufficiency against the supplied boundary; it cannot validate GitHub branch protection state or live advisory data, and it does not evaluate the implementation beyond the plan's own evidence.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| FR-001 | Covered | P01-T01 explicitly defines per-ecosystem group separation and user-confirmed grouping behavior. |
| FR-002 | Covered | P01-T01 and User Decisions D2 fix the pip cooldown values and exempt security updates. |
| FR-003 | Covered | P01-T01, P02-T01, P03-T01 all preserve exact SHA and == pin semantics and validate them structurally. |
| FR-004 | Covered | P02-T01 requires dependency review on runtime/development/unknown scopes with low-severity fail behavior. |
| FR-005 | Covered | P02-T02 and P03-T02 define the fail-closed GitHub Advisory Database malware matcher and its tests. |
| FR-006 | Covered | P03-T01 and P03-T02 require deterministic policy and gate regression tests without live network usage. |
| NFR-001 | Covered | P03-T02 explicitly excludes live advisory calls and expects fixture/mock coverage for API behavior and malformed responses. |
| NFR-002 | Covered | P02-T01 and P03-T01 require least-privilege read permissions and `pull_request` events only. |
| NFR-003 | Covered | P03-T02 records the functional validation commands and interpreter consistency requirement. |
| NFR-004 | Covered | P02-T02 and P03-T02 require malware results to be described as advisory matches rather than comprehensive malware verdicts. |
| P01-T01 | Covered | Configuration task is specific about ecosystem grouping, cooldown values, scheduling, and avoiding `target-branch`. |
| P02-T01 | Covered | Dependency Review workflow is scoped to `pull_request`, minimal permissions, fail on low severity, and all scopes. |
| P02-T02 | Covered | The malware matcher plan is bounded to direct dependency changes, advisory-based matching, fail-closed behavior, and precise failure semantics. |
| P03-T01 | Covered | Structural validation and policy checks are concrete and anchored to `.github/dependabot.yml` and existing validator/tests. |
| P03-T02 | Covered | The plan specifies regression tests and status-check evidence, including mock fixtures rather than live requests. |

## Verdict

* Verdict: Pass
* Rationale: The plan is materially complete against the confirmed user direction, tightly scoped to the supplied repository and research, and it specifies deterministic validation and failure semantics without proposing any production change in the planning phase. The remaining points are implementation-detail refinements rather than plan-blocking defects.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [Medium]: Clarify the malware-check file contract and output wording before implementation

* Related IDs: FR-005; NFR-004; P02-T02; P03-T02
* Evidence: .copilot-tracking/plans/2026-09-19/dependabot-hardening-plan.md, sections P02-T02 and P03-T02; .copilot-tracking/research/2026-09-19/dependabot-hardening-research.md, “Dependency Review is the GitHub-native vulnerability gate; advisory malware data needs an explicit, bounded integration”
* Concern: The plan states the expected behavior well, but it still leaves the exact implementation contract somewhat loose: the file path, script name, and exact output wording for a GitHub Advisory Database malware match are not fixed in advance. That creates avoidable ambiguity during implementation and weakens the specific “known advisory match, not a general malware verdict” guarantee.
* Impact: Without a stable file contract and output expectation, different implementers could create equivalent logic with inconsistent logging, misleading failure messages, or mismatched test assertions. That reduces the confidence that the workflow is reliably fail-closed and auditable.
* Smallest useful change: In the implementation plan or execution notes, name the repository-owned checker file (for example, a dedicated script under `scripts/`), define its exit-code behavior, and state the exact expected human-facing message fragment, such as “GitHub Advisory Database malware advisory match” alongside the package name and advisory identifier. Then assert that in the unit tests.
* Action owner: implementer
* Exact resolving evidence: A committed implementation artifact (script + tests) states the exact output contract and the tests assert the message and exit code. The acceptance condition should prove both “match detected” and “advisory-based evidence only” in the same fixture-driven test.
* Decision route: direct_planner_correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [Low]: Separate code-validation from any future branch-protection enablement

* Related IDs: NFR-002; P02-T01; P02-T02; P03-T02; Non-Goals section
* Evidence: .copilot-tracking/plans/2026-09-19/dependabot-hardening-plan.md, sections P03-T02 and “Non-Goals”; .github/workflows/ci.yml
* Concern: The plan correctly says branch protection settings are outside scope and should not be enabled without approval, but it still uses phrasing like “required-check suite” and “final changes record must capture passing results” without clearly separating workflow existence/pass results from actual repository setting enforcement. The distinction matters because passing status checks in a PR are not equivalent to a currently enforced required check in GitHub.
* Impact: A future implementation could be misread as if the repository settings are already enforcing the new gates, even though the plan explicitly forbids changing those settings during planning. That is a communication risk, not a technical execution issue.
* Smallest useful change: Add one sentence in the plan that states: “Passing workflow runs are a code-level validation result; any GitHub repository setting that marks them as required branch protection remains a separate, explicit approval step and is not assumed to exist in this phase.”
* Action owner: user + implementer
* Exact resolving evidence: The implementation record and final status notes show code/test validation results and clearly label required-status enforcement as a separate future, approval-gated repository-setting task.
* Decision route: direct_planner_correction_with_explicit_user_approval_for_repo_settings

## Strengths and Residual Risk

* Strengths: The plan is unusually well bounded for a standard critique. It covers all confirmed user requirements, names the specific GitHub controls, preserves the repository’s existing pin conventions, and includes deterministic tests that avoid live advisory calls. Its evidence chain is anchored to the repo’s existing validator and existing test suite rather than a speculative design.
* Residual risk: The plan is structurally strong but still depends on implementation discipline in two places: the malware-check output contract and the separation between local validation evidence and any later GitHub required-check enablement. Those are manageable refinements rather than plan blockers.

## Questions or Blocking Evidence Gaps

* None.

## Limitations

* This critique is bounded to the supplied plan, repository evidence, and research artifact; it does not observe a live GitHub repository or a real dependency advisory response. It therefore judges readiness and completeness as a planning artifact, not the live enforcement state of the eventual GitHub configuration.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: implementer
* Smallest next action: Define and freeze the malware-check file path and output contract before implementation, then encode that contract in fixture-driven tests.
* User response required: no
