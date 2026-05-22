# Story CS-219 chart-object-motion-visibility-payloads: Rattacher mouvement et visibilite aux chart objects

Status: done

## 1. Objective

Enrichir `ChartObjectRuntimeData` pour que les objets du theme exposent les
faits de mouvement apparent et de visibilite planetaire via
`payloads.motion` et `payloads.visibility`, pilotes par
`capabilities.supports_motion` et `capabilities.supports_visibility`. La story
doit mapper les conditions deja calculees par CS-209 a CS-214 vers le contrat
runtime unifie, sans recreer les calculateurs de retrogradation, station,
cazimi, combustion, under beams, relation oriental/occidental ou visibilite.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: brief utilisateur du 2026-05-22 pour `CS-219 - Chart Object Motion & Visibility Payloads`.
- Reason for change: CS-217 a cree `NatalResult.chart_objects` et CS-218 a
  migre les aspects vers `capabilities.supports_aspects`, mais les faits de
  mouvement et visibilite restent disperses entre `planet_positions`,
  `advanced_planetary_conditions` et des payloads chart-object minimaux.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: le brief demande une normalisation runtime, pas un
  nouveau moteur doctrinal. Les AC couvrent contrats types, builders purs,
  validation capacites/payloads, branchement au builder chart-object,
  compatibilite des sorties historiques, absence de seuils magiques et
  guardrails anti-duplication.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`
- In scope:
  - stabiliser `ChartObjectPayloads.motion` et `ChartObjectPayloads.visibility`;
  - creer ou renommer des payloads types motion/visibility selon les conventions
    existantes;
  - ajouter les enums runtime necessaires ou mapper explicitement les enums
    `planetary_conditions` existantes;
  - creer des builders purs qui mappent depuis `PlanetaryMotionCondition`,
    `SolarProximityCondition`, `PlanetarySolarPhaseRelation` et
    `PlanetVisibilityCondition`;
  - brancher ces builders dans `build_chart_object_runtime_data`;
  - valider strictement capacite vraie avec payload present, et payload absent
    quand la capacite est fausse;
  - alimenter les planetes/luminaires applicables dans `NatalResult.chart_objects`;
  - statuer explicitement sur les points astraux calcules, dont noeuds et
    Lilith: motion seulement si une donnee existante fiable est disponible,
    visibility absente par defaut sauf doctrine existante;
  - garder angles, cuspides, maisons, etoiles fixes et objets non applicables
    sans payload motion/visibility;
  - conserver `planet_positions`, `advanced_planetary_conditions`,
    `advanced_conditions`, aspects, dignites, profils et signaux;
  - ajouter tests unitaires, integration natal, guardrails et evidence finale.
- Out of scope:
  - refonte des dignites, dominance, interpretation, scoring ou narration;
  - changement des seuils astrologiques CS-209 a CS-214;
  - nouveau calcul astronomique, ephemeride ou vitesse;
  - suppression de champs ou collections historiques;
  - exposition JSON publique, API, OpenAPI, frontend, DB, migrations, seeders
    ou repositories.
- Explicit non-goals:
  - ne pas modifier volontairement les calculateurs purs
    `solar_proximity_calculator.py`, `planetary_motion_calculator.py`,
    `solar_phase_relation_calculator.py`, `planetary_visibility_calculator.py`
    ou `moon_phase_calculator.py`;
  - ne pas modifier volontairement `backend/app/domain/astrology/dignities/**`,
    `dominance/**`, `interpretation/**`, `backend/app/services/chart/json_builder.py`,
    `backend/app/api/**`, `backend/app/infra/**`, `backend/migrations/**` ou
    `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas affaiblir les invariants `RG-135` a `RG-146`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story enrichit un contrat runtime interne existant tout
  en preservant les collections historiques et les calculateurs canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: `chart_objects` expose des payloads motion/visibility types pour
    les objets applicables;
  - autorise: le builder recoit une source de conditions avancees deja calculee
    pour mapper les payloads;
  - interdit: changer les regles de calcul, seuils, scores, projection publique
    ou collections historiques.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: les payloads ne peuvent pas etre alimentes sans
  recalculer les conditions CS-209 a CS-214, changer la projection publique ou
  supprimer une sortie historique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `payloads.motion` et `payloads.visibility` deviennent la surface runtime cible. |
| Baseline Snapshot | yes | Les collections et calculateurs existants doivent etre preserves. |
| Ownership Routing | yes | Les contrats vivent dans `runtime`, les mappings dans `builders`, les calculs dans `planetary_conditions`. |
| Allowlist Exception | yes | Aucune exception shim/fallback/duplication n'est autorisee. |
| Contract Shape | yes | La forme des payloads et enums est le coeur de la story. |
| Batch Migration | no | Aucun lot multi-consommateurs n'est migre. |
| Reintroduction Guard | yes | Les guards bloquent recalculs concurrents, seuils magiques et branches `object_type`. |
| Persistent Evidence | yes | Les preuves finales doivent etre conservees dans le dossier CS-219. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `ChartObjectRuntimeData.payloads.motion`;
  - `ChartObjectRuntimeData.payloads.visibility`;
  - `ChartObjectCapabilities.supports_motion`;
  - `ChartObjectCapabilities.supports_visibility`;
  - `NatalResult.chart_objects`.
- Runtime artifacts:
  - tests unitaires des payload builders;
  - tests unitaires du validateur capacites/payloads;
  - tests d'integration `build_natal_result`;
  - guard AST `test_chart_object_runtime_architecture.py`;
  - runtime schema `app.openapi()` via les tests d'exclusion schema public.
- Secondary evidence:
  - scans `rg` anti-duplication et anti-seuils magiques;
  - tests CS-209 a CS-214 maintenus;
  - `ruff check .` et `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas que `NatalResult.chart_objects` contient les payloads
    attendus ni que les anciennes sorties restent presentes.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/chart_object_runtime_builder.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `rg -n "ChartObjectMotionPayload|ChartObjectVisibilityPayload|supports_motion|supports_visibility" backend/app/domain/astrology backend/tests -g "*.py"`;
  - `rg -n "retrograde|stationary|combust|cazimi|under_beams|oriental|occidental|visibility" backend/app/domain/astrology -g "*.py"`;
  - `Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140|RG-141|RG-144|RG-145|RG-146" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes scans apres implementation;
  - tests cibles du Validation Plan;
  - diff adjacent sur `planetary_conditions` calculateurs, `dignities`,
    `dominance`, `interpretation`, `json_builder.py`, API, infra, migrations et
    frontend.
- Expected invariant:
  - les conditions avancees restent calculees par CS-209 a CS-214;
  - `build_chart_object_runtime_data` rattache les payloads au contrat unifie;
  - les sorties historiques restent disponibles.
- Allowed differences:
  - payloads runtime enrichis, builders purs, validateur, branchement minimal,
    tests, evidence et `RG-146`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats chart-object runtime | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | API schema, frontend type, `natal_calculation.py` |
| Calcul des conditions motion/visibility | `backend/app/domain/astrology/planetary_conditions/*_calculator.py` | `chart_object_runtime_builder.py`, dignities, interpretation |
| Mapping conditions vers payloads | `backend/app/domain/astrology/builders` ou `runtime` | calculateurs CS-209 a CS-214, API, services chart |
| Validation capacites/payloads | runtime chart-object ou validateur dedie | consommateurs metier |
| Branchement natal | `backend/app/domain/astrology/natal_calculation.py` | API, DB, frontend |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-219. | Politique permanente sans exception. |

Validation rule:

- Toute exception pour seuil magique local, recalcul de combustion/retrograde,
  payload sans capacite ou capacite sans payload doit bloquer l'implementation.

## 4f. Contract Shape

- Contract type:
  - dataclasses immuables `frozen=True, slots=True`;
  - enums `StrEnum`;
  - builders purs et deterministes;
  - validateur explicite levant une erreur coherente avec les conventions
    existantes.
- Fields:
  - `MotionRuntimePayload` ou remplacement canonique de `ChartObjectMotionPayload`;
  - `VisibilityRuntimePayload` ou remplacement canonique de `ChartObjectVisibilityPayload`;
  - `ChartObjectPayloads.motion`;
  - `ChartObjectPayloads.visibility`.
- Required fields:
  - motion: vitesse longitudinale ou condition de mouvement deja calculee,
    etat de mouvement, booleens `is_direct`, `is_retrograde`, `is_stationary`
    et `source`;
  - visibility: separation solaire quand disponible, phase/proximite solaire,
    flags cazimi/combust/under beams non applicables a `None`, relation
    oriental/occidental quand disponible, `is_visible` prudent et `source`.
- Optional fields:
  - latitude speed, distance speed, speed condition, station phase;
  - `solar_separation_deg`, `solar_phase`, flags solaires, relation
    oriental/occidental et `is_visible` quand le moteur ne porte pas le fait.
- Planetary conditions payload:
  - `payloads.motion` et `payloads.visibility` sont les surfaces principales;
  - `payloads.planetary_conditions` ne doit pas dupliquer les memes faits, sauf
    facade deja existante et documentee.
- Status codes:
  - aucun endpoint HTTP, methode ou status code n'est modifie.
- Serialization names:
  - `chart_objects` reste un champ interne exclu du schema public existant;
  - aucune nouvelle cle JSON publique n'est autorisee.
- Frontend type impact:
  - aucun type frontend ne change volontairement.
- Generated contract impact:
  - aucun OpenAPI, client genere, schema public ou migration n'est modifie.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-219 enrichit `chart_objects` sans deplacer la source canonique des
  conditions avancees ni migrer d'autre consommateur.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, ruff/pytest et preuve finale demandee par le brief. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher la duplication des calculs motion/visibility hors CS-209 a CS-214;
  - empecher les payloads incoherents avec les capacites;
  - empecher les seuils magiques locaux dans le builder chart-object;
  - empecher les consommateurs de piloter motion/visibility par `object_type`.
- Forbidden examples:
  - `if abs(speed) < 0.01`;
  - `if solar_distance < 8.5`;
  - nouveau calcul local `combust`, `cazimi`, `under_beams`, `retrograde` ou
    `stationary` dans `chart_object_runtime_builder.py`;
  - `supports_motion=False` avec `payloads.motion` non nul;
  - `supports_visibility=False` avec `payloads.visibility` non nul;
  - `if obj.object_type == ChartObjectType.PLANET` dans les consommateurs.
- Required guard evidence:
  - test de validateur, test AST, scans `rg` bornes et `RG-146`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

Le codebase actuel indique:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-219` est enregistree
  comme story `ready-to-dev` apres CS-218.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-135` a `RG-146` protegent les conditions
  planetaires, `chart_objects`, les aspects et les payloads motion/visibility.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `ChartObjectPayloads.motion` et `.visibility` existent deja, mais les
  payloads sont minimaux.
- Evidence 4: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  - le builder alimente seulement un payload motion minimal depuis
  `PlanetPosition`, sans payload visibility.
- Evidence 5: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - les contrats `PlanetaryMotionCondition`, `SolarProximityCondition`,
  `PlanetarySolarPhaseRelation`, `PlanetVisibilityCondition` et
  `MoonPhaseCondition` existent deja.
- Evidence 6: `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  - l'orchestrateur calcule deja les bundles par planete depuis positions et
  vitesses existantes.
- Evidence 7: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` expose deja `advanced_planetary_conditions` et `chart_objects`
  comme champs internes exclus du schema public.
- Evidence 8: source-alignment review - le brief demande que les nouveaux
  consommateurs lisent `capabilities -> payloads` et que les anciennes sorties
  restent presentes.

## 6. Target State

Apres implementation:

- les payloads motion et visibility sont des contrats types explicites;
- les planetes/luminaires applicables portent les capacites et payloads
  correspondants;
- les noeuds, Lilith et futurs points calcules ne portent motion/visibility que
  si une source existante fiable permet de declarer la capacite;
- le Soleil est traite comme non applicable pour cazimi/combust/under beams sur
  lui-meme, avec convention testee;
- la phase lunaire est seulement raccordee si un contrat runtime existe deja;
  aucun payload complet de phase lunaire n'est cree dans CS-219;
- angles, cuspides et objets non applicables ne portent pas ces payloads;
- le validateur refuse capacite sans payload et payload sans capacite;
- le builder mappe les conditions existantes sans recalcul local ni seuil
  magique;
- les collections historiques restent disponibles;
- l'evidence finale inclut la preuve courte demandee par le brief.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-135` - les contrats `planetary_conditions` restent purs.
  - `RG-136` a `RG-140` - CS-219 mappe les resultats existants sans les
    recalculer ni changer leurs seuils.
  - `RG-141` - l'orchestrateur natal des conditions avancees reste la source
    des bundles motion/visibility.
  - `RG-144` - `ChartObjectRuntimeData` et son builder restent les owners du
    contrat runtime unifie.
  - `RG-145` - le moteur d'aspects reste borne a `supports_aspects`.
  - `RG-146` - invariant CS-219 a verifier et maintenir pour les payloads
    motion/visibility.
- Non-applicable invariants:
  - `RG-142` et `RG-143` - CS-219 ne touche pas le scoring accidentel ni les
    profils interpretatifs.
- Required regression evidence:
  - tests unitaires payload builders et validateur;
  - tests d'integration `NatalResult.chart_objects`;
  - tests CS-209 a CS-214 maintenus;
  - scans anti-recalcul, anti-seuils magiques et anti-`object_type`.
- Allowed differences:
  - enrichment interne de `chart_objects` uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le contrat motion expose un payload type immuable sans dictionnaire libre. | `pytest -q` test payloads; commande exacte dans le Validation Plan. |
| AC2 | Le contrat visibility expose un payload type avec `is_visible` prudent. | `pytest -q` test payloads; commande exacte dans le Validation Plan. |
| AC3 | Le mapping motion reutilise `PlanetaryMotionCondition` ou les vitesses existantes. | `pytest -q` test payloads + scans seuils du Validation Plan. |
| AC4 | Le mapping visibility reutilise les contrats solaires existants sans recalcul local. | `pytest -q` test payloads + scans recalculs du Validation Plan. |
| AC5 | `supports_motion=True` exige `payloads.motion` non nul. | Tests payloads + `test_chart_object_runtime_builder.py`. |
| AC6 | `supports_visibility=True` exige `payloads.visibility` non nul. | Tests payloads + `test_chart_object_runtime_builder.py`. |
| AC7 | Un payload motion ou visibility present avec capacite false est invalide. | `pytest -q` test payloads; commande exacte dans le Validation Plan. |
| AC8 | Les planetes/luminaires applicables exposent les payloads attendus. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`. |
| AC9 | Les objets sans source fiable restent sans motion/visibility. | `test_natal_result_chart_objects.py`; couvre angles, cuspides, maisons, etoiles fixes et points. |
| AC10 | Les sorties historiques restent stables. | Tests `test_natal_result_conditions_integration.py` + chart objects. |
| AC11 | Le schema public reste stable. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`; `app.openapi()`. |
| AC12 | Aucun consommateur ne pilote motion/visibility par `object_type`. | `pytest -q` test architecture; commande exacte dans le Validation Plan. |
| AC13 | Aucun seuil magique local lie aux conditions solaires ou motion n'est introduit. | Scans `rg` exacts du Validation Plan. |
| AC14 | `RG-146` est enregistre. | `rg -n "RG-146" _condamad/stories/regression-guardrails.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les sources canoniques (AC: AC3, AC4, AC10, AC11, AC13)
  - [ ] Subtask 1.1 - Inspecter les contrats/runtime/builders et l'orchestrateur conditions.
  - [ ] Subtask 1.2 - Capturer les scans initiaux motion/visibility/seuils.
  - [ ] Subtask 1.3 - Documenter le baseline dans `evidence/validation.md`.

- [ ] Task 2 - Stabiliser les contrats runtime motion/visibility (AC: AC1, AC2, AC5, AC6, AC7)
  - [ ] Subtask 2.1 - Ajouter ou renommer les payloads types selon les conventions existantes.
  - [ ] Subtask 2.2 - Ajouter les enums necessaires ou mapper les enums existantes.
  - [ ] Subtask 2.3 - Ajouter un validateur explicite capacites/payloads.

- [ ] Task 3 - Creer les builders purs de payloads (AC: AC3, AC4, AC13)
  - [ ] Subtask 3.1 - Mapper motion depuis `PlanetaryMotionCondition` ou vitesses existantes.
  - [ ] Subtask 3.2 - Mapper visibility depuis `PlanetaryConditionsBundle`.
  - [ ] Subtask 3.3 - Traiter le Soleil comme non applicable pour cazimi/combust/under beams.
  - [ ] Subtask 3.4 - Raccorder la phase lunaire uniquement si un contrat runtime existe deja.
  - [ ] Subtask 3.5 - Refuser les approximations silencieuses si la source manque.

- [ ] Task 4 - Brancher le mapping dans `build_chart_object_runtime_data` (AC: AC8, AC9, AC10, AC11)
  - [ ] Subtask 4.1 - Faire accepter au builder la source `AdvancedPlanetaryConditionsResult`.
  - [ ] Subtask 4.2 - Alimenter motion et visibility pour les objets applicables.
  - [ ] Subtask 4.3 - Garder angles, cuspides, maisons, etoiles fixes et points sans source fiable sans payload.
  - [ ] Subtask 4.4 - Adapter `natal_calculation.py` sans deplacer les calculateurs.

- [ ] Task 5 - Ajouter les tests comportementaux (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
  - [ ] Subtask 5.1 - Tester direct, retrograde et stationary.
  - [ ] Subtask 5.2 - Tester cazimi, combust, under beams et hors faisceau.
  - [ ] Subtask 5.3 - Tester la convention Soleil non applicable.
  - [ ] Subtask 5.4 - Tester les erreurs de coherence capacites/payloads.

- [ ] Task 6 - Ajouter integration et guardrails (AC: AC8, AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Subtask 6.1 - Etendre les tests `NatalResult.chart_objects`.
  - [ ] Subtask 6.2 - Etendre le guard AST/architecture.
  - [ ] Subtask 6.3 - Verifier que `RG-146` couvre CS-219 et documenter le resultat.
  - [ ] Subtask 6.4 - Produire `evidence/validation.md`.

- [ ] Task 7 - Valider (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer tests cibles, `ruff format .`, `ruff check .` et `pytest -q` depuis `backend`.
  - [ ] Subtask 7.3 - Executer les scans anti-duplication et anti-seuils.
  - [ ] Subtask 7.4 - Reporter la preuve finale courte demandee par le brief.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartObjectRuntimeData`, `ChartObjectPayloads` et `ChartObjectCapabilities`;
  - `AdvancedPlanetaryConditionsResult` et `PlanetaryConditionsBundle`;
  - `PlanetaryMotionCondition`, `SolarProximityCondition`,
    `PlanetarySolarPhaseRelation` et `PlanetVisibilityCondition`;
  - `build_chart_object_runtime_data` comme owner de projection.
- Do not recreate:
  - calcul de retrogradation/station, cazimi/combust/under beams,
    oriental/occidental, visibilite planetaire ou phase lunaire complete;
  - projection publique JSON ou types frontend.
- Applicability:
  - noeuds, Lilith et futurs points calcules peuvent recevoir motion seulement
    si une source existante fiable le permet;
  - visibility reste absente par defaut pour ces points sauf doctrine existante;
  - etoiles fixes, angles, maisons et cuspides restent hors motion/visibility
    dans CS-219.
- Shared abstraction allowed only if:
  - elle remplace une duplication concrete du mapping de payloads;
  - elle reste dans `runtime` ou `builders`;
  - elle ne devient pas un second calculateur de conditions.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- broad allowlist
- `PASS with limitation`

Specific forbidden symbols / paths:

- nouveau calcul local de `cazimi`, `combust`, `under_beams`, `retrograde` ou
  `stationary` dans `chart_object_runtime_builder.py`;
- `if abs(speed) < 0.01`;
- `if solar_distance < 8.5`;
- `if obj.object_type == ChartObjectType.PLANET` dans les consommateurs;
- `payloads.motion` non nul avec `supports_motion=False`;
- `payloads.visibility` non nul avec `supports_visibility=False`;
- modification volontaire de `backend/app/services/chart/json_builder.py`;
- modification volontaire de `frontend/src/**`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Contrat payload motion/visibility | `runtime/chart_object_runtime_data.py` | API, frontend, `natal_calculation.py` |
| Calcul conditionnel motion/visibility | `planetary_conditions/*` | chart-object builder, dignities, interpretation |
| Mapping vers chart objects | `builders` / runtime validator | calculateurs de conditions |
| Validation capacites/payloads | runtime chart-object | consommateurs metier |
| Integration natal | `natal_calculation.py` | services chart, DB, frontend |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Internal Usage Search

- Internal usage search: required
- Reason: CS-219 doit prouver l'absence de calculs concurrents et de branches
  consommateur par `object_type`.
- Required searches:
  - `rg -n "combust|cazimi|under_beams|under beams|retrograde|stationary" backend/app/domain/astrology -g "*.py"`
  - `rg -n "if .*object_type|\.object_type ==" backend/app/domain/astrology -g "*.py"`
  - `rg -n "\b8\.5\b|\b17\b|\b0\.2833\b|\b0\.01\b" backend/app/domain/astrology -g "*.py"`

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is intentionally affected. If OpenAPI or frontend
  contracts change, the dev agent must stop and record the blocker.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`
- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - payloads et validation.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - mapping motion/visibility.
- `backend/app/domain/astrology/builders/chart_object_payload_builders.py` - nouveau module possible pour builders purs.
- `backend/app/domain/astrology/natal_calculation.py` - passage minimal du resultat `advanced_planetary_conditions`.
- `_condamad/stories/regression-guardrails.md` - verification de `RG-146` et documentation du resultat.
- `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/evidence/validation.md` - preuves finales.

Likely tests:

- `backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py` - payload builders, enums et validateur.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` - projections.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` - integration natal.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - guardrails.

Files not expected to change:

- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` - calculateur canonique a preserver.
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py` - calculateur canonique a preserver.
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py` - calculateur canonique a preserver.
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py` - calculateur canonique a preserver.
- `backend/app/domain/astrology/dignities/**`, `dominance/**`, `interpretation/**` - hors scope.
- `backend/app/services/chart/json_builder.py`, API, infra, migrations et frontend - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Toutes les commandes Python doivent etre lancees apres activation du venv.

Depuis la racine du repo pour les tests cibles:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py
```

Depuis `backend` pour la validation globale demandee:

```powershell
Push-Location backend
ruff format .
ruff check .
pytest -q
Pop-Location
```

Scans anti-regression depuis la racine:

```powershell
rg -n "combust|cazimi|under_beams|under beams|retrograde|stationary" backend/app/domain/astrology -g "*.py"
rg -n "if .*object_type|\.object_type ==" backend/app/domain/astrology -g "*.py"
rg -n "\b8\.5\b|\b17\b|\b0\.2833\b|\b0\.01\b" backend/app/domain/astrology -g "*.py"
rg -n "calculate_solar_proximity|calculate_planetary_motion|calculate_solar_phase|calculate_planet_visibility" `
  backend/app/domain/astrology/builders backend/app/domain/astrology/runtime -g "*.py"
rg -n "RG-146" _condamad/stories/regression-guardrails.md
Test-Path _condamad/stories/CS-219-chart-object-motion-visibility-payloads/evidence/validation.md
```

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Resultat attendu:

- les tests cibles passent;
- `ruff format .`, `ruff check .` et `pytest -q` passent depuis `backend`;
- les scans interdits n'ont pas de hit applicatif non documente;
- toute commande sautee est documentee dans `evidence/validation.md`.

## 22. Regression Risks

- Risque: dupliquer les calculs de retrograde, station, combustion ou visibilite.
  - Guardrail: AC3, AC4, AC13 et `RG-146`.
- Risque: declarer une capacite sans payload ou un payload sans capacite.
  - Guardrail: AC5, AC6, AC7 et validateur.
- Risque: surpromettre une visibilite astronomique reelle.
  - Guardrail: AC2 et mapping prudent de `is_visible`.
- Risque: casser les sorties historiques ou la projection publique.
  - Guardrail: AC10, AC11 et baseline avant/apres.

## 23. Dev Agent Instructions

- Implement only CS-219.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Map existing condition outputs into `chart_objects`; do not recreate the
  condition calculators.
- Keep thresholds in existing contracts or named runtime profiles; do not add
  local magic numbers.
- Use capabilities and payloads for consumption, not `object_type` branches.
- Do not remove or rename historical collections or fields.
- Do not change JSON public output, API, DB, migrations or frontend.
- Use French top-of-file comments/docstrings for new or significantly modified
  applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  compatibility, legacy, shim, alias or hidden residual in-domain work.

## 24. References

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - contrat chart-object actuel.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - owner de projection.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration natal.
- `backend/app/domain/astrology/planetary_conditions/contracts.py` - contrats motion/visibility existants.
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py` - source runtime des bundles.
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md` - contrat d'origine.
- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` - precedent de consommation par capacites.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
