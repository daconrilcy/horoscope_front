# Story CS-187 brancher-points-astraux-runtime-natal: Brancher les points astraux dans le runtime natal

Status: ready-to-dev

## 1. Objective

Brancher le référentiel canonique des points astraux dans le runtime natal sans ajouter de
responsabilités aux calculateurs existants. Après implémentation, les tables `astral_point_*`
alimentent des contrats runtime immutables, un resolver transforme chaque demande métier en
instruction moteur ou dérivée, `NatalResult` expose un tableau normalisé `points[]`, les aspects
peuvent inclure ces points via option explicite, et l'interprétation consomme ces positions depuis
un service éditorial séparé.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-18 sur le branchement runtime des tables
  `AstralPointFamilyModel`, `AstralPointModel`, `AstralPointCalculationVariantModel`,
  `AstralPointAliasModel`, `AstralPointInterpretationKeywordModel`,
  `AstralPointInterpretationProfileModel` et traductions associées.
- Reason for change: les tables et seeds des points astraux existent, mais le flux natal calcule
  aujourd'hui surtout planètes, maisons, signes et aspects. Les noeuds, Lilith/apogee, perigee
  dérivé et profils éditoriaux de points ne sont pas exposés comme contrats runtime typés.

## 3. Domain Boundary

- Domain: `backend/app/domain/astrology`
- In scope:
  - Vérifier les modèles SQLAlchemy `astral_point_*`.
  - Isoler ou clarifier le seed des points astraux.
  - Étendre `AstrologyRuntimeReferenceRepository.load()` avec des contrats typés de points astraux.
  - Ajouter les dataclasses runtime immutables des points, variantes et alias.
  - Ajouter `AstralPointCalculationResolver`.
  - Ajouter `calculate_astral_points()` dans le calcul natal.
  - Normaliser `NatalResult.points`.
  - Brancher les aspects avec option explicite `include_points_in_aspects`.
  - Préparer le contrat d'enrichissement éditorial sans faire connaître keywords/profils au calcul natal.
  - Ajouter tests, guardrails, preuves persistantes et documentation `docs/tables-astral-points.md`.
- Out of scope:
  - Modifier le frontend.
  - Ajouter une nouvelle table DB ou migration de schéma sans décision utilisateur explicite.
  - Réécrire le calcul des planètes, maisons, signes ou orbes hors adaptation minimale.
  - Générer du texte éditorial ou appeler un LLM depuis `domain/astrology`.
  - Mélanger le seed des points avec les seeds d'aspects, planètes ou maisons.
- Explicit non-goals:
  - Ne pas recréer `north_node`, `south_node`, `black_moon_lilith`, apogee/perigee ou aliases sous forme de constantes métier locales hors resolver strict.
  - Ne pas exposer des champs publics plats comme `true_node`, `mean_node` ou `lilith` dans `NatalResult`.
  - Ne pas introduire de fallback silencieux quand une variante DB ou une clé moteur est absente.
  - Ne pas contourner `RG-095`, `RG-107`, `RG-108`, `RG-111`, `RG-112`, `RG-113`, `RG-114` et `RG-115`.

## 4. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les points astraux doivent provenir des tables DB et du repository runtime, pas de mappings locaux. |
| Baseline Snapshot | yes | Le payload natal et l'inventaire des points doivent être capturés avant/après. |
| Ownership Routing | yes | Le resolver décide, les calculateurs calculent, l'interprétation enrichit. |
| Allowlist Exception | no | Aucune exception ou fallback métier n'est autorisé. |
| Contract Shape | yes | `NatalResult.points` et les dataclasses runtime ajoutent une forme observable. |
| Batch Migration | no | Une seule verticale runtime natal est visée, sans migration progressive. |
| Reintroduction Guard | yes | Les points DB-backed ne doivent pas revenir comme constantes locales ou champs plats legacy. |
| Persistent Evidence | yes | Les snapshots, scans et preuves de seed/runtime restent dans le dossier de story. |

## 4a. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story enrichit un runtime natal DB-backed déjà canonique en conservant les frontières infra/domain/services.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les thèmes natals avec DB complète exposent une nouvelle collection additive `points`.
  - Les aspects n'incluent les points que si `include_points_in_aspects` est explicitement actif.
  - Aucun champ éditorial ne doit entrer dans le résultat brut du calcul natal.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un point attendu n'a pas de ligne seed canonique, de variante par
  défaut, de clé moteur ou de règle dérivée permettant de le calculer sans constante locale.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Modèles SQLAlchemy `AstralPoint*` et traductions associées.
  - Données seed `docs/db_seeder/astrology/astral_point_*.json`.
  - `AstrologyRuntimeReferenceRepository.load()` retourne des dataclasses, pas des `dict`.
