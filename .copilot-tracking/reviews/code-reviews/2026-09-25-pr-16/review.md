# Code Review: PR #16 — Release pipeline

| Field | Value |
|---|---|
| Reviewer | GitHub Copilot Code Review |
| Repository | `benarculus/resume-builder` |
| Pull request | #16 |
| Base → head | `main` → `benarculus-release-pipeline-research` |
| Reviewed head | `575e3b9ce82021d051062eba92eee2c57511e3a9` |
| Date | 2026-09-25 |
| Profile / depth | standard / comprehensive |
| Perspectives | functional, standards, security, readiness, supply-chain |
| Severity counts | Critical 0 · High 2 · Medium 4 · Low 1 |
| Open severity counts | Critical 0 · High 0 · Medium 0 · Low 0 |

## Summary

The release workflow remains functionally sound: it disables the default `GITHUB_TOKEN`, mints a repository-scoped installation token from SHA-pinned code, requests only the release permissions it uses, serializes mutations, and passes the ephemeral token to release-please. The three documentation findings were corrected.

The focused supply-chain review found four actionable gaps and all were remediated. The live ruleset now requires one fresh code-owner approval, last-push separation, resolved review threads, strict required checks, and no bypass actors. Release-please now creates a draft and version tag; a separate least-privilege workflow generates, validates, uploads, and checksum-verifies an SPDX 2.3 SBOM before publishing. Immutable releases then lock the tag/assets and generate native release attestations. A SHA-pinned OpenSSF Scorecard workflow publishes OIDC-authenticated results and uploads SARIF to code scanning, with executable policy tests guarding the configuration.

**Verdict: Approve.**

## Changed Files Overview

| File | Change | Risk | Issues |
|---|---|---:|---:|
| `.github/workflows/release-please.yml` | App-token-backed release workflow | High | 0 |
| `.github/workflows/publish-release.yml` | Draft release, SPDX generation, checksum verification, immutable publication | High | 0 |
| `release-please-config.json` | Release strategy and version updaters | Medium | 0 |
| `.syft.yaml` | Product-focused SBOM scan configuration | Medium | 0 |
| `.release-please-manifest.json` | Current release version | Medium | 0 |
| `version.txt` | Simple-strategy primary version | Low | 0 |
| `scripts/validate_repo.py` | Hardened workflow contract validation | Medium | 0 |
| `scripts/prepare_spdx_sbom.py` | Root product supplier enrichment | Medium | 0 |
| `scripts/validate_spdx_sbom.py` | SPDX and runtime dependency validation | Medium | 0 |
| `tests/test_structure.py` | Positive and negative regression tests | Medium | 0 |
| `tests/test_spdx_sbom.py` | SPDX preparation and rejection regressions | Medium | 0 |
| `.copilot-tracking/plans/2026-09-22/release-pipeline-plan.md` | Authoritative plan and acceptance contract | Low | 1 |
| `.copilot-tracking/reviews/logs/2026-09-22/release-pipeline-review.md` | Prior implementation review | Low | 1 |
| `.copilot-tracking/research/2026-09-22/release-pipeline-research.md` | Release-tool research record | Low | 1 |
| `.copilot-tracking/changes/2026-09-22/release-pipeline-changes.md` | Implementation evidence | Low | 0 |
| `.copilot-tracking/reviews/plans/2026-09-22/release-pipeline-plan-critique.md` | Plan critique evidence | Low | 0 |
| `.copilot-tracking/pr/pr.md` | PR description source | Low | 0 |

## Merged Findings

### 1. Reconcile NFR-001 with the App-token permissions model — Resolved

- **Severity:** Medium
- **Perspective:** Standards
- **Category:** Contract consistency
- **File:** `.copilot-tracking/plans/2026-09-22/release-pipeline-plan.md`
- **Lines:** 445-446

**Problem**

NFR-001 still requires the workflow's top-level `permissions:` block to contain `contents: write`, `pull-requests: write`, and `issues: write`. The final workflow and P02-T01 binding contract intentionally require `permissions: {}` and grant those capabilities only to the short-lived App token. The plan therefore contains two mutually exclusive acceptance contracts for the same requirement.

**Current text**

