<!-- markdownlint-disable-file -->
# Task Research: spdx-tools-migration

| Field              | Value       |
|--------------------|-------------|
| Date               | 2026-09-25  |
| Researcher / agent | rpi-research |
| Output mode        | convergence |

## Executive Summary

* Bottom line: Migrate SPDX specification validation to official `spdx-tools==0.8.5`, but install it in a dedicated, fully hash-locked Python 3.12 environment and retain a renamed `validate_release_sbom_contract.py` for repository-owned assertions.
* Why this matters: This removes recurring hand-written SPDX type/schema defects from repository code while preserving the release-specific guarantees a generic validator cannot know, without replacing them with an unpinned Marketplace dependency chain.
* Research status: Complete. One focused wider/deeper/contrarian cycle covered official behavior, real Syft compatibility, dependency resolution, current workflow boundaries, known validator limitations, and alternatives.
* Confidence and uncertainty: High confidence in the responsibility split and migration direction. Remaining uncertainty is bounded to normal upstream-validator defects and the maintenance cost of a 13-artifact hash lock; neither prevents planning when explicitly mitigated.

## What You May Not Know

* The current custom validator is stricter than the official SPDX 2.3 JSON schema in several places. SPDX does not schema-require package `supplier`, `filesAnalyzed`, `licenseConcluded`, `licenseDeclared`, or `copyrightText`; absent licensing and copyright values can imply `NOASSERTION`. Supplier remains important here because it is an NTIA/repository release requirement, not because every SPDX package must carry it.
* The official validator is not infallible. It has an open false-negative report for lowercase `primaryPackagePurpose`, and malformed missing fields can produce a traceback rather than a friendly diagnostic. The latter still exits nonzero, so it is a usability defect rather than a publication bypass.
* Pinning only `spdx-tools==0.8.5` does not freeze validation behavior. Its resolved Python 3.12 environment currently contains 13 artifacts, which should be exact-pinned and hash-verified.
* `spdx-tools` 0.8.5 cannot run under the repository owner's local Python 3.9. The release job and hosted CI already target Python 3.12, so the validator should remain isolated from the application's normal/local dependency set.

## Findings

### Official validation should own SPDX conformance

Official `spdx-tools` parses and validates SPDX 2.2/2.3 documents, including creation metadata, package and relationship semantics, license expressions, URI rules, document relationships, and identifier uniqueness. Passing `--version SPDX-2.3` also prevents an otherwise valid SPDX 2.2 document from satisfying this release contract. Empirical tests confirmed nonzero failures for the exact CCR creation-metadata defects, duplicate identifiers, and missing package download location. A checksum-verified Syft 1.52.0 SBOM generated from this repository passed after the current metadata enrichment step.

* Questions: Q1
* Evidence state: Evidence-backed finding
* Evidence: W1, W2, W7, W9, W11, W12, E2
* Confidence and limits: High. Upstream source and local mutation testing agree. Current 0.8.5 could not execute under local Python 3.9, but its CLI source is materially the same and upstream exercises it on Python 3.12.

### The repository validator still has a necessary but narrower role

A generic SPDX validator cannot establish that the document is for `resume-builder`, that its root version equals the release tag, that the supplier is `benarculus`, that every exact runtime pin from `requirements.txt` is present, or that the document/root/runtime relationships express this repository's intended release model. Those assertions should remain in a renamed `validate_release_sbom_contract.py`. Generic JSON shape, SPDX-required fields, field types, verification-code semantics, identifier uniqueness, creation metadata, license syntax, and general relationship validity should be removed from that script.

* Questions: Q2
* Evidence state: Evidence-backed finding
* Evidence: C1-C4, W8, W12, E2
* Confidence and limits: High. The current function's checks divide cleanly between standard-owned and repository-owned rules. Exact namespace policy is a repository choice: if retained, it should assert the intended Syft/release identity rather than merely duplicating generic URI validity.

