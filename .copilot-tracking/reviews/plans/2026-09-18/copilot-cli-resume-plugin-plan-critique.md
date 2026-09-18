<!-- markdownlint-disable-file -->
# RPI Plan Critique: Copilot CLI resume-building plugin

## Metadata

* Task ID: copilot-cli-resume-plugin
* Critique date: 2026-09-18
* Plan: .copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md
* Critique execution status: Complete
* Critique depth: standard
* Depth provenance: default
* Invocation consumed: yes
* Attempt ID and kind: copilot-cli-resume-plugin-critique-01, kind=initial
* Candidate identity and saved hash boundary: task `copilot-cli-resume-plugin`; plan-content sha256 `47f92ef2b8fabbbf6d63f4b57a636d17c5eac813ce757b04f08c0a17b0d3a080`; reservation boundary as recorded in the plan's `## Critique Disposition`
* Current-dispatch provenance: immediate, uninterrupted parent dispatch from the standalone `rpi-plan` planner for the just-reserved initial critique attempt to `.copilot-tracking/reviews/plans/2026-09-18/copilot-cli-resume-plugin-plan-critique.md`
* Original attempt and recovery approval: not applicable — initial attempt, no recovery approval in scope

## Inputs and Criterion Boundary

* Task context and caller requirements: assess the complete plan against its own Goals, Scope and Non-Goals, FR-001..FR-006, NFR-001..NFR-004, Risks and Open Questions, and Planning Decisions and Feedback D1..D5; prioritize implementation blockers, contradictions, missing dependencies, unsupported scope or architecture claims, and material risks; do not edit the plan.
* Research and evidence considered: `.copilot-tracking/research/2026-09-18/copilot-cli-resume-plugin-research.md`
* Decisions, dependencies, task Goals, and task Requirements considered: confirmed user decisions D1-D4, deferred D5, phase/task dependencies P01-P05, the shared anti-fabrication and schema strategy, the dual-install packaging goal, and the three-skill artifact pipeline.
* Assessment boundary: this critique evaluates only the supplied plan and supplied research evidence. It can judge internal consistency, evidence support, and implementation readiness, but it cannot confirm runtime behavior because no implementation artifacts or validation outputs were supplied.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| Goals; FR-001; FR-003; NFR-001; D4 | Partial | The plan consistently carries the anti-fabrication rule and shared-contract intent, but the data-model fit concern from research W3 remains deferred instead of being resolved before downstream tasks depend on the shared contract. |
| FR-002; NFR-002; D1; W4 | Covered | P03 constrains ingestion to one user-supplied link at a time through browser/computer-use tooling and rejects crawling/bypass behavior, matching the evidence-backed risk posture in research. |
| FR-004; W7 | Covered | P04-T02 specifies a portable `python-docx` script and P05-T02 includes a smoke test against a representative payload. |
| FR-005; NFR-004; D2; W2; W6; C1; C2 | Missing | The plan's primary plain-skills layout is nested under `.github/skills/resume-builder/<skill>/SKILL.md`, while the supplied research's official contract evidence is `.github/skills/<skill-name>/SKILL.md`; the plan asserts compatibility without supplied evidence. |
| FR-006; P03-T01; P04-T01; W3 | Partial | The career-document contract is defined, but the `job-requirements` artifact has no pinned shared schema/template even though the resume drafter must parse it deterministically. |
| Planning Readiness and Next Step; Critique Disposition | Missing | The plan claims a latest critique `Pass` and passed gates before this critique existed, while its own `## Critique Disposition` still recorded `started` with pending disposition. |
| D5; Scope and Non-Goals | Covered | Visual resume-formatting details are correctly treated as implementer judgment rather than a blocked design decision. |

## Verdict

* Verdict: Revise
* Rationale: The plan is directionally strong, but it is not yet credible for implementation as written because it relies on an unsupported plain-skills directory claim, leaves the planner→drafter artifact interface underspecified, and prematurely marks the critique gate as passed before the critique existed.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: The plain-skills install path depends on an unsupported nested discovery layout

