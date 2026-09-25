# Code Review: PR #16 — Release pipeline, round 3

| Field | Value |
| --- | --- |
| Reviewer | GitHub Copilot Code Review |
| Repository | `benarculus/resume-builder` |
| Pull request | #16 |
| Base → head | `main` → `benarculus-release-pipeline-research` |
| Reviewed head | `8b692df05152a4091bfcb0bce27783080015caae` |
| Date | 2026-09-25 |
| Profile / depth | standard / comprehensive |
| Perspectives | functional, standards, security, readiness |
| Severity counts | Critical 0 · High 0 · Medium 2 · Low 0 |

## Summary

The release pipeline has strong foundational boundaries: ambient permissions are disabled, App and job tokens are narrowly scoped, third-party actions are SHA-pinned, SPDX dependencies are hash-locked, untrusted generation is isolated in a read-only job, and the draft publication path verifies the downloaded release asset before making the release immutable.

The two Medium integrity gaps identified at the reviewed PR head are resolved in the working tree. The repository SBOM contract now preserves all package entries and requires exactly one entry at the pinned version for each runtime dependency. The already-published release shortcut now fails closed instead of inferring validated provenance from a same-name asset.

Local repository validation, focused tests, the full suite, Python compilation, and diff hygiene pass. Refreshed hosted Python 3.12/Linux CI also passed 123 tests without skips at remediation commit `4ef51c5`.

**Verdict after remediation: Approve.**

## Changed Files Overview

| File or area | Change | Risk | Issues |
| --- | --- | ---: | ---: |
| `.github/workflows/release-please.yml` | App-token-backed release orchestration | High | 0 |
| `.github/workflows/publish-release.yml` | Draft resolution, SBOM transfer, and immutable publication | High | 1 |
| `.github/workflows/ci.yml` | Hosted official SPDX validation environment | Medium | 0 |
| `requirements-spdx-validation.txt` | Hash-locked SPDX validation dependencies | High | 0 |
| `.syft.yaml` and `scripts/prepare_spdx_sbom.py` | Product-focused SPDX generation and metadata preparation | Medium | 0 |
| `scripts/validate_release_sbom_contract.py` | Repository-owned release SBOM policy | Medium | 1 |
| `scripts/validate_repo.py` | Executable workflow and supply-chain policy | Medium | 0 |
| `tests/test_spdx_sbom.py` and `tests/test_structure.py` | Official conformance and structural mutation coverage | Medium | 0 |
| `README.md` | Release integrity, recovery, and validation guidance | Low | 0 |
| `.copilot-tracking/pr/pr.md` and implementation records | PR packaging and validation evidence | Low | 0 |

## Merged Findings

### 1. Reject duplicate runtime package entries

- **Severity:** Medium
- **Perspective:** Functional
- **Category:** SBOM contract
- **File:** `scripts/validate_release_sbom_contract.py`
- **Lines:** 43-46, 63-76
- **Board items:** CR3-4, CR3-5

**Problem**

`observed_packages` is a dictionary keyed by normalized package name, so only the final entry for a name survives. A standards-valid SBOM may contain distinct package entries with the same name and different SPDX IDs. If a valid pinned entry appears after a conflicting entry, the contract ignores the earlier version and supplier. This allows ambiguous runtime metadata or dependency attribution to pass despite the exact-version and supplier policy.

The bypass was reproduced locally with a duplicate `python-docx` package carrying version `999.0` and `Organization: benarculus` before the valid `1.2.0` entry; the validator accepted the document.

**Current code**

```python
observed_packages = {
    normalized_name(package["name"]): package
    for package in packages
    if isinstance(package.get("name"), str) and package["name"]
}
```

**Suggested fix**

Preserve all entries per normalized name. Require exactly one entry for each expected runtime package at the pinned version, and evaluate supplier attribution across every package entry. Add regressions with the conflicting entry both before and after the valid entry.

**Resolution**

Resolved in the working tree. The validator now retains lists of package entries per normalized name, inspects attribution across every entry, and requires exactly one pinned entry for each expected runtime package. Four parameterized regressions cover conflicting versions and supplier attribution with the conflicting entry before and after the valid entry.

### 2. Do not accept an unverified published release as a successful run

- **Severity:** Medium
- **Perspective:** Security
- **Category:** Release integrity
- **File:** `.github/workflows/publish-release.yml`
- **Lines:** 52-59
- **Board item:** CR3-2

**Problem**

When the matching release is already public, the resolver reports `state=published` as long as an asset named `resume-builder.spdx.json` exists. That branch does not verify the asset digest or any provenance binding it to this workflow, and the downstream generation and publication jobs are skipped.

