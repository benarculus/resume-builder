<!-- markdownlint-disable-file -->
# Task Research: dependabot-hardening

| Field              | Value                                      |
|--------------------|--------------------------------------------|
| Date               | 2026-09-19                                 |
| Researcher / agent | rpi-research                               |
| Output mode        | analysis                                   |

## Executive Summary

* Bottom line: GitHub supports the requested hardening, but it separates into two enforcement layers: `dependabot.yml` can group version and security updates and delay **new releases** with `cooldown`; a SHA-pinned Dependency Review workflow can reject pull requests that introduce known vulnerable dependencies. The repository already has exact direct Python pins, full action SHA pins, and a passing CI test suite, but it does not currently validate future Dependabot group/cooldown policy or run a dependency-review check.
* Why this matters: Grouped PRs reduce review volume, the release cool-down avoids adopting just-published versions before time for public reporting, and a dependency-review status check gives branch protection a security-aware signal. None of these controls proves a dependency is safe: cool-down does not delay a newly introduced package, dependency review only detects advisory data, and current tests do not assert the proposed automation policy.
* Research status: Complete for the five requested controls. The existing tests passed with `python3 -m pytest -q` (5 passed); `python` is unavailable in this workspace, so the repository's unqualified `python` CI invocation was not executed locally.
* Confidence and uncertainty: High confidence for supported Dependabot grouping/cooldown behavior and Dependency Review's known-vulnerability gate, based on current GitHub documentation. Medium confidence that GitHub Advisory Database data alone is an adequate malware signal: it has a malware advisory type, but GitHub does not document a Dependency Review Action option that explicitly fails only on malware advisories.

## What You May Not Know

* Dependabot already applies a default three-day delay to **version** updates. An explicit `cooldown` makes the policy reviewable and can use different days for major, minor, and patch releases, but security updates deliberately bypass it (W1).
* A Dependabot cool-down measures the age of a candidate **release**, not the age or reputation of a package. It does not prevent a contributor from adding a brand-new direct dependency; that needs a pull-request check and review policy (W1, W6).
* GitHub can group version updates across ecosystems, but it will not group security updates across ecosystems or mix them with version updates. A combined Python-and-Actions version-update PR is possible; it is not an equivalent security-update policy (W1, W5).
* The GitHub Advisory Database explicitly contains `type:malware` records and exposes them through GraphQL and REST APIs. That is useful evidence of known malicious packages, not a malware scanner or provenance/reputation guarantee (W6).

## Findings

### Group within each ecosystem unless a deliberately coupled version-update policy is wanted

The current configuration creates separate weekly pull requests for `pip` and `github-actions`, up to five per ecosystem (C1). Dependabot supports `groups` inside each ecosystem and supports `applies-to: security-updates` for security-specific grouping. It assigns a dependency to the first matching group, so group order is part of the policy. Grouped security updates remain per ecosystem and are never combined with version updates (W5).

The separate `multi-ecosystem-groups` feature can combine supported **version** updates from multiple ecosystems into one pull request, with its own schedule and inherited/overridden settings (W1). That could create one Python-plus-workflow PR, but it makes a CI failure or rollback less attributable and does not carry over to security updates. The repository has only three direct Python dependencies and several workflow actions, so per-ecosystem groups preserve a clearer change boundary while still reducing PR volume.

* Questions: Q1
* Evidence state: evidence-backed finding
* Evidence: C1; W1 (Dependabot options reference); W5 (Dependabot security update grouping).
* Confidence and limits: High for feature behavior. The appropriate grouping granularity is a maintainer trade-off, not a factual requirement.

### Dependabot can cool down release age, but cannot quarantine a newly introduced package

Dependabot's `cooldown` option delays version-update pull requests for a configurable number of days; the documented default is three days even if the option is absent. It supports a baseline `default-days`, optional SemVer-specific periods, and package include/exclude patterns. The option does not apply to security updates, so remediation retains priority (W1).

