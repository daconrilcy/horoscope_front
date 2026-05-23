# Story CS-226 natal-calculation-graph-definition: Declarer le graphe de calcul natal
Status: done

## 1. Objective

Declarer le graphe de calcul natal `natal_chart_v1` comme documentation executable des dependances du pipeline, sans remplacer
`build_natal_result` et sans changer les sorties publiques existantes.

## 2. Trigger / Source

- Source type: architecture-runtime-definition.
- Source reference: `_story_briefs/cs-226-natal-calculation-graph-definition.md`.
- Reason for change: CS-225 introduit les contrats de graphe; CS-226 applique ces contrats au theme natal.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story ajoute une definition pure du graphe natal, sans execution, API, DB, frontend, migration ou donnees astrologiques nouvelles.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology/runtime`.
- In scope:
  - creer `build_natal_calculation_graph_definition`;
  - declarer les inputs natals minimaux et derives;
  - declarer les nodes canonical runtime du pipeline natal;
  - declarer les nodes de projection compatibility/public;
  - valider la definition avec `CalculationGraphValidator`;
  - aligner les noms de nodes avec les surfaces runtime documentees du pipeline natal;
  - documenter chaque node par nom, output, dependances et tags;
  - ajouter les tests unitaires d'alignement et d'ordre topologique.
- Out of scope:
  - executer le graphe en production;
  - migrer `build_natal_result`;
  - supprimer le pipeline procedural;
  - changer une route FastAPI, un schema public, OpenAPI, DB, migrations, frontend ou prompts;
  - ajouter transits, synastrie, progressions, directions ou returns;
  - ajouter de nouvelles donnees astrologiques;
  - deplacer massivement les fichiers.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas faire dependre un node calculatoire d'une projection compatibility ou public;
  - ne pas importer FastAPI, SQLAlchemy, services HTTP, repositories, settings, LLM ou frontend depuis la definition;
  - ne pas introduire un runner topologique ni une execution metier par node.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story ajoute une definition backend-domain pure fondee sur les contrats CS-225.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: nouveau module de definition sous le runtime astrologique;
  - autorise: enum ou constantes de codes de nodes natals;
  - autorise: tests unitaires et evidence de validation du graphe;
  - interdit: execution metier du graphe, changement API, DB, frontend, pipeline natal ou contrats publics.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'implementation touche une route publique, une migration DB, le frontend, une dependance externe ou `build_natal_result`.
- Additional validation rules:
  - `build_natal_calculation_graph_definition()` retourne une `CalculationGraphDefinition` valide par le validator CS-225;
  - `graph_code` vaut `natal_chart_v1`;
  - les nodes calculatoires dependent seulement d'inputs declares ou d'outputs canoniques;
  - les projections compatibility/public dependent de surfaces canoniques et ne sont jamais sources de calcul;
  - `houses_runtime` depend de `julian_day`, `coordinates` et `house_system`;
  - `house_rulerships` depend de `houses_runtime` et `chart_objects`;
  - `chart_signature` depend des signes, maisons et aspects runtime;
  - `dominance` peut dependre des dignites, mais les dignites ne dependent pas de `dominance`;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le graphe natal devient la carte declarative des dependances de calcul. |
| Baseline Snapshot | yes | Le pipeline procedural et les contrats CS-225 doivent etre connus avant ajout. |
| Ownership Routing | yes | Definition, contrats, pipeline et tests ont des proprietaires distincts. |
| Allowlist Exception | yes | Les projections legacy restent des sorties de compatibilite, pas des sources de calcul. |
| Contract Shape | yes | Inputs, nodes, outputs, dependances et tags forment le coeur de la story. |
| Batch Migration | yes | Definition, tests, scans et evidence sont livres par lots controlables. |
| Reintroduction Guard | yes | Les scans bloquent execution de graphe, dependances externes et deltas API/DB/front. |
| Persistent Evidence | yes | Tests, scans et preuve finale doivent etre conserves dans le dossier CS-226. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_validator.py`;
  - `backend/app/domain/astrology/services/natal_calculation.py` comme pipeline procedural non migre.
