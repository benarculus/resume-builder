<!-- markdownlint-disable-file -->
# Task Research: resume-writing-guidance

| Field | Value |
|---|---|
| Date | 2026-09-19 |
| Researcher / agent | rpi-research |
| Output mode | research-only |

## Executive Summary

* Bottom line: A future update should give the two skills **different roles**: the career-document builder preserves detailed, sourced achievement evidence; the resume drafter converts only that verified evidence into concise, job-relevant bullets whose action, scope, and result are immediately visible. The supplied 475–600-word range should be a resume-level target, not a career-document limit. Its top matter should be a name line followed by `email address | city, state | optional government security clearance info`. The new strategic-format guidance adds reverse-chronological ordering, consistent typography/date treatment, focused structure, margins no smaller than 0.5 inch, body text at 10–12 pt, and a 16–22 pt name. Education and training entries should spell out the degree and major, include completion date and institution, and add an abbreviation only when it supports a verified job-description keyword.
* Why this matters: Applying a two-line limit to the evidence record would discard valuable proof, while applying verbose bullets to the resume defeats its scanning goal. A shared evidence and keyword-mapping rule prevents either outcome from inventing claims or stuffing unsupported terms.
* Research status: Complete for the supplied deck, current two-skill surfaces, Indeed’s accessible metadata/section taxonomy, the supplied Columbia source text, and an independent limit on the F-pattern claim.
* Confidence and uncertainty: High for the required two-artifact separation, the existing provenance/anti-fabrication constraints, and Columbia’s supplied STAR/What–How–Why guidance; medium for the action-verb taxonomy because Indeed’s accessible article structure, rather than every explanatory paragraph, was retrieved; medium for F-pattern use because the research applies to web-content scanning, not a controlled recruiter-resume study.

## What You May Not Know

* The F-shaped pattern is not a rule that people always follow. NN/g says it is one possible web-scanning pattern and that good formatting can prevent it. Treat it as a reason to make left-edge cues and the first words of bullets meaningful, not as a promise about recruiter attention (W3).
* A two-line bullet cannot be guaranteed by a word count alone: it depends on the rendered font, margins, bullets, and available width. The future resume rule needs an actual rendered-output check, plus concise construction guidance, rather than a fixed character ceiling (C4).
* Columbia’s web page returned `403` to direct retrieval, but the user supplied its complete relevant text. It supports using STAR to develop the full evidence statement, then leading the final resume statement with the **Action** and including **Result** when appropriate (U1).
* The supplied image gives presentation guidance, not a complete template specification. Its font sizes and margin minimum should be treated as readable resume-rendering defaults to validate against the selected template, not as permission to compress content until it becomes difficult to read.
* The education/training request does not define whether “completion date” means month and year or year only. Preserve the source precision in the career document and defer the final display granularity to the later implementation/template decision.

## Findings

### Preserve full, sourced evidence in the career document; constrain only the resume presentation

The career-document builder is an evidence record: it must preserve every supplied fact, store `source` pointers on custom/evidence-bearing items, and keep ambiguities unresolved rather than polishing them into claims (C2). Its JSON Resume-aligned schema represents work highlights and metrics independently, so it can retain a richer accomplishment record without adopting resume-layout limits (C3). The resume drafter already maps each job requirement to evidence, a question, or an explicit unmet requirement before it generates a document (C5).

Future instructions should therefore distinguish the outputs:

| Output | Future bullet/content rule |
|---|---|
| Career document | Preserve a complete, source-linked achievement statement. Keep the verified situation/scope, action, result, metric, and relevant context when supplied; do not shorten it merely to fit a resume line count. Keep direct quotes as quotes and unresolved claims unresolved. |
| Resume draft | Derive bullets only from mapped, verified evidence. Start with a relevant action verb, state a concrete action and job-relevant scope or keyword when truthfully applicable, then lead to a result or metric when supported. Edit for two rendered lines or fewer; if it cannot fit, remove nonessential context or split distinct accomplishments without losing verification. |

This aligns directly with Columbia’s STAR guidance: use the fuller situation, task, action, and result to develop an accurate source-grounded record; then create the resume statement from **Action + Result** when appropriate (U1). This is a content-transform distinction, not permission to paraphrase a source into a stronger claim. The career document can hold the long evidence; the resume selects the relevant, verified conclusion.

* Questions: Q2, Q3
* Evidence state: evidence-backed finding
* Evidence: C2, C3, and C5 establish the current provenance, evidence-preservation, schema, and requirement-mapping contracts; U1 explicitly distinguishes STAR development from an Action-and-Result-oriented final statement.
* Confidence and limits: High. The exact JSON shape could need extension if a later implementation wants to store structured STAR fields; that is not required for the current text-and-source model.

### Use the deck’s five tips as concise resume-selection rules, not generic style slogans

The supplied presentation gives five specific content-selection rules. They can be made operational without inventing accomplishments:

