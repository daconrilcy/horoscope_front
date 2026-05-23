# Story CS-228 migrate-natal-runtime-to-calculation-graph: Migrate Natal Runtime to Calculation Graph
Status: done

## 1. Objective

Faire produire `build_natal_result` par `CalculationGraphRunner` et la definition `natal_chart_v1`, en conservant le contrat public actuel du theme natal.
La story deplace l'orchestration metier vers le graphe sans changer l'API, le frontend, la DB, les scores ou la doctrine astrologique.

## 2. Trigger / Source

- Source type: architecture-runtime-migration.
- Source reference: `_story_briefs/cs-228-migrate-natal-runtime-to-calculation-graph.md`.
- Reason for change: CS-225 a CS-227 fournissent contrats, definition `natal_chart_v1` et runner; le pipeline natal doit maintenant les consommer.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story migre l'orchestration backend-domain, sans nouvelle route, schema public, DB, frontend, persistance ou feature flag permanent.

## References

- `_story_briefs/cs-228-migrate-natal-runtime-to-calculation-graph.md`.
- `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md`.
- `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md`.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-144|RG-145|RG-147|RG-148`.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`.
- In scope:
  - creer les adapters de nodes natals qui deleguent aux calculateurs existants;
  - creer `build_natal_calculation_node_registry`;
  - brancher `build_natal_result` sur `CalculationGraphRunner` et `natal_chart_v1`;
  - creer ou isoler `NatalResultAssembler`;
  - produire les outputs canoniques necessaires a `NatalResult`;
  - conserver `chart_objects` comme source runtime canonique interne;
  - conserver les projections historiques publiques et internes controlees;
  - propager les erreurs de node avec le code de node;
  - ajouter tests unitaires, integration et architecture;
  - verifier l'absence de delta OpenAPI, DB et frontend.
- Out of scope:
  - changer les contrats API publics;
  - changer le frontend;
  - ajouter transits, synastrie, progressions, directions, returns ou profections;
  - changer les scores, orbes, dignites, dominance, aspects, fixed stars ou doctrine astrologique;
  - ajouter une persistance du graphe;
  - parallelliser les calculs;
  - introduire un feature flag permanent;
  - ajouter une dependance externe.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas dupliquer les calculateurs astrologiques dans les adapters de nodes;
  - ne pas utiliser les projections legacy comme sources de verite calculatoires;
  - ne pas exposer `chart_objects` dans le JSON public sans story API dediee.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story remplace l'orchestration procedurale interne par une execution de graphe backend-domain avec compatibilite publique stable.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: `build_natal_result` prepare les inputs, execute `natal_chart_v1` et assemble `NatalResult`;
  - autorise: nouveaux adapters, registry natal et assembler sous le runtime ou service astrology;
  - autorise: legacy path prive temporaire uniquement borne, documente et compare par tests;
  - autorise: evidence de neutralite API via `app.routes`, `app.openapi()` et `TestClient`;
  - interdit: changement API, DB, frontend, doctrine, scores, dependance externe ou feature flag permanent.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'implementation touche une route publique, une migration DB, le frontend, une dependance externe ou une suppression de champ public.
- Additional validation rules:
  - `build_natal_result` utilise `CalculationGraphRunner` avec la definition `natal_chart_v1`;
  - les nodes natals sont resolus par `build_natal_calculation_node_registry`;
  - les adapters lisent leurs inputs depuis `CalculationGraphContext` et retournent un output unique;
  - les adapters appellent les calculateurs existants sans recopier leur logique;
  - `NatalResultAssembler` lit les outputs canoniques et construit les projections historiques;
  - `chart_objects` reste la source runtime canonique interne;
  - les projections legacy restent sorties de compatibilite et ne deviennent pas sources calculatoires;
  - les erreurs de node incluent le code de node dans un message stable;
  - `build_natal_result` ne contient plus une longue sequence d'orchestration metier;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `natal_chart_v1` et `chart_objects` deviennent la source d'orchestration et de runtime interne. |
