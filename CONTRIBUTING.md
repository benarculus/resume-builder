# Contributing

Thanks for helping improve `resume-builder`.

## Before opening a change

- Do not include real resumes, performance reviews, LinkedIn exports, or other personal data. Use synthetic fixtures.
- Read the [anti-fabrication contract](docs/shared/anti-fabrication-contract.md).
- Keep the flattened skill layout: `.github/skills/<skill-name>/SKILL.md`.
- Update the shared contract under `docs/shared/` when changing an artifact interface.

## Local checks

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py
pytest -q
```

## Pull requests

Explain the user-facing behavior, validation performed, and any privacy or security considerations. Contributions that add skill behavior should include a representative synthetic example and preserve explicit clarifying questions for unsupported facts.
