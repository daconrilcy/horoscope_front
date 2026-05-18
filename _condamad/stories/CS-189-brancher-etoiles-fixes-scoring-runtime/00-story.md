# Story CS-189 brancher-etoiles-fixes-scoring-runtime: Brancher les étoiles fixes au scoring runtime daily

Status: done

## 1. Objective

Corriger les écarts du runtime étoiles fixes daily.
Les conjonctions aux étoiles fixes doivent rester chargées depuis les tables `astral_fixed_star_*`,
mais utiliser un contrat typé complet incluant longitude, magnitude, catégorie, orbe configurable
et routage de scoring. Après implémentation, les étoiles fixes ne sont plus seulement affichées
dans la narration: elles produisent des contributions contrôlées, testées et traçables.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-18 après vérification backend des écarts "Les étoiles fixes runtime".
- Reason for change: le backend charge déjà les étoiles fixes depuis la DB et détecte des
  `fixed_star_conjunction`, mais l'orbe est hardcodé, la magnitude n'est pas propagée,
  les catégories ne routent pas le scoring et `base_weight=0.0` rend les événements
  sans contribution effective.

## 3. Domain Boundary

Cette story appartient à un seul domaine:

- Domain: `backend/app/domain/prediction`
- In scope:
  - Étendre le contrat runtime `FixedStarData` consommé par `PredictionContext`.
  - Résoudre l'orbe fixed star depuis une source runtime DB-backed ou ruleset parameter explicite, pas depuis une constante locale.
  - Propager `visual_magnitude`, mots-clés, catégorie de source (`source_category`) et source utile au filtrage.
  - Filtrer les étoiles fixes inactives ou hors magnitude selon une règle configurée et testée.
  - Produire des `fixed_star_conjunction` structurées avec `orb_deg`, `orb_max`, `star_key`, `star_display_name`, `visual_magnitude`, `source_category` et routage.
  - Donner aux événements fixed stars un `base_weight` contrôlé, non nul quand ils doivent contribuer.
  - Router ces événements vers les catégories prédiction sans créer un second moteur de scoring.
  - Ajouter les tests unitaires et gardes anti-retour.
- Out of scope:
  - Modifier le calcul natal, les points astraux, les aspects natals ou les maisons.
  - Modifier le frontend ou les contrats API publics.
  - Ajouter une nouvelle famille LLM ou déplacer la narration horoscope.
  - Ajouter une dépendance externe.
  - Recalculer les longitudes d'étoiles par épochage dynamique.
- Explicit non-goals:
  - Ne pas recréer un catalogue `_STAR_DATA`, `fixed_star_longitudes` ou `fixed_star_display_name`.
  - Ne pas hardcoder durablement l'orbe fixed stars dans `EnrichedAstroEventsBuilder`.
  - Ne pas mettre de logique produit dans `backend/app/domain/astrology`.
  - Ne pas contourner `RG-035`, `RG-095`, `RG-108`, `RG-110`, `RG-112`, `RG-113` et `RG-117`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story enrichit un contrat runtime existant sans changer les routes ni les
  contrats publics; le comportement autorisé est limité au scoring daily des étoiles fixes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les conjonctions fixed stars déjà détectées restent visibles dans `astro_daily_events.fixed_stars`.
  - Les événements fixed stars peuvent désormais contribuer aux scores si leur orbe, magnitude et routage passent les règles.
  - Les contributions doivent être bornées par le calculateur existant et rester traçables dans les drivers/contributors.
  - Aucune donnée fixed star ne peut venir d'une constante locale concurrente.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le produit exige des catégories fixed stars incompatibles avec les
  catégories daily existantes ou une règle d'orbe différente par étoile sans donnée DB disponible.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les longitudes, magnitudes et métadonnées viennent des tables DB/seeders ou des paramètres ruleset. |
| Baseline Snapshot | yes | Les événements before/after doivent prouver le passage de display-only à scoring contrôlé. |
| Ownership Routing | no | La story ne déplace pas d'ownership entre modules; elle étend les owners existants. |
| Allowlist Exception | no | Aucune exception ou allowlist de fallback n'est autorisée. |
| Contract Shape | yes | `FixedStarData` et `AstroEvent.metadata` doivent avoir une forme explicite. |
| Batch Migration | no | Pas de migration par lots ni de déplacement de consommateurs. |
| Reintroduction Guard | yes | La story crée `RG-117` et doit bloquer le retour des catalogues fixed stars locaux, des poids nuls et de l'orbe hardcodée. |
| Persistent Evidence | yes | La story doit conserver les preuves before/after et les scans de non-duplication. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Tables `astral_fixed_stars`, `astral_fixed_star_definitions`, `astral_fixed_star_keywords`, `astral_reference_sources` et traductions associées.
  - Paramètres `ruleset_context.parameters` uniquement pour les seuils runtime daily comme `fixed_star_orb_deg`, `fixed_star_max_visual_magnitude` ou `fixed_star_base_weight`.
