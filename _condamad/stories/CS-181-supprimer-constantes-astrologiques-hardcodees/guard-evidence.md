# Guard Evidence

## Guards ajoutés ou renforcés

- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py::test_prediction_aspect_mappings_are_not_reintroduced`
  - Vérifie par AST que `ASPECTS_V1` et `ASPECTS` ne sont pas redéfinis dans `backend/app/domain/prediction` ou `backend/app/services/prediction`.

## Première validation exécutée

| Command | Result | Evidence |
|---|---|---|
| `pytest -q app/tests/unit/test_event_detector.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_natal_calculation_service.py` | PASS | 54 tests passed. |

## Validation finale

| Command | Result | Evidence |
|---|---|---|
| `ruff format .` | PASS | `1390 files left unchanged` après corrections. |
| `ruff check . --fix` | PASS | 3 imports de tests triés automatiquement. |
| `ruff check .` | PASS | `All checks passed!`. |
| `pytest -q app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_transit_signal_v3.py app/tests/unit/test_event_detector.py app/tests/unit/test_intraday_activation_v3.py app/tests/unit/test_impulse_signal_v3.py app/tests/unit/test_engine_orchestrator.py` | PASS | 113 tests passed. |
| `rg -n 'sign_rulerships\s*=\s*\{|payload\.setdefault\("sign_rulerships"\|payload\["house_axes"\]\s*=\|payload\["aspect_orb_rules"\]\s*=' app/services/natal -g '*.py'` | PASS | Zéro hit, `rg` exit 1 attendu. |
| `rg -n 'ASPECTS_V1\|ASPECTS\s*=\s*\{\|orb_max_fallback.*2\.0\|_ASPECT_TONES\|_STAR_DATA' app/domain/astrology app/domain/prediction -g '*.py'` | PASS | Hits uniquement pour `_STAR_DATA` et `_ASPECT_TONES` dans `public_astro_vocabulary.py`, classés dans `astrology-constant-exceptions.md`. |
| `rg -n 'app\.domain\.prediction\|app\.services\.prediction' app/domain/astrology -g '*.py'` | PASS | Zéro hit, `rg` exit 1 attendu. |
| `git diff --check` | PASS | Aucun whitespace error; warnings CRLF uniquement. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md` | PASS | Story validation contract OK. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md` | PASS | Story lint strict OK. |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8017` | PASS | Processus démarré puis arrêté après smoke start local. |

## Cycle review/fix

- Itération 1: review `BLOCKING` sur validation incomplète et fixtures de tests encore incompatibles avec les contrats runtime d'aspects/orbes.
- Corrections: `aspect_reference.py` lit le système actif depuis `LoadedPredictionContext`; les fixtures V3 fournissent `AspectProfileData` complet et `AspectOrbRuleData` explicite.
- Itération 2: review `CLEAN` après lint, tests ciblés, scans de garde et `git diff --check`.
