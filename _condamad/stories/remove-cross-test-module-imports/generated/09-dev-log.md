# Dev Log

## Preflight

- `git status --short` showed `_condamad/stories/remove-cross-test-module-imports/` and `_condamad/stories/replace-seed-validation-facade-test/` as untracked before implementation.
- `AGENTS.md` and `_condamad/stories/regression-guardrails.md` were read.
- Applicable guardrails: `RG-005`, `RG-006`.

## Baseline search

- Cross-test import scan found 9 hits before implementation.

## Implementation notes

- Added non-executable helper owners for billing, ops alerts, entitlement alert handling, and regression engine input helpers.
- Updated all 9 consumers to import helper owners directly.
- Added AST guard `app/tests/unit/test_backend_test_helper_imports.py`.
- Full `pytest -q` initially failed on DB harness classification for the three new helper files; fixed by classifying them in the existing DB guard/allowlist, then reran the full suite successfully.
