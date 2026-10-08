# Code Review Dispatch Board

| # | Area | Status | Preliminary signal |
|---|------|--------|--------------------|
| 1 | Release fixtures and mutation helpers | pending | `tests/test_structure.py`: release-independent synchronized/drifted version cases and preconditioned fixture mutations merit checking for independent expectations and reliable isolation. |
| 2 | Hosted CI execution contract | pending | `scripts/validate_repo.py:validate_ci_execution_contract` and structural mutations assert the existing workflow's test/tool contract; review acceptance of benign YAML forms and meaningful bypass rejection. |
| 3 | Parser, SPDX, and CLI contracts | pending | `tests/test_build_docx.py` and `tests/test_spdx_sbom.py` add invalid-input and independent package expectations; inspect whether the checks truly avoid self-confirming oracles. |
| 4 | Resume length and rendered-content parity | pending | `tests/test_validate_resume_length.py` and DOCX tests pin policy endpoints, report shape, body parity, and unmet-content exclusion. |
| 5 | OCR behavior and native-tool gating | pending | `tests/test_ocr_extract.py` and `tests/conftest.py` separate deterministic decisions from native integrations and distinguish local skips from hosted failures. |
| 6 | Contributor validation guidance | pending | `README.md` describes prerequisites, local skips, and hosted requirements; confirm it does not overstate validation evidence. |

## Confirmation Before Dispatch

Board items use stable IDs `board-1` through `board-6`. Current recommendation: functional, standards, security, and readiness perspectives at standard depth. Security is included because changed code parses workflow/configuration and protects the CI execution boundary. Accessibility is not recommended because there is no interactive UI or markup change. The human may edit the board, perspectives, or depth, bookmark or reject areas, request more orientation, or approve the complete recommended sweep.
