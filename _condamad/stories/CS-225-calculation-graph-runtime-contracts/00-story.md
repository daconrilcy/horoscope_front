# Story CS-225 calculation-graph-runtime-contracts: Creer les contrats runtime du graphe de calcul
Status: done

## 1. Objective

Creer les contrats types d'un graphe de calcul declaratif pour le runtime astrologique, sans migrer le pipeline natal vers ce graphe.
La story rend les dependances entre calculs explicites, validables et inspectables avant l'ajout d'un runner topologique.

## 2. Trigger / Source

- Source type: architecture-runtime-contract.
- Source reference: `_story_briefs/cs-225-calculation-graph-runtime-contracts.md`.
- Reason for change: CS-217 a CS-224 ont stabilise `NatalResult.chart_objects` et les payloads runtime; les dependances de calcul restent implicites.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story ajoute des contrats et validations purs, sans API, DB, frontend, migration du pipeline natal ou dependance externe de graph processing.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology/runtime`.
- In scope:
  - creer `CalculationGraphDefinition`, `CalculationNodeDefinition`, `CalculationInputDefinition`;
  - creer les statuts de node: declared, ready, executed, failed, skipped;
  - creer `CalculationGraphValidationResult` et les erreurs deterministes du validator;
  - verifier les codes vides, doublons de node, doublons d'`output_key`, dependances inconnues et cycles;
  - distinguer dependances obligatoires et dependances optionnelles;
  - produire un ordre topologique theorique stable sans executer les calculateurs;
  - documenter calculation graph, astrological graph et `chart_objects`;
  - ajouter les tests unitaires du validator et des contrats.
- Out of scope:
  - migrer `build_natal_result` vers le graphe;
  - executer un graphe complet en production;
  - ajouter transits, progressions, directions, synastrie ou returns;
  - changer une route FastAPI, un schema public, OpenAPI, DB, migrations, frontend ou prompts;
  - ajouter une dependance externe de graph processing;
  - remplacer `AstrologicalGraphNodeType` ou le graphe astrologique semantique.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas importer dynamiquement une fonction calculatrice depuis le contrat;
  - ne pas introduire de calcul astrologique nouveau.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story ajoute un socle de contrats backend-domain et un validator pur pour une orchestration future.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: nouveaux modules de contrats et de validation sous le runtime astrologique;
  - autorise: tests unitaires et documentation d'architecture dediee;
  - autorise: ordre topologique theorique retourne par le validator;
  - interdit: execution metier d'un graphe, changement API, DB, frontend, pipeline natal ou contrats publics.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'implementation touche une route publique, une migration DB, le frontend, une dependance externe ou `build_natal_result`.
- Additional validation rules:
  - les contrats utilisent des dataclasses immuables et typees sans dependance FastAPI, SQLAlchemy, infra, settings, LLM ou frontend;
  - `calculator` reste un identifiant stable sous forme de chaine, sans import dynamique ni appel de fonction;
  - les dependances sont resolues seulement contre les inputs declares et les `output_key` de nodes;
  - les dependances optionnelles inconnues ne bloquent pas la validite, mais restent inspectables;
  - les cycles directs et indirects produisent des messages explicites et deterministes;
  - `ChartObjectRuntimeData` reste compatible comme surface runtime consommee par futurs nodes, sans devenir obligatoire pour tous les graphes;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le graphe de calcul decrit l'orchestration technique; `chart_objects` reste la surface canonique des objets du theme. |
| Baseline Snapshot | yes | Les contrats runtime existants et le pipeline natal doivent etre connus avant ajout. |
| Ownership Routing | yes | Contrats, validator, documentation et tests ont des proprietaires separes. |
| Allowlist Exception | yes | Les seuls usages conserves hors graphe sont le pipeline procedural et les contrats semantiques existants. |
| Contract Shape | yes | Les dataclasses et enums attendus sont le coeur de la story. |
| Batch Migration | yes | Contrats, validator, documentation et tests sont livres en lots controlables. |
| Reintroduction Guard | yes | Les scans bloquent les dependances externes de graph processing et les deltas API/DB/front. |
| Persistent Evidence | yes | Tests, scans et preuve finale doivent etre conserves dans le dossier CS-225. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_validator.py`;
  - `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` pour compatibilite des futurs nodes;
  - `docs/architecture/astrology-calculation-graph.md`.