| Baseline Snapshot | yes | Le pipeline procedural, CS-225, CS-226 et CS-227 doivent etre connus avant migration. |
| Ownership Routing | yes | Adapters, registry, runner, assembler, projections et API ont des owners distincts. |
| Allowlist Exception | yes | Un legacy path temporaire reste possible seulement avec comparaison et sortie planifiee. |
| Contract Shape | yes | Registry, adapters, outputs canoniques, assembler et erreurs structurent la migration. |
| Batch Migration | yes | Adapters, registry, branchement, assemblage, tests et preuves sont livres par lots. |
| Reintroduction Guard | yes | Les scans bloquent orchestration procedurale, duplication de calculateurs et deltas publics. |
| Persistent Evidence | yes | Tests, scans, comparaison et preuve OpenAPI doivent etre conserves dans le dossier CS-228. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_runner.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_registry.py`;
  - `backend/app/domain/astrology/runtime/natal_result_assembler.py`;
  - `backend/app/domain/astrology/natal_calculation.py` comme facade mince.
- Runtime/domain artifacts:
  - adapters de nodes natals;
  - registry explicite de calculateurs;
  - execution `natal_chart_v1`;
  - outputs canoniques;
  - assembler `NatalResult`;
  - projections historiques conservees;
  - tests unitaires, integration et architecture.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - `pytest -q backend/tests/integration/astrology`;
  - `app.routes`, `app.openapi()` et `TestClient` sans delta public volontaire.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni l'execution runtime de `natal_chart_v1`, ni la compatibilite `NatalResult`, ni la propagation controlee des erreurs de node.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/natal_calculation.py`;
  - `Get-Content backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `Get-Content backend/app/domain/astrology/runtime/calculation_graph_runner.py`;
  - recherche ciblee `def build_natal_result|chart_objects =|FixedStarConjunctionCalculator|DignityPayloadEnricher|DominancePayloadEnricher`;
  - recherche ciblee `CalculationGraphRunner|build_natal_calculation_graph_definition|CalculationNodeRegistry`;
  - `Select-String "RG-144|RG-145|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests CS-228 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations et frontend;
  - comparaison golden ou integration entre sorties publiques avant/apres.
- Expected invariant:
  - `build_natal_result` retourne toujours `NatalResult`;
  - `chart_objects`, `houses` et `aspects` restent produits;
  - les projections historiques restent disponibles;
  - `chart_objects` reste absent du JSON public;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - nouveaux modules `natal_calculation_nodes.py`, `natal_calculation_registry.py` et `natal_result_assembler.py`;
  - reduction de l'orchestration dans `natal_calculation.py`;
  - tests et evidence CS-228;
  - Registry gap: un invariant global dedie au branchement production de `natal_chart_v1` pourra etre ajoute ulterieurement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Orchestration du pipeline natal | `natal_chart_v1` + `CalculationGraphRunner` | sequence longue dans `build_natal_result` |
| Resolution des nodes | `natal_calculation_registry.py` | import dynamique, global lookup, route API |
| Adaptation des calculateurs | `natal_calculation_nodes.py` | duplication d'algorithmes metier |
| Assemblage compatible | `natal_result_assembler.py` | adapters de nodes, API, frontend |
| Facade publique domaine | `natal_calculation.py` | orchestration metier croissante |
| Projection API publique | serializers/adapters existants | runtime interne du graphe |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `natal_calculation.py` | preparation inputs | Facade publique domaine conservee. | Permanent pour cette story. |
| `natal_calculation.py` | legacy path prive temporaire | Comparaison de non-regression seulement. | Temporary; exit condition: CS-229 cleanup story or same PR removal. |
| serializers et routes publics | projections historiques | Contrat public conserve sans exposition de `chart_objects`. | Permanent pour cette story. |
| tests golden et snapshots | sorties historiques | Preuve de compatibilite. | Borne aux tests et evidence. |

Validation rule:

- Toute dependance calculatoire vers `planet_positions_projection`, `dignity_results_projection`, `advanced_conditions_projection` ou
  `public_natal_result` bloque l'implementation CS-228.

## 4f. Contract Shape