```markdown
NFR-001: The new release workflow's declared GitHub Actions `permissions`
are the minimum needed (`contents: write`, `pull-requests: write`,
`issues: write`) ...
```

**Suggested fix**

Rewrite NFR-001 and its objective threshold to require top-level `permissions: {}`, plus a GitHub App installation token scoped to the current repository and exactly Contents/Pull requests/Issues write.

**Resolution**

NFR-001 now records the empty ambient-permission model and exact ephemeral App-token scope.

### 2. Update the final acceptance table to the current release design — Resolved

- **Severity:** Medium
- **Perspective:** Readiness
- **Category:** Deliverable readiness
- **File:** `.copilot-tracking/reviews/logs/2026-09-22/release-pipeline-review.md`
- **Lines:** 116-121

**Problem**

The acceptance table certifies deleted ruleset `23850509`, claims three top-level workflow write permissions, and says the workflow has no explicit token. The current state uses consolidated ruleset `23698833`, `permissions: {}`, and an explicit ephemeral App-token handoff. This section presents final acceptance coverage, so the evidence is materially stale rather than merely historical.

**Suggested fix**

Update FR-005/P03-T01 to the current `Protect main` ruleset and update NFR-001/P02-T01 to the empty default permissions plus repository-scoped App-token contract.

**Resolution**

The acceptance table now identifies ruleset `23698833`, `permissions: {}`, and the explicit App-token handoff.

### 3. Remove the superseded default-token conclusion from the research record — Resolved

- **Severity:** Low
- **Perspective:** Standards
- **Category:** Documentation accuracy
- **File:** `.copilot-tracking/research/2026-09-22/release-pipeline-research.md`
- **Lines:** 75-81, 226

**Problem**

The post-CCR correction says an App token is required so the generated Release PR can trigger CI, but the adjacent rationale and W3 evidence note still conclude that no elevated token is needed because there is no publish step. Those statements conflate downstream release-event workflows with CI on the generated PR.

**Suggested fix**

Retain the historical source observation but update its disposition: a non-`GITHUB_TOKEN` identity is required for Release PR CI even though the repository has no downstream publish workflow.

**Resolution**

The research rationale and W3 evidence disposition now distinguish generated-PR CI from downstream release workflows.

## Supply-Chain Findings

### SSSC-001. Release credential workflows could merge without human approval — Resolved

- **Severity:** High
- **Evidence:** The live ruleset previously required zero approvals.
- **Resolution:** One fresh code-owner approval is now required; stale approvals are dismissed; the last pusher cannot provide the required approval; review threads must be resolved; required checks are strict; bypass actors remain empty.

### SSSC-002. Published release tags and assets were mutable — Resolved

- **Severity:** High
- **Evidence:** Repository release immutability was not enabled.
- **Resolution:** Immutable releases are enabled. Future release tags and assets are locked after publication and receive GitHub's cryptographic release attestation.

### SSSC-003. No continuous OpenSSF Scorecard assessment — Resolved

- **Severity:** Medium
- **Evidence:** No Scorecard workflow existed.
- **Resolution:** Added `.github/workflows/scorecard.yml` with full-SHA action pins, read-only defaults, minimal SARIF/OIDC writes, public result publishing, short-lived SARIF retention, code-scanning upload, and structural regression tests.

### SSSC-004. Published releases lacked a distributable SPDX SBOM — Resolved

- **Severity:** Medium
- **Evidence:** Immutable publication previously occurred without a repository-specific SBOM asset.
- **Resolution:** Release-please creates a draft and version tag. The tag workflow generates SPDX 2.3 under read-only permissions, validates the product/version and exact runtime pins, passes only the validated artifact into the contents-write job, verifies the uploaded SHA-256 digest, and publishes the immutable release.

## Acceptance Criteria Coverage

| Requirement | Status | Notes |
|---|---|---|
| FR-001 | Implemented | Config, manifest, and primary version file exist at the root. |
| FR-002 | Partial | JSON paths are configured correctly; no Release PR merge has exercised them. |
| FR-003 | Implemented | Push-to-main workflow invokes release-please with an App installation token. |
| FR-004 | Partial | Action is configured to tag and create the release; behavior awaits the first Release PR merge. |
| FR-005 | Implemented | Live `Protect main` ruleset contains `required_linear_history`. |
| NFR-001 | Implemented | Workflow and durable documentation require empty default permissions and a down-scoped App token. |

