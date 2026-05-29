# Final Evidence — CS-381-non-regression-generation-theme-natal-prompts

## Story status

- Validation outcome: passed
- Ready for review: yes
- Story key: CS-381-non-regression-generation-theme-natal-prompts
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts`
- Story registry status: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: existing CS-381 implementation/test changes and capsule files were already dirty.
- AGENTS.md files considered: `AGENTS.md`
- Capsule validation before implementation: PASS
- Resume logs considered: `_condamad/codex-runs/cs-381-*.log`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story source unchanged. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Existing capsule file. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Completed AC matrix. |
| `generated/04-target-files.md` | yes | yes | PASS | Completed file map. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Completed validation commands. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Existing guardrail file. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `frontend/e2e/natal-generation-regression.spec.ts` covers saved Paris birth data, POST generation and latest reload. | E2E with explicit Vite server PASS after review fix. | PASS | Real provider not called. |
| AC2 | `backend/tests/integration/astrology/test_natal_generation_regression.py` asserts known-time traditions. | Targeted backend pytest with `--long` PASS. | PASS | `traditional_conditions` complete. |
| AC3 | Backend integration and E2E assert latest reload preserves `chart_id` and traditional contract. | Pytest plus reviewed E2E PASS. | PASS | Public contract preserved. |
| AC4 | E2E asserts `/natal` renders `Panneau expert natal`; unit tests cover UI projection. | Vitest targeted PASS and reviewed E2E PASS. | PASS | No `NatalExpertPanel` console error in E2E. |
| AC5 | Route regression also checks rendered provider `birth_context` beside the generated public payload. | Targeted backend pytest with `--long` PASS. | PASS | Paris fixture preserved. |
| AC6 | Provider builder test asserts selected enriched blocks and limits. | Targeted backend pytest PASS. | PASS | Prompt-visible enrichment covered. |
| AC7 | Architecture guard and route/provider coexistence assertions separate UI/provider payloads. | Backend pytest with `--long` PASS. | PASS | No payload merge path added. |
| AC8 | Public and provider tests assert no `chart_json`/`natal_data` primary source. | Classified `rg` scan plus tests PASS. | PASS | Existing legacy terms remain guarded. |
| AC9 | E2E and backend tests are mocked/fixture based. | Provider-smoke scan classified opt-in only. | PASS | No external credentials required. |
| AC10 | Runtime route inventory asserted in test and commands. | `app.routes` and `app.openapi()` commands PASS. | PASS | Natal endpoints registered. |
| AC11 | `evidence/preconditions.md` and `evidence/validation.txt` persisted. | Capsule validation PASS. | PASS | Evidence directory present. |

## Files changed

- `backend/tests/integration/astrology/test_natal_generation_regression.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `frontend/e2e/natal-generation-regression.spec.ts`
- `frontend/playwright.config.ts`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/**`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/generated/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added backend route integration regression for `POST /v1/users/me/natal-chart`, `/latest`, and provider-payload coexistence.
- Updated provider handoff and provider builder tests for enriched prompt payload assertions.
- Added Playwright natal generation regression scenario.
- Updated BirthProfilePage and NatalExpertPanel tests for generated public payload proof.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `condamad_validate.py _condamad\stories\CS-381-non-regression-generation-theme-natal-prompts` | repo | PASS | Capsule complete. |
| `ruff format <changed python tests>` | repo | PASS | 3 files unchanged. |
| `ruff check backend` | repo | PASS | Backend lint clean. |
| `python -B -m pytest -q backend\tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input"` | repo | PASS | 67 passed, 1 skipped. |
| `python -B -m pytest -q backend\tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input" --long` | repo | PASS | 85 passed, 1 skipped. |
| `python -B -m pytest -q backend\tests\integration\astrology\test_natal_generation_regression.py --long --tb=short` | repo | PASS | 1 passed. |
| `ruff check backend\tests\integration\astrology\test_natal_generation_regression.py` | repo | PASS | Coexistence test lint clean. |
| `python -B -m pytest -q backend\tests\architecture\test_llm_astrology_input_payload_boundaries.py --tb=short` | repo | PASS | 6 passed. |
| `python -B -c` app route inventory | repo | PASS | `app.routes` includes natal chart. |
| `python -B -c` OpenAPI inventory | repo | PASS | `app.openapi()` includes natal chart. |
| `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage` | repo | PASS | 48 passed. |
| `pnpm --dir frontend lint` | repo | PASS | TypeScript lint configs pass. |
| `pnpm --dir frontend build` | repo | PASS | Production build pass. |
| `$env:PLAYWRIGHT_SKIP_WEBSERVER='1'; pnpm --dir frontend test:e2e -- --grep "natal"` | repo | PASS | 1 Playwright test passed. |
| Review fix E2E command with explicit Vite server on `4193` | repo | PASS | `/latest` and expert panel assertions pass. |
| `pnpm --dir frontend lint` after review fix | repo | PASS | TypeScript lint configs pass after E2E patch. |
| `git diff --check` | repo | PASS | Whitespace clean. |
| `rg -n "style=" <touched frontend files>` | repo | PASS | Exit 1, no matches. |
| `rg -n "chart_json|natal_data" <scoped backend paths>` | repo | PASS_WITH_CLASSIFICATION | Existing guarded terms only. |
| `rg -n "provider_smoke|OPENAI_API_KEY|ANTHROPIC_API_KEY" backend\tests frontend\e2e` | repo | PASS_WITH_CLASSIFICATION | Opt-in smoke suite only. |

## Commands skipped or blocked

- Direct `pnpm --dir frontend test:e2e -- --grep "natal"` with Playwright-managed `webServer` did not complete in this Windows session.
  It first failed on occupied port `4173`, then timed out on alternate ports while the Vite URL was reachable.
  Compensating evidence: same Playwright scenario PASS against an explicit Vite server with `PLAYWRIGHT_SKIP_WEBSERVER=1`.
- Review wrapper attempts before the successful E2E rerun failed before test execution due to PowerShell redirect/shim syntax and
  `pnpm dev -- --host` port forwarding; the final wrapper used `pnpm.cmd` and no extra separator.
- A direct pytest run without `--long` selected no integration test because repository collection excludes integration tests
  from the fast suite; the corrected validation command uses `--long`.
- One retry from `backend` used the wrong relative venv activation path and failed before useful validation; all accepted
  Python validation commands were rerun from the repository root after activating `.\.venv\Scripts\Activate.ps1`.

## DRY / No Legacy evidence

- No production code path, compatibility wrapper, alias, shim, or fallback was added.
- Public UI payload tests and provider payload tests stay separate, with one route regression proving their coexistence.
- `chart_json` and `natal_data` scans show existing guarded runtime surfaces, not a new primary prompt handoff.
- Frontend inline-style scan on touched files has no matches.
- Provider smoke remains opt-in and outside standard validation.

## Diff review

- `git diff --stat`: reviewed for backend tests, frontend tests, Playwright config and capsule evidence.
- `git diff --check`: PASS.
- Unrelated pre-existing untracked run files remain outside story scope: `_condamad/critical-errors.jsonl`, `_condamad/run-state.json`.

## Final worktree status

- Application and evidence files for CS-381 are modified/untracked as expected.
- No CS-381 Vite/Playwright server left active on validation ports `4192` or `4193`.

## Remaining risks

- Direct Playwright-managed `webServer` remains unreliable in this local Windows session; validation uses an explicit Vite server.
- Scoped `chart_json`/`natal_data` terms remain in existing legacy/adapter/guard areas and are classified by architecture tests.
- No remaining implementation finding is open after the fresh review.

## Suggested reviewer focus

- Review that the new tests prove coexistence of public natal generation and enriched provider prompt payload without merging their contracts.