- Contract type:
  - adapters de nodes Python types;
  - registry explicite `CalculationNodeRegistry`;
  - runner `CalculationGraphRunner`;
  - assembler `NatalResult`;
  - aucune nouvelle API HTTP.
- Required functions/classes:
  - `build_natal_calculation_node_registry`;
  - adapters de nodes pour preparation, positions, points astraux, maisons, signes, chart objects, aspects, rulerships, fixed stars, conditions, dignites, dominance et signature;
  - `NatalResultAssembler`;
  - facade `build_natal_result` amincie.
Fields:

- `graph_code`;
- `node_code`;
- `calculator`;
- `input_keys`;
- `output_key`;
- `outputs`;
- `chart_objects`;
- `houses_runtime`;
- `aspects_runtime`;
- `dignities`;
- `dominance`;
- `chart_signature`;
- `legacy_projection`;
- `error_message`.

Required fields:

- `graph_code`;
- `node_code`;
- `calculator`;
- `output_key`;
- `outputs`;
- `chart_objects`;
- `houses_runtime`;
- `aspects_runtime`;
- `NatalResult`.

Optional fields:

- `legacy_projection`;
- `temporary_legacy_comparison_path`;
- `error_message` peut etre vide pour un node reussi.

- Required output surfaces:
  - `chart_objects`;
  - `houses_runtime`;
  - `aspects_runtime`;
  - `house_positions`;
  - `house_rulerships`;
  - `fixed_star_conjunctions`;
  - `advanced_conditions`;
  - `dignities`;
  - `dominance`;
  - `chart_signature`;
  - projections historiques necessaires a `NatalResult`.
- Required behavior:
  - chaque adapter consomme `CalculationGraphContext`;
  - chaque adapter retourne un output unique;
  - le registry mappe les calculator codes de CS-226 vers les adapters;
  - l'assembler echoue avec un message stable lorsqu'un output obligatoire manque;
  - une erreur de node est remontee avec `node_code`;
  - le JSON public reste compatible.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-228.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | calculateurs appeles en ligne | adapters de nodes | tests factices | unit adapters | delegation proof | logique dupliquee |
| 2 | resolution implicite | registry natal | runner | registry tests | no dynamic import | calculator inconnu |
| 3 | ordre procedural | `natal_chart_v1` | `build_natal_result` | graph execution | runner evidence | ordre divergent |
| 4 | assemblage disperse | `NatalResultAssembler` | service natal | contract tests | missing output error | projection manquante |
| 5 | legacy path actif | graph path canonique | aucun public | comparison tests | bounded temporary path | divergence publique |
| 6 | preuve manuelle API | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route/schema modifie |

Completion rule: chaque batch conserve `pytest -q`, `app.routes`, `app.openapi()`, `chart_objects` interne et aucune modification frontend/DB.

## 4h. Reintroduction Guard

- Guard target:
  - aucune longue sequence d'orchestration metier dans `build_natal_result`;
  - aucun adapter de node ne recopie un calculateur existant;
  - aucune resolution dynamique par `importlib.import_module`, `eval`, `globals()` ou lookup magique;
  - aucune dependance calculatoire vers une projection compatibility ou public;
  - aucun changement volontaire de `app.routes`, `app.openapi()` ou payload public;
  - aucune exposition de `chart_objects` dans le JSON public;
  - aucun changement DB, migration, frontend ou feature flag permanent.
- Guard mechanism:
  - tests unitaires des adapters et du registry;
  - tests d'integration `build_natal_result`;
  - tests de contrat `NatalResult` et JSON public;
  - AST guard ou scans cibles sur orchestration procedurale, imports dynamiques et projections;
  - `TestClient` smoke sur OpenAPI;
  - scan cible `rg -n "natal_result\\.planet_positions|natal_result\\.dignity_results|natal_result\\.advanced_conditions"`
    sur `backend/app/domain/astrology/runtime` et `backend/app/domain/astrology/natal_calculation.py`.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`;
  - `backend/tests/unit/domain/astrology/test_natal_result_contract.py`;
  - `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - `backend/tests/integration/astrology`.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`;
  - chemin complet `pytest -q backend/tests/integration/astrology`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/validation.md` | Conserver tests, lint et resultats cibles CS-228. |
