# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Login flow creates a natal chart. | `frontend/e2e/natal-generation-regression.spec.ts` covers login token, birth save, geocoding mocks and POST generation. | `pnpm --dir frontend test:e2e -- --grep "natal"` with explicit Vite server: PASS. | PASS |
| AC2 | Known time returns traditions. | `backend/tests/integration/astrology/test_natal_generation_regression.py` asserts complete `traditional_conditions`. | `python -B -m pytest -q backend/tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input"`: PASS. | PASS |
| AC3 | Latest reload keeps contract. | The same integration test asserts POST and `/latest` keep `chart_id`, public result and route inventory. | `pytest` targeted command plus `app.routes` and `app.openapi()` checks: PASS. | PASS |
| AC4 | Expert panel renders generated payload. | `frontend/src/tests/NatalExpertPanel.test.tsx` and `BirthProfilePage.test.tsx` cover generated public payload rendering. | `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage`: PASS. | PASS |
| AC5 | Provider payload keeps birth context. | `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` asserts Paris birth context in rendered provider payload. | `python -B -m pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`: PASS via targeted suite. | PASS |
| AC6 | Enriched prompt blocks stay present. | `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` asserts selected themes and missing-data limits. | `python -B -m pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`: PASS via targeted suite. | PASS |
| AC7 | UI payload stays provider-distinct. | Public route test and provider tests assert distinct payload roles; architecture guard remains active. | `python -B -m pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`: PASS. | PASS |
| AC8 | Legacy carrier sources do not drive prompts. | Tests assert `chart_json` and `natal_data` are absent from public result/provider rendering. | `rg` found legacy terms only in existing adapters/guards/tests; architecture and prompt tests PASS. | PASS |
| AC9 | Standard validation skips real providers. | E2E and provider assertions use mocks/fixtures; no external provider call added. | `rg -n "provider_smoke|OPENAI_API_KEY|ANTHROPIC_API_KEY" backend/tests frontend/e2e` classified opt-in smoke tests only. | PASS |
| AC10 | Runtime route inventory includes natal endpoints. | `backend/tests/integration/astrology/test_natal_generation_regression.py` asserts route and OpenAPI paths. | `python -B -c` checks for `app.routes` and `app.openapi()` both PASS. | PASS |
| AC11 | Story evidence artifacts are persisted. | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/**` created. | Capsule validation and final evidence update completed; `condamad_validate.py`: PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
