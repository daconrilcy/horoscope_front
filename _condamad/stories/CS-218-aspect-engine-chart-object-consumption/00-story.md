# Story CS-218 aspect-engine-chart-object-consumption: Migrer le moteur d'aspects vers chart_objects

Status: ready-to-dev

## 1. Objective

Migrer la frontiere d'entree du moteur d'aspects natal pour qu'il consomme
`ChartObjectRuntimeData` via `obj.capabilities.supports_aspects`, puis projette
ces objets vers `AspectBodyRuntimeData` avant d'appeler le coeur geometrique
existant. La story doit conserver les regles d'orbes, les definitions
d'aspects, l'ordre deterministe des resultats et les collections historiques de
`NatalResult`, sans changer l'API publique ni introduire de branches metier par
`object_type`.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: brief utilisateur du 2026-05-22 pour `CS-218 - Aspect Engine Consumption from Chart Objects`.
- Reason for change: CS-217 a cree `ChartObjectRuntimeData` et
  `NatalResult.chart_objects`, mais `natal_calculation.py` construit encore les
  entrees du moteur d'aspects depuis `positions_raw` et `points_raw`. Le risque
  est une fausse migration ou une croissance de builders specialises.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: le brief demande une migration de frontiere
  d'entree, pas une refonte astrologique. Les AC couvrent la selection par
  `supports_aspects`, les erreurs explicites, les doublons, la projection
  unique, le branchement natal, la non-regression et le guardrail `object_type`.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology/calculators`
- In scope:
  - creer un selector pur des objets aspectables depuis `ChartObjectRuntimeData`;
  - creer un projector unique `ChartObjectRuntimeData -> AspectBodyRuntimeData`;
  - faire passer l'orchestrateur natal par `chart_objects` avant `calculate_major_aspects`;
  - conserver le coeur algorithmique de `calculate_major_aspects`;
  - conserver les contrats d'aspects existants et les sorties publiques;
  - conserver `planet_positions`, `astral_points`, `houses`, `chart_objects` et les autres collections de `NatalResult`;
  - ajouter des tests unitaires selector/projector/calcul depuis `chart_objects`;
  - etendre le guardrail d'architecture borne au domaine aspects.
- Out of scope:
  - migration des dignites, dominance, interpretation, conditions planetaires avancees ou scoring;
  - activation automatique des etoiles fixes, parts arabes ou cuspides dans les aspects si leur capacite n'est pas explicitement vraie;
  - refonte des orbes, familles d'aspects, priorites, ecoles ou definitions;
  - changement d'API publique, OpenAPI, frontend, DB, migrations ou seeders;
  - suppression de `planet_positions`, `astral_points`, `houses`, `angles` ou `chart_objects`.
- Explicit non-goals:
  - ne pas modifier volontairement `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier volontairement `backend/app/domain/astrology/dominance/**`;
  - ne pas modifier volontairement `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier volontairement `backend/app/domain/astrology/planetary_conditions/**`;
  - ne pas modifier volontairement `backend/app/domain/astrology/interpretation/**`;
  - ne pas modifier volontairement `backend/app/services/chart/json_builder.py`;
  - ne pas modifier volontairement `backend/app/api/**`, `backend/app/infra/**`, `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas changer les invariants `RG-135` a `RG-144`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: service-boundary-refactor
- Archetype reason: la story deplace la frontiere de service du calculateur
  d'aspects depuis des collections specialisees vers une entree runtime unifiee,
  sans changer le comportement geometrique interne.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: tout objet `ChartObjectRuntimeData` avec `supports_aspects=True` peut devenir candidat d'aspect;
  - autorise: les points ou angles deja marques aspectables peuvent apparaitre dans les calculs;
  - interdit: modifier les regles d'orbes, definitions d'aspects, familles, scores ou interpretation;
  - interdit: changer les champs publics ou supprimer les collections historiques de `NatalResult`.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le maintien des resultats existants exige de
  conserver `planet_positions` comme source active parallele, ou si un
  changement d'API publique devient necessaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le flux effectif doit etre prouve depuis `NatalResult.chart_objects` et les objets transmis a `calculate_major_aspects`, pas par un scan seul. |
| Baseline Snapshot | yes | Les aspects existants doivent etre compares avant/apres la migration d'entree. |
| Ownership Routing | yes | Le selector/projector doivent vivre au voisinage du calculateur d'aspects, pas dans le builder general de `chart_objects`. |
| Allowlist Exception | yes | Les exceptions sont interdites explicitement; le registre doit prouver qu'il n'existe aucune allowlist. |
| Contract Shape | no | Aucun contrat public/API n'est modifie; `AspectBodyRuntimeData` conserve sa forme sauf extension strictement necessaire et testee. |
| Batch Migration | no | Un seul consommateur est migre: le moteur d'aspects natal. |
| Reintroduction Guard | yes | Le domaine aspects doit bloquer les branches `object_type` et les dependances directes aux collections specialisees. |
| Persistent Evidence | yes | La migration affirme une non-regression et doit conserver baseline, scans et resultats de validation dans l'evidence finale. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects` produit par `build_natal_result`;
  - les `AspectBodyRuntimeData` transmis a `calculate_major_aspects` apres selector/projector;
  - AST guard du domaine aspects, etendu depuis `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`.
- Secondary evidence:
  - scans cibles `rg`;
  - diff sur `natal_calculation.py` et `calculators/aspects.py`;
  - tests unitaires selector/projector.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas que l'orchestrateur natal utilise reellement `chart_objects` au moment de calculer les aspects.
- Required runtime/domain proof:
  - un test avec spy ou instrumentation locale doit observer les codes transmis a `calculate_major_aspects` depuis `chart_objects`;
  - un test selector doit prouver le filtrage par `supports_aspects`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `rg -n "aspect_source_positions|aspect_positions|build_aspect_body_from_position|calculate_major_aspects" backend/app/domain/astrology/natal_calculation.py`;
  - `rg -n "build_aspect_body_from_position|calculate_major_aspects" backend/app/domain/astrology/calculators/aspects.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`;
  - un inventaire des paires d'aspects d'un theme natal existant ou test golden deja disponible.
- Comparison after implementation:
  - memes tests cibles avant/apres;
  - nouveau test prouvant que le pool transmis a `calculate_major_aspects` vient de `chart_objects`;
  - scans anti-regression listes dans le Validation Plan.
- Expected invariant:
  - pour les objets deja aspectables avant CS-218, les aspects produits restent equivalents;
  - les nouvelles participations ne viennent que d'objets `supports_aspects=True`;
  - l'ordre de projection reste deterministe.
- Allowed differences:
  - ajout d'un selector;
  - ajout d'un projector;
  - branchement natal depuis `chart_objects`;
  - nouveaux tests et guardrails;
  - nouveaux aspects uniquement si un objet non planetaire existant declare deja explicitement `supports_aspects=True`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Selection d'objets aspectables | domaine aspects ou `aspect_inputs.py` | `natal_calculation.py`, API, frontend, builders specialises |
| Projection `ChartObjectRuntimeData -> AspectBodyRuntimeData` | module unique du domaine aspects | builder par planete, angle, point ou etoile |
| Coeur geometrique des aspects | `backend/app/domain/astrology/calculators/aspects.py` | orchestrateur natal, runtime builder general |
| Construction de `chart_objects` | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | calculateur d'aspects |
| Branchement orchestration natal | `backend/app/domain/astrology/natal_calculation.py` | services chart, API, frontend |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-218. | Politique permanente sans exception. |

Validation rule:

- Tout besoin d'exception pour branche `object_type`, builder specialise ou
  consommation directe de collection historique doit bloquer l'implementation.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: la story ne doit pas changer l'API publique, l'OpenAPI, les schemas
  frontend ou la forme publique de `NatalResult`. Toute extension de
  `AspectBodyRuntimeData` doit rester interne, justifiee et testee.
- Internal projection rule:
  - `longitude` est obligatoire pour le calcul brut des aspects;
  - `zodiac_position` reste optionnel tant que le calculateur et la sortie
    aspectuelle publique n'exposent pas signe/degre/minute depuis le participant;
  - si une extension interne de `AspectBodyRuntimeData` devient necessaire pour
    transporter `display_name` ou `classifications`, ces champs doivent etre
    copies depuis `ChartObjectRuntimeData` dans le projector unique.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-218 migre un seul consommateur concret, le moteur d'aspects natal. Les autres consommateurs de `chart_objects` restent hors scope.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/evidence/validation.md` | Baseline, tests, scans, ruff/pytest et ecarts assumables. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le domaine aspects revienne a une selection par collections specialisees ou par `object_type`.
- Forbidden examples in aspect engine files:
  - `if obj.object_type ==`;
  - `if object_type == "planet"`;
  - `if object_type == "angle"`;
  - `if object_type == "astral_point"`;
  - `ChartObjectType.PLANET`;
  - `ChartObjectType.ANGLE`;
  - nouveau `PlanetAspectBodyBuilder`, `AngleAspectBodyBuilder` ou `AstralPointAspectBodyBuilder`.
- Required guard evidence:
  - test AST ou scan cible sous `backend/tests/unit/domain/astrology`;
  - scan `rg` borne a `backend/app/domain/astrology/calculators`;
  - scan des dependances anciennes `planet_positions|astral_points|angles|fixed_stars` dans le domaine aspects.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

Le codebase actuel indique:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-217` est la derniere story numerotee et elle est enregistree comme `done`; `CS-218` est donc le prochain numero.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-144` protege `ChartObjectRuntimeData`, le builder
  canonique et l'interdiction des branches `object_type`.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - `ChartObjectCapabilities.supports_aspects` existe deja comme capacite contractuelle.
- Evidence 4: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  - le builder CS-217 projette les familles existantes en `ChartObjectRuntimeData`.
- Evidence 5: `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`
  - `AspectBodyRuntimeData` existe avec `code`, `body_type` et `longitude`.
- Evidence 6: `backend/app/domain/astrology/calculators/aspects.py` -
  `calculate_major_aspects` calcule deja depuis `AspectBodyRuntimeData`.
- Evidence 7: `backend/app/domain/astrology/natal_calculation.py` -
  l'orchestrateur construit aujourd'hui `aspect_source_positions` depuis
  `positions_raw` et `points_raw`, avant `chart_objects`.
- Evidence 8: `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
  - les tests prouvent l'ancien controle par option `include_points_in_aspects`.
- Evidence 9: source-alignment review - une story qui ajoute `chart_objects`
  mais laisse le moteur consommer `planet_positions` ne satisfait pas CS-218.

## 6. Target State

Apres implementation:

- le pool d'aspects natal est derive de `chart_objects`;
- la selection se fait exclusivement par `obj.capabilities.supports_aspects`;
- les objets non aspectables sont ignores sans erreur;
- les objets aspectables sans longitude provoquent une erreur explicite;
- l'absence de `zodiac_position` ne bloque pas le calcul brut tant que la sortie
  aspectuelle n'en depend pas;
- deux objets aspectables avec le meme `code` provoquent une erreur explicite;
- la projection vers `AspectBodyRuntimeData` est centralisee;
- `calculate_major_aspects` conserve son coeur algorithmique;
- les anciennes collections de `NatalResult` restent presentes;
- les tests prouvent qu'un angle ou point non planetaire peut participer si sa capacite est vraie;
- le domaine aspects ne contient pas de logique metier par `object_type`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-144` - CS-218 consomme explicitement le contrat cree par CS-217 et doit interdire les branches `object_type` dans le calculateur d'aspects.
  - `RG-163` - les regles d'aspects, orbes et DTO runtime existants ne doivent pas etre remplaces par un second moteur.
  - `RG-164` - la projection publique enrichie des aspects doit rester stable; CS-218 ne change pas le format public.
- Non-applicable invariants:
  - `RG-135` a `RG-143` - CS-218 ne touche pas les moteurs de conditions planetaires avancees, dignites ou profils symboliques.
- Required regression evidence:
  - tests selector/projector/calcul depuis `chart_objects`;
  - test natal de non-regression des aspects existants;
  - scan anti-branches `object_type` dans les calculateurs d'aspects;
  - scan anti-dependances directes a `planet_positions`, `astral_points`, `angles`, `fixed_stars` dans le domaine aspects.
- Allowed differences:
  - nouveaux aspects uniquement lorsque les objets runtime portent deja `supports_aspects=True`;
  - aucune difference autorisee sur orbes, definitions, familles, ecole, sortie publique ou collections historiques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Selector filtre `supports_aspects=True`. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`. |
| AC2 | Non-aspectable sans longitude ignore. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`. |
| AC3 | Aspectable sans longitude erreur explicite. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`. |
| AC4 | Code aspectable duplique erreur explicite. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`. |
| AC5 | Projection unique vers `AspectBodyRuntimeData`. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`; scan builders. |
| AC6 | Sun/Moon/Mars aspectent depuis `chart_objects`. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`. |
| AC7 | Angle aspectable inclus. | `unit_test`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`. |
| AC8 | Orchestrateur natal consomme `chart_objects`. | `integration_test`; `pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`. |
| AC9 | Aspects planetaires existants equivalents. | `baseline_before_after_diff`; `pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`. |
| AC10 | `NatalResult` garde ses collections. | `contract_test`; `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`. |
| AC11 | Aucune branche `object_type` dans aspects. | `ast_architecture_guard`; `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`. |
| AC12 | Aucun usage direct des collections historiques dans les calculateurs. | Evidence profile: `static_scan`; command: `rg` calculators legacy inputs. |
| AC13 | Regles d'orbes stables. | `baseline_before_after_diff`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`. |
| AC14 | `RG-145` est enregistre. | Evidence profile: `reintroduction_guard`; command: `rg -n "RG-145" _condamad/stories/regression-guardrails.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer le flux actuel (AC: AC8, AC9, AC12, AC13)
  - [ ] Subtask 1.1 - Inspecter `natal_calculation.py`, `calculators/aspects.py`,
    `aspect_calculation_contracts.py`, `chart_object_runtime_data.py` et
    `chart_object_runtime_builder.py`.
  - [ ] Subtask 1.2 - Capturer les scans initiaux sur `build_aspect_body_from_position`, `aspect_source_positions`, `planet_positions`, `astral_points` et `object_type`.
  - [ ] Subtask 1.3 - Executer le test actuel `test_natal_aspects_include_points.py`
    comme baseline.

- [ ] Task 2 - Creer le selector par capacites (AC: AC1, AC2, AC3, AC4)
  - [ ] Subtask 2.1 - Ajouter `AspectChartObjectSelector` dans le domaine aspects.
  - [ ] Subtask 2.2 - Filtrer uniquement par `chart_object.capabilities.supports_aspects`.
  - [ ] Subtask 2.3 - Valider longitude obligatoire pour les objets aspectables.
  - [ ] Subtask 2.4 - Detecter les doublons de code aspectable en preservant l'ordre.

- [ ] Task 3 - Creer le projector unique vers `AspectBodyRuntimeData` (AC: AC5, AC11, AC12)
  - [ ] Subtask 3.1 - Ajouter `AspectBodyProjector` dans le module d'entree aspects.
  - [ ] Subtask 3.2 - Copier `code` et `longitude` depuis `ChartObjectRuntimeData`.
  - [ ] Subtask 3.3 - Resoudre `body_type` sans branche metier par `object_type`,
    en reutilisant le contrat local choisi.
  - [ ] Subtask 3.4 - Copier `display_name` ou `classifications` depuis
    `ChartObjectRuntimeData` uniquement si `AspectBodyRuntimeData` est etendu.
  - [ ] Subtask 3.5 - Supprimer l'usage natal direct de
    `build_aspect_body_from_position` du flux `chart_objects`.

- [ ] Task 4 - Adapter l'orchestrateur natal (AC: AC8, AC9, AC10, AC13)
  - [ ] Subtask 4.1 - Construire `chart_objects` avant le calcul des aspects si l'ordre actuel ne permet pas de l'utiliser.
  - [ ] Subtask 4.2 - Remplacer la construction `aspect_positions` depuis `positions_raw`/`points_raw` par selector + projector depuis `chart_objects`.
  - [ ] Subtask 4.3 - Mapper `include_points_in_aspects` au contrat de capacites
    ou bloquer avec evidence si le flag ne peut pas rester coherent.
  - [ ] Subtask 4.4 - Garder les compteurs d'observabilite coherents avec le nombre de candidats projetes.

- [ ] Task 5 - Ajouter les tests comportementaux (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
  - [ ] Subtask 5.1 - Ajouter des tests selector/projector sous `backend/tests/unit/domain/astrology`.
  - [ ] Subtask 5.2 - Ajouter un test de calcul d'aspects depuis `chart_objects`.
  - [ ] Subtask 5.3 - Ajouter un test avec angle aspectable.
  - [ ] Subtask 5.4 - Verifier messages d'erreur et ordre deterministe.

- [ ] Task 6 - Ajouter les tests d'integration et guardrails (AC: AC8, AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Subtask 6.1 - Creer un test natal dedie au flux `chart_objects`.
  - [ ] Subtask 6.2 - Etendre le guard AST d'architecture pour le domaine aspects.
  - [ ] Subtask 6.3 - Verifier que `RG-145` reste enregistre dans le registre des guardrails.
  - [ ] Subtask 6.4 - Documenter toute difference autorisee dans l'evidence finale.

- [ ] Task 7 - Valider et documenter (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer tests cibles, `ruff format .`, `ruff check .` et `pytest -q` depuis `backend`.
  - [ ] Subtask 7.3 - Executer les scans `rg` anti-regression.
  - [ ] Subtask 7.4 - Produire l'evidence finale courte demandee par le brief.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartObjectRuntimeData` et `ChartObjectCapabilities` depuis `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `AspectBodyRuntimeData` et `calculate_major_aspects` depuis les contrats/calculateur existants;
  - `CelestialRuntimeCatalog` pour le `body_type` canonique des regles d'orbes;
  - `build_chart_object_runtime_data` comme source de construction de `chart_objects`, sans le dupliquer.
- Do not recreate:
  - un builder par famille (`PlanetAspectBodyBuilder`, `AngleAspectBodyBuilder`, `AstralPointAspectBodyBuilder`, `FixedStarAspectBodyBuilder`);
  - les regles d'orbes;
  - les definitions d'aspects;
  - le calcul de positions planetaires, points astraux, maisons ou angles;
  - un second contrat concurrent a `ChartObjectRuntimeData`.
- Shared abstraction allowed only if:
  - elle remplace une duplication concrete du flux selector/projector;
  - elle reste dans le domaine aspects;
  - elle ne cree pas de compatibilite transitoire ou de fallback silencieux.

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

Symboles et chemins explicitement interdits dans le moteur d'aspects:

- `if obj.object_type ==`
- `if chart_object.object_type ==`
- `if object_type == "planet"`
- `if object_type == "angle"`
- `if object_type == "astral_point"`
- `ChartObjectType.PLANET`
- `ChartObjectType.ANGLE`
- `ChartObjectType.ASTRAL_POINT`
- `PlanetAspectBodyBuilder`
- `AngleAspectBodyBuilder`
- `AstralPointAspectBodyBuilder`
- `FixedStarAspectBodyBuilder`
- nouvelle selection directe par `planet_positions`, `astral_points`, `angles` ou `fixed_stars` dans le domaine aspects

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Contrat runtime des objets du theme | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | calculateur d'aspects, API, frontend |
| Construction `chart_objects` | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | selector/projector aspects |
| Selection aspectable | domaine aspects, selector unique | `natal_calculation.py`, builders specialises |
| Projection vers corps d'aspects | domaine aspects, projector unique | builders par famille d'objet |
| Calcul geometrique | `backend/app/domain/astrology/calculators/aspects.py` | orchestrateur natal |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Internal Usage Search

- Internal usage search: required
- Reason: la migration doit prouver que le flux natal d'aspects ne consomme
  plus directement les collections historiques dans les calculateurs, tout en
  conservant ces collections dans `NatalResult`.
- Required searches:
  - `rg -n "planet_positions|astral_points|angles|fixed_stars" backend/app/domain/astrology/calculators -g "*.py"`
  - `rg -n "object_type ==|\\.object_type|ChartObjectType" backend/app/domain/astrology/calculators -g "*.py"`

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is intentionally affected. If OpenAPI or frontend
  contract changes, the dev agent must stop and record the blocker.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/calculators/aspect_inputs.py` - nouveau module pur
  pour le selector et le projector.
- `backend/app/domain/astrology/calculators/aspects.py` - suppression de l'entree
  historique si elle reste dans le flux natal.
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py` -
  ajustement interne strictement limite de `AspectBodyRuntimeData`.
- `backend/app/domain/astrology/natal_calculation.py` - brancher selector/projector depuis `chart_objects`.
- `_condamad/stories/regression-guardrails.md` - verifier que `RG-145` reste present; ne modifier que si la garde doit etre corrigee.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py` - tests selector/projector/calcul depuis `chart_objects`.
- `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` -
  adaptation du test de flux.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - extension du guard anti-branches `object_type`.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` -
  non-regression des collections historiques.

Files not expected to change:

- `backend/app/domain/astrology/dignities/**` - scoring hors scope.
- `backend/app/domain/astrology/dominance/**` - dominance hors scope.
- `backend/app/domain/astrology/advanced_conditions/**` - conditions traditionnelles hors scope.
- `backend/app/domain/astrology/planetary_conditions/**` - conditions planetaires avancees hors scope.
- `backend/app/domain/astrology/interpretation/**` - interpretation hors scope.
- `backend/app/services/chart/json_builder.py` - projection publique hors scope.
- `backend/app/api/**` - aucune route/schema.
- `backend/app/infra/**` - aucune persistence.
- `backend/migrations/**` - aucune migration.
- `frontend/src/**` - aucun frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Toutes les commandes Python doivent etre lancees apres activation du venv, conformement a `AGENTS.md`.

Depuis la racine du repo pour les tests cibles:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py
pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
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
rg -n "object_type ==|\\.object_type|ChartObjectType" backend/app/domain/astrology/calculators -g "*.py"
rg -n "planet_positions|astral_points|angles|fixed_stars" backend/app/domain/astrology/calculators -g "*.py"
rg -n "PlanetAspectBodyBuilder|AngleAspectBodyBuilder|AstralPointAspectBodyBuilder|FixedStarAspectBodyBuilder" backend/app backend/tests -g "*.py"
rg -n "RG-145" _condamad/stories/regression-guardrails.md
```

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Resultat attendu:

- les tests cibles passent;
- `ruff format .`, `ruff check .` et `pytest -q` passent dans `backend`;
- les scans interdits n'ont pas de hit applicatif non documente;
- tout hit tolere est limite aux tests, contrats, ou builders de compatibilite
  explicitement cites.

## 22. Regression Risks

- Risque: fausse migration, avec `chart_objects` present mais moteur encore branche sur `planet_positions`.
  - Guardrail: AC8, test de flux natal et scan `aspect_source_positions`.
- Risque: plusieurs builders specialises recreent la dette par famille d'objet.
  - Guardrail: AC5, AC11, AC12 et scan des noms interdits.
- Risque: les aspects changent par modification involontaire des orbes ou definitions.
  - Guardrail: AC9, AC13 et baseline avant/apres.
- Risque: un objet aspectable invalide est ignore silencieusement.
  - Guardrail: AC3 et AC4.
- Risque: fuite de changement public vers JSON/OpenAPI/frontend.
  - Guardrail: AC10, generated contract blocker et fichiers hors scope.

## 23. Dev Agent Instructions

- Implement only CS-218.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Consume `chart_objects` through `capabilities.supports_aspects`.
- Keep `AspectBodyRuntimeData` as a technical projection, not a parallel source of truth.
- Do not add business logic based on `object_type` inside aspect calculators.
- Do not create planet/angle/point/fixed-star-specific aspect builders.
- Do not change aspect orb rules, aspect definitions, aspect schools, scoring or interpretation.
- Do not remove `planet_positions`, `astral_points`, `houses`, `chart_objects` or existing aspect output fields.
- Use French top-of-file comments/docstrings for new or significantly modified applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 24. References

- `backend/app/domain/astrology/calculators/aspects.py` - coeur actuel de calcul des aspects.
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py` - contrats `AspectBodyRuntimeData`, definitions et regles d'orbes.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - contrat runtime unifie et `supports_aspects`.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - owner de construction `chart_objects`.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration actuelle du theme natal et flux d'entree aspects.
- `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` - non-regression existante sur l'inclusion de points.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - guardrail CS-217 a etendre.
- `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md` - source contractuelle de `ChartObjectRuntimeData`.
- `_condamad/stories/regression-guardrails.md` - invariants applicables `RG-144` et `RG-145`.