- Source limitation:
  - Le schéma actuel ne porte pas de catégorie produit par étoile fixe; l'implémentation ne doit donc pas inventer de `category_code` DB-backed.
  - Le routage scoring doit passer par une configuration explicite de ruleset.
  - `source_category` et keywords restent des métadonnées traçables, pas des catégories produit inventées.
- Secondary evidence:
  - `PredictionReferenceRepository.get_fixed_stars()` charge uniquement les lignes actives.
  - `PredictionContext.fixed_stars` transporte un contrat immuable consommable par le builder daily.
- Runtime artifact:
  - DB schema `Base.metadata` pour `AstralFixedStarModel`, `AstralFixedStarDefinitionModel` et `AstralFixedStarKeywordModel`.
  - Loaded config `LoadedPredictionContext.prediction_context.fixed_stars`.
  - `FixedStarData` enrichi et événements `AstroEvent(event_type="fixed_star_conjunction")`.
- Static scans alone are not sufficient because le risque principal est un événement affiché mais sans contribution ou alimenté par une constante locale.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/evidence/fixed-stars-runtime-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/evidence/fixed-stars-runtime-after.md`
- Expected invariant:
  - Les mêmes étoiles actives viennent des tables DB.
  - L'orbe et le seuil de magnitude viennent du contexte runtime, pas d'un littéral dispersé.
  - Les événements hors orbe ou hors magnitude ne contribuent pas.
  - Les événements retenus portent `orb_max` et un `base_weight` non nul.

## 4d. Ownership Routing Rule

- Ownership routing rule: not applicable
- Reason: les owners restent inchangés; le repository charge les références, `domain/prediction` détecte les événements et le scoring utilise les services existants.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed; no local fixed-star catalog, fallback or shim may remain or be introduced.

## 4f. Contract Shape

Contract type:

- Dataclass runtime immuable et `AstroEvent.metadata` sérialisable.

Fields:

- `FixedStarData.key: str`
- `FixedStarData.display_name: str`
- `FixedStarData.ecliptic_longitude_deg: float`
- `FixedStarData.visual_magnitude: float | None`
- `FixedStarData.keywords: tuple[str]`
- `FixedStarData.source_category: str | None`
- `FixedStarData.source_key: str | None`
- `AstroEvent.event_type = "fixed_star_conjunction"`
- `AstroEvent.aspect = "conjunction"`
- `AstroEvent.orb_deg: float`
- `AstroEvent.base_weight: float`
- `AstroEvent.metadata.orb_max: float`
- `AstroEvent.metadata.star_key: str`
- `AstroEvent.metadata.star_display_name: str`
- `AstroEvent.metadata.visual_magnitude: float | None`
- `AstroEvent.metadata.fixed_star_source_category: str | None`
- `AstroEvent.metadata.fixed_star_keywords: list[str]`

Required fields:

- `key`, `display_name`, `ecliptic_longitude_deg`, `event_type`, `aspect`, `orb_deg`, `base_weight`, `metadata.orb_max`, `metadata.star_key`, `metadata.star_display_name`.

Optional fields:

- `visual_magnitude`, `keywords`, `source_category`, `source_key`, `metadata.fixed_star_source_category`, `metadata.fixed_star_keywords`.

Status codes:

- Aucun changement HTTP.

Serialization names:

- Les noms publics existants dans `astro_daily_events.fixed_stars` restent inchangés.
- Les métadonnées internes utilisent des clés `snake_case`.

Frontend type impact:

- Aucun impact frontend attendu.

Generated contract impact:

- OpenAPI ne doit pas changer.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: single runtime contract update; no consumer migration batch is planned.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before runtime evidence | `evidence/fixed-stars-runtime-before.md` | Capturer orbe hardcodé, absence de magnitude runtime et `base_weight=0.0`. |
| After runtime evidence | `evidence/fixed-stars-runtime-after.md` | Prouver orbe configurée, filtrage magnitude et contribution non nulle. |
| Guard evidence | `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/evidence/guard-evidence.md` | Consolider tests, scans et absence de catalogue local. |

## 4i. Reintroduction Guard

- Reintroduction guard: required
- Registry invariant: `RG-117`
- Reason: la story établit un invariant durable sur les étoiles fixes daily.
  Les tests ciblés et scans doivent bloquer les catalogues locaux, l'orbe hardcodée
  et les événements `fixed_star_conjunction` sans contribution contrôlée.
- Required guard behavior:
  - Échouer si `_STAR_DATA`, `fixed_star_longitudes`, `fixed_star_display_name` ou `FIXED_STAR_*` reviennent comme catalogue local dans `domain/prediction`.
  - Échouer si `_compute_fixed_star_conjunctions()` conserve une condition d'orbe hardcodée `dist <= 1.0`.
  - Échouer si un événement `fixed_star_conjunction` retenu n'expose pas `orb_max` ou garde `base_weight=0.0`.
- Executable evidence:
  - `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py`
  - `pytest -q app/tests/unit/test_prediction_reference_repository.py`
  - `pytest -q tests/unit/prediction/test_public_astro_daily_events.py`
  - `rg -n "_STAR_DATA|fixed_star_(longitudes|display_name)|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"`
  - `rg -n "dist <= 1\\.0" app/domain/prediction/enriched_astro_events_builder.py`

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

Le code actuel indique:

- Evidence 1: `backend/app/infra/db/models/reference.py` - `AstralFixedStarDefinitionModel` possède `ecliptic_longitude_deg`, `visual_magnitude`, keywords et `is_active`.
- Evidence 2: `backend/app/infra/db/repositories/prediction_reference_repository.py` - `get_fixed_stars()` charge uniquement `key`, `display_name` et `ecliptic_longitude_deg`.
- Evidence 3: `backend/app/infra/db/repositories/prediction_schemas.py` - `FixedStarData` ne transporte pas magnitude, keywords, catégorie de source, source ni règle d'orbe.
- Evidence 4: `backend/app/domain/prediction/enriched_astro_events_builder.py` -
  `_compute_fixed_star_conjunctions()` matche la longitude mais utilise une orbe fixe `1.0`
  et `base_weight=0.0`.
- Evidence 5: `backend/app/domain/prediction/contribution_calculator.py` - la contribution
  multiplie par `event.base_weight`; un événement fixed star à `0.0` reste sans effet.
- Evidence 6: `backend/tests/unit/prediction/test_enriched_astro_events_builder.py` - un test couvre la détection runtime, mais pas orbe configurée, magnitude ni scoring.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consultés avant cadrage,
  notamment `RG-035`, `RG-095`, `RG-108`, `RG-110`, `RG-112`, `RG-113` et ajout de `RG-117`.

## 6. Target State

Après implémentation:

- `FixedStarData` porte les champs nécessaires au runtime daily: longitude, magnitude, keywords, catégorie de source et source.
- `PredictionReferenceRepository.get_fixed_stars()` ne perd plus les métadonnées disponibles en DB.
- `EnrichedAstroEventsBuilder` lit l'orbe, le seuil de magnitude et le poids depuis `LoadedPredictionContext`.
- Les conjonctions hors orbe ou hors magnitude sont filtrées.
- Les conjonctions retenues ont un `base_weight` positif, `orb_deg`, `orb_max` et métadonnées structurées.
- `DomainRouter` ou un helper dédié dans `domain/prediction` route ces événements
  via une configuration explicite de ruleset.
- Le routage ne duplique pas le moteur existant et n'invente pas une catégorie DB absente.
- Aucun champ de catégorie produit n'est présenté comme DB-backed tant qu'aucune table de référence ne l'expose.
- Les sorties publiques `astro_daily_events.fixed_stars` restent compatibles.
- Les tests prouvent que les fixed stars contribuent quand elles passent les règles et restent muettes quand elles échouent.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-035` - le moteur pur prediction ne doit pas prendre de dépendance API, infra directe ou LLM.
  - `RG-095` - `domain/astrology` ne doit pas importer prediction ni logique produit.
  - `RG-108` - les vocabulaires DB-backed ne doivent pas être recréés en constantes locales.
  - `RG-110` - `domain/prediction` ne doit pas redevenir propriétaire de mappings FR locaux.
  - `RG-112` - les constantes astrologiques DB-backed et fallbacks legacy ne doivent pas revenir.
  - `RG-113` - `_STAR_DATA`, `fixed_star_longitudes` et `fixed_star_display_name` ne doivent pas revenir dans prediction.
  - `RG-117` - les étoiles fixes daily doivent utiliser le contrat DB-backed enrichi et contribuer seulement via les règles runtime testées.