| Responsibility | Official `spdx-tools` | Release-contract validator |
|----------------|-----------------------|----------------------------|
| JSON/SPDX parsing and typed fields | Own | Do not duplicate |
| SPDX version | Own via `--version SPDX-2.3` | Do not duplicate |
| Data license, creation metadata, license/URI syntax | Own | Do not duplicate |
| Required package fields and `filesAnalyzed` semantics | Own | Do not duplicate |
| General relationship validity and unique SPDX IDs | Own | Do not duplicate |
| Product name and exactly one release root | No | Own |
| Release version equality | No | Own |
| Root supplier/originator policy and dependency non-misattribution | No | Own |
| Exact runtime dependency versions | No | Own |
| Document describes the selected root and root relates every runtime dependency | Only general validity | Own exact topology |

### Secure installation requires a dedicated hash-locked validation dependency set

`spdx-tools==0.8.5` requires Python 3.10+ and resolves to 13 artifacts for the hosted Linux/Python 3.12 environment. The repository's current exact-direct-pin policy does not freeze transitives, and the package does not publish evidence of release provenance comparable to the alternative binary action. A dedicated release-validation requirements file with exact versions and SHA-256 hashes, installed with `pip --require-hashes --only-binary=:all:` after the already approved SHA-pinned `actions/setup-python` Python 3.12 step, gives deterministic artifact selection and confines the added dependency graph to SBOM validation.

* Questions: Q3
* Evidence state: Evidence-backed finding
* Evidence: C4, W3, W6, W7, E3
* Confidence and limits: High for the current Linux/Python 3.12 resolution. Hashes and versions need normal automated maintenance when upgrading; cross-platform local installation is intentionally not the release contract.

### Marketplace actions are viable but not preferable here

The schema-only `validate-sbom-action` is concise, but its action dynamically installs unconstrained npm validator dependencies and offers schema validation rather than the broader official semantic validator. `sbom-tools-action` has materially stronger binary checksum/provenance controls and richer quality checks, but it is a newer third-party validation interpretation rather than the SPDX project's tool, and its broader feature set is unnecessary for this release gate. Keeping the current combined Python validator avoids dependencies but preserves the demonstrated maintenance problem: each CCR round can reveal another hand-coded fragment of the specification.

* Questions: Q4
* Evidence state: Evidence-backed finding
* Evidence: W4, W5, W13, C2
* Confidence and limits: Medium-high. Marketplace project maturity can change; the recommendation reflects the current pinned releases and this repository's narrow need.

### Known official-validator gaps are manageable, not disqualifying

Open upstream issues show that `spdx-tools` can miss at least one enum-casing violation and can emit a traceback for some malformed required fields. This means “official” is not equivalent to complete or perfect. The recommended mitigation is not to reproduce the SPDX specification again; it is to pin the validator, keep fail-closed workflow behavior, retain small integration mutations proving the specific release gate rejects known invalid classes, and let the repository-specific script remain policy-only.

* Questions: Q1, Q5
* Evidence state: Evidence-backed finding
* Evidence: W14, W15, E2
* Confidence and limits: High that the known issues exist and do not bypass the tested gate. Unknown future false negatives remain an upstream-tool risk shared by any validator.

## Recommendation and Alternatives

* Recommendation or decision state: Adopt pinned official `spdx-tools==0.8.5` for SPDX 2.3 conformance, installed from a dedicated fully hashed Python 3.12 requirements set; rename and reduce the custom script to `validate_release_sbom_contract.py`.
* Rationale: It gives the most authoritative and maintainable division of responsibility while preserving product-specific assertions and the read-only generation boundary. Real Syft output passes, current CCR mutations fail, and deterministic installation is feasible with 13 known artifacts. W1-W15, C1-C4, E2-E3.
* What could change this result: A future official validator regression that accepts the generated invalidity classes, an organization policy prohibiting PyPI dependencies in release jobs, or a substantially more mature Marketplace validator with equally authoritative SPDX coverage and stronger verified distribution.