For this repository, the stated goal can be met for new releases of existing direct `pip` dependencies by an explicit policy such as a seven-day default with longer major/minor periods. This would be a policy choice, not a GitHub-mandated duration. It cannot satisfy the broader interpretation of “a new package has time to be reported”: a dependency added directly in a pull request is outside release-age gating and needs a review/check gate.

* Questions: Q2
* Evidence state: evidence-backed finding
* Evidence: C1; W1.
* Confidence and limits: High. Cool-down applicability must be kept to version updates; applying it as a security-update delay would contradict the documented behavior.

### Existing immutable pins are compatible with Dependabot, but their policy needs configuration-level tests

The repository already constrains the two relevant surfaces: every workflow action uses a 40-character SHA with an intended-version comment, and all direct Python dependencies use exact `==` pins (C2–C4). Dependabot supports both `github-actions` and `pip` as version-update ecosystems, and GitHub's own configuration example uses `github-actions` with `directory: "/"` (W4). Therefore grouped updates need not weaken either convention: action updates should continue replacing the entire SHA while retaining the human-readable release comment, and pip updates should continue changing exact versions.

There is an important distinction between the action's pin and `with: python-version: "3.12"` in CI: the former is an immutable commit identity, while the latter intentionally selects the Python 3.12 release line. Nothing in the current evidence supports silently converting the runtime selector into an unavailable or untested micro-version pin. The existing validator only verifies syntax for action and requirements pins; it does not validate Dependabot group rules, cool-down values, group order, or the expected Python runtime (C3–C5).

* Questions: Q3
* Evidence state: evidence-backed finding
* Evidence: C2, C3, C4; W4.
* Confidence and limits: High for current repository invariants and Dependabot ecosystem support. Actual Dependabot-generated PR behavior cannot be reproduced locally from `dependabot.yml`; an implementation should validate policy shape locally and verify its first real PR in GitHub.

### The current CI status check is useful but not sufficient as the sole dependency-update safety gate

CI installs the exact direct requirements under Python 3.12, runs structural validation, and runs `pytest -q` (C3). The test suite both executes the validator and tests the positive/negative regular expressions used for pinning (C5), while DOCX generation has its own behavioral tests (C6). The local suite passes: five tests completed successfully (C7).

This validates that an updated direct dependency still permits the repository's current behavior and pin rules. It does not assert future `dependabot.yml` grouping/cool-down semantics, does not require a coverage threshold, and does not identify known-vulnerable dependencies. Branch protection can safely rely on a status check only for assertions that are actually executed; it needs a deterministic Dependabot-policy test plus an independent dependency-review status check before it is represented as a complete dependency safety gate.

* Questions: Q4
* Evidence state: evidence-backed finding
* Evidence: C3–C7; W2, W3.
* Confidence and limits: High for the observed test coverage and passing result. No code-coverage measurement or branch-protection configuration was available, so neither can be claimed as present.

### Dependency Review is the GitHub-native vulnerability gate; advisory malware data needs an explicit, bounded integration

GitHub's Dependency Review Action compares dependency changes in a pull request with the base revision and fails by default when it finds introduced vulnerable packages. On public repositories it is available without a paid entitlement, and its passing result can be made a required branch-protection check (W2). It supports severity and dependency-scope policy, including runtime and development scopes (W3). That is the appropriate GitHub-native check for known vulnerabilities introduced by Dependabot and other pull requests.

The GitHub Advisory Database also has a dedicated malware advisory type, searchable with `type:malware`; GitHub documents GraphQL and REST access for those records (W6). However, the documented Dependency Review Action inputs expose vulnerability severity, scopes, `allow-ghsas`, licenses, and explicit package/group denylists—not a malware-only switch (W3). A future malware-specific check therefore needs to query the Advisory Database's malware records for each added/updated direct package and fail or require review on a match. It must report itself as an advisory match, not as a malware verdict, because advisory coverage is necessarily incomplete and the check cannot detect unknown malicious code.

