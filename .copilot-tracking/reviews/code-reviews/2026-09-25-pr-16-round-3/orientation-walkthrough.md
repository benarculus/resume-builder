# PR #16 Round 3 Orientation Walkthrough

## Target

- Pull request: `benarculus/resume-builder#16`
- Base: `main`
- Head: `benarculus-release-pipeline-research`
- Reviewed head SHA: `8b692df05152a4091bfcb0bce27783080015caae`
- Diff: 45 files, 5,543 insertions, 15 deletions
- Profile: standard

## Map the Diff

The pull request introduces semantic release automation and then hardens the full path from a conventional commit on `main` through an App-authored Release PR, protected tag creation, draft release resolution, SPDX SBOM generation and validation, asset checksum verification, and immutable publication.

`release-please-config.json`, `.release-please-manifest.json`, and `version.txt` define the release state. The `simple` release strategy synchronizes the primary version and the plugin and marketplace consumers, creates draft releases, and forces tag creation so publication can be completed by a separate workflow.

`.github/workflows/release-please.yml` is the release-control entry point. It disables ambient permissions, mints a repository-scoped GitHub App installation token with Contents, Pull requests, and Issues write, and passes that token to a SHA-pinned release-please action. The App identity allows generated Release PR activity to exercise normal pull-request CI and branch rules.

`.github/workflows/publish-release.yml` is the publication entry point. A created `v*` tag enters a small write-capable resolver that verifies tag ancestry and locates the matching release-please draft. A dependent read-only job checks out the immutable event SHA without persisted credentials, installs the official SPDX validator from a binary-only hash lock under Python 3.12, generates an SPDX JSON SBOM with Syft, enriches repository-owned root metadata, validates official SPDX 2.3 conformance, applies the repository-specific release contract, and uploads only the validated artifact. A final contents-write job downloads the artifact, uploads it to the draft release, downloads the release asset again, verifies its SHA-256 digest, and publishes the draft.

`requirements-spdx-validation.txt` and `.github/workflows/ci.yml` establish the official validation environment. The lock exact-pins and hashes the complete `spdx-tools==0.8.5` Python 3.12/Linux resolution, and hosted CI installs it with `--require-hashes --only-binary=:all:` before running the repository and pytest suites.

`.syft.yaml`, `scripts/prepare_spdx_sbom.py`, and `scripts/validate_release_sbom_contract.py` define the SBOM content boundary. Syft excludes development, workflow, test, cache, and tracking content. The preparer identifies exactly one `resume-builder` root package and assigns its release version, supplier, and originator. Official tooling owns SPDX parsing and standard semantics; the reduced repository validator owns root identity and version, supplier policy, exact runtime packages, and document/root/runtime topology.

`scripts/validate_repo.py`, `tests/test_spdx_sbom.py`, and `tests/test_structure.py` turn the architecture into executable policy. The repository validator verifies full-SHA action pins, the exact validation lock, Python and install commands, workflow step order, permissions, release ancestry, Syft configuration, validator fail-closed behavior, artifact transfer, checksum verification, and publication. The tests exercise valid fixtures plus mutations for official SPDX failures, release-contract failures, dependency drift, runtime and install weakening, validator bypass, required-step removal, upload reordering, and obsolete-script restoration.

`.github/workflows/scorecard.yml` adds scheduled and branch-rule-triggered OpenSSF Scorecard analysis with OIDC publication, short-lived SARIF retention, and code-scanning upload. README, PR-body source, RPI artifacts, and prior review artifacts record the architecture, validation evidence, and recovery model.

## Map the Runway

1. A conventional commit reaches `main`.
2. The release-please workflow creates a short-lived, repository-scoped App token and opens or updates the Release PR.
3. The Release PR passes the repository's normal CI, code-owner review, last-push separation, resolved-thread, up-to-date, and linear-history rules.
4. Merging the Release PR updates version consumers, creates a protected `v*` tag, and creates the matching draft release.
5. The tag event starts publication; the resolver proves the event commit belongs to `main` and exports only the draft state, release ID, and version.
6. The read-only generation job installs the locked official validator, generates and enriches the SBOM, and runs official and repository validation in sequence.
7. Only the validated SBOM crosses the workflow-artifact boundary into the write-capable publication job.
8. Publication uploads the asset, re-downloads it, verifies the digest, and then publishes the immutable release.