| Option | Benefits | Costs and risks | Evidence | Disposition |
|--------|----------|-----------------|----------|-------------|
| Hash-locked official `spdx-tools` plus reduced release-contract validator | Authoritative broad SPDX validation; tested against real artifact and CCR mutations; clear responsibility boundary | 13-artifact lock; Python 3.12 isolation; upstream defects still possible | C1-C4, W1-W15, E2-E3 | Selected recommendation |
| `sbom-tools-action` plus reduced release-contract validator | Checksummed and provenance-verified downloaded binary; broader quality features | Third-party semantics, newer/lower adoption, unnecessary feature breadth, action/tool versioning to govern | W5, W13 | Viable but rejected |
| Schema-only Marketplace action plus reduced release-contract validator | Simple workflow; vendored official schemas | Runtime installation of unconstrained npm packages; schema-only coverage; very new project | W4 | Rejected |
| Keep combined custom validator | No new runtime dependency; local Python 3.9 compatible | Ongoing specification duplication and repeated review defects; narrower coverage | C2, current CCR history | Rejected |

## Scope and Questions

* Goal: Determine whether PR #16 should migrate SPDX specification conformance to pinned official `spdx-tools` and narrow the custom validator to release-specific assertions.
* Audience and use: The repository owner will use the evidence to decide whether to plan and implement the migration in the active release-pipeline pull request.
* In scope: Current publication workflow and tests; official SPDX 2.3 tooling and validation behavior; deterministic installation and pinning; Marketplace alternatives; naming and responsibility boundary for the remaining script.
* Out of scope: Implementing workflow or source changes, selecting SPDX 3.0, changing SBOM generation away from Syft, vulnerability scanning, and unrelated release-pipeline changes.
* Decision and evidence criteria: SPDX 2.3 conformance coverage, authority and maintenance, reproducibility, supply-chain risk, least privilege, offline/runtime behavior, compatibility with generated Syft output, testability, and preservation of repository-specific release assertions.
* Requested output: Evidence-backed convergence recommendation and planning-readiness assessment.

| ID | Question | Source | Status |
|----|----------|--------|--------|
| Q1 | Can official `spdx-tools` reliably validate the generated SPDX 2.3 JSON and catch the class of schema/type defects repeatedly identified by CCR? | Explicit caller direction and current PR findings | Answered |
| Q2 | What exact responsibilities must remain in a repository-specific validator after migration? | Inferred from current release contract | Answered |
| Q3 | How should `spdx-tools` be pinned and installed without undermining the hardened release workflow? | Inferred from supply-chain criteria | Answered |
| Q4 | Are Marketplace actions or other validators materially better alternatives? | Explicit prior discussion | Answered |
| Q5 | Is the migration ready for planning, and what material risks remain? | RPI continuation contract | Answered |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|-------|---------------------------|--------|-------|---------------------------|----------|------------------|
| D1 | Adopt the recommended official-validator migration for planning | Confirmed | User | User selected pinned official `spdx-tools` plus the reduced release-contract validator | C1-C4, W1-W15, E2-E3; user decision 2026-09-25 | Planning Readiness is Ready |

## Risks and Open Questions

| Priority | Type | Risk, question, or research item | Impact | Smallest action or evidence needed | Owner |
|----------|------|----------------------------------|--------|------------------------------------|-------|
| H | Risk | Official validator dependencies drift if only the top-level package is pinned | Validation behavior or supply-chain inputs could change unexpectedly | Commit a dedicated full lock with exact versions and hashes; install with `--require-hashes --only-binary=:all:` | Downstream planning/implementation |
| M | Risk | `spdx-tools` has known validation and diagnostic defects | A future malformed document might be mishandled or errors may be noisy | Pin the version, assert nonzero workflow behavior, preserve mutation integration tests, and monitor Dependabot/upstream changes | Downstream maintenance |
| M | Risk | Local Python 3.9 cannot install current `spdx-tools` | Local full validation cannot reproduce the release validator directly | Isolate it under explicit Python 3.12 in release and hosted CI; keep the policy validator stdlib-only | Downstream planning |
| L | Further research | Revisit Marketplace alternatives if provenance policy becomes more important than official-validator authority | Could change the preferred tool | Compare then-current adoption, attestations, validation corpus, and release cadence | Future research |

## Planning Readiness and Next Step