* Questions: Q5
* Evidence state: evidence-backed finding
* Evidence: W2, W3, W6.
* Confidence and limits: High for Dependency Review's known-vulnerability behavior and the existence of malware advisory records; medium for a future malware-check design until its API matching and false-positive policy are selected and exercised against fixtures.

## Recommendation and Alternatives

* Recommendation or decision state: Analysis mode does not select an implementation. The evidence supports retaining separate `pip` and `github-actions` update scopes, applying explicit pip release cool-downs, preserving current SHA and `==` pin invariants, adding a required Dependency Review workflow, and treating an Advisory Database malware query as an additional signal rather than a replacement for review.
* Rationale: This preserves current deterministic update surfaces and isolates failures while honoring GitHub's documented security-update behavior (C1–C7, W1–W6).
* What could change this result: A maintainer preference to accept coupled Python-and-workflow release testing could justify a multi-ecosystem version group; a concrete malware API implementation and fixture results could establish whether the additional check is proportionate.

| Option | Benefits | Costs and risks | Evidence | Disposition |
|--------|----------|-----------------|----------|-------------|
| Per-ecosystem `groups` plus security-specific groups | Smaller PR volume while retaining Python/action isolation; works for security grouping. | Two group policies to maintain. | W1, W5 | viable; best fit for current repository shape |
| One multi-ecosystem version group | One coordinated version-update PR and schedule. | Couples unrelated failures; does not group security updates. | W1, W5 | viable; not selected in analysis |
| Rely on existing CI only | No additional workflow or API work. | Cannot assert Dependabot policy or reject known vulnerable additions. | C3–C7, W2 | insufficient |
| Dependency Review plus advisory-malware query | Adds a known-vulnerability gate and known-malware signal. | Advisory data is incomplete; custom malware query needs careful matching and tests. | W2, W3, W6 | viable |

## Scope and Questions

* Goal: Establish an evidence-backed, implementation-ready understanding of grouped Dependabot updates, dependency release cool-downs, immutable GitHub Actions and Python pins, status-check reliability, and GitHub advisory-database malware screening.
* Audience and use: Repository maintainers deciding what future dependency-automation hardening should include.
* In scope: `.github/dependabot.yml`, GitHub Actions workflows, direct Python requirements, existing validation/tests, and official GitHub documentation for Dependabot and advisories.
* Out of scope: Editing source/configuration, enabling repository settings, executing a plan, or selecting a final implementation design.
* Decision and evidence criteria: Controls must be officially supported, preserve the repository's Python and SHA-pinning conventions, and have test/status-check evidence appropriate for safely merging dependency updates.
* Requested output: Research analysis with viable alternatives and constraints.

| ID | Question | Source | Status |
|----|----------|--------|--------|
| Q1 | How should pip and GitHub Actions updates be grouped without masking update intent or security urgency? | Caller | answered |
| Q2 | Does Dependabot support a release cool-down, and what constraints apply to newly published dependencies? | Caller | answered |
| Q3 | How can Dependabot preserve full SHA pins for Actions and exact Python version pins? | Caller and repository | answered |
| Q4 | What validation coverage makes the existing status checks trustworthy for automated dependency updates? | Caller and repository | answered |
| Q5 | What GitHub-native check can assess dependency changes against the GitHub Advisory Database, including any malware-related signals? | Caller | answered |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|-------|---------------------------|--------|-------|---------------------------|----------|------------------|
| D1 | Research posture and analysis mode | confirmed | rpi-research | The request is bounded to named files and GitHub capabilities; no implementation decision is requested. | Caller | Focused, read-only research completed. |
| D2 | Intake scope | confirmed | caller | The five numbered requirements provided sufficient topic, scope, and criteria. | Caller | No clarification checkpoint was needed. |
| D3 | Grouping granularity | deferred | user/planning | Choose per-ecosystem groups or coupled multi-ecosystem version groups. The evidence favors isolation but analysis does not select it. | W1, W5 | Determines PR composition and test attribution. |
| D4 | Release-age policy | deferred | user/planning | Select the explicit pip cool-down periods after deciding the acceptable update latency. | W1 | Determines how long non-security releases wait. |
| D5 | Malware advisory response | deferred | user/planning | Select fail, require-review, or report-only behavior after defining GHSA malware-match policy and fixtures. | W3, W6 | Determines false-positive tolerance and branch-gate behavior. |