- Runtime/domain artifacts:
  - definition `natal_chart_v1`;
  - inputs natals declares;
  - nodes canonical runtime;
  - projections compatibility/public taguees;
  - tests unitaires sous `backend/tests/unit/domain/astrology/`.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - `app.routes`, `app.openapi()` et `TestClient` sans delta public volontaire;
  - scans anti-dependance calculatoire vers projections.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la validite du graphe, ni l'ordre topologique, ni la neutralite runtime/OpenAPI.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `Get-Content backend/app/domain/astrology/runtime/calculation_graph_validator.py`;
  - recherche ciblee de `build_natal_result` dans `backend/app/domain/astrology/services/natal_calculation.py`;
  - recherche ciblee de `chart_objects`, `houses_runtime`, `dignities`, `dominance` et `chart_signature`;
  - `Select-String "RG-144|RG-145|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests CS-226 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend et pipeline natal.
- Expected invariant:
  - le pipeline natal reste procedural;
  - le graphe natal reste descriptif et non execute;
  - les projections legacy restent des outputs de compatibilite;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - nouveau module `natal_calculation_graph.py`;
  - tests unitaires et evidence CS-226;
  - exports package minimaux si le runtime les utilise deja;
  - Registry gap: un invariant dedie aux graphes de calcul natals pourra etre ajoute ulterieurement hors generation normale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Definition du graphe natal | `backend/app/domain/astrology/runtime/natal_calculation_graph.py` | route API, service monolithique, frontend |
| Contrats de graphe | `calculation_graph_contracts.py` | definition natal locale dupliquant les contrats |
| Validation declarative | `calculation_graph_validator.py` | `natal_calculation.py`, infra, DB |
| Execution procedurale | `natal_calculation.py` existant | runner de graphe CS-226 |
| Tests unitaires | `backend/tests/unit/domain/astrology/` | tests API opaques pour logique pure |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `natal_calculation.py` | ordre procedural | Pipeline natal hors migration CS-226. | Temporary; exit condition: migration story approved. |
| `public_natal_result` | projection publique | Sortie publique finale documentee comme projection. | Permanent pour cette story. |
| `planet_positions_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| `astral_points_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| `houses_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| `aspects_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| `dignity_results_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| `advanced_conditions_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| `fixed_star_conjunctions_projection` | compatibility projection | Surface legacy de sortie seulement. | Temporary; exit condition: cleanup story approved. |
| serializers et routes publics | contrats JSON existants | CS-226 ne change pas l'API publique. | Permanent pour cette story. |

Validation rule:

- Toute dependance calculatoire vers `planet_positions_projection`, `dignity_results_projection`, `advanced_conditions_projection` ou
  `public_natal_result` bloque l'implementation CS-226.

## 4f. Contract Shape

- Contract type:
  - `CalculationGraphDefinition` existant CS-225;
  - `CalculationInputDefinition` existant CS-225;
  - `CalculationNodeDefinition` existant CS-225;
  - enum ou constantes de node codes natals;
  - aucune nouvelle API HTTP.
- Required graph fields:
  - `graph_code`;
  - `version`;
  - `required_inputs`;
  - `nodes`.
- Fields:
  - `graph_code`;
  - `version`;
  - `required_inputs`;
  - `nodes`;
  - `code`;
  - `output_key`;
  - `depends_on`;
  - `optional_depends_on`;
  - `calculator`;
  - `tags`.
- Required fields:
  - `graph_code`;
  - `version`;
  - `required_inputs`;
  - `nodes`;
  - `code`;
  - `output_key`;
  - `depends_on`;
  - `calculator`.
- Optional fields:
  - `optional_depends_on`;
  - `tags`.
- Required inputs:
  - `birth_datetime`;
  - `timezone`;
  - `coordinates`;
  - `house_system`;
  - `zodiac_mode`;
  - `runtime_reference`;
  - `locale`;
  - `calculation_options`;
  - `prepared_birth_data`;
  - `julian_day`;
  - `effective_house_system`.
- Required canonical runtime nodes:
  - `prepare_birth_data`;
  - `planet_positions`;
  - `astral_points`;
  - `houses_raw`;
  - `houses_runtime`;
  - `signs_runtime`;
  - `chart_objects`;
  - `aspects_runtime`;
  - `house_positions`;
  - `house_rulerships`;
  - `fixed_star_conjunctions`;
  - `advanced_conditions`;
  - `motion_visibility_payloads`;
  - `dignities`;
  - `dominance`;
  - `chart_signature`;
  - `interpretation_input`.
- Required projection nodes:
  - `planet_positions_projection`;
  - `astral_points_projection`;
  - `houses_projection`;
  - `aspects_projection`;
  - `dignity_results_projection`;
  - `advanced_conditions_projection`;
  - `fixed_star_conjunctions_projection`;
  - `public_natal_result`.
- Required tags:
  - `canonical_runtime`;
  - `compatibility_projection`;
  - `public_projection`.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-226.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | dependances implicites dans `natal_calculation.py` | `natal_chart_v1` | aucun runtime | graph definition tests | import pur | CS-225 absent |
| 2 | surfaces legacy non classees dans le graphe | tags projection | aucun runtime | projection tests | no calculatory dependency | projection source |
| 3 | ordre procedural seul | validator topological order | aucun runtime | order tests | validator valid | cycle ou unknown dependency |
| 4 | preuve manuelle API neutre | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route ou schema modifie |

Completion rule: chaque batch conserve `pytest -q`, `app.routes`, `app.openapi()` et le pipeline natal procedural.

## 4h. Reintroduction Guard

- Guard target:
  - aucune execution de `natal_chart_v1` dans `build_natal_result`;
  - aucune dependance calculatoire vers une projection compatibility ou public;
  - aucun import FastAPI, SQLAlchemy, infra, settings, LLM ou frontend dans `natal_calculation_graph.py`;
  - aucun ajout `networkx`, `igraph`, `graphlib` ou dependance externe de graph processing;
  - aucun changement volontaire de `app.routes`, `app.openapi()` ou payload public.
- Guard mechanism:
  - test unitaire de validite du graphe natal;
  - test unitaire de dependances critiques;
  - test unitaire des tags projection;
  - AST guard ou scans cibles sur imports interdits;
  - `TestClient` smoke sur OpenAPI;
  - scan cible `rg -n "public_natal_result.*depends_on|dignity_results_projection.*depends_on" backend/app/domain/astrology/runtime -g "*.py"`.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`;
  - `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - `backend/tests/architecture` seulement si un guard d'imports transverse est ajoute.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`;
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-226-natal-calculation-graph-definition/evidence/validation.md` | Conserver tests, lint et resultats cibles CS-226. |
| API neutrality evidence | `_condamad/stories/CS-226-natal-calculation-graph-definition/evidence/openapi-routes.md` | Conserver `app.routes`, `app.openapi()` et TestClient. |
| Dependency proof | `_condamad/stories/CS-226-natal-calculation-graph-definition/evidence/natal-graph-dependencies.md` | Lister dependances principales et projections. |

## 5. Current State Evidence

- CS-225 fournit les contrats `CalculationGraphDefinition`, `CalculationNodeDefinition`, `CalculationInputDefinition` et le validator.
- Le pipeline natal est encore orchestre proceduralement dans `natal_calculation.py`.
- Les etapes positions, maisons, objets du theme, aspects, dignites, dominance et signature existent comme surfaces runtime.
- Les dependances entre ces etapes ne sont pas encore exprimees dans un graphe natal declaratif.
- Evidence 1: `_story_briefs/cs-226-natal-calculation-graph-definition.md` - brief source lu avant generation.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - IDs locaux consultes par recherche ciblee.

## 6. Target State

- `build_natal_calculation_graph_definition()` retourne `natal_chart_v1`.
- Les inputs natals minimaux et derives sont declares.
- Les nodes canonical runtime, dont `houses_raw`, documentent leurs dependances principales.
- Les noms de nodes et d'outputs restent alignes avec les surfaces runtime documentees du pipeline natal.
- Les projections legacy sont taguees `compatibility_projection` ou `public_projection`.
- `CalculationGraphValidator().validate(definition).is_valid` est vrai.
- Les tests prouvent l'ordre topologique et l'absence de dependance calculatoire vers une projection.
- Aucun comportement runtime, API, DB ou frontend ne change.

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
| RG-144 | local | `ChartObjectRuntimeData` reste le contrat canonique des objets exploitables; CS-226 le reference dans le graphe sans le remplacer. |
| RG-145 | local | Le moteur d'aspects reste consommateur de `chart_objects`; CS-226 declare cette dependance sans migrer le moteur. |
| RG-148 | local | Les payloads house/rulership restent des surfaces runtime existantes; CS-226 declare leurs dependances. |

Non-applicable examples:

- RG-147 dignity/dominance scoring: hors scope, aucun scoring n'est recalcule.
- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: hors scope, aucun fichier frontend, CSS ou build n'est touche.

Registry gap:

- Aucun guardrail global dedie a `natal_chart_v1` n'existe encore; ne pas enrichir le registre pendant cette generation normale.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Le graphe `natal_chart_v1` est declare. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`. |
| AC2 | La definition passe le validator CS-225. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`; validator result. |
| AC3 | Les inputs natals minimaux sont declares. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`. |
| AC4 | Les dependances critiques sont explicites. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`; AST guard. |
| AC5 | Les projections legacy ne sont pas sources de calcul. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`; scan projection. |
| AC6 | Aucun comportement runtime n'est modifie. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`; AST guard; service scan. |
| AC7 | Aucune API publique ne change. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; `app.routes`; `app.openapi()`; `TestClient`. |
| AC8 | Les inputs derives sont declares. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`. |
| AC9 | Les tests documentent l'ordre topologique. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`. |
| AC10 | Les tests documentent les dependances principales. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`. |
| AC11 | Les surfaces runtime documentees sont couvertes. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`; runtime evidence. |