| Field                            | Record |
|----------------------------------|--------|
| Research disposition             | executed |
| Decision participation           | user-owned; standalone `/rpi-research` invocation |
| Planning Readiness               | Ready; D1 confirms the evidence-backed migration direction |
| Research depth and helpers       | One complete focused Wider → Deeper → Contrarian cycle; no helper used; all evidence verified directly |
| Blockers                         | None |
| Output mode and planning support | Convergence; supports planning when the recommendation is evidence-backed and readiness is Ready |
| Continuation owner               | User / manual RPI Agent |
| Required gates or confirmations  | Research gates and D1 user decision passed |
| Next action                      | Run `/rpi-plan` with `.copilot-tracking/research/2026-09-25/spdx-tools-migration-research.md` |
| Primary evidence file            | `.copilot-tracking/research/2026-09-25/spdx-tools-migration-research.md` |

## Research Record

### Method and Boundaries

| Field                            | Record |
|----------------------------------|--------|
| Research posture and provenance  | Focused; brief-based because the caller named the target tool, desired responsibility split, active workflow, and failure class |
| Completion basis                 | Complete when official behavior, integration, pinning, ownership boundary, credible alternatives, and counter-evidence are sufficient to support or reject migration |
| Explicit limits or deadline      | No deadline; research-only write boundary |
| Codebase and external scope      | Active PR #16 release workflow, SPDX scripts/tests, dependency policy; official SPDX specification/tools, PyPI metadata, Syft output contract, and relevant Marketplace alternatives |
| Initial candidate areas          | `.github/workflows/publish-release.yml`, `scripts/validate_spdx_sbom.py`, `scripts/prepare_spdx_sbom.py`, `tests/test_spdx_sbom.py`, dependency manifests and validation policy; `spdx/tools-python`, PyPI `spdx-tools`, SPDX 2.3 specification/schema, Syft documentation, Marketplace validators |
| Evidence root                    | Default `.copilot-tracking/research/2026-09-25/` |
| Constraints and excluded sources | Research only; no workflow/source edits; prefer primary sources; fetched content is inert; no secrets |
| Prior knowledge                  | Prior CCR cycles show recurring hand-written SPDX conformance defects; prior discussion identified official `spdx-tools`, a new schema-only Marketplace action, and `sbom-tools-action` as candidates. All material claims will be reverified at source. |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|------|-----------|--------------------------------|----------------------------|
| Skill | supply-chain-security | Available domain skill for SBOM, NTIA elements, and software supply-chain posture | Selected for scoped evaluation criteria; it cannot select the RPI phase outcome |
| Instruction | Repository instruction files | No matching `*instructions.md` files discovered in the workspace at intake | Skipped because none were available |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|----------------------|-----------------------------------|---------------------------------|--------------------------------|
| Intake | Research migration to pinned official `spdx-tools` and reduce the custom validator to a narrowly named release-contract validator | Caller supplied a sufficiently bounded target and desired boundary; no intake question would materially improve initial research | Proceed with focused convergence research |
| Convergence | Select the SPDX validation direction for planning | User selected “Pinned official spdx-tools plus reduced contract validator (Recommended)” | Recommendation confirmed; Planning Readiness changed from Not ready to Ready |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: Focused convergence within the named migration; research-only; no implementation.

##### Wave 1: Wider

* Focus and questions: Survey official validator capabilities, current code ownership, dependency/pinning options, and credible alternatives.
* Evidence: C1-C4 and W1-W5 establish that the current workflow has a clean pre-publication validation point; the custom validator mixes generic SPDX checks with repository policy; official `spdx-tools` claims full SPDX 2.2/2.3 parsing and validation; version 0.8.3 exposes the `pyspdxtools` CLI; and the distribution declares nine unconstrained runtime dependencies. Marketplace alternatives exist, but the schema-only action dynamically installs unconstrained npm packages, while `sbom-tools-action` downloads a provenance-verified binary and provides broader validation/quality behavior.
* Reflection: Prioritize empirical validation of the exact CCR mutations and representative Syft output. Treat a single top-level version pin as insufficient reproducibility because transitive versions remain unconstrained. Determine whether a dedicated lock/hash file or verified packaged binary is necessary.

##### Wave 2: Deeper