- Non-applicable invariants:
  - `RG-115` - cette story ne touche pas les points astraux natals.
  - `RG-116` - cette story ne touche pas l'interprétation éditoriale des points astraux.
- Required regression evidence:
  - Tests repository, builder, contribution/routing et projection publique.
  - Scans ciblés contre catalogues fixed stars locaux.
  - Evidence before/after persistée.
- Allowed differences:
  - Les scores daily peuvent changer uniquement quand une conjonction fixed star passe orbe, magnitude et routage.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime DTO fields. | Evidence profile: `runtime_contract_preservation`; runtime evidence: `pytest -q app/tests/unit/test_prediction_reference_repository.py`. |
| AC2 | L'orbe fixed stars n'est plus hardcodée. | Evidence profile: `targeted_forbidden_symbol_scan`; builder pytest + scan orbe. |
| AC3 | Le filtrage magnitude est explicite. | Evidence profile: `runtime_behavior`; pytest magnitude présente, absente et hors seuil. |
| AC4 | Metadata fixed stars explicite. | Evidence profile: `contract_shape`; builder pytest + projection publique; `source_category` n'est pas produit. |
| AC5 | Les événements retenus contribuent avec poids positif. | Evidence profile: `runtime_behavior`; fixed star contribution pytest. |
| AC6 | No local fixed-star catalog. | Evidence profile: `reintroduction_guard`; `rg -n "_STAR_DATA\|fixed_star_\|FIXED_STAR_" app/domain/prediction`. |
| AC7 | La validation backend ciblée passe dans le venv. | Evidence profile: `runtime_contract`; `ruff check .` et pytest ciblés listés dans le plan de validation. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline fixed stars actuel. (AC: AC1, AC2, AC5)
  - [ ] Subtask 1.1 - Créer `evidence/fixed-stars-runtime-before.md` avec les lignes actuelles `FixedStarData`, `get_fixed_stars()` et `_compute_fixed_star_conjunctions()`.
  - [ ] Subtask 1.2 - Noter explicitement `base_weight=0.0`, l'orbe `1.0` et l'absence de magnitude dans le DTO.

