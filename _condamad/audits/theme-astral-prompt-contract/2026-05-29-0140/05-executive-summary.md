# Executive Summary

Audit folder: `_condamad/audits/theme-astral-prompt-contract/2026-05-29-0140/`.

Verdict: corrections required before final closure.

Findings:

- 0 Critical
- 0 High
- 1 Medium: official provider examples keep known Paris birth context only in `chart_id` while structured `birth_context` fields are null.
- 0 Low
- 2 Info: provider smoke external call skipped without opt-in; mixed source material is disclosed and accepted.

Validation:

- `ruff check .`: PASS.
- Targeted theme astral pytest set including provider smoke file: PASS with `16 passed, 1 skipped, 9 deselected`.
- Provider-smoke marker run: SKIPPED by missing opt-in with `1 skipped, 3 deselected`.
- Domain-audit validate/lint: PASS. `condamad_domain_audit_validate.py` and `condamad_domain_audit_lint.py` passed for this folder after review; see E-015.

Recommended next action: create the CS-378 remediation from SC-001 and close F-001 by regenerating or correcting the final provider example payloads plus validator coverage.
