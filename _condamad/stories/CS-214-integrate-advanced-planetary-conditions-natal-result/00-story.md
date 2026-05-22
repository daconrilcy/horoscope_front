# Story CS-214 integrate-advanced-planetary-conditions-natal-result: Integrer les conditions planetaires avancees dans NatalResult

Status: ready-to-dev

## 1. Objective

Integrer les calculateurs CS-209 a CS-213 dans le runtime natal global afin que
`NatalResult` expose un bloc natif `advanced_planetary_conditions:
AdvancedPlanetaryConditionsResult | None`. La story doit creer un orchestrateur
pur dans `planetary_conditions`, produire les bundles et signaux techniques par
planete, calculer la phase lunaire globale, puis brancher ce resultat dans le
pipeline natal sans scoring, interpretation, projection JSON publique, API, DB
ou frontend.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-22 pour `CS-214 - Integrate
  Advanced Planetary Conditions Into NatalResult`.
- Reason for change: les contrats et calculateurs purs CS-208 a CS-213 existent
  dans `planetary_conditions`, mais ils ne sont pas encore orchestrés dans le
  calcul natal principal et ne sont pas exposes par `NatalResult`.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme une integration
  runtime mono-domaine. Les AC couvrent creation de l'orchestrateur, execution
  proximite solaire, mouvement, relation solaire, visibilite, phase lunaire,
  construction des bundles, production de signaux, tolerance aux donnees
  partielles, inclusion Soleil/Lune, enrichissement optionnel de `NatalResult`,
  branchement dans `calculate_natal_chart`, et interdits de scoring,
  interpretation, API, DB, JSON public specifique, UI et LLM.
- Brief-stakes alignment: l'enjeu est de rendre les conditions planetaires
  avancees consommables par les futures dignites accidentelles, interpretation,
  scoring, rendering, API, LLM et UI, sans commencer ces usages dans CS-214.
  La story etablit donc uniquement la source runtime structuree.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology`
- In scope:
  - creer
    `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`;
  - creer
    `backend/app/domain/astrology/planetary_conditions/signal_factory.py` si
    aucun helper canonique equivalent n'existe;
  - reutiliser `AdvancedPlanetaryConditionsResult`,
    `PlanetaryConditionsBundle`, `PlanetaryConditionSignal`,
    `PlanetaryConditionFamily`, `ConditionSeverity`, `ConditionConfidence`,
    `SolarProximityCondition`, `PlanetaryMotionCondition`,
    `PlanetarySolarPhaseRelation`, `PlanetVisibilityCondition` et
    `MoonPhaseCondition` depuis `planetary_conditions/contracts.py`;
  - reutiliser les calculateurs purs publics CS-209 a CS-213;
  - ajouter les exports publics explicites depuis
    `backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - ajouter `advanced_planetary_conditions:
    AdvancedPlanetaryConditionsResult | None = None` a `NatalResult` dans
    `backend/app/domain/astrology/natal_calculation.py`;
  - brancher le calcul dans `calculate_natal_chart` depuis les positions et
    vitesses deja calculees;
  - tolerer les vitesses planetaires absentes en laissant `bundle.motion` a
    `None` pour la planete concernee;
  - tolerer les conditions partielles attendues sans casser le resultat global;
  - inclure un bundle pour le Soleil et un bundle pour la Lune;
  - calculer aussi une `moon_phase` globale quand Soleil et Lune sont presents;
  - produire des `PlanetaryConditionSignal` techniques non narratifs;
  - ajouter les tests unitaires cibles du runtime et de l'integration
    `NatalResult`;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou significativement modifies.
