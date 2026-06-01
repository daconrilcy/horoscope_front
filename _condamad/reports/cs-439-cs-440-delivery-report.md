<!-- Commentaire global: ce rapport consolide les preuves de delivery CS-439 et CS-440 sans modifier le code applicatif. -->

# Delivery Report - CS-439 to CS-440

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-06-01 18:05:07 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced |
| Stories covered | `CS-439`, `CS-440` |
| Source documents | `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md`; `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`; `_condamad/stories/story-status.md`; story capsules under `_condamad/stories/CS-439-*` and `_condamad/stories/CS-440-*` |
| Diff source | Story-time final evidence, code reviews, validation logs, and report-time `git status --short`; no commit range evidenced |
| Validation source | Story-time and final-validation logs under `_condamad/codex-runs`; no new app validation executed for this report |
| Audits in this series | None declared by the user; no story-audit folder is linked to `CS-439` or `CS-440` |

## 1. Executive summary

`CS-439` is `Delivered`: `_condamad/stories/story-status.md` marks it `done`, `generated/10-final-evidence.md` records `Validation outcome: PASS`, and `generated/11-code-review.md` records `Verdict: CLEAN`.

`CS-440` is `Partially delivered`: it has implemented guards, reports and targeted validations, but `generated/10-final-evidence.md` records `Validation outcome: BLOCKED_BY_REVIEW_FINDINGS`, AC2-AC4 are `BLOCKED`, and `generated/11-code-review.md` records `Verdict: BLOCKED`.

Final initiative status: `Partially delivered`.

No audits were performed inside this two-story series. The only related report artifact is the CS-440 zero-hit closure report `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`, which is implementation evidence, not an audit.

## 2. Initial context and trigger

The trigger for `CS-439` was removal of frontend legacy natal interpretation adapters: the brief requires public `/natal` rendering to consume `theme_natal` payloads directly and stop using `NatalInterpretationResult`, old `use_case`, `level`, or `variant_code` command heuristics (`_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md`).

The trigger for `CS-440` was final zero-hit guarding after legacy natal deletion: the brief requires temporary CS-434/CS-435 allowlists to become zero-hit or proof-only guards and requires residual old-symbol tests/fixtures to stop acting as nominal behavior (`_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`).

The tracker proves the current story lifecycle state: `CS-439` is `done`; `CS-440` is `ready-to-review`; prerequisites `CS-436`, `CS-437`, and `CS-438` remain `ready-to-dev` (`_condamad/stories/story-status.md`).

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-439` | Remove first-party frontend adapters and fixtures that treat historical natal interpretation DTOs as modern public readings. | `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/00-story.md`; `generated/03-acceptance-traceability.md` | No backend contract changes; no visual redesign; keep `variant_code` for entitlement display only. |
| `CS-440` | Close legacy natal test/guard allowlists with zero-hit or classified proof-only guards. | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/00-story.md`; `generated/03-acceptance-traceability.md` | Do not implement functional deletions owned by `CS-436`, `CS-437`, `CS-438`; do not delete historical `_condamad` reports or briefs; do not edit `_condamad/run-state.json`. |

## 4. Implementation summary

### CS-439