- Runtime/domain artifacts:
  - dataclasses immuables de definition du graphe, nodes, inputs, resultats et erreurs;
  - enum de statut de node;
  - validator pur produisant validite, erreurs et ordre topologique theorique;
  - tests unitaires sous `backend/tests/unit/domain/astrology/`.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - `app.routes`, `app.openapi()` et `TestClient` sans delta public volontaire;
  - scans anti-dependance externe `networkx|igraph|graphlib`.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la detection de cycles, ni l'ordre topologique stable, ni la neutralite OpenAPI runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/runtime/astrological_graph_contracts.py`;
  - recherche ciblee de `build_natal_result` et de `NatalResult`;
  - recherche ciblee de `CalculationGraphDefinition|CalculationNodeDefinition`;
  - `Select-String "RG-144|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests CS-225 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend et pipeline natal.
- Expected invariant:
  - le pipeline natal reste procedural;
  - le graphe de calcul reste descriptif et non execute;
  - le graphe astrologique semantique reste distinct;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - nouveaux modules de contrats et validator;
  - documentation d'architecture;
  - tests unitaires et guards cibles;
  - Registry gap: un invariant dedie au graphe de calcul pourra etre ajoute ulterieurement hors generation normale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats de graphe de calcul | `backend/app/domain/astrology/runtime/calculation_graph_contracts.py` | route API, service monolithique, frontend |
| Validation declarative | `backend/app/domain/astrology/runtime/calculation_graph_validator.py` | `natal_calculation.py`, infra, DB |
| Graphe astrologique semantique | `astrological_graph_contracts.py` existant | contrats de graphe de calcul |
| Documentation architecture | `docs/architecture/astrology-calculation-graph.md` | commentaires disperses uniquement |
| Tests unitaires | `backend/tests/unit/domain/astrology/` | tests API opaques pour logique pure |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `natal_calculation.py` | ordre procedural | Pipeline natal hors scope CS-225. | Temporary; exit condition: migration story approved. |
| `astrological_graph_contracts.py` | graphe semantique astrologique | Contrat metier distinct du graphe de calcul. | Permanent. |
| serializers et routes publics | contrats JSON existants | CS-225 ne change pas l'API publique. | Permanent pour cette story. |

Validation rule:

- Toute execution metier d'un node ou toute mutation du pipeline natal bloque l'implementation CS-225.

## 4f. Contract Shape

- Contract type:
  - dataclasses Python immuables avec `frozen=True` et `slots=True`;
  - enum de statut de node;
  - validator pur retournant un resultat structure;
  - aucune nouvelle API HTTP.
- Required dataclasses:
  - `CalculationGraphDefinition`;
  - `CalculationNodeDefinition`;
  - `CalculationInputDefinition`;
  - `CalculationGraphValidationResult`;
  - `CalculationGraphValidationError`.
- Required enum:
  - `CalculationNodeStatus`.
- Fields:
  - `graph_code`;
  - `version`;
  - `nodes`;
  - `required_inputs`;
  - `code`;
  - `output_key`;
  - `depends_on`;
  - `optional_depends_on`;
  - `calculator`;
  - `tags`;
  - `key`;
  - `value_type`;
  - `required`;
  - `is_valid`;
  - `errors`;
  - `topological_order`.
- Required fields:
  - `graph_code`;
  - `version`;
  - `nodes`;
  - `code`;
  - `output_key`;
  - `depends_on`;
  - `calculator`;
  - `key`;
  - `value_type`;
  - `is_valid`;
  - `errors`.
- Optional fields:
  - `optional_depends_on`;
  - `tags`;
  - `topological_order` may be empty when validation fails before ordering.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-225.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | dependances implicites documentees dans le code | contrats dataclass | aucun runtime | contracts tests | import pur | dependance externe |
| 2 | validation manuelle des dependances | validator pur | aucun runtime | validator tests | topological order | cycle non detecte |
| 3 | distinction floue graphes | doc architecture | aucun runtime | doc presence test | doc mentions | confusion graphe semantique |
| 4 | preuve manuelle API neutre | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route ou schema modifie |

Completion rule: chaque batch conserve `pytest -q`, `app.routes`, `app.openapi()` et le pipeline natal procedural.

## 4h. Reintroduction Guard

- Guard target:
  - aucun `networkx`, `igraph` ou dependance externe de graph processing dans `backend/app/domain/astrology`;
  - `graphlib` standard library reste absent sauf justification explicite dans l'evidence finale;
  - aucun import FastAPI, SQLAlchemy, infra, settings, LLM ou frontend dans les modules de contrats et validator;
  - aucun changement volontaire de `app.routes`, `app.openapi()` ou payload public;
  - aucune mutation de `build_natal_result` pour executer un graphe.
- Guard mechanism:
  - tests unitaires de contrats;
  - tests unitaires de validator;
  - AST guard ou scans cibles sur imports interdits;
  - `TestClient` smoke sur OpenAPI;
  - scan cible `rg -n "networkx|igraph|graphlib" backend/app/domain/astrology backend/tests -g "*.py"`.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - `backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`;
  - `backend/tests/architecture` seulement si un guard d'imports transverse est ajoute.
- Guard evidence:
  - chemins complets `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`;
  - chemins complets `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-225-calculation-graph-runtime-contracts/evidence/validation.md` | Conserver tests, lint et resultats cibles CS-225. |
| API neutrality evidence | `_condamad/stories/CS-225-calculation-graph-runtime-contracts/evidence/openapi-routes.md` | Conserver `app.routes`, `app.openapi()` et TestClient. |
| Dependency scan evidence | `_condamad/stories/CS-225-calculation-graph-runtime-contracts/evidence/graph-dependency-scan.md` | Prouver zero dependance externe de graph. |

## 5. Current State Evidence

- Le runtime astrologique contient deja des contrats specialises sous `backend/app/domain/astrology/runtime`.
- Le pipeline natal est encore orchestre proceduralement dans `natal_calculation.py`.
- `NatalResult.chart_objects` est la surface runtime canonique recente pour les objets du theme.
- Les dependances entre maisons, rulerships, aspects, dignites, dominance et signature ne sont pas encore decrites par un contrat commun.
- Le graphe astrologique semantique existant ne doit pas etre confondu avec le graphe de calcul.
- Evidence 1: `backend/app/domain/astrology/runtime` - contrats runtime existants constates par lecture ciblee du dossier.

## 6. Target State

- Les contrats `CalculationGraphDefinition`, `CalculationNodeDefinition` et `CalculationInputDefinition` existent.
- Les nodes declarent `code`, `output_key`, `depends_on`, `optional_depends_on`, `calculator` et `tags`.
- Le validator detecte doublons, dependances inconnues, cycles directs et cycles indirects.
- Le validator produit un ordre topologique theorique deterministe.
- Les dependances optionnelles sont representees sans erreur bloquante.
- La documentation distingue calculation graph, astrological graph et `chart_objects`.
- Aucun runtime metier n'est execute par le graphe dans CS-225.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-contracts: yes;
- astrology: yes;
- API: no;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-144 | local | `ChartObjectRuntimeData` reste le contrat canonique des objets exploitables; CS-225 ne le remplace pas. |
| RG-148 | local | Les payloads house/rulership restent des surfaces runtime existantes; CS-225 declare seulement des dependances futures. |

Non-applicable examples:

- RG-145 aspect engine: hors scope, aucun moteur d'aspects n'est migre.
- RG-147 dignity/dominance: hors scope, aucun scoring n'est recalcule.
- Frontend/style guardrails: hors scope, aucun fichier frontend ou CSS n'est touche.

Registry gap:

- Aucun guardrail global dedie au graphe de calcul declaratif n'existe encore; ne pas enrichir le registre pendant cette generation normale.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Les contrats de graphe existent dans le runtime astrology. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`. |
| AC2 | Chaque node expose un contrat de calcul stable. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`. |
| AC3 | Le validator rejette les graphes invalides. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`. |
| AC4 | Pas de calcul metier ni execution de graphe. | `rg -n "importlib|__import__|build_natal_result" backend/app/domain/astrology/runtime -g "*.py"`. |
| AC5 | Le graphe de calcul reste declaratif. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`; doc cible. |
| AC6 | Le contrat API public reste neutre. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; evidence OpenAPI/TestClient. |
| AC7 | Les tests unitaires du validator passent avec ordre topologique deterministe. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`. |
| AC8 | La doc d'architecture borne CS-225. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`; doc cible. |