* Related IDs: FR-005, NFR-004, P01-T01, P01-T02, P05-T01, P05-T02, D2, W2, W6, C2
* Evidence: `.copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md` (`P01-T01` directory layout and compatibility claim; `P01-T02` README/install requirements); `.copilot-tracking/research/2026-09-18/copilot-cli-resume-plugin-research.md` (`GitHub Copilot CLI's real extensibility surface...`; Evidence W2/W6)
* Concern: The plan's "plain Agent Skills" path is `.github/skills/resume-builder/career-document-builder/SKILL.md` (and peers), but the supplied official-discovery evidence names `.github/skills/<skill-name>/SKILL.md`. The plan treats the extra namespace layer as safe based on the installed `hve-core` bundle pattern, yet the research also says that bundle pattern is app-specific and not GitHub-official. As written, the plan does not supply evidence that the nested layout preserves the standards-based install path it calls the primary portable option.
* Impact: If the nested layout is not recognized by the plain-skills loader, the repo would fail its most important portability promise: FR-005's standard install path and NFR-004's README-only user onboarding.
* Smallest useful change: Revise the repository layout and related tasks to use an evidence-backed plain-skills structure for each skill (or explicitly downgrade the plain-skills portability claim and treat the nested structure as bundle-specific only).
* Action owner: planning parent
* Exact resolving evidence: The revised plan shows an official-contract-compatible plain-skills path for all three skills, updates P01/P05 validation around that path, and removes any unsupported claim that the extra namespace layer is standards-compatible unless new supplied evidence explicitly proves it.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [High]: The planner→drafter artifact interface is underspecified even though FR-006 depends on deterministic parsing

* Related IDs: FR-003, FR-006, P03-T01, P04-T01, P05-T02
* Evidence: `.copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md` (`P03-T01` allows "plain Markdown or lightweight JSON" as long as it is structured enough; `P04-T01` requires the resume-drafter to parse upstream outputs)
* Concern: The plan establishes one shared contract for the career document but not for the `job-requirements` artifact. P03 leaves the output format open-ended, while P04 assumes deterministic consumption of that artifact. This leaves a load-bearing integration point to implementer discretion without a canonical schema, template, or validation target.
* Impact: The resume-drafter can only enforce its anti-fabrication mapping logic if the requirements artifact has a stable machine-readable structure. Without a pinned interface, implementation can drift into brittle prompt parsing or incompatible assumptions between skills, undermining FR-003 and FR-006.
* Smallest useful change: Add a shared `job-requirements` contract (schema or fixed template) under the repo's references/templates, require P03 to emit it, require P04 to consume it, and add a P05 validation check against that contract.
* Action owner: planning parent
* Exact resolving evidence: The revised plan introduces one named shared artifact contract for `job-requirements`, cites it from both P03 and P04, and extends P05-T02 to validate at least one representative producer/consumer example against it.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-003 -->
### PC-003 [Medium]: The plan claims critique-pass readiness before the critique gate actually completed

* Related IDs: Planning Readiness and Next Step, Critique Disposition
* Evidence: `.copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md` (`Planning Readiness and Next Step` says latest critique `Pass` and required gates `passed`; `## Critique Disposition` still records `Critique execution: started` and a fully pending disposition table); caller-supplied critique output path was absent at assessment start
* Concern: The plan's readiness and gate state were advanced as if critique had already passed, even though the plan's own disposition section still marked the critique as merely started and no critique artifact existed yet.
* Impact: This undermines trust in the plan's gating and could push implementation forward on an artifact that had not actually cleared critique.
* Smallest useful change: Update the plan's readiness, gate, and latest-critique fields only after this critique artifact exists and its actual verdict has been incorporated.
* Action owner: planning parent
* Exact resolving evidence: The revised plan's readiness block, critique disposition block, and linked critique artifact all agree on the same final execution status and verdict.
* Decision route: direct planner correction

## Strengths and Residual Risk

* The plan is otherwise well-grounded on the user-confirmed anti-fabrication posture, dual packaging intent, and one-link browser-ingestion constraint; the remaining residual LinkedIn ToS/legal exposure is already surfaced honestly as a user-owned risk rather than hidden inside implementation tasks.

## Questions or Blocking Evidence Gaps

* none

## Limitations

* This assessment was limited to the supplied plan and supplied research artifact. No implementation outputs, validation logs, or runtime proofs were available.
* The caller constrained file reads to the supplied plan/evidence and critique instructions/template, so parent-dispatch provenance was assessed from caller-supplied context plus the plan's own `## Critique Disposition` rather than an independently supplied planning-reference pointer.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning parent
* Smallest next action: revise the plan to use an evidence-backed plain-skills discovery layout, then add the missing `job-requirements` artifact contract and correct the readiness/disposition gate state in the same revision.
* User response required: no
