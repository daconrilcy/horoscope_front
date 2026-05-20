# Code Review - CS-202-natal-expert-panel

## Review target

- Story: `CS-202-natal-expert-panel`
- Capsule: `_condamad/stories/CS-202-natal-expert-panel`
- Surface reviewed:
  - `frontend/src/api/natal-chart/index.ts`
  - `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
  - `frontend/src/features/natal-chart/NatalExpertPanel.css`
  - `frontend/src/pages/NatalChartPage.tsx`
  - `frontend/src/tests/NatalExpertPanel.test.tsx`
  - `frontend/src/tests/NatalChartPage.test.tsx`
  - story evidence and status files

## Inputs reviewed

- Root `AGENTS.md`.
- `_condamad/stories/regression-guardrails.md`, including `RG-129`.
- `00-story.md`.
- `generated/03-acceptance-traceability.md`.
- `generated/06-validation-plan.md`.
- `generated/07-no-legacy-dry-guardrails.md`.
- `generated/10-final-evidence.md`.
- Frontend implementation and tests listed above.

## Diff summary

- Frontend natal API types were extended to describe CS-201 public expert blocks.
- `NatalExpertPanel` was added as a display-only panel for public natal facts.
- `/natal` now renders the panel from the already loaded latest chart payload.
- Tests were added or updated for panel rendering, explicit grouping and page integration.
- Evidence files and story status were updated for closure.

## Findings

No actionable findings.

## Acceptance audit

- AC1-AC2: `dignities.sect` and `dignities.planets[*].sect_condition` are rendered directly from the payload.
- AC3: sect grouping uses `is_in_sect`, `is_out_of_sect` and the remaining explicit backend code path only.
- AC4-AC8: `advanced_conditions`, dignity scores, profiles, signals, `dominant_planets` and `interpretation_adapter` are rendered as factual payload data.
- AC9: loading, error, missing chart, old payload, empty expert blocks and no-time mode are covered by tests.
- AC10/RG-129: forbidden frontend astrology constants, legacy fields and derivation patterns have no unclassified hits.
- AC11: backend CS-201 regression tests passed under activated venv.
- AC12: before/after/validation evidence exists and is populated.

## Validation audit

Fresh review validation on 2026-05-20:

| Command | Result |
|---|---|
| `npm --prefix frontend test -- NatalExpertPanel` | PASS, 4 tests |
| `npm --prefix frontend test -- NatalChartPage` | PASS, 71 tests |
| `npm --prefix frontend run lint` | PASS |
| `npm --prefix frontend run build` | PASS |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | PASS, 35 tests |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-202-natal-expert-panel/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-202-natal-expert-panel/00-story.md` | PASS |
| RG-129 forbidden frontend scans | PASS, no forbidden hits |
| Broad `OpenAI|AIEngineAdapter|prompt_hint|personalized|conseil` scan | PASS with classified pre-existing or contract-typing hits |
| `git diff -- backend/app/domain/astrology backend/app/services/chart/json_builder.py backend/app/api backend/app/infra migrations docs/db_seeder` | PASS, empty diff |
| `git diff --check` | PASS, only CRLF conversion warnings |
| `Invoke-WebRequest http://127.0.0.1:5173/natal` | PASS, HTTP 200 |

## DRY / No Legacy audit

- Existing `useLatestNatalChart()` remains the single retrieval path.
- No duplicate fetch layer, route, store, backend adapter, shim or legacy alias was introduced.
- The panel has no direct HTTP call, no `any`, no inline style and no frontend astrology doctrine constants.
- `prompt_hint` is typed for contract fidelity but is not rendered.
- Backend forbidden paths were not changed.

## Residual risks

- `npm --prefix frontend test:e2e` was not run because this story changes component/page rendering, not an auth/navigation E2E flow. Component tests, page test, build and local HTTP startup cover the changed surface.

## Verdict

CLEAN
