# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Login flow creates a natal chart. | `frontend/e2e/natal-generation-regression.spec.ts` covers login token, birth save, geocoding mocks, POST generation and `/latest`. | `pnpm --dir frontend test:e2e -- --grep "natal"` with explicit Vite server: PASS after review fix. | PASS |
| AC2 | Known time returns traditions. | `backend/tests/integration/astrology/test_natal_generation_regression.py` asserts complete `traditional_conditions`. | `python -B -m pytest -q backend/tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input" --long`: PASS. | PASS |
| AC3 | Latest reload keeps contract. | Backend integration and Playwright both assert POST then `/latest` keep `chart_id` and traditional contract. | `pytest` targeted command plus reviewed Playwright E2E: PASS. | PASS |
| AC4 | Expert panel renders generated payload. | E2E waits for `/natal` and `Panneau expert natal`; unit tests cover generated public payload rendering. | `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage` and reviewed E2E: PASS. | PASS |
| AC5 | Provider payload keeps birth context. | Route regression also asserts same Paris public contract coexists with rendered provider birth context. | `python -B -m pytest -q backend/tests/integration/astrology/test_natal_generation_regression.py --long`: PASS. | PASS |
| AC6 | Enriched prompt blocks stay present. | `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` asserts selected themes and missing-data limits. | `python -B -m pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`: PASS via targeted suite. | PASS |
| AC7 | UI payload stays provider-distinct. | Public route test now checks provider payload in the same proof without merging the two contracts. | `ruff check` and backend pytest with `--long`: PASS. | PASS |
| AC8 | Legacy carrier sources do not drive prompts. | Tests assert `chart_json` and `natal_data` are absent from public result/provider rendering. | `rg` found legacy terms only in existing adapters/guards/tests; architecture and prompt tests PASS. | PASS |
| AC9 | Standard validation skips real providers. | E2E and provider assertions use mocks/fixtures; no external provider call added. | `rg -n "provider_smoke|OPENAI_API_KEY|ANTHROPIC_API_KEY" backend/tests frontend/e2e` classified opt-in smoke tests only. | PASS |
| AC10 | Runtime route inventory includes natal endpoints. | `backend/tests/integration/astrology/test_natal_generation_regression.py` asserts route and OpenAPI paths. | `python -B -c` checks for `app.routes` and `app.openapi()` both PASS. | PASS |
| AC11 | Story evidence artifacts are persisted. | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/**` created. | Capsule validation and final evidence update completed; `condamad_validate.py`: PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
