## Summary

Adds evidence-grounded resume-writing guidance and updates the DOCX renderer so career documents retain complete source-linked evidence while tailored resumes use concise, readable, job-relevant presentation.

The change adds STAR/What–How–Why and action-verb rules, verified keyword mapping, education/training requirements, requested top matter with optional clearance, reverse chronology, readability defaults, and regression coverage. Existing phone and URL fields remain supported after the requested identity/location/clearance fields.

## Validation

- [x] `python scripts/validate_repo.py`
- [x] `pytest -q`

Additional preflight checks: `python3 -m py_compile skills/resume-drafter/scripts/build_docx.py tests/test_build_docx.py`, representative DOCX generation, and `git diff --check`.

## Anti-fabrication and privacy

- [x] No personal, confidential, or real resume data is included.
- [x] Any new skill behavior preserves source pointers and clarifying questions.
- [x] Unmet job requirements remain visible rather than being filled with invented claims.

## Checklist

- [x] README or shared contracts updated when behavior changed.
- [x] Tests added or updated for executable behavior.
- [ ] Security-sensitive changes are called out in the description.

## Review outcome

The completed implementation was reviewed against the full approved plan and found conformant. No substantive review findings or follow-up routes remain. The review noted that exact two-line visual wrapping is not independently measured across arbitrary DOCX widths and fonts; this remains a documented validation limitation rather than an observed defect.
