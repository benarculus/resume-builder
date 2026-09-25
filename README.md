# resume-builder

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/benarculus/resume-builder/badge)](https://scorecard.dev/viewer/?uri=github.com/benarculus/resume-builder)

GitHub Copilot CLI skills for building accurate, job-tailored resumes from a verified career document. The workflow is intentionally anti-fabrication: it asks for missing evidence instead of inventing experience, numbers, titles, or accomplishments.

## Release integrity

Each published version includes `resume-builder.spdx.json`, an SPDX 2.3 software bill of materials generated from the tagged source and its pinned runtime dependencies. A small write-capable resolver locates the draft release, then a separate read-only job generates and validates the SBOM. The release remains a draft until the SBOM is uploaded and its downloaded SHA-256 digest matches the generated file. An active release-tag ruleset restricts creation, update, and deletion of `v*` tags to the release GitHub App. GitHub then publishes the release immutably, locking the tag and assets and generating a cryptographic release attestation.

### Release recovery

The publication workflow can be rerun safely while the matching release remains a draft. A run may fail before publication if the draft does not appear within the two-minute lookup window, SBOM generation or validation fails, the workflow artifact cannot be transferred, or the uploaded asset fails checksum verification.

1. Confirm the tag commit is in `main` history and inspect the matching draft release and its `resume-builder.spdx.json` asset.
2. Fix a repository validation or workflow defect through the normal pull-request process. Do not edit the generated SBOM or publish the draft manually.
3. Rerun the failed `Publish release with SPDX SBOM` workflow. Its resolver reuses the existing draft; asset upload is idempotent and the downloaded asset is checksum-verified again before publication.
4. If the tag or draft points to the wrong commit or version, stop and investigate before deleting either object. Deletion is a recovery action, not part of a normal retry.

Do not publish a draft without the verified SBOM. After publication, release immutability locks the tag and assets; corrections require a new release rather than replacing the published artifact.

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

The validation script checks skill frontmatter, `plugin.json`, marketplace metadata, exact runtime dependency pins, the job-requirements producer/consumer contract, and the security-sensitive workflow contracts. Those workflow checks include full-SHA action pins, the least-privilege GitHub App release token, draft release and SPDX publication boundaries, OpenSSF Scorecard permissions, and dependency-gate structure. The test suite covers those policies, validates SPDX preparation and rejection cases, and opens a generated `.docx` to check its sections.

Pull requests also run a centralized advisory malware gate through the pinned reusable workflow `benarculus/malware-advisory-check/.github/workflows/reusable-malware-advisory-check.yml@733acbdf20304f70ac0c9a763921cac4c23882ef` (`v1.0.2`). This repository maps the pull-request base and head SHAs into that workflow explicitly and keeps the local validation commands above for repository structure and regression coverage.

## License

Released under the [MIT License](LICENSE).
