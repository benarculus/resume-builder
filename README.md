# resume-builder

GitHub Copilot CLI skills for building accurate, job-tailored resumes from a verified career document. The workflow is intentionally anti-fabrication: it asks for missing evidence instead of inventing experience, numbers, titles, or accomplishments.

## Install

### Plain Agent Skills (portable path)

Clone this repository and copy the three skill directories into the consumer repository:

```bash
mkdir -p .github/skills
cp -R resume-builder/.github/skills/career-document-builder .github/skills/
cp -R resume-builder/.github/skills/job-requirements-planner .github/skills/
cp -R resume-builder/.github/skills/resume-drafter .github/skills/
```

The same directories can be installed under `~/.copilot/skills` for user-wide use. This `.github/skills/<skill-name>/SKILL.md` layout is the portable, standards-based installation path.

### Plugin bundle

This repository also includes `.github/plugin/marketplace.json`, following the marketplace convention used by this environment. The manifest is metadata for hosts that explicitly support this convention; it is not an official GitHub CLI install format, and there is no portable `resume-builder` command that can load it across hosts.

The plain Agent Skills procedure above is the only self-service installation path documented by this repository. If your host supports this bundle convention, use that host's documented **Import marketplace/plugin from a repository** action with `https://github.com/benarculus/resume-builder`; verify that it reads `.github/plugin/marketplace.json`, then invoke the skills by their names. If the host does not provide that importer, use the portable copy procedure instead.

## How the skills fit together

The skills form a research → plan → implement pipeline:

1. [`career-document-builder`](.github/skills/career-document-builder/SKILL.md) gathers and verifies evidence from resumes, reviews, awards, metrics, and user-provided LinkedIn content.
2. [`job-requirements-planner`](.github/skills/job-requirements-planner/SKILL.md) reads one user-supplied job-posting link at a time and produces a structured requirements artifact.
3. [`resume-drafter`](.github/skills/resume-drafter/SKILL.md) maps the career evidence to the requirements, asks clarifying questions, and renders an approved draft as a Word document.

Shared contracts live in [`docs/shared`](docs/shared/).

## Quickstart

1. Run `career-document-builder` with your prior resumes, performance-review excerpts, award citations, metrics, and a LinkedIn export or pasted profile content. Review and correct the resulting `career-document.json`.
2. Run `job-requirements-planner` with the job-posting URL and any optional supplementary links. Review the resulting `job-requirements.json`; blocked or paywalled pages must be supplied as pasted text rather than bypassed.
3. Run `resume-drafter` with both artifacts. Answer its evidence questions, approve the mapped sections, and let it run `build_docx.py` to write `resume.docx`.

The plugin will not invent resume content. Requirements without supporting career evidence are listed as unmet or turned into explicit questions for you.

## Validation

Install development dependencies and run the same checks used by CI:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py
pytest -q
```

The validation script checks skill frontmatter, the marketplace manifest, and the job-requirements producer/consumer contract. The test suite opens a generated `.docx` and checks its sections.

## License

Released under the [MIT License](LICENSE).