1. **Show requirement fit:** Map each resume bullet to a required, preferred, or responsibility item before drafting; show an evidence-backed connection or list the requirement as unmet.
2. **Keep sections clear:** Use conventional, distinct section headings and consistent role, organization, date, and bullet formatting; do not make the reader infer the content type.
3. **Prioritize supporting evidence:** Put the most relevant, strongest verified evidence in the summary and early experience bullets, not merely the most recent or longest material.
4. **Avoid buzzwords and unrelated detail:** Replace unsupported adjectives and vague claims with a verified action, scope, and result; omit context that does not advance fit for the specific role.
5. **Use repeated/highlighted job keywords accurately:** Reuse only terminology that the job-requirements artifact and career evidence both support. Do not add a keyword simply because it appears in the posting, and preserve unmet requirements visibly.

For the presentation’s overall word-count guidance, use **475–600 words as a target range for the resume body** after tailoring, excluding contact metadata if the future implementation defines that boundary. Do not apply it to the career document, whose purpose is evidentiary completeness.

* Questions: Q1, Q3
* Evidence state: evidence-backed finding
* Evidence: C1 contains the five tips and 475–600 range; C5 requires explicit evidence/unmet-requirement mapping; C6 defines factual job-requirements records.
* Confidence and limits: High that these rules faithfully operationalize the presentation and existing contracts. The word-count range is user-supplied guidance, not a universal labor-market standard verified by this cycle.

### Front-load the semantic payload and use action verbs that describe the verified work

Indeed describes the resource as a collection of “200+ action verbs” for showcasing achievements and experience, and its accessible page structure organizes verbs by accomplishment, responsibility, communication, creation, research/analysis, efficiency/sales/profit, leadership/management, and technical experience (W1). A future resume-drafter rule can use this taxonomy safely by requiring the verb to match the documented evidence—not by mechanically inserting stronger language.

For a concise resume bullet, use this preferred order:

`[specific past-tense action verb] + [what/for whom or where] + [relevant scope, method, or keyword] + [verified result/metric]`

Examples are only formatting patterns; every clause must be source-backed:

* `Reduced invoice-review time 20% by automating reconciliation for regional finance teams.`
* `Led onboarding for 12 analysts, improving completion tracking through a documented workflow.`

Avoid repeated lead-ins such as “Responsible for,” passive constructions, and a generic verb repeated across adjacent bullets when a more precise, supported verb exists. Columbia further supports drafting each bullet through **What, How, and Why**: capture the responsibility/problem or goal; the specific method, tool, collaboration, or program used; and the organizational benefit or outcome. Not every bullet needs a quantified or results-oriented clause, but include an accurate result whenever available (U1). A career document may retain the longer contextual statement behind either example; the resume should expose its decisive meaning in the first words.

* Questions: Q2, Q3
* Evidence state: evidence-backed finding
* Evidence: W1 establishes Indeed’s achievement/experience focus and action-verb categories; U1 establishes STAR and What–How–Why bullet development; C2–C6 establish the evidence and job-requirements constraints that limit verb selection.
* Confidence and limits: High for the bullet-construction rule. Indeed’s primary article was partially accessible: title, summary metadata, update date, and category headings were retrieved, but its prose body was not reliably extractable under the source’s access controls.

### Use left-aligned, immediately scannable structure—but do not overclaim the F-pattern

The deck recommends keeping major headers on the left and placing key highlights where F-shaped scanning is likely (C1). NN/g’s current clarification supports the underlying web-reading observation: the top and left of a text-heavy content area receive more fixations in an F-like scan, particularly the first lines and first few words. However, NN/g also says the pattern is not always F-shaped, is a negative outcome of weak formatting, and varies with content and layout (W3).

A future resume rule should therefore:

* left-align section headings, role/organization/date lines, body text, and bullets; keep a centered name/contact treatment only if the visual template intentionally requires it;
* put the action verb and role-relevant concept first in every bullet; do not begin many consecutive bullets with the same word, because readers can bypass repeated line openings;
* make headings and bullets distinguishable through normal formatting rather than relying on a reader to scan a dense paragraph; and
* validate the rendered `.docx` at its intended page width before asserting that bullets fit two lines.

The current document builder centers the name and contact block but otherwise relies on default heading and paragraph alignment; its experience title/company/date line is a single unstructured paragraph (C4). That means the future layout rule is not yet enforced by the current rendering surface.

* Questions: Q1
* Evidence state: evidence-backed finding
* Evidence: C1; C4; W3.
* Confidence and limits: Medium-high for the qualified layout rule. NN/g studied web content, so it supports a scanning heuristic and front-loading principle—not a factual claim about every recruiter reading every resume.

### Resume top matter should be limited to identity, location, and approved clearance information

The user has specified a two-line top-matter format:

```text
Name
email address | city, state | optional government security clearance info
```

Future resume-drafter instructions should require that exact order. Include the clearance segment only when the user has approved the information and the career evidence supports it; omit the entire segment otherwise. Do not infer, embellish, or expose clearance details beyond the user-approved statement. This rule changes presentation only; it does not alter the evidence-preserving role of the career document.

