---
name: career-document-builder
description: Build a verified, JSON Resume-aligned career document from user-supplied resumes, performance reviews, award citations, metrics, and LinkedIn profile content. Use when a user needs a reliable source of career evidence before tailoring a resume.
argument-hint: "[source files, pasted evidence, or a LinkedIn export]"
license: MIT
user-invocable: true
allowed-tools: []
---

# Career document builder

## Goal

Create one machine-friendly career document from the evidence the user supplies, while preserving provenance and asking questions instead of guessing.

## Flow

1. Ask the user to provide whatever source mix they have: prior resumes, performance-review text or files, award citations, metrics, and a LinkedIn export or pasted profile content.
2. Inventory every source and assign stable source pointers before synthesizing facts. For a source that yields no extractable text through normal reading (an image file, or an image-based PDF page with no text layer), run the bundled OCR script before fact extraction continues:

   ```bash
   python skills/career-document-builder/scripts/ocr_extract.py \
     --input path/to/scanned-source.pdf \
     --output path/to/extracted-source.txt
   ```

   OCR output is raw extracted text, not verified fact; treat it the same as any other source and apply the ambiguity and clarifying-question rules in step 4 to whatever it returns.
3. Extract candidate facts into the contract in [`docs/shared/career-document-schema.md`](../../../docs/shared/career-document-schema.md).
4. For every ambiguous, conflicting, missing, or internally inconsistent fact, ask a focused clarifying question. Do not choose the most plausible answer.
5. Preserve every supplied fact. If a fact does not fit the schema, keep it in an evidence note and ask the user how it should be represented.
6. Add `source` pointers to every custom extension item and to evidence-bearing highlights.
7. Validate that `basics` is present, custom extension arrays are structurally valid, and each custom item has a source pointer.
8. Present the complete career document for user review before treating it as ready for the resume drafter.

## Evidence-writing rules

- Preserve the complete verified context behind an accomplishment. When supplied, retain the situation or problem, task or responsibility, action and method, result or organizational impact, scope, tools, collaboration, and metrics. This is the evidence record and is not constrained by the resume's 475–600-word target or two-rendered-line bullet preference.
- Use STAR (Situation, Task, Action, Result) and What–How–Why questions to organize discovery and clarify what the user did, how they did it, and why it mattered. Do not turn those prompts into inferred facts, stronger claims, or invented outcomes.
- Preserve an accurate result when one is supplied, but do not require a result or quantified metric for every evidence item. Keep unresolved results unresolved and ask a focused question when the missing detail is material.
- Keep the full spelled-out degree, credential, training program, major, field of study, or specialization as the canonical value. Preserve an abbreviation only as an additional evidence-supported form; it may be useful later for a verified job-description keyword, but it must never replace the full term.
- Education and training records must retain the completion date and institution, school, provider, or certifying organization when supplied. Do not infer a date, institution, degree, major, or equivalency from an abbreviation or context.

## Inputs

Accept files, pasted text, or explicit user answers. Do not fetch LinkedIn or infer profile information from a public page; the user must provide an export or pasted content.

## Success criteria

- The output follows the shared career-document schema.
- No unresolved ambiguity is presented as fact.
- No supplied evidence is silently omitted.
- A reviewer can trace custom evidence to its source pointer.

## Constraints

Follow the binding rules in [`docs/shared/anti-fabrication-contract.md`](../../../docs/shared/anti-fabrication-contract.md). The output is a verified evidence record, not a polished resume.
