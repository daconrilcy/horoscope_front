# Implementation Review CS-381

Verdict: CLEAN

## Scope

- Story:
  `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/00-story.md`
- Brief:
  `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`
- Implementation surfaces reviewed:
  backend route/provider tests, frontend unit tests, Playwright E2E, validation evidence and tracker row.

## Iteration 1 Findings

### F1 - E2E did not assert latest reload after generation

- Severity: medium.
- Evidence: `frontend/e2e/natal-generation-regression.spec.ts` mocked `/v1/users/me/natal-chart/latest`, but only asserted
  the `POST /v1/users/me/natal-chart` response before the review fix.
- Risk: the browser scenario could pass while the post-generation reload path stayed broken, contrary to the brief.
- Fix: the E2E now waits for `GET /v1/users/me/natal-chart/latest`, asserts status `200`, checks `chart_id` consistency,
  verifies the traditional contract on the reloaded payload, and waits for `Panneau expert natal` on `/natal`.
- Validation: explicit Vite server plus `pnpm --dir frontend test:e2e -- --grep "natal"` PASS.

## Iteration 2 Findings

### F2 - Provider enrichment proof was too isolated from natal generation

- Severity: medium.
- Evidence: the browser scenario used mocked API responses, while the provider enrichment proof lived in separate builder
  and handoff tests.
- Risk: the suite could still prove "front does not crash" and "prompt is enriched" separately, despite the source brief
  requiring coexistence in the same validation slice.
- Fix: `backend/tests/integration/astrology/test_natal_generation_regression.py` now asserts the generated public payload
  and a rendered `theme_astral_llm_input_v1` provider payload together, from the same Paris known-time proof.
- Validation: backend targeted pytest with `--long` PASS, broad CS-381 backend selection with `--long` PASS, Ruff PASS.

## Fresh Review

- AC1: PASS. The browser path saves Paris birth data, generates the chart, and reloads latest.
- AC2: PASS. Backend integration asserts complete `traditional_conditions` for known time.
- AC3: PASS. Backend and E2E both cover `/latest` after creation.
- AC4: PASS. Unit tests and E2E prove expert panel rendering for the public payload.
- AC5: PASS. Provider handoff and route regression assert structured `birth_context`.
- AC6: PASS. Provider builder test asserts prompt-visible enriched blocks.
- AC7: PASS. Architecture guard and route regression keep UI/provider payloads distinct.
- AC8: PASS. Legacy carrier scan is classified and guarded by tests.
- AC9: PASS. Standard tests remain fixture/mocked and do not call a real provider.
- AC10: PASS. Route/OpenAPI inventory is covered by backend tests and commands.
- AC11: PASS. Evidence files are present and updated.

## Validation Summary

- `pnpm --dir frontend test:e2e -- --grep "natal"` with explicit Vite server on port `4193`: PASS.
- `pnpm --dir frontend lint`: PASS.
- `python -B -m pytest -q backend\tests\integration\astrology\test_natal_generation_regression.py --long --tb=short`: PASS.
- `python -B -m pytest -q backend\tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input" --long`: PASS.
- `ruff check backend\tests\integration\astrology\test_natal_generation_regression.py`: PASS.
- Prior implementation validations remain recorded in `generated/10-final-evidence.md`.
- Story and capsule validations were rerun after evidence/status updates.

## Propagation

- no-propagation: the issues were local to this story's regression coverage and evidence.

## Residual Risk

- Direct Playwright-managed `webServer` remains unreliable in this Windows session; the accepted local validation uses an
  explicit Vite server with `PLAYWRIGHT_SKIP_WEBSERVER=1`.