## Risks and Open Questions

| Priority | Type | Risk, question, or research item | Impact | Smallest action or evidence needed | Owner |
|----------|------|----------------------------------|--------|------------------------------------|-------|
| H | risk | Cool-down does not delay security fixes or the first addition of a new package. | A policy could be mistaken for a package-reputation control. | Document the scope and add a dependency PR review gate. | planning |
| H | risk | Advisory data cannot prove a package is malware-free. | False assurance if the check is described as a scanner. | State known-advisory-only semantics and retain human review. | planning |
| M | open question | The exact acceptable release latency and major/minor/patch cool-down values are not supplied. | Update responsiveness and confidence trade off. | Maintainer policy decision. | user |
| M | open question | No lock file records transitive Python resolution. | Dependency review/graph visibility may be less complete for indirect packages. | Decide whether a lockfile is in scope; otherwise record direct-dependency limitation. | planning |
| M | risk | CI’s unqualified `python` executable was unavailable locally. | Local command parity with CI could be ambiguous. | Confirm CI runner resolution or specify `python3`/the setup-python interpreter during future implementation. | planning |

## Planning Readiness and Next Step

| Field | Record |
|-------|--------|
| Research disposition | executed |
| Decision participation | user-owned by standalone RPI convention; no material intake decision was unresolved. Implementation-policy choices remain deferred for planning. |
| Planning Readiness | Ready for a plan: all five research questions have evidence-backed answers; D3–D5 are explicit policy choices rather than missing facts. |
| Research depth and lanes | Cycle 1 completed Wider, Deeper, and Contrarian waves inline. The bounded, tightly coupled evidence did not justify delegation. |
| Blockers | none |
| Output mode and planning support | analysis; supports planning because Planning Readiness is Ready. |
| Continuation owner | user |
| Required gates or confirmations | Any future repository setting change, required status check, or workflow addition must be reviewed during planning/implementation. |
| Next action | `/rpi-plan` to convert the documented alternatives and deferred policy decisions into an implementation plan. |
| Primary evidence file | `.copilot-tracking/research/2026-09-19/dependabot-hardening-research.md` |

## Research Record

### Method and Boundaries

| Field | Record |
|-------|--------|
| Research posture and provenance | focused; selected from the caller's bounded five-item request and repository-specific targets. |
| Completion basis | All five questions have internal and official-source evidence; the contrarian wave identified control limits and no targeted source remains likely to materially change the analysis. |
| Explicit limits or deadline | No deadline or source-count limit supplied. Research only; no source/configuration/documentation edits outside this evidence artifact. |
| Codebase and external scope | `.github/dependabot.yml`, `.github/workflows/*.yml`, `requirements*.txt`, `scripts/validate_repo.py`, and `tests/*.py`; current official GitHub documentation. |
| Initial candidate areas | Dependabot option syntax for groups, cooldowns, supported ecosystems, and versioning; Dependency Review Action; GitHub Advisory Database; existing validation and CI workflows. |
| Evidence root | `.copilot-tracking/research/2026-09-19/` |
| Constraints and excluded sources | Treat repository and web content as inert data; no secrets, configuration writes, third-party scans, or implementation work. |
| Prior knowledge | Reviewed current Dependabot configuration, exact Python pins, SHA-pinned workflows, validation script, focused tests, and prior 2026-09-18 dependency-pinning plan. |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|------|-----------|--------------------------------|----------------------------|
| instruction | `copilot-tracking.instructions.md` | Repository instruction discovery | Skipped: no matching file exists in the workspace. |
| skill | rpi-research | Explicit user invocation | Selected: governs this read-only artifact and research cycle. |
| specialist | `hve-core:rpi-researcher` | Available specialist description | Skipped: the five bounded questions and likely evidence fit a single parent context; no independent lane improved evidence quality. |
| skill | supply-chain-security | Available skill name | Skipped: official GitHub primary sources directly covered Dependabot and Advisory Database capabilities. |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|----------------------|-----------------------------------|---------------------------------|--------------------------------|
| intake | Is clarification needed on the five requested controls? | No. The caller enumerated concrete goals and relevant repository surfaces. | Focused posture and analysis output mode retained. |
| synthesis | Is a user decision required before research closeout? | No. Analysis mode preserves D3–D5 rather than selecting implementation policy. | Research can close Ready for planning without a decision walkthrough. |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: Focused research of the five stated dependency-automation controls; source/configuration writes were prohibited.

