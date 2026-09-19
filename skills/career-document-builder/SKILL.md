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
2. Inventory every source and assign stable source pointers before synthesizing facts.
3. Extract candidate facts into the contract in [`docs/shared/career-document-schema.md`](../../../docs/shared/career-document-schema.md).
4. For every ambiguous, conflicting, missing, or internally inconsistent fact, ask a focused clarifying question. Do not choose the most plausible answer.
5. Preserve every supplied fact. If a fact does not fit the schema, keep it in an evidence note and ask the user how it should be represented.
6. Add `source` pointers to every custom extension item and to evidence-bearing highlights.
7. Validate that `basics` is present, custom extension arrays are structurally valid, and each custom item has a source pointer.
8. Present the complete career document for user review before treating it as ready for the resume drafter.

## Inputs

Accept files, pasted text, or explicit user answers. Do not fetch LinkedIn or infer profile information from a public page; the user must provide an export or pasted content.

## Success criteria

- The output follows the shared career-document schema.
- No unresolved ambiguity is presented as fact.
- No supplied evidence is silently omitted.
- A reviewer can trace custom evidence to its source pointer.

## Constraints

Follow the binding rules in [`docs/shared/anti-fabrication-contract.md`](../../../docs/shared/anti-fabrication-contract.md). The output is a verified evidence record, not a polished resume.