* Focus and questions: Verify exact validator behavior, integration requirements, compatibility, and responsibility split.
* Evidence: W6-W12 and empirical evidence E1-E2 show that 0.8.3 and the current 0.8.5 CLI source detect the CCR creation-metadata defects and duplicate identifiers and exit nonzero. The earlier apparent status-0 observation was a shell-capture error and was corrected by storing the status immediately after each invocation. The current stable 0.8.5 requires Python >=3.10 and upstream tests it on Python 3.10-3.14, including 3.12. The official SPDX 2.3 JSON schema requires only `SPDXID`, `downloadLocation`, and `name` at package-schema level; several fields currently treated as universally mandatory by the custom validator are optional or have `NOASSERTION` semantics. A checksum-verified Syft 1.52.0 SBOM generated from this repository, enriched by the existing preparer, passed official SPDX 2.3 validation.
* Reflection: The official CLI is suitable as a fail-closed conformance gate when invoked with `--version SPDX-2.3`. Reclassify supplier, package-presence, root identity/version, runtime completeness, and exact relationships as repository contract. Remove generic type/schema duplication from the custom validator. Address Python-version and dependency-locking constraints before recommending implementation.

##### Wave 3: Contrarian

* Focus and questions: Challenge migration value, examine failure modes and stronger alternatives, and test whether keeping or replacing all custom validation is preferable.
* Evidence: W13-W15 and E3 show that the strongest Marketplace alternative verifies its downloaded binary but remains a third-party validator; official `spdx-tools` has open validation and diagnostic issues; the current stable dependency graph contains 13 artifacts and lacks comparable published provenance; and local Python 3.9 is incompatible. Keeping the combined validator avoids those costs but preserves repeated specification-maintenance failures. Anchore generation alone is insufficient because repository enrichment mutates the artifact and an independent pre-publication gate detects generator or enrichment regressions.
* Reflection: Counter-evidence weakens any claim that official tooling eliminates validation risk, but does not weaken the responsibility-boundary recommendation. The secure form must hash-lock dependencies, explicitly select Python 3.12, retain fail-closed mutation coverage, and keep repository policy separate.

##### Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|-------------------|----------|-------------|-----------|--------------------|
| Migrate SPDX conformance to official tooling | W1-W12, E2 | Accepted | Real output passes and the CCR defect class fails; official tooling owns broader semantics | Selected recommendation |
| Keep a reduced repository-specific validator | C1-C4, W8, W12 | Accepted | Product version, supplier, exact dependencies, and exact topology are outside generic validator knowledge | Defines script boundary |
| Use only a top-level package pin | W3, E3 | Rejected | Leaves 12 transitive artifacts unconstrained | Requires full hash lock |
| Replace validation wholly with a Marketplace action | W4, W5, W13 | Rejected | Either weaker dependency determinism/schema-only coverage or unnecessary third-party breadth | Marketplace remains future alternative |
| Treat official validation as perfect | W14, W15 | Rejected | Open false-negative and diagnostic issues exist | Retain fail-closed integration mutations and version governance |

* Another complete three-wave cycle needed: No.
* Trigger or stop basis: Material questions are answered with primary-source and empirical evidence; alternatives and counter-evidence are covered; likely next sources are redundant for the current decision.
* Readiness or revalidation effect: Evidence is planning-ready; only the user-owned adoption decision remains.

### Evidence Log

