# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story registry status: `done` after clean review.
- Story key: `CS-179-fermer-i18n-prediction-astrologique`
- Source story: `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/00-story.md`
- Capsule path: `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `M _condamad/stories/regression-guardrails.md`, `M _condamad/stories/story-status.md`, untracked CS-179 capsule.
- Pre-existing dirty files: story registry, regression guardrail row, and CS-179 capsule created before implementation.
- AGENTS.md considered: `AGENTS.md`.
- Capsule generated: yes, in the existing CS-179 folder.
- Story sufficiency gate: PASS. Full-closure scope has exact files, forbidden symbols, before/after audit, RG-110, and validation commands.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Created and updated. |
| `generated/04-target-files.md` | yes | yes | PASS | Created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `prediction-i18n-before.md` records baseline mappings and consumers. | Baseline scan recorded in before audit. | PASS | |
| AC2 | `public_astro_vocabulary.py` now exposes `PublicAstroVocabulary` consuming injected `PredictionAstroLabels`; local DB-backed mappings removed. | Resolver test, projection tests, forbidden-symbol scans. | PASS | |
| AC3 | `astrologer_prompt_builder.py` requires injected labels and no longer owns planet/sign label mappings. | `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py` passed. | PASS | |
| AC4 | Public assembler, daily events and foundation keep payload keys while label sources are injected. | `pytest -q app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py tests/unit/prediction/test_public_time_window.py` passed. | PASS | |
| AC5 | `test_astrology_localization_guardrails.py` blocks forbidden prediction symbols and hidden aspect mapping growth. | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` passed. | PASS | |
| AC6 | `prediction-i18n-after.md` records zero active residual in-domain work and classifies non DB-backed metadata. | Residual marker scan passed; forbidden scans zero-hit. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/generated/*` | added | Capsule execution and evidence files. | AC1-AC6 |
| `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-before.md` | added | Baseline audit. | AC1 |
| `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-after.md` | added | After audit and residual proof. | AC6 |
| `backend/app/domain/prediction/public_astro_vocabulary.py` | modified | Remove local DB-backed FR mappings; add injected vocabulary adapter. | AC2 |
| `backend/app/domain/prediction/public_projection.py` | modified | Inject vocabulary into public projection policies. | AC2, AC4 |
| `backend/app/domain/prediction/public_astro_daily_events.py` | modified | Inject vocabulary into public daily event labels. | AC2, AC4 |
| `backend/app/domain/prediction/astrologer_prompt_builder.py` | modified | Require canonical label contract for prompt context. | AC3 |
| `backend/app/domain/prediction/enriched_astro_events_builder.py` | modified | Stop importing old fixed-star data symbol. | AC2 |
| API/service narration files | modified | Resolve labels outside `domain/prediction` and inject them. | AC2, AC3 |
| Backend tests | modified | Add label-injection and guard coverage. | AC3-AC5 |

## Files deleted

None.

## Tests added or updated

- Added `app/tests/helpers/prediction_astro_labels.py` so unit and integration
  tests reuse one canonical fake label contract instead of duplicating local
  mappings.
- Updated prompt builder, daily events, foundation, time window and projection tests to inject fake canonical labels.
- Updated V4 integration scenarios and the llm orchestration helper module to
  pass the required label contract into `PublicPredictionAssembler`.
- Extended localization guardrails for RG-110 and classified aspect tonality metadata.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `ruff format .` | `backend/` | PASS | 0 | Formatting completed. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_astrology_localization_guardrails.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py tests/unit/prediction/test_public_time_window.py app/tests/unit/prediction/test_public_projection_evidence.py` | `backend/` | PASS | 0 | 46 tests passed. |
| `pytest --long -q tests/integration/test_v4_scenarios.py tests/integration/test_v4_migration.py` | `backend/` | PASS | 0 | 6 V4 integration tests passed after fixing missing `astro_labels` injection. |
| AST scan for `.assemble(...)` calls without `astro_labels` under `app/` and `tests/` | `backend/` | PASS | 0 | Zero missing injections. |
| `rg -n "PLANET_NAMES_FR\|SIGN_NAMES_FR\|SIGN_LABELS_FR\|PLANET_CODE_LABELS" app/domain/prediction -g "*.py"` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "ASPECT_LABELS\|HOUSE_SIGNIFICATIONS\|EFFECT_LABELS" app/domain/prediction -g "*.py"` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "get_planet_name_fr\|get_sign_name_fr\|get_aspect_label\|get_effect_label" app/domain/prediction -g "*.py"` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "AstrologyTranslationResolver\|astrology_translation_resolver\|LanguageModel\|from app\.services" app/domain/prediction -g "*.py"` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "TechnicalAstroLabels\|astro_labels: .*None\|astro_vocabulary: .*None\|PublicAstroVocabulary\(\)" app tests -g "*.py"` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "Known residual in-domain work: none" ../_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-after.md` | `backend/` | PASS | 0 | Residual marker found. |
| `python -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | App import smoke returned `horoscope-backend`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Full `pytest -q` | no | Story validation plan required targeted domain tests; full suite is broader than this closure slice. | Wider unrelated regression could remain. | Targeted tests cover resolver, prompt, projection, daily events, foundation, time windows and guardrails. |

## DRY / No Legacy evidence

- No forbidden prediction symbols remain under `backend/app/domain/prediction`.
- `domain/prediction` has zero `app.services` or resolver imports.
- Production-facing assembler/prompt paths require labels; no technical label fallback remains.
- Test-facing assembler paths now inject the shared fake label contract,
  including integration tests selected by `--long`.
- API and service layers resolve labels with `language_code=None, user_id=...` so the resolver honors user default language before system fallback.
- `_ASPECT_TONES` is classified as non DB-backed public tonality metadata, with guard coverage preventing unclassified aspect mapping growth.

## Diff review

- `git diff --stat` reviewed: changes are limited to CS-179 evidence, prediction i18n surfaces, service/API injection points, and tests.
- `git diff --check` passed with line-ending warnings only.

## Final worktree status

Recorded after review sync:

```text
M _condamad/stories/regression-guardrails.md
M _condamad/stories/story-status.md
M backend/app/api/v1/routers/internal/llm/qa.py
M backend/app/api/v1/routers/public/predictions.py
M backend/app/domain/prediction/astrologer_prompt_builder.py
M backend/app/domain/prediction/enriched_astro_events_builder.py
M backend/app/domain/prediction/public_astro_daily_events.py
M backend/app/domain/prediction/public_astro_vocabulary.py
M backend/app/domain/prediction/public_projection.py
M backend/app/services/llm_generation/horoscope_daily/narration_service.py
M backend/app/services/prediction/public_predictions.py
M backend/app/tests/unit/prediction/test_public_projection_evidence.py
M backend/app/tests/unit/test_astrology_localization_guardrails.py
M backend/app/tests/unit/test_public_projection.py
M backend/tests/integration/test_v4_migration.py
M backend/tests/integration/test_v4_scenarios.py
M backend/tests/llm_orchestration/__init__.py
M backend/tests/unit/prediction/test_astrologer_prompt_builder.py
M backend/tests/unit/prediction/test_public_astro_daily_events.py
M backend/tests/unit/prediction/test_public_astro_foundation.py
M backend/tests/unit/prediction/test_public_time_window.py
?? _condamad/stories/CS-179-fermer-i18n-prediction-astrologique/
?? backend/app/tests/helpers/prediction_astro_labels.py
```

## Remaining risks

- Full backend test suite not run.

## Suggested reviewer focus

- Verify the required-label contract and user-language routing in API/service entry points.
- Verify `_ASPECT_TONES` classification is acceptable as non DB-backed tonality metadata.