## 8. Implementation Tasks

- [x] Task: creer `calculation_graph_contracts.py` avec commentaire global et docstrings en francais. (AC: AC1, AC2)
- [x] Task: ajouter `CalculationNodeStatus` avec les statuts declared, ready, executed, failed et skipped. (AC: AC1, AC2)
- [x] Task: creer `calculation_graph_validator.py` sans import API, DB, infra, settings, LLM ou frontend. (AC: AC3, AC4)
- [x] Task: implementer les validations de champs vides, doublons, dependances inconnues, cycles directs et indirects. (AC: AC3)
- [x] Task: produire un ordre topologique stable fonde sur les nodes declares et leurs `output_key`. (AC: AC3, AC7)
- [x] Task: ajouter les tests unitaires contracts et validator, dont dependances optionnelles et ordre deterministe. (AC: AC1, AC2, AC3, AC7)
- [x] Task: ajouter `docs/architecture/astrology-calculation-graph.md` et le test de presence documentaire. (AC: AC5, AC8)
- [x] Task: ajouter les guards anti-dependance externe et neutralite API via `app.routes`, `app.openapi()` et `TestClient`. (AC: AC4, AC6)
- [x] Task: collecter l'evidence finale dans le dossier CS-225. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les conventions de dataclasses immuables deja presentes dans `backend/app/domain/astrology/runtime`.
- Reutiliser les helpers de tests et fixtures backend existants au lieu de creer une seconde topologie de test.
- Ne pas dupliquer les definitions de `ChartObjectRuntimeData`, `AstrologicalGraphNodeType` ou des payloads existants.
- Ne pas creer une seconde logique de calcul des maisons, aspects, dignites, dominance ou signature.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter `networkx`, `igraph` ou dependance externe de graph processing.
- Ne pas creer de runner de graphe en production.
- Ne pas migrer `build_natal_result`.
- Ne pas utiliser `calculator` comme import dynamique.
- Ne pas ajouter de fallback runtime, shim legacy ou couche compatibility pour executer le graphe.