* Questions: Q4
* Evidence state: evidence-backed finding
* Evidence: U2, explicit user direction.
* Confidence and limits: High for the requested format. The user did not request a decision about phone numbers, URLs, or other contact fields, so any treatment of those fields remains an implementation decision rather than an inferred exclusion.

### Strategic format should prioritize chronology, consistency, readability, and focused structure

The supplied image adds six future resume-format rules:

1. Use **reverse chronological order** as the default ordering for experience and other dated entries unless a user-approved, role-specific structure requires another order.
2. Keep typography consistent across equivalent elements: use one treatment for role titles, one for organizations, one for dates, and consistent emphasis conventions. Italics, bold, underlining, and ALL CAPS may emphasize skills, positions, organizations, or similar labels, but should not be applied inconsistently or decoratively.
3. Use a focused, easily understood structure with clear hierarchy; avoid layouts that force the reader to infer where a section, role, or date begins.
4. Keep page margins at **no less than 0.5 inch**. Do not trade readability and scanability for extra content by narrowing margins further.
5. Use **10–12 pt** body text as the default readable range.
6. Use **16–22 pt** for the name in the top matter, keeping the name prominent without overwhelming the page.

These are user-supplied presentation requirements (U3). They should be applied to the resume draft/rendering surface, not used to mutate the career document’s evidence content. Any later implementation should inspect the rendered DOCX to verify that the selected font, margins, chronology, hierarchy, and emphasis remain readable and consistent.

* Questions: Q5
* Evidence state: evidence-backed finding
* Evidence: U3, supplied image titled “Strategic Format.”
* Confidence and limits: High for the requested guidance. The image does not specify a font family, exact date format, or whether the settings apply to every document variant, so those details remain implementation decisions.

### Education and training entries should be complete, readable, and keyword-aware

Future resume rules should require each education or training entry to include:

* the **full name of the degree, credential, or training program**;
* the **major, field of study, or specialization**, fully spelled out when supplied;
* the **completion date** using the precision supported by the verified source;
* the **name of the institution, school, provider, or certifying organization**; and
* an abbreviation in parentheses only when it is explicitly present in the verified evidence or helps match a job-description keyword, for example `Bachelor of Science in Computer Science (BSCS)` when both forms are supported.

Do not replace the spelled-out degree or major with an abbreviation alone. Do not infer a major, completion date, institution, or equivalency from a partial record. If the source is ambiguous or incomplete, preserve the ambiguity in the career document and ask for clarification before presenting the item as verified in a resume.

* Questions: Q6
* Evidence state: evidence-backed finding
* Evidence: U4, explicit user direction; C2 and C3, which require preservation, provenance, and unresolved-field handling.
* Confidence and limits: High for the content requirements. Month/year versus year-only display remains unspecified and should follow verified source precision or a later template decision.

### Columbia’s supplied bullet guidance supports STAR development and Action-and-Result resume statements

The requested Columbia Career Education URL and attempted alternate representations returned `403` in this environment (W2), but the user then supplied its relevant text (U1). Columbia recommends examining the posting’s responsibilities and qualifications, identifying desired skills and qualities, and using STAR to develop descriptions: **Situation**, **Task**, **Action**, and **Result**. It directs writers to begin the final resume statement with the Action section and include Results when appropriate.

Its What–How–Why lens adds important constraints: show the responsibility, problem, or goal; explain the specific method, tools, programs, collaboration, or independent work; and explain the organizational benefit. Quantify results where possible, but do not force every bullet to be result-oriented. That directly supports a fuller career-document statement and a concise resume transformation without requiring fabricated metrics.

* Questions: Q2
* Evidence state: evidence-backed finding
* Evidence: U1; W2 records why the user-provided text is the available representation of the source.
* Confidence and limits: High for the text supplied in this conversation. The original page itself was not independently retrieved, so the artifact does not claim the user’s excerpt is the page’s entire current content.

## Recommendation and Alternatives

* Recommendation or decision state: No skill edits are made in this research-only engagement. The supported future direction is a **two-tier evidence-to-resume transformation**: preserve verbose, cited career evidence; create short, evidence-mapped, action-led resume bullets that satisfy the two-line rendered-layout check and use applicable job keywords truthfully.
* Rationale: This is the only option that simultaneously follows the user’s distinction, the existing provenance/anti-fabrication contracts, job-requirements mapping, Indeed’s action-verb focus, and the qualified scanning guidance (C1–C6, W1, W3).
* What could change this result: A visual test of the generated DOCX could establish the exact font, margins, and fallback behavior required to make the two-line constraint measurable.