## Positive Changes

- Both actions are pinned to full verified commit SHAs with version comments.
- `permissions: {}` removes ambient repository access from the workflow's default token.
- The installation token is explicitly limited to the current repository and three required permissions.
- The token action's default post-job revocation remains enabled.
- The App is not a ruleset bypass actor; the live rulesets require `validate` and the advisory-malware check.
- One fresh human code-owner approval, last-push separation, resolved review threads, and an up-to-date branch are required.
- Future GitHub Releases are immutable and receive native release attestations.
- Every future release includes a validated `resume-builder.spdx.json` asset before immutable publication.
- OpenSSF Scorecard continuously reports supply-chain posture to code scanning and the public Scorecard service.
- The validator turns the security contract into executable policy, and negative tests cover two meaningful weakening attempts.
- All hosted checks passed on the reviewed head and the PR is cleanly mergeable.

## Testing Recommendations

- After merge, verify the first `release-please` run successfully mints the App token and creates the expected Release PR.
- Confirm that the App-authored Release PR triggers `validate` and `Advisory Malware Check / check`, and cannot merge while either required check is failing.
- Inspect the first generated PR to confirm `version.txt`, `plugin.json`, both marketplace version fields, and `CHANGELOG.md` receive the same proposed version.
- Periodically rotate the App private key and verify the workflow after rotation.

## Recommended Actions

1. Treat the first post-merge release workflow, generated Release PR, draft release, SBOM attachment, and immutable publication as the end-to-end acceptance test.

## Out-of-scope Observations

- The reviewer could confirm both credential names exist but could not read App installation settings with the available user token. Verify in the GitHub App UI that installation scope is limited to `resume-builder` and that the App itself grants only Contents/Pull requests/Issues write.
- Secret-scanning non-provider patterns and validity checks remained unavailable/disabled after a repository API update attempt; provider-pattern scanning and push protection remain enabled.

## Recommended Specialist Follow-up

| Concern | Signals | Backing | Availability | Action |
|---|---|---|---|---|
| Supply chain / SSSC | CI workflow, new third-party action, automated tag and GitHub Release creation | supply-chain-security skill | completed | Findings persisted in `supply-chain-findings.json`; all actionable findings resolved. |

## Risk Assessment and Verdict

Runtime risk is moderated by strong token boundaries, full-SHA action pins, executable contract validation, mandatory fresh human review, strict CI, immutable release attestations, continuous Scorecard monitoring, and no bypass actors. Residual uncertainty is operational: the App installation configuration and the first real release lifecycle cannot be exercised from this PR.

**Final verdict: `approve`.**

## PR Comment Draft (human review required)

<!-- PR scope only. Edit freely. It is NOT posted until you check the box. -->

**Proposed event:** COMMENT

**Comment body (edit before posting):**

> The release flow and its supply-chain controls now look ready for human approval. The documentation drift is resolved; the ruleset requires fresh code-owner approval, last-push separation, resolved threads, strict CI, and no bypass; release-please creates a draft and tag so a validated SPDX 2.3 SBOM can be checksum-verified before immutable publication; and OpenSSF Scorecard is SHA-pinned, policy-validated, and uploads SARIF to code scanning. The remaining acceptance step is the first post-merge release lifecycle.

- [ ] Reviewed, edited, and approved this comment for posting to the PR

## Disclaimer and Human Review

> [!CAUTION]
> **Disclaimer:** This agent is an assistive review tool only. It does not provide engineering sign-off, security certification, or compliance approval and does not replace qualified human code review, security review boards, or other professional reviewers. The output consists of AI-assisted findings, observations, and suggested remediations to support a reviewer's own analysis and decision-making. All code-review findings — including functional, standards, and accessibility observations — generated by this tool must be independently reviewed and validated by a qualified human reviewer before acting on them, merging changes, or treating any finding as resolved. Outputs from this tool do not constitute engineering approval, merge authorization, or compliance certification.

- [ ] Reviewed and validated by a qualified human reviewer
