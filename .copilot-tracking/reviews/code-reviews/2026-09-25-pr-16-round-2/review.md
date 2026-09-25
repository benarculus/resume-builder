# Code Review: PR #16 — Release pipeline, round 2

| Field | Value |
|---|---|
| Reviewer | GitHub Copilot Code Review |
| Repository | `benarculus/resume-builder` |
| Pull request | #16 |
| Base → head | `main` → `benarculus-release-pipeline-research` |
| Reviewed head | `02e79a76bfe1d33330e5195691382c8f990c870d` |
| Date | 2026-09-25 |
| Profile / depth | standard / comprehensive |
| Perspectives | functional, standards, security, readiness |
| Severity counts | Critical 0 · High 0 · Medium 4 · Low 0 |

## Summary

The release architecture has strong credential and publication boundaries: ambient permissions are disabled, App and job tokens are narrowly scoped, untrusted SBOM generation is isolated from the write-capable job, the release asset is downloaded and checksum-verified before publication, all actions are SHA-pinned, and the live main ruleset requires strict CI plus fresh human approval.

The four non-blocking findings were resolved. The SPDX validator now binds `SPDXRef-DOCUMENT` to the root package and has a negative regression test; active tag ruleset `24008744` restricts `v*` tag creation, update, and deletion to the release GitHub App; the README validation evidence is current; and the release-integrity section includes pre-publication recovery guidance.

**Verdict: Approve.**

## Changed Files Overview

| File or area | Change | Risk | Issues |
|---|---|---:|---:|
| `.github/workflows/release-please.yml` | App-token-backed release orchestration | High | 0 |
| `.github/workflows/publish-release.yml` | Draft resolution, SBOM transfer, and immutable publication | High | 1 |
| `.github/workflows/scorecard.yml` | OpenSSF Scorecard and SARIF publication | High | 0 |
| `release-please-config.json` and release state files | Simple strategy, forced tag, draft release, synchronized versions | Medium | 0 |
| `.syft.yaml` and `scripts/prepare_spdx_sbom.py` | Product-focused SPDX generation and supplier attribution | Medium | 0 |
| `scripts/validate_spdx_sbom.py` | SPDX document and runtime dependency contract | Medium | 1 |
| `scripts/validate_repo.py` | Executable workflow and supply-chain policy | Medium | 0 |
| `tests/test_spdx_sbom.py` and `tests/test_structure.py` | Positive and negative regression coverage | Medium | 0 |
| `README.md` | Release integrity and contributor validation guidance | Low | 2 |
| RPI, PR, and prior review records | Research, plan, implementation, and review evidence | Low | 0 |

## Merged Findings

### 1. Require the SPDX document to describe the root package — Resolved

- **Severity:** Medium
- **Perspective:** Functional
- **Category:** SBOM correctness
- **File:** `scripts/validate_spdx_sbom.py`
- **Lines:** 91-98

**Problem**

The validator accepts any relationship whose type is `DESCRIBES`. It does not require the relationship source to be the document SPDX ID or the target to be the `resume-builder` source package ID. An SBOM can therefore pass while the document describes a dependency or an unrelated element, contrary to the validator error and release contract.

**Current code**

```python
if not isinstance(relationships, list) or not any(
    relationship.get("relationshipType") == "DESCRIBES"
    for relationship in relationships
    if isinstance(relationship, dict)
):
    raise AssertionError("SBOM must describe its source package")
```

**Suggested fix**

Resolve `source_id` before this predicate and require:

```python
relationship.get("spdxElementId") == document["SPDXID"]
and relationship.get("relationshipType") == "DESCRIBES"
and relationship.get("relatedSpdxElement") == source_id
```

Add a negative test that redirects `DESCRIBES` to a runtime dependency.

**Resolution**

The validator now requires the exact document-to-root relationship, and `test_spdx_validator_rejects_document_describing_dependency` covers the prior false-positive case.

### 2. Protect release-tag creation with an App-only ruleset — Resolved

- **Severity:** Medium
- **Perspective:** Security
- **Category:** Release provenance
- **File:** `.github/workflows/publish-release.yml`
- **Lines:** 3-10

**Problem**

Any created `v*` tag starts the publication workflow. The workflow proves that the tag commit is reachable from `main` and that a matching draft exists, but it cannot prove that release-please and the designated GitHub App created the tag. The repository currently has two branch rulesets and no tag ruleset.

This is not a demonstrated privilege escalation: the current direct collaborator list contains only the owner with administrator permission, who can already manage releases. It is nevertheless a governance gap in the stated App-authored provenance model and becomes more important if repository write access or installed integrations expand.

**Current code**

```yaml
on:
  create:

jobs:
  generate:
    if: github.ref_type == 'tag' && startsWith(github.ref_name, 'v')
```

**Suggested fix**

Add an active tag ruleset for `v*` that restricts creation, update, and deletion, with the release GitHub App as the only normal bypass actor. Persist the live ruleset ID and verification evidence with the release architecture.

**Resolution**

Created active tag ruleset `24008744` for `refs/tags/v*`. Creation, update, and deletion are restricted, release GitHub App ID `5074470` is the sole bypass actor, and the repository owner reports `current_user_can_bypass: never`.

### 3. Refresh the documented validation and malware workflow contract — Resolved

- **Severity:** Medium
- **Perspective:** Standards
- **Category:** Documentation accuracy
- **File:** `README.md`
- **Lines:** 97-109