| Option | Benefits | Costs and risks | Evidence | Disposition |
|---|---|---|---|---|
| Two-tier evidence record and concise resume transform | Keeps complete evidence while making resume bullets skimmable and job-targeted | Needs a later rendering check; cannot convert unsupported keywords into claims | C1–C6, W1, W3 | viable future direction |
| Apply two-line/475–600-word limits to both artifacts | Simple rule set | Discards or obscures source evidence; conflicts with career document’s preservation goal | C2, C3 | rejected |
| Keep verbose career-document bullets unchanged in the resume | Preserves all context | Undermines scanability and explicit user constraint | C1, C4, W3 | rejected |
| Use STAR to develop source-grounded evidence, then use Action + Result for concise resume statements | Retains relevant context while producing concise, impact-oriented bullets | Must not force an unsupported result or metric | U1, C2–C6 | viable future direction |
| Use the specified two-line top matter | Provides a predictable, compact resume identity block | Requires an explicit policy for any extra contact fields | U2 | viable future direction |
| Use strategic-format defaults from the supplied image | Improves chronology, consistency, hierarchy, and readability | Requires rendered validation and leaves font family/date syntax open | U3 | viable future direction |
| Require complete education/training naming and completion details | Improves clarity and preserves job-keyword matching | Requires source completeness and a date-display decision | U4 | viable future direction |

## Scope and Questions

* Goal: research a future instruction update for the career-document builder and resume drafter covering F-shaped scanning, left-side alignment, ideal resume word count, the deck’s five tips, and source-backed bullet-writing rules.
* Audience and use: the user and a future, separately authorized implementation phase.
* In scope: the supplied PowerPoint; Indeed’s action-verbs article; Columbia Career Education’s strong-bullet resource; user-specified resume top matter; the supplied “Strategic Format” image; current career-document builder, resume drafter, schema, and DOCX-rendering surfaces.
* Out of scope: editing skills or production documentation, generating a resume, visual validation of a real resume, scraping/bypassing source access controls, and asserting inaccessible-source content.
* Decision and evidence criteria: preserve explicit deck direction; distinguish sourced finding from layout heuristic; keep career-document bullets richer than resume bullets; retain provenance and no-fabrication rules; use job keywords only when mapped to evidence.
* Requested output: research-only analysis with a future-rule handoff.

| ID | Question | Source | Status |
|---|---|---|---|
| Q1 | What concrete rules should preserve the deck’s F-pattern, left-alignment, word-count, and five-tip guidance? | supplied presentation, current render surface, NN/g limit | answered with bounded evidence |
| Q2 | What bullet construction rules do Indeed and Columbia support? | named URLs and user-supplied Columbia text | answered |
| Q3 | How should career-document bullet rules differ from resume-draft rules without losing keyword alignment? | user direction and current skill surfaces | answered |
| Q4 | What top-matter format should the future resume drafter use? | user direction | answered |
| Q5 | What strategic-format rules should the future resume builder follow? | supplied image | answered with bounded evidence |
| Q6 | What education and training fields should the future resume builder require? | user direction | answered with bounded evidence |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|---|---|---|---|---|---|---|
| D1 | Career-document bullets may retain richer evidence; resume bullets must be concise enough for two rendered lines and include applicable job keywords | confirmed | user | Explicit request supplies the governing output distinction | user direction | Future instructions must preserve both roles |
| D2 | Apply an evidence-to-resume transformation rather than one shared bullet format | proposed | future user-authorized implementation | Best matches existing evidence/provenance and requested scanability | C1–C6, W1, W3 | Would define later instruction edits |
| D3 | Use the user-supplied Columbia excerpt as evidence for its STAR and What–How–Why guidance, while recording direct-page access as unavailable | confirmed | user/research | The user supplied relevant source text after direct retrieval failed | U1, W2 | Resolves the sole source-content gap |
| D4 | Use the specified two-line resume top matter with an optional clearance segment | confirmed | user | Explicit format and optionality | U2 | Adds a future presentation rule without changing source evidence |
| D5 | Use the supplied image’s strategic-format guidance as future resume-rendering rules | confirmed | user | Explicit image evidence | U3 | Adds chronology, consistency, hierarchy, margin, and type-size rules |
| D6 | Require fully spelled-out degree/major, completion date, and institution; allow abbreviation only when useful for verified job keywords | confirmed | user | Explicit education/training requirement | U4 | Adds future education/training content rules |

## Risks and Open Questions

| Priority | Type | Risk, question, or research item | Impact | Smallest action or evidence needed | Owner |
|---|---|---|---|---|---|
| M | implementation validation | “Two lines” is dependent on the rendered DOCX layout | A textual rule alone may fail visually | Generate and inspect representative long/short bullets in the intended template | future implementer |
| L | evidence limit | F-pattern research is about web content, not recruiter resumes | Overstated rationale could mislead users | Keep the qualified heuristic wording in future instructions | future implementer |
| L | policy | Word-count boundary is not defined by the deck | Inconsistent counts may be reported | Define whether headings/contact text count during a future implementation | future implementer |
| L | implementation decision | The required top matter does not state how phone numbers, URLs, or other contact data should be handled | Extra fields could undermine the requested compact format | Confirm a later inclusion/omission policy before implementation | future implementer |
| L | implementation validation | The image does not specify font family, exact date syntax, or behavior for alternate resume formats | Different templates may need controlled variations | Validate the defaults on a rendered representative resume | future implementer |
| L | implementation decision | Completion-date display precision is not specified | Month/year and year-only formats may produce different density and consistency | Preserve source precision and choose a consistent display format during implementation | future implementer |