The highest blast radius remains durable repository and release state: App credentials, installation tokens, branches, Release PRs, protected tags, draft and immutable releases, release assets, version files, workflow artifacts, and live rulesets. A pre-publication failure can leave a tag and draft release for safe retry or investigation; successful immutable publication is intentionally difficult to reverse.

## Change-Risk Evidence

| Category | State | Evidence |
|---|---|---|
| Change scope | observed | 45 files; executable behavior spans four workflows, release configuration, a dependency lock, SPDX scripts, repository validation, and large mutation suites. |
| Path criticality | observed | The change crosses credentials, authorization, tag/release mutation, dependency installation, third-party actions, shell/API input, artifact transfer, parsing, and immutable state. |
| History | observed | Twenty-seven branch commits reflect repeated trigger, authentication, version, ancestry, SPDX, and fail-closed hardening. |
| Test presence | observed | Structural policy, negative workflow mutations, official SPDX CLI tests, repository-contract tests, a checksummed Syft run, and hosted CI with 118 tests are present. |
| Coverage | unavailable | No line/branch coverage report exists, and the production tag-to-immutable-release lifecycle cannot run until the workflow lands on `main`. |
| Rollback | qualitative | Git changes are reversible; published immutable releases are not normally mutable, and failed pre-publication runs can leave durable tag/draft state. |

## Dispatch Appendix

| ID | Area | Status | Preliminary signal | Entry points / blast radius | Selectable symbols and questions |
|---|---|---|---|---|---|
| CR3-1 | Release trigger and App identity | pending | The Release PR must be created by a narrowly scoped App identity while preserving normal CI and branch governance. | `.github/workflows/release-please.yml`; release-please config; App secrets; protected `main` | `Create repository-scoped GitHub App token`, `release-please`: Are token scope, event behavior, concurrency, and Release PR lifecycle coherent? |
| CR3-2 | Tag, draft, and immutable publication lifecycle | pending | Multiple jobs coordinate protected tag provenance, ancestry, draft convergence, reruns, asset mutation, and the irreversible publish point. | `.github/workflows/publish-release.yml`; release tags; draft releases; immutable releases | `resolve`, `generate`, `publish`: Are partial states, retries, and already-published paths fail-safe and correctly bound to the event SHA/version? |
| CR3-3 | Official SPDX environment and supply-chain boundary | pending | Release validity depends on a 13-artifact PyPI lock, SHA-pinned actions, Syft output, and a strict read-only-to-write artifact boundary. | `requirements-spdx-validation.txt`; `.github/workflows/ci.yml`; `.syft.yaml`; third-party actions | `validate_spdx_validation_lock`, install steps: Are hashes, package isolation, action pins, artifact identity, and update paths reproducible without bypass? |
| CR3-4 | SBOM preparation and repository contract | pending | Official tooling and repository policy intentionally split ownership; gaps or duplication can produce false acceptance or brittle maintenance. | `prepare_spdx_sbom.py`; `validate_release_sbom_contract.py`; `requirements.txt` | `prepare_spdx_sbom`, `validate_release_sbom_contract`, `expected_runtime_packages`: Are root selection, attribution, dependency normalization, and topology checks exact for real Syft output? |
| CR3-5 | Executable policy and mutation effectiveness | pending | The validator and tests protect exact workflow shape, but exact-string contracts can miss semantic bypasses or overconstrain safe maintenance. | `scripts/validate_repo.py`; `tests/test_structure.py`; `tests/test_spdx_sbom.py` | `validate_publish_release_workflow`, `validate_spdx_validation_lock`, official mutation parameterization: Do mutations prove every critical failure path and fail for the intended reason? |
| CR3-6 | Deliverable readiness and evidence accuracy | pending | The PR includes extensive tracking and prior review artifacts alongside current docs and a green live check set. | `README.md`; `.copilot-tracking/pr/pr.md`; changes/review records; PR metadata | Are architecture claims, counts, recovery guidance, merge state, and remaining first-release acceptance work current and non-contradictory? |

Accessibility is out of scope because no user interface or interactive end-user surface changed. Security and supply-chain signals are active because the diff changes credentials, permissions, dependency locks, workflows, SBOM tooling, and release mutation.
