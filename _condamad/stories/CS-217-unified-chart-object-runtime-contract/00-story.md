# Story CS-217 unified-chart-object-runtime-contract: Unifier le contrat runtime des objets du theme

Status: ready-to-dev

## 1. Objective

Introduire le contrat canonique `ChartObjectRuntimeData` afin que le theme natal
expose une collection unifiee `chart_objects` couvrant planetes, luminaires,
points astraux deja calcules (dont noeuds et Lilith s'ils sont presents dans la
configuration runtime), angles et cuspides de maisons. La story cree le rail
contractuel et le builder de projection runtime tout en gardant les collections
historiques, sans migrer les calculateurs metier et sans lancer les futurs
usages de dignites, dominance, interpretation, parts ou etoiles fixes.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: brief utilisateur du 2026-05-22 pour `CS-217 - Unified
  Chart Object Runtime Contract`.
- Reason for change: le moteur natal converge vers plusieurs familles
  paralleles (`planet_positions`, `astral_points`, `houses`, angles implicites,
  futures `fixed_stars` et futurs points calcules), ce qui pousserait les
  nouveaux calculateurs vers des branches `object_type` au lieu d'une selection
  par capacites.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story conserve la decision du brief:
  `capabilities` remplace `calculability`, la capacite annonce le contrat et le
  payload prouve la donnee. Les AC couvrent contrats, enums, source, builder,
  projection de planetes/luminaires/points/angles/cuspides, maintien des
  anciennes collections, payloads obligatoires par capacite, selection par
  capacites et guardrail anti-branches `object_type`.
- Brief-stakes alignment: l'enjeu est d'eviter une explosion de DTO, builders
  et calculateurs avec cas particuliers. CS-217 cree donc uniquement le socle
  unifie et la collection `chart_objects`, avec une frontiere claire: les
  branches `object_type` restent tolerees dans les builders de projection et
  interdites dans les nouveaux calculateurs metier.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`
- In scope:
  - creer `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - creer `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`;
  - definir `ChartObjectRuntimeData`, `ChartObjectCapabilities`,
    `ChartObjectPayloads`, `ChartObjectSourceRuntimeData`,
    `ChartObjectType` et `ChartObjectSourceType`;
  - definir les payloads runtime minimaux utiles au contrat si aucun contrat
    canonique equivalent n'existe deja;
  - exposer `NatalResult.chart_objects` comme collection runtime unifiee;
  - alimenter `chart_objects` depuis `planet_positions`, `astral_points`,
    `houses` et les angles ASC/MC deja disponibles dans les donnees de maisons;
  - representer les maisons dans `chart_objects` par leurs cuspides runtime
    dans CS-217, sans creer de contrat de maison concurrent;
  - conserver `planet_positions`, `astral_points`, `houses`, `aspects`,
    `dignities`, `advanced_planetary_conditions` et les autres collections
    historiques;
  - ajouter des tests de projection runtime et de non-regression natal;
  - ajouter un guardrail d'architecture borne aux nouveaux modules runtime et
    aux calculateurs metier du domaine astrologie;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou significativement modifies.