- [ ] Task 2 - Étendre le contrat runtime DB-backed. (AC: AC1, AC3, AC4)
  - [ ] Subtask 2.1 - Étendre `FixedStarData` sans casser les consommateurs existants.
  - [ ] Subtask 2.2 - Adapter `PredictionReferenceRepository.get_fixed_stars()` pour charger magnitude, keywords/catégorie et source depuis les modèles existants.
  - [ ] Subtask 2.3 - Mettre à jour `ContextLoader._freeze_fixed_star()`.

- [ ] Task 3 - Remplacer l'orbe hardcodée et ajouter le filtrage magnitude. (AC: AC2, AC3, AC4)
  - [ ] Subtask 3.1 - Résoudre `fixed_star_orb_deg`, `fixed_star_max_visual_magnitude`
    et `fixed_star_base_weight` depuis `ruleset_context.parameters`.
  - [ ] Subtask 3.2 - Ajouter tests pour orbe différente, hors orbe, magnitude hors seuil et magnitude absente.

- [ ] Task 4 - Brancher les contributions catégorielles. (AC: AC4, AC5)
  - [ ] Subtask 4.1 - Porter les métadonnées structurées sur `AstroEvent`.
  - [ ] Subtask 4.2 - Adapter le routage dans `domain/prediction` via des poids explicites de ruleset.
    Ne pas toucher `domain/astrology` ni présenter une catégorie produit comme DB-backed.
  - [ ] Subtask 4.3 - Ajouter un test prouvant une contribution non nulle quand l'événement passe les règles.

- [ ] Task 5 - Préserver projection publique et narration. (AC: AC4, AC6)
  - [ ] Subtask 5.1 - Vérifier que `PublicAstroDailyEventsPolicy` affiche toujours `Lune conjoint à l'étoile Regulus`.
  - [ ] Subtask 5.2 - Ajouter ou maintenir une assertion de compatibilité sur `astro_daily_events.fixed_stars`.

