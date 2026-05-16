# Final Evidence CS-176

## Story status

done

## Preflight

- AGENTS.md lu.
- Regression guardrails lus.
- Story gate passed: additive runtime/signature phase.

## Capsule validation

- Capsule générée avec `condamad_prepare.py`.
- Validation finale exécutée avec `condamad_validate.py`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `chart_signature_runtime_data.py` | `test_chart_signature_runtime_data.py` | PASS |
| AC2 | `ChartSignatureCalculator` | `test_chart_signature.py` | PASS |
| AC3 | Uses `SignRuntimeData`, house strengths and `DominantAspectEvaluator` | targeted tests passed | PASS |
| AC4 | `json_builder.py` serializes precomputed balance only | projection scan classified | PASS |
| AC5 | astrology/prediction boundary unchanged | boundary test passed | PASS |

## Files changed

- `backend/app/domain/astrology/runtime/chart_signature_runtime_data.py`
- `backend/app/domain/astrology/interpretation/chart_signature.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_signature_runtime_data.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`

## Files deleted

None.

## Tests added or updated

- Added signature runtime and calculator tests.
- Updated chart JSON tests for additive signature and canonical-code fallback.

## Commands run

- `ruff format .` - PASS
- `ruff check .` - PASS
- `pytest -q` - PASS, 2588 passed, 1 skipped, 1175 deselected
- Backend startup `/docs` on `127.0.0.1:8015` - PASS, HTTP 200

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No local element/modality/sign weight constants.
- Serializer does not calculate dominance.
- No prediction dependency.

## Diff review

Scope limited to additive chart balance/signature runtime, projection, tests and evidence.

## Final worktree status

Dirty with intended story/code changes; no commit requested.

## Remaining risks

None identified.

## Suggested reviewer focus

Check tie-break and score normalization policy.