- Out of scope:
  - suppression ou remplacement des collections historiques;
  - migration profonde des aspects, dignites, dominance, interpretations,
    conditions planetaires avancees, etoiles fixes, parts arabes ou futurs
    points calcules;
  - modification volontaire de la projection JSON publique, de l'API, OpenAPI,
    DB, migrations, seeders, repositories ou frontend;
  - nouveau calcul astronomique, nouvelle ephemeride ou recalcul de positions;
  - modification des scores, poids, dignites ou profils interpretatifs.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier `backend/app/domain/astrology/dominance/**`;
  - ne pas modifier `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/planetary_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation_adapters/**`;
  - ne pas modifier `backend/app/services/chart/json_builder.py`;
  - ne pas modifier `backend/app/api/**`, `backend/app/infra/**`,
    `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas creer shim, alias, fallback silencieux ou second contrat concurrent;
  - ne pas changer les invariants `RG-135` a `RG-143`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story ajoute un contrat runtime interne et une projection
  unifiee tout en preservant les contrats existants du theme natal; les
  archetypes de suppression, API, migration ou namespace ne couvrent pas ce cas.
- Additional validation rules:
  - le contrat doit rester stable, minimal et extensible par payloads types;
  - `ChartObjectRuntimeData` ne doit pas devenir un modele monolithique rempli
    de champs optionnels metier;
  - les nouveaux modules doivent rester purs, deterministes, sans IO, DB, API,
    settings, logging, FastAPI, SQLAlchemy ou Pydantic;
  - les branches sur `object_type` sont autorisees uniquement dans les builders
    de projection;
  - les calculateurs metier ne doivent pas introduire de nouvelles branches
    `if obj.object_type == value` ou `if object_type == "planet"`;
  - toute capacite qui requiert une donnee doit verifier le payload associe et
    lever une erreur explicite si le payload manque.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise: `NatalResult.chart_objects` expose une
    collection runtime interne unifiee;
  - compatibilite attendue: les anciennes collections restent exposees et
    stables;
  - aucun changement volontaire de JSON public, API, DB, scoring,
    interpretation, dominance ou frontend.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: `chart_objects` ne peut pas etre ajoute sans
  modifier volontairement la projection JSON publique, OpenAPI, DB, frontend ou
  les collections historiques; le dev agent doit bloquer au lieu d'elargir le
  scope.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `NatalResult.chart_objects` et le builder prouvent la source runtime unifiee. |
| Baseline Snapshot | yes | Les collections historiques doivent etre comparees avant/apres. |
| Ownership Routing | yes | Les contrats vivent dans `runtime`, la projection dans `builders`, le pipeline natal branche seulement. |
| Allowlist Exception | yes | Aucune exception shim/fallback/compatibilite n'est autorisee. |
| Contract Shape | yes | La forme des dataclasses, enums, payloads et champ natal est le coeur de la story. |
| Batch Migration | no | Aucun consommateur metier n'est migre par lots dans CS-217. |
| Reintroduction Guard | yes | Le guardrail doit bloquer les nouvelles branches metier sur `object_type`. |
| Persistent Evidence | yes | Les tests, scans et snapshots doivent etre conserves dans l'evidence de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `ChartObjectRuntimeData`;
  - `build_chart_object_runtime_data`;
  - `NatalResult.chart_objects`.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`;
  - `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`;
  - AST guard:
    `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - un test d'architecture borne aux nouveaux modules runtime et aux
    calculateurs metier.
- Secondary evidence:
  - tests existants `test_natal_result_conditions_integration.py`,
    `test_natal_result_contains_configured_points.py` et
    `test_natal_result_contract.py`;
  - scans `rg` anti-branches `object_type` hors builders de projection;
  - `ruff check backend` et `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas que `chart_objects` contient les projections attendues
    ni que les anciennes collections restent stables.
- Forbidden sources:
  - API, infra, DB, migrations, services chart, frontend, scoring, dominance,
    interpretation narrative et recalcul astronomique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/natal_calculation.py`;
  - `Get-Content backend/app/domain/astrology/runtime/house_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/house_runtime_builder.py`;
  - `rg -n "class NatalResult|planet_positions|astral_points|houses|aspects" backend/app/domain/astrology/natal_calculation.py`;
  - `rg -n "ChartObjectRuntimeData|chart_objects|build_chart_object_runtime_data" backend/app backend/tests -g "*.py"`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140|RG-141|RG-142|RG-143"`.
- Comparison after implementation:
  - `rg -n "ChartObjectRuntimeData|ChartObjectCapabilities|ChartObjectPayloads|chart_objects" backend/app/domain/astrology backend/tests -g "*.py"`;
  - targeted pytest commands listed in the Validation Plan;
  - diff adjacent sur `planetary_conditions`, `dignities`, `dominance`,
    `advanced_conditions`, `interpretation`, `json_builder.py`, API, infra,
    migrations et frontend.
- Expected invariant:
  - `chart_objects` est une projection runtime supplementaire;
  - les anciennes collections restent presentes et stables;
  - les calculateurs metier ne dependent pas de branches `object_type`.
- Allowed differences:
  - nouveau contrat runtime;
  - nouveau builder pur de projection;
  - nouveau champ `NatalResult.chart_objects`;
  - branchement minimal dans `calculate_natal_chart`;
  - nouveaux tests, guardrail et evidence;
  - ajout de `RG-144`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats d'objet runtime unifie | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | `natal_calculation.py`, API schema, frontend |
