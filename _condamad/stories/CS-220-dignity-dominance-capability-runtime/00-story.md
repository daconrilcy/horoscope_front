# Story CS-220 dignity-dominance-capability-runtime: Migrer dignites et dominance vers le runtime chart objects

Status: ready-to-dev

## 1. Objective

Faire converger les dignites astrologiques et la dominance vers la surface
runtime `NatalResult.chart_objects`: les candidats sont selectionnes par
`capabilities.supports_dignities` et `capabilities.supports_dominance`, les
calculateurs existants restent proprietaires des scores, puis les resultats sont
projetes dans `payloads.dignity` et `payloads.dominance`. La story preserve les
sorties historiques `dignities`, `dominant_planets`, `condition_profiles`,
`advanced_conditions`, `planet_positions`, aspects et JSON public.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: brief utilisateur du 2026-05-22 pour `CS-220 - Dignity &
  Dominance Capability Runtime`.
- Reason for change: CS-217 a introduit `ChartObjectRuntimeData`, CS-218 a
  migre la consommation aspects par `supports_aspects`, et CS-219 a rattache
  mouvement/visibilite aux payloads. Les dignites et la dominance restent
  encore calculees depuis des collections specialisees et ne sont pas projetes
  dans `chart_objects`.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: le brief demande une migration de surface runtime,
  pas une reforme doctrinale. Les AC couvrent payloads, selectors, projectors,
  enrichers immuables, orchestration en plusieurs passes, preservation des
  resultats historiques, stabilite des scores, absence d'interpretation et
  guardrails anti-branches `object_type`.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`
- In scope:
  - stabiliser un payload runtime de dignite calculatoire;
  - ajouter un payload runtime de contribution a la dominance;
  - ajouter `ChartObjectPayloads.dominance`;
  - etendre ou assouplir la validation capacites/payloads pour permettre une
    construction multi-passes puis valider strictement les phases dignity,
    dominance et final;
  - creer des selectors purs `DignityChartObjectSelector` et
    `DominanceChartObjectSelector` selectionnant par capacite;
  - definir la semantique de `supports_dignities` comme eligibilite a une
    evaluation de dignite astrologique, pas comme categorie planete/luminaire;
  - definir la semantique de `supports_dominance` comme candidature au calcul
    de dominance, pas comme preuve que l'objet est dominant;
  - creer des projectors centralises depuis `ChartObjectRuntimeData` vers les
    entrees des calculateurs existants;
  - creer des projectors de resultats depuis `PlanetDignityResult` et
    `PlanetDominanceResult` vers les payloads runtime;
  - creer des enrichers immuables qui retournent de nouveaux
    `ChartObjectRuntimeData`;
  - adapter l'orchestrateur natal pour calculer dignites et dominance depuis
    `chart_objects` enrichis, en plusieurs passes;
  - conserver `NatalResult.dignities`, `NatalResult.dominant_planets`,
    `condition_profiles`, `condition_signals`, `advanced_conditions`,
    `traditional_conditions`, `planet_positions`, `houses`, `aspects` et
    `chart_objects`;
  - ajouter tests unitaires, integration natal, non-regression golden,
    architecture guard et evidence finale.
- Out of scope:
  - changer les tables ou regles de domicile, exaltation, triplicite, terme,
    face, detriment, chute, secte, hayz ou rejoicing;
  - changer les poids, scores, rangs, tie-breaks ou doctrines de dominance;
  - remplacer `dominant_planets` par un payload objet;
  - marquer angles, cuspides, maisons ou etoiles fixes
    `supports_dignities=True` sans doctrine explicite deja supportee;
  - marquer maisons ou cuspides `supports_dominance=True` par defaut;
  - supprimer ou renommer les sorties historiques;
  - exposer volontairement ces payloads dans l'API publique, OpenAPI, JSON
    public, frontend, DB, migrations, seeders ou repositories;
  - ajouter une couche interpretative, prompts, narration ou texte utilisateur.
- Explicit non-goals:
  - ne pas modifier volontairement les calculateurs purs CS-209 a CS-214;
  - ne pas modifier volontairement les tables ou catalogues de reference des
    dignites et dominantes;
  - ne pas modifier volontairement `backend/app/services/chart/json_builder.py`,
    `backend/app/api/**`, `backend/app/infra/**`, `backend/migrations/**` ou
    `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas affaiblir les invariants `RG-135` a `RG-146`;
  - ne pas introduire de shim, alias, fallback silencieux ou second moteur de
    dignite/dominance.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story modifie la surface runtime interne
  `chart_objects` tout en preservant les contrats historiques et les resultats
  de calcul existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: les objets eligibles exposent `payloads.dignity` et
    `payloads.dominance` apres les phases de calcul correspondantes;
  - autorise: l'orchestrateur natal utilise selectors/projectors depuis
    `chart_objects` avant d'appeler les calculateurs existants;
  - autorise: les validations deviennent phase-aware ou methodes dediees pour
    eviter le cycle de construction;
  - interdit: changer les scores, rangs, breakdowns, doctrine astrologique,
    JSON public ou collections historiques.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la migration exige de changer une doctrine, un
  score attendu, le contrat JSON public, une migration DB ou la suppression
  d'une sortie historique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `chart_objects`, `capabilities` et `payloads` deviennent la surface cible de consommation interne. |
| Baseline Snapshot | yes | Les resultats historiques de dignite et dominance doivent etre compares avant/apres. |
| Ownership Routing | yes | Contrats runtime, selectors, projectors, enrichers et calculateurs existants ont des owners distincts. |
| Allowlist Exception | yes | Aucune exception shim/fallback/branche `object_type` n'est autorisee. |
| Contract Shape | yes | La forme des payloads dignity/dominance est le coeur de la story. |
| Batch Migration | no | La migration porte sur un seul flux natal dignity/dominance. |
| Reintroduction Guard | yes | Des guards doivent bloquer le retour de l'eligibilite par type ou collection historique. |
| Persistent Evidence | yes | Baseline, scans, tests et preuve finale doivent etre conserves dans le dossier CS-220. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects`;
  - `ChartObjectCapabilities.supports_dignities`;
  - `ChartObjectCapabilities.supports_dominance`;
  - `ChartObjectPayloads.dignity`;
  - `ChartObjectPayloads.dominance`;
  - les selectors/projectors/enrichers crees par CS-220.
- Runtime/domain artifacts:
  - AST guard: `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - tests unitaires des selectors, projectors et enrichers;
  - tests d'erreurs explicites pour donnees minimales absentes, payload manquant
    apres enrichment, payload sans capacite et code de payload inconnu;
  - tests d'integration du resultat natal prouvant les payloads presents;
  - tests golden dignites et dominance existants avant/apres;
  - extensions dediees a dignity/dominance dans le guard AST.
- Secondary evidence:
  - scans `rg` anti-branches `object_type`, anti-`planet_positions` dans les
    nouveaux projectors/consommateurs, anti-texte interpretatif;
  - `ruff check .`, `ruff format .` et `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni que `NatalResult.chart_objects` est enrichi apres calcul,
    ni que `dignities` et `dominant_planets` gardent les memes scores.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/chart_object_runtime_builder.py`;
  - `Get-Content backend/app/domain/astrology/dignities/contracts.py`;
  - `Get-Content backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`;
  - `Get-Content backend/app/domain/astrology/dominance/contracts.py`;
  - `Get-Content backend/app/domain/astrology/dominance/planet_dominance_engine.py`;
  - `Select-String` dans `natal_calculation.py` sur `PlanetDignityScoringService`,
    `PlanetDominanceEngine`, `chart_objects`, `dominant_planets` et `dignities`;
  - `pytest -q` sur `test_planet_dignity_scoring_service.py`,
    `test_planet_dominance_engine.py` et `test_traditional_golden_cases.py`;
  - `Select-String "RG-144|RG-145|RG-146" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes tests cibles;
  - nouveaux tests unitaires/integration CS-220;
  - `pytest -q`;
  - scans anti-regression listes dans le Validation Plan;
  - evidence persistante `_condamad/stories/CS-220-dignity-dominance-capability-runtime/evidence/validation.md`.
- Expected invariant:
  - les scores et rangs historiques restent stables;
  - les nouvelles consommations passent par `chart_objects` et capacites;
  - `dominant_planets` reste un resultat chart-level;
  - les payloads restent calculatoires.
- Allowed differences:
  - payloads runtime nouveaux ou stabilises;
  - selectors/projectors/enrichers nouveaux;
  - validation phase-aware ou methodes dediees;
  - branchement natal multi-passes;
  - tests, guardrails, evidence et ajout de `RG-147`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats payloads chart-object | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` ou module runtime voisin | `natal_calculation.py`, API schema, frontend |
| Selection des objets dignity-capable | module runtime/dignities dedie, par capacite | builder specialise par planete, branche `object_type` |
| Projection `ChartObjectRuntimeData -> PlanetDignityInput` | projector unique dignity runtime | `natal_calculation.py`, calculateur essential/accidental |
| Projection `PlanetDignityResult -> DignityRuntimePayload` | projector unique dignity runtime | enricher, API, frontend |
| Enrichissement immuable dignity | enricher runtime/dignities dedie | mutation en place, calculateur |
| Selection/projection dominance | module runtime/dominance dedie, par capacite | `PlanetDominanceEngine` avec logique `object_type` |
| Classement chart-level dominance | `backend/app/domain/astrology/dominance/planet_dominance_engine.py` | payload objet, runtime builder |
| Orchestration natal multi-passes | `backend/app/domain/astrology/natal_calculation.py` | API, services chart, frontend |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-220. | Politique permanente sans exception. |

Validation rule:

- Toute exception pour eligibilite par `object_type`, recalcul de score dans un
  payload/enricher, fallback vers `planet_positions` dans un nouveau
  consommateur ou texte interpretatif doit bloquer l'implementation.

## 4f. Contract Shape

- Contract type:
  - dataclasses immuables `frozen=True, slots=True`;
  - tuples pour breakdowns/factors;
  - strings de codes/sources, pas de texte narratif;
  - projectors purs et deterministes.
- Fields:
  - `DignityRuntimePayload`;
  - `DominanceRuntimePayload`;
  - `ChartObjectPayloads.dignity`;
  - `ChartObjectPayloads.dominance`.
- Required fields:
  - dignity: `essential_score: float`, `accidental_score: float`,
    `total_score: float` et `source: str`;
  - dominance: `contribution_score: float` et `source: str`.
- Optional fields:
  - `functional_strength_score: float | None`;
  - `expression_quality_score: float | None`;
  - `intensity_score: float | None`;
  - `essential_breakdown: tuple of DignityBreakdownItem`;
  - `accidental_breakdown: tuple of DignityBreakdownItem`;
  - `condition_codes: tuple of str`;
  - `rank: int | None`;
  - `contribution_breakdown: tuple of DominanceBreakdownItem`;
  - `factors: tuple of str`.
- Projection rules:
  - les champs de score sont copies depuis `PlanetDignityResult` ou
    `PlanetDominanceResult`;
  - aucun payload projector ou enricher ne reconstruit `total_score`,
    `essential_score`, `accidental_score` ou la contribution de dominance par
    addition locale.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - `NatalResult.chart_objects` reste exclu du schema public par
    `SkipJsonSchema` sauf decision explicite future;
  - aucun nouveau champ OpenAPI ou frontend n'est attendu.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; no OpenAPI, generated client, schema public or migration changes are
    allowed.
- Compatibility decision:
  - `PlanetDignityResult` et `DominantPlanetsResult` restent les sorties
    historiques;
  - `DignityRuntimePayload` doit etre une projection stable, pas un wrapper
    direct obligatoire autour de `PlanetDignityResult`, sauf blocker technique
    documente et approuve.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-220 migre un flux natal unique. La story peut organiser les
  travaux en passes techniques, mais ne migre pas plusieurs domaines ou clients.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, ruff/pytest et preuve finale CS-220. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher le retour de l'eligibilite dignity/dominance par `object_type`;
  - empecher les nouveaux consumers dignity/dominance de lire directement
    `planet_positions`;
  - empecher la duplication ou le recalcul des scores dans payload projectors et
    enrichers;
  - empecher les textes interpretatifs dans les payloads runtime.
- Forbidden examples:
  - `if obj.object_type == ChartObjectType.PLANET` dans dignities/dominance;
  - `if object_type == "planet"`;
  - `if code in TRADITIONAL_PLANETS` comme critere d'eligibilite;
  - `if planet_name == "mars"` ou tout branchement nominal equivalent;
  - `ChartObjectType.LUMINARY` comme critere d'eligibilite;
  - `PlanetDignityPayloadBuilder`, `MarsDominancePayloadBuilder` ou builder par
    objet;
  - `total_score = essential_score + accidental_score` dans un payload projector
    au lieu de copier le resultat du calculateur;
  - `interpretation`, `narrative`, `prompt`, `llm`, `meaning`,
    `psychological` dans les payloads runtime.
- Required guard evidence:
  - test AST ou scan cible borne a `backend/app/domain/astrology/dignities`,
    `backend/app/domain/astrology/dominance` et nouveaux modules runtime;
  - scans `rg` listes dans le Validation Plan;
  - tests de validation capacites/payloads.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

Le codebase actuel indique:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-219` est la derniere
  story numerotee et `CS-220` est le prochain numero disponible.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-144`, `RG-145` et `RG-146` protegent deja
  `chart_objects`, la consommation aspects et les payloads motion/visibility.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `ChartObjectCapabilities` contient deja `supports_dignities` et
  `supports_dominance`; `ChartObjectPayloads` contient un placeholder
  `dignity` mais pas `dominance`.
- Evidence 4: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `_validate_required_payloads` valide `supports_dignities` contre
  `payloads.dignity`, mais ne valide pas `supports_dominance`.
- Evidence 5: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  - les planetes/luminaires et angles peuvent etre marques
  `supports_dominance=True` sans payload dominance, ce qui confirme le besoin
  d'une validation multi-passes.
- Evidence 6: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  - les planetes ne declarent pas encore `supports_dignities=True`; les tests
  existants attendent `dignity_codes == set()`.
- Evidence 7: `backend/app/domain/astrology/dignities/contracts.py` -
  `PlanetDignityResult` porte deja `essential_score`, `accidental_score`,
  `total_score`, scores d'axes, breakdowns et condition de secte.
- Evidence 8: `backend/app/domain/astrology/dominance/contracts.py` -
  `PlanetDominanceResult` porte `total_score`, `rank`, `dominance_level`,
  `factors` et `explanation_facts`, et `DominantPlanetsResult` reste le
  classement chart-level.
- Evidence 9: `backend/app/domain/astrology/natal_calculation.py` -
  l'orchestrateur construit deja `chart_objects` avant les aspects, mais cree
  encore `dignity_inputs` depuis `positions` et appelle
  `PlanetDominanceEngine().calculate` avec `planet_positions=positions`.
- Evidence 10: `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`,
  `test_planet_dominance_engine.py`, `test_dominance_integration.py` et
  `test_traditional_golden_cases.py` couvrent deja les resultats historiques.
- Evidence 11: source-alignment review - une story qui ajoute les payloads mais
  laisse les nouveaux consommateurs retourner vers `planet_positions` ne
  satisfait pas le brief CS-220.

## 6. Target State

After implementation:

- `ChartObjectPayloads` porte des payloads dignity et dominance calculatoires.
- Les objets dignity-capable sont selectionnes uniquement via
  `supports_dignities`.
- Les objets dominance-capable sont selectionnes uniquement via
  `supports_dominance`.
- `supports_dignities` signifie que l'objet peut recevoir une evaluation de
  dignite astrologique; angles, cuspides, maisons et etoiles fixes restent
  exclus par defaut sans doctrine explicite.
- `supports_dominance` signifie que l'objet peut contribuer au calcul de
  dominance; le payload objet porte une contribution et ne remplace pas le
  classement global.
- Les entrées des calculateurs historiques sont produites par projectors
  centralises depuis `chart_objects`.
- Les resultats historiques sont projetes dans les payloads runtime sans
  recalcul de score.
- `chart_objects` est enrichi immuablement apres dignites, puis apres dominance.
- `NatalResult.dignities` et `NatalResult.dominant_planets` restent disponibles
  et stables.
- La dominance objet porte une contribution; le classement final reste
  chart-level.
- Les payloads ne contiennent aucun texte interpretatif ou prompt.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-135` - les contrats purs de conditions planetaires restent separes des
    calculs de dignite/dominance.
  - `RG-141` - l'orchestration des conditions planetaires avancees ne doit pas
    etre recodee dans CS-220.
  - `RG-142` - les modificateurs accidentels issus des conditions avancees ne
    doivent pas etre recalcules ou contournes.
  - `RG-144` - `ChartObjectRuntimeData` reste le contrat canonique et les
    collections historiques restent exposees.
  - `RG-145` - le moteur d'aspects reste sur `supports_aspects` et ne doit pas
    etre regresse par le nouveau flux.
  - `RG-146` - motion/visibility restent des payloads types mappes depuis les
    conditions existantes.
- Non-applicable invariants:
  - `RG-001` a `RG-134` et les invariants `RG-136` a `RG-140`, `RG-143` hors
    surfaces astrology runtime/dignities/dominance - la story ne touche pas
    routes API, frontend, prediction, prompts, DB, migrations ou autres
    domaines non astrologiques.
- Required regression evidence:
  - tests cibles CS-217 a CS-219;
  - tests dignity/dominance existants;
  - nouveaux tests CS-220;
  - scans anti-`object_type`, anti-`planet_positions` et anti-interpretation;
  - evidence persistante `evidence/validation.md`.
- Allowed differences:
  - ajout de payloads, selectors, projectors, enrichers, validation phase-aware,
    tests, branchement natal multi-passes et `RG-147`.

## 7. Acceptance Criteria

Sauf mention contraire, les commandes de test ci-dessous ciblent les fichiers
sous `backend/tests/unit/domain/astrology/`.

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `DignityRuntimePayload` expose une projection calculatoire stable. | Evidence: `pytest -q test_chart_object_dignity_runtime.py`. |
| AC2 | `DominanceRuntimePayload` porte une contribution objet sans remplacer `DominantPlanetsResult`. | Evidence: `pytest -q test_chart_object_dominance_runtime.py`. |
| AC3 | `ChartObjectPayloads` expose les payloads CS-220 avec validation par phase. | Evidence: `pytest -q test_chart_object_runtime_builder.py`. |
| AC4 | `DignityChartObjectSelector` selectionne par `supports_dignities=True`. | Evidence: `pytest -q test_chart_object_dignity_runtime.py -k selector`. |
| AC5 | `DominanceChartObjectSelector` selectionne par `supports_dominance=True`. | Evidence: `pytest -q test_chart_object_dominance_runtime.py -k selector`. |
| AC6 | Les projectors d'entree dignity consomment `ChartObjectRuntimeData` sans `object_type`. | Evidence: `pytest -q test_chart_object_dignity_runtime.py -k input_projector`. |
| AC7 | Les projectors de resultats dignity ne recalculent pas les scores. | Evidence: `pytest -q test_chart_object_dignity_runtime.py -k payload_projector`. |
| AC8 | Les enrichers dignity retournent de nouvelles instances. | Evidence: `pytest -q test_chart_object_dignity_runtime.py -k enricher`. |
| AC9 | L'orchestrateur natal execute le flux multi-passes CS-220. | Evidence: `pytest -q test_natal_result_chart_objects.py`. |
| AC10 | Les sorties historiques restent disponibles avec les nouveaux payloads chart-object. | Evidence: `pytest -q test_natal_result_contract.py`. |
| AC11 | Les golden cases de dignite/dominance restent stables. | Evidence: `pytest -q test_traditional_golden_cases.py`. |
| AC12 | Les nouveaux consommateurs runtime ne retournent pas vers `planet_positions`. | Evidence: `pytest -q test_chart_object_runtime_architecture.py`. |
| AC13 | Aucun payload runtime dignity ne contient de texte narratif. | Evidence: `pytest -q test_chart_object_dignity_runtime.py -k narrative`. |
| AC14 | Les objets non concernes ne recoivent pas de payload incoherent. | Evidence: `pytest -q test_chart_object_runtime_builder.py`. |
| AC15 | Le guardrail bloque l'eligibilite par `object_type`. | Evidence: `pytest -q test_chart_object_runtime_architecture.py`. |
| AC16 | L'evidence finale CS-220 est persistee. | Evidence: `rg -n "CS-220 Final Evidence" evidence/validation.md`. |
| AC17 | Les entrees dominance viennent de `ChartObjectRuntimeData` sans `object_type`. | Evidence: `pytest -q test_chart_object_dominance_runtime.py -k input_projector`. |
| AC18 | Les projectors de resultats dominance ne recalculent pas les scores. | Evidence: `pytest -q test_chart_object_dominance_runtime.py -k payload_projector`. |
| AC19 | Les enrichers dominance retournent de nouvelles instances. | Evidence: `pytest -q test_chart_object_dominance_runtime.py -k enricher`. |
| AC20 | Aucun payload runtime dominance ne contient de texte narratif. | Evidence: `pytest -q test_chart_object_dominance_runtime.py -k narrative`. |
| AC21 | Un objet dignity-capable sans donnees minimales produit une erreur explicite. | Evidence: `pytest -q test_chart_object_dignity_runtime.py -k invalid`. |
| AC22 | Un payload dignity/dominance sans capacite ou cible inconnue produit une erreur. | Evidence: `pytest -q test_chart_object_runtime_builder.py -k payload`. |
| AC23 | Les objets sans doctrine explicite ne deviennent pas dignifiables par defaut. | Evidence: `pytest -q test_chart_object_runtime_builder.py -k dignity`. |
| AC24 | Le guardrail bloque l'eligibilite par code nominal ou liste traditionnelle. | Evidence: `pytest -q test_chart_object_runtime_architecture.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les owners existants (AC: AC10, AC11, AC16)
  - [ ] Subtask 1.1 - Executer les commandes de baseline listees en section 4c.
  - [ ] Subtask 1.2 - Creer `evidence/validation.md` et y consigner baseline, scans initiaux et hypotheses.

- [ ] Task 2 - Stabiliser les contrats runtime payloads et validation (AC: AC1, AC2, AC3, AC13, AC20, AC22)
  - [ ] Subtask 2.1 - Remplacer ou faire evoluer `ChartObjectDignityPayload` vers un payload calculatoire stable.
  - [ ] Subtask 2.2 - Ajouter `DominanceRuntimePayload` et `ChartObjectPayloads.dominance`.
  - [ ] Subtask 2.3 - Introduire validation phase-aware ou methodes dediees `validate_*_payloads` sans bloquer la construction de base.
  - [ ] Subtask 2.4 - Ajouter tests de forme, erreurs et absence de texte interpretatif.

- [ ] Task 3 - Creer selectors et projectors dignity (AC: AC4, AC6, AC7, AC12, AC15, AC21, AC23, AC24)
  - [ ] Subtask 3.1 - Ajouter `DignityChartObjectSelector` avec controles code, longitude, zodiac position et maison si requise.
  - [ ] Subtask 3.2 - Ajouter `DignityInputProjector` vers `PlanetDignityInput` ou contrat existant.
  - [ ] Subtask 3.3 - Ajouter `DignityPayloadProjector` depuis `PlanetDignityResult` sans recalcul.
  - [ ] Subtask 3.4 - Tester selection, projection et erreurs explicites.

- [ ] Task 4 - Creer selector, projectors et payload enrichment dominance (AC: AC5, AC17, AC18, AC19, AC12, AC15)
  - [ ] Subtask 4.1 - Ajouter `DominanceChartObjectSelector` par capacite et donnees necessaires.
  - [ ] Subtask 4.2 - Ajouter un projector d'entree vers le contrat attendu par `PlanetDominanceEngine` ou adapter ce moteur sans changer ses scores.
  - [ ] Subtask 4.3 - Ajouter `DominancePayloadProjector` depuis `PlanetDominanceResult`.
  - [ ] Subtask 4.4 - Ajouter `DominancePayloadEnricher` immuable et tests associes.

- [ ] Task 5 - Ajouter l'enrichment dignity immuable (AC: AC8, AC14)
  - [ ] Subtask 5.1 - Ajouter `DignityPayloadEnricher` refusant codes inconnus, doublons, payload manquant et payload sans capacite.
  - [ ] Subtask 5.2 - Verifier la preservation de motion, visibility, house_position, angle et autres payloads.

- [ ] Task 6 - Adapter l'orchestrateur natal multi-passes (AC: AC9, AC10, AC11)
  - [ ] Subtask 6.1 - Construire les `chart_objects` de base sans cycle.
  - [ ] Subtask 6.2 - Selectionner/projecter les objets dignity-capable, appeler `PlanetDignityScoringService`, puis enrichir `chart_objects`.
  - [ ] Subtask 6.3 - Recalculer les dependances historiques dans l'ordre existant sans changer leur contrat.
  - [ ] Subtask 6.4 - Selectionner/projecter les objets dominance-capable, appeler `PlanetDominanceEngine`, puis enrichir `chart_objects`.
  - [ ] Subtask 6.5 - Renseigner `NatalResult` avec les collections historiques et `chart_objects` enrichis.

- [ ] Task 7 - Ajouter guards, tests integration et evidence finale (AC: AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC21, AC22, AC23, AC24)
  - [ ] Subtask 7.1 - Ajouter tests integration `NatalResult.chart_objects` dignity/dominance.
  - [ ] Subtask 7.2 - Etendre `test_chart_object_runtime_architecture.py` ou ajouter un guard dedie.
  - [ ] Subtask 7.3 - Executer validation complete et consigner la section `CS-220 Final Evidence`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetDignityScoringService` pour les scores de dignite;
  - `PlanetDignityResult` comme source historique de projection;
  - `PlanetDominanceEngine` pour le classement chart-level;
  - `DominantPlanetsResult` et `PlanetDominanceResult` comme source historique
    de projection dominance;
  - `ChartObjectRuntimeData`, `ChartObjectCapabilities` et
    `ChartObjectPayloads` comme surface runtime canonique;
  - `ChartObjectMotionPayload` et `ChartObjectVisibilityPayload` existants sans
    duplicer leurs faits.
- Do not recreate:
  - un second moteur de dignite essentielle ou accidentelle;
  - un second moteur de dominance;
  - des builders specialises par planete, angle, luminaire ou objet;
  - un DTO runtime wrapper qui expose tout `PlanetDignityResult` si une
    projection explicite suffit;
  - une interpretation textuelle des scores.
- Shared abstraction allowed only if:
  - elle centralise une responsabilite repetee entre selectors/projectors/enrichers;
  - elle reste dans le domaine astrology runtime/dignities/dominance;
  - elle est couverte par tests et ne devient pas un service fourre-tout.

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

- `if obj.object_type == ChartObjectType.PLANET` dans dignity/dominance consumers;
- `if object_type == "planet"`;
- `if object_type == "luminary"`;
- `if code in TRADITIONAL_PLANETS`;
- `if planet_name == "mars"` ou equivalent nominal;
- `ChartObjectType.PLANET` ou `ChartObjectType.LUMINARY` comme critere
  d'eligibilite dans selectors/projectors;
- `PlanetDignityPayloadBuilder`;
- `MoonDignityPayloadBuilder`;
- `MarsDominancePayloadBuilder`;
- recalcul de `total_score`, `accidental_score`, `essential_score` ou
  `dominance_score` dans un payload projector/enricher;
- payload contenant `interpretation`, `narrative`, `prompt`, `llm`, `meaning`,
  `psychological`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Objet runtime du theme | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | DTO API, frontend, wrappers historiques |
| Projection collections historiques vers chart objects | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | calculateurs metier |
| Calcul des dignites | `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` et calculateurs existants | payload projectors, enrichers |
| Calcul de dominance chart-level | `backend/app/domain/astrology/dominance/planet_dominance_engine.py` | payload objet |
| Orchestration du theme natal | `backend/app/domain/astrology/natal_calculation.py` | API, services chart, frontend |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Internal Usage Search

- Required before implementation:
  - rechercher les consommateurs actuels de `PlanetDignityScoringService`,
    `PlanetDominanceEngine`, `NatalResult.dignities`,
    `NatalResult.dominant_planets`, `ChartObjectPayloads.dignity`,
    `supports_dignities` et `supports_dominance`;
  - identifier quels usages doivent rester historiques et lesquels doivent
    passer par selectors/projectors `chart_objects`.
- Required after implementation:
  - prouver dans `evidence/validation.md` que les nouveaux consommateurs
    dignity/dominance passent par `ChartObjectRuntimeData` et que les
    calculateurs historiques restent les owners des scores.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: `chart_objects` reste exclu du schema public; aucune route, OpenAPI,
  migration DB, client genere ou schema frontend ne doit changer.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/calculators/aspect_inputs.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dominance/contracts.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - payloads
  dignity/dominance et validation phase-aware ou methodes dediees.
- `backend/app/domain/astrology/dignities/chart_object_inputs.py` ou module
  equivalent - selector/projector/enricher dignity.
- `backend/app/domain/astrology/dominance/chart_object_inputs.py` ou module
  equivalent - selector/projector/enricher dominance.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration multi-passes.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` -
  declaration initiale des capacites applicables sans payload final, si la
  validation phase-aware l'exige.
- `_condamad/stories/regression-guardrails.md` - ajout `RG-147`.
- `_condamad/stories/CS-220-dignity-dominance-capability-runtime/evidence/validation.md`
  - preuve finale.

Likely tests:

- `backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py` -
  contrats, selector, projector, enricher dignity.
- `backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py` -
  contrats, selector, projector, enricher dominance.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` -
  capacites et payloads applicables.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` -
  integration `NatalResult.chart_objects`.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
  - guards anti-drift.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
  et `test_planet_dominance_engine.py` - non-regression.
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` -
  golden dignity/dominance.

Files not expected to change:

- `backend/app/domain/astrology/planetary_conditions/*_calculator.py` - CS-220
  consomme leurs resultats indirectement, sans recalculer.
- `backend/app/services/chart/json_builder.py` - aucun changement JSON public.
- `backend/app/api/**` - aucun endpoint modifie.
- `backend/app/infra/**` et `backend/migrations/**` - aucune persistance ou DB.
- `frontend/src/**` - `chart_objects` reste interne backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Python commands must be run after activating `.venv` from repository root:
  `.\.venv\Scripts\Activate.ps1`.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
Pop-Location
pytest -q
pytest -q backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py `
  backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py `
  backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py `
  backend/tests/unit/domain/astrology/test_planet_dominance_engine.py `
  backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/dignities
pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py
rg "object_type ==|\\.object_type ==|ChartObjectType\\.PLANET|ChartObjectType\\.LUMINARY" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance
rg "TRADITIONAL_PLANETS|planet_name ==|code in" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance
rg "planet_positions" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance
rg "PlanetDignityPayloadBuilder|MoonDignityPayloadBuilder|MarsDominancePayloadBuilder|AngleDominancePayloadBuilder" backend/app backend/tests
rg "interpretation|narrative|prompt|llm|meaning|psychological" backend/app/domain/astrology/runtime backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance
```

Expected scan results:

- `object_type` scan: zero hit in new consumers/projectors/enrichers, except
  explicitly documented compatibility builders if unavoidable and not used for
  eligibility.
- `TRADITIONAL_PLANETS` / nominal-code scan: zero hit comme critere
  d'eligibilite; les references historiques restent seulement documentees si
  elles appartiennent aux tables doctrinales existantes.
- `planet_positions` scan: zero hit in new projectors/consumers; existing
  historical calculator signatures may remain only if routed through the
  central projectors and documented in evidence.
- anti-interpretation scan: zero hit in payload runtime modules, or hits only in
  pre-existing interpretation modules outside the payload path and documented.

## 22. Regression Risks

- Risk: cycle de construction entre `ChartObjectRuntimeBuilder` et les
  calculateurs de dignite.
  - Guardrail: validation par phases et enrichers immuables, test integration du
    flux multi-passes.
- Risk: changement involontaire des scores de dignite ou rangs de dominance.
  - Guardrail: tests golden avant/apres et comparaison des payloads projetes
    aux resultats historiques.
- Risk: confusion entre contribution objet et dominance chart-level.
  - Guardrail: `DominanceRuntimePayload` ne remplace pas `DominantPlanetsResult`
    et les tests verifient les deux surfaces.
- Risk: retour de branches par type ou builders specialises.
  - Guardrail: test AST et scans `object_type`/builders interdits.
- Risk: introduction de texte interpretatif dans les payloads.
  - Guardrail: scan anti-interpretation et tests de forme payload.

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
  unresolved implementation note, or hidden residual in-domain work when this story is marked
  `full-closure`.
- Keep comments and docstrings in French for new or significantly modified
  Python files.
- Use the venv for every Python command.

## 24. References

- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`
  - socle `ChartObjectRuntimeData`.
- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
  - precedent selector/projector par capacite.
- `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md`
  - precedent payloads et validation capacites/payloads.
- `_condamad/stories/regression-guardrails.md` - invariants RG-135 a RG-146
  consultes et nouveau RG-147 attendu.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - contrat
  runtime a enrichir.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration natal a
  migrer en plusieurs passes.
