<!-- Review finale CONDAMAD CS-182 apres boucle correction. -->

# CONDAMAD Code Review

## Review target

- Story: `CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db`
- Closure class: `full-closure`
- Verdict final: `CLEAN`
- Review/fix iterations: 2

## Inputs reviewed

- `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-before.md`
- `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-after.md`
- `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/runtime-reference-evidence.md`
- Diff applicatif et tests backend lies a la projection prediction, au repository reference et aux guards.

## Diff summary

- Suppression de `backend/app/domain/prediction/public_astro_vocabulary.py`.
- Ajout de `backend/app/domain/prediction/astro_label_formatter.py`, sans donnees DB-backed fixed star ou aspect tone.
- Ajout de `FixedStarData` et chargement DB des etoiles fixes actives dans `PredictionReferenceRepository`.
- Propagation de `PredictionContext.fixed_stars` via le loader et consommation par `EnrichedAstroEventsBuilder`.
- Migration des rendus publics fixed star vers `AstroEvent.metadata["star_display_name"]`.
- Migration de `dominant_aspects[*].tonality` vers `AspectProfileData.energy_type`.
- Mise a jour des guards et tests ciblant `RG-108`, `RG-110`, `RG-112`, `RG-113`.

## Review layers

- Diff integrity: scope coherent avec CS-182; `.discord/bot.py` est sale mais hors perimetre et non inclus dans la conclusion CS-182.
- Acceptance audit: AC1 a AC7 couverts par tests, scans et artefacts persistants.
- Validation audit: commandes ciblees executees dans le venv, resultats passes, app backend demarree localement; la suite complete conserve 3 echecs natal/aspect hors perimetre CS-182.
- DRY / No Legacy audit: aucun import runtime `PublicAstroVocabulary`, `_STAR_DATA`, `_ASPECT_TONES`, `fixed_star_longitudes` ou `fixed_star_display_name`.
- Edge/failure audit: absence de profil d'aspect declenche une erreur explicite; pas de fallback local `"nuance"`.
- Security/data audit: pas de secret, pas de changement auth/CORS, pas de SQL dans `domain/prediction`.

## Findings

Aucun finding restant.

### Findings corriges pendant la boucle

| Finding | Severity | Fix |
|---|---|---|
| `PublicPredictionAssembler` passait `aspect_profiles` a `PublicTimeWindowPolicy.build()`, provoquant un `TypeError` sur les parcours assembleur existants. | High | Argument retire de l'appel time windows. |
| Les profils d'aspects charges par les routes etaient non propages a `PublicAstroFoundationPolicy`; la tonalite publique ne pouvait pas venir du profil DB-backed dans le chemin assembleur. | High | Propagation ajoutee et test assembleur dedie. |
| Les imports routeurs CS-182 decalaient les lignes exactes de la garde SQL routeur. | Medium | Allowlist realignee et garde ciblee relancee. |

## Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `PredictionReferenceRepository.get_fixed_stars()` + `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py`. |
| AC2 | PASS | `EnrichedAstroEventsBuilder` consomme `fixed_stars` runtime + test enriched events. |
| AC3 | PASS | `PublicAstroFoundationPolicy` lit `AspectProfileData.energy_type`; test direct et test assembleur. |
| AC4 | PASS | Guard runtime prediction zero import legacy. |
| AC5 | PASS | Guard catalog interdit les symboles legacy fixed star/aspect tone. |
| AC6 | PASS | Artefacts before/after/runtime evidence presents et fermes. |
| AC7 | PASS | Ruff + pytests cibles executes dans le venv. |

## Validation audit

- `ruff format .`: PASS.
- `ruff check .`: PASS.
- `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py`: PASS, 50 passed.
- `pytest -q app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py`: PASS, 10 passed.
- `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_time_window.py`: PASS, 36 passed.
- `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py`: PASS, 4 passed.
- Review regression suite public projection: PASS, 26 passed, 4 deselected.
- Final targeted suite including SQL allowlist guard: PASS, 101 passed.
- Scans `RG-113`: PASS, zero hit.
- `git diff --check`: PASS.
- Backend local start `/health`: PASS.
- Full backend `pytest -q`: FAIL hors perimetre CS-182, 3 echecs restants dans `test_calibration_versioning.py` et `test_natal_structural_v3.py` sur des regles/profils d'aspects natal.

## DRY / No Legacy audit

- Aucun wrapper, alias, shim ou re-export `public_astro_vocabulary.py`.
- Aucune nouvelle dependance.
- Aucune dependance SQLAlchemy introduite dans `domain/prediction`.
- Les labels publics restent resolus par contrat injecte; les donnees DB-backed fixed star/aspect tone ne sont plus recréees localement.

## Commands run by reviewer

Toutes les commandes Python ont ete lancees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

Voir `generated/10-final-evidence.md` et `runtime-reference-evidence.md` pour les commandes completes.

## Residual risks

Aucun risque restant identifie sur CS-182. La suite complete du depot conserve 3 echecs natal/aspect hors perimetre de cette story; ils sont documentes dans `generated/10-final-evidence.md`.

## Verdict

`CLEAN`