| Projection depuis collections existantes | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | calculateurs metier, services chart |
| Branchement dans le theme natal | `backend/app/domain/astrology/natal_calculation.py` | API, DB, frontend |
| Selection des entrees par capacite | calculateurs futurs du domaine astrologie | branches `object_type` |
| Compatibilite collections historiques | `NatalResult` existant | shim, alias, fallback ou second owner |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-217. | Politique permanente sans exception. |

Validation rule:

- Toute exception requise doit bloquer l'implementation et exiger une decision
  utilisateur; aucune exception wildcard, dossier entier, fallback silencieux
  ou compatibilite transitoire ne doit etre ajoutee.

## 4f. Contract Shape

- Contract type:
  - dataclasses immuables `frozen=True, slots=True`;
  - enums `StrEnum`;
  - builder pur retournant un tuple de `ChartObjectRuntimeData`.
- Fields:
  - `ChartObjectRuntimeData.code`;
  - `ChartObjectRuntimeData.object_type`;
  - `ChartObjectRuntimeData.display_name`;
  - `ChartObjectRuntimeData.longitude`;
  - `ChartObjectRuntimeData.latitude`;
  - `ChartObjectRuntimeData.zodiac_position`;
  - `ChartObjectRuntimeData.source`;
  - `ChartObjectRuntimeData.capabilities`;
  - `ChartObjectRuntimeData.classifications`;
  - `ChartObjectRuntimeData.payloads`.
- Required fields:
  - every `ChartObjectRuntimeData` field listed above;
  - every `ChartObjectCapabilities` boolean listed below;
  - every `ChartObjectPayloads` typed slot listed below;
  - `ChartObjectSourceRuntimeData.source_type`;
  - `ChartObjectSourceRuntimeData.source_key`.
- Optional fields:
  - `longitude`;
  - `latitude`;
  - `zodiac_position`;
  - individual payload slots when their matching capability is false;
  - future typed payload slots in later stories.
- Required dataclasses:
  - `ChartObjectRuntimeData`;
  - `ChartObjectCapabilities`;
  - `ChartObjectPayloads`;
  - `ChartObjectSourceRuntimeData`.
- Required enum values:
  - `ChartObjectType.PLANET`;
  - `ChartObjectType.LUMINARY`;
  - `ChartObjectType.ASTRAL_POINT`;
  - `ChartObjectType.ANGLE`;
  - `ChartObjectType.HOUSE_CUSP`;
  - `ChartObjectType.FIXED_STAR`;
  - `ChartObjectType.ARABIC_PART`;
  - `ChartObjectType.CALCULATED_POINT`;
  - `ChartObjectSourceType.EPHEMERIS`;
  - `ChartObjectSourceType.HOUSE_SYSTEM`;
  - `ChartObjectSourceType.CATALOG`;
  - `ChartObjectSourceType.DERIVED`;
  - `ChartObjectSourceType.USER_OPTION`.
- Required `ChartObjectRuntimeData` fields:
  - `code: str`;
  - `object_type: ChartObjectType`;
  - `display_name: str`;
  - `longitude: float | None`;
  - `latitude: float | None`;
  - `zodiac_position: ZodiacPositionRuntimeData | None`;
  - `source: ChartObjectSourceRuntimeData`;
  - `capabilities: ChartObjectCapabilities`;
  - `classifications: tuple de chaines`;
  - `payloads: ChartObjectPayloads`.
- Required `ChartObjectCapabilities` fields:
  - `supports_aspects`;
  - `supports_dignities`;
  - `supports_house_position`;
  - `supports_visibility`;
  - `supports_motion`;
  - `supports_interpretation`;
  - `supports_dominance`;
  - `supports_fixed_star_conjunction`.
- Required `ChartObjectPayloads` fields:
  - `motion`;
  - `visibility`;
  - `dignity`;
  - `planetary_conditions`;
  - `fixed_star`;
  - `house_cusp`;
  - `angle`.
