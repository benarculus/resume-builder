---
name: resume-drafter
description: Draft an evidence-grounded, job-tailored Word resume from a career document and job-requirements artifact, asking clarifying questions instead of inventing unsupported content.
argument-hint: "[career-document.json] [job-requirements.json]"
license: MIT
user-invocable: true
allowed-tools:
  - shell
---

# Resume drafter

## Goal

Map verified career evidence to a specific role, make unsupported requirements visible, and render only user-approved content as a Word document.

## Flow

1. Load and validate the career document against [`docs/shared/career-document-schema.md`](../../../docs/shared/career-document-schema.md).
2. Load and validate the job-requirements artifact against [`docs/shared/job-requirements-schema.md`](../../../docs/shared/job-requirements-schema.md). Reject alternate shapes instead of guessing how to parse them.
3. Before drafting any section content, ask the user which optional sections to include in this resume: Skills, Awards, both, or neither. Use a fixed-choice question consistent with the rest of the pipeline's clarifying-question style. Summary, Experience, and Education are always included and are not part of this question. Use the answer to scope which sections are drafted in the remaining steps.
4. For each required, preferred, and responsibility item, record either:
   - a specific career-document source mapping;
   - a focused question when a plausible mapping is uncertain; or
   - an explicit unmet requirement when no supporting evidence exists.
5. Present proposed summary, experience, and education sections, plus skills and awards only when the user chose to include them in step 3, to the user in checkpoints. Incorporate explicit answers and edits before finalizing. By this point the section list itself is no longer open; only the drafted content within the already-chosen sections is under review.
6. Apply [`docs/shared/anti-fabrication-contract.md`](../../../docs/shared/anti-fabrication-contract.md) to every sentence and number. Do not silently omit unmet requirements.
7. Write the user-approved intermediate JSON payload and run the bundled `build_docx.py` script:

   ```bash
   python skills/resume-drafter/scripts/build_docx.py \
     --input path/to/approved-resume.json \
     --output resume.docx
   ```

   `path/to/approved-resume.json` is the user-approved payload written in this step, not the bundled `skills/resume-drafter/scripts/fixtures/sample-resume.json` test fixture. The input shape is:

   ```json
   {
     "basics": {"name": "Full Name", "email": "name@example.com", "location": "City, Region"},
     "summary": "Approved summary",
     "experience": [{"company": "Employer", "title": "Verified title", "dates": "2020-2024", "bullets": ["Verified bullet"]}],
     "education": [{"institution": "School", "degree": "Degree", "major": "Field", "completionDate": "2024-05"}],
     "skills": ["Skill"],
     "awards": [{"title": "Award", "details": "Verified citation"}],
     "unmetRequirements": ["RQ-002"]
   }
   ```

8. Run the bundled length-validation script against the rendered `.docx` and the same approved payload written in step 7:

   ```bash
   python skills/resume-drafter/scripts/validate_resume_length.py \
     --docx resume.docx \
     --payload path/to/approved-resume.json
   ```

   Treat a failing `withinWordBudget` or `withinPageCap` result as a hard gate: a resume that fails validation is never delivered through the normal path in step 9. Trim content and repeat steps 7–8 until both checks pass. Only when the user explicitly requests an exception may an over-budget resume be delivered — through a distinct, named override checkpoint, never the normal delivery step — and the override and its reason must be disclosed in the chat/summary response.
9. Deliver the `.docx` and, in the chat/summary response only (never inside the document itself), the visible unmet-requirements note so the user can decide whether to provide additional evidence.

## Resume content and formatting rules

- Derive every bullet from mapped, verified career evidence. Start with a precise past-tense action verb that matches the documented work, then front-load the relevant action, scope, method or tool, supported job keyword, and result or metric when available.
- Draft the underlying evidence with STAR and What–How–Why, then select the concise Action-plus-Result wording for the resume when appropriate. Do not add a result, number, keyword, credential, or stronger verb merely because it appears in the job posting.
- Prefer concise bullets that fit within two rendered lines at the selected document width. Remove nonessential context or split distinct accomplishments only when the evidence remains intact; do not silently discard a required or unsupported-to-omit fact. The career document remains verbose and is not subject to this limit.
- Target 475–600 words for the tailored resume body, excluding contact metadata, and a maximum 2-page rendered length. Both are enforced, not merely documented: run `skills/resume-drafter/scripts/validate_resume_length.py` (see `Flow` step 8) before delivery, and treat a failing result as a hard gate rather than permission to omit mapped requirements or fabricate filler.
- Use the five selection rules from the supplied resume guidance: show requirement fit, keep sections clear, prioritize the strongest relevant evidence, avoid buzzwords and unrelated detail, and reuse job-description keywords only when both the requirements artifact and career evidence support them. Keep unsupported or unmet requirements visible.
- Use a focused, left-aligned structure with conventional section headings, reverse chronological ordering for dated entries by default, and consistent role, organization, date, typography, and emphasis treatment. Use bold, italics, underlining, or all caps intentionally rather than decoratively.
- Use reverse chronological experience ordering by default. A user-approved alternative ordering may be represented with the top-level payload field `"experienceOrder": "approved"`; otherwise use `"reverseChronological"` or omit the field. Never infer approval from the payload order alone.
- Use the following top matter order:
  ```text
  Name
  email address | city, state | optional government security clearance info
  ```
  Include the clearance segment only when the user explicitly approves it and the career document supports it. Do not infer clearance level, status, or eligibility.
- Education and training entries must show the fully spelled-out degree, credential, or program; fully spelled-out major, field, or specialization when supplied; completion date; and institution/provider. An abbreviation is optional and may appear only when evidence-supported and useful for a verified job-description keyword; it must not replace the full term.
- Apply the renderer defaults of at least 0.5-inch margins, 10–12 pt body text, and 16–22 pt name text. Validate the generated document because line count depends on the selected font, margins, and available width; do not claim that a word or character count guarantees two lines.

## Constraints

The script uses `python-docx`; install it with `python -m pip install python-docx`. Exact fonts and page length are ATS-safe implementation details, not permission to embellish content.