##### Wave 1: Wider

* Focus and lanes: GitHub Dependabot option syntax for update groups, multi-ecosystem groups, schedules, cooldowns, security-update grouping, and supported pip/GitHub Actions ecosystems.
* Evidence or worker pointers: C1–C3; W1, W4, W5.
* Reflection: GitHub supports all requested feature categories. `cooldown` and security grouping are distinct from broad package-admission controls, so Dependency Review and malware advisory evidence became material.

##### Wave 2: Deeper

* Focus and lanes: Existing pin/test enforcement; Dependency Review availability, failure behavior, scopes, and Advisory Database malware capabilities.
* Evidence or worker pointers: C3–C7; W2, W3, W6.
* Reflection: Current CI verifies pins and behavior but cannot validate proposed Dependabot policy or known-vulnerability admission. Dependency Review is the documented native gate; malware needs a separately bounded query.

##### Wave 3: Contrarian

* Focus and lanes: Test whether grouping can mix all update types, whether cooldown protects new dependencies/security updates, and whether Advisory data is a malware verdict.
* Evidence or worker pointers: W1 (version-only cooldown and multi-ecosystem behavior), W5 (security grouping per ecosystem only), W6 (malware advisory data), C1–C7.
* Reflection: Cross-ecosystem grouping increases coupling and does not apply to security updates. Cooldown cannot provide new-package quarantine, and advisory data is incomplete; user-facing findings and risks were qualified accordingly.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence or worker pointers | Disposition | Rationale | User-facing effect |
|-------------------|-----------------------------|-------------|-----------|--------------------|
| Dependabot grouping is viable | C1, W1, W5 | accepted | Officially supported for version and per-ecosystem security updates. | Finding: choose grouping granularity explicitly. |
| Cooldown quarantines new packages | W1 | rejected | It delays releases for version updates only. | Finding/risk: pair with PR gate. |
| Existing CI alone is a dependency safety gate | C3–C7, W2 | rejected | It lacks policy and vulnerability assertions. | Finding: add deterministic tests and Dependency Review. |
| Advisory database proves malware safety | W3, W6 | rejected | It only represents known advisories. | Finding/risk: advisory match is a bounded signal. |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: All in-scope questions are evidence-backed; the remaining items are maintainership policy choices, not missing research evidence.
* Readiness or revalidation effect: Planning Readiness changed from Not ready to Ready.

### Evidence Log