| API neutrality evidence | `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/openapi-routes.md` | Conserver OpenAPI et routes. |
| Graph migration proof | `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/natal-graph-migration.md` | Prouver graph et compatibilite. |

## 5. Current State Evidence

- CS-225 fournit les contrats `CalculationGraphDefinition`, nodes, inputs, statuts et validator.
- CS-226 declare `natal_chart_v1` comme definition du pipeline natal.
- CS-227 fournit `CalculationGraphRunner`, `CalculationGraphContext` et `CalculationNodeRegistry`.
- Le brief indique que `build_natal_result` orchestre encore preparation, positions, maisons, signes, chart objects, aspects, dignites, dominance et projections.
- Evidence 1: `_story_briefs/cs-228-migrate-natal-runtime-to-calculation-graph.md` - demande une migration progressive sans changement public.
- Evidence 2: `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md` - contrats de graphe prets.
- Evidence 3: `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md` - definition `natal_chart_v1` prete.
- Evidence 4: `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md` - runner et registry prets.
- Evidence 5: `backend` existe dans l'arborescence courante.
- Evidence 6: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` existe.
- Evidence 7: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` existe.

## 6. Target State

- `build_natal_result` reste l'entree domaine mais devient mince.
- Les inputs natals sont prepares puis injectes dans `CalculationGraphContext`.
- `CalculationGraphRunner` execute `natal_chart_v1`.
- `build_natal_calculation_node_registry` resout tous les calculator codes natals.
- Les adapters de nodes deleguent aux calculateurs existants.
- `NatalResultAssembler` produit un `NatalResult` complet.
- `chart_objects` reste la source runtime canonique interne.
- Les projections historiques restent disponibles.
- Une erreur de node indique le code de node.
- Les tests prouvent compatibilite publique, execution graph et absence de delta API/DB/frontend.

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
| RG-144 | local | `ChartObjectRuntimeData` reste le contrat canonique; les nodes et l'assembler ne le remplacent pas par les collections historiques. |
| RG-145 | local | Le moteur d'aspects reste consommateur des objets du theme et de leurs capabilities, pas des anciennes collections directes. |
| RG-147 | local | Dignity et dominance restent des payloads et resultats controles; les adapters ne recalculent pas les scores. |
| RG-148 | local | House position et rulership restent projetes depuis les resolvers/helpers existants, sans second resolver local. |

Non-applicable examples:

- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: hors scope, aucun fichier React, CSS ou build n'est touche.
- Auth/i18n guardrails: hors scope, aucune authentification ou localisation n'est modifiee.

Registry gap:

- Aucun guardrail global dedie a l'execution production de `natal_chart_v1` n'existe encore; ne pas enrichir le registre pendant cette generation normale.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Graph runner execute `natal_chart_v1`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`; AST. |
| AC2 | Les nodes natals sont resolus par registry explicite. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`; registry assertions. |
| AC3 | Les adapters deleguent aux calculateurs existants sans duplication. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`; AST. |
| AC4 | `build_natal_result` retourne un `NatalResult` complet. | `pytest -q backend/tests/integration/astrology`; runtime assertions `chart_objects`, `houses`, `aspects`. |
| AC5 | `chart_objects` reste source runtime canonique interne. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`; AST guard. |
| AC6 | Les projections historiques restent disponibles. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`; runtime projection assertions. |
| AC7 | Les projections legacy ne sont pas sources calculatoires. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`; scan projection. |
| AC8 | Une erreur de node inclut le code de node. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`; node_code assertion. |
| AC9 | `build_natal_result` ne contient plus une longue sequence procedurale. | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`; AST. |
| AC10 | Le graphe execute correspond a `natal_chart_v1`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`; graph_code assertion. |
| AC11 | `chart_objects` reste absent du JSON public. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`; `app.openapi()`; `TestClient`. |
| AC12 | Aucun changement OpenAPI involontaire n'est introduit. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; `app.routes`; `app.openapi()`. |
| AC13 | Aucun changement DB ou frontend n'est introduit. | `pytest -q backend/tests/integration/astrology`; AST guard; diff adjacent DB/frontend. |
| AC14 | Les tests golden existants restent verts. | `pytest -q backend/tests`; targeted natal graph tests. |
| AC15 | L'evidence finale CS-228 est persistee. | from story dir, `rg -n "CS-228 Final Evidence" evidence/validation.md`. |