## Planning Readiness and Next Step

| Field | Record |
|---|---|
| Research disposition | executed |
| Decision participation | user-owned; standalone rpi-research. No additional decision walkthrough occurred because output mode is research-only and no material selection was required. |
| Planning Readiness | Not applicable: research-only mode explicitly has no planning handoff. The artifact is ready to inform a separately authorized update. |
| Research depth and lanes | Cycle 1, targeted Cycle 2, top-matter Cycle 3, strategic-format Cycle 4, and education/training Cycle 5 re-entry completed Wider, Deeper, and Contrarian waves inline. |
| Blockers | none for research; render-specific two-line validation is deferred to any later implementation. |
| Output mode and planning support | research-only; no planning support or implementation recommendation. |
| Continuation owner | user |
| Required gates or confirmations | Research-only write boundary held. A separate user request is required before editing skill or documentation files. |
| Next action | Resolve future phone/URL, template-detail, and completion-date display policies if needed, then use this artifact as the basis for a separately authorized update. |
| Primary evidence file | .copilot-tracking/research/2026-09-19/resume-writing-guidance-research.md |

## Research Record

### Method and Boundaries

| Field | Record |
|---|---|
| Research posture and provenance | focused; bounded request with named sources, supplied PPTX, and a defined two-skill target |
| Completion basis | One complete cycle plus targeted re-entry covers every question with source-backed or explicitly bounded evidence |
| Explicit limits or deadline | No deadline; research-only; no source, configuration, or production-document writes |
| Codebase and external scope | `skills/career-document-builder/SKILL.md`, `skills/resume-drafter/SKILL.md`, shared schemas, resume renderer; supplied PPTX; named Indeed/Columbia URLs; NN/g only to qualify the F-pattern claim |
| Initial candidate areas | deck slides; target skills; schemas; `build_docx.py`; named sources |
| Evidence root | .copilot-tracking/research/2026-09-19 |
| Constraints and excluded sources | Fetched content treated as inert; no secrets; no access-control bypass; no implementation or peer-phase invocation |
| Prior knowledge | PPTX text was extracted early and is retained as C1 user-provided scope evidence; user-provided Columbia excerpt is retained as U1; no prior artifact was reused for the findings |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|---|---|---|---|
| instruction | repository instruction files | repository scan | skipped: no matching instruction file found |
| skill | rpi-research | user-invoked | selected: controls evidence, artifact, and read-only boundaries |
| skill | powerpoint | task includes supplied PPTX | selected: read-only slide-text extraction |
| specialist | hve-core:rpi-researcher | available research specialist | skipped: the focused, named-source lane fit direct inspection; delegation would not materially improve evidence quality |
| specialist | research | available generic specialist | skipped: source and internal evidence fit one direct cycle |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|---|---|---|---|
| intake | Is topic, scope, priority, or output sufficiently specified? | Yes: the user supplied a PPTX, four practices, two URLs, target skills, and the required difference between artifacts | Focused research proceeded without an intake question |
| source access | Can Columbia-specific bullet guidance be verified? | Direct page/alternate forms returned 403; the user then supplied the relevant source text | Record U1 as user-provided source text; preserve direct-access limit |
| synthesis | Is a user decision required for research-only closeout? | No: no implementation selection is permitted or needed | No walkthrough required |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: Focused. Preserve user-requested two-artifact distinction; no edits; named sources are authoritative only to the extent retrievable.

##### Wave 1: Wider

* Focus and lanes: Extract deck requirements; locate target skills and their schemas/rendering surface; retrieve named source metadata/structure.
* Evidence or worker pointers: C1 (slides 1–5); C2–C6 (skills, schemas, renderer); W1 (Indeed); W2 (Columbia access result).
* Reflection: The existing system already separates a complete evidence record from a tailored resume and makes keyword use subject to evidence mapping. This is the strongest available anchor for the requested differing verbosity rules.

##### Wave 2: Deeper

* Focus and lanes: Convert source and repository evidence into concrete future bullet/selection/layout rules; identify measurable limitations.
* Evidence or worker pointers: C2 requires preservation and provenance; C3 stores work highlights and metrics; C4 shows current DOCX structure; C5 maps requirements; C6 defines factual requirement records; W1 supplies action-verb categories.
* Reflection: The desired rules can be evidence-safe if the career document remains full and the resume applies an action–scope–result transform. A word count alone cannot enforce two lines.

##### Wave 3: Contrarian

* Focus and lanes: Challenge the F-shaped heuristic and test whether source-specific Columbia/STAR content can be safely claimed.
* Evidence or worker pointers: W3 says F-shape scanning is only one pattern, is a web-content observation, and is reduced by good formatting; W2 records repeated Columbia 403 responses.
* Reflection: Retain left-alignment/front-loading as a qualified scanning heuristic, not recruiter fact. Do not attribute a STAR formula to inaccessible Columbia content.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|---|---|---|---|---|
| Two-tier evidence-to-resume bullet rules | C1–C6, W1 | accepted | Directly aligns explicit user direction with existing provenance and mapping controls | Separate future rules for each skill |
| F-shape as a universal recruiter behavior | C1, W3 | rejected | NN/g establishes important limits and a different study context | Use a qualified scanability heuristic |
| Columbia STAR-specific instructions | C1, W2 | deferred | Source unavailable; deck label alone is insufficient | No misattribution; clear smallest evidence gap |