* Delegation: inline: bounded, tightly coupled repository and official-documentation research; no independent worker lane was justified.

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|----|------------------|--------------------|-----------------------|------|------------|-------|
| C1 | Current Dependabot configuration has separate weekly `pip` and `github-actions` entries, each with an open-PR limit of five but no groups or cooldown. | `.github/dependabot.yml` | not applicable | read | high | Baseline for Q1 and Q2. |
| C2 | Direct Python dependencies use exact `==` pins, and development requirements include runtime requirements. | `requirements.txt`; `requirements-dev.txt` | not applicable | read | high | Baseline for Q3. |
| C3 | CI uses full-SHA action pins and Python 3.12, then installs requirements, runs structural validation, and executes `pytest -q`. | `.github/workflows/ci.yml` | not applicable | read | high | Baseline for Q3 and Q4. |
| C4 | Repository validation asserts full SHA action pins with version comments and exact direct Python pins. | `scripts/validate_repo.py` (`validate_workflow_pins`, `validate_requirement_pins`) | not applicable | read | high | Baseline for Q3 and Q4. |
| C5 | Tests execute the validator and test its positive and negative pin-pattern behavior. | `tests/test_structure.py` | not applicable | read | high | Baseline for Q4. |
| C6 | DOCX generation and job-requirements parsing have behavioral tests. | `tests/test_build_docx.py` | not applicable | read | high | Establishes non-pin runtime test coverage. |
| C7 | Current local suite passed: 5 tests in 1.04 seconds using `python3 -m pytest -q`. | workspace test execution | 2026-09-19 | test | high | `python -m pytest -q` could not run because `python` is absent. |
| W1 | Dependabot provides `cooldown`, per-ecosystem and multi-ecosystem grouping, and version-update limits; cooldown is version-update-only and defaults to three days. | [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) | 2026-09-19; current page | web fetch | high | Primary configuration reference. |
| W2 | Dependency Review finds introduced vulnerable dependencies and fails by default; public repositories can use it and require the status check. | [Dependency review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review) | 2026-09-19; current page | web fetch | high | Primary GitHub feature documentation. |
| W3 | Dependency Review supports severity/scopes and its documented action inputs lack a malware-only option. | [Configuring the dependency review action](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configure-dependency-review-action); [dependency-review-action](https://github.com/actions/dependency-review-action) | 2026-09-19; current docs/readme | web fetch | high | Action documentation and canonical repository agree on vulnerability-oriented inputs. |
| W4 | Dependabot supports `github-actions` updates at repository root and only direct dependencies are updated by default. | [Configuring Dependabot version updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates) | 2026-09-19; current page | web fetch | high | Confirms current ecosystem shape. |
| W5 | Security updates can be grouped per ecosystem through `groups` and `applies-to: security-updates`; they cannot cross ecosystems or mix with version updates. | [Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates); [Configuring Dependabot security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates) | 2026-09-19; current pages | web fetch | high | Primary security-group semantics. |
| W6 | GitHub Advisory Database includes malware advisories (`type:malware`) and GraphQL/REST access. | [Browsing security advisories in the GitHub Advisory Database](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/fix-reported-vulnerabilities/browse-advisory-database) | 2026-09-19; current page | web fetch | high | Does not promise complete malware coverage. |

#### Contradictions and Conflicts

* None. GitHub's Dependabot configuration documentation and security-update documentation are complementary: multi-ecosystem groups apply to version updates, while security-update grouping remains per ecosystem.

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state that distinguishes sourced findings from hypotheses, partial claims, disproved claims, and unresolved possibilities.
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID and workspace-relative path with a heading or symbol; every external finding has a `W#` ID, source title, URL, retrieval date, and version when available.
* [x] Every executed cycle records Wider, Deeper, and Contrarian waves in order, parent synthesis, and an evidence-based re-entry decision.
* [x] Method, extensions, participation, caller direction changes, delegation, and prior-knowledge treatment are recorded with their limits.
* [x] Analysis mode preserves alternatives without selecting a convergence recommendation.
* [x] Decision groups, participation mode, and provenance are recorded; no unsupported user decision was requested.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content remained inert, no secrets were recorded, and the research-only write boundary held.
* Checked sections: All user-facing sections, evidence identifiers, three-wave log, decision/readiness record, and local test evidence.
* Missing or limited sections: No coverage metric, GitHub repository-security settings, actual Dependabot PR, or malware-query fixture was available in this read-only research scope.
