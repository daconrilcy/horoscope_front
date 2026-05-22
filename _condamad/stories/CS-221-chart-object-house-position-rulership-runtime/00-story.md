# Story CS-221 chart-object-house-position-rulership-runtime: Rattacher maisons et maitrises au runtime chart objects

Status: done

## 1. Objective

Faire converger la position en maison et les maitrises de maisons vers la
surface runtime `NatalResult.chart_objects`: les objets eligibles exposent une
position en maison enrichie via `payloads.house_position`, et les corps qui
gouvernent des maisons exposent un payload typé `payloads.rulership`. La story
doit reutiliser les maisons, cuspides, rulers et rulerships deja calcules, sans
recalcul doctrinal concurrent, sans interpretation narrative, sans changer le
JSON public, et sans revenir a une selection par `object_type`.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: brief utilisateur du 2026-05-22 pour `CS-221 - Chart Object
  House Position & Rulership Runtime`.
- Reason for change: CS-217 a introduit
  `ChartObjectCapabilities.supports_house_position`, CS-219/CS-220 ont rattache
  d'autres payloads calculatoires aux objets du theme, mais la position en
  maison reste minimale et les maitrises restent dispersees entre `houses`,
  `house_rulers`, `planet_positions`, dominance, dignites accidentelles et
  contexte d'interpretation.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: le brief demande de finir le graphe calculable du
  theme pour les maisons et maitrises, pas d'ajouter une interpretation. Les AC
  couvrent payloads types, modalite de maison, selectors/projectors/enrichers,
  reutilisation de `HouseRulerResolver`, dispositors, rulers ASC/MC, preservation
  des sorties historiques, guardrails anti-`object_type` et maintien des
  etoiles fixes pour une story ulterieure.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`
- In scope:
  - enrichir `ChartObjectHousePositionPayload` avec une modalite de maison
    calculatoire (`angular`, `succedent`, `cadent`) et une source explicite;
  - creer un payload runtime typé `RulershipRuntimePayload`;
  - ajouter `ChartObjectPayloads.rulership`;
  - traiter `ChartObjectHousePositionPayload` comme le payload runtime house
    position existant a enrichir, sans creer un doublon
    `HousePositionRuntimePayload` concurrent;
  - valider `rulership` contre une capacite dediee si le contrat existant doit
    evoluer, ou definir explicitement la regle si la capacite reste derivee de
    `supports_house_position`;
  - mapper les resultats de `HouseRulerResolver` et les `sign_rulerships` deja
    charges depuis `AstrologyRuntimeReference`;
  - permettre a un objet runtime de porter `rules_houses`, `is_house_ruler`,
    `is_ascendant_ruler`, `is_midheaven_ruler` et un `dispositor_code`;
  - garder les cuspides et angles avec leurs payloads existants, sans les
    transformer en planetes ou en rulers;
  - creer des selectors/projectors/enrichers purs bases sur `ChartObjectRuntimeData`
    et les capacites/payloads;
  - brancher l'enrichissement dans l'orchestrateur natal apres calcul des
    maisons/rulers et avant les consommateurs qui lisent `chart_objects`;
  - conserver `NatalResult.house_rulers`, `houses`, `planet_positions`,
    `dignities`, `dominant_planets`, `chart_objects` et les sorties historiques;
  - ajouter tests unitaires, integration natal, garde architecture et evidence.
- Out of scope:
  - changer la doctrine de rulership, domicile, exaltation, triplicite, terme,
    face ou dominance;
  - recalculer les maisons, cuspides, signes ou rulers avec une nouvelle source;
  - modifier les scores de dignite accidentelle, dominance ou interpretation;
  - remplacer `HouseRulerResolver` ou les champs historiques `house_rulers`;
  - exposer volontairement ces payloads dans l'API publique, OpenAPI, JSON
    public, frontend, DB, migrations, seeders ou repositories;
  - ajouter une narration, un texte utilisateur, un prompt ou une couche LLM.
  - traiter les conjonctions d'etoiles fixes ou la future CS-222.
- Explicit non-goals:
  - ne pas modifier volontairement les calculateurs purs CS-209 a CS-214;
  - ne pas modifier volontairement les scores ou poids de `dignities/**` et
    `dominance/**`;
  - ne pas modifier volontairement
    `backend/app/services/chart/json_builder.py`, `backend/app/api/**`,
    `backend/app/infra/**`, `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas affaiblir les invariants `RG-135` a `RG-147`;
  - ne pas introduire de shim, alias, fallback silencieux, allowlist large ou
    second moteur de maitrises.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story enrichit la surface runtime interne
  `chart_objects` tout en preservant les contrats historiques de maisons,
  rulers, dignites, dominance et projection publique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: `chart_objects` expose une position en maison plus riche et un
    payload de rulership pour les objets applicables;
  - autorise: l'orchestrateur natal enrichit `chart_objects` depuis
    `house_rulers` et `sign_rulerships` deja calcules;
  - interdit: changer les calculs de maisons, rulers, scores, classements,
    JSON public, API ou collections historiques.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la migration exige de changer la doctrine de
  rulership, le contrat JSON public, une migration DB, la suppression d'une
  sortie historique ou une compatibilite transitoire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `chart_objects`, `payloads.house_position` et `payloads.rulership` deviennent la surface cible de consommation interne. |
| Baseline Snapshot | yes | Les maisons, house rulers, dignites et dominance historiques doivent etre compares avant/apres. |
| Ownership Routing | yes | Contrats runtime, resolver de rulers, builders/enrichers et orchestrateur natal ont des owners distincts. |
| Allowlist Exception | yes | Aucune exception shim/fallback/branche `object_type` n'est autorisee. |
| Contract Shape | yes | La forme des payloads house/rulership est le coeur de la story. |
| Batch Migration | no | La migration porte sur un flux runtime natal unique, sans lot multi-clients. |
| Reintroduction Guard | yes | Des guards doivent bloquer le retour de maitrises dispersees ou d'eligibilite par type. |
| Persistent Evidence | yes | Baseline, tests, scans et preuve finale doivent etre conserves dans le dossier CS-221. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects`;
  - `ChartObjectPayloads.house_position`;
  - `ChartObjectPayloads.rulership`;
  - `ChartObjectCapabilities.supports_house_position`;
  - les selectors/projectors/enrichers CS-221;
  - `NatalResult.house_rulers` comme sortie historique preservee.
- Runtime/domain artifacts:
  - tests unitaires des payloads house/rulership;
  - tests unitaires des selectors/projectors/enrichers;
  - tests d'integration `NatalResult.chart_objects`;
  - AST guard:
    `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - runtime schema artifact: `app.openapi()` via le test existant de stabilite
    du schema public de `NatalResult`;
  - tests de non-regression dominance/dignites qui dependent des rulers.
- Secondary evidence:
  - scans `rg` anti-branches `object_type`, anti-recalcul des rulers et
    anti-texte interpretatif;
  - `ruff format .`, `ruff check .` et `pytest -q` apres activation du venv.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni que les payloads sont presents dans `NatalResult`, ni que
    les rulers ASC/MC et dispositors sont projetes correctement.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/chart_object_runtime_builder.py`;
  - `Get-Content backend/app/domain/astrology/house_ruler_resolver.py`;
  - `Get-Content backend/app/domain/astrology/runtime/house_runtime_data.py`;
  - `Select-String` dans `natal_calculation.py` sur `house_rulers`,
    `sign_rulerships`, `build_chart_object_runtime_data`, `chart_objects`;
  - `rg -n "house_position|rulership|dispositor|house_rulers|supports_house_position" backend/app/domain/astrology backend/tests/unit/domain/astrology -g "*.py"`;
  - `Select-String "RG-144|RG-145|RG-146|RG-147" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes scans cibles apres implementation;
  - tests CS-221 du Validation Plan;
  - tests `test_chart_object_runtime_builder.py`,
    `test_natal_result_chart_objects.py`, `test_planet_dominance_engine.py`,
    `test_traditional_golden_cases.py`;
  - diff adjacent sur `planetary_conditions`, `dignities`, `dominance`,
    `interpretation`, `json_builder.py`, API, infra, migrations et frontend.
- Expected invariant:
  - les maisons et rulers historiques restent disponibles;
  - les payloads house/rulership sont des projections calculatoires;
  - les consommateurs nouveaux lisent les capacites et payloads, pas
    `object_type`;
  - aucune projection publique volontaire ne change.
- Allowed differences:
  - payload house_position enrichi;
  - payload rulership ajoute;
  - selectors/projectors/enrichers nouveaux;
  - branchement natal minimal;
  - tests, guardrails, evidence et verification ou ajout de `RG-148` si absent.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats payloads chart-object | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` ou module runtime voisin | API schema, frontend, `natal_calculation.py` |
| Calcul historique des rulers de maisons | `backend/app/domain/astrology/house_ruler_resolver.py` | chart-object payload projector, dominance, interpretation |
| Classification angular/succedent/cadent | `backend/app/domain/astrology/runtime/house_runtime_data.py` / catalogue runtime existant | constantes locales dispersees |
| Projection house/rulership vers chart objects | module runtime/builder dedie CS-221 | calculateurs de dignite, dominance, API |
| Orchestration natal | `backend/app/domain/astrology/natal_calculation.py` | services chart, DB, frontend |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-221. | Politique permanente sans exception. |

Validation rule:

- Toute exception pour eligibilite par `object_type`, recalcul local de
  rulership, fallback de sign rulerships, payload sans capacite ou compatibilite
  transitoire doit bloquer l'implementation.

## 4f. Contract Shape

- Contract type:
  - dataclasses immuables `frozen=True, slots=True`;
  - tuples pour les maisons gouvernees et codes de faits;
  - strings de codes/sources, pas de texte narratif;
  - selectors/projectors/enrichers purs et deterministes.
- Fields:
  - `ChartObjectHousePositionPayload`;
  - `RulershipRuntimePayload`;
  - `ChartObjectPayloads.house_position`;
  - `ChartObjectPayloads.rulership`.
- Naming rule:
  - le brief cible un `HousePositionRuntimePayload`; dans le repo courant, la
    surface canonique equivalente est `ChartObjectHousePositionPayload`, qui
    doit etre enrichie au lieu de creer un second payload house position.
- Required fields:
  - house_position: `house_number: int`, `house_modality: str`,
    `source: str`;
  - rulership: `rules_houses: tuple of int`, `is_house_ruler: bool`,
    `is_ascendant_ruler: bool`, `is_midheaven_ruler: bool`, `source: str`.
- Optional fields:
  - house_position: `house_cusp_code: str | None`,
    `house_cusp_longitude: float | None`;
  - rulership: `dispositor_code: str | None`,
    `rules_signs: tuple of str`, `rulership_sources: tuple of str`.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - `NatalResult.chart_objects` reste une surface interne exclue du schema
    public selon la convention existante;
  - aucune nouvelle cle JSON publique n'est autorisee.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; no OpenAPI, generated client, public schema or migration change is
    allowed.
- Example target:

```python
mars.payloads.house_position.house_number == 10
mars.payloads.house_position.house_modality == "angular"
mars.payloads.rulership.rules_houses == (1, 8)
mars.payloads.rulership.dispositor_code == "venus"
```

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-221 enrichit un flux runtime natal unique et ne migre pas plusieurs
  clients ou surfaces publiques.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, ruff/pytest et preuve finale CS-221. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher le retour de maitrises dispersees dans les consommateurs;
  - empecher les branches d'eligibilite par `object_type`;
  - empecher le recalcul local des rulers et modalites de maison;
  - empecher l'ajout de texte interpretatif dans les payloads.
- Forbidden examples:
  - `if obj.object_type == ChartObjectType.PLANET`;
  - `if object_type == "planet"`;
  - `if code in TRADITIONAL_PLANETS` comme critere d'eligibilite;
  - `if planet_name == "mars"` ou equivalent nominal;
  - `HouseRulershipPayloadBuilder`, `MarsRulershipPayloadBuilder` ou builder
    par corps;
  - table locale de rulers zodiacaux concurrente a
    `AstrologyRuntimeReference.dignities.sign_rulerships`;
  - constantes locales `{1, 4, 7, 10}` hors helper/catalogue canonique pour
    classer les maisons;
  - `interpretation`, `narrative`, `prompt`, `llm`, `meaning`,
    `psychological` dans les payloads runtime.
- Required guard evidence:
  - test AST ou scan cible borne aux nouveaux modules et aux consommateurs
    house/rulership;
  - scans `rg` listes dans le Validation Plan;
  - test de validation capacites/payloads.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

Le codebase actuel indique:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-221` est enregistree
  comme story `chart-object-house-position-rulership-runtime` en statut
  `ready-to-dev`.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-144`, `RG-145`, `RG-146`, `RG-147` et `RG-148`
  protegent deja `chart_objects`, aspects, motion/visibility,
  dignity/dominance et house/rulership.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `ChartObjectCapabilities.supports_house_position` existe et valide
  `payloads.house_position`.
- Evidence 4: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `ChartObjectHousePositionPayload` ne porte aujourd'hui que
  `house_number`.
- Evidence 5: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `ChartObjectPayloads` ne contient pas encore de payload `rulership`.
- Evidence 6: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  - les planetes, luminaires, points, angles et cuspides peuvent porter
  `supports_house_position` avec un payload minimal.
- Evidence 7: `backend/app/domain/astrology/house_ruler_resolver.py` -
  `HouseRulerResolver` produit deja `HouseRulerResult` depuis les cuspides et
  `sign_rulerships`.
- Evidence 8: `backend/app/domain/astrology/natal_calculation.py` - le runtime
  extrait `sign_rulerships`, calcule `house_rulers`, puis transmet ces donnees
  a `houses`, `dignities`, `dominance` et `NatalResult`.
- Evidence 9: `backend/app/domain/astrology/runtime/house_runtime_data.py` -
  `resolve_house_kind` classe deja les maisons en `angular`, `succedent` ou
  `cadent`.
- Evidence 10: source-alignment review - une story qui enrichit seulement
  `house_number` sans rattacher les rulers, dispositors, ASC/MC rulers et
  guardrails ne couvre pas le manque logique decrit dans le brief.

## 6. Target State

After implementation:

- `ChartObjectHousePositionPayload` porte `house_number`, `house_modality` et
  une source explicite.
- Les objets avec `supports_house_position=True` portent un payload coherent.
- `ChartObjectPayloads.rulership` expose les maisons gouvernees, flags
  ruler/ASC/MC et dispositor lorsque calculable depuis les donnees existantes.
- Les rulers sont projetes depuis `HouseRulerResult` et les sign rulerships
  canoniques, sans table concurrente.
- Les dispositors sont deduits depuis le signe de l'objet et les rulerships
  canoniques; si le signe manque, le champ reste `None` sans fallback.
- Les cuspides, angles et objets non eligibles ne recoivent pas de payload
  incoherent.
- Les etoiles fixes restent hors scope de CS-221 et doivent etre traitees dans
  une story dediee ulterieure.
- `NatalResult.house_rulers`, `houses`, `planet_positions`, `dignities`,
  `dominant_planets` et `chart_objects` restent disponibles.
- Les futurs consommateurs peuvent lire:
  `if obj.capabilities.supports_house_position: obj.payloads.house_position`.
- Aucun consommateur nouveau ne selectionne par `object_type`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-144` - `ChartObjectRuntimeData` reste le contrat canonique et les
    collections historiques restent exposees.
  - `RG-145` - le moteur d'aspects reste borne a `supports_aspects`; CS-221 ne
    doit pas perturber les candidats d'aspects.
  - `RG-146` - les payloads motion/visibility restent des mappings de
    conditions existantes, non recalcules.
  - `RG-147` - les payloads dignity/dominance restent calculatoires et ne
    doivent pas recalculer ou contourner les rulers.
  - `RG-148` - invariant CS-221 pour position en maison et rulership
    depuis `chart_objects`.
- Non-applicable invariants:
  - `RG-135` a `RG-143` - CS-221 ne modifie pas les contrats de conditions
    planetaires avancees, modificateurs accidentels ou profils symboliques.
- Required regression evidence:
  - tests payloads house/rulership;
  - tests integration `NatalResult.chart_objects`;
  - tests non-regression `HouseRulerResolver`, dominance et golden cases;
  - scans anti-`object_type`, anti-rulers concurrents et anti-interpretation.
- Allowed differences:
  - enrichment interne de `chart_objects` uniquement;
  - verification ou ajout de `RG-148` si absent.

## 7. Acceptance Criteria

Sauf mention contraire, les commandes de test ci-dessous ciblent les fichiers
sous `backend/tests/unit/domain/astrology/`.

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `house_position` expose une forme typée complete. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k house_position`. |
| AC2 | La modalite reutilise le helper canonique. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k modality`; scan `rg`. |
| AC3 | `RulershipRuntimePayload` expose une projection calculatoire stable. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k rulership_payload`. |
| AC4 | `ChartObjectPayloads` expose `rulership` sans dictionnaire libre. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k payload_shape`. |
| AC5 | Les planetes/luminaires qui gouvernent des maisons portent `rules_houses`. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k rules_houses`. |
| AC6 | Les flags rulers angulaires ciblent les maisons attendues. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k angles`. |
| AC7 | `dispositor_code` vient des rulerships canoniques. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k dispositor`. |
| AC8 | Sans signe exploitable, `dispositor_code` reste `None`. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k missing_sign`. |
| AC9 | Les objets non eligibles ne recoivent pas de payload rulership incoherent. | Evidence: `pytest -q test_chart_object_house_position_rulership_runtime.py -k non_eligible`. |
| AC10 | L'orchestrateur natal renseigne `chart_objects` avec house/rulership runtime. | Evidence: `pytest -q test_natal_result_chart_objects.py -k house`. |
| AC11 | Les sorties historiques restent disponibles. | Evidence: `pytest -q test_natal_result_contract.py`. |
| AC12 | Les cas golden lies aux rulers restent stables. | Evidence: `pytest -q test_planet_dominance_engine.py test_traditional_golden_cases.py`. |
| AC13 | Aucun nouveau consommateur ne selectionne house/rulership par `object_type`. | Evidence: `pytest -q test_chart_object_runtime_architecture.py` + scan `rg`. |
| AC14 | Aucun second resolver ou table locale de sign rulerships n'est cree. | Evidence: scan `rg` du Validation Plan. |
| AC15 | Les payloads restent non narratifs. | Evidence: scan `rg` anti-interpretation du Validation Plan. |
| AC16 | Le schema public reste stable. | Evidence: `pytest -q test_natal_result_chart_objects.py -k schema`; `app.openapi()`; `git diff` adjacent. |
| AC17 | L'evidence finale CS-221 est persistee. | Evidence: `rg -n "CS-221 Final Evidence" evidence/validation.md`. |
| AC18 | Le guardrail `RG-148` est enregistre. | Evidence: `rg -n "RG-148" _condamad/stories/regression-guardrails.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les owners existants (AC: AC11, AC12, AC14, AC16, AC18)
  - [ ] Subtask 1.1 - Executer les commandes de baseline listees en section 4c.
  - [ ] Subtask 1.2 - Creer `evidence/validation.md` et y consigner baseline,
    scans initiaux et hypotheses.

- [ ] Task 2 - Stabiliser les contrats runtime house/rulership (AC: AC1, AC3, AC4, AC15)
  - [ ] Subtask 2.1 - Enrichir `ChartObjectHousePositionPayload` sans casser les
    appels existants ou adapter les constructeurs canoniques.
  - [ ] Subtask 2.2 - Ajouter `RulershipRuntimePayload`.
  - [ ] Subtask 2.3 - Ajouter `ChartObjectPayloads.rulership`.
  - [ ] Subtask 2.4 - Ajouter ou adapter la validation capacites/payloads sans
    creer de cycle de construction.

- [ ] Task 3 - Creer les projectors/enrichers house position (AC: AC1, AC2, AC9)
  - [ ] Subtask 3.1 - Mapper `house_number` et `house_modality` depuis les
    maisons/cuspides existantes.
  - [ ] Subtask 3.2 - Reutiliser `resolve_house_kind` ou le catalogue runtime
    existant, sans constantes locales concurrentes.
  - [ ] Subtask 3.3 - Verifier les objets sans maison et les payloads incoherents.

- [ ] Task 4 - Creer les projectors/enrichers rulership (AC: AC3, AC5, AC6, AC7, AC8, AC9, AC14)
  - [ ] Subtask 4.1 - Construire un index depuis `HouseRulerResult` existants.
  - [ ] Subtask 4.2 - Projeter `rules_houses`, `is_house_ruler`,
    `is_ascendant_ruler` et `is_midheaven_ruler`.
  - [ ] Subtask 4.3 - Projeter `dispositor_code` depuis le signe de l'objet et
    `sign_rulerships`.
  - [ ] Subtask 4.4 - Retourner de nouvelles instances
    `ChartObjectRuntimeData` sans mutation en place.

- [ ] Task 5 - Adapter l'orchestrateur natal (AC: AC10, AC11, AC12, AC16)
  - [ ] Subtask 5.1 - Brancher l'enrichissement apres calcul de `house_rulers`
    et construction initiale de `chart_objects`.
  - [ ] Subtask 5.2 - Passer les donnees enrichies aux consommateurs existants
    si leur ordre depend de `chart_objects`.
  - [ ] Subtask 5.3 - Garder `house_rulers`, `houses`, `dignities` et
    `dominant_planets` comme sorties historiques.

- [ ] Task 6 - Ajouter tests et guards (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC18)
  - [ ] Subtask 6.1 - Creer
    `backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py`.
  - [ ] Subtask 6.2 - Etendre `test_natal_result_chart_objects.py`.
  - [ ] Subtask 6.3 - Etendre `test_chart_object_runtime_architecture.py`.
  - [ ] Subtask 6.4 - Verifier `RG-148` dans le registre.

- [ ] Task 7 - Valider et documenter (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer tests cibles, `ruff format .`, `ruff check .`
    et `pytest -q` depuis `backend`.
  - [ ] Subtask 7.3 - Executer les scans anti-regression.
  - [ ] Subtask 7.4 - Consigner la section `CS-221 Final Evidence`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartObjectRuntimeData`, `ChartObjectCapabilities` et
    `ChartObjectPayloads`;
  - `ChartObjectHousePositionPayload` comme surface house existante;
  - `HouseRulerResolver` et `HouseRulerResult`;
  - `AstrologyRuntimeReference.dignities.sign_rulerships`;
  - `resolve_house_kind` ou le catalogue runtime existant pour angular/succedent/cadent;
  - `build_chart_object_runtime_data` comme owner de projection initiale.
- Do not recreate:
  - un second resolver de rulers de maisons;
  - une table locale de sign rulerships;
  - un moteur de dignites ou dominance;
  - des builders specialises par planete, angle, luminaire ou cuspide;
  - une projection JSON publique ou type frontend.
- Shared abstraction allowed only if:
  - elle centralise une responsabilite concrete de projection/enrichment;
  - elle reste dans le domaine astrology runtime/builders;
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
- broad allowlist
- `PASS with limitation`

Specific forbidden symbols / paths:

- `if obj.object_type == ChartObjectType.PLANET` dans house/rulership consumers;
- `if object_type == "planet"`;
- `if object_type == "luminary"`;
- `if code in TRADITIONAL_PLANETS` comme critere d'eligibilite;
- `if planet_name == "mars"` ou equivalent nominal;
- nouvelle table de rulership zodiacal locale;
- nouveau resolver concurrent a `HouseRulerResolver`;
- `HouseRulershipPayloadBuilder`;
- `MarsRulershipPayloadBuilder`;
- payload contenant `interpretation`, `narrative`, `prompt`, `llm`, `meaning`,
  `psychological`;
- modification volontaire de `backend/app/services/chart/json_builder.py`;
- modification volontaire de `frontend/src/**`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Objet runtime du theme | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | DTO API, frontend, wrappers historiques |
| Projection collections historiques vers chart objects | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | calculateurs metier |
| Resolution des rulers de maisons | `backend/app/domain/astrology/house_ruler_resolver.py` | payload projector, dominance, interpretation |
| Classification des maisons | `backend/app/domain/astrology/runtime/house_runtime_data.py` / catalogue runtime | constantes dispersees |
| Orchestration du theme natal | `backend/app/domain/astrology/natal_calculation.py` | API, services chart, frontend |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Internal Usage Search

- Required before implementation:
  - rechercher les consommateurs actuels de `house_rulers`,
    `supports_house_position`, `payloads.house_position`,
    `HouseRulerResolver`, `sign_rulerships`, `chart_ruler_code` et
    `dominant_planets`;
  - identifier quels usages doivent rester historiques et lesquels peuvent lire
    `ChartObjectRuntimeData`.
- Required after implementation:
  - prouver dans `evidence/validation.md` que les nouveaux consommateurs
    house/rulership passent par les payloads runtime, sans resolver concurrent.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: `chart_objects` reste exclu du schema public; aucune route, OpenAPI,
  migration DB, client genere ou schema frontend ne doit changer.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/house_ruler_resolver.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/dignities/chart_object_inputs.py`
- `backend/app/domain/astrology/dominance/chart_object_inputs.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`
- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
- `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md`
- `_condamad/stories/CS-220-dignity-dominance-capability-runtime/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - payloads
  house/rulership et validation.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` -
  mapping house_position enrichi et branchement initial si approprie.
- `backend/app/domain/astrology/builders/chart_object_house_runtime_enricher.py`
  ou module equivalent - selectors/projectors/enrichers house/rulership.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration
  d'enrichissement apres `house_rulers`.
- `_condamad/stories/regression-guardrails.md` - ajout/verif `RG-148`.
- `_condamad/stories/CS-221-chart-object-house-position-rulership-runtime/evidence/validation.md`
  - preuve finale.

Likely tests:

- `backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py`
  - contrats, selector, projector, enricher.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` -
  coherence capacites/payloads.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` -
  integration `NatalResult.chart_objects`.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
  - guards anti-drift.
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` et
  `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` -
  non-regression rulers/dominance.

Files not expected to change:

- `backend/app/domain/astrology/planetary_conditions/**` - hors scope.
- `backend/app/domain/astrology/dignities/**` - aucune doctrine ou score ne
  doit changer, sauf adaptation strictement necessaire de consommation
  `house_position` deja existante et justifiee.
- `backend/app/domain/astrology/dominance/**` - aucune doctrine ou score ne
  doit changer, sauf adaptation strictement necessaire de consommation runtime
  et justifiee.
- `backend/app/domain/astrology/interpretation/**` - hors scope.
- `backend/app/services/chart/json_builder.py` - aucun changement JSON public.
- `backend/app/api/**` - aucun endpoint modifie.
- `backend/app/infra/**` et `backend/migrations/**` - aucune persistance ou DB.
- `frontend/src/**` - `chart_objects` reste interne backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: `dataclasses`, les contrats runtime existants et pytest
  suffisent.

## 21. Validation Plan

Run or justify why skipped. Toutes les commandes Python doivent etre lancees
apres activation du venv depuis la racine du repo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Tests cibles:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
```

Controles qualite depuis `backend`:

```powershell
Push-Location backend
ruff format .
ruff check .
pytest -q
Pop-Location
```

Scans anti-regression depuis la racine:

```powershell
rg -n "object_type ==|\\.object_type ==|ChartObjectType\\.PLANET|ChartObjectType\\.LUMINARY" `
  backend/app/domain/astrology/builders `
  backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/dominance -g "*.py"
rg -n "HouseRulershipPayloadBuilder|MarsRulershipPayloadBuilder|new.*HouseRulerResolver|SIGN_RULERS|sign_rulers\\s*=\\s*\\{" `
  backend/app/domain/astrology -g "*.py"
rg -n "\\{1, 4, 7, 10\\}|\\{2, 5, 8, 11\\}|angular.*succedent.*cadent" `
  backend/app/domain/astrology/builders `
  backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/dominance -g "*.py"
rg -n "interpretation|narrative|prompt|llm|meaning|psychological" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders -g "*.py"
rg -n "RG-148" _condamad/stories/regression-guardrails.md
rg -n "CS-221 Final Evidence" _condamad/stories/CS-221-chart-object-house-position-rulership-runtime/evidence/validation.md
git diff -- backend/app/domain/astrology/planetary_conditions `
  backend/app/domain/astrology/interpretation `
  backend/app/services/chart/json_builder.py backend/app/api `
  backend/app/infra backend/migrations frontend/src
```

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-221-chart-object-house-position-rulership-runtime/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Expected scan results:

- `object_type` scan: zero hit in new consumers/projectors/enrichers, except
  tests or projection builders explicitly documented;
- rulership resolver/table scan: zero second resolver or local sign-ruler table;
- house modality scan: zero new local constant table outside canonical helper;
- anti-interpretation scan: zero hit in runtime payload modules, or only
  pre-existing names outside the payload path and documented;
- adjacent diff: empty unless blocker documented.

Skipped-command rule:

- Toute commande sautee doit etre consignée dans l'evidence finale avec la
  commande exacte, la raison, le risque et la preuve de remplacement.

## 22. Regression Risks

- Risk: les maitrises sont dupliquees dans un second resolver.
  - Guardrail: reuse `HouseRulerResolver`, AC14 et `RG-148`.
- Risk: la modalite de maison est recodee localement avec des constantes.
  - Guardrail: AC2 et scans de constantes.
- Risk: les payloads deviennent interpretatifs.
  - Guardrail: AC15 et scan anti-interpretation.
- Risk: la dominance change car les rulers ASC/MC sont projetes differemment.
  - Guardrail: AC12, golden cases et preservation des sorties historiques.
- Risk: fuite vers JSON public, API ou frontend.
  - Guardrail: AC16, generated contract blocker et diff adjacent.

## 23. Dev Agent Instructions

- Implement only CS-221.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, unresolved marker or hidden residual work.
- Reuse `HouseRulerResolver`, `HouseRulerResult`, `sign_rulerships` and
  `resolve_house_kind` or the canonical runtime equivalent.
- Consume `chart_objects` through capabilities and payloads, not `object_type`.
- Do not change house calculation, rulership doctrine, dignity scores,
  dominance ranking, JSON public output, API, DB, migrations or frontend.
- Use French top-of-file comments/docstrings for new or significantly modified
  Python files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved markers or hidden residual in-domain work.

## 24. References

- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`
  - socle `ChartObjectRuntimeData` et `supports_house_position`.
- `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
  - precedent selector/projector par capacite.
- `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md`
  - precedent payloads runtime et validation.
- `_condamad/stories/CS-220-dignity-dominance-capability-runtime/00-story.md`
  - precedent selectors/projectors/enrichers et calculs multi-passes.
- `_condamad/stories/regression-guardrails.md` - invariants RG-144 a RG-148.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - contrat
  runtime a enrichir.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` -
  builder initial des objets du theme.
- `backend/app/domain/astrology/house_ruler_resolver.py` - resolver canonique
  des rulers de maisons.
- `backend/app/domain/astrology/runtime/house_runtime_data.py` - source de
  classification des maisons.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration natal a
  enrichir.