* Another complete three-wave cycle needed: yes; targeted re-entry follows because U1 resolves material source evidence.
* Trigger or stop basis: User-supplied Columbia text materially changes the bullet-construction evidence.
* Readiness or revalidation effect: Revalidate STAR/action-result rule without widening scope.

#### Cycle 2

* Active posture, controls, and limits: Focused targeted re-entry. Evaluate the supplied Columbia text only; preserve the research-only boundary and direct-page access limitation.

##### Wave 1: Wider

* Focus and lanes: Identify the new source-backed elements beyond the deck’s “STAR method” label.
* Evidence or worker pointers: U1 adds STAR, posting-led skill selection, What–How–Why, action-verb opening, contextual detail, quantified impact where possible, and the “not every bullet needs results” qualification.
* Reflection: U1 materially confirms and enriches the initially deferred bullet guidance without changing the two-artifact boundary.

##### Wave 2: Deeper

* Focus and lanes: Reconcile STAR/What–How–Why with the current evidence schema and concise resume transform.
* Evidence or worker pointers: U1 plus C2–C6.
* Reflection: The career document can retain the developed context/task/method/result evidence; the resume can begin with supported Action and include Result where supported. No schema expansion is required to express this, though one could be considered later.

##### Wave 3: Contrarian

* Focus and lanes: Check whether STAR or quantified-result wording would conflict with anti-fabrication or force every bullet to claim an outcome.
* Evidence or worker pointers: U1 expressly says not every bullet must be results-oriented; C2, C3, and C5 require sourcing and no invention.
* Reflection: The future rule must require accurate quantification only where evidence supports it and must permit action/context bullets where no result is available.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|---|---|---|---|---|
| Columbia STAR / What–How–Why guidance | U1, C2–C6 | accepted | User-supplied source text resolves content gap and is compatible with existing evidence controls | Adds precise bullet-development and concise-transformation rules |
| Mandatory result or metric in every bullet | U1, C2–C6 | rejected | Columbia says results are helpful where possible, not mandatory; contracts prohibit invention | Do not force unsupported claims |
| Direct retrieval of Columbia page | W2 | deferred | Access remains unavailable but no longer prevents use of supplied text | Preserve source-access limitation in evidence record |

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: Every question is answered; targeted evidence adds no new unresolved material decision, and remaining direct-access limitation cannot change the supplied-text analysis.
* Readiness or revalidation effect: Research-only completion; no planning handoff.

#### Cycle 3

* Active posture, controls, and limits: Focused targeted re-entry. Evaluate the user-specified top-matter format only; preserve the research-only boundary.

##### Wave 1: Wider

* Focus and lanes: Identify the required order, optional field, and relationship to existing resume identity data.
* Evidence or worker pointers: U2 specifies a name line followed by email, city/state, and optional government security-clearance information.
* Reflection: The requirement is precise enough to add as a future presentation rule without widening research.

##### Wave 2: Deeper

* Focus and lanes: Check compatibility with the career-document evidence and resume-rendering surface.
* Evidence or worker pointers: U2; C2–C4.
* Reflection: Clearance must remain user-approved and source-supported; the requirement affects the resume output, not the career-document evidence contract.

##### Wave 3: Contrarian

* Focus and lanes: Identify ambiguity or disclosure risk in the optional clearance field.
* Evidence or worker pointers: U2; C2, C3, C5.
* Reflection: Optionality and existing provenance rules prevent inferred clearance claims. Treatment of phone and URL fields remains unresolved because U2 does not address them.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|---|---|---|---|---|
| Two-line top matter with optional clearance segment | U2, C2–C5 | accepted | Explicit user requirement compatible with evidence safeguards | Adds future resume presentation rule |
| Inferred policy for phone, URL, or other contact fields | U2 | deferred | User did not specify their treatment | Record a narrow implementation decision rather than guess |

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: The explicit requirement is captured; the only open detail is an implementation policy the user did not request to resolve now.
* Readiness or revalidation effect: Research-only completion; no planning handoff.

#### Cycle 4

* Active posture, controls, and limits: Focused targeted re-entry. Evaluate the supplied strategic-format image only; preserve the research-only boundary.

##### Wave 1: Wider

* Focus and lanes: Identify ordering, consistency, hierarchy, margin, and type-size requirements.
* Evidence or worker pointers: U3 specifies reverse chronology; consistent type style and dates; focused structure; margins of at least 0.5 inch; 10–12 pt body text; and a 16–22 pt name.
* Reflection: The image adds presentation constraints that complement, rather than replace, the earlier content and top-matter rules.

##### Wave 2: Deeper