**Problem**

The validation description omits the release-token, draft publication, SPDX, and Scorecard policies now enforced by `scripts/validate_repo.py`. It also identifies the advisory malware workflow as `v1.0.1` at `7a825d...`, while the checked-in workflow uses `v1.0.2` at `733acb...`. Contributors cannot reliably reconcile the documented local and hosted checks with the current repository contract.

**Suggested fix**

Describe the current release, SPDX, Scorecard, dependency, and action-pin validation scope and update the reusable malware workflow version and full SHA to match the checked-in workflow.

**Resolution**

README now describes the full validation scope and references malware workflow `v1.0.2` at `733acbdf20304f70ac0c9a763921cac4c23882ef`.

### 4. Document recovery for stranded tags and draft releases — Resolved

- **Severity:** Medium
- **Perspective:** Readiness
- **Category:** Operational readiness
- **File:** `README.md`
- **Lines:** 7-9

**Problem**

The release-integrity section documents only the successful path. The publication workflow can fail before publication when draft discovery exceeds its 12 attempts at 10-second intervals, SBOM generation or validation fails, artifact transfer fails, or checksum verification fails. These states can leave a version tag and draft release for a safe rerun or manual investigation. There is no runbook describing those recovery steps, prohibited manual publication without a verified SBOM, or the immutable publication boundary.

**Suggested fix**

Add a concise recovery runbook covering:

- draft lookup timeout and safe workflow reruns,
- inspection of the version tag, draft release, and SBOM asset,
- validation, upload, and checksum failures,
- when cleanup or escalation is required,
- the prohibition on manually publishing without the verified SBOM,
- the point at which immutable publication prevents normal correction.

**Resolution**

README now documents safe reruns, draft and asset inspection, validation and checksum failure handling, escalation before deletion, the prohibition on manual publication without the verified SBOM, and the immutable point of no return.

## Positive Changes

- `permissions: {}` removes ambient repository access from both release workflows.
- The installation token is explicitly scoped to the current repository and the three release permissions it needs.
- SBOM generation is read-only; only the publication job receives `contents: write`.
- The write-capable job receives only the validated artifact, verifies the downloaded asset SHA-256, and publishes afterward.
- Supplier enrichment applies only to the repository-owned root package, avoiding false dependency attribution.
- Action pins, workflow shape, dependency pins, Scorecard settings, and release policies are guarded by executable validation and mutation tests.
- The live main ruleset has no bypass actors and requires strict `validate`, code-owner approval, stale-review dismissal, last-push separation, resolved threads, and linear history.
- Immutable releases are enabled.

## Testing Recommendations

- Add the negative `DESCRIBES`-to-dependency regression before merging the validator correction.
- After merge, treat the first complete release lifecycle as an operational acceptance test: Release PR, tag, draft release, SPDX generation, asset checksum verification, and immutable publication.
- Test the recovery runbook once with a disposable pre-publication failure or dry-run repository before relying on it for a real release.
- Verify the release App remains installed only on `resume-builder` with exactly Contents, Pull requests, and Issues write.

## Recommended Actions

1. Obtain the required qualified human approval after the fixes are pushed and hosted checks rerun.
2. Treat the first production release as the end-to-end acceptance test for App tag creation, draft discovery, SPDX publication, and immutable finalization.

## Out-of-scope Observations

- The GitHub App installation's selected-repository scope and granted permissions could not be inspected through the reviewer token.
- The tag-to-draft-to-immutable lifecycle cannot be executed end to end until the workflow is present on `main`.
- Accessibility review was omitted because no user interface or interactive end-user surface changed.

## Risk Assessment and Verdict

The reviewed design is materially stronger than the initial pipeline and does not contain an open verified finding. The four Medium findings were resolved with an exact SPDX relationship predicate and regression, an App-only release-tag ruleset, current validation documentation, and an operational recovery runbook.

All seven hosted checks pass at the exact reviewed head. The pull request is open with `mergeStateStatus: BLOCKED` and `reviewDecision: REVIEW_REQUIRED`; that is the expected live human-authorization gate and is separate from this code-review verdict.

**Final verdict: `approve`.**

## PR Comment Draft (human review required)

<!-- PR scope only. Edit freely. It is NOT posted until you check the box. -->

**Proposed event:** APPROVE

**Comment body (edit before posting):**

> The four round-two findings are resolved: SPDX validation now binds the document to the root package with a negative regression test; active ruleset `24008744` restricts `v*` tag changes to the release GitHub App; validation and malware-workflow documentation is current; and release recovery guidance covers safe reruns and immutable publication. The release pipeline is ready for qualified human approval after hosted checks complete.

- [ ] Reviewed, edited, and approved this comment for posting to the PR

## Disclaimer and Human Review

> [!CAUTION]
> **Disclaimer:** This agent is an assistive review tool only. It does not provide engineering sign-off, security certification, or compliance approval and does not replace qualified human code review, security review boards, or other professional reviewers. The output consists of AI-assisted findings, observations, and suggested remediations to support a reviewer's own analysis and decision-making. All code-review findings — including functional, standards, and accessibility observations — generated by this tool must be independently reviewed and validated by a qualified human reviewer before acting on them, merging changes, or treating any finding as resolved. Outputs from this tool do not constitute engineering approval, merge authorization, or compliance certification.

- [ ] Reviewed and validated by a qualified human reviewer
