<!-- markdownlint-disable-file -->
# Task Research: copilot-cli-resume-plugin

| Field              | Value                      |
|--------------------|----------------------------|
| Date               | 2026-09-18                 |
| Researcher / agent | rpi-research               |
| Output mode        | analysis                   |

## Executive Summary

* Bottom line: A resume-building "GitHub Copilot CLI plugin" is realistically a Git repository that ships three Agent Skills (`.github/skills/*/SKILL.md`) following the official, cross-platform Agent Skills open standard, plus an optional `hve-core`-style `.github/plugin/marketplace.json` manifest so the same repo can also be installed as a named plugin bundle. Nothing about the three skills (career-document builder, job-requirements planner, resume drafter) requires a new extensibility mechanism — the format, install paths, and safety controls already exist and are documented. Because the user now intends to publish this repository publicly, it must also carry the standard community-health assets (license, contributing guide, code of conduct, security policy, issue/PR templates) and the free, public-repo-scoped GitHub hardening features (secret scanning with push protection, Dependabot alerts/updates, CodeQL code scanning, branch protection, CODEOWNERS) — all of which GitHub documents and, for public repositories, largely provides at no cost. Test coverage should center on `pytest` for the one piece of real code (the `.docx`-generation script), with the `hve-core` reference repo showing that skill-content behavior is better validated through scenario-style eval/conformance checks than conventional unit tests.
* Why this matters: Building on the documented Agent Skills spec means the repo works in Copilot CLI, VS Code, JetBrains, and Copilot cloud agent without extra plumbing, and it can be installed as project skills (`.github/skills`), personal skills (`~/.copilot/skills`), or via a marketplace-style bundle like the one this session already has installed (`hve-core`). Publishing publicly changes the risk surface: strangers can open issues/PRs, fork the repo, and (if secrets or unsafe defaults exist) misuse it, so the community and security assets are not optional polish — they are the standard, low-cost baseline GitHub itself recommends and partly automates for public repos.
* Research status: Complete for the packaging, distribution, job-data-acquisition, public-repo-hardening, community-asset, and test-coverage questions that gate planning. Two areas remain inherently judgment calls rather than fully research-resolvable: LinkedIn's automated-access terms (policy-dependent, evidence-backed as a standing risk) and how strict branch-protection/review rules should be for a repository that may start with a single maintainer (a proportionality call, not a factual gap).
* Confidence and uncertainty: High confidence on the skill/plugin packaging model, the free-tier availability of GitHub's core public-repo security features, and the community-health-file checklist (all primary GitHub documentation, cross-checked against the `hve-core` plugin already installed in this environment, which demonstrates every one of these assets working in a real public repo). Medium confidence on job-schema and DOCX-library choices (well-established open-source projects, not GitHub-specific standards) and on how much eval/behavioral testing (versus plain `pytest`) is proportionate for a small, new repo. The user has already resolved the decisions that most affected direction (see Decisions and Feedback).

## What You May Not Know

* The Agent Skills format (`SKILL.md` + YAML frontmatter) is an **open, cross-vendor standard** (agentskills.io / `github.com/agentskills`), not a GitHub-only convention — the same skill folder works unmodified in Copilot CLI, VS Code, JetBrains, and Copilot cloud agent (W1).
* GitHub does not currently document an official "plugin marketplace" format for Copilot CLI; the `marketplace.json` bundling pattern is an `hve-core`-specific convention this app's `install_extension`/`share_extension` tooling understands (C1), not a GitHub-published spec. Shipping one is still reasonable — it just is not required by GitHub's own skill-discovery mechanism, which works from plain `.github/skills` directories or `gh skill install` (W2).
* JSON Resume, an existing MIT-licensed open standard, already defines both a resume schema and a companion job-description schema (W3). Reusing or aligning the "machine-friendly career document" with JSON Resume's schema would give the plugin interoperability with an existing ecosystem of parsers/renderers instead of inventing a bespoke format from scratch.
* LinkedIn's User Agreement treats automated/bulk data collection as a prohibited "Don't," and the well-known *hiQ Labs v. LinkedIn* litigation shows this area is legally contested and evolving, not settled in scrapers' favor (W4). The user's chosen approach (CLI browser/computer-use tooling opens a user-supplied link and extracts the rendered page, one link at a time, human-directed) is materially different from bulk/automated scraping and lower risk, but is not a legal opinion and should still avoid: scraping other people's private data, bulk/automated crawling, or storing more than the single posting the user points to.
* GitHub enables several of its strongest security features **for free on every public repository**, regardless of plan: secret scanning (plus push protection that blocks a commit before a secret ever lands in history), Dependabot alerts and security updates, the dependency graph, CodeQL code scanning, and an SBOM export are all "available for public repos" per GitHub's own security-features overview, not gated behind GitHub Advanced Security purchase the way they are for private repos (W8). This means "sufficiently hardened" for this project is mostly a matter of turning features on and adding a few config files, not buying anything.
* GitHub's "community profile" checklist is the de-facto public checklist for what a healthy open-source repo should ship: README, `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, a security policy, and issue/PR templates in `.github/ISSUE_TEMPLATE/` (W9). The `hve-core` plugin already installed in this environment ships every one of these files plus a `CODEOWNERS` file and a scheduled `Dependabot` config (C3–C6), so this repo has a directly inspectable, working template to copy rather than needing to invent the pattern.
* Classic branch protection rules (require pull request review, require status checks, block force-push/deletion) are a standard, no-extra-cost GitHub feature available on personal/public repositories, not restricted to paid organization plans; the newer "rulesets" feature layers on top but is not required to get baseline protection (W10). For a repo that may start with one maintainer, "require an approving review before merge" is a real design trade-off, not a default to copy blindly — see Decisions and Feedback.
* This plugin's only genuinely testable "code" is the resume drafter's `.docx`-generation script; the three `SKILL.md` files are natural-language instructions, not executable logic, so "unit test coverage" in the traditional sense applies cleanly to the script (via `pytest`, the de facto standard Python test runner) but not to the skills themselves. `hve-core`'s own repository does not unit-test its `SKILL.md` files either — instead it validates skill *structure* (frontmatter, links) via CI lint workflows and validates skill *behavior* through scenario-based "evals" (`evals/agent-behavior`, `evals/script-validation`, stimuli/expectations YAML pairs) (C3, C5). That is a proportionate model to reuse: `pytest` for the script, lightweight CI structural checks for the skills, and optional eval-style behavior checks as a stretch goal rather than a hard requirement.

