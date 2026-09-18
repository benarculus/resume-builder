---
name: job-requirements-planner
description: Turn one user-supplied job-posting link and optional supplementary links into a source-linked, resume-ready requirements artifact. Use when planning a tailored resume from a specific role.
argument-hint: "[one job posting URL] [optional supplementary URLs]"
license: MIT
user-invocable: true
allowed-tools:
  - computer-use
---

# Job requirements planner

## Goal

Produce a deterministic job-requirements artifact from the exact pages the user names, without crawling, bulk scraping, or bypassing access controls.

## Flow

1. Ask for exactly one primary job-posting URL and zero or more optional supplementary URLs.
2. Open each supplied URL individually with the CLI's browser/computer-use tooling and read only the rendered, visible page content.
3. If a page is blocked, paywalled, unavailable, or requires bypassing a warning, tell the user and ask them to paste the visible text. Never bypass the block.
4. Separate required qualifications, preferred qualifications, responsibilities, and explicit constraints such as compensation, level, and location.
5. Preserve the exact source URL (or a pasted-text pointer) on every extracted item.
6. Write the result in the exact shape defined by [`docs/shared/job-requirements-schema.md`](../../../docs/shared/job-requirements-schema.md).
7. Ask the user to review wording and resolve any ambiguity before passing the artifact to `resume-drafter`.

## Inputs

The primary posting URL is required. Supplementary links, such as a user-provided announcement post, are optional. Process only those links explicitly named in the current conversation.

## Success criteria

- The artifact has all required top-level sections from the shared contract.
- Every requirement is grounded in visible source text.
- No seniority, compensation, location, or qualification is inferred when the posting does not state it.
- The output is ready for deterministic parsing by `resume-drafter`.

## Constraints

This skill processes one user-directed page at a time. It must not crawl related pages, enumerate job postings, follow unrelated links, automate bulk collection, or use anti-bot-bypass techniques. Apply [`docs/shared/anti-fabrication-contract.md`](../../../docs/shared/anti-fabrication-contract.md) to any interpretation.