A principal with `contents: write` can therefore publish or alter the existing draft with an arbitrary same-name asset before the resolver processes the tag event. The workflow then exits successfully even though the release did not pass official SPDX validation, the repository contract, artifact transfer, or digest verification.

**Current code**

```python
if not release["draft"]:
    if "resume-builder.spdx.json" not in asset_names:
        raise SystemExit("immutable release exists without resume-builder.spdx.json")
    with open(output_path, "a", encoding="utf-8") as output:
        output.write("state=published\n")
```

**Suggested fix**

Fail closed unless the published release contains verifiable evidence binding the SBOM digest and publication to the trusted workflow run and triggering commit. Do not use filename presence alone as proof that validated publication completed. Add a regression for a published release containing a forged same-name asset.

**Resolution**

Resolved in the working tree using the fail-closed route. Published releases are no longer treated as idempotent workflow success; only matching drafts may be retried. Repository validation rejects `state=published` and asset-name-based success, and a structural mutation recreates the forged same-name asset bypass.

## Positive Changes

- `permissions: {}` removes ambient repository access from release workflows.
- Release-please uses a short-lived repository-scoped App token with explicit permissions.
- Action pins and the dedicated SPDX environment are protected by executable repository validation.
- SPDX conformance and repository policy are cleanly separated, and both gates precede artifact upload.
- Generation is read-only; only the publication job receives `contents: write`.
- The normal draft path downloads and SHA-256-verifies the uploaded release asset before publication.
- Structural mutations cover dependency drift, installation weakening, validator bypass, gate ordering, and required-step removal.
- Documentation describes recovery, safe reruns, and the immutable point of no return.

## Testing Recommendations

- [x] Added duplicate-runtime-name contract mutations for conflicting versions and supplier attribution in both package orders.
- [x] Added a resolver mutation for an already-published release with a forged same-name SBOM.
- [x] Refreshed hosted Python 3.12/Linux suite passed 123 tests without skips. The Linux-only hash lock also correctly prevented a macOS ARM installation from substituting unreviewed wheels.
- [ ] Treat the first complete tag-to-draft-to-immutable release as the operational acceptance test, including SBOM validation and asset checksum verification. This requires the workflow to be merged to `main`.

## Recommended Actions

1. Obtain qualified human approval before merge.
2. Treat the first production release as the end-to-end operational acceptance test.

## Out-of-scope Observations

- Accessibility review was omitted because no user interface or interactive end-user surface changed.
- The tag-to-draft-to-immutable lifecycle cannot run end to end until the workflow is present on `main`.
- Live GitHub App installation scope and granted permissions were not independently inspected in this round.

## Recommended Specialist Follow-up Reviews

| Concern | Signals | Backing | Availability | Suggested action |
| --- | --- | --- | --- | --- |
| Supply-chain security | Hash lock, pinned Actions, Syft, SBOM gates, artifact transfer, immutable publication | `supply-chain-security` skill | Available | Optional focused follow-up after remediation if independent assurance beyond the standards and security perspectives is desired. |

## Risk Assessment and Verdict

The architecture substantially reduces credential, dependency, and artifact risk. Both findings are resolved, focused regressions pass locally, and all seven refreshed hosted checks pass at the remediation commit.

The pull request is open and mergeable, but `mergeStateStatus: BLOCKED` and `reviewDecision: REVIEW_REQUIRED`. The code-review verdict independently remains:

**Final verdict after remediation: `approve`.**

## PR Comment Draft (human review required)

<!-- PR scope only. Edit freely. It is NOT posted until you check the box. -->

**Proposed event:** APPROVE

**Comment body (edit before posting):**

> The two round-three findings are resolved. The release contract rejects duplicate runtime entries in either package order, and already-published releases fail closed instead of treating a same-name asset as validated provenance. Focused and full local validation pass, and refreshed hosted Python 3.12/Linux CI reported 123 passed without skips. The change is ready for qualified human approval.

- [x] Reviewed, edited, and approved this comment for posting to the PR

## Disclaimer and Human Review

> [!CAUTION]
> **Disclaimer:** This agent is an assistive review tool only. It does not provide engineering sign-off, security certification, or compliance approval and does not replace qualified human code review, security review boards, or other professional reviewers. The output consists of AI-assisted findings, observations, and suggested remediations to support a reviewer's own analysis and decision-making. All code-review findings — including functional, standards, and accessibility observations — generated by this tool must be independently reviewed and validated by a qualified human reviewer before acting on them, merging changes, or treating any finding as resolved. Outputs from this tool do not constitute engineering approval, merge authorization, or compliance certification.

- [x] Reviewed and validated by a qualified human reviewer