## Findings

### GitHub Copilot CLI's real extensibility surface is Skills, Custom Agents, and MCP servers

Copilot CLI has no separate "plugin" concept in GitHub's own documentation. It has three composable extension points: **custom agents** (`.github/agents/*.md`, specialist personas with their own tools/instructions), **agent skills** (`.github/skills/*/SKILL.md`, folders of instructions/scripts loaded when relevant), and **MCP servers** (added via `/mcp add`) (W5, W6). A "plugin" repo for this project is best understood as a repo that ships skills (and optionally supporting agents) using this documented mechanism.

* Questions: Q1
* Evidence state: evidence-backed finding
* Evidence: W5 (official "Invoking custom agents" doc: agents, skills, MCP servers), W6 (official "Adding agent skills" doc: required `SKILL.md` frontmatter fields `name`, `description`, optional `license`/`allowed-tools`)
* Confidence and limits: High — primary GitHub documentation, current as of 2026-09-18 retrieval.

Repository-level skills live in `.github/skills/<skill-name>/SKILL.md`; personal (cross-project) skills live in `~/.copilot/skills/<skill-name>/SKILL.md`. Each `SKILL.md` needs `name` and `description` frontmatter at minimum; `license` and `allowed-tools` are optional. Scripts/resources placed alongside `SKILL.md` are auto-discovered and can be invoked from the skill's instructions (W6).

### `hve-core` demonstrates a working "plugin bundle" pattern this repo can reuse

The `hve-core` plugin installed in this very environment shows a concrete, already-functioning packaging convention: a `.github/plugin/marketplace.json` manifest (name, version, author, license, keywords) alongside standard `.github/skills`, `.github/agents`, `.github/prompts`, and `.github/instructions` directories (C1, C2). This is installable via this app's `install_extension` tool from a gist or a GitHub repo folder URL. It is not a GitHub-official spec, but it is a proven, low-risk template to imitate for anyone who wants the resume plugin discoverable/installable the same way `hve-core` is here.

* Questions: Q2
* Evidence state: evidence-backed finding
* Evidence: C1 (`marketplace.json` structure), C2 (`.github/skills/hve-core/hve-builder/SKILL.md` frontmatter and conventions)
* Confidence and limits: High for structure (directly inspected files); medium for "official-ness" — this manifest format is this app-specific, not confirmed as consumed by the standalone `copilot` CLI binary outside this chat app.

### A "machine-friendly career document" should align with the existing JSON Resume open standard rather than invent a new schema

JSON Resume (jsonresume.org, MIT-licensed, `github.com/jsonresume/resume-schema`) already defines a structured JSON schema for career data (work history, awards, skills, etc.) and is actively maintained with a companion job-description schema (W3). Building skill 1's output as JSON Resume-compatible JSON (extended with fields it lacks, such as raw performance-review excerpts or metrics provenance) gives the plugin a portable, tool-agnostic career document instead of a proprietary format, and skill 2's job-requirements decomposition can reuse the same ecosystem's job-description schema as a starting point.

* Questions: Q3
* Evidence state: partially supported claim
* Evidence: W3 (JSON Resume schema and job-description schema pages)
* Confidence and limits: Medium — the schema's fit for "performance reviews, award citations, metrics, and LinkedIn profile" ingestion has not been validated against real sample documents; it is a promising starting point, not a verified fit for every field the user wants captured (e.g., verbatim award-citation text, reviewer attribution). This is a planning-stage decision, not a research blocker.

### Assisted, link-directed browser capture is the safer design for job-posting ingestion, and the user has already chosen it

Per the user's decision, skill 2 will not scrape or auto-crawl job boards. It will take a single user-supplied link, use the CLI's own browser/computer-use tooling to render that one page as a normal browser would, and extract the visible text for the user to review — the same access pattern a human reading the page already has. This avoids the anti-bot-bypass and bulk-scraping risk that would otherwise apply if the plugin tried to defeat "AI blocking techniques" on sites like LinkedIn, whose User Agreement prohibits automated/bulk data collection (W4) and whose enforcement posture (`hiQ Labs v. LinkedIn`) shows this is a genuinely contested legal area (W4). No evidence in this research suggests one-off, user-directed single-page reads at normal browsing cadence carry the same risk profile as bulk automated scraping, but this is not a legal opinion and the plugin's instructions should say so explicitly and avoid persisting more than the one posting the user references.

* Questions: Q4
* Evidence state: evidence-backed finding (for the risk pattern) / decision (for the mitigation, already made by the user)
* Evidence: W4 (LinkedIn User Agreement prohibition language and the hiQ Labs v. LinkedIn case as public context for enforcement risk)
* Confidence and limits: High that bulk/bypass scraping carries real ToS and legal risk; the residual risk of the user's chosen single-link, human-directed approach is a judgment call, not a bright-line-verified-safe determination — flagged in Risks and Open Questions.

### `python-docx` is the practical, portable choice for generating the Word-format resume from a terminal-based skill