- Out of scope:
  - scoring accidentel ou essentiel;
  - integration dans les dignites accidentelles;
  - interpretation, narration, signification, texte editorial ou prompts;
  - rendering UI, frontend, TypeScript ou composants React;
  - endpoint API dedie, schema FastAPI, OpenAPI volontaire ou client genere;
  - serialization JSON publique specifique ou modification de
    `json_builder.py`, sauf si une compatibilite Pydantic force un ajustement
    strictement minimal et documente comme blocker;
  - DB, migrations, seeders, repositories, SQLAlchemy ou persistence;
  - observabilite, metrics, logging ou instrumentation;
  - systeme heliacal avance;
  - phases planetaires complexes Mercure/Venus;
  - recalcul astronomique des positions ou vitesses.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/condition/**`;
  - ne pas modifier `backend/app/domain/astrology/dominance/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation_adapters/**`;
  - ne pas modifier `backend/app/services/chart/json_builder.py`;
  - ne pas modifier `backend/app/api/**`, `backend/app/infra/**`,
    `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas ajouter de shim, alias, fallback, compatibilite ou second owner;
  - ne pas utiliser les signaux produits comme score, poids, interpretation ou
    decision de dignite.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un orchestrateur runtime domaine et enrichit
  un contrat runtime Pydantic existant; elle ne correspond pas aux archetypes
  API, suppression, migration, route, namespace ou service boundary.
- Additional validation rules:
  - l'orchestrateur doit rester pur, deterministe, sans IO, sans DB, sans API,
    sans settings, sans logging et sans appel ephemeride;
  - l'orchestrateur doit consommer uniquement les positions et vitesses deja
    calculees par le runtime natal;
  - `calculate_advanced_planetary_conditions` doit retourner un
    `AdvancedPlanetaryConditionsResult`;
  - le runtime natal ne doit pas contenir de logique metier conditionnelle
    detaillee du type `if combust then branch` ou `if retrograde then branch`;
  - les regles de signal doivent etre concentrees dans `signal_factory.py` ou un
    helper equivalent du meme package;
  - les signaux doivent rester techniques: `condition_key`, famille, severite,
    confiance, activation, valeur, unite et metadata factuelle seulement;
  - `score`, `score_delta`, `dignity_score`, `strength_modifier`,
    `interpretation`, `meaning`, `description`, `narrative`, `prompt`, `LLM`,
    `OpenAI`, `AIEngineAdapter`, `FastAPI`, `SQLAlchemy`, `Session`,
    `repository`, `json_builder`, `frontend` et `pydantic` sont interdits dans
    les nouveaux modules `planetary_conditions`;
  - `pydantic` reste autorise dans `natal_calculation.py` car ce fichier est
    deja le contrat Pydantic de `NatalResult`.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise: `NatalResult.advanced_planetary_conditions`
    est renseigne par defaut pendant `calculate_natal_chart`;
  - compatibilite backward: le champ reste optionnel avec valeur par defaut
    `None`, afin que les validations de payloads historiques continuent;
  - aucun endpoint, payload JSON public dedie, scoring, dignite, dominance,
    interpretation, persistence ou frontend ne change volontairement.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: `NatalResult` ne peut pas accepter
  `AdvancedPlanetaryConditionsResult` sans changer une projection publique ou un
  schema externe non couvert par cette story; le dev agent doit bloquer au lieu
  de creer une serialization parallele.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le resultat runtime et les tests de `calculate_natal_chart` prouvent la verite effective consommee par le theme natal. |
| Baseline Snapshot | yes | Il faut capturer l'etat des calculateurs CS-209 a CS-213, de `NatalResult` et des guardrails `RG-135` a `RG-141`. |
| Ownership Routing | yes | L'orchestration detaillee doit vivre dans `planetary_conditions`, tandis que `natal_calculation.py` orchestre seulement le pipeline natal. |
| Allowlist Exception | yes | Aucune exception shim/fallback/compatibilite n'est autorisee; les exceptions doivent bloquer. |
| Contract Shape | yes | La forme de la fonction runtime, du champ `NatalResult` et des signaux est le coeur de la story. |
| Batch Migration | no | Aucun consommateur existant n'est migre et aucune surface publique n'est remplacee. |
| Reintroduction Guard | yes | Les scans doivent bloquer scoring, interpretation, API, DB, JSON builder, frontend et logique detaillee dans le runtime natal. |
| Persistent Evidence | yes | La validation et les scans doivent etre conserves dans l'artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_advanced_planetary_conditions`;
  - `NatalResult.advanced_planetary_conditions`;
  - les `AdvancedPlanetaryConditionsResult` produits par les tests unitaires.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`;
  - `backend/tests/unit/domain/astrology/natal/test_natal_result_conditions_integration.py`
    si la racine `backend/tests/unit/domain/astrology/natal` est retenue, ou un
    fichier de test existant equivalent sous la topologie backend actuelle.
  - AST guard / importability guard:
    `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
    et scans `rg` bornes listés dans le Validation Plan.
- Secondary evidence:
  - tests existants CS-209 a CS-213 maintenus;
  - scans des imports interdits, scoring, interpretation et surfaces
    adjacentes;
  - `ruff check .`;
  - `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas que les calculateurs sont executes ensemble, que les
    bundles contiennent Soleil/Lune, que `motion=None` est tolere ou que
    `NatalResult` est enrichi.
- Forbidden sources:
  - API, infra, DB, services chart, frontend, JSON builder, scoring,
    interpretation, LLM, observabilite et recalcul astronomique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/signal_factory.py`;
  - `Get-Content backend/app/domain/astrology/natal_calculation.py`;
  - `rg -n "advanced_planetary_conditions|AdvancedPlanetaryConditionsResult" backend/app backend/tests -g "*.py"`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140|RG-141"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`;
  - `Test-Path backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`;
  - `rg -n $public_symbols $planetary_condition_paths`;
  - `rg -n "advanced_planetary_conditions" backend/app/domain/astrology/natal_calculation.py backend/tests -g "*.py"`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140|RG-141"`.
- Expected invariant:
  - l'orchestrateur assemble des faits deja calculables par CS-209 a CS-213;
  - `natal_calculation.py` ne fait qu'extraire positions/vitesses, appeler
    l'orchestrateur et injecter le resultat dans `NatalResult`;
  - `json_builder.py`, API, infra, migrations et frontend restent inchanges.
- Allowed differences:
  - nouveau runtime d'orchestration;
  - nouveau signal factory lorsque requis par le scope;
  - nouveaux exports publics du package `planetary_conditions`;
  - nouveau champ optionnel sur `NatalResult`;
  - branchement minimal dans `calculate_natal_chart`;
  - nouveaux tests unitaires;
  - evidence de validation et ajout de `RG-141`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats de conditions avancees | `planetary_conditions/contracts.py` | contrats locaux dans `natal_calculation.py`, API schema, frontend type |
| Calculs unitaires de conditions | `planetary_conditions/*_calculator.py` | `natal_calculation.py`, dignities, services chart |
| Orchestration avancee pure | `planetary_conditions/advanced_planetary_conditions_runtime.py` | `advanced_conditions`, API, services, infra, frontend |
| Signaux techniques de conditions | `planetary_conditions/signal_factory.py` ou helper du meme package | scoring, interpretation adapters, frontend |
| Branchement pipeline natal | `backend/app/domain/astrology/natal_calculation.py` | services chart, API, DB |
| Projection JSON publique | out of scope | ne pas modifier dans CS-214 |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-214. | Politique permanente sans exception. |

Validation rule:

- Toute exception requise doit bloquer l'implementation et exiger une decision
  utilisateur; aucune exception wildcard, dossier entier, fallback silencieux ou
  compatibilite transitoire ne doit etre ajoutee.

## 4f. Contract Shape

- Contract type:
  - fonction pure importable retournant `AdvancedPlanetaryConditionsResult`;
  - champ Pydantic optionnel sur `NatalResult`;
  - signaux techniques `PlanetaryConditionSignal`.
- Fields:
  - `AdvancedPlanetaryConditionsResult.conditions_by_planet`;
  - `AdvancedPlanetaryConditionsResult.moon_phase`;
  - `AdvancedPlanetaryConditionsResult.signals`;
  - `PlanetaryConditionsBundle.planet_key`;
  - `PlanetaryConditionsBundle.solar_proximity`;
  - `PlanetaryConditionsBundle.solar_phase_relation`;
  - `PlanetaryConditionsBundle.motion`;
  - `PlanetaryConditionsBundle.visibility`;
  - `PlanetaryConditionsBundle.signals`;
  - `NatalResult.advanced_planetary_conditions`.
- Required fields:
  - `planetary_positions: Mapping[str, PlanetPosition]` ou mapping equivalent
    adapte au runtime existant;
  - `planetary_speeds_deg_per_day: Mapping[str, float]`;
  - `conditions_by_planet: Mapping[str, PlanetaryConditionsBundle]`;
  - `signals: tuple[PlanetaryConditionSignal]`.
- Optional fields:
  - `PlanetaryConditionsBundle.motion: PlanetaryMotionCondition | None`;
  - `PlanetaryConditionsBundle.visibility: PlanetVisibilityCondition | None`
    seulement si une condition amont requise manque;
  - `AdvancedPlanetaryConditionsResult.moon_phase: MoonPhaseCondition | None`;
  - `NatalResult.advanced_planetary_conditions:
    AdvancedPlanetaryConditionsResult | None = None`.
- Status codes:
  - aucun endpoint HTTP, methode ou status code n'est modifie.
- Serialization names:
  - aucun contrat JSON public dedie n'est ajoute dans CS-214;
  - le nom interne attendu du champ Pydantic est
    `advanced_planetary_conditions`.
- Frontend type impact:
  - aucun type frontend ne change.
- Generated contract impact:
  - aucun OpenAPI, client genere, schema genere ou contrat API public n'est
    volontairement modifie.
- Public function shape:

```python
calculate_advanced_planetary_conditions(
    *,
    planetary_positions: Mapping[str, PlanetPosition],
    planetary_speeds_deg_per_day: Mapping[str, float],
) -> AdvancedPlanetaryConditionsResult
```

- Accepted adaptation:
  - si importer `PlanetPosition` depuis `natal_calculation.py` cree une boucle
    d'import, l'orchestrateur doit typer l'entree avec un `Protocol` local ou
    un mapping strict des champs necessaires (`longitude`, `speed_longitude`)
    sans creer de contrat concurrent public.
- Signal keys minimales:
  - `combust`;
  - `under_beams`;
  - `retrograde`;
  - `stationary`;
  - `emerging`;
  - `oriental`;
  - `occidental`;
  - `waxing_moon`;
  - `waning_moon`.
- Signal source rule:
  - les signaux planetaires proviennent de chaque
    `PlanetaryConditionsBundle`;
  - les signaux lunaires globaux `waxing_moon` et `waning_moon` proviennent de
    `AdvancedPlanetaryConditionsResult.moon_phase` via `_build_global_signals`
    ou un helper equivalent du package `planetary_conditions`;
  - `result.signals` agrege les signaux des bundles et les signaux globaux sans
    ajouter de narration, poids, score ou interpretation.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-214 ne migre aucun consommateur existant et ne remplace aucun
  module public.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, statut `RG-135` a `RG-141` et absence de scoring/interpretation/API/DB/frontend. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que l'integration runtime des conditions planetaires avancees
    devienne une couche de scoring, interpretation, projection JSON, API, DB,
    frontend ou second moteur astrologique.
- Forbidden examples in
  `advanced_planetary_conditions_runtime.py` and `signal_factory.py`:
  - `score`
  - `score_delta`
  - `dignity_score`
  - `accidental_score_delta`
  - `essential_score_delta`
  - `strength_modifier`
  - `interpretation`
  - `meaning`
  - `description`
  - `narrative`
  - `prompt`
  - `LLM`
  - `OpenAI`
  - `AIEngineAdapter`
  - `FastAPI`
  - `SQLAlchemy`
  - `Session`
  - `repository`
  - `json_builder`
  - `frontend`
  - `from app.api`
  - `from app.infra`
  - `from app.infrastructure`
  - `from app.services`
  - `sqlalchemy`
  - `fastapi`
  - `pydantic`
- Forbidden detailed condition logic in `natal_calculation.py`:
  - `combust`
  - `under_beams`
  - `retrograde`
  - `stationary`
  - `emerging`
  - `oriental`
  - `occidental`
  - `waxing_moon`
  - `waning_moon`
- Required guard evidence:
  - tests unitaires comportementaux;
  - scans cibles du Validation Plan;
  - diff des surfaces adjacentes obligatoire.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-213` est la derniere
  story numerotee avant cette creation et elle est enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
  - la section `Follow-up Story` annonce `CS-214 - Integrate Advanced
  Planetary Conditions Into NatalResult`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `AdvancedPlanetaryConditionsResult`, `PlanetaryConditionsBundle` et
  `PlanetaryConditionSignal` existent deja.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - les calculateurs CS-209 a CS-213 sont exportes, mais aucun export
  `calculate_advanced_planetary_conditions` n'existe encore.
- Evidence 5: `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - fournit `calculate_solar_proximity_conditions`.
- Evidence 6: `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  - fournit `calculate_planetary_motion_conditions` depuis des vitesses deja
  fournies.
- Evidence 7: `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  - fournit `calculate_solar_phase_relations`.
- Evidence 8: `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  - fournit `calculate_moon_phase_condition`.
- Evidence 9: `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
  - fournit `calculate_planet_visibility_conditions` en composant proximite et
  relation solaire.
- Evidence 10: `backend/app/domain/astrology/natal_calculation.py` -
  `PlanetPosition` contient `planet_code`, `longitude` et `speed_longitude`,
  `NatalResult` n'expose pas encore `advanced_planetary_conditions`, et
  `calculate_natal_chart` construit deja `positions` avant dignites, profils,
  conditions avancees existantes, dominantes et interpretation adapter.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - `RG-135` protege
  les contrats, `RG-136` la proximite solaire, `RG-137` le mouvement, `RG-138`
  la relation solaire, `RG-139` la phase lunaire et `RG-140` la visibilite.

Assumptions to verify during implementation:

- `advanced_planetary_conditions_runtime.py` n'existe pas encore;
- `signal_factory.py` n'existe pas encore sous `planetary_conditions`;
- la topologie de tests cible peut etre
  `backend/tests/unit/domain/astrology/planetary_conditions` et
  `backend/tests/unit/domain/astrology/natal`; si la racine `natal` n'existe
  pas, utiliser le dossier de tests natal deja canonique sans creer de racine
  non conforme a la topologie backend;
- les vitesses absentes doivent etre filtrees avant appel au calculateur de
  mouvement, car `calculate_planetary_motion_conditions` attend des flottants
  finis et un profil connu.

## 6. Target State

After implementation:

- `advanced_planetary_conditions_runtime.py` existe et reste pur;
- `calculate_advanced_planetary_conditions` retourne un
  `AdvancedPlanetaryConditionsResult`;
- l'orchestrateur extrait les longitudes depuis les positions fournies et
  reutilise la longitude du Soleil et de la Lune sans recalcul astronomique;
- les calculateurs de proximite solaire, mouvement, relation solaire,
  visibilite et phase lunaire sont appeles depuis l'orchestrateur;
- chaque planete presente dans `planetary_positions` recoit un
  `PlanetaryConditionsBundle`;
- le Soleil recoit un bundle;
- la Lune recoit un bundle et le resultat global expose aussi `moon_phase`;
- les vitesses absentes ou non utilisables ne cassent pas le resultat global et
  laissent `bundle.motion` a `None`;
- les conditions partielles tolerees ne cassent pas la construction de
  `AdvancedPlanetaryConditionsResult`;
- les signaux techniques minimaux sont produits pour les conditions actives
  pertinentes et agreges dans `bundle.signals` et `result.signals`;
- `NatalResult` expose `advanced_planetary_conditions` avec une valeur par
  defaut `None`;
- `calculate_natal_chart` renseigne ce champ avec le resultat de
  l'orchestrateur;
- aucune dignite, dominance, interpretation, projection JSON publique, API, DB,
  migration ou UI n'est ajoutee;
- les tests unitaires, scans anti-drift et checks qualite passent dans le venv.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les faits astrologiques doivent traverser les frontieres sous
    contrats types, pas en dictionnaires libres.
  - `RG-119` - les profils et signaux conditionnels ne doivent pas devenir un
    second moteur astrologique ou une source locale de scoring.
  - `RG-122` - le moteur avance existant ne doit pas absorber cette orchestration
    des conditions planetaires avancees.
  - `RG-128` - `json_builder.py` reste une projection stricte et ne calcule pas
    les conditions.
  - `RG-129` - le frontend reste hors scope et ne derive pas les conditions.
  - `RG-135` - les contrats `planetary_conditions` restent immutables, sans
    scoring, interpretation ni dependance interdite.
  - `RG-136` - la proximite solaire reste calculee par son calculateur pur.
  - `RG-137` - le mouvement planetaire reste calcule par son calculateur pur.
  - `RG-138` - la relation solaire reste calculee par son calculateur pur.
  - `RG-139` - la phase lunaire reste calculee par son calculateur pur.
  - `RG-140` - la visibilite planetaire reste calculee par son calculateur pur.
- New durable invariant:
  - ajouter `RG-141` pour proteger
    `planetary_conditions/advanced_planetary_conditions_runtime.py`,
    `signal_factory.py` et le champ `NatalResult.advanced_planetary_conditions`
    comme orchestration runtime pure, sans scoring, interpretation, API, DB,
    JSON builder, frontend ou logique detaillee dans `natal_calculation.py`.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du runtime;
  - test d'integration `NatalResult`;
  - tests CS-209 a CS-213 maintenus;
  - scans imports interdits, scoring, interpretation, JSON builder, API, DB,
    frontend et logique detaillee dans `natal_calculation.py`;
  - diff des surfaces adjacentes obligatoire;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau runtime;
  - nouveau signal factory lorsque requis par le scope;
  - exports publics;
  - champ optionnel `NatalResult.advanced_planetary_conditions`;
  - branchement minimal dans `calculate_natal_chart`;
  - nouveaux tests;
  - evidence de validation et ajout de `RG-141`.

## 7. Acceptance Criteria

Evidence variables used below:

- `$runtime` =
  `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `$runtime_tests` =
  `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
- `$natal_tests` =
  `backend/tests/unit/domain/astrology/natal/test_natal_result_conditions_integration.py`
- `$new_modules` =
  `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  and `backend/app/domain/astrology/planetary_conditions/signal_factory.py`
- `$adjacent_diff_check` =
  commande de diff des surfaces adjacentes listee dans le Validation Plan.

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le fichier runtime existe. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC2 | La fonction publique est importable. | Evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC3 | La fonction retourne le contrat global. | Evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC4 | La proximite solaire est integree. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC5 | La relation solaire est integree. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC6 | Mouvement avec vitesse. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC7 | Mouvement absent tolere. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC8 | Visibilite integree. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC9 | Phase lunaire globale. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC10 | Bundle Soleil present. | Evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC11 | Bundle Lune present. | Evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC12 | Signaux techniques produits. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC13 | Signaux agreges globalement. | Evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC14 | Conditions partielles tolerees. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`. |
| AC15 | `NatalResult` expose le champ optionnel. | Evidence: `pytest -q backend/tests/unit/domain/astrology/natal/test_natal_result_conditions_integration.py`. |
| AC16 | `calculate_natal_chart` renseigne le bloc. | Evidence: `pytest -q backend/tests/unit/domain/astrology/natal/test_natal_result_conditions_integration.py`. |
| AC17 | `natal_calculation.py` ne contient pas de logique metier detaillee. | Evidence: `rg -n $natal_detail_logic backend/app/domain/astrology/natal_calculation.py`. |
| AC18 | Les nouveaux modules n'introduisent pas de scoring. | Evidence: `rg -n $forbidden_scoring $new_modules`; zero hit attendu. |
| AC19 | Les nouveaux modules n'introduisent pas d'interpretation ou LLM. | Evidence: `rg -n $forbidden_interpretation $new_modules`; zero hit attendu. |
| AC20 | Imports interdits absents. | Evidence: `rg -n $forbidden_deps $new_modules`; zero hit attendu. |
| AC21 | Surfaces adjacentes inchangees. | Manual check: executer `$adjacent_diff_check`; expected diff vide et verify surfaces adjacentes inchangees. |
| AC22 | `RG-141` est present dans le registre de guardrails. | Evidence: `rg -n "RG-141" _condamad/stories/regression-guardrails.md`. |
| AC23 | La qualite backend passe dans le venv. | Evidence: `ruff format .`; `ruff check .`; `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC2, AC15, AC17, AC18, AC19, AC20, AC21, AC22)
  - [ ] Subtask 1.1 - Inspecter `contracts.py`, `__init__.py`, les cinq
    calculateurs CS-209 a CS-213, `natal_calculation.py`, les tests
    `planetary_conditions`, les tests natal existants, CS-208 a CS-213 et
    `regression-guardrails.md`.
  - [ ] Subtask 1.2 - Verifier l'absence preexistante de
    `advanced_planetary_conditions_runtime.py`,
    `signal_factory.py` et des tests cibles.
  - [ ] Subtask 1.3 - Documenter dans l'evidence l'etat attendu de `RG-135` a
    `RG-141`.

- [ ] Task 2 - Creer la factory de signaux techniques (AC: AC12, AC13, AC18, AC19, AC20)
  - [ ] Subtask 2.1 - Creer `signal_factory.py` ou reutiliser un helper
    canonique equivalent si decouvert dans le meme package.
  - [ ] Subtask 2.2 - Implementer
    `build_planetary_condition_signals(*, bundle: PlanetaryConditionsBundle) ->
    tuple[PlanetaryConditionSignal]`.
  - [ ] Subtask 2.3 - Mapper uniquement les signaux techniques minimaux
    attendus depuis les contrats existants.
  - [ ] Subtask 2.4 - Ne pas ajouter de poids, score, signification,
    interpretation ou texte produit.

- [ ] Task 3 - Creer l'orchestrateur runtime pur (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC18, AC19, AC20)
  - [ ] Subtask 3.1 - Creer `advanced_planetary_conditions_runtime.py`.
  - [ ] Subtask 3.2 - Extraire `planet_longitudes_deg` depuis
    `planetary_positions` sans recalcul astronomique.
  - [ ] Subtask 3.3 - Identifier `sun_longitude_deg` et `moon_longitude_deg`
    depuis les positions fournies.
  - [ ] Subtask 3.4 - Appeler `calculate_solar_proximity_conditions`.
  - [ ] Subtask 3.5 - Appeler `calculate_planetary_motion_conditions`
    uniquement avec les vitesses disponibles et profils existants.
  - [ ] Subtask 3.6 - Appeler `calculate_solar_phase_relations`.
  - [ ] Subtask 3.7 - Appeler `calculate_planet_visibility_conditions` quand
    proximite et relation solaire sont disponibles.
  - [ ] Subtask 3.8 - Appeler `calculate_moon_phase_condition` quand Soleil et
    Lune sont disponibles.
  - [ ] Subtask 3.9 - Implementer `_build_planetary_condition_bundle`.
  - [ ] Subtask 3.10 - Implementer `_build_global_signals`.
  - [ ] Subtask 3.10a - Produire les signaux globaux `waxing_moon` et
    `waning_moon` depuis `moon_phase` quand la phase lunaire est disponible.
  - [ ] Subtask 3.11 - Exporter la fonction publique depuis `__init__.py`.

- [ ] Task 4 - Integrer dans le runtime natal (AC: AC15, AC16, AC17, AC21)
  - [ ] Subtask 4.1 - Importer uniquement l'orchestrateur public dans
    `natal_calculation.py`.
  - [ ] Subtask 4.2 - Ajouter
    `advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None =
    None` a `NatalResult`.
  - [ ] Subtask 4.3 - Construire le mapping des positions et vitesses depuis
    `positions` deja calculees.
  - [ ] Subtask 4.4 - Appeler `calculate_advanced_planetary_conditions` dans
    le pipeline natal apres construction de `positions` et avant le retour
    `NatalResult`, sans condition business detaillee.
  - [ ] Subtask 4.5 - Passer le resultat a `NatalResult`.

- [ ] Task 5 - Ajouter les tests unitaires (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16)
  - [ ] Subtask 5.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`.
  - [ ] Subtask 5.2 - Tester resultat global, bundles par planete, Soleil,
    Lune, phase lunaire, signaux, aggregation globale et conditions partielles.
  - [ ] Subtask 5.3 - Ajouter un test d'integration natal dans la racine de
    tests canonique existante pour prouver que `NatalResult` expose le bloc.
  - [ ] Subtask 5.4 - Maintenir les tests existants CS-209 a CS-213.

- [ ] Task 6 - Ajouter et prouver les gardes anti-drift (AC: AC17, AC18, AC19, AC20, AC21, AC22)
  - [ ] Subtask 6.1 - Ajouter ou verifier `RG-141` dans
    `_condamad/stories/regression-guardrails.md`.
  - [ ] Subtask 6.2 - Executer les scans imports interdits, scoring,
    interpretation, logique detaillee dans `natal_calculation.py` et diff des
    surfaces adjacentes.
  - [ ] Subtask 6.3 - Documenter les resultats dans l'evidence.

- [ ] Task 7 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21, AC22, AC23)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer les tests cibles.
  - [ ] Subtask 7.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 7.4 - Documenter les resultats dans `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AdvancedPlanetaryConditionsResult`, `PlanetaryConditionsBundle` et
    `PlanetaryConditionSignal` depuis `contracts.py`;
  - `calculate_solar_proximity_conditions`;
  - `calculate_planetary_motion_conditions`;
  - `DEFAULT_PLANETARY_MOTION_PROFILES`;
  - `calculate_solar_phase_relations`;
  - `calculate_planet_visibility_conditions`;
  - `calculate_moon_phase_condition`;
  - `PlanetPosition` ou un protocole local minimal uniquement si l'import direct
    cree une boucle;
  - conventions des calculateurs purs existants et des tests pytest
    `planetary_conditions`.
- Do not recreate:
  - contrats CS-208 sous un autre nom ou dans un autre package;
  - calculateurs unitaires CS-209 a CS-213;
  - moteur d'ephemerides, calcul de positions ou calcul de vitesses;
  - moteur de dignites accidentelles;
  - moteur de scoring, dominance ou interpretation;
  - schemas API/Pydantic dedies aux memes concepts;
  - projection JSON publique des conditions avancees.
- Shared abstraction allowed only if:
  - elle reste dans `planetary_conditions`;
  - elle supprime une duplication reelle dans la construction des bundles ou
    signaux;
  - elle n'expose pas de second contrat public concurrent.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- scoring
- dignity scoring
- interpretation textuelle
- narration
- prompts ou LLM
- API schemas
- migrations, seeders, repositories, DB models
- JSON public specifique
- frontend rendering
- heliacal rising/setting reel
- calcul astronomique des positions ou vitesses

Specific forbidden symbols / paths:

- `score`
- `score_delta`
- `dignity_score`
- `accidental_score_delta`
- `essential_score_delta`
- `strength_modifier`
- `interpretation`
- `meaning`
- `description`
- `narrative`
- `prompt`
- `LLM`
- `OpenAI`
- `AIEngineAdapter`
- `FastAPI`
- `SQLAlchemy`
- `Session`
- `repository`
- `json_builder`
- `frontend`
- `from app.api`
- `from app.infra`
- `from app.infrastructure`
- `from app.services`
- `sqlalchemy`
- `fastapi`
- `pydantic` dans les nouveaux modules `planetary_conditions`

Specific forbidden production modifications unless explicitly justified by the
scope:

- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
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
| Contrats des conditions avancees | `planetary_conditions/contracts.py` | `natal_calculation.py`, API schema, frontend |
| Calculateurs unitaires | `planetary_conditions/*_calculator.py` | runtime natal, services chart |
| Orchestration globale des conditions avancees | `planetary_conditions/advanced_planetary_conditions_runtime.py` | `advanced_conditions`, dignities, API, services |
| Signaux techniques de conditions avancees | `planetary_conditions/signal_factory.py` | scoring, interpretation, frontend |
| Injection dans le theme natal | `natal_calculation.py` | services chart, API, DB |
| Projection publique future | future story | CS-214 ne modifie pas `json_builder.py` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is intentionally affected by CS-214.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is intentionally affected. If an existing OpenAPI
  snapshot changes because `NatalResult` is directly serialized elsewhere, the
  dev agent must stop and record the blocker rather than expanding CS-214.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md`
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  - nouveau runtime pur d'orchestration.
- `backend/app/domain/astrology/planetary_conditions/signal_factory.py` -
  nouveau helper de signaux si aucun helper canonique equivalent n'existe.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exporter
  l'orchestrateur et la factory si publique.
- `backend/app/domain/astrology/natal_calculation.py` - ajouter le champ
  optionnel `NatalResult.advanced_planetary_conditions` et le branchement
  minimal dans `calculate_natal_chart`.
- `_condamad/stories/regression-guardrails.md` - ajouter ou verifier
  l'invariant `RG-141`.
- `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
  - couverture comportementale du runtime.
- `backend/tests/unit/domain/astrology/natal/test_natal_result_conditions_integration.py`
  - couverture d'integration `NatalResult`, si cette racine est conforme a la
  topologie existante.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - a maintenir et etendre seulement si l'export public ou le champ optionnel
  exige une couverture contractuelle.

Files not expected to change:

- `backend/app/domain/astrology/dignities/**` - aucune dignite ou scoring ne
  change.
- `backend/app/domain/astrology/advanced_conditions/**` - aucun moteur avance
  existant ne change.
- `backend/app/domain/astrology/condition/**` - aucun profil/signal existant ne
  change.
- `backend/app/domain/astrology/dominance/**` - aucune dominance ne change.
- `backend/app/domain/astrology/interpretation_adapters/**` - aucune
  interpretation ne change.
- `backend/app/services/chart/json_builder.py` - pas de projection JSON.
- `backend/app/api/**` - aucune route/schema.
- `backend/app/infra/**` - aucune persistence.
- `backend/migrations/**` - aucune migration.
- `frontend/src/**` - aucun frontend.

## 19a. Follow-up Story

- Next planned story: `CS-215 - Integrate Advanced Planetary Conditions Into
  Accidental Dignities`
- Expected scope: connecter combustion, retrogradation, stationnarite,
  visibilite et relation oriental/occidental au systeme de dignites
  accidentelles.
- Boundary: CS-214 ne modifie aucune dignite, aucun score et aucun usage
  interpretatif.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: la bibliotheque standard, Pydantic deja present dans
  `natal_calculation.py` et les contrats/calculateurs CS-208 a CS-213 suffisent.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
$runtime_tests = "backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py"
$natal_tests = "backend/tests/unit/domain/astrology/natal/test_natal_result_conditions_integration.py"
pytest -q $runtime_tests
pytest -q $natal_tests
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py
```

Quality checks:

```powershell
ruff format .
ruff check .
pytest -q
```

Required scans:

```powershell
$runtime = "backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py"
$signals = "backend/app/domain/astrology/planetary_conditions/signal_factory.py"
$new_modules = @($runtime, $signals) | Where-Object { Test-Path $_ }
$planetary_condition_paths = "backend/app/domain/astrology/planetary_conditions", "backend/tests/unit/domain/astrology/planetary_conditions"
$public_symbols = "calculate_advanced_planetary_conditions|AdvancedPlanetaryConditionsResult|advanced_planetary_conditions|build_planetary_condition_signals"
$forbidden_deps = "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|FastAPI|SQLAlchemy|Session|repository"
$forbidden_scoring = "\\bscore\\b|score_delta|dignity_score|accidental_score_delta|essential_score_delta|strength_modifier"
$forbidden_interpretation = "interpretation|meaning|description|narrative|prompt|LLM|OpenAI|AIEngineAdapter"
$natal_detail_logic = "combust|under_beams|retrograde|stationary|emerging|oriental|occidental|waxing_moon|waning_moon"
rg -n $forbidden_deps $new_modules
rg -n $forbidden_scoring $new_modules
rg -n $forbidden_interpretation $new_modules
rg -n "json_builder|frontend" $new_modules
rg -n $public_symbols $planetary_condition_paths
rg -n $public_symbols backend/app/domain/astrology/natal_calculation.py backend/tests -g "*.py"
rg -n $natal_detail_logic backend/app/domain/astrology/natal_calculation.py
Select-String "RG-141" _condamad/stories/regression-guardrails.md
git diff -- `
  backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/condition `
  backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters `
  backend/app/services/chart/json_builder.py `
  backend/app/api backend/app/infra backend/migrations frontend/src
```

Expected scan result:

- imports interdits dans les nouveaux modules: zero hits;
- scoring: zero hits;
- interpretation/narration/prompt/LLM: zero hits;
- `json_builder`/`frontend` dans les nouveaux modules: zero hits;
- symbols publics: hits limites aux nouveaux modules, exports, runtime natal et
  tests;
- logique detaillee dans `natal_calculation.py`: zero hit nouveau lie a CS-214
  hors noms de champ/imports autorises; tout hit preexistant doit etre classe
  dans `evidence/validation.md`;
- diff des surfaces adjacentes: vide.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le runtime natal commence a coder les regles conditionnelles directement
  au lieu de deleguer a `planetary_conditions`.
  - Guardrail: AC17, ownership routing, scans de logique detaillee et `RG-141`.
- Risk: les vitesses absentes provoquent une exception globale et cassent le
  theme natal.
  - Guardrail: AC7 et AC14.
- Risk: les signaux deviennent du scoring ou de l'interpretation avant CS-215.
  - Guardrail: AC18, AC19, non-goals et `RG-141`.
- Risk: l'ajout du champ `NatalResult` modifie indirectement une projection
  publique ou un schema API.
  - Guardrail: AC21, generated contract blocker et diff adjacent obligatoire.
- Risk: les calculateurs CS-209 a CS-213 sont dupliques dans l'orchestrateur.
  - Guardrail: mandatory reuse, AC4 a AC9 et scans de surface.

## 23. Dev Agent Instructions

- Implement only CS-214.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, unresolved marker or hidden residual work.
- Keep `advanced_planetary_conditions_runtime.py` pure and deterministic.
- Keep detailed condition rules outside `natal_calculation.py`.
- Reuse all existing calculators CS-209 to CS-213.
- Include Sun and Moon bundles.
- Keep `motion=None` acceptable when a speed is missing.
- Do not change JSON public output.
- Do not change frontend.
- Do not change DB, migrations or seeds.
- Do not add scoring, dignities integration, interpretation, prompts, LLM, API
  schemas, Pydantic models in `planetary_conditions`, repositories, heliacal
  rising/setting reel, horizon, altitude, weather, magnitude, latitude,
  topocentric or ephemeris logic.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task marker or hidden residual in-domain work.

## 24. References

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - contrats
  CS-208 reutilises.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exports
  publics du package.
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - calculateur de proximite solaire CS-209.
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  - calculateur de mouvement CS-210.
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`
  - profils de mouvement a reutiliser.
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  - calculateur de relation solaire CS-211.
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  - calculateur de phase lunaire CS-212.
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
  - calculateur de visibilite CS-213.
- `backend/app/domain/astrology/natal_calculation.py` - owner reel de
  `PlanetPosition`, `NatalResult` et `calculate_natal_chart`.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - precedent proximite solaire.
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
  - precedent mouvement planetaire.
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
  - precedent relation solaire.
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md` - precedent
  phase lunaire.
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
  - precedent visibilite et follow-up explicite CS-214.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-107`, `RG-119`, `RG-122`, `RG-128`, `RG-129`, `RG-135`, `RG-136`,
  `RG-137`, `RG-138`, `RG-139`, `RG-140` et nouvel invariant `RG-141`.