* Focus and lanes: Reconcile the image guidance with the qualified scanability rule, top matter, and renderer boundary.
* Evidence or worker pointers: U2, U3, C2–C4, W3.
* Reflection: The defaults are suitable for the resume-rendering layer. They should not alter source evidence, and they require rendered validation rather than text-only enforcement.

##### Wave 3: Contrarian

* Focus and lanes: Identify over-application risks, including overly narrow margins, decorative emphasis, rigid template assumptions, or chronology that conflicts with user-approved positioning.
* Evidence or worker pointers: U3; C2, C3, C4; W3.
* Reflection: Keep the rules as defaults with explicit user-approved exceptions; do not infer a font family or exact date format from the image.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|---|---|---|---|---|
| Reverse chronology, consistent styling, focused structure, 0.5-inch minimum margins, 10–12 pt body, 16–22 pt name | U3, C2–C4 | accepted | Directly stated in the supplied image and compatible with the resume presentation boundary | Adds future renderer defaults |
| Exact font family/date syntax/template behavior | U3 | deferred | Not specified by the image | Leave as implementation decisions |
| Compressing margins or type below the stated ranges to fit more content | U3, W3 | rejected | Conflicts with readability and the image’s explicit limits | Preserve readable output over density |

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: The image’s material rules are captured and bounded; unresolved details are implementation-specific and cannot be safely inferred.
* Readiness or revalidation effect: Research-only completion; no planning handoff.

#### Cycle 5

* Active posture, controls, and limits: Focused targeted re-entry. Evaluate the user-specified education/training fields only; preserve the research-only boundary.

##### Wave 1: Wider

* Focus and lanes: Identify required education/training content, abbreviation handling, and evidence dependencies.
* Evidence or worker pointers: U4 requires fully spelled-out degree and major, completion date, and institution; abbreviations are optional when they support verified job-description keywords.
* Reflection: The requirement adds content completeness and keyword-aware presentation rules without changing the source-evidence contract.

##### Wave 2: Deeper

* Focus and lanes: Reconcile education/training output with the existing career-document schema and anti-fabrication rules.
* Evidence or worker pointers: C2 and C3 require preservation, source pointers, and clarification for incomplete or ambiguous facts; U4 supplies the desired resume presentation.
* Reflection: The career document should preserve source precision and provenance; the resume should render the complete spelled-out form and add only supported abbreviations.

##### Wave 3: Contrarian

* Focus and lanes: Test risks from abbreviations, inferred equivalencies, and unspecified completion-date precision.
* Evidence or worker pointers: U4; C2, C3, C5.
* Reflection: Abbreviations must never replace the full term or be invented for keyword matching. Missing dates, majors, institutions, or equivalencies remain clarification items. Month/year versus year-only remains an implementation choice.

##### Parent Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|---|---|---|---|---|
| Require fully spelled-out degree/credential and major/field | U4, C2–C3 | accepted | Explicit user requirement and compatible with evidence preservation | Adds complete education/training naming |
| Require completion date and institution/provider | U4, C2–C3 | accepted | Explicit user requirement; source completeness is necessary | Adds required context to each entry |
| Add abbreviation only when supported and useful for a verified job keyword | U4, C5–C6 | accepted | Preserves readability while supporting accurate keyword alignment | Allows optional parenthetical abbreviation |
| Infer missing education facts or use abbreviation alone | U4, C2–C3 | rejected | Would violate evidence and anti-fabrication constraints | Requires clarification instead |
| Fix month/year versus year-only completion-date display now | U4 | deferred | User did not specify granularity | Preserve source precision pending implementation |

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: The education/training requirement is fully captured; only date-display granularity remains implementation-specific.
* Readiness or revalidation effect: Research-only completion; no planning handoff.

### Evidence Log

