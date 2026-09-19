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
3. For each required, preferred, and responsibility item, record either:
   - a specific career-document source mapping;
   - a focused question when a plausible mapping is uncertain; or
   - an explicit unmet requirement when no supporting evidence exists.
4. Present proposed summary, experience, education, skills, awards, and certifications sections to the user in checkpoints. Incorporate explicit answers and edits before finalizing.
5. Apply [`docs/shared/anti-fabrication-contract.md`](../../../docs/shared/anti-fabrication-contract.md) to every sentence and number. Do not silently omit unmet requirements.
6. Write the user-approved intermediate JSON payload and run the bundled `build_docx.py` script:

   ```bash
   python skills/resume-drafter/scripts/build_docx.py \
     --input skills/resume-drafter/scripts/fixtures/sample-resume.json \
     --output resume.docx
   ```

   The input shape is:

   ```json
   {
     "basics": {"name": "Full Name", "email": "name@example.com", "location": "City, Region"},
     "summary": "Approved summary",
     "experience": [{"company": "Employer", "title": "Verified title", "dates": "2020-2024", "bullets": ["Verified bullet"]}],
     "education": [{"institution": "School", "degree": "Degree"}],
     "skills": ["Skill"],
     "awards": [{"title": "Award", "details": "Verified citation"}],
     "unmetRequirements": ["RQ-002"]
   }
   ```

7. Deliver the `.docx` and the visible unmet-requirements note together so the user can decide whether to provide additional evidence.

## Constraints

The script uses `python-docx`; install it with `python -m pip install python-docx`. Exact fonts and page length are ATS-safe implementation details, not permission to embellish content.