- Secondary evidence:
  - Scans ciblés sur constantes, champs plats et imports interdits.
  - Documentation `docs/tables-astral-points.md`.
- Runtime artifact: DB schema `Base.metadata`, chargement DB via `AstrologyRuntimeReferenceRepository(db).load("1.0.0")` et payload Pydantic `NatalResult.model_dump()`.
- Static scans alone are not sufficient for this story because le risque principal est un référentiel DB seedé mais non consommé au runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/astral-points-runtime-before.json`
  - `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/natal-payload-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/astral-points-runtime-after.json`
  - `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/natal-payload-after.json`
- Expected invariant:
  - Planètes, maisons, signes, balances et aspects existants restent stables quand `include_points_in_aspects=false`.
  - La nouvelle collection `points[]` est additive, normalisée et dérivée du référentiel DB.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Lecture SQLAlchemy et seed JSON des points | `backend/app/infra/db/**` | `backend/app/domain/astrology/**` |
| Mapping DB vers contrats runtime | `AstrologyRuntimeReferenceRepository` / mapper infra | calculateurs planétaires, maisons ou aspects |
| Contrats immutables points/variantes/alias | `backend/app/domain/astrology/runtime/**` | `backend/app/services/**` |
| Résolution point + variante vers instruction | `AstralPointCalculationResolver` | calculateurs planétaires, serializer |
| Orchestration natal | `backend/app/domain/astrology/natal_calculation.py` et `backend/app/services/natal/calculation_service.py` | route API ou infra |
| Enrichissement keywords/profils | service d'interprétation astrology/natal | calcul natal brut |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

Contract type:

- Domain dataclasses immutables et modèle Pydantic `NatalResult`.

Fields:

- Voir champs runtime et payload natal ci-dessous.

Required fields:

- `code`, `longitude`, `sign`, `degree_in_sign`, `is_physical_body`; `variant_code` requis pour tout point avec variantes configurées.

Optional fields:

- `house`; `default_variant_code` si un point n'a pas de variante par défaut configurée.

Status codes:

- Aucun changement HTTP attendu; les erreurs de référence utilisent l'enveloppe existante.

Serialization names:

- `points` pour la liste normalisée; aucun champ plat `true_node`, `mean_node` ou `lilith`.

Frontend type impact:

- Aucun changement frontend dans cette story.

Generated contract impact:

- Note OpenAPI avant/après si le schéma public natal expose `points`.

Runtime fields:

- `AstralPointRuntime.code: str`
- `AstralPointRuntime.display_name: str`
- `AstralPointRuntime.family_code: str`
- `AstralPointRuntime.astronomical_type: str`
- `AstralPointRuntime.is_physical_body: bool`
- `AstralPointRuntime.default_variant_code: str | None`
- `AstralPointRuntime.variants: tuple of AstralPointVariantRuntime`
- `AstralPointRuntime.aliases: tuple of AstralPointAliasRuntime`
- `AstralPointVariantRuntime.variant_code: str`
- `AstralPointVariantRuntime.calculation_mode: str`
- `AstralPointVariantRuntime.engine_key: str | None`
- `AstralPointVariantRuntime.is_default: bool`
- `AstralPointAliasRuntime.alias: str`
- `AstralPointAliasRuntime.language_code: str`
- `AstralPointAliasRuntime.source: str`

Natal payload fields:

- `NatalAstralPointPosition.code: str`
- `NatalAstralPointPosition.variant_code: str | None`
- `NatalAstralPointPosition.longitude: float`
- `NatalAstralPointPosition.sign: str`
- `NatalAstralPointPosition.degree_in_sign: float`
- `NatalAstralPointPosition.house: int | None`
- `NatalAstralPointPosition.is_physical_body: bool`
- `NatalResult.points: list[NatalAstralPointPosition]`

## 5a. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-batch migration is allowed; implementation lands as one coherent backend runtime slice.

## 5b. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Runtime before | `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/astral-points-runtime-before.json` | Inventaire avant branchement runtime. |
| Runtime after | `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/astral-points-runtime-after.json` | Inventaire DB final sous contrat typé. |
| Payload before | `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/natal-payload-before.json` | Payload natal avant `points[]`. |
| Payload after | `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/natal-payload-after.json` | Payload natal après ajout de `points[]`. |
| OpenAPI impact | `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/openapi-impact.md` | Diff ou non-impact public. |
| Guard evidence | `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/evidence/guard-evidence.md` | Commandes, scans et résultats des guards. |

## 5c. Reintroduction Guard

- Reintroduction guard: required
- Reason: les points astraux sont DB-backed et ne doivent pas redevenir des constantes locales, champs plats ou payloads libres.
- Required guard behavior:
  - Échouer si `NatalResult` expose des champs plats `true_node`, `mean_node` ou `lilith`.
  - Échouer si des constantes locales `ASTRAL_POINTS`, `POINT_VARIANTS`, `NODE_VARIANTS` ou `LILITH_VARIANTS` reviennent.
  - Échouer si les keywords/profils éditoriaux sont importés dans le calcul natal brut.
- Executable evidence:
  - `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`
  - scans négatifs listés dans le plan de validation.

## 6. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - `domain/astrology` ne doit pas importer prediction.
  - `RG-107` - les JSON/rows DB ne doivent pas traverser le runtime sous forme de `dict` métier.
  - `RG-108` - un vocabulaire DB-backed ne doit pas être recréé en constante locale.
  - `RG-111` - toute table DB applicative doit rester exposée par un modèle chargé dans `Base.metadata`.
  - `RG-112` - les constantes métier astrologiques DB-backed ne doivent pas revenir.
  - `RG-113` - les longitudes/noms DB-backed ne doivent pas redevenir propriétés de `domain/prediction`.
  - `RG-114` - les enrichissements runtime DB-backed restent chargés depuis les tables canoniques.
  - `RG-115` - les points astraux natals traversent le runtime sous contrats typés.

## 6a. Current State Evidence

- Evidence 1: `backend/app/infra/db/models/reference.py` - les modèles `AstralPoint*` existent avec contraintes uniques et FK principales.
- Evidence 2: `backend/app/infra/db/models/interpretation_reference.py` - `AstralPointInterpretationProfileModel` existe avec FK composite vers les variantes.
- Evidence 3: `backend/app/infra/db/repositories/reference_repository.py` - `seed_astral_point_defaults()` charge families, points, variants, aliases, keywords et profiles.
- Evidence 4: `backend/app/domain/astrology/natal_calculation.py` - `NatalResult` expose les
  planètes, maisons, signes runtime, balance, maîtres et aspects, mais pas encore les points.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultés avant cadrage,
  notamment `RG-095`, `RG-107`, `RG-108`, `RG-111`, `RG-112`, `RG-113`, `RG-114` et `RG-115`.

## 6b. Target State

- Les points astraux sont chargés depuis DB dans une collection runtime typed et immutable.
- Le seed des points est testable et reste séparé des aspects.
- `AstralPointCalculationResolver` traduit chaque couple point/variant en instruction calculable.
- Les règles dérivées `south_node` et `lunar_perigee` appliquent un offset explicite de 180 degrés.
- `NatalResult.points` contient des positions normalisées et assignées à une maison.
- Les aspects peuvent inclure les points uniquement via `include_points_in_aspects`.
- Le calcul natal ne charge pas les keywords ni les profils éditoriaux.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les modèles points/profils sont dans `Base.metadata` avec contraintes/FK attendues. | `pytest -q app/tests/unit/test_astral_point_seed_integrity.py`. |
| AC2 | Le seed des points passe par une unité dédiée ou équivalente clairement séparée. | `pytest -q app/tests/unit/test_prediction_reference_repository.py`. |
| AC3 | `load_astral_points()` ou le chargement runtime équivalent retourne uniquement des objets typed immutables. | `pytest -q app/tests/unit/test_astral_point_repository.py`. |
| AC4 | Le seed rejette les références de variantes invalides. | `pytest -q app/tests/unit/test_astral_point_seed_integrity.py`. |
| AC5 | `AstralPointCalculationResolver` retourne une instruction de calcul typée. | `pytest -q tests/unit/domain/astrology/test_astral_point_calculation_resolver.py`. |
| AC6 | `calculate_astral_points()` produit des positions de points normalisées. | `pytest -q tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`. |
| AC7 | `NatalResult.points` est une liste; aucun champ plat point n'est introduit. | `pytest -q app/tests/unit/test_natal_calculation_service.py` + scan négatif. |
| AC8 | L'option `include_points_in_aspects` préserve ou inclut les points. | `pytest -q tests/unit/domain/astrology/test_natal_aspects_include_points.py`. |
| AC9 | Le calcul natal ne charge pas keywords/profils; l'enrichissement est séparé. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC10 | `docs/tables-astral-points.md` documente le contrat runtime. | `pytest -q app/tests/unit/test_backend_docs_ownership.py` si applicable. |
| AC11 | Les preuves avant/après viennent d'un chargement runtime. | `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'état initial et vérifier le schéma (AC: AC1, AC11)
- [ ] Task 2 - Isoler le seed des points astraux (AC: AC2, AC4)
- [ ] Task 3 - Ajouter les contrats runtime typed (AC: AC3, AC4)
- [ ] Task 4 - Implémenter `AstralPointCalculationResolver` (AC: AC5)
- [ ] Task 5 - Brancher `calculate_astral_points()` dans le calcul natal (AC: AC6, AC7)
- [ ] Task 6 - Brancher les aspects optionnels (AC: AC8)
- [ ] Task 7 - Séparer interprétation et calcul (AC: AC9)
- [ ] Task 8 - Documenter et produire les preuves finales (AC: AC10, AC11)

## 8a. Mandatory Reuse / DRY Constraints

- Reuse:
  - modèles `AstralPoint*` existants pour familles, points, variantes, alias, keywords et profils.
  - `AstrologyRuntimeReferenceRepository` et `AstrologyRuntimeReferenceMapper`.
  - `sign_from_longitude`, `assign_house_number`, `build_aspect_body_from_position` et `calculate_major_aspects`.
- Do not recreate:
  - catalogue local de noeuds lunaires, Lilith, apogee/perigee, aliases ou variantes.
  - second calculateur d'aspects pour les points.
  - second pipeline natal.

## 8b. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- champs `NatalResult.true_node`, `NatalResult.mean_node`, `NatalResult.lilith`
- payload public plat contenant `true_node`, `mean_node` ou `lilith`
- `ASTRAL_POINTS = {`, `POINT_VARIANTS = {`, `NODE_VARIANTS = {`, `LILITH_VARIANTS = {`
- keywords ou profils éditoriaux importés par `backend/app/domain/astrology/natal_calculation.py`
- nouveau `requirements.txt`

## 8c. Files to Inspect First

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/interpretation_reference.py`
- `backend/app/infra/db/models/translation_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_reference_sources.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/natal/calculation_service.py`
- `_condamad/stories/regression-guardrails.md`

## 9. Validation Plan

Depuis la racine du dépôt:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astral_point_seed_integrity.py
pytest -q app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_repository.py
pytest -q tests/unit/domain/astrology/test_astral_point_calculation_resolver.py
pytest -q tests/unit/domain/astrology/test_natal_result_contains_configured_points.py
pytest -q tests/unit/domain/astrology/test_natal_aspects_include_points.py
pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py
pytest -q app/tests/unit/test_natal_calculation_service.py
rg -n "true_node|mean_node|\blilith\b" app/domain/astrology app/services/natal -g "*.py"
rg -n "ASTRAL_POINTS\s*=|POINT_VARIANTS\s*=|NODE_VARIANTS\s*=|LILITH_VARIANTS\s*=" app/domain/astrology app/services/natal -g "*.py"
rg -n "dict\[str, Any\]|list\[dict" app/domain/astrology/runtime `
  app/infra/db/repositories/astrology_runtime_reference_repository.py `
  app/infra/db/repositories/astrology_runtime_reference_mapper.py -g "*.py"
rg -n "AstralPointInterpretationKeywordModel|AstralPointInterpretationProfileModel|keyword_set|micro_note" `
  app/domain/astrology/natal_calculation.py app/domain/astrology/calculators -g "*.py"
```

Story validation, depuis la racine:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-187-brancher-points-astraux-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-187-brancher-points-astraux-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-187-brancher-points-astraux-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-187-brancher-points-astraux-runtime-natal/00-story.md
```

## 10. Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/astral_point_calculation_resolver.py`
- `backend/app/services/natal/calculation_service.py`
- `docs/tables-astral-points.md`
- tests ciblés backend et capsule evidence.

Likely tests:

- `backend/app/tests/unit/test_astral_point_seed_integrity.py`
- `backend/app/tests/unit/test_astral_point_repository.py`
- `backend/tests/unit/domain/astrology/test_astral_point_calculation_resolver.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`
- `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`

Files not expected to change:

- `frontend/**`
- `backend/pyproject.toml`
- `backend/migrations/versions/**`
- `backend/requirements.txt`

## 10a. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 10b. Regression Risks

- Risk: le resolver devient un second calculateur et duplique SwissEph.
  - Guardrail: tests du resolver sur instructions, pas sur longitudes moteur.
- Risk: `NatalResult.points` casse un serializer ou une comparaison historique.
  - Guardrail: snapshots before/after et OpenAPI impact.
- Risk: les aspects incluent les points par défaut.
  - Guardrail: option `include_points_in_aspects=false` par défaut.
- Risk: les keywords éditoriaux contaminent le calcul brut.
  - Guardrail: scan/import guard sur `natal_calculation.py` et calculateurs.

## 10c. References

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/interpretation_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `_condamad/stories/regression-guardrails.md`

## 11. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not preserve legacy behavior for convenience.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Keep global French file comments and French docstrings on new or significantly modified files.