- Required builder behavior:
  - planetes et luminaires ont `supports_aspects=True`;
  - planetes et luminaires ont `supports_house_position=True`;
  - planetes hors luminaires peuvent avoir `supports_dignities=True` seulement
    si le payload de dignite est disponible;
  - points astraux existants peuvent supporter aspects et interpretation selon
    leur reference runtime;
  - angles ont `object_type=ANGLE`, source `HOUSE_SYSTEM` et payload `angle`;
  - cuspides ont `object_type=HOUSE_CUSP`, source `HOUSE_SYSTEM` et payload
    `house_cusp`;
  - les maisons sont couvertes par les cuspides `HOUSE_CUSP` dans CS-217; un
    objet runtime `HOUSE` distinct est hors scope sauf decision utilisateur;
  - toute declaration `supports_motion=True` exige `payloads.motion`;
  - toute declaration `supports_visibility=True` exige `payloads.visibility`;
  - toute declaration `supports_dignities=True` exige `payloads.dignity`;
  - si la donnee de dignite n'est pas disponible dans CS-217, le builder doit
    garder `supports_dignities=False` et documenter cette decision dans les
    tests ou l'evidence.
- Public function shape:

```python
build_chart_object_runtime_data(
    *,
    planet_positions: Sequence[PlanetPosition],
    astral_points: Sequence[NatalAstralPointPosition],
    houses: Sequence[HouseRuntimeData],
) -> tuple[ChartObjectRuntimeData]
```

- Status codes:
  - aucun endpoint HTTP, methode ou status code n'est modifie.
- Serialization names:
  - `NatalResult.chart_objects` est le nom runtime interne attendu;
  - si la convention actuelle de `NatalResult` exclut les champs internes du
    JSON public, `chart_objects` doit suivre cette convention.
- Frontend type impact:
  - aucun type frontend ne change.
- Generated contract impact:
  - aucun OpenAPI, client genere, schema genere ou contrat API public n'est
    volontairement modifie.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-217 cree le rail contractuel et ne migre aucun calculateur
  existant vers `chart_objects`.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, lint, `RG-135` a `RG-144` et absence de regression JSON/API/frontend. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que les calculateurs metier ajoutent des branches par famille
    d'objet au lieu de consommer `ChartObjectCapabilities`.
- Forbidden examples in calculators outside projection builders:
  - `if object_type == "planet"`;
  - `if object_type == "angle"`;
  - `if object_type == "fixed_star"`;
  - `if object_type == "astral_point"`;
  - `if obj.object_type ==`;
  - `match obj.object_type`;
  - `match object_type`.
- Tolerated boundary:
  - `chart_object_runtime_builder.py` peut convertir les collections
    historiques en `ChartObjectRuntimeData`;
  - les tests peuvent contenir des assertions sur `object_type`;
  - les enums et contrats peuvent declarer les valeurs `object_type`.
- Required guard evidence:
  - architecture guard against reintroduced branches `object_type`;
  - test AST borne;
  - scans `rg` bornes;
  - diff adjacent obligatoire.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

Le codebase actuel ou l'audit indique:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-216` est la derniere
  story numerotee avant cette creation et elle est enregistree comme `done`.
- Evidence 2: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` expose `planet_positions`, `houses`, `astral_points`,
  `aspects`, `dignities`, `advanced_planetary_conditions` et
  `interpretation_profiles_by_planet`, mais pas encore `chart_objects`.
- Evidence 3: `backend/app/domain/astrology/builders/house_runtime_builder.py`
  - le package `builders` existe deja pour les projections runtime pures.
- Evidence 4: `backend/app/domain/astrology/runtime/house_runtime_data.py` -
  les contrats runtime immuables de maison existent deja dans `runtime`.
- Evidence 5: `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
  - les champs internes de `NatalResult` sont deja testes comme exclus du schema
  public.
- Evidence 6: `backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`
  - les points astraux existants sont couverts comme collection historique.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage, notamment `RG-135` a `RG-143`.
- Evidence 8: source-alignment review - le brief demande explicitement une
  collection unifiee consommee par capacites, sans suppression des collections
  historiques et sans migration profonde des consommateurs.

## 6. Target State

Apres implementation:

- `NatalResult` expose `chart_objects` comme collection runtime unifiee.
- Les planetes et luminaires calcules sont projetes en objets runtime.
- Les points astraux existants, incluant noeuds et Lilith lorsqu'ils sont
  configures, sont projetes en objets runtime.
- Les angles deja disponibles depuis les maisons sont projetes en objets runtime.
- Les cuspides de maisons representent les maisons dans `chart_objects` pour
  CS-217 et sont projetees en objets runtime.