- `frontend/src/api/natal-chart/index.ts`: `generated/10-final-evidence.md` states `ThemeNatalReadingPublicPayload` and `UseThemeNatalReadingResult` replaced the old modern target, and `adapter-symbol-after.txt` recorded zero matches for `NatalInterpretationResult`, `mapProductActionDataToInterpretation`, and `isNatalInterpretationResult`.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`: final evidence records old `use_case` and `level` selection removed from public reading selection, with `frontend-legacy-after.txt` and `level-selection-after.txt` as validation anchors.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: final evidence records rendering by public schema presence, not old `use_case` or `level`.
- `frontend/src/tests/*`: final evidence records updated API, page, interpretation and DOM guard tests; review evidence records 136 targeted frontend tests passing.
- `generated/11-code-review.md`: final implementation review is `CLEAN` after a stale-review evidence fix and a `level` heuristic fix.

### CS-440

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`: final evidence records added runtime, test-hit and fixture-directory architecture assertions.
- `backend/app/tests/unit/test_eval_harness_natal.py` and `backend/app/tests/eval_fixtures/generic_structured_*`: final evidence records legacy-named eval fixture directories renamed to generic structured-output fixtures.
- `_condamad/stories/regression-guardrails.md`: final evidence and the CS-440 report record new durable invariant `RG-174` for "Legacy natal deleted: zero public/runtime hit".
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md`: classifies residual old symbols as readonly, admin-only, rejection guard, extinction test, or historical proof.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`: persists a final zero-hit closure report, but its own residual risks state `CS-436`, `CS-437`, and `CS-438` remain `ready-to-dev`.
- `generated/11-code-review.md`: final review is `BLOCKED` because prerequisites remain unfinished and positive Basic/free tests still exercise legacy service/adapter behavior.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-439` | AC1 modern API hook returns public reading payloads. | CS-439 brief AC1, AC3 | `frontend/src/api/natal-chart/index.ts`; `generated/10-final-evidence.md` AC1 | `pnpm --dir frontend test -- natalChartApi.test.tsx ...` PASS; `pnpm --dir frontend lint` PASS | `Delivered` |
| `CS-439` | AC2 old use-case selection removed from `NatalInterpretation.tsx`. | CS-439 brief AC1-AC2 | `frontend/src/features/natal-chart/NatalInterpretation.tsx`; `frontend-removal-audit.md` | `frontend-legacy-after.txt`; `level-selection-after.txt` | `Delivered` |
| `CS-439` | AC3 content no longer decides from old `use_case`. | CS-439 brief AC2, AC5 | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | `natalInterpretation.test.tsx`, `natalPublicDomGuard.test.tsx` PASS | `Delivered` |
| `CS-439` | AC4 command bodies use only authorized fields. | CS-439 brief AC4 | `ThemeNatalReadingCommandRequest` in `frontend/src/api/natal-chart/index.ts` | `natalChartApi.test.tsx` PASS | `Delivered` |
| `CS-439` | AC5 `variant_code` entitlement-only. | CS-439 brief AC5 | `NatalChartPage.tsx`; `NatalAstrologerMode.tsx` classified as gate/display reads | `variant-code-after.txt` | `Delivered` |
| `CS-439` | AC6 public DOM rejects legacy symbols. | CS-439 brief AC7 | `frontend/src/tests/natalPublicDomGuard.test.tsx` | `pnpm --dir frontend test -- natalPublicDomGuard.test.tsx` PASS | `Delivered` |
| `CS-439` | AC7 positive old-use-case fixtures removed. | CS-439 brief AC9 | tests now use `theme_natal_preview` fixtures per final evidence | `frontend-legacy-after.txt` denylist-only hit | `Delivered` |
| `CS-439` | AC8 no inline styles introduced. | CS-439 brief AC8 | No TSX style changes recorded in final evidence | `inline-style-after.txt`: no matches | `Delivered` |
| `CS-439` | AC9 adapter symbols cannot reappear. | CS-439 story AC9 | `NatalInterpretationResult`, mapper and guard removed from modern public flow | `adapter-symbol-after.txt`: no matches | `Delivered` |
| `CS-439` | AC10 evidence artifacts persisted. | CS-439 story AC10 | CS-439 `evidence/**` and `generated/**` | `generated/10-final-evidence.md` capsule validation PASS | `Delivered` |
| `CS-439` | AC11 historical route actions absent or modernized. | CS-439 story AC11 | PDF and generation actions use product endpoint per final evidence | `NatalChartPage.test.tsx`, `natalInterpretation.test.tsx` PASS | `Delivered` |
| `CS-440` | AC1 allowlists reject runtime old-symbol hits. | CS-440 brief AC1 | CS-434/CS-435 superseded by CS-440 audit/report | Architecture guard and OpenAPI/routes evidence PASS | `Delivered` |
| `CS-440` | AC2 no nominal backend test uses `natal_interpretation_short`. | CS-440 brief AC2 | Exact test-hit guard added | AC is `BLOCKED`: residual Basic/readonly tests remain while CS-436/CS-438 are not done | `Partially delivered` |
| `CS-440` | AC3 no nominal backend test uses `natal_long_free`. | CS-440 brief AC3 | Exact test-hit guard added | AC is `BLOCKED`: residual free/admin/readonly tests remain while CS-436/CS-437 are not done | `Partially delivered` |
| `CS-440` | AC4 no nominal old-generation success mocks. | CS-440 brief AC4 | Old route test renamed anti-return; mocks classified | AC is `BLOCKED`: positive adapter/service mocks remain in Basic/runtime tests | `Partially delivered` |
| `CS-440` | AC5 public app scans zero-hit for old natal controls. | CS-440 brief AC5 | Public refresh controls and public `use_case_level` absent | Bounded scans PASS; architecture guard classifies old keys | `Delivered` |
| `CS-440` | AC6 `variant_code` never constructs theme natal command. | CS-440 brief AC6 | CS-440 audit classifies remaining `variant_code` owners | Product-action OpenAPI and rejection tests PASS | `Delivered` |
| `CS-440` | AC7 explicit anti-return test names. | CS-440 brief AC7 | `test_old_public_route_is_removed_or_gone`; `test_theme_natal_contract_is_only_public_generation_path` | Backend/frontend targeted tests PASS | `Delivered` |
| `CS-440` | AC8 architecture guard fails on unauthorized hits. | CS-440 brief AC8 | `test_legacy_natal_runtime_hits_are_explicitly_authorized` and test-hit guard | Architecture tests PASS | `Delivered` |
| `CS-440` | AC9 durable zero-hit invariant tracked. | CS-440 brief AC7 | `RG-174` in `_condamad/stories/regression-guardrails.md` | Guard checks registry; validation log PASS for `zero public/runtime hit` scan | `Delivered` |
| `CS-440` | AC10 final zero-hit report persisted. | CS-440 brief AC8 | `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` | Architecture guard checks report/audit | `Delivered` |
| `CS-440` | AC11 old public route removed or gone. | CS-440 story AC11 | route documented/tested as `410 Gone` | `test_old_public_route_is_removed_or_gone`; route/OpenAPI checks | `Delivered` |

## 6. Evidence of completion

### Code evidence

- `frontend/src/api/natal-chart/index.ts`: proves CS-439 moved the frontend public reading target to `ThemeNatalReadingPublicPayload` and no longer exposes the old DTO as the modern target, per CS-439 final evidence AC1 and AC9.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`: proves CS-439 removed `natal_long_free`, `natal_interpretation_short`, old `use_case`, and old `level` selection for public readings, per `level-selection-after.txt` and final evidence AC2.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: proves CS-439 content rendering is schema-presence based, not `use_case`/`level` based, per final evidence AC3.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`: proves CS-440 has deterministic architecture guards for runtime and test/fixture legacy hits, per final evidence implementation evidence.
- `backend/app/tests/unit/test_eval_harness_natal.py` and `backend/app/tests/eval_fixtures/generic_structured_*`: prove CS-440 removed legacy prompt names from eval fixture paths, per code review findings corrected CR-1/CR-2.

### Test evidence

- `frontend/src/tests/natalChartApi.test.tsx`: proves CS-439 public payload normalization and authorized command-body fields.
- `frontend/src/tests/natalInterpretation.test.tsx`: proves CS-439 public rendering and no old `level` heuristic selection.
- `frontend/src/tests/natalPublicDomGuard.test.tsx`: proves CS-439/CS-440 DOM denylist and public generation anti-return guard.
- `frontend/src/tests/NatalChartPage.test.tsx`: proves CS-439 page-level product-action behavior.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`: proves CS-440 runtime/test-hit classification guard.
- `backend/tests/architecture/test_llm_legacy_extinction.py`: proves CS-440 old LLM key extinction checks.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` and `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`: prove CS-440 prompt governance and extinction validation.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py`, `backend/tests/integration/test_theme_natal_public_reads.py`, `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`, and `tests/unit/domain/theme_natal`: prove CS-440 modern theme natal runtime routes and reads passed targeted backend suites.

### Documentation evidence

- `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/frontend-removal-audit.md`: classifies deleted frontend adapters, old use cases, `level` heuristic removal, and `variant_code` entitlement-only ownership.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md`: classifies residual legacy symbols and exact authorized test owners.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`: documents CS-440 closure evidence and residual blockers.
- `_condamad/stories/regression-guardrails.md`: contains `RG-174`, the durable zero public/runtime hit invariant created by CS-440.
- `_condamad/stories/story-status.md`: records `CS-439` as `done`, `CS-440` as `ready-to-review`, and `CS-436`-`CS-438` as `ready-to-dev`.

### Operational evidence

- `_condamad/codex-runs/cs-439-final-validation.log`: `condamad_story_validate.py` PASS and strict story lint PASS.
- `_condamad/codex-runs/cs-439-implementation-review-fix.log`: records CS-439 final status `done`, review `CLEAN`, targeted frontend tests/lint/scans PASS, and Vite startup PASS.
- `_condamad/codex-runs/cs-440-final-validation.log`: `condamad_story_validate.py` PASS and strict story lint PASS.
- `_condamad/codex-runs/cs-440-implementation-review-fix.log`: records CS-440 final status `ready-to-review` / `BLOCKED`, corrected guard/fixture issues, targeted backend/frontend validations PASS, and remaining blockers.
- Report-time `git status --short`: `_condamad/run-state.json` is modified before this report; no report-target file existed before generation.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx` | targeted | PASS | CS-439 `generated/10-final-evidence.md`; `evidence/validation.txt`; CS-439 review | 4 files, 136 tests in final evidence; CS-439 log also mentions 138 tests in an earlier final summary, so the report anchors on capsule evidence. |
| `pnpm --dir frontend lint` | targeted | PASS | CS-439 `generated/10-final-evidence.md`; CS-439 review | TypeScript lint/typecheck passed. |
| CS-439 legacy use-case scan over `frontend/src` | targeted | PASS | `frontend-legacy-after.txt`; CS-439 final evidence | Only intentional DOM denylist literal remains. |
| CS-439 adapter-symbol scan | targeted | PASS | `adapter-symbol-after.txt`; CS-439 final evidence | No `NatalInterpretationResult`, mapper, or old adapter guard hits in bounded production roots. |
| CS-439 variant scan | targeted | PASS | `variant-code-after.txt`; CS-439 final evidence | Remaining hits classified as entitlement/gate display. |
| CS-439 inline-style scan | targeted | PASS | `inline-style-after.txt`; CS-439 final evidence | No matches. |
| CS-439 Vite startup | manual | PASS | `evidence/vite-start.txt`; `cs-439-implementation-review-fix.log` | HTTP 200 on local Vite startup; server stopped after check. |
| CS-439 backend `pytest`/`ruff` | targeted | NOT RUN | CS-439 final evidence commands skipped | Backend unchanged and story scope frontend-only. |
| `ruff format .` and `ruff check .` in `backend` | targeted | PASS | CS-440 `generated/10-final-evidence.md`; CS-440 review | Python commands are recorded as run after venv activation in CS-440 logs/final summary. |
| `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short` | targeted | PASS | CS-440 review | Architecture and LLM extinction/governance suite passed. |
| `python -B -m pytest -q --long tests/unit/domain/theme_natal tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_basic_full_reading_runtime.py tests/integration/test_theme_natal_public_reads.py --tb=short` | targeted | PASS | CS-440 review and final evidence | Targeted theme natal backend suites passed. |
| `pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx` | targeted | PASS | CS-440 review and final evidence | 136 frontend tests passed for CS-440 relevant surfaces. |
| `pnpm --dir frontend lint` | targeted | PASS | CS-440 review and final evidence | Frontend lint passed. |
| `rg -n "forceRefresh|shouldRefreshShortAfterBasicUpgrade|use_case_level" ...` | targeted | PASS | CS-440 `evidence/validation.txt` | Public refresh controls and public `use_case_level` absent in bounded roots. |
| `rg -n "Legacy natal deleted: zero public/runtime hit|zero public/runtime hit" ...` | targeted | PASS | CS-440 `evidence/validation.txt` | `RG-174` invariant evidenced. |
| `rg -n "natal_interpretation_short|natal_long_free" backend/app frontend/src` | targeted | FAIL | CS-440 `evidence/validation.txt` | Marked `BLOCKED`; residual backend/app hits remain. |
| `rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation" backend/app backend/tests` | targeted | FAIL | CS-440 `evidence/validation.txt`; CS-440 review CR-4 | Marked `BLOCKED`; positive adapter/service tests remain. |
| Full backend `python -B -m pytest -q --tb=short` | full suite | NOT RUN | CS-440 final evidence commands skipped | Targeted suite used; full suite not evidenced. |
| Full frontend test suite | full suite | NOT RUN | CS-440 final evidence commands skipped | Targeted natal suite and lint used. |
| Local dev server for CS-440 | manual | SKIPPED | CS-440 final evidence commands skipped | Story changed tests, guards and evidence only; FastAPI import/OpenAPI/route/TestClient checks were used instead. |
| Audits in this series | external | NOT RUN | User instruction: "Audits de la serie: Aucun audit dans cette serie." | No audit findings, risks or candidates to link. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- `CS-440` cannot close as done although it produced guards and a report: the review records blockers `CR-3` and `CR-4` in `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`.
- `CS-440` AC2-AC4 remain `BLOCKED` in `generated/10-final-evidence.md`; the report therefore does not claim full zero-hit closure.

### Known limits

- `CS-439` backend validation was not run because the story was frontend-only and backend was unchanged, per `generated/10-final-evidence.md`.
- `CS-440` full backend and full frontend suites were not run; final evidence records targeted suites instead.
- No commit range is evidenced; this report relies on story capsules, codex logs, validation artifacts, and current tracker state.

### Assumptions

- Story-time validation logs are treated as the authoritative execution evidence for code changes because this report phase explicitly forbids modifying application code and does not require rerunning app validation.
- The user-declared series audit state is authoritative: there were no audits in this series.

## 9. Residual risks

- `CS-440` closure risk: `CS-436`, `CS-437`, and `CS-438` remain `ready-to-dev` in `_condamad/stories/story-status.md`, while CS-440 is framed as closing work after those functional removals. Impact: CS-440 cannot honestly be marked `done`.
- Legacy-positive test risk: `CS-440` review `CR-4` states Basic/free tests still exercise `NatalInterpretationService.interpret` or `AIEngineAdapter.generate_natal_interpretation`. Impact: old generator vocabulary may remain nominal in tests until CS-436-CS-438 are completed or the scope is recut.
- Historical-row rendering risk: `CS-439` final evidence states historical stored rows without modern public `theme_natal` schema may no longer render through the modern public reading hook. Impact: acceptable story delta, but reviewer should confirm no required environment still depends on old DTO rendering.
- Validation coverage risk: full backend and full frontend suites are `NOT RUN` for CS-440; targeted checks passed, but suite-wide regressions are not evidenced by this report.

## 10. Evidence gaps

- Commit range: Not evidenced.
- CI status: Not evidenced; no CI logs were provided or found in the requested source set.
- Full backend regression suite for CS-440: NOT RUN.
- Full frontend regression suite for CS-440: NOT RUN.
- Audits in this series: NOT RUN / not applicable, because the user explicitly stated none.
- Completion of prerequisite stories `CS-436`, `CS-437`, and `CS-438`: Not evidenced; tracker records them as `ready-to-dev`.

## 11. Recommended next actions

1. Implement or explicitly recut `CS-436`, `CS-437`, and `CS-438`, then rerun CS-440 review because `CR-3` blocks closure.
2. Remove or rebase positive Basic/free tests around `NatalInterpretationService.interpret` and `AIEngineAdapter.generate_natal_interpretation`, then rerun the CS-440 blocked scans and review because `CR-4` blocks closure.
3. After CS-440 is clean, rerun targeted backend/frontend validations plus the full feasible regression suites, then update `_condamad/stories/story-status.md` only if review is no longer blocked.

## 12. Final delivery status

`Partially delivered`

`CS-439` is delivered with `PASS` validation and `CLEAN` review. `CS-440` has substantial implemented guard/report/test evidence, but it is not fully delivered because AC2-AC4 are `BLOCKED`, the code review verdict is `BLOCKED`, and prerequisite stories `CS-436`, `CS-437`, and `CS-438` remain `ready-to-dev`.