## 8. Implementation Tasks

- [x] Task: creer `natal_calculation_graph.py` avec commentaire global et docstrings en francais. (AC: AC1)
- [x] Task: ajouter les codes de nodes natals selon les conventions runtime existantes. (AC: AC1, AC9)
- [x] Task: declarer les inputs `birth_datetime`, `timezone`, `coordinates`, `house_system`, `zodiac_mode`, `runtime_reference` et `locale`. (AC: AC3)
- [x] Task: declarer les inputs derives `prepared_birth_data`, `julian_day` et `effective_house_system`. (AC: AC8)
- [x] Task: declarer les nodes canonical runtime du pipeline natal, incluant la transition `houses_raw` vers `houses_runtime`. (AC: AC1, AC4, AC9, AC11)
- [x] Task: declarer les projections compatibility/public avec tags dedies. (AC: AC5)
- [x] Task: verifier par test que `houses_runtime`, `house_rulerships` et `chart_signature` ont les dependances attendues. (AC: AC4, AC10)
- [x] Task: verifier par test l'alignement entre la definition et les noms de surfaces runtime documentees. (AC: AC11)
- [x] Task: verifier par test qu'aucun node calculatoire ne depend d'une projection. (AC: AC5)
- [x] Task: ajouter la validation `CalculationGraphValidator().validate(definition)`. (AC: AC2)
- [x] Task: ajouter les preuves `app.routes`, `app.openapi()` et `TestClient` de neutralite API. (AC: AC7)
- [x] Task: collecter l'evidence finale dans le dossier CS-226. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les contrats CS-225 au lieu de recreer des dataclasses de graphe.
- Reutiliser `CalculationGraphValidator` pour prouver la validite.
- Reutiliser les noms de surfaces runtime existants du pipeline natal.
- Ne pas dupliquer `ChartObjectRuntimeData`, les payloads house/rulership, aspects, dignites, dominance ou signature.
- Ne pas creer une seconde logique de calcul astrologique.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter `networkx`, `igraph`, `graphlib` ou dependance externe de graph processing.
- Ne pas creer de runner de graphe en production.
- Ne pas migrer `build_natal_result`.
- Ne pas faire dependre un node calculatoire d'une projection compatibility/public.
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

- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py`.
- `backend/app/domain/astrology/services/natal_calculation.py`.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-144|RG-145|RG-148`.

## 13. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `_condamad/stories/CS-226-natal-calculation-graph-definition/evidence/validation.md`.
- `_condamad/stories/CS-226-natal-calculation-graph-definition/evidence/openapi-routes.md`.
- `_condamad/stories/CS-226-natal-calculation-graph-definition/evidence/natal-graph-dependencies.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`.

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
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

Run anti-regression scans:

```powershell
rg -n "natal_chart_v1|build_natal_calculation_graph_definition|compatibility_projection" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "public_natal_result.*depends_on|dignity_results_projection.*depends_on" backend/app/domain/astrology/runtime -g "*.py"
rg -n "networkx|igraph|graphlib|from app\\.api|from app\\.infra|sqlalchemy|fastapi" backend/app/domain/astrology/runtime/natal_calculation_graph.py
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

If the dedicated API neutrality test does not exist, add a focused TestClient test that records `app.routes` and `app.openapi()` for CS-226 evidence.

## 16. Regression Risks

- Une dependance oubliee peut rendre l'ordre topologique trompeur.
- Une projection legacy peut redevenir source de calcul si elle n'est pas testee.
- Une confusion entre definition declarative et execution peut migrer trop tot `build_natal_result`.
- Un nom de node vague peut affaiblir la documentation executable du pipeline natal.

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

## 18. CS-226 Final Evidence Template

```markdown
## CS-226 Final Evidence

### Natal Graph
- Declared natal_chart_v1 calculation graph.
- Declared inputs, canonical runtime nodes and projection nodes.
- Graph validates without cycles or unknown dependencies.

### Dependency Proof
- houses_runtime depends on julian_day, coordinates and house_system.
- house_rulerships depends on houses_runtime and chart_objects.
- chart_signature depends on signs, houses and aspects runtime.

### Compatibility
- No runtime execution changed.
- Legacy surfaces are tagged as projections.
- No API, DB or frontend changes.

### Commands
- ruff format .
- ruff check .
- pytest -q
- targeted natal graph tests
```

## 19. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-226-natal-calculation-graph-definition.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the recent CS-225 validated structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.
- Last validation attempt failed before this final correction with:
  - `Allowlist / Exception Register must not use wildcards`;
  - `AC6 touches a runtime contract and must include runtime evidence`.
- Final rerun not launched because this session limits each validation command to two attempts.

## 20. References

- `_story_briefs/cs-226-natal-calculation-graph-definition.md`.
- `_condamad/stories/regression-guardrails.md` targeted IDs `RG-144|RG-145|RG-148`.
- `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md` structure reference.