- Les anciennes collections restent presentes et stables.
- Les calculateurs peuvent selectionner leurs entrees par `capabilities`.
- Les payloads types prouvent les donnees necessaires aux capacites declarees.
- Les nouveaux calculateurs metier ne peuvent pas ajouter de branches
  `object_type`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-135` - les contrats `planetary_conditions` ne doivent pas devenir une
    dependance ou un double owner du contrat `chart_objects`.
  - `RG-141` - l'orchestration des conditions avancees reste separee du nouveau
    builder d'objets.
  - `RG-142` - le scoring accidentel ne doit pas etre migre vers le nouveau
    contrat.
  - `RG-143` - les profils symboliques ne doivent pas etre recalcules depuis
    `chart_objects` dans CS-217.
  - `RG-144` - nouvel invariant attendu pour proteger le contrat runtime
    unifie et l'usage par capacites.
- Non-applicable invariants:
  - `RG-001` a `RG-009` - la story ne touche aucune route ou facade API.
  - `RG-026` a `RG-038` - la story ne touche pas le domaine prediction.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`;
  - scans `rg` anti-branches `object_type`;
  - diff adjacent sur API, DB, JSON builder, frontend, dignities, dominance et
    planetary conditions.
- Allowed differences:
  - ajout de `chart_objects`, du contrat runtime, du builder, des tests et de
    `RG-144`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les dataclasses runtime unifiees existent. | Evidence profile: `json_contract_shape`; AST guard; `pytest -q $builder_tests` |