## 11. Generated Contract Check

- Capture before:
  - `app.routes`;
  - `app.openapi()`;
  - un smoke `TestClient` sur OpenAPI.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code ou schema public ne change volontairement.

## 12. Files to Inspect First

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`.
- `backend/app/domain/astrology/runtime/astrological_graph_contracts.py`.
- `backend/app/domain/astrology/services/natal_calculation.py`.
- `backend/tests/unit/domain/astrology/`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-144|RG-148`.

## 13. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py`.
- `docs/architecture/astrology-calculation-graph.md`.
- `_condamad/stories/CS-225-calculation-graph-runtime-contracts/evidence/validation.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`.

Files not expected to change:

- `frontend/src`.
- `backend/alembic`.
- `backend/app/api`.
- `backend/app/domain/astrology/services/natal_calculation.py`.

## 14. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 15. Validation Plan

Run all Python commands after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

Run anti-regression scans:

```powershell
rg -n "networkx|igraph|graphlib" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "CalculationGraphDefinition|CalculationNodeDefinition" backend/app/domain/astrology/runtime backend/tests
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

If the dedicated API neutrality test does not exist, add a focused TestClient test that records `app.routes` and `app.openapi()` for CS-225 evidence.

## 16. Regression Risks

- Un validator trop permissif peut laisser passer une dependance inconnue ou un cycle.
- Un validator trop couple peut importer FastAPI, DB, settings ou services et casser la purete domaine.
- Une confusion entre calculation graph et astrological graph peut detourner les contrats semantiques existants.
- Une migration prematuree du pipeline natal peut introduire un changement runtime non demande.

## 17. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Implementer le plus petit delta coherent.
- Garder les commentaires globaux et docstrings en francais dans les nouveaux fichiers applicatifs.
- Ne pas utiliser de style inline, CSS ou frontend: aucun fichier frontend n'est attendu.
- Ne pas creer de `requirements.txt`.
- Executer les validations apres activation du venv.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in the story evidence.
- Do not preserve legacy behavior by adding a fallback, shim or compatibility layer for graph execution.
- Conserver dans l'evidence les commandes lancees, les resultats de tests, les scans et la preuve `app.routes` / `app.openapi()`.

## 18. CS-225 Final Evidence Template

```markdown
## CS-225 Final Evidence

### Contracts
- Added calculation graph contracts.
- Added explicit node dependencies and output keys.
- Calculation graph is distinct from astrological graph.

### Validation
- Unknown dependencies are rejected.
- Duplicate nodes and outputs are rejected.
- Cycles are rejected.
- Topological order is deterministic.

### Scope
- No natal pipeline migration yet.
- No API, DB or frontend changes.
- No external graph dependency.

### Commands
- ruff format .
- ruff check .
- pytest -q
- pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py
- pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

## 19. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-225-calculation-graph-runtime-contracts.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the recent validated story structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.
- Final validator rerun note: a third validator execution was not launched after the final marker-only correction because this session limits each command to two attempts.

## 20. References

- `_story_briefs/cs-225-calculation-graph-runtime-contracts.md`.
- `_condamad/stories/regression-guardrails.md` targeted IDs `RG-144|RG-148`.
- `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md` structure reference.