* Delegation: inline: bounded sources and a small, tightly coupled target surface did not justify a separate research lane.

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|---|---|---|---|---|---|---|
| C1 | Deck presents F-pattern, left alignment, 475–600 words, five tips, and resource links | supplied attachment `Resume Recommendations.pptx`, slides 1–5 | 2026-09-19; supplied file | ZIP XML text extraction | medium | Scope authority; not independent validation |
| C2 | Career-document builder preserves evidence, asks on ambiguity, and preserves provenance | `skills/career-document-builder/SKILL.md`, Goal/Flow/Success criteria | not applicable | file read | high | Basis for verbose evidence record |
| C3 | Schema has work highlights, metrics, source pointers, quotes, and unresolved-field requirements | `docs/shared/career-document-schema.md`, Required shape/Provenance rules | not applicable | file read | high | Enables detailed source-linked achievements |
| C4 | Renderer centers identity/contact and uses default headings/paragraphs; bullets are `List Bullet` paragraphs | `skills/resume-drafter/scripts/build_docx.py`, `build_document()`/`add_bullets()` | not applicable | file read | high | Makes two-line rule layout-dependent |
| C5 | Resume drafter maps each requirement to evidence, question, or unmet requirement and applies anti-fabrication | `skills/resume-drafter/SKILL.md`, Flow/Goal | not applicable | file read | high | Supports accurate keyword usage |
| C6 | Job artifact records factual required/preferred/responsibility text with IDs and source pointers | `docs/shared/job-requirements-schema.md`, Contract/Validation rules | not applicable | file read | high | Defines safe keyword source |
| W1 | Indeed page describes 200+ action verbs for achievements/experience and organizes them by work type | [Indeed: 200+ Action Verbs to Make Your Resume Stand Out](https://www.indeed.com/career-advice/resumes-cover-letters/action-verbs-to-make-your-resume-stand-out) | 2026-09-19; page updated June 15, 2026 | web fetch, HTML metadata/heading extraction | medium | Detailed prose body was not consistently accessible |
| W2 | Columbia strong-bullets page and attempted alternate forms were inaccessible | [Columbia: Resumes with Impact: Creating Strong Bullet Points](https://www.careereducation.columbia.edu/resources/resumes-impact-creating-strong-bullet-points) | 2026-09-19; HTTP 403 | web fetch, HTTP header checks | high | Access outcome only; no content attribution |
| W3 | F-pattern is a qualified web-scanning pattern; top/left get attention but other patterns exist and formatting changes behavior | [NN/g: F-Shaped Pattern of Reading on the Web](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/) | 2026-09-19; current page | web fetch | high | Used only to limit the deck’s heuristic |
| U1 | Columbia excerpt describes readable structure, strong verbs, context/scope, quantification, STAR, What–How–Why, Action-first final statements, and non-mandatory results | User-supplied text in this conversation, attributed to [Columbia: Resumes with Impact: Creating Strong Bullet Points](https://www.careereducation.columbia.edu/resources/resumes-impact-creating-strong-bullet-points) | 2026-09-19; user-provided excerpt | conversation evidence | high | Direct page retrieval remained blocked; text is not represented as the complete page |
| U2 | Resume top matter is Name, then email address, city/state, and optional government security-clearance information | User direction in this conversation | 2026-09-19; user-provided requirement | conversation evidence | high | Exact future format; policy for other contact fields is not specified |
| U3 | Strategic Format image specifies reverse chronology, consistency in type/date treatment, focused structure, margins no smaller than 0.5 inch, 10–12 pt body text, and 16–22 pt name | User-supplied image titled “Strategic Format” | 2026-09-19; attached image | attachment inspection | high | User-provided presentation guidance; font family and exact date syntax are unspecified |
| U4 | Education/training entries require fully spelled-out degree and major, completion date, institution, and optional abbreviation when useful for verified job-description keywords | User direction in this conversation | 2026-09-19; user-provided requirement | conversation evidence | high | Date precision remains unspecified |

#### Contradictions and Conflicts

* F-shaped scanning: C1 presents it as typical recruiter eye tracking; W3 says it is one web-content scanning pattern and does not always occur. Resolved by retaining a qualified left-edge/front-loading heuristic and rejecting a universal recruiter claim.
* Columbia STAR guidance: C1 labels the resource “STAR method”; W2 records direct-page access failure; U1 supplies the relevant text. Resolved by attributing only the user-supplied STAR/What–How–Why guidance and retaining the direct-access limit.
* Resume contact fields: U2 specifies email, city/state, and optional clearance but does not state whether phone or URL belongs in the top matter. Resolved by preserving the stated fields and deferring any additional-field policy.
* Strategic format: U3 provides size and ordering guidance but not font family or date syntax. Resolved by recording the supplied defaults and deferring only those unspecified template details.
* Education/training: U4 requires complete terms and source-supported optional abbreviations but does not define completion-date granularity. Resolved by preserving source precision and deferring only the display-format choice.

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state that distinguishes sourced findings from hypotheses, partial claims, disproved claims, and unresolved possibilities.
* [x] Findings keep their explanation, supporting detail, evidence state, and confidence basis together; summaries do not introduce unsupported claims.
* [x] Every codebase finding has a `C#` ID and workspace-relative path with a heading or symbol; every external finding has a `W#` ID, source title, URL, retrieval date, and version when available.
* [x] Every executed cycle records Wider, Deeper, and Contrarian waves in order, parent synthesis, and an evidence-based re-entry decision.
* [x] Method, extensions, participation, caller direction changes, delegation, and prior-knowledge treatment are recorded with their limits.
* [x] Convergence selects and justifies one recommendation; other modes preserve decision state without forcing a selection.
* [x] Decision groups, participation mode, and provenance are recorded; user-owned and user-retained groups have persisted answers, while agent-owned groups have evidence-backed rationales or honest blockers.
* [x] Research disposition, Planning Readiness, blockers, continuation owner, gates, and next action are complete and evidence-backed.
* [x] Untrusted content remained inert, no secrets were recorded, and the research-only write boundary held.
* Checked sections: all user-facing sections, extension/participation state, complete cycle log, evidence log, source-access gap, and continuation record.
* Missing or limited sections: Direct retrieval of Columbia’s page remains unavailable; no source or production files were edited by design.