- [ ] Task 6 - Capturer l'after et exécuter la validation. (AC: AC6, AC7)
  - [ ] Subtask 6.1 - Créer `evidence/fixed-stars-runtime-after.md` et `evidence/guard-evidence.md`.
  - [ ] Subtask 6.2 - Exécuter lint, tests ciblés et scans négatifs dans le venv.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PredictionReferenceRepository.get_fixed_stars()` comme seul point de lecture DB fixed stars pour prediction.
  - `PredictionContext.fixed_stars` comme contrat d'entrée runtime.
  - `ContributionCalculator` pour le bornage et le calcul de contribution.
  - `DomainRouter` ou un helper adjacent sous `domain/prediction` pour le routage catégorie.
  - `PublicAstroDailyEventsPolicy` pour la projection lisible existante.
- Do not recreate:
  - Catalogues de longitudes, noms, magnitudes ou catégories fixed stars.
  - Un calculateur de contribution parallèle.
  - Un routeur catégorie parallèle hors domaine prediction.
- Shared abstraction allowed only if:
  - Elle évite une duplication réelle entre repository, builder et tests.
  - Elle reste dans `domain/prediction` ou `infra/db/repositories` selon l'ownership.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `_STAR_DATA`
- `fixed_star_longitudes`
- `fixed_star_display_name`
- `FIXED_STAR_*` constants in `backend/app/domain/prediction`
- hardcoded fixed-star orb literal inside `_compute_fixed_star_conjunctions`
- imports from `app.domain.prediction` inside `backend/app/domain/astrology`
- direct SQLAlchemy reads from `EnrichedAstroEventsBuilder`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Fixed star DB rows | `backend/app/infra/db/models/reference.py` | local constants in prediction |
| Fixed star runtime DTO | `backend/app/infra/db/repositories/prediction_schemas.py` | ad hoc dicts in builder/tests |
| Fixed star reference loading | `backend/app/infra/db/repositories/prediction_reference_repository.py` | direct DB calls from domain |
| Daily event detection | `backend/app/domain/prediction/enriched_astro_events_builder.py` | services or API routes |
| Contribution scoring | `backend/app/domain/prediction/contribution_calculator.py` | fixed-star-specific calculator |
| Public display | `backend/app/domain/prediction/public_astro_daily_events.py` | duplicated formatter |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/contribution_calculator.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/prediction_schemas.py` - enrichir `FixedStarData`.
- `backend/app/infra/db/repositories/prediction_reference_repository.py` - charger les champs DB manquants.
- `backend/app/services/prediction/context_loader.py` - freezer le nouveau contrat.
- `backend/app/domain/prediction/enriched_astro_events_builder.py` - appliquer orbe, magnitude, poids et métadonnées structurées.
- `backend/app/domain/prediction/domain_router.py` - router les catégories fixed stars.
- `backend/app/services/prediction/reference_seed_service.py` - ajouter les paramètres ruleset si le mécanisme existant les centralise ici.

Likely tests:

- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py` - orbe, magnitude, métadonnées.
- `backend/app/tests/unit/test_prediction_reference_repository.py` - contrat repository enrichi.
- `backend/tests/unit/prediction/test_public_astro_daily_events.py` - projection publique inchangée.
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py` - scan anti-catalogue.
- `backend/tests/unit/prediction/test_fixed_star_contributions.py` - nouveau test ciblé si aucun test existant ne couvre contribution/routing.

Files not expected to change:

- `frontend/` - aucun changement UI ou API public.
- `backend/app/domain/astrology/` - aucune logique produit fixed stars.
- `backend/migrations/versions/` - aucune nouvelle table attendue; les colonnes existent déjà.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_prediction_reference_repository.py tests/unit/prediction/test_public_astro_daily_events.py
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py
rg -n "_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"
rg -n "dist.*1\\.0" app/domain/prediction/enriched_astro_events_builder.py
rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"
```

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/00-story.md
```

## 22. Regression Risks

- Risk: les étoiles fixes restent visibles mais sans effet score.
  - Guardrail: AC5 exige contribution non nulle et preuve par test.
- Risk: un seuil d'orbe hardcodé revient dans le builder.
  - Guardrail: AC2 impose test multi-orbes et scan ciblé.
- Risk: une constante locale recrée un mini-catalogue fixed stars.
  - Guardrail: AC6 et `RG-108`/`RG-113` imposent scans négatifs.
- Risk: la magnitude est stockée en DB mais ignorée par le runtime.
  - Guardrail: AC1 et AC3 couvrent repository et builder.
- Risk: le scoring fixed stars contourne les catégories daily.
  - Guardrail: AC5 impose `ContributionCalculator` et routage sous `domain/prediction`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  deferred marker, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- `backend/app/infra/db/models/reference.py` - modèle DB fixed stars avec magnitude et source.
- `backend/app/infra/db/repositories/prediction_reference_repository.py` - chargement runtime des fixed stars.
- `backend/app/domain/prediction/enriched_astro_events_builder.py` - détection actuelle des conjonctions.
- `backend/app/domain/prediction/contribution_calculator.py` - formule de contribution impactée par `base_weight`.
- `_condamad/stories/regression-guardrails.md` - invariants applicables aux référentiels DB-backed et fixed stars.