## 8. Implementation Tasks

- [ ] Task: lire les contrats CS-225, la definition CS-226, le runner CS-227 et le service natal actuel. (AC: AC1, AC10)
- [ ] Task: creer `natal_calculation_nodes.py` avec commentaire global et docstrings en francais. (AC: AC3)
- [ ] Task: ajouter les adapters de nodes natals pour les calculateurs existants. (AC: AC3, AC4)
- [ ] Task: creer `natal_calculation_registry.py` et `build_natal_calculation_node_registry`. (AC: AC2)
- [ ] Task: creer ou isoler `NatalResultAssembler` avec commentaire global et docstrings en francais. (AC: AC4, AC6)
- [ ] Task: brancher `build_natal_result` sur `CalculationGraphRunner` et `natal_chart_v1`. (AC: AC1, AC10)
- [ ] Task: conserver les projections historiques dans l'assembler sans les utiliser comme sources calculatoires. (AC: AC6, AC7)
- [ ] Task: propager les erreurs de node avec le code de node. (AC: AC8)
- [ ] Task: reduire l'orchestration procedurale restante dans `build_natal_result`. (AC: AC9)
- [ ] Task: ajouter les tests unitaires d'execution graph, registry, adapters et erreur de node. (AC: AC1, AC2, AC3, AC8, AC10)
- [ ] Task: ajouter les tests d'integration du theme natal complet. (AC: AC4, AC14)
- [ ] Task: renforcer les tests de contrat `NatalResult`, JSON public et `chart_objects`. (AC: AC5, AC6, AC11)
- [ ] Task: ajouter ou renforcer l'AST guard anti-orchestration procedurale et anti-projections comme sources. (AC: AC7, AC9)
- [ ] Task: ajouter les preuves `app.routes`, `app.openapi()` et `TestClient` de neutralite API. (AC: AC11, AC12)
- [ ] Task: collecter l'evidence finale dans le dossier CS-228. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser `CalculationGraphDefinition`, `CalculationGraphRunner`, `CalculationGraphContext` et `CalculationNodeRegistry`.
- Reutiliser `build_natal_calculation_graph_definition` et `natal_chart_v1`.
- Reutiliser les calculateurs existants pour positions, maisons, aspects, fixed stars, conditions, dignites, dominance et signature.
- Reutiliser `ChartObjectRuntimeData`, capabilities et payloads.
- Reutiliser les projections historiques existantes via un assembler ou projector borne.
- Ne pas recreer une logique de calcul astrologique dans les adapters.
- Ne pas creer une seconde definition du graphe natal.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter de dependance externe de graph processing ou workflow.
- Ne pas exposer `chart_objects` dans le JSON public.
- Ne pas faire dependre un node calculatoire d'une projection compatibility/public.
- Ne pas utiliser `importlib.import_module`, `eval`, `globals()` ou lookup magique.
- Ne pas ajouter de legacy path public ou non borne.
- Ne pas conserver deux chemins actifs sans comparaison, borne temporelle et story de fermeture.
- Ne pas ajouter de fallback silencieux ou feature flag permanent.
- Ne pas changer la doctrine astrologique, les scores, les orbes ou les golden cases.

## 11. Generated Contract Check

- Capture before:
  - `app.routes`;
  - `app.openapi()`;
  - un smoke `TestClient` sur OpenAPI;
  - un endpoint natal public couvert par les tests existants.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code, schema public ou cle JSON publique ne change volontairement.

## 12. Files to Inspect First

- `backend/app/domain/astrology/natal_calculation.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-144|RG-145|RG-147|RG-148`.