| AC2 | Les enums requis exposent le catalogue du brief. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC3 | Le contrat expose `capabilities`. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "calculability" $runtime_paths` |
| AC4 | Le builder produit les corps celestes principaux. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC5 | Le builder produit les points astraux existants. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC6 | Le builder produit les angles disponibles. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC7 | Le builder produit les cuspides de maisons. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC8 | `NatalResult` expose `chart_objects`. | Evidence profile: `json_contract_shape`; `pytest -q $natal_tests` |
| AC9 | Les collections natales historiques restent exposees. | Evidence profile: `baseline_before_after_diff`; `pytest -q $natal_tests` |
| AC10 | Le schema public ne change pas volontairement. | Evidence profile: `runtime_openapi_contract`; AST guard; `pytest -q $natal_tests` |
| AC11 | Un payload obligatoire manquant leve une erreur explicite. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC12 | Les objets sont filtrables par `supports_aspects`. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC13 | Les objets sont filtrables par `supports_dignities`. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC14 | Les objets sont filtrables par `supports_house_position`. | Evidence profile: `json_contract_shape`; `pytest -q $builder_tests` |
| AC15 | Les nouveaux modules restent purs. | Evidence profile: `ast_architecture_guard`; `pytest -q $architecture_tests` |
| AC16 | Les calculateurs metier restent sans branches `object_type`. | Evidence profile: `ast_architecture_guard`; `pytest -q $architecture_tests` |
| AC17 | Les surfaces hors scope ne changent pas volontairement. | Evidence profile: `baseline_before_after_diff`; `rg -n "chart_objects" $excluded_paths` |
| AC18 | Le guardrail `RG-144` est enregistre. | Evidence profile: `reintroduction_guard`; `rg -n "RG-144" _condamad/stories/regression-guardrails.md` |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les owners (AC: AC8, AC9, AC10, AC17)
  - [ ] Subtask 1.1 - Inspecter `natal_calculation.py`, `house_runtime_data.py`
    et les builders existants.
  - [ ] Subtask 1.2 - Capturer les scans initiaux `chart_objects` et
    `ChartObjectRuntimeData`.
  - [ ] Subtask 1.3 - Documenter le baseline dans `evidence/validation.md`.

- [ ] Task 2 - Creer les contrats runtime unifies (AC: AC1, AC2, AC3, AC11, AC15)
  - [ ] Subtask 2.1 - Creer `chart_object_runtime_data.py` avec commentaire
    global en francais.
  - [ ] Subtask 2.2 - Ajouter les enums et dataclasses immuables du contrat.
  - [ ] Subtask 2.3 - Ajouter la validation explicite des payloads obligatoires
    par capacite.
  - [ ] Subtask 2.4 - Exporter les symboles publics selon les conventions du
    package runtime si un `__init__.py` local existe.

- [ ] Task 3 - Creer le builder de projection (AC: AC4, AC5, AC6, AC7, AC11, AC12, AC13, AC14, AC15)
  - [ ] Subtask 3.1 - Creer `chart_object_runtime_builder.py`.
  - [ ] Subtask 3.2 - Projeter planetes et luminaires depuis
    `PlanetPosition`.
  - [ ] Subtask 3.3 - Projeter les points astraux depuis
    `NatalAstralPointPosition`.
  - [ ] Subtask 3.4 - Projeter angles et cuspides depuis `HouseRuntimeData` et
    les donnees ASC/MC disponibles.
  - [ ] Subtask 3.5 - Garder les branches `object_type` limitees au builder de
    projection.

- [ ] Task 4 - Brancher `chart_objects` dans `NatalResult` (AC: AC8, AC9, AC10, AC17)
  - [ ] Subtask 4.1 - Ajouter le champ `chart_objects` dans `NatalResult`.
  - [ ] Subtask 4.2 - Appeler le builder apres construction des positions,
    points et maisons.
  - [ ] Subtask 4.3 - Garder les anciennes collections inchangees.
  - [ ] Subtask 4.4 - Exclure le champ du schema public si la convention des
    champs runtime internes l'exige.

- [ ] Task 5 - Ajouter les tests runtime et non-regression (AC: AC1, AC2, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Subtask 5.1 - Creer
    `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`.
  - [ ] Subtask 5.2 - Creer ou etendre
    `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`.
  - [ ] Subtask 5.3 - Couvrir payload manquant, filtrage par capacites et
    stabilite des collections historiques.
  - [ ] Subtask 5.4 - Maintenir les tests existants du runtime natal.

- [ ] Task 6 - Ajouter les guardrails anti-drift (AC: AC15, AC16, AC17, AC18)
  - [ ] Subtask 6.1 - Creer
    `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`.
  - [ ] Subtask 6.2 - Bloquer les nouveaux patterns `object_type` dans les
    calculateurs metier hors builders.
  - [ ] Subtask 6.3 - Ajouter `RG-144` dans
    `_condamad/stories/regression-guardrails.md`.
  - [ ] Subtask 6.4 - Executer les scans bornes du Validation Plan.

- [ ] Task 7 - Valider et documenter (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer les tests cibles.
  - [ ] Subtask 7.3 - Executer `ruff format backend`, `ruff check backend` et
    `pytest -q`.
  - [ ] Subtask 7.4 - Documenter commandes, resultats et risques residuels dans
    `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetPosition` et `NatalAstralPointPosition` depuis `natal_calculation.py`
    comme sources de projection;
  - `HouseRuntimeData` depuis `runtime/house_runtime_data.py`;
  - `ZodiacPositionRuntimeData` si un contrat canonique existe deja dans
    `runtime`;
  - les conventions `SkipJsonSchema` et `exclude=True` deja employees dans
    `NatalResult` pour les champs internes;
  - les builders existants comme modele de projection pure.
- Do not recreate:
  - les calculateurs de positions planetaires;
  - le calcul de maisons ou d'angles;
  - les contrats `planetary_conditions`;
  - les moteurs de dignites, dominance, interpretation ou aspects;
  - un schema API ou type frontend concurrent.
- Shared abstraction allowed only if:
  - elle reste dans `runtime` ou `builders`;
  - elle evite une duplication reelle dans la projection;
  - elle ne cree pas un second contrat actif.

## 10. No Legacy / Forbidden Paths

Interdit sans approbation explicite:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- broad allowlist
- `PASS with limitation`

Symboles et chemins explicitement interdits:

- `calculability`
- `if object_type == "planet"`
- `if object_type == "angle"`
- `if object_type == "fixed_star"`
- `if object_type == "astral_point"`
- `if obj.object_type ==`
- `match obj.object_type`
- `from app.api`
- `from app.infra`
- `from app.infrastructure`
- `from app.services`
- `sqlalchemy`
- `fastapi`
- `pydantic` dans les nouveaux modules runtime/builder
- `json_builder`
- `frontend`

Modifications de production interdites sauf justification explicite par le
scope:

- `backend/app/domain/astrology/planetary_conditions/**`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Contrat d'objet runtime unifie | `runtime/chart_object_runtime_data.py` | API, frontend, `natal_calculation.py` |
| Builder de projection unifiee | `builders/chart_object_runtime_builder.py` | calculateurs metier |
| Branchement natal | `natal_calculation.py` | services chart, DB, frontend |
| Selection metier par capacites | futurs calculateurs consommateurs | branches `object_type` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is intentionally affected by CS-217.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is intentionally affected. If an existing OpenAPI or
  public JSON snapshot changes because `NatalResult` serialization changes, the
  dev agent must stop and record the blocker rather than expanding CS-217.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/domain/astrology/calculators/houses.py`
- `backend/app/domain/astrology/calculators/natal.py`
- `backend/app/domain/astrology/astral_point_calculation_resolver.py`
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`
- `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md`
- `_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md`
- `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` -
  nouveaux contrats runtime unifies.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` -
  builder pur de projection.
- `backend/app/domain/astrology/natal_calculation.py` - ajout et branchement
  minimal de `chart_objects`.
- `_condamad/stories/regression-guardrails.md` - ajout de `RG-144`.
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` -
  couverture des contrats et projections.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` -
  integration `NatalResult` et compatibilite.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
  - guardrail anti-branches `object_type`.
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
  - a maintenir pour les champs internes existants.

Files not expected to change:

- `backend/app/domain/astrology/planetary_conditions/**` - conditions avancees
  hors scope.
- `backend/app/domain/astrology/dignities/**` - scoring hors scope.
- `backend/app/domain/astrology/dominance/**` - dominance hors scope.
- `backend/app/domain/astrology/advanced_conditions/**` - moteur traditionnel
  hors scope.
- `backend/app/domain/astrology/interpretation/**` - profils et interpretation
  hors scope.
- `backend/app/services/chart/json_builder.py` - projection publique hors scope.
- `backend/app/api/**` - aucune route/schema.
- `backend/app/infra/**` - aucune persistence.
- `backend/migrations/**` - aucune migration.
- `frontend/src/**` - aucun frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: `dataclasses`, `StrEnum`, les contrats runtime existants et
  pytest suffisent.

## 21. Validation Plan

Toutes les commandes Python doivent etre lancees depuis la racine du repo apres
activation du venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Tests cibles:

```powershell
$builder_tests = "backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py"
$natal_tests = "backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py"
$architecture_tests = "backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py"
$compat_tests = "backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py"
pytest -q $builder_tests
pytest -q $natal_tests
pytest -q $architecture_tests
pytest -q $compat_tests
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
```

Controles qualite:

```powershell
ruff format backend
ruff check backend
pytest -q
```

Scans requis depuis la racine du repo:

```powershell
$contract = "backend/app/domain/astrology/runtime/chart_object_runtime_data.py"
$builder = "backend/app/domain/astrology/builders/chart_object_runtime_builder.py"
$new_modules = @($contract, $builder) | Where-Object { Test-Path $_ }
$forbidden_deps = (
  "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|" +
  "sqlalchemy|fastapi|pydantic|FastAPI|SQLAlchemy|Session|repository"
)
$forbidden_public_surfaces = "json_builder|frontend|migrations|router"
$forbidden_object_type_branches = (
  "if object_type ==|if .*\\.object_type ==|match object_type|match .*\\.object_type"
)
$domain_calculators = @(
  "backend/app/domain/astrology/calculators",
  "backend/app/domain/astrology/dignities",
  "backend/app/domain/astrology/dominance",
  "backend/app/domain/astrology/advanced_conditions",
  "backend/app/domain/astrology/planetary_conditions",
  "backend/app/domain/astrology/interpretation",
  "backend/app/domain/astrology/interpretation_adapters"
)
$adjacent_diff_paths = @(
  "backend/app/domain/astrology/planetary_conditions",
  "backend/app/domain/astrology/dignities",
  "backend/app/domain/astrology/dominance",
  "backend/app/domain/astrology/advanced_conditions",
  "backend/app/domain/astrology/interpretation",
  "backend/app/domain/astrology/interpretation_adapters",
  "backend/app/services/chart/json_builder.py",
  "backend/app/api",
  "backend/app/infra",
  "backend/migrations",
  "frontend/src"
)
rg -n $forbidden_deps $new_modules
rg -n $forbidden_public_surfaces $new_modules
rg -n "calculability" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders backend/tests/unit/domain/astrology
rg -n "ChartObjectRuntimeData|ChartObjectCapabilities|ChartObjectPayloads|chart_objects" backend/app/domain/astrology backend/tests -g "*.py"
rg -n $forbidden_object_type_branches $domain_calculators -g "*.py"
rg -n "chart_objects|ChartObjectRuntimeData" backend/app/services/chart backend/app/api backend/app/infra frontend/src
Select-String "RG-144" _condamad/stories/regression-guardrails.md
git diff -- $adjacent_diff_paths
```

Resultat attendu des scans:

- imports interdits dans les nouveaux modules: zero hits;
- surfaces API/DB/frontend/json builder dans les nouveaux modules: zero hits;
- `calculability`: zero hits;
- symbols publics: hits limites aux nouveaux modules, runtime natal et tests;
- branches `object_type`: zero hit nouveau hors builders/tests/contrats;
- diff adjacent: vide sauf blocker documente.

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md"
python -B C:\dev\tools\rust_codex_orchestrator\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py $story
python -B C:\dev\tools\rust_codex_orchestrator\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py --explain-contracts $story
python -B C:\dev\tools\rust_codex_orchestrator\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py $story
python -B C:\dev\tools\rust_codex_orchestrator\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict $story
```

Regle pour les commandes sautees:

- Toute commande sautee doit etre consignée dans l'evidence finale avec la
  commande exacte, la raison, le risque et la preuve de remplacement.

## 22. Regression Risks

- Risque: le nouveau contrat devient un DTO monolithique avec des champs metier
  optionnels.
  - Guardrail: AC1, AC11, contract shape et tests de dataclasses/payloads.
- Risque: les calculateurs continuent a brancher par famille d'objet.
  - Guardrail: AC16, test AST et `RG-144`.
- Risque: les anciennes collections disparaissent ou changent de forme.
  - Guardrail: AC9, tests non-regression et baseline avant/apres.
- Risque: `chart_objects` fuit dans le JSON public ou OpenAPI.
  - Guardrail: AC10 et generated contract blocker.
- Risque: le builder duplique des calculs astronomiques ou conditions avancees.
  - Guardrail: DRY constraints, scans interdits et diff adjacent.

## 23. Dev Agent Instructions

- Implement only CS-217.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior through shim, alias, fallback or wrapper.
- Keep `ChartObjectRuntimeData` minimal and extensible by typed payloads.
- Use `capabilities`, never `calculability`.
- Keep `object_type` branches inside projection builders only.
- Do not migrate aspects, dignities, dominance, interpretation, fixed stars,
  arabic parts or advanced conditions in CS-217.
- Do not change JSON public output, API, DB, migrations or frontend.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task markers or hidden residual in-domain work.

## 24. Follow-up Story

- Next planned story: non assignee.
- Expected future scope: migrer un consommateur cible vers la selection par
  `ChartObjectCapabilities`, par exemple un calculateur d'aspects ou de
  dominance.
- Boundary: CS-217 ne migre aucun calculateur metier profond; il rend seulement
  la source runtime unifiee disponible.

## 25. References

- `backend/app/domain/astrology/natal_calculation.py` - owner actuel de
  `NatalResult`, des positions, points, maisons et branchements runtime.
- `backend/app/domain/astrology/runtime/house_runtime_data.py` - precedent local
  de contrat runtime immuable.
- `backend/app/domain/astrology/builders/house_runtime_builder.py` - precedent
  local de builder runtime pur.
- `backend/app/domain/astrology/calculators/houses.py` - source actuelle des
  cuspides et assignations de maisons.
- `backend/app/domain/astrology/calculators/natal.py` - source actuelle des
  positions planetaires.
- `backend/app/domain/astrology/astral_point_calculation_resolver.py` - source
  actuelle des points astraux calcules.
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
  - precedent de champs internes exclus du schema public.
- `backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`
  - precedent de non-regression des points astraux.
- `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md`
  - precedent d'integration runtime natal.
- `_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md`
  - precedent de scoring accidentel a ne pas elargir.
- `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md`
  - precedent de profils symboliques a ne pas elargir.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-135` a `RG-144`.