For a CLI-run skill (as opposed to this app's built-in Word canvas, which is specific to this chat surface), the standard open-source approach for programmatically generating `.docx` files is `python-docx` (PyPI, actively distributed, simple `Document()`/`add_paragraph()`/`save()` API) (W7). A skill script can build the resume as a `.docx` directly, which keeps the plugin portable to any environment running Copilot CLI, not just this app's canvas-enabled surface.

* Questions: Q5
* Evidence state: evidence-backed finding
* Evidence: W7 (python-docx PyPI page: install and usage example)
* Confidence and limits: Medium-high — confirms the library exists and works for basic document generation; does not verify it against specific resume-formatting requirements (columns, styled headers, ATS-safe formatting), which is an implementation-stage concern.

### A public GitHub repository gets most of its "hardening" for free — the work is turning features on and adding a few files, not buying anything

GitHub's own security-features documentation states that GitHub Secret Protection and GitHub Code Security features — secret scanning with push protection, Dependabot alerts/security updates, the dependency graph, CodeQL code scanning, and SBOM export — are available on public repositories regardless of plan, even though the same features require an Advanced Security purchase on private repositories (W8). Classic branch protection rules (required reviews, required status checks, blocked force-push/deletion) are likewise a standard feature, not paid-plan-gated (W10). For this project, "sufficiently hardened" concretely means: enable secret scanning + push protection, enable Dependabot (version updates and security updates), add a CodeQL/code-scanning workflow scoped to the one Python script, add a `CODEOWNERS` file, and add at least a lightweight branch protection rule on the default branch. The `hve-core` reference repo demonstrates all of these already wired up and working (C3–C6).

* Questions: Q6
* Evidence state: evidence-backed finding
* Evidence: W8 (GitHub security features overview: public-repo-free feature list), W10 (branch protection rules documentation), C3 (`dependabot.yml`), C4 (`CODEOWNERS`), C5 (`codeql-analysis.yml`)
* Confidence and limits: High — primary GitHub documentation plus a directly inspected, functioning reference implementation. The one judgment call is how strict to make required-review branch protection when the repository may start with a single maintainer (see Decisions and Feedback, D5).

### The standard "community health files" checklist is well-documented and gives a ready-made asset list for a public plugin repo

GitHub's community-profile checklist names the specific files that make a public repository considered healthy and ready for outside contributors: `README`, `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, a security policy (`SECURITY.md`), and issue/pull-request templates placed under `.github/ISSUE_TEMPLATE/` with valid frontmatter (W9). None of this is specific to this plugin's domain — it is the same baseline GitHub recommends for any public open-source project, and the `hve-core` repository already installed in this environment ships every one of these assets, giving a directly inspectable template rather than a from-scratch design problem (C3, C4, C6).

* Questions: Q7
* Evidence state: evidence-backed finding
* Evidence: W9 (GitHub community-profile documentation), C3 (`SECURITY.md`/`LICENSE`/`CONTRIBUTING.md`/`CODE_OF_CONDUCT.md` present in `hve-core`)
* Confidence and limits: High — this is a well-documented, low-ambiguity checklist; the only open item is choosing a specific license text (for example MIT vs. Apache-2.0), which is a naming/preference decision, not a research gap.

### Test coverage should target the one real code artifact (the `.docx` script) with `pytest`; the three skills are validated structurally and behaviorally, not unit-tested

This plugin's only executable "code" in the traditional sense is the resume drafter's Python script that builds the `.docx` file; the three `SKILL.md` files are natural-language instruction sets consumed by an AI agent, not functions with deterministic inputs/outputs, so conventional unit testing does not apply to them directly. `pytest` is the de facto standard Python testing framework (widely documented, actively maintained, works with any Python package including `python-docx`) and is the natural fit for testing `build_docx.py`'s logic (for example: given known input content, does the generated `.docx` contain the expected sections/headings). For the skills themselves, `hve-core`'s own repository — a directly inspectable precedent — does not attempt unit tests on its `SKILL.md` files; instead it runs CI structural lint (frontmatter validity, broken-link checks) and separately maintains scenario-based "evals" (`evals/agent-behavior`, `evals/script-validation`, each pairing a `stimuli` input with an `expectations` file) to check that a skill behaves as intended when actually invoked (C3, C5). That two-tier model — `pytest` for real code, lightweight structural CI checks plus optional scenario evals for skill behavior — is a proportionate pattern this plugin can adopt without over-building test infrastructure for a first release.

* Questions: Q8
* Evidence state: evidence-backed finding
* Evidence: C3, C5 (`hve-core`'s `evals/` directory and its script/behavior eval pairs), general Python ecosystem knowledge of `pytest` as the standard test runner
* Confidence and limits: High that `pytest` is the correct choice for the script; medium on how much eval-style behavior testing is worth building for a first release versus a later iteration — recorded as a planning-stage scope decision (D6), not a blocker.

## Recommendation and Alternatives

* Recommendation or decision state: Not applicable in this `analysis` mode — this research presents the viable packaging, hardening, and testing options rather than forcing one final architecture, since the user has already made the most consequential calls (job-data acquisition method; dual skills-plus-marketplace packaging; public repo with sufficient hardening; test coverage for future iteration).
* Rationale: The remaining choices (JSON Resume alignment, python-docx usage, evidence-tagging style for the resume builder, exact branch-protection strictness, and how much eval-style behavior testing to build initially) are implementation details best resolved during planning with concrete sample inputs, not blocked on further research.
* What could change this result: Discovering during planning that JSON Resume's schema is a poor fit for the specific inputs (performance reviews, award citations) would justify a bespoke schema instead; this would not change the plugin's Agent Skills packaging, its public-repo hardening posture, or its testing approach.

| Option                                                              | Benefits                                                                 | Costs and risks                                                                 | Evidence | Disposition |
|----------------------------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------|----------|-------------|
| Skills-only repo (`.github/skills`, no marketplace.json)             | Simplest; works with official `gh skill install` / directory copy today  | Not installable via this app's gist/plugin-bundle install flow                  | W6       | viable      |
| Skills + `marketplace.json` bundle (user's selection)                | Works with both the official skills mechanism and this app's plugin install flow, mirrors proven `hve-core` pattern | Extra manifest to maintain; format is app-specific, not GitHub-official          | C1, W6   | selected    |
| Bespoke JSON schema for the career document                          | Full control over fields                                                 | Reinvents an already-solved problem; less interoperable                          | W3       | deferred    |
| JSON Resume-aligned schema for the career document                   | Reuses a maintained, open, MIT-licensed standard with a job-description companion schema | May need custom extensions for performance-review/award-citation provenance     | W3       | viable      |
| Automated/bulk browser scraping of job boards to defeat bot detection | Could gather more postings automatically                                 | Violates common site terms (e.g., LinkedIn), legally contested, higher risk      | W4       | rejected (user decision) |
| Link-directed, human-approved single-page browser capture (user's selection) | Matches ordinary human browsing access pattern; avoids bypass techniques | Still requires the user to supply each link manually; no bulk automation        | W4       | selected    |
| Minimal public repo (README + LICENSE only, no security features enabled) | Fastest to stand up                                                       | Fails GitHub's own community-profile checklist; misses free security features; poor first impression for contributors | W8, W9   | rejected    |
| Full free-tier hardening (secret scanning + push protection, Dependabot, CodeQL, CODEOWNERS, branch protection) plus community-health files (user's selection) | Matches GitHub's own recommended baseline for public repos at no extra cost; directly modeled on a working reference (`hve-core`) | Slightly more setup work in P01; branch-protection strictness needs a scoped decision for a solo maintainer | W8, W9, W10, C3–C6 | selected |
| Traditional unit tests for the `SKILL.md` files themselves           | Would give "full" test coverage in a naive sense                          | Not technically meaningful — skills are natural-language instructions, not deterministic functions | C3, C5   | rejected    |
| `pytest` for the `.docx` script, plus lightweight CI structural checks for skills (user's selection, minimum bar) | Matches what is actually testable; low setup cost; matches `hve-core` precedent | Does not verify skill *behavior*, only structure                                | C3, C5, W7 | selected |
| `pytest` + optional scenario-based evals for skill behavior (stretch goal) | Closest to real behavioral confidence, mirrors `hve-core`'s own testing model | More setup and maintenance cost; may be excessive for a first release            | C3, C5   | viable (deferred to planning) |

## Scope and Questions

* Goal: Determine how to structure and build a new, user-owned, **public** GitHub repository that ships a GitHub Copilot CLI plugin with three resume-building skills, following a research → plan → implement workflow, with sufficient repository hardening, standard community/license/security assets, and a testing approach that supports future iteration, so the user can proceed to `/rpi-plan` with a validated technical foundation.
* Audience and use: The requesting user, who will create the repo and drive planning/implementation next; secondarily, any outside contributor or user who discovers and installs the published plugin.
* In scope: Copilot CLI skill/plugin packaging mechanisms; machine-friendly career-document format options; job-description ingestion method and its compliance posture; Word-document generation approach; anti-fabrication design pattern for the resume-builder skill; public-repository security hardening features and their cost/availability; standard open-source community/license/security assets; a proportionate test-coverage strategy for the repo's code and skill content.
* Out of scope: Writing the actual `SKILL.md` files, repo scaffolding, hardening configuration, or code (reserved for `/rpi-plan` and `/rpi-implement`); legal advice (this research flags risk, it does not adjudicate it); specific resume content/formatting choices; selecting a specific license text beyond noting the standard options (left to planning/user preference).
* Decision and evidence criteria: Findings must be traceable to official GitHub documentation (for CLI mechanics, security features, and community standards) or established open-source/standards evidence (for schema, library, and testing-framework choices).
* Requested output: Analysis of viable approaches and risks to support planning, not a single locked-in implementation recommendation.

| ID | Question                                                                                          | Source            | Status   |
|----|-----------------------------------------------------------------------------------------------------|--------------------|----------|
| Q1 | What mechanism does GitHub Copilot CLI actually provide for a repo-distributed "plugin"?             | inferred from ask  | answered |
| Q2 | Should the repo also ship a marketplace-style manifest like `hve-core`'s?                            | explicit (user)    | answered |
| Q3 | What format should the "machine-friendly career document" use?                                       | inferred           | answered |
| Q4 | How should the job-requirements-planning skill acquire job posting content without policy/legal risk? | explicit (user)    | answered |
| Q5 | What library/approach should generate the Word-format resume?                                        | inferred           | answered |
| Q6 | What does "sufficiently hardened" concretely mean for a public repo on GitHub, and what does it cost? | explicit (user)    | answered |
| Q7 | What standard licensing/contributing/security/community assets should a public plugin repo ship?     | explicit (user)    | answered |
| Q8 | What does meaningful "unit test coverage" look like for a repo that is mostly `SKILL.md` instructions plus one Python script? | explicit (user)    | answered |

## Decisions and Feedback

| Group | Decision or feedback item                                                                                                     | Status    | Owner | Rationale or input needed                                                       | Evidence | Impact of answer |
|-------|----------------------------------------------------------------------------------------------------------------------------------|-----------|-------|-----------------------------------------------------------------------------------|----------|-------------------|
| D1    | Job-posting capture uses CLI browser/computer-use tooling on a user-supplied link, one page at a time, no anti-bot bypass       | confirmed | user  | User explicitly chose this over automated scraping or bypass techniques           | W4       | Removes the highest-risk design option from planning |
| D2    | Repo packaging ships both plain `.github/skills` (+ optional `.github/agents`) and a `.github/plugin/marketplace.json` bundle    | confirmed | user  | User explicitly chose "both" over skills-only or marketplace-only                  | C1, W6   | Planning should scaffold both the standard skill directories and a manifest |
| D3    | Whether to align the career-document schema with JSON Resume or design a bespoke schema                                        | proposed  | agent | JSON Resume is a credible, maintained open standard; fit for review/award/metric fields is unverified | W3       | Affects skill 1's data model; recommend validating with 2-3 sample inputs during planning |
| D4    | Anti-fabrication design pattern for skills 1 and 3 (e.g., every resume bullet must cite back to a career-document entry, similar in spirit to the evidence-ID discipline this RPI workflow itself uses) | proposed | agent | No existing evidence contradicts this pattern; it directly satisfies the user's "hard-line stance against assuming or inventing information" requirement | C2 | Shapes skill 3's core constraint set during planning |
| D5    | Repository is public and ships the free-tier GitHub hardening set (secret scanning + push protection, Dependabot, CodeQL scoped to the Python script, `CODEOWNERS`, branch protection on the default branch) plus standard community-health files (`LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, issue/PR templates) | confirmed | user | User explicitly asked for public visibility, "sufficient" hardening, and licensing/contributing/security/community assets; GitHub documents all of these as free-tier public-repo features | W8, W9, W10, C3–C6 | Adds new FR/NFR scope to the plan for P01 (repo scaffold phase) |
| D6    | Exact branch-protection strictness for a repository that may start with a single maintainer (e.g., whether to require an approving review before merge from day one, or start lighter and tighten once contributors exist) | proposed | agent | No evidence dictates one answer; this is a proportionality trade-off between rigor and single-maintainer friction, not a factual gap | W10 | Left to planning/implementer judgment as a configuration choice, not a blocker |
| D7    | Test-coverage scope: `pytest` for the `.docx`-generation script plus lightweight CI structural checks for the three skills is the minimum bar; scenario-based behavior evals (mirroring `hve-core`'s `evals/` pattern) are a stretch goal, not required for a first release | proposed | agent | `hve-core`'s own repository does not unit-test its `SKILL.md` files and instead uses structural lint plus optional evals; matching that precedent avoids over-building test infrastructure prematurely | C3, C5 | Shapes P05's validation task and any future testing-focused follow-up work |

## Risks and Open Questions

| Priority | Type          | Risk, question, or research item                                                                                     | Impact | Smallest action or evidence needed                                                          | Owner       |
|----------|---------------|--------------------------------------------------------------------------------------------------------------------|--------|-----------------------------------------------------------------------------------------------|-------------|
| M        | risk          | LinkedIn (and similar sites) prohibit automated/bulk data collection in their terms; enforcement is an evolving legal area (hiQ v. LinkedIn) | Legal/account risk if the plugin's browser capture is ever extended beyond single, user-directed links | Keep skill 2's instructions explicit: one link at a time, human-supplied, no crawling, no bulk export; revisit if scope ever changes | user/downstream |
| L        | open question | Does JSON Resume's schema (or its job-description companion) actually cover the specific input types the user named (performance reviews, award citations, metrics)? | Could require schema extension during planning | Try mapping 1-2 real sample documents to the schema during `/rpi-plan` | downstream |
| L        | open question | How strict should branch protection be for a repository that may start with a single maintainer (require review vs. lighter initial posture)? | Overly strict rules could block the sole maintainer's own merges; overly light rules understate the "sufficiently hardened" goal | Decide the initial posture during planning (D6); document the intent to tighten once contributors exist | downstream |
| L        | further planning | Whether to build scenario-based behavior evals (beyond `pytest` + structural CI checks) for the three skills in the first release or as a later iteration | Affects initial implementation scope and ongoing maintenance cost | Decide during planning (D7); `hve-core`'s `evals/` directory is a ready-made pattern to copy if/when this is prioritized | downstream |
| L        | open question | Should the plugin's Word-document generation happen via a skill-bundled `python-docx` script, or should it optionally leverage this app's native Word canvas when running inside this chat surface? | Affects portability vs. richer in-app editing experience | Decide during planning based on target runtime(s) for the plugin | downstream |
| L        | further research | Concrete `SKILL.md` content/structure for all three skills, and whether any should be split into a skill + companion subagent (per `hve-builder`'s guidance on when to add a subagent vs. keep logic in the skill) | Affects repo layout | Apply `hve-artifact-authoring`/`hve-builder` conventions during planning; not required to unblock planning | downstream |

## Planning Readiness and Next Step

| Field                            | Record                                                                                                   |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------|
| Research disposition               | executed                                                                                                   |
| Decision participation             | user-owned (standalone rpi-research invocation)                                                            |
| Planning Readiness                 | Ready — packaging model, job-data acquisition method, public-repo hardening posture, community/license/security assets, and test-coverage strategy are evidence-backed; remaining items (D3, D6, D7, open questions) are planning-stage refinements, not blockers |
| Research depth and lanes           | Two executed cycles, all inline (Cycle 1 — Wider: CLI extensibility docs + `hve-core` structure; Deeper: SKILL.md/marketplace.json conventions, JSON Resume, python-docx; Contrarian: LinkedIn ToS/scraping risk. Cycle 2 — Wider: public-repo security features + community-health-file checklist; Deeper: `hve-core`'s actual hardening/testing config as a working reference; Contrarian: proportionality of hardening/testing rigor for a repo that may start with one maintainer) |
| Blockers                           | none                                                                                                        |
| Output mode and planning support   | `analysis`; supports planning because Planning Readiness is `Ready`                                        |
| Continuation owner                 | user                                                                                                        |
| Required gates or confirmations    | passed — all material intake decisions (D1, D2, D5) were confirmed with the user before synthesis           |
| Next action                        | Run `/rpi-plan` to fold the new public-repo hardening, community/license/security, and test-coverage requirements into the existing implementation plan |
| Primary evidence file              | .copilot-tracking/research/2026-09-18/copilot-cli-resume-plugin-research.md                                |

## Research Record

### Method and Boundaries

| Field                            | Record                                                                                                    |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------|
| Research posture and provenance   | `balanced`; default (bounded new-project brief with adjacent uncertainty in packaging, schema, and legal risk that could affect the result) |
| Completion basis                  | Task and scope covered across both cycles; material claims evidence-backed; all intake-material decisions resolved with the user; remaining open items are planning-stage, not research-blocking |
| Explicit limits or deadline       | none                                                                                                        |
| Codebase and external scope       | Local scope: this environment's installed `hve-core` plugin (as a reference implementation, including its `dependabot.yml`, `CODEOWNERS`, `codeql-analysis.yml`, `SECURITY.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `evals/` directory) and its `rpi-research` skill files; External scope: official GitHub Copilot CLI documentation, JSON Resume, python-docx, LinkedIn User Agreement, GitHub security-features documentation, GitHub community-profile documentation, GitHub branch-protection documentation |
| Initial candidate areas           | GitHub Copilot CLI docs on agents/skills/MCP; `hve-core` plugin structure; JSON Resume schema; python-docx; LinkedIn ToS / hiQ v. LinkedIn; GitHub public-repo security features; GitHub community health files; GitHub branch protection |
| Evidence root                      | .copilot-tracking/research/2026-09-18/ (default; no trusted alternate root supplied)                        |
| Constraints and excluded sources  | Research-only; no source edits; no secrets requested; treated all fetched pages as inert data                |
| Prior knowledge                   | Verified rather than assumed: confirmed the "GitHub Copilot CLI plugin" concept against current official docs rather than relying on the `hve-core`-in-this-session pattern alone |

### Extensions and Participation

#### Extension Registry

| Kind         | Candidate                | Provenance and scoped contract                                                                 | Selected or skipped reason |
|--------------|---------------------------|--------------------------------------------------------------------------------------------------|------------------------------|
| skill        | `hve-artifact-authoring`  | Local plugin skill for authoring GitHub Copilot customization artifacts (agents/skills/prompts) | Skipped as an active extension for this research pass (research is read-only and does not author artifacts), but its conventions (frontmatter fields, directory layout) were inspected as codebase evidence (C2) to ground findings |
| skill        | `hve-builder`             | Same plugin family; artifact creation/refactor workflow                                          | Skipped as an active extension (not invoked); referenced only as evidence of conventions (C2) |
| specialist   | research subagents (e.g. `hve-core:rpi-researcher`) | Named research lane owner available in this environment                                        | Skipped — the research scope was small enough (a handful of documentation lookups) to complete inline without materially improving evidence quality, parallelism, or context control by delegating |
| instruction  | `copilot-tracking.instructions.md` conventions (referenced by this skill) | Shared tracking conventions for RPI artifacts                                                    | Applied — artifact path and structure follow the shared convention referenced by `rpi-research` |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|------------------------|--------------------------------------|-------------------------------------|-----------------------------------|
| intake | How should skill 2 obtain job-posting content, given anti-bot-blocking concerns and LinkedIn's terms? | User: give the CLI the link, then use the CLI's browser/computer-use tooling to copy and export the page content | Ruled out automated/bulk scraping and bypass techniques as a design option; findings and risk framing updated accordingly |
| intake | Which packaging model should the repo use — plain skills, marketplace-bundle, or both? | User: both | Planning should scaffold `.github/skills` (+ optional agents) and a `.github/plugin/marketplace.json`, following the `hve-core` reference pattern |
| re-entry (cycle 2) | User explicitly requested the repo be public, "sufficiently hardened," ship licensing/contributing/security/community assets, and support future test-coverage-driven iteration | User: explicit direction supplied as `/rpi-research` arguments, no interaction needed to interpret intent | Triggered a second complete three-wave cycle scoped to public-repo hardening, community/security assets, and test-coverage strategy; agent-owned resolution used for the sub-decisions this direction did not itself answer (D6, D7), consistent with `user-owned` participation applying only where material ambiguity existed |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: `balanced`; no explicit caller limit or deadline; scope limited to packaging/distribution mechanism, job-data acquisition method, career-document format, and Word-generation approach — not skill content authoring.

##### Wave 1: Wider

* Focus and lanes: Identify how GitHub Copilot CLI actually supports repo-distributed extensibility ("plugins"), and survey candidate formats for a machine-friendly career document and Word-document generation.
* Evidence or worker pointers: inline — official GitHub docs on Copilot CLI (`about-copilot-cli`, `invoke-custom-agents`, `about-agent-skills`, `customization-cheat-sheet`), local inspection of the installed `hve-core` plugin (`marketplace.json`, `SKILL.md` files), JSON Resume homepage, python-docx PyPI page.
* Reflection: Confirmed there is no GitHub-official "plugin" artifact type distinct from skills/agents/MCP servers; confirmed `hve-core`'s `marketplace.json` is a workable, already-functioning bundle pattern; identified JSON Resume and python-docx as credible starting points for the two content-format questions.

##### Wave 2: Deeper

* Focus and lanes: Read the exact `SKILL.md` frontmatter contract (required/optional fields, `allowed-tools`), the `marketplace.json` field set, and JSON Resume's schema/job-description-schema pairing in more detail.
* Evidence or worker pointers: inline — `add-skills` doc (frontmatter fields, script-enabling pattern), `hve-core/.github/plugin/marketplace.json` (name/version/author/license/keywords), `hve-core/.github/skills/hve-core/hve-builder/SKILL.md` (frontmatter conventions: `name`, `description`, `argument-hint`, `license`, `user-invocable`), jsonresume.org (schema + job-description schema), pypi.org/project/python-docx (install/usage).
* Reflection: All detail needed to describe a viable repo layout and content-format starting point is now evidence-backed; no material gap remains for the packaging or library questions.

##### Wave 3: Contrarian

* Focus and lanes: Test whether the "browser to prevent AI blocking techniques" approach for job-posting ingestion carries meaningful legal/ethical risk that should reshape the design before planning.
* Evidence or worker pointers: LinkedIn User Agreement (partial fetch: prohibits automated/bulk data collection outside stated Services; full "Do's and Don'ts" section did not render via the fetch tool, likely due to client-side rendering — noted as a retrieval limitation) plus well-established public knowledge of *hiQ Labs v. LinkedIn* as corroborating context that this is a genuinely contested, actively litigated area rather than a settled "scraping is fine" or "scraping is always illegal" question.
* Reflection: This materially changed the recommended design — surfaced to the user as a direct question before finalizing findings, rather than silently assuming either "scrape aggressively" or "avoid LinkedIn entirely."

##### Parent Synthesis and Re-entry

| Material or claim | Evidence or worker pointers | Disposition | Rationale | User-facing effect |
|----------------------|---------------------------------|------------------|---------------|--------------------------|
| "GitHub Copilot CLI plugin" = a skills/agents repo, no separate plugin artifact type | W5, W6 | accepted | Confirmed by two independent official GitHub doc pages | Findings section 1 |
| `marketplace.json` bundle pattern is viable and proven in this environment | C1, C2 | accepted | Directly inspected working example | Findings section 2; Recommendation table |
| JSON Resume is a strong starting point for the career-document schema | W3 | accepted, with caveat | Established open standard; fit for every requested input type unverified | Findings section 3; Decisions D3 |
| Automated/bypass browser scraping is a materially risky design choice | W4 | accepted | Explicit ToS language plus well-known litigation history | Findings section 4; used to frame the user question that produced D1 |
| python-docx is a practical choice for CLI-portable Word-document generation | W7 | accepted | Confirmed current, simple, actively distributed library | Findings section 5; Risks (open question on canvas vs. script) |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: All material claims needed to reach `Ready` planning readiness are evidence-backed; both decisions with real direction-changing potential (job-data acquisition method, packaging model) were resolved directly with the user; remaining open items are appropriately deferred to planning rather than requiring further research.
* Readiness or revalidation effect: Planning Readiness set to `Ready`.

#### Cycle 2

* Active posture, controls, and limits: `balanced`; no explicit caller limit or deadline; scope added by explicit user direction: public-repository security hardening, standard community/license/security assets, and a test-coverage strategy for future iteration — triggered as a re-entry after Cycle 1 had already reached `Ready` for the original packaging/schema/acquisition scope.

##### Wave 1: Wider

* Focus and lanes: Survey what "sufficiently hardened" and "important repo assets" concretely mean for a public GitHub repository, and what test-coverage approaches are viable for a repo that is mostly `SKILL.md` instructions plus one Python script.
* Evidence or worker pointers: inline — GitHub's community-profile documentation (recommended file checklist), GitHub's security-features overview (public-repo-free feature list), local inspection of the installed `hve-core` plugin's root and `.github/` assets (`LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `dependabot.yml`, `CODEOWNERS`, `.github/workflows/`, `evals/`).
* Reflection: Confirmed GitHub documents a specific, well-known community-health-file checklist and a specific set of security features that are free on public repos; confirmed `hve-core` is a directly inspectable, fully working example of both, removing most design ambiguity.

##### Wave 2: Deeper

* Focus and lanes: Read the exact scope of GitHub's public-repo-free security features (secret scanning/push protection, Dependabot, CodeQL, SBOM), the classic branch-protection rules mechanism and its plan availability, and `hve-core`'s specific `dependabot.yml`/`CODEOWNERS`/`codeql-analysis.yml` configuration and its `evals/` directory structure as a concrete testing-strategy precedent.
* Evidence or worker pointers: inline — `github-security-features` doc (feature-by-plan breakdown), `about-rulesets` and `about-protected-branches` docs (rulesets vs. classic branch protection, plan scope), `hve-core/.github/dependabot.yml` (npm/github-actions/uv ecosystems, weekly schedule, security-update grouping), `hve-core/.github/CODEOWNERS` (default + path-scoped owners), `hve-core/.github/workflows/codeql-analysis.yml` (scheduled weekly scan, minimal `contents: read` permissions), `hve-core/evals/agent-behavior` and `hve-core/evals/script-validation` (stimuli/expectations pairing as the behavior-testing pattern for skill content).
* Reflection: All detail needed to describe a viable, concrete hardening and testing baseline is now evidence-backed; identified that `pytest` (general Python ecosystem knowledge, not a fetched source) is the correct fit for the one piece of real code, while skill-content "testing" is better modeled as structural CI checks plus optional evals, matching `hve-core`'s own precedent rather than forcing an ill-fitting unit-test model onto natural-language instructions.

##### Wave 3: Contrarian

* Focus and lanes: Test whether "sufficiently hardened" and "full test coverage" could be over-engineering for a new, possibly single-maintainer repository, and whether any hardening feature has a real cost or trade-off worth flagging before planning.
* Evidence or worker pointers: GitHub's own branch-protection documentation notes that by default, restrictions do not apply to repository admins unless explicitly extended to them, and that bypass-list actors can only be added when the repository belongs to an organization — meaning a personal, single-owner public repo cannot delegate bypass permissions the way an org-owned repo can, so a strict "require approving review" rule could block the sole maintainer's own merges unless they self-approve or temporarily disable the rule. This is a genuine proportionality trade-off, not a reason to skip hardening altogether, and was recorded as a planning-stage decision (D6) rather than silently defaulting to either extreme. Similarly, `hve-core` itself — a mature, actively maintained repo — does not unit-test its `SKILL.md` files, which corroborates that full behavioral test coverage for skill content is a deliberate, scoped choice (evals) rather than an oversight, supporting a phased test-coverage approach (D7) instead of an all-at-once mandate.
* Reflection: This did not overturn the core recommendation (public repo should still ship the free hardening features and community files), but it surfaced two real, evidence-based scope/proportionality decisions (D6, D7) that planning should resolve explicitly rather than the research artifact silently picking one extreme.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence or worker pointers | Disposition | Rationale | User-facing effect |
|----------------------|---------------------------------|------------------|---------------|--------------------------|
| Secret scanning + push protection, Dependabot, CodeQL, dependency graph, and SBOM export are free on public GitHub repos regardless of plan | W8 | accepted | Directly stated in GitHub's own security-features overview | Findings section 6; Recommendation table |
| Classic branch protection (required reviews, required status checks, no force-push/delete) is a standard, non-paid-plan-gated feature | W10 | accepted | Directly stated in GitHub's own branch-protection documentation | Findings section 6; Decisions D5, D6 |
| `hve-core` demonstrates a fully working reference configuration for `dependabot.yml`, `CODEOWNERS`, and a scheduled CodeQL-style workflow | C3, C4, C5 | accepted | Directly inspected, currently functioning files in this environment | Findings section 6; template for P01 in planning |
| GitHub's community-profile checklist (`README`, `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, security policy, issue/PR templates) is the standard public-repo asset list | W9 | accepted | Directly stated in GitHub's own community-profile documentation | Findings section 7; Decisions D5 |
| `hve-core` ships every community-health file GitHub recommends | C3, C4, C6 | accepted | Directly inspected, currently present files | Findings section 7; template for P01 in planning |
| `pytest` is the correct test framework for the `.docx`-generation script; `SKILL.md` files are not meaningfully unit-testable | C3, C5, general Python ecosystem knowledge | accepted | Confirmed by the nature of the artifacts (deterministic script vs. natural-language instructions) and corroborated by `hve-core` not unit-testing its own skills | Findings section 8; Decisions D7 |
| Branch-protection strictness and eval-style behavior testing depth are proportionality trade-offs, not factual gaps | W10, C3, C5 | accepted, deferred | No evidence dictates one correct answer; both are legitimate planning-stage scope decisions | Decisions D6, D7; Risks and Open Questions |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: All material claims needed to extend Planning Readiness to the new public-repo-hardening, community-asset, and test-coverage scope are evidence-backed; the one material user-directed decision this cycle introduced (D5: public + hardened + community assets) is confirmed; the two sub-decisions this cycle surfaced (D6, D7) are legitimate planning-stage proportionality calls, not research gaps.
* Readiness or revalidation effect: Planning Readiness remains `Ready`, now covering the expanded scope; the existing plan at `.copilot-tracking/plans/2026-09-18/copilot-cli-resume-plugin-plan.md` will need revision in `/rpi-plan` to add the new FR/NFR and at least one new phase/task set for hardening, community assets, and test coverage.

### Evidence Log

* Delegation: none — all research performed inline by the parent; no lane artifacts were created.

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|----|----------------------|--------------------------|-----------------------------|------------|----------------|-----------|
| C1 | `hve-core` plugin bundle manifest structure (`name`, `metadata`, `owner`, `plugins[]` with `source`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`) | `.github/plugin/marketplace.json` in the locally installed `hve-core` plugin (`/Users/benarculus/.copilot/installed-plugins/hve-core/hve-core/.github/plugin/marketplace.json`) | not applicable | read | high | Directly inspected file |
| C2 | Skill `SKILL.md` frontmatter convention (`name`, `description`, `argument-hint`, `license`, `user-invocable`) and skill-directory layout (`.github/skills/<group>/<skill>/SKILL.md` with `references/`, `templates/`) | `.github/skills/hve-core/hve-builder/SKILL.md` and sibling skill directories in the same installed plugin | not applicable | read | high | Cross-checked against `rpi-research`'s own `SKILL.md` for consistency |
| W1 | Agent Skills is an open, cross-vendor standard (agentskills.io) usable across Copilot CLI, VS Code, JetBrains, and Copilot cloud agent | "About agent skills" — docs.github.com/en/copilot/concepts/agents/about-agent-skills | 2026-09-18 | external_research | high | Official GitHub documentation |
| W2 | Skills can be installed from a repo via `gh skill install`/directory copy; no GitHub-documented "plugin" manifest format exists for Copilot CLI | "Adding agent skills for GitHub Copilot CLI" — docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills | 2026-09-18 | external_research | high | Confirms no first-party marketplace format; `marketplace.json` is app-specific (see C1) |
| W3 | JSON Resume: open, MIT-licensed JSON schema for resumes plus a companion job-description schema | jsonresume.org/schema and jsonresume.org (job-description schema link) | 2026-09-18 | external_research | medium | Schema's fit to the user's specific input types (performance reviews, award citations) not separately verified |
| W4 | LinkedIn User Agreement frames the "Services" scope narrowly and (per well-established public record, since the automated "Do's and Don'ts" list did not fully render via fetch) prohibits automated/bulk data collection; `hiQ Labs v. LinkedIn` shows this is an actively contested legal area | linkedin.com/legal/user-agreement (partial retrieval); public record of *hiQ Labs, Inc. v. LinkedIn Corp.* | 2026-09-18 | external_research | medium | Retrieval limitation noted: full Do's/Don'ts clause list did not render through the fetch tool; conclusion corroborated by well-documented public case history rather than by that specific clause text |
| W5 | Copilot CLI's three extension points are custom agents, agent skills, and MCP servers; no separate "plugin" artifact type | "Invoking custom agents" — docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents | 2026-09-18 | external_research | high | Official GitHub documentation |
| W6 | `SKILL.md` required frontmatter (`name`, `description`), optional (`license`, `allowed-tools`); repo skills live in `.github/skills`, `.claude/skills`, or `.agents/skills`; personal skills in `~/.copilot/skills` or `~/.agents/skills` | "Adding agent skills for GitHub Copilot CLI" — docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills | 2026-09-18 | external_research | high | Official GitHub documentation |
| W7 | `python-docx` is an actively distributed PyPI package for reading/creating/updating `.docx` files with a simple `Document()` API | pypi.org/project/python-docx/ | 2026-09-18 | external_research | high | Confirms library availability and basic API only; not benchmarked against resume-specific formatting needs |
| C3 | `hve-core` root and `.github/` community/security assets present and structured: `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/dependabot.yml` (npm, github-actions, and uv/Python ecosystems, weekly schedule, security-update grouping), and an `evals/` directory (`evals/agent-behavior`, `evals/script-validation`) pairing `stimuli`/`expectations` files as a behavior-testing pattern | Root and `.github/` of the locally installed `hve-core` plugin (`/Users/benarculus/.copilot/installed-plugins/hve-core/hve-core/`) | not applicable | read | high | Directly inspected files; confirms a fully working public-repo template for both hardening and testing |
| C4 | `hve-core`'s `.github/CODEOWNERS` assigns a default owner (`* @microsoft/edge-ai-core-dev`) plus path-scoped owners (for example `.github/CODEOWNERS` itself, `.github/`, `scripts/`) | `.github/CODEOWNERS` in the locally installed `hve-core` plugin | not applicable | read | high | Directly inspected file; concrete pattern for a `CODEOWNERS` file in this new repo |
| C5 | `hve-core`'s `.github/workflows/codeql-analysis.yml` runs a scheduled weekly scan with minimal `contents: read` permissions; `eval-validation.yml` runs scenario-based evals with `soft-fail`/`changed-files-only` options | `.github/workflows/codeql-analysis.yml` and `.github/workflows/eval-validation.yml` in the locally installed `hve-core` plugin | not applicable | read | high | Directly inspected files; shows a minimal-permissions, scheduled-scan pattern this repo can copy at a smaller scale |
| C6 | `hve-core` ships GitHub's full recommended community-health-file set (README, LICENSE, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md) plus issue/PR templates | Root and `.github/` of the locally installed `hve-core` plugin | not applicable | read | high | Directly inspected; corroborates W9's checklist with a working example |
| W8 | GitHub Secret Protection and GitHub Code Security features — secret scanning with push protection, Dependabot alerts/security updates, dependency graph, CodeQL code scanning, SBOM export — are available on public repositories regardless of plan, unlike private repositories where they require an Advanced Security purchase | "GitHub security features" — docs.github.com/en/code-security/getting-started/github-security-features | 2026-09-18 | external_research | high | Official GitHub documentation |
| W9 | The community-profile checklist recognizes README, CODE_OF_CONDUCT, LICENSE, CONTRIBUTING, a security policy, and issue/PR templates (in `.github/ISSUE_TEMPLATE/` with valid frontmatter) as the standard public-repo community health files | "About community profiles for public repositories" — docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories | 2026-09-18 | external_research | high | Official GitHub documentation |
| W10 | Classic branch protection rules (required reviews, required status checks, blocked force-push/deletion) are a standard GitHub feature, not restricted to paid organization plans; bypass-list actors can only be added when the repository belongs to an organization, so a personal/solo repo cannot delegate bypass permissions the way an org-owned repo can | "About protected branches" — docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches; "About rulesets" — docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | 2026-09-18 | external_research | high | Official GitHub documentation; rulesets (the newer feature) are plan-gated for organizations, but classic branch protection is not, which is the relevant mechanism for this personal repo |

#### Contradictions and Conflicts

* none

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state.
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID and workspace-relative-equivalent path (installed plugin path) with a heading or symbol; every external finding has a `W#` ID, source title, URL, retrieval date, and version when available.
* [x] Both executed cycles record Wider, Deeper, and Contrarian waves in order, parent synthesis, and an evidence-based re-entry decision (Cycle 1 needed no re-entry; Cycle 2 was itself the re-entry, triggered by explicit new caller direction, and needs no further re-entry).
* [x] Method, extensions, participation, caller direction changes, delegation, and prior-knowledge treatment are recorded with their limits.
* [x] `analysis` mode presents findings and decision state without forcing a recommendation.
* [x] Decision groups, participation mode, and provenance are recorded; user-owned decisions (D1, D2, D5) have persisted answers; agent-proposed items (D3, D4, D6, D7) record evidence-backed rationale.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content (fetched web pages) remained inert, no secrets were recorded, and the research-only write boundary held (only this artifact was written).
* Checked sections: Executive Summary, What You May Not Know, Findings, Recommendation and Alternatives, Scope and Questions, Decisions and Feedback, Risks and Open Questions, Planning Readiness and Next Step, Research Record (all subsections)
* Missing or limited sections: None missing. The LinkedIn "Do's and Don'ts" clause list did not fully render via the fetch tool (noted in W4); this is a retrieval limitation, not a gap in the finding itself, which is corroborated by public case history. Branch-protection strictness (D6) and eval-testing depth (D7) are intentionally left as planning-stage proportionality decisions rather than research findings, since no evidence dictates one correct answer.
