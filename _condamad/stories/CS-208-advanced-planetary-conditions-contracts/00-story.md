# Story CS-208 advanced-planetary-conditions-contracts: Creer les contrats des conditions planetaires avancees

Status: done

## 1. Objective

Creer un module domaine strictement contractuel pour les futures conditions
planetaires avancees du moteur natal. La story doit introduire des enums et des
dataclasses immutables pour la proximite solaire, la relation
oriental/occidental, le mouvement planetaire, la visibilite, la phase lunaire,
les signaux generiques, les bundles par planete et le resultat global, sans
implementer de calculateur, scoring, interpretation, persistance, migration ou
projection publique.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour `CS-208 - Advanced
  Planetary Conditions Contracts`.
- Reason for change: les prochaines stories doivent calculer combustion,
  cazimi, under beams, orientation solaire, vitesse, retrogradation,
  stationnarite, phases lunaires et visibilite sur un contrat domaine unique,
  strictement type, au lieu de disperser des sorties libres ou des
  `dict[str, Any]`.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme un socle
  contractuel mono-domaine; les AC couvrent module, contrats, enums,
  immutabilite, absence de dependances interdites, absence de calcul metier,
  tests unitaires et scans anti-drift. Les calculateurs et integrations
  `NatalResult` restent explicitement hors scope pour CS-209 et suivantes.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/planetary_conditions`
- In scope:
  - creer `backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - creer `backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - definir les enums de severite, confiance, proximite solaire, phase
    solaire, mouvement, vitesse, visibilite, phase lunaire, waxing/waning et
    famille de condition;
  - definir les dataclasses immutables demandees par le brief;
  - exporter explicitement les contrats depuis `planetary_conditions/__init__.py`;
  - ajouter des tests unitaires de forme, instanciation, enums, immutabilite,
    bundle partiel, resultat global et annotations publiques;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les nouveaux fichiers applicatifs.
- Out of scope:
  - calcul de combustion, cazimi, under beams ou free of beams;
  - calcul oriental/occidental;
  - calcul de vitesse, retrogradation ou stationnarite;
  - calcul des phases lunaires;
  - calcul de visibilite heliacale ou astronomique;
  - scoring accidentel, dignites, dominance ou interpretation;
  - integration dans `NatalResult`, JSON public, frontend, API, DB ou
    migrations;
  - seeders, SQLAlchemy, FastAPI, Pydantic et services runtime.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier `backend/app/domain/astrology/aspects/**`;
  - ne pas modifier `backend/app/domain/astrology/houses/**`;
  - ne pas modifier `backend/app/domain/astrology/planets/**`;
  - ne pas modifier `backend/app/domain/astrology/condition/**`;
  - ne pas modifier `backend/app/domain/astrology/dominance/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation_adapters/**`;
  - ne pas modifier `backend/app/services/chart/json_builder.py`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas ajouter de `dict[str, Any]`, `Any`, shim, alias, fallback,
    compatibilite ou contrat legacy.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un nouveau module de contrats domaine purs et
  ne correspond pas aux archetypes API, suppression, migration, route,
  namespace ou service boundary. Le `custom` active les contrats Contract Shape,
  Ownership Routing, Reintroduction Guard et Baseline Snapshot.
- Additional validation rules:
  - `contracts.py` ne doit contenir aucune fonction de calcul dont le nom
    commence par `calculate_`, `compute_`, `resolve_` ou `detect_`;
  - les collections exposees par les contrats doivent etre des tuples ou des
    mappings en lecture;
  - `Mapping[str, object]` est autorise uniquement pour le champ
    `PlanetaryConditionSignal.metadata`;
  - aucune logique de priorite metier telle que cazimi avant combust avant
    under beams ne doit etre implementee dans les contrats;
  - aucune dependance vers `app.api`, `app.infra`, `app.infrastructure`,
    `app.services`, `sqlalchemy`, `fastapi` ou `pydantic` n'est autorisee.
- Behavior change allowed: no
- Behavior change constraints:
  - aucun resultat astrologique existant ne change;
  - aucun endpoint, schema public, payload JSON, seed, migration, score ou
    comportement frontend ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un contrat demande par le brief entre en conflit
  avec une convention domaine existante non compatible avec dataclasses
  immutables; le dev agent doit bloquer au lieu de creer un second style de
  contrat concurrent.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les garde-fous doivent prouver depuis les annotations et l'import graph Python que le nouveau module reste contractuel. |
| Baseline Snapshot | yes | Le dev agent doit prouver que le module n'existait pas et que l'ajout ne modifie aucune surface adjacente. |
| Ownership Routing | yes | La nouvelle responsabilite doit rester dans le nouveau package domaine et ne pas migrer vers `advanced_conditions`, services, API ou infra. |
| Allowlist Exception | no | Aucune exception, fallback, alias, shim ou compatibilite n'est autorise. |
| Contract Shape | yes | Les enums, champs, types et nullabilites des contrats sont le coeur de la story. |
| Batch Migration | no | Aucun consommateur existant n'est migre et aucune surface concurrente n'est remplacee. |
| Reintroduction Guard | yes | Les tests/scans doivent bloquer `Any`, `dict[str, Any]`, imports interdits et fonctions de calcul. |
| Persistent Evidence | yes | La baseline, les scans et la validation finale doivent etre conserves dans un artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - les annotations publiques et `__dataclass_params__` des classes importees
    depuis `app.domain.astrology.planetary_conditions`;
  - l'import graph Python du nouveau package;
  - les scans bornes sur le nouveau package pour dependances interdites,
    fonctions de calcul et types libres.
- Runtime artifact:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
    importe les contrats publics, inspecte dataclasses, slots, annotations et
    metadata en lecture seule.
- Secondary evidence:
  - `rg` scans du Validation Plan;
  - `ruff check .`;
  - `git diff` sur les surfaces adjacentes interdites.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas que les contrats publics importables sont bien des
    dataclasses immutables avec annotations attendues.
- Forbidden sources:
  - imports API, infra, services, SQLAlchemy, FastAPI ou Pydantic dans le
    package;
  - calculateur, scoring, interpretation ou prompt dans `contracts.py`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions` doit etre
    capture ou documente avant edition.
  - `rg -n "AdvancedPlanetaryConditionsResult|SolarProximityCondition" backend/app/domain/astrology backend/tests` doit identifier l'absence ou les hits preexistants exacts.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `Test-Path backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - `git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/services/chart`
- Expected invariant:
  - seuls le nouveau package `planetary_conditions`, ses tests et les exports
    strictement necessaires changent;
  - aucun calculateur, scoring, JSON public, persistence, API ou frontend ne
    change.
- Allowed differences:
  - nouveaux fichiers du module et des tests;
  - export optionnel depuis `backend/app/domain/astrology/__init__.py` seulement
    si ce fichier centralise deja les exports publics.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats avances futurs | `backend/app/domain/astrology/planetary_conditions/contracts.py` | contrats existants `advanced_conditions`, `dignities`, `condition` |
| Exports publics du nouveau package | `backend/app/domain/astrology/planetary_conditions/__init__.py` | re-export legacy ou alias de compatibilite |
| Tests de contrats purs | `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | tests API, DB, services ou frontend |
| Futures integrations `NatalResult` | out of scope for CS-208 | modification opportuniste dans `natal_calculation.py` |
| Futures projections JSON/frontend | out of scope for CS-208 | `json_builder.py` ou `frontend/src/**` |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception exacte ou large n'est autorisee. Les scans doivent
  etre zero-hit pour imports interdits, `Any`, `dict[str, Any]` et noms de
  fonctions de calcul dans le nouveau module.

## 4f. Contract Shape

- Contract type:
  - dataclasses domaine immutables plus enums `StrEnum`.
- Fields:
  - `ConditionSeverity`;
  - `ConditionConfidence`;
  - `SolarProximityConditionKey`;
  - `SolarPhaseRelationKey`;
  - `PlanetaryMotionDirection`;
  - `PlanetarySpeedState`;
  - `PlanetVisibilityKey`;
  - `MoonPhaseKey`;
  - `WaxingWaningState`;
  - `PlanetaryConditionFamily`;
  - `SolarProximityCondition`;
  - `PlanetarySolarPhaseRelation`;
  - `PlanetaryMotionCondition`;
  - `PlanetVisibilityCondition`;
  - `MoonPhaseCondition`;
  - `PlanetaryConditionSignal`;
  - `PlanetaryConditionsBundle`;
  - `AdvancedPlanetaryConditionsResult`.
- Required fields:
  - `SolarProximityCondition.planet_key: str`
  - `SolarProximityCondition.condition_key: SolarProximityConditionKey`
  - `SolarProximityCondition.sun_distance_deg: float`
  - `SolarProximityCondition.orb_deg: float | None`
  - `SolarProximityCondition.severity: ConditionSeverity`
  - `SolarProximityCondition.is_active: bool`
  - `SolarProximityCondition.source: str = "solar_proximity"`
  - `PlanetarySolarPhaseRelation.planet_key: str`
  - `PlanetarySolarPhaseRelation.relation_key: SolarPhaseRelationKey`
  - `PlanetarySolarPhaseRelation.angular_distance_deg: float`
  - `PlanetarySolarPhaseRelation.is_oriental: bool | None`
  - `PlanetarySolarPhaseRelation.is_occidental: bool | None`
  - `PlanetaryMotionCondition.planet_key: str`
  - `PlanetaryMotionCondition.speed_deg_per_day: float`
  - `PlanetaryMotionCondition.absolute_speed_deg_per_day: float`
  - `PlanetaryMotionCondition.direction: PlanetaryMotionDirection`
  - `PlanetaryMotionCondition.speed_state: PlanetarySpeedState`
  - `PlanetaryMotionCondition.is_retrograde: bool`
  - `PlanetaryMotionCondition.is_stationary: bool`
  - `PlanetaryMotionCondition.normalized_speed_ratio: float | None`
  - `PlanetVisibilityCondition.planet_key: str`
  - `PlanetVisibilityCondition.visibility_key: PlanetVisibilityKey`
  - `PlanetVisibilityCondition.is_visible: bool | None`
  - `PlanetVisibilityCondition.confidence: ConditionConfidence`
  - `PlanetVisibilityCondition.reason: str | None`
  - `MoonPhaseCondition.phase_key: MoonPhaseKey`
  - `MoonPhaseCondition.sun_moon_angle_deg: float`
  - `MoonPhaseCondition.illumination_ratio: float | None`
  - `MoonPhaseCondition.waxing_or_waning: WaxingWaningState`
  - `MoonPhaseCondition.phase_index: int | None`
  - `PlanetaryConditionSignal.planet_key: str`
  - `PlanetaryConditionSignal.condition_key: str`
  - `PlanetaryConditionSignal.condition_family: PlanetaryConditionFamily`
  - `PlanetaryConditionSignal.severity: ConditionSeverity`
  - `PlanetaryConditionSignal.confidence: ConditionConfidence`
  - `PlanetaryConditionSignal.is_active: bool`
  - `PlanetaryConditionSignal.value: float | None`
  - `PlanetaryConditionSignal.unit: str | None`
  - `PlanetaryConditionSignal.metadata: Mapping[str, object]`
  - `PlanetaryConditionsBundle.planet_key: str`
  - `PlanetaryConditionsBundle.solar_proximity: SolarProximityCondition | None`
  - `PlanetaryConditionsBundle.solar_phase_relation: PlanetarySolarPhaseRelation | None`
  - `PlanetaryConditionsBundle.motion: PlanetaryMotionCondition | None`
  - `PlanetaryConditionsBundle.visibility: PlanetVisibilityCondition | None`
  - `PlanetaryConditionsBundle.signals: tuple` immuable de `PlanetaryConditionSignal`
  - `AdvancedPlanetaryConditionsResult.conditions_by_planet: Mapping[str, PlanetaryConditionsBundle]`
  - `AdvancedPlanetaryConditionsResult.moon_phase: MoonPhaseCondition | None`
  - `AdvancedPlanetaryConditionsResult.signals: tuple` immuable de `PlanetaryConditionSignal`
- Optional fields:
  - all fields explicitly typed with `| None`;
  - `PlanetaryConditionSignal.metadata` defaults to an empty read-only mapping;
  - aggregate mappings may be empty but must remain typed.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - no public JSON serialization is added in CS-208;
  - enum values must be stable snake_case strings matching the brief.
- Frontend type impact:
  - no frontend type change.
- Generated contract impact:
  - no OpenAPI, generated client, generated schema or public API contract
    change.

### 4f.1 Enum Values

Required enum values:

- `ConditionSeverity`: `none`, `minor`, `moderate`, `major`, `extreme`
- `ConditionConfidence`: `unknown`, `low`, `medium`, `high`, `exact`
- `SolarProximityConditionKey`: `none`, `cazimi`, `combust`, `under_beams`
- `SolarPhaseRelationKey`: `unknown`, `oriental`, `occidental`,
  `conjunct_solar`
- `PlanetaryMotionDirection`: `direct`, `retrograde`, `stationary`, `unknown`
- `PlanetarySpeedState`: `unknown`, `very_slow`, `slow`, `normal`, `fast`,
  `very_fast`
- `PlanetVisibilityKey`: `unknown`, `visible`, `invisible`, `under_beams`,
  `emerging`, `heliacal_rising`, `heliacal_setting`
- `MoonPhaseKey`: `unknown`, `new_moon`, `waxing_crescent`, `first_quarter`,
  `waxing_gibbous`, `full_moon`, `waning_gibbous`, `last_quarter`,
  `waning_crescent`, `balsamic`
- `WaxingWaningState`: `unknown`, `waxing`, `waning`, `exact`
- `PlanetaryConditionFamily`: `solar_proximity`, `solar_phase`, `motion`,
  `visibility`, `lunar_phase`

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-208 ne migre aucun consommateur et ne remplace aucun module
  existant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation record | `evidence/validation.md` | Conserver baseline, commandes, scans, resultats, skipped commands, diff adjacent et statut de `RG-135`. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le module contractuel devienne un calculateur, une projection,
    un schema API ou une couche d'interpretation.
- Forbidden examples in `backend/app/domain/astrology/planetary_conditions/**`:
  - `Any`
  - `dict[str, Any]`
  - `calculate_`
  - `compute_`
  - `resolve_`
  - `detect_`
  - `from app.api`
  - `from app.infra`
  - `from app.infrastructure`
  - `from app.services`
  - `sqlalchemy`
  - `fastapi`
  - `pydantic`
  - `score_delta`
  - `interpretation`
  - `prompt`
  - `OpenAI`
  - `AIEngineAdapter`
- Required guard evidence:
  - unit tests inspectent annotations publiques;
  - scans cibles du Validation Plan retournent zero hit hors docstrings de
    test justifiees;
  - `ruff check .` et `pytest -q` passent apres activation du venv.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-208` est enregistree
  comme prochaine story canonique apres `CS-207`, avec le statut
  `ready-to-dev`.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - les invariants
  `RG-107`, `RG-118`, `RG-119`, `RG-120`, `RG-121`, `RG-122`, `RG-123` et
  `RG-124` a `RG-134` protegent les contrats typees, owners astrologiques,
  conditions avancees, JSON public, frontend et absence de recalcul local.
- Evidence 3: `backend/app/domain/astrology/advanced_conditions/contracts.py`
  - les contrats domaine astrologiques existants utilisent des
  `dataclass(frozen=True, slots=True)` et des docstrings francaises.
- Evidence 4: `backend/app/domain/astrology/dignities/contracts.py` - les
  contrats de dignites et secte sont immutables et valident la forme publique.
- Evidence 5: `backend/app/domain/astrology/condition/contracts.py` - les
  profils et signaux conditionnels existants sont des contrats immutables sans
  dependance API/infra.
- Evidence 6: `backend/app/domain/astrology/planetary_conditions` - le dossier
  n'existe pas encore avant CS-208.
- Evidence 7: `backend/tests/unit/domain/astrology` - les tests unitaires
  astrologie domaine existent sous ce root; le nouveau test doit y suivre
  l'arborescence `planetary_conditions/test_contracts.py`.

Assumptions to verify during implementation:

- `backend/app/domain/astrology/__init__.py` ne centralise pas necessairement les
  exports; ne le modifier que si une convention locale le justifie.
- Les tests peuvent utiliser `dataclasses.FrozenInstanceError` et `typing`
  introspection pour prouver l'immutabilite et l'absence de `Any`.

## 6. Target State

After implementation:

- `backend/app/domain/astrology/planetary_conditions/` existe;
- `contracts.py` contient uniquement enums et dataclasses immutables;
- `__init__.py` exporte les contrats publics du package;
- aucun calculateur, service, schema API, modele SQLAlchemy, Pydantic model,
  projection JSON ou interpretation n'est ajoute;
- les tests unitaires prouvent instanciation, enums, immutabilite, bundle
  partiel, resultat global multi-planetes et absence d'annotations publiques
  `Any` / `dict[str, Any]`;
- les scans prouvent l'absence d'import interdit et de fonctions de calcul.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les donnees astrologiques metier doivent traverser les frontieres
    sous contrats types, pas en `dict` libre.
  - `RG-118` - les contrats de dignites restent factuels et sans dependance
    infra/API/services; CS-208 doit garder la meme separation.
  - `RG-119` - les profils conditionnels ne doivent pas devenir un second moteur
    astrologique; CS-208 fournit des contrats futurs sans scoring.
  - `RG-120` - les signaux doivent rester gouvernes et non narratifs; le signal
    generique CS-208 ne doit pas porter de texte interpretatif.
  - `RG-122` - le moteur avance existant reste owner des conditions avancees
    calculees; CS-208 ne doit pas modifier ce moteur ni ses referentiels.
  - `RG-128` - `json_builder.py` reste une projection stricte et ne doit pas
    etre modifie pour calculer ces nouvelles conditions.
  - `RG-129` - le frontend reste display-only et hors scope.
  - `RG-134` - la chaine traditionnelle avancee deja fermee ne doit pas etre
    rouverte par une nouvelle story contractuelle.
- New durable invariant:
  - CS-208 doit verifier que le registre contient `RG-135`, ou l'ajouter s'il
    est absent, afin de proteger
    `backend/app/domain/astrology/planetary_conditions/**` comme module de
    contrats purs sans calcul, scoring, interpretation ni dependances
    interdites.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du nouveau module;
  - scans imports interdits / fonctions de calcul / `Any`;
  - `git diff` prouvant l'absence de changement adjacent;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau package `planetary_conditions`;
  - nouveau test unitaire;
  - ligne `RG-135` presente dans `regression-guardrails.md`;
  - export optionnel dans un `__init__.py` central si la convention existe.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le package existe. | Evidence profile: `baseline_before_after_diff`; `pytest -q $t` + `Test-Path`. |
| AC2 | Les huit dataclasses demandees sont importables. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC3 | Les dix enums demandees existent avec des valeurs snake_case stables. | Evidence profile: `deterministic_test`; assertions enum dans `test_contracts.py`. |
| AC4 | Tous les contrats publics sont frozen avec slots. | Evidence profile: `deterministic_test`; `pytest -q $t` couvre frozen et slots. |
| AC5 | `PlanetaryConditionsBundle` accepte des conditions partielles sans faux calcul. | Evidence profile: `deterministic_test`; `pytest -q $t` couvre le bundle partiel. |
| AC6 | Le resultat global accepte plusieurs planetes. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC7 | `contracts.py` n'importe aucune dependance interdite. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "from app\\.api|sqlalchemy|fastapi" $p`. |
| AC8 | `contracts.py` exclut tout calcul. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "calculate_|score_delta|prompt" $p`. |
| AC9 | Les annotations publiques excluent `Any`. | Evidence profile: `ast_architecture_guard`; `pytest -q $t` + scan `Any` cible sur `$p`; introspection dans les tests. |
| AC10 | Les collections exposees ne sont pas des listes mutables. | Evidence profile: `deterministic_test`; `pytest -q $t` couvre tuples et metadata. |
| AC11 | Les surfaces adjacentes restent sans integration. | Evidence profile: `repo_wide_negative_scan`; `rg -n "planetary_conditions" $adj` zero-hit. |
| AC12 | La qualite backend passe dans le venv. | Evidence profile: `deterministic_test`; `ruff format .`, `ruff check .`, `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC7, AC11)
  - [ ] Subtask 1.1 - Verifier l'absence du dossier `planetary_conditions`
    avant edition ou documenter tout hit existant.
  - [ ] Subtask 1.2 - Inspecter `advanced_conditions/contracts.py`,
    `dignities/contracts.py`, `condition/contracts.py` et
    `regression-guardrails.md`.
  - [ ] Subtask 1.3 - Confirmer que le nouveau package est le seul owner de ces
    contrats et que les modules existants ne doivent pas etre modifiés.

- [ ] Task 2 - Creer le module contractuel (AC: AC1, AC2, AC3, AC4, AC9, AC10)
  - [ ] Subtask 2.1 - Creer `backend/app/domain/astrology/planetary_conditions/contracts.py`.
  - [ ] Subtask 2.2 - Ajouter les enums avec `StrEnum` et les valeurs de la
    section 4f.1.
  - [ ] Subtask 2.3 - Ajouter les dataclasses `frozen=True, slots=True` avec les
    champs exacts de la section 4f.
  - [ ] Subtask 2.4 - Utiliser `Mapping[str, object]` uniquement pour
    `PlanetaryConditionSignal.metadata`, avec valeur par defaut en lecture
    seule.
  - [ ] Subtask 2.5 - Ajouter `backend/app/domain/astrology/planetary_conditions/__init__.py`
    avec exports explicites.

- [ ] Task 3 - Ajouter les tests unitaires de contrats (AC: AC2, AC3, AC4, AC5, AC6, AC9, AC10)
  - [ ] Subtask 3.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`.
  - [ ] Subtask 3.2 - Tester l'instanciation de chaque contrat.
  - [ ] Subtask 3.3 - Tester les valeurs d'enums.
  - [ ] Subtask 3.4 - Tester l'immutabilite et les `__slots__`.
  - [ ] Subtask 3.5 - Tester un bundle partiel et un resultat global avec
    plusieurs planetes.
  - [ ] Subtask 3.6 - Tester l'absence d'annotations `Any` /
    `dict[str, Any]` et la lecture seule de `metadata`.

- [ ] Task 4 - Ajouter les gardes anti-drift (AC: AC7, AC8, AC9, AC11)
  - [ ] Subtask 4.1 - Ajouter ou mettre a jour le test d'architecture le plus
    proche si le projet en a un; sinon garder les scans exacts du Validation
    Plan comme preuve obligatoire.
  - [ ] Subtask 4.2 - Verifier ou ajouter `RG-135` dans
    `_condamad/stories/regression-guardrails.md` avec un guard deterministe.
  - [ ] Subtask 4.3 - Verifier qu'aucun fichier adjacent n'a ete modifie sauf
    export central explicitement justifie.

- [ ] Task 5 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12)
  - [ ] Subtask 5.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 5.2 - Executer le test cible.
  - [ ] Subtask 5.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 5.4 - Executer les scans anti-drift.
  - [ ] Subtask 5.5 - Documenter toute commande non executee avec raison,
    risque et preuve de substitution.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - conventions `dataclass(frozen=True, slots=True)` observees dans
    `advanced_conditions/contracts.py`, `dignities/contracts.py` et
    `condition/contracts.py`;
  - `StrEnum` standard library pour les enums a valeur string;
  - `Mapping` standard library pour la seule metadata ouverte;
  - tests pytest existants sous `backend/tests/unit/domain/astrology`.
- Do not recreate:
  - `AdvancedPlanetaryCondition` existant de CS-195;
  - `PlanetConditionProfile`, `PlanetConditionSignal` et builders existants;
  - calculateurs `advanced_conditions`;
  - scoring de dignites, dominance ou signaux;
  - schemas API/Pydantic pour les memes concepts.
- Shared abstraction allowed only if:
  - elle reste dans `contracts.py`, retire une duplication reelle dans les
    tests ou annotations, et ne devient pas une logique de calcul.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- `dict[str, Any]`
- `Any`
- SQLAlchemy model
- FastAPI schema
- Pydantic API schema
- interpretation textuelle
- scoring
- calcul astronomique
- migrations
- seeders

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/planetary_conditions/**` importing `app.api`
- `backend/app/domain/astrology/planetary_conditions/**` importing `app.infra`
- `backend/app/domain/astrology/planetary_conditions/**` importing `app.infrastructure`
- `backend/app/domain/astrology/planetary_conditions/**` importing `app.services`
- `backend/app/domain/astrology/planetary_conditions/**` importing `sqlalchemy`
- `backend/app/domain/astrology/planetary_conditions/**` importing `fastapi`
- `backend/app/domain/astrology/planetary_conditions/**` importing `pydantic`
- symbols beginning with `calculate_`
- symbols beginning with `compute_`
- symbols beginning with `resolve_`
- symbols beginning with `detect_`
- `essential_score_delta`
- `accidental_score_delta`
- `interpretation_weight`

Specific forbidden production modifications unless explicitly justified by an
export convention:

- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/astrology/natal_calculation.py`
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
| Proximite solaire contractuelle | `planetary_conditions/contracts.py` | `advanced_conditions/contracts.py`, JSON builder, frontend |
| Relation oriental/occidental contractuelle | `planetary_conditions/contracts.py` | heliacal calculator, serializer |
| Mouvement planetaire contractuel | `planetary_conditions/contracts.py` | speed classifier, dignities |
| Visibilite contractuelle | `planetary_conditions/contracts.py` | heliacal calculator, frontend |
| Phase lunaire contractuelle | `planetary_conditions/contracts.py` | natal calculation, UI |
| Signal generique de condition avancee | `planetary_conditions/contracts.py` | condition signal builder, interpretation adapters |
| Bundle/resultat global | `planetary_conditions/contracts.py` | `NatalResult` until a future integration story |

## 13a. Follow-up Story

- Next planned story: `CS-209 - Solar Proximity Conditions Calculator`
- Expected scope: utiliser les contrats CS-208 pour calculer cazimi,
  combustion, under beams et none/free of beams.
- Boundary: CS-208 ne cree pas `solar_proximity_calculator.py` et ne porte
  aucune logique de priorite entre ces conditions.

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is affected by CS-208.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is affected by CS-208.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/advanced_conditions/__init__.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/__init__.py` if it exists
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exports
  publics du nouveau package.
- `backend/app/domain/astrology/planetary_conditions/contracts.py` - enums et
  dataclasses immutables.
- `_condamad/stories/regression-guardrails.md` - verifier ou ajouter
  l'invariant `RG-135`.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/evidence/validation.md`
  - baseline, scans et validation finale.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - couverture des contrats, enums, immutabilite et annotations.

Files not expected to change:

- `backend/app/domain/astrology/advanced_conditions/**` - existing engine and
  contracts remain unchanged.
- `backend/app/domain/astrology/dignities/**` - no dignity or sect change.
- `backend/app/domain/astrology/condition/**` - no profile/signal builder
  change.
- `backend/app/domain/astrology/dominance/**` - no dominance change.
- `backend/app/domain/astrology/natal_calculation.py` - no integration in
  `NatalResult`.
- `backend/app/services/chart/json_builder.py` - no public JSON change.
- `backend/app/api/**` - no route/schema change.
- `backend/app/infra/**` - no persistence change.
- `backend/migrations/**` - no migration.
- `frontend/src/**` - no frontend change.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: Python standard library dataclasses, enum and typing are
  sufficient.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py"
pytest -q $t
```

Quality checks:

```powershell
ruff format .
ruff check .
pytest -q
```

Required scans:

```powershell
$p = "backend/app/domain/astrology/planetary_conditions"
$tp = "backend/tests/unit/domain/astrology/planetary_conditions"
rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" $p -g "*.py"
rg -n "sqlalchemy|fastapi|pydantic" $p -g "*.py"
rg -n "calculate_|compute_|resolve_|detect_|score_delta|interpretation_weight" $p -g "*.py"
rg -n "prompt|OpenAI|AIEngineAdapter" $p -g "*.py"
rg -n "\\bAny\\b|dict\\[str, Any\\]" $p -g "*.py"
git diff -- `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/condition `
  backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/natal_calculation.py `
  backend/app/services/chart/json_builder.py `
  backend/app/api backend/app/infra backend/migrations frontend/src
```

Expected scan result:

- first scan: zero hits;
- second scan: zero hits in production module;
- fifth scan: zero hits for `Any` and `dict[str, Any]` in the production
  module; tests prove the same rule by introspecting public annotations, not by
  relying on a broad text scan of test prose;
- `git diff` on adjacent surfaces must be empty unless an export central is
  justified.

Story validation commands:

```powershell
$story = "_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le module contractuel devient un second moteur de conditions avancees.
  - Guardrail: AC8 et scans interdisent fonctions de calcul, scoring et
    interpretation.
- Risk: les futures stories utilisent `dict[str, Any]` au lieu des contrats.
  - Guardrail: AC9 et `RG-135` bloquent les annotations libres.
- Risk: un developpeur modifie `advanced_conditions` ou `json_builder.py` pour
  integrer les contrats trop tot.
  - Guardrail: AC11 et diff adjacent obligatoire.
- Risk: les collections mutables permettent une mutation post-calcul.
  - Guardrail: AC4 et AC10 couvrent frozen dataclasses, slots, tuples et
    metadata read-only.
- Risk: le signal generique devient interpretatif.
  - Guardrail: champ `metadata` technique seulement, pas de texte narratif,
    scans `prompt`/`interpretation_weight`.

## 23. Dev Agent Instructions

- Implement only CS-208.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias,
  fallback, or re-export.
- Keep the story strictly contract-only.
- Do not implement calculators.
- Do not integrate into `NatalResult`.
- Do not change JSON public output.
- Do not change frontend.
- Do not change DB, migrations or seeds.
- Do not add scoring, interpretation, prompts, LLM, API schemas or Pydantic
  models.
- Use dataclasses immutables unless repository evidence proves a different
  convention.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task marker or hidden residual in-domain work.

## 24. References

- `backend/app/domain/astrology/advanced_conditions/contracts.py` - convention
  actuelle des dataclasses immutables et contrats avances existants.
- `backend/app/domain/astrology/dignities/contracts.py` - convention de contrats
  immutables avec validation stricte.
- `backend/app/domain/astrology/condition/contracts.py` - contrats de profils
  et signaux conditionnels existants.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` - moteur
  avance existant a ne pas modifier dans CS-208.
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`
  - precedent de contrats explicites et projection sans recalcul.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md`
  - cloture recente a ne pas rouvrir.
- `_condamad/stories/regression-guardrails.md` - invariants applicables et
  nouvel invariant `RG-135`.
