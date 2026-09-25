# resume-builder

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/benarculus/resume-builder/badge)](https://scorecard.dev/viewer/?uri=github.com/benarculus/resume-builder)

GitHub Copilot CLI skills for building accurate, job-tailored resumes from a verified career document. The workflow is intentionally anti-fabrication: it asks for missing evidence instead of inventing experience, numbers, titles, or accomplishments.

## Install

### System prerequisites

`career-document-builder`'s OCR extraction script and `resume-drafter`'s length-validation script depend on two system-level binaries that are not installable through `pip`:

* [`tesseract-ocr`](https://github.com/tesseract-ocr/tesseract) — the OCR engine `pytesseract` wraps, used to extract text from scanned or image-based career-document sources.
* [LibreOffice](https://www.libreoffice.org/) (providing the `soffice` CLI) — used to render a tailored resume `.docx` to PDF for an actual rendered page-count check.

Install both with your OS package manager before running the skills locally, for example:

```bash
# Debian/Ubuntu
sudo apt-get install -y tesseract-ocr libreoffice

# macOS (Homebrew) — LibreOffice is a cask, so it needs a separate install
brew install tesseract
brew install --cask libreoffice
```

### Python runtime dependencies

The same scripts also depend on Python packages (`pytesseract`, `pymupdf`, `pillow`, `python-docx`) that must be installed separately from the system binaries above. This is required to run `career-document-builder`'s OCR extraction and `resume-drafter`'s length validation and document rendering, regardless of which install path below you use. It is distinct from `requirements-dev.txt`, which is only needed by repository contributors running the test suite.

If you have a checkout of this repository, install the pinned versions from [`requirements.txt`](requirements.txt):

```bash
python -m pip install -r requirements.txt
```

Otherwise (for example after a direct or marketplace plugin install with no local checkout), install the same pinned versions directly — check [`requirements.txt`](requirements.txt) for the current pins, which at the time of writing are:

```bash
python -m pip install python-docx==1.2.0 pytesseract==0.3.13 pymupdf==1.26.7 pillow==12.3.0
```

### Direct plugin install

Install the Agent Plugins 1.0 package directly from this repository:

```bash
copilot plugin install benarculus/resume-builder
```

Verify that the plugin is installed from your shell:

```bash
copilot plugin list
```

Inside Copilot CLI, verify that the plugin and skills are visible:

```text
/plugin list
/skills list
```

### Marketplace install

This repository also includes official marketplace metadata at `.github/plugin/marketplace.json`. Add the marketplace repository, then install the plugin from that marketplace:

```bash
copilot plugin marketplace add benarculus/resume-builder
copilot plugin install resume-builder@resume-builder
```

The marketplace manifest points at the repository root (`"."`), which contains `plugin.json` and the root `skills/` directories required by Agent Plugins 1.0.

## How the skills fit together

The skills form a research → plan → implement pipeline:

1. [`career-document-builder`](skills/career-document-builder/SKILL.md) gathers and verifies evidence from resumes, reviews, awards, metrics, and user-provided LinkedIn content.
2. [`job-requirements-planner`](skills/job-requirements-planner/SKILL.md) reads one user-supplied job-posting link at a time and produces a structured requirements artifact.
3. [`resume-drafter`](skills/resume-drafter/SKILL.md) maps the career evidence to the requirements, asks clarifying questions, and renders an approved draft as a Word document.

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

The validation script checks skill frontmatter, `plugin.json`, marketplace metadata, workflow SHA pins, exact direct dependency pins, dependency-gate workflow structure, and the job-requirements producer/consumer contract. The test suite opens a generated `.docx` and checks its sections.

Pull requests also run a centralized advisory malware gate through the pinned reusable workflow `benarculus/malware-advisory-check/.github/workflows/reusable-malware-advisory-check.yml@7a825d2fdb99f459bb4595cf999a5faaa883d87f` (`v1.0.1`). This repository maps the pull-request base and head SHAs into that workflow explicitly and keeps the local validation commands above for repository structure and regression coverage.

## License

Released under the [MIT License](LICENSE).