* Helpers: None.

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|----|------------------|--------------------|-----------------------|------|------------|-------|
| C1 | Current workflow generates, prepares, then validates the SPDX document before artifact transfer and publication | `.github/workflows/publish-release.yml`, `generate` job | not applicable | Read | High | Establishes integration point |
| C2 | Current validator combines generic SPDX shape/type checks with repository-specific version, supplier, dependency, and relationship assertions | `scripts/validate_spdx_sbom.py`, `validate_spdx_sbom` | not applicable | Read | High | Establishes current mixed responsibility |
| C3 | The enrichment script changes only the matching root package's supplier and originator, so conformance validation must occur after enrichment | `scripts/prepare_spdx_sbom.py`, `prepare_spdx_sbom` | not applicable | Read | High | Enrichment can affect SPDX values and belongs before validation |
| C4 | Repository dependency policy requires exact direct pins but does not currently lock or hash transitive dependencies | `requirements-dev.txt`; `scripts/validate_repo.py`, dependency-pin validation | not applicable | Read/search | High | A top-level `spdx-tools==0.8.3` pin alone would not reproduce its full dependency graph |
| W1 | Official tools-python states that v0.8 provides full validation against SPDX 2.2 and 2.3 and supports JSON parsing | SPDX tools-python README, https://github.com/spdx/tools-python/blob/v0.8.3/README.md | 2026-09-25; v0.8.3 | External source read | High | Primary upstream source |
| W2 | `pyspdxtools -i <filename>` parses and validates by default; `--novalidation` is the explicit bypass | SPDX tools-python README, https://github.com/spdx/tools-python/blob/v0.8.3/README.md | 2026-09-25; v0.8.3 | External source read | High | Establishes intended CLI behavior |
| W3 | `spdx-tools` 0.8.3 requires Python >=3.7 and declares click, PyYAML, xmltodict, rdflib, beartype, uritools, license-expression, ply, and semantic-version without exact dependency versions | PyPI JSON and upstream pyproject, https://pypi.org/pypi/spdx-tools/0.8.3/json and https://github.com/spdx/tools-python/blob/v0.8.3/pyproject.toml | 2026-09-25; v0.8.3 | External metadata read | High | Exact top-level pin does not pin transitives |
| W4 | `thomasvincent/validate-sbom-action` validates vendored SPDX schemas but installs unconstrained `ajv-cli` and `ajv-formats` at runtime | Action definition, https://github.com/thomasvincent/validate-sbom-action/blob/main/action.yml | 2026-09-25; main at 421baf4 | External source read | High | Concise but conflicts with deterministic-dependency objective |
| W5 | `sbom-tool/sbom-tools-action` supports validation and quality checks and verifies downloaded binaries using checksums and provenance by default | Marketplace listing, https://github.com/marketplace/actions/sbom-tools-action | 2026-09-25; action v1.2.0 listing | External source read | Medium | Credible alternative, but not the SPDX project's validator |
| W6 | The current stable upstream release is `spdx-tools` 0.8.5, published 2026-03-13; it requires Python >=3.10 and advertises Python 3.10-3.14 support | PyPI metadata, https://pypi.org/project/spdx-tools/0.8.5/ | 2026-09-25; v0.8.5 | External metadata read | High | Hosted Python 3.12 is in range; local Python 3.9 is not |
| W7 | Upstream 0.8.5 CI tests the package and CLI on Ubuntu, macOS, and Windows across Python 3.10-3.14 | Upstream CI workflow, https://github.com/spdx/tools-python/blob/v0.8.5/.github/workflows/install_and_test.yml | 2026-09-25; v0.8.5 | External source read | High | Direct Python 3.12 compatibility evidence |
| W8 | The official SPDX 2.3 JSON schema lists package `SPDXID`, `downloadLocation`, and `name` as required; `supplier`, `filesAnalyzed`, `licenseConcluded`, `licenseDeclared`, and `copyrightText` are typed properties but not schema-required | SPDX 2.3 JSON schema, https://github.com/spdx/spdx-spec/blob/v2.3/schemas/spdx-schema.json | 2026-09-25; SPDX 2.3 | External source read | High | Current custom “mandatory” set is stricter than the JSON schema and partly represents repository policy/quality |
| W9 | SPDX schema requires creation `created` as a string and `creators` as a non-empty array of strings | SPDX 2.3 JSON schema, https://github.com/spdx/spdx-spec/blob/v2.3/schemas/spdx-schema.json | 2026-09-25; SPDX 2.3 | External source read | High | Directly supports the current CCR finding |
| W10 | Version 0.8.3 upstream CI did not include Python 3.12; 0.8.5 adds 3.12-3.14 and drops <3.10 | Upstream CI workflows at v0.8.3 and v0.8.5 | 2026-09-25 | External source comparison | High | Prefer current stable 0.8.5 for hosted Python 3.12 |
| E1 | Local mutation trial with `spdx-tools==0.8.3` detected malformed `created`, malformed `creators`, and duplicate identifiers in output, but the CLI invocation returned status 0 for those tested cases | Temporary `/tmp/spdx-tools-research` environment and `/tmp/spdx-cases` fixtures generated from `tests/test_spdx_sbom.py` | 2026-09-25; v0.8.3 | Local empirical trial | High for 0.8.3 | Temporary evidence, not committed; 0.8.5 still requires source/hosted verification |
| W11 | Both 0.8.3 and 0.8.5 CLI implementations call `sys.exit(1)` for parsing errors, unsupported/mismatched versions, and non-empty validation messages | Official CLI source, https://github.com/spdx/tools-python/blob/v0.8.5/src/spdx_tools/spdx/clitools/pyspdxtools.py | 2026-09-25; v0.8.5 | External source read | High | Confirms fail-closed intended behavior |
| W12 | Official full-document validation covers creation info, packages, files, snippets, annotations, relationships, extracted licenses, required document relationships, and duplicate SPDX identifiers | Official document validator, https://github.com/spdx/tools-python/blob/v0.8.5/src/spdx_tools/spdx/validation/document_validator.py | 2026-09-25; v0.8.5 | External source read | High | Substantially broader than JSON Schema alone |
| E2 | Correctly captured 0.8.3 CLI statuses were 1 for malformed creation date, malformed creators, duplicate identifiers, and missing download location, and 0 for the valid fixture; a real checksum-verified Syft 1.52.0 repository SBOM passed after existing enrichment | Temporary `/tmp/spdx-tools-research`, `/tmp/spdx-cases`, `/tmp/syft-1.52.0`, and `/tmp/resume-builder-real.spdx.json` | 2026-09-25 | Local empirical trial | High | Supersedes the status interpretation in E1 |
| E3 | Python 3.12/Linux resolution for `spdx-tools==0.8.5` produced 13 wheel artifacts with stable SHA-256 digests, demonstrating that a complete binary-only hash lock is feasible | Temporary `/tmp/spdx-lock-linux312` resolution | 2026-09-25; v0.8.5 | Local dependency resolution | High | Exact hashes are transient research evidence; implementation must generate and review the committed lock |
| W13 | The strongest Marketplace alternative, `sbom-tools-action`, verifies downloaded tool checksums and provenance and supports validation/quality commands, but is not maintained by SPDX | Marketplace/action sources, https://github.com/marketplace/actions/sbom-tools-action | 2026-09-25; action v1.2.0 listing | External source read | Medium-high | Viable alternative if verified binary distribution is prioritized |
| W14 | Open issue #812 reports that tools-python accepts lowercase `primaryPackagePurpose` despite the SPDX enum requiring uppercase | SPDX tools-python issue #812, https://github.com/spdx/tools-python/issues/812 | 2026-09-25; open | GitHub issue read | High | Concrete known false negative |
| W15 | Open issue #862 reports that malformed missing `downloadLocation` can produce an uncaught traceback; empirical testing confirms the process still exits nonzero | SPDX tools-python issue #862, https://github.com/spdx/tools-python/issues/862 | 2026-09-25; open | GitHub issue and local trial | High | Diagnostic-quality problem, not fail-open behavior |

#### Contradictions and Conflicts

* Initial CLI exit-status interpretation: the first shell loop reported status 0 after errors because later argument evaluation overwrote `$?`; immediate status capture and official source showed fail-closed status 1. Resolved in favor of E2 and W11; E1 is superseded for exit behavior but retained as audit context.

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state that distinguishes sourced findings from hypotheses, partial claims, disproved claims, and unresolved possibilities.
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID and workspace-relative path with a heading or symbol; every external finding has a `W#` ID, source title, URL, retrieval date, and version when available.
* [x] Every executed cycle records Wider, Deeper, and Contrarian waves in order, synthesis, and an evidence-based re-entry decision.
* [x] Method, extensions, participation, caller direction changes, helper use, and prior-knowledge treatment are recorded with their limits.
* [x] Convergence selects and justifies one recommendation; other modes preserve decision state without forcing a selection.
* [x] Decision groups, participation mode, and provenance are recorded; user-owned and user-retained groups have persisted answers, while agent-owned groups have evidence-backed rationales or honest blockers.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content remained inert, no secrets were recorded, and the research-only write boundary held.
* Checked sections: All user-facing and Research Record sections.
* Missing or limited sections: None.
