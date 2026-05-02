# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/classify-converge-remaining-prompt-fallbacks/00-story.md`
- Review date: 2026-05-02
- Mode: read-only code review

## Inputs reviewed

- Story contract and AC1-AC5.
- `fallback-classification.md`.
- `generated/03-acceptance-traceability.md`.
- `generated/07-no-legacy-dry-guardrails.md`.
- `generated/10-final-evidence.md`.
- Diff for:
  - `backend/app/domain/llm/prompting/catalog.py`
  - `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
  - `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
  - `_condamad/stories/classify-converge-remaining-prompt-fallbacks/00-story.md`
- Regression guardrails: `RG-018`, `RG-019`, `RG-020`, `RG-021`.

## Diff summary

- Six non-fixture prompt fallback entries were removed from
  `PROMPT_FALLBACK_CONFIGS`.
- `PROMPT_FALLBACK_CONFIGS` now keeps only `test_natal` and `test_guidance`.
- Tests now assert the exact fixture allowlist, builder non-generation for
  converged keys, and persistent audit coverage.
- Persistent CONDAMAD evidence was added under the story capsule.

## Review layers

- Diff integrity: scoped code/test/story changes; `backend/horoscope.db` remains
  a dirty binary worktree file and is outside the story scope.
- Acceptance audit: AC1-AC5 have corresponding code and validation evidence.
- Validation audit: targeted pytest, lint, format check, story validate/lint,
  and `git diff --check` were rerun by reviewer.
- No Legacy / DRY audit: no wrapper, alias, repointed fallback prompt, or second
  fallback registry found in reviewed diff.
- Guardrail audit: RG-018 and RG-021 are directly protected by tests; RG-019 and
  RG-020 were not broadened by this diff.

## Findings

No actionable findings.

## Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `fallback-classification.md` lists all 8 reviewed keys and before/after inventory. |
| AC2 | PASS | Removed keys are absent from `PROMPT_FALLBACK_CONFIGS`; builder guards assert `None`. |
| AC3 | PASS | Exact allowlist test requires only `test_natal` and `test_guidance`. |
| AC4 | PASS | New fallback keys fail the exact allowlist unless tests/audit are updated. |
| AC5 | PASS | Production `missing_assembly` test remains covered in `test_assembly_resolution.py`. |

## Validation audit

Reviewer reran:

```powershell
git diff --check
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .; ruff check .
.\.venv\Scripts\Activate.ps1; cd backend; python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\classify-converge-remaining-prompt-fallbacks\00-story.md; python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\classify-converge-remaining-prompt-fallbacks\00-story.md
```

Results:

- `git diff --check`: PASS.
- Targeted pytest: 59 passed.
- Ruff format check: 1246 files already formatted.
- Ruff check: all checks passed.
- Story validation/lint: PASS.

The full suite was not rerun by the reviewer; `generated/10-final-evidence.md`
records a prior full-suite pass of 3521 passed, 12 skipped.

## DRY / No Legacy audit

- Remaining fallback prompt owner surface is exact and fixture-only.
- Removed canonical/near-nominal keys still exist in runtime metadata, tests,
  seeds, and documentation as expected, but not as fallback prompt entries.
- `build_fallback_use_case_config` now requires both runtime metadata and a
  prompt fallback entry, so removed keys no longer build executable fallback
  configs.

## Commands run by reviewer

- `git status --short`
- `git diff --check`
- `git diff --stat`
- Targeted `rg` scans for fallback keys and forbidden surfaces.
- Targeted pytest, Ruff, and story validation commands listed above.

## Residual risks

- `backend/horoscope.db` remains modified in the worktree and must stay out of
  this story commit unless intentionally handled separately.
- Reviewer did not rerun the full test suite because the targeted checks cover
  the story risk and the existing final evidence records the full run.

## Verdict

ACCEPTABLE_WITH_LIMITATIONS
