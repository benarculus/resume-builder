# PR #16 Round 2 Orientation Walkthrough

## Target

- Pull request: `benarculus/resume-builder#16`
- Base: `main`
- Head: `benarculus-release-pipeline-research`
- Reviewed head SHA: `02e79a76bfe1d33330e5195691382c8f990c870d`
- Diff: 29 files, 2,787 insertions, 13 deletions
- Profile / depth: standard / comprehensive

## Map the Diff

The PR establishes semantic release automation and then layers repository governance, supply-chain monitoring, and SPDX publication around it.

`release-please-config.json`, `.release-please-manifest.json`, and `version.txt` define the release state. The manifest uses the `simple` strategy, synchronizes `plugin.json` plus two marketplace version fields, creates draft releases, and forces tag creation so a second workflow can complete publication.

`.github/workflows/release-please.yml` is the release-control entry point. A push to `main` disables ambient `GITHUB_TOKEN` access, exchanges the App Client ID and private key for a repository-scoped installation token with Contents, Pull requests, and Issues write, and passes that token to the SHA-pinned release-please action.

`.github/workflows/publish-release.yml` is the publication entry point. A created `v*` tag starts a read-only generation job. That job checks out the tag without persisted credentials, verifies the tag commit is an ancestor of `main`, polls for the matching draft release, generates SPDX JSON with Syft, enriches only the repository-owned root package, validates the document and runtime pins, and uploads a one-day workflow artifact. A separate contents-write job downloads that artifact, uploads it to the draft release, downloads it through the release-assets API, compares SHA-256 digests, and publishes the draft. If a rerun sees a published release, the resolution step accepts it only when the expected SBOM asset already exists.

`.syft.yaml`, `scripts/prepare_spdx_sbom.py`, and `scripts/validate_spdx_sbom.py` define the SBOM content contract. Tracking, workflow, test, cache, and development-requirement paths are excluded. The preparer assigns supplier and originator only to the `resume-builder` source package. The validator requires SPDX 2.3 metadata, a unique namespace, creation metadata, package identifiers and suppliers, the release version, exact runtime pins, no dependency misattribution, a document `DESCRIBES` relationship, and source-to-runtime relationships.

`.github/workflows/scorecard.yml` adds scheduled and branch-rule-triggered OpenSSF Scorecard analysis with OIDC publication, short-lived SARIF artifacts, and code-scanning upload.

`scripts/validate_repo.py`, `tests/test_structure.py`, and `tests/test_spdx_sbom.py` turn the workflow and SBOM designs into executable repository policy. The tests cover accepted shapes and selected weakening mutations. The README, PR description source, RPI records, and persisted review artifacts describe the current release and governance model.

## Map the Runway

1. A conventional commit reaches `main`.
2. The release-please workflow mints a short-lived App installation token and opens or updates the Release PR.
3. The App-authored Release PR follows normal CI and human-review rules because it is not using `GITHUB_TOKEN`.
4. Merging the Release PR updates release state, creates a `v*` tag immediately, and creates the matching GitHub Release as a draft.
5. The tag `create` event starts the SPDX workflow.
6. The read-only job waits for the draft, generates and validates the SBOM, and places only that file into the cross-job artifact boundary.
7. The contents-write job attaches and checksum-verifies the SBOM, then publishes the release.
8. Repository release immutability locks the published tag and asset and produces GitHub's release attestation.

The highest blast radius is durable repository state: App credentials, branches, PRs, tags, draft releases, immutable releases, release assets, changelog/version files, workflow artifacts, and live rulesets. A failure before the final publish can leave a tag and draft release for retry or manual recovery. A successful immutable publication is intentionally difficult to reverse.

## Change-Risk Evidence

| Category | State | Evidence |
|---|---|---|
| Change scope | observed | 29 files; executable behavior spans three workflows, release configuration, two SPDX scripts, repository validation, and tests. |
| Path criticality | observed | The change crosses secrets, authorization, tag/release mutation, shell/API input, artifact transfer, parsing, and immutable-state boundaries. |
| History | observed | Thirteen commits reflect repeated trigger, authentication, governance, and publication redesign. |
| Test presence | observed | Exact structural validators, mutation tests, SPDX unit tests, a real checksummed Syft run, and hosted CI are present. |
| Coverage | unavailable | The tag-to-draft-to-immutable lifecycle has not executed on GitHub because the workflow is not on `main`. |
| Rollback | qualitative | Git changes are reversible; tags, drafts, App configuration, rulesets, and immutable publication require separate operational recovery. |

## Dispatch Appendix

| ID | Area | Status | Preliminary signal | Entry points / blast radius | Questions |
|---|---|---|---|---|---|
| CR2-1 | Tag and draft-release lifecycle | pending | Tag creation and draft creation occur inside release-please while a separate workflow polls for convergence. | `release-please-config.json`; `.github/workflows/publish-release.yml`; tags and draft releases | Are event ordering, retries, missing drafts, existing drafts, and already-published releases handled without silent partial state? |
| CR2-2 | Cross-job SBOM trust boundary | pending | Untrusted repository content and a third-party generator run in a read-only job; only the generated artifact crosses into a write-capable job. | `generate` and `publish` jobs; workflow artifacts; release assets | Can repository-controlled content or artifact substitution affect the write job, release identity, or asset verification? |
| CR2-3 | SPDX content contract | pending | The preparer and validator enrich and enforce product, dependency, supplier, identifier, and relationship data. | `.syft.yaml`; `prepare_spdx_sbom.py`; `validate_spdx_sbom.py`; release consumers | Does the output meet the declared SPDX/NTIA contract without false attribution, omitted runtime components, or unstable assumptions about Syft output? |
| CR2-4 | App token and release permissions | pending | The first workflow uses App credentials; the second uses job-scoped `GITHUB_TOKEN` permissions. | App secrets; installation token; contents-write publication | Are the permission boundaries minimal and are credentials or write capabilities exposed to code that should remain read-only? |
| CR2-5 | Executable policy and regression tests | pending | Exact validators protect workflow shape but may encode incomplete assumptions or miss semantic bypasses. | `validate_repo.py`; `test_structure.py`; `test_spdx_sbom.py` | Do tests cover material failure and recovery paths, and can safe maintenance occur without weakening the intended guarantees? |
| CR2-6 | Governance and deliverable readiness | pending | Claims depend on live rulesets, immutable-release settings, green checks, and documentation that has evolved through multiple designs. | PR metadata; ruleset `23698833`; review records; README | Does the current package accurately represent the final architecture, validation evidence, remaining operational setup, and merge blockers? |

Accessibility is out of scope because no user interface or interactive end-user surface changed.