## 13. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/natal_calculation.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_registry.py`.
- `backend/app/domain/astrology/runtime/natal_result_assembler.py`.
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/validation.md`.
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/openapi-routes.md`.
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/natal-graph-migration.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`.
- `backend/tests/integration/astrology/test_natal_calculation_graph_integration.py`.

Files not expected to change:

- `frontend/src`.
- `backend/alembic`.
- `backend/app/api`.
- `backend/app/infra` hors lecture de configuration deja existante.

## 14. Dependency Policy

New dependencies: none.
Justification: no dependency changes are authorized.
- New dependencies: none.
- Justification: no dependency changes are authorized.

## 15. Validation Plan

Run all Python commands from repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
pytest -q backend/tests/integration/astrology
```

Run anti-regression scans:

```powershell
rg -n "def build_natal_result|CalculationGraphRunner|natal_chart_v1" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "natal_result\.planet_positions|natal_result\.dignity_results|natal_result\.advanced_conditions" backend/app/domain/astrology -g "*.py"
rg -n "importlib|eval\(|globals\(|networkx|igraph|graphlib|celery|prefect|airflow" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "chart_objects" backend/app/api frontend/src
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

The dedicated API neutrality evidence must name `app.routes`, `app.openapi()` and `TestClient`.

## 16. Regression Risks

- Un adapter peut dupliquer un calculateur existant au lieu de deleguer.
- Un output obligatoire peut manquer et produire un `NatalResult` partiel.
- Une projection legacy peut redevenir source calculatoire.
- Le JSON public peut exposer `chart_objects` par erreur.
- Un legacy path temporaire peut rester actif sans borne de retrait.
- La reduction de `build_natal_result` peut oublier une projection historique.

## 17. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only CS-228.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Implementer le plus petit delta coherent.
- Garder les commentaires globaux et docstrings en francais dans les nouveaux fichiers applicatifs.
- Ne pas utiliser de style inline, CSS ou frontend: aucun fichier frontend n'est attendu.
- Ne pas creer de `requirements.txt`.
- Executer les validations apres activation du venv.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in story evidence.
- Do not preserve legacy behavior through an unbounded fallback, shim or compatibility layer.
- Conserver dans l'evidence les commandes lancees, les resultats de tests, les scans et la preuve `app.routes` / `app.openapi()`.

## 18. CS-228 Final Evidence Template

```markdown
## CS-228 Final Evidence

### Graph Execution
- build_natal_result uses natal_chart_v1 through CalculationGraphRunner.
- Natal node registry is explicit.
- Node adapters reuse existing calculators.

### Runtime Outputs
- chart_objects remains canonical internal runtime.
- Houses, aspects, dignities, dominance, fixed stars and signature are produced through graph outputs.
- Legacy projections remain available.

### Compatibility
- No public API or OpenAPI delta.
- chart_objects remains excluded from public JSON.
- Existing golden and integration tests pass.

### Guardrails
- No new procedural orchestration sequence in build_natal_result.
- No calculator depends on legacy projections as source of truth.
- Node failures include node code.

### Commands
- ruff format .
- ruff check .
- pytest -q
- targeted graph/natal tests
```

## 19. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-228-migrate-natal-runtime-to-calculation-graph.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the recent CS-225 to CS-227 structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.
- Story validation result after review fix cycle: PASS.
- Strict lint result after review fix cycle: PASS.
- Redaction review fixed path consistency, AC evidence concreteness and validation-plan command scope.

## 20. References

- Source brief: `_story_briefs/cs-228-migrate-natal-runtime-to-calculation-graph.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-144`, `RG-145`, `RG-147`, `RG-148`).
- Previous story: `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md`.

## 21. Implementation Evidence

- Status updated to `done` on 2026-05-23 after a fresh implementation review found no actionable issue.
- Evidence files:
  - `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/validation.md`;
  - `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/openapi-routes.md`;
  - `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/evidence/natal-graph-migration.md`.
- AC traceability is recorded in `evidence/validation.md`.
- Final validations:
  - `ruff check backend` -> OK;
  - `python -B -m pytest -q backend/tests` -> `833 passed, 201 deselected`;
  - `python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py` -> `2 passed`.
