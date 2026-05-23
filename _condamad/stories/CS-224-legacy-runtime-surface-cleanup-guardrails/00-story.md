# Story CS-224 legacy-runtime-surface-cleanup-guardrails: Verrouiller les surfaces runtime legacy du theme natal
Status: done

## 1. Objective

Faire de `NatalResult.chart_objects` la surface runtime canonique pour les nouveaux consommateurs du theme natal.
Les collections historiques restent disponibles comme projections de compatibilite ou resultats chart-level, sans redevenir sources metier paralleles.

## 2. Trigger / Source

- Source type: architecture-guardrail.
- Source reference: `_story_briefs/cs-224-legacy-runtime-surface-cleanup-guardrails.md`.
- Reason for change: CS-217 a cree `ChartObjectRuntimeData`; CS-218 a migre les aspects; CS-219 a rattache motion/visibility;
  CS-220 a rattache dignity/dominance; CS-221 a rattache house/rulership; CS-222 a rattache fixed stars; CS-223 prepare l'input interpretation.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md` et le cheatsheet demande ne sont pas presents; les scripts de validation existent.
- Source-alignment review: la story consolide et documente les surfaces runtime; elle ne casse pas API/front, ne change pas la doctrine et ne migre pas un nouveau domaine.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`
- In scope:
  - inventorier les surfaces runtime du theme natal;
  - documenter `chart_objects` comme source canonique interne;
  - documenter `planet_positions`, `astral_points`, `houses`, `angles`, `dignity_results`, `advanced_conditions` et
    `fixed_star_conjunctions` comme projections de compatibilite;
  - documenter `aspects` et `dominance_result` comme resultats chart-level controles;
  - ajouter ou renforcer les tests d'architecture anti-consommation directe des surfaces historiques;
  - ajouter ou renforcer les tests anti-eligibilite par `object_type`;
  - verifier la coherence entre projections historiques et `chart_objects`;
  - supprimer ou consolider uniquement les builders/adapters manifestement morts avec preuve ciblee.
- Out of scope:
  - casser l'API publique ou les contrats front;
  - supprimer brutalement une collection historique;
  - modifier les scores, orbes, dignites, dominance, aspects, fixed star contacts ou doctrine astrologique;
  - changer les prompts LLM, les routes FastAPI, la DB, les migrations ou le frontend;
  - creer un projection builder monolithique sans duplication concrete a reduire.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas utiliser les collections historiques comme source metier dans les nouveaux calculateurs;
  - ne pas introduire de selection metier par `object_type`, code nominal ou famille planetaire.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story classe les surfaces historiques et autorise le retrait borne de builders/adapters morts uniquement avec preuve de non-usage.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: `chart_objects` devient la source canonique documentee pour nouveaux consommateurs;
  - autorise: les surfaces historiques sont marquees comme projections de compatibilite ou resultats chart-level;
  - autorise: des tests d'architecture bloquent les nouvelles lectures directes non autorisees;
  - autorise: suppression de code mort uniquement avec preuve `rg`, test ou audit cible;
  - interdit: changer volontairement schema public, OpenAPI, routes, DB, frontend, prompts ou sorties historiques.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une suppression touche une sortie publique, un contrat front/API, une doctrine astrologique, une dependance ou une migration DB.
- Additional validation rules:
  - les calculateurs nouveaux lisent `NatalResult.chart_objects` ou une projection explicitement construite depuis `chart_objects`;
  - les usages directs de `planet_positions`, `astral_points`, `advanced_conditions`, `dignity_results` et `fixed_star_conjunctions` sont allowlistes;
  - les usages par projection API, serializer public, fixture, debug snapshot ou bridge de migration sont nommes et bornes;
  - les branches `object_type ==`, `.object_type ==` et `ChartObjectType.PLANET|ANGLE|FIXED_STAR` sont bloquees hors owners allowlistes;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta public volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `NatalResult.chart_objects` est la source canonique interne. |
| Baseline Snapshot | yes | Les surfaces historiques et usages actuels doivent etre connus avant nettoyage. |
| Ownership Routing | yes | Calculateurs, projection, API, tests et debug ont des proprietaires distincts. |
| Allowlist Exception | yes | Tout usage legacy conserve doit etre nomme et justifie. |
| Contract Shape | yes | `NatalResult` reste un contrat de transition avec projections publiques. |
| Batch Migration | yes | Documentation, tests, scans et cleanup sont separes en lots controlables. |
| Reintroduction Guard | yes | Les guards doivent bloquer les nouvelles sources paralleles. |
| Persistent Evidence | yes | Baseline, scans, tests et preuve finale doivent etre conserves dans le dossier CS-224. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects`;
  - `ChartObjectRuntimeData.capabilities`;
  - `ChartObjectRuntimeData.payloads`;
  - resultats chart-level deja calcules lorsque la surface est globale, comme `aspects` et `dominance_result`.
- Runtime/domain artifacts:
  - `docs/architecture/astrology-runtime-surfaces.md`;
  - tests d'inventaire documentaire;
  - tests de coherence des projections historiques;
  - tests d'architecture AST ou scans cibles;
  - preuves `app.routes`, `app.openapi()` et `TestClient` sans delta public volontaire.
- Secondary evidence:
  - scans anti-legacy direct, anti-`object_type`, anti-builders specialises et anti-seuils magiques;
  - `ruff format .`, `ruff check .` et `pytest -q` apres activation du venv.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la coherence runtime des projections, ni la conservation du contrat `NatalResult`, ni l'absence de delta OpenAPI.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/chart_object_runtime_builder.py`;
  - recherche ciblee des definitions de `NatalResult`;
  - scans cibles sur `planet_positions`, `astral_points`, `houses`, `angles`, `dignity_results`, `advanced_conditions`, `fixed_star_conjunctions`;
  - scans cibles sur `object_type ==`, `.object_type ==`, `ChartObjectType.PLANET`, `ChartObjectType.ANGLE` et `ChartObjectType.FIXED_STAR`;
  - `Select-String "RG-144|RG-145|RG-146|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes scans cibles apres implementation;
  - tests CS-224 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend et providers LLM.
- Expected invariant:
  - `chart_objects` est documente comme source canonique;
  - les surfaces historiques restent exposees mais non sources metier;
  - les calculateurs nouveaux consomment les capacites et payloads;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - documentation d'architecture;
  - tests d'architecture et de coherence;
  - module de projection centralise uniquement si une duplication concrete est retiree;
  - suppression de code mort prouvee;
  - Registry gap: un invariant dedie CS-224 pourra etre ajoute ulterieurement hors generation normale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Source runtime interne | `NatalResult.chart_objects` | nouveaux calculateurs branches sur collections historiques |
| Documentation surfaces | `docs/architecture/astrology-runtime-surfaces.md` | commentaires disperses uniquement |
| Projections de compatibilite | projector ou builder central nomme | calculateurs metier |
| Sorties API/front | serializers/adapters publics existants | domaine runtime canonique |
| Guards architecture | `backend/tests/architecture` | tests unitaires opaques sans scan borne |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| projection builders nommes | lectures historiques | Compatibilite API/front et transition. | Temporary; exit condition: approved removal story validates no public consumer. |
| serializers API publics | projections historiques | Contrat public conserve. | Permanent tant que le contrat public existe. |
| fixtures et debug snapshots | surfaces historiques | Non-regression et diagnostic. | Borne aux tests/debug. |

Validation rule:

- Toute lecture directe nouvelle de `planet_positions`, `astral_points`, `advanced_conditions`, `dignity_results` ou
  `fixed_star_conjunctions` depuis un calculateur metier bloque l'implementation.

## 4f. Contract Shape

- Contract type:
  - documentation markdown d'architecture;
  - tests d'architecture deterministes;
  - allowlists explicites avec chemins et raisons;
  - aucune nouvelle API HTTP.
- Fields:
  - surface;
  - status;
  - target source;
  - calculator access;
  - owner;
  - comment;
  - removal classification;
  - allowlist reason.
- Required documented surfaces:
  - `chart_objects`;
  - `planet_positions`;
  - `astral_points`;
  - `houses`;
  - `angles`;
  - `aspects`;
  - `dignity_results`;
  - `dominance_result`;
  - `advanced_conditions`;
  - `fixed_star_conjunctions`.
- Required fields:
  - `surface`;
  - `status`;
  - `source cible`;
  - `autorisee dans calculateurs`;
  - `commentaire`;
  - `owner`;
  - `allowlist reason`.
- Optional fields:
  - `future removal story`;
  - `debug snapshot`;
  - `public API projection`;
  - `migration bridge`;
  - `non-usage proof`.
- Required statuses:
  - `canonical`;
  - `compatibility projection`;
  - `public API projection`;
  - `chart-level result`;
  - `legacy`;
  - `deprecated` seulement si une decision de retrait est explicite.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-224.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | undocumented legacy fields | architecture doc | aucun runtime | doc inventory | doc test | surface manquante |
| 2 | direct legacy reads | `chart_objects` or projector | calculateurs cibles | architecture | AST guard | public adapter touche |
| 3 | duplicated mappers | projector central borne | mappers morts | unit + rg | non-usage proof | risque API/front |
| 4 | manual review | deterministic guards | nouveaux developpements | architecture | zero new hit | guard trop fragile |

Completion rule: chaque batch conserve `pytest -q`, `app.routes`, `app.openapi()` et les sorties historiques.

## 4h. Reintroduction Guard

- Guard target:
  - empecher le retour de `planet_positions`, `astral_points`, `advanced_conditions`, `dignity_results` ou `fixed_star_conjunctions`
    comme sources metier dans les calculateurs;
  - empecher les branches d'eligibilite par `object_type`;
  - empecher les nouveaux builders specialises par objet;
  - empecher les seuils magiques locaux dans les calculateurs.
- Forbidden examples:
  - `natal_result.planet_positions` dans un nouveau calculateur;
  - `natal_result.advanced_conditions` dans un nouvel adapter metier;
  - `if obj.object_type == ChartObjectType.PLANET`;
  - `ChartObjectType.ANGLE` pour router une logique metier;
  - `PlanetRuntimeBuilder`, `AngleRuntimeBuilder`, `AstralPointRuntimeBuilder` ou `FixedStarRuntimeBuilder` nouveau sans preuve.
- Required guard evidence:
  - test AST ou scan cible borne a `backend/app/domain/astrology`;
  - tests de coherence projection;
  - preuves `app.routes`, `app.openapi()` et `TestClient`;
  - preuve `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- Required architecture guard against reintroduction:
  - architecture guard: forbidden symbols must not be reintroduced outside documented allowlists;
  - interdire les lectures directes non allowlistees;
  - interdire les selectors par `object_type` ou code nominal;
  - interdire les builders specialises futurs sans decision documentee.
- Deterministic source: forbidden symbols dans `backend/app/domain/astrology` et allowlist dans le test d'architecture.
- Evidence profile: `reintroduction_guard`.
- Command:
  - `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation CS-224 | `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/evidence/validation.md` | Baseline, scans, tests et preuve finale. |
| Review CS-224 | `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/generated/11-code-review.md` | Resultat de review apres implementation. |

## 5. Current State Evidence

Le codebase actuel indique:

repository evidence assumption risk: le SKILL.md et le cheatsheet demandes sont absents, donc la story suit le brief et les diagnostics de validation.

- Repository evidence assumption risk - le SKILL.md et le cheatsheet demandes sont absents, donc la story suit le brief et les diagnostics de validation.
- Evidence 1: `_story_briefs/cs-224-legacy-runtime-surface-cleanup-guardrails.md` - demande une consolidation, pas une suppression cassante.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - contient `RG-144` a `RG-148`, couvrant le runtime chart objects.
- Evidence 3: `_condamad/stories/CS-223-chart-object-interpretation-input-adapter/00-story.md` - est `ready-to-dev`.
- Evidence 4: `backend` - existe dans l'arborescence courante.
- Evidence 5: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` - existe.
- Evidence 6: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` - existe.
- Evidence 7: `.agents/skills/condamad-story-writer/SKILL.md` - absent, donc la story suit le brief et les diagnostics.

## 6. Target State

After implementation:

- `docs/architecture/astrology-runtime-surfaces.md` existe.
- `chart_objects` est documente comme source canonique interne.
- Les anciennes collections sont documentees comme projections de compatibilite ou resultats chart-level.
- Les usages legacy conserves sont allowlistes avec raison et owner.
- Les calculateurs nouveaux passent par `chart_objects`, capabilities ou projectors explicites.
- Les tests d'architecture bloquent la consommation directe legacy non autorisee.
- Les tests d'architecture bloquent la logique metier par `object_type`.
- Les projections historiques restent coherentes avec `chart_objects`.
- `NatalResult` conserve les surfaces publiques necessaires.
- Les sorties publiques ne sont pas cassees.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - backend domain astrology;
  - natal runtime surfaces;
  - chart objects runtime;
  - projection compatibility;
  - architecture tests;
  - no frontend, DB, auth, i18n, style, build or migration scope.
- Applicable guardrails:
  - `RG-144`: `ChartObjectRuntimeData` reste le contrat runtime canonique et les calculateurs lisent les capacites.
  - `RG-145`: le moteur d'aspects reste branche sur la frontiere chart objects.
  - `RG-146`: motion/visibility restent des payloads runtime types sans recalcul ni seuil local.
  - `RG-147`: dignity/dominance restent des payloads et resultats controles sans retour a `object_type`.
  - `RG-148`: house/rulership restent des payloads runtime types sans resolver concurrent.
- Non-applicable examples:
  - frontend/style: aucune surface React ou CSS n'est dans le scope.
  - DB/migrations: aucune persistance ou schema DB n'est dans le scope.
  - auth/i18n: aucun comportement d'authentification ou localisation n'est dans le scope.
- Registry gap: aucun `RG-149` dedie CS-224 n'est ajoute dans cette generation normale; l'evidence finale doit recommander son ajout ulterieur.

## 7. Acceptance Criteria

Alias de preuve:

- `$arch`: `backend/tests/architecture`
- `$astro`: `backend/tests/unit/domain/astrology`
- `$int`: `backend/tests/integration/astrology`
- `$doc`: `docs/architecture/astrology-runtime-surfaces.md`

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La documentation des surfaces runtime existe. | Evidence: `pytest -q $arch/test_chart_runtime_surface_documentation.py`; AST guard. |
| AC2 | `chart_objects` est documente comme source canonique interne. | Evidence: `pytest -q $arch/test_chart_runtime_surface_documentation.py`; scan `rg`. |
| AC3 | Les anciennes collections sont classees comme projections ou resultats chart-level. | Evidence: `pytest -q $arch/test_chart_runtime_surface_documentation.py`. |
| AC4 | Les usages legacy conserves sont allowlistes. | Evidence: `pytest -q $arch/test_chart_runtime_surface_guardrails.py`; scan `rg`. |
| AC5 | Les calculateurs migrés ne lisent plus directement les collections historiques. | Evidence: `pytest -q $arch/test_chart_runtime_surface_guardrails.py`; AST guard. |
| AC6 | La logique metier par `object_type` est bloquee hors owners allowlistes. | Evidence: `pytest -q $arch/test_chart_runtime_surface_guardrails.py`; AST guard. |
| AC7 | Les builders specialises futurs sont detectes. | Evidence: `pytest -q $arch/test_chart_runtime_surface_guardrails.py`; scan `rg`. |
| AC8 | Les seuils magiques locaux restent bloques dans les calculateurs. | Evidence: `pytest -q $arch/test_chart_runtime_surface_guardrails.py`; scan `rg`. |
| AC9 | `planet_positions` reste coherent avec les objets concernes de `chart_objects`. | Evidence: `pytest -q $astro/test_chart_runtime_surface_projections.py`; runtime pytest. |
| AC10 | `dignity_results` reste coherent avec `payloads.dignity`. | Evidence: `pytest -q $astro/test_chart_runtime_surface_projections.py`; runtime pytest. |
| AC11 | `fixed_star_conjunctions` reste coherent avec les payloads fixed star. | Evidence: `pytest -q $astro/test_chart_runtime_surface_projections.py`; runtime pytest. |
| AC12 | `NatalResult` conserve les surfaces historiques necessaires. | Evidence: `pytest -q $astro/test_natal_result_contract.py`; `app.routes`; `app.openapi()`. |
| AC13 | Les sorties publiques ne changent pas volontairement. | Evidence: `pytest -q $int/test_natal_public_contract_compatibility.py`; `TestClient`; `app.openapi()`. |
| AC14 | Toute suppression est prouvee par non-usage. | Evidence: `rg` cible + tests; note dans `evidence/validation.md`. |
| AC15 | Aucun changement de doctrine astrologique n'est introduit. | Evidence: golden tests existants; `pytest -q $astro/test_traditional_golden_cases.py`. |
| AC16 | L'evidence finale CS-224 est persistee. | Evidence: from story dir, `rg -n "CS-224 Final Evidence" evidence/validation.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline runtime et les usages legacy (AC: AC1, AC2, AC3, AC4, AC14, AC16)
  - [ ] Subtask 1.1 - Executer les scans cibles listes en section 4c.
  - [ ] Subtask 1.2 - Creer `evidence/validation.md` avec baseline et hypotheses.
  - [ ] Subtask 1.3 - Classer chaque usage comme canonical, projection, public compatibility, chart-level result ou debug/test.

- [ ] Task 2 - Documenter les surfaces runtime (AC: AC1, AC2, AC3, AC12)
  - [ ] Subtask 2.1 - Creer `docs/architecture/astrology-runtime-surfaces.md`.
  - [ ] Subtask 2.2 - Documenter toutes les surfaces requises par la section 4f.
  - [ ] Subtask 2.3 - Ajouter le test d'inventaire documentaire.

- [ ] Task 3 - Renforcer les guards d'architecture (AC: AC4, AC5, AC6, AC7, AC8)
  - [ ] Subtask 3.1 - Ajouter l'allowlist exacte des usages legacy acceptes.
  - [ ] Subtask 3.2 - Bloquer les nouvelles lectures directes des collections historiques.
  - [ ] Subtask 3.3 - Bloquer les branches `object_type` hors owners allowlistes.
  - [ ] Subtask 3.4 - Bloquer les builders specialises futurs non justifies.
  - [ ] Subtask 3.5 - Bloquer les seuils magiques locaux couverts par le brief.

- [ ] Task 4 - Verifier les projections historiques (AC: AC9, AC10, AC11, AC12)
  - [ ] Subtask 4.1 - Ajouter un test runtime `planet_positions` versus `chart_objects`.
  - [ ] Subtask 4.2 - Ajouter un test runtime `dignity_results` versus `payloads.dignity`.
  - [ ] Subtask 4.3 - Ajouter un test runtime `fixed_star_conjunctions` versus payloads fixed star.
  - [ ] Subtask 4.4 - Adapter les assertions aux surfaces reellement presentes sans masquer une divergence.

- [ ] Task 5 - Nettoyer les duplications prouvees (AC: AC4, AC5, AC14)
  - [ ] Subtask 5.1 - Identifier les builders, mappers ou adapters morts par scan cible.
  - [ ] Subtask 5.2 - Supprimer ou consolider uniquement les elements prouvés sans usage.
  - [ ] Subtask 5.3 - Consigner chaque retrait dans `evidence/validation.md`.

- [ ] Task 6 - Finaliser validation et preuve publique (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16)
  - [ ] Subtask 6.1 - Executer tests cibles et `pytest -q`.
  - [ ] Subtask 6.2 - Executer `ruff format .` et `ruff check .`.
  - [ ] Subtask 6.3 - Capturer `app.routes`, `app.openapi()` et un test `TestClient`.
  - [ ] Subtask 6.4 - Persister `CS-224 Final Evidence`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartObjectRuntimeData`, `ChartObjectCapabilities` et `ChartObjectPayloads`;
  - `NatalResult.chart_objects`;
  - les payloads runtime motion, visibility, dignity, dominance, house_position, rulership et fixed_star_conjunctions;
  - les projectors/builders existants si leur responsabilite est deja canonique;
  - les tests CS-217 a CS-223 lorsque leur scope couvre deja la frontiere.
- Do not recreate:
  - un second graphe runtime hors `chart_objects`;
  - un second calculateur d'aspects, dignity, dominance, houses, rulership, motion, visibility ou fixed stars;
  - des builders specialises par planete, angle, point astral ou etoile fixe;
  - une projection API publique concurrente.
- Shared abstraction allowed only if:
  - elle reduit une duplication concrete;
  - elle reste bornee a la projection ou validation runtime;
  - elle est couverte par tests.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers non nommes
- transitional aliases non bornes
- legacy imports dans les calculateurs
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- broad allowlist
- `PASS with limitation`

Specific forbidden symbols / paths:

- `natal_result.planet_positions` dans un nouveau calculateur;
- `natal_result.astral_points` dans un nouveau calculateur;
- `natal_result.advanced_conditions` dans un nouveau calculateur;
- `natal_result.dignity_results` dans un nouveau calculateur;
- `natal_result.fixed_star_conjunctions` dans un nouveau calculateur;
- `if obj.object_type == ChartObjectType.PLANET`;
- `if object_type == "planet"`;
- `ChartObjectType.ANGLE` pour router une logique metier;
- `ChartObjectType.FIXED_STAR` pour router une logique metier;
- `Planet*Builder`, `Angle*Builder`, `AstralPoint*Builder`, `FixedStar*Builder` nouveaux sans decision documentee;
- modification volontaire de `backend/app/api/**`, `backend/app/infra/**`, `backend/migrations/**` ou `frontend/src/**`.

## 11. Removal Classification Rules

La classification doit etre deterministe:

- `canonical-active`: l'element est reference par le code de production first-party ou il est le proprietaire canonique.
- `external-active`: l'element est reference par une API publique, le frontend, la documentation publique, un client ou une preuve d'audit.
- `historical-facade`: l'element delegue a une implementation canonique uniquement pour preserver une ancienne surface.
- `dead`: l'element n'a aucune reference dans le code de production, les tests, la documentation, les contrats generes et les surfaces externes connues.
- `needs-user-decision`: une ambiguite persiste apres les scans obligatoires et doit bloquer la suppression.

Matrice de decision de classification:

| Classification | Decisions autorisees | Regle |
|---|---|---|
| `canonical-active` | `keep` | Ne doit pas etre supprime. |
| `external-active` | `keep`, `needs-user-decision` | Ne doit pas etre supprime sans decision utilisateur explicite. |
| `historical-facade` | `delete`, `replace-consumer`, `needs-user-decision` | Doit etre remplace ou supprime quand aucun blocage externe ne subsiste. |
| `dead` | `delete` | Doit etre supprime. |
| `needs-user-decision` | `needs-user-decision` | Doit bloquer l'implementation jusqu'a decision. |

## 12. Removal Audit Format

Chemin obligatoire de la table d'audit:

- `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/evidence/runtime-surface-removal-audit.md`

Table d'audit obligatoire:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Decisions autorisees: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Chaque element supprime doit avoir une preuve issue de scans de references de code et de tests cibles.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Source runtime interne | `NatalResult.chart_objects` | collections historiques |
| Projection legacy | projector/builder nomme | calculateurs metier |
| Aspects chart-level | moteur d'aspects chart objects | `planet_positions` direct |
| Dignity/dominance payloads | enrichers chart objects et resultats globaux | `object_type` direct |
| Documentation surfaces | `docs/architecture/astrology-runtime-surfaces.md` | notes dispersees |
| Guards anti-retour | `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` | revue manuelle seule |

## 14. Delete-Only Rule

Les elements classes `dead` doivent etre supprimes, pas repointes.
They must be deleted, not repointed.

Interdit:

- rediriger vers une surface legacy;
- preserver un wrapper;
- ajouter un alias de compatibilite non documente;
- garder un builder specialise mort actif;
- preserver l'ancien chemin via un re-export;
- remplacer la suppression par un comportement soft-disable.

## 15. External Usage Blocker

- External usage blocker: public API/front/LLM consumers must remain compatible.
- If an item is `external-active`, it must not be deleted without a user decision.
- Required proof:
  - `app.routes`;
  - `app.openapi()`;
  - `TestClient` on the natal public path used by existing tests;
  - no voluntary diff under `frontend/src`.

## 16. Internal Usage Search

- Required before implementation:
  - rechercher les consommateurs actuels de `planet_positions`, `astral_points`, `houses`, `angles`, `aspects`, `dignity_results`,
    `dominance_result`, `advanced_conditions`, `fixed_star_conjunctions` et `chart_objects`;
  - identifier quels usages sont projections, API/front, fixtures, debug, migration bridge ou calculateurs.
- Required after implementation:
  - prouver dans `evidence/validation.md` que les nouveaux usages metier passent par `chart_objects` ou un projector explicite.

## 17. Generated Contract Check

- Generated contract check: required as no-public-delta proof.
- Reason: CS-224 modifie une architecture interne et ne doit pas modifier route, OpenAPI, client genere, migration DB ou schema frontend.
- Required evidence:
  - `app.routes` inspecte par test ou script local;
  - `app.openapi()` inspecte par test ou script local;
  - `TestClient` sur un endpoint natal public couvert par les tests existants;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- fichier qui declare `NatalResult`
- fichiers qui construisent le resultat natal
- fichiers qui exposent la projection JSON publique du theme natal
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `docs/architecture/astrology-runtime-surfaces.md` - inventaire et statut des surfaces.
- `backend/tests/architecture/test_chart_runtime_surface_documentation.py` - test documentaire.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` - tests AST/scans anti-retour.
- `backend/tests/unit/domain/astrology/test_chart_runtime_surface_projections.py` - coherence projections historiques.
- `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/evidence/validation.md` - preuve finale.

Possible files:

- projector ou builder de compatibilite existant - centralisation bornee si duplication prouvee.
- tests existants CS-217 a CS-223 - renforcement si le scope est deja couvert.

Likely tests:

- `backend/tests/architecture/test_chart_runtime_surface_documentation.py`
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- `backend/tests/unit/domain/astrology/test_chart_runtime_surface_projections.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`

Files not expected to change:

- `backend/app/api/**` - aucun endpoint modifie.
- `backend/app/infra/**` et `backend/migrations/**` - aucune persistance ou DB.
- `frontend/src/**` - aucune surface React.
- `backend/app/domain/astrology/dignities/**` - aucun score ou doctrine ne doit changer.
- `backend/app/domain/astrology/dominance/**` - aucun score ou classement ne doit changer.

## 20. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 21. Validation Plan

Run or justify why skipped. Toutes les commandes Python doivent etre lancees apres activation du venv depuis la racine du repo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Tests cibles:

```powershell
pytest -q backend/tests/architecture/test_chart_runtime_surface_documentation.py
pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py
pytest -q backend/tests/unit/domain/astrology/test_chart_runtime_surface_projections.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
pytest -q backend/tests/integration/astrology/test_natal_public_contract_compatibility.py
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
rg -n "natal_result\.planet_positions|natal_result\.astral_points|natal_result\.advanced_conditions|natal_result\.dignity_results" `
  backend/app/domain/astrology -g "*.py"
rg -n "natal_result\.fixed_star_conjunctions|natal_result\.houses|natal_result\.angles" backend/app/domain/astrology -g "*.py"
rg -n "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.ANGLE|ChartObjectType\.FIXED_STAR" `
  backend/app/domain/astrology -g "*.py"
rg -n "Planet.*Builder|Angle.*Builder|AstralPoint.*Builder|FixedStar.*Builder" backend/app/domain/astrology -g "*.py"
rg -n "\b8\.5\b|\b17\b|\b0\.2833\b|\b0\.01\b" backend/app/domain/astrology -g "*.py"
rg -n "CS-224 Final Evidence" _condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/evidence/validation.md
git diff -- backend/app/api backend/app/infra backend/migrations frontend/src
```

Runtime checks:

```powershell
pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py
pytest -q backend/tests/unit/domain/astrology/test_chart_runtime_surface_projections.py
```

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md"
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py $story
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict $story
```

Expected scan results:

- direct legacy scan: zero nouveau hit hors allowlist documentee;
- `object_type` scan: zero hit dans les nouveaux calculateurs, selectors, projectors et consumers;
- specialized builder scan: zero nouveau builder hors decision documentee;
- magic threshold scan: zero nouveau seuil local;
- adjacent diff: empty unless blocker documented.

Skipped-command rule:

- Toute commande sautee doit etre consignee dans l'evidence finale avec la commande exacte, la raison, le risque et la preuve de remplacement.

## 22. Regression Risks

- Risk: un nouveau calculateur consomme `planet_positions` comme source primaire.
  - Guardrail: AC4, AC5 et `RG-144`.
- Risk: la selection revient a une logique par `object_type`.
  - Guardrail: AC6, `RG-144`, `RG-145`, `RG-147` et `RG-148`.
- Risk: les projections historiques divergent de `chart_objects`.
  - Guardrail: AC9, AC10, AC11 et tests runtime.
- Risk: une suppression casse l'API ou le front.
  - Guardrail: AC12, AC13, `app.routes`, `app.openapi()` et `TestClient`.
- Risk: le cleanup devient une refonte de doctrine.
  - Guardrail: AC15 et golden tests existants.

## 23. Dev Agent Instructions

- Implement only CS-224.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export, broad allowlist, unresolved marker or hidden residual work.
- Consume `chart_objects` through capabilities and payloads, not `object_type`.
- Keep API, DB, migrations, prompts LLM and frontend out of scope.
- Preserve public compatibility projections unless a separate approved removal story exists.
- Use French top-of-file comments/docstrings for new or significantly modified Python files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard deltas, unclassified fallback, compatibility, legacy, migration-only,
  shim, alias, unresolved markers or hidden residual in-domain work.

## 24. CS-224 Final Evidence Template

Create `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/evidence/validation.md` with:

```markdown
## CS-224 Final Evidence

### Runtime surfaces
- Documented canonical and legacy runtime surfaces.
- chart_objects is the canonical internal source.
- Legacy collections are retained as compatibility projections.

### Cleanup
- Removed or consolidated redundant builders/adapters where safe.
- No public API/front-breaking removal.

### Guardrails
- Added architecture tests for direct legacy consumption.
- Added architecture tests for object_type-driven logic.
- Added guardrails against specialized builders.

### Consistency
- Historical projections remain coherent with chart_objects.
- NatalResult compatibility is preserved.
- app.routes, app.openapi() and TestClient show no public API delta.

### Validation
- ruff format .
- ruff check .
- pytest -q
- targeted architecture and runtime projection tests

### Allowlist
- Listed all whitelisted legacy usages and reasons.
- Registry gap for a future dedicated CS-224 guardrail is documented.
```

## 25. Story Generation Validation Notes

- Story validation command attempted after venv activation:
  - `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md`
- Story validation result:
  - first run: FAIL with unsupported archetype, deletion marker, allowlist contract, contract shape, removal audit and guardrail diagnostics.
  - second run: FAIL with current evidence marker, temporary allowlist exit condition and reintroduction guard wording diagnostics.
  - final correction: replaced by the current validation results after this review cycle.
  - current review cycle: PASS.
- Strict lint command attempted after venv activation:
  - `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md`
- Strict lint result:
  - first run: FAIL with the same structural diagnostics as validation.
  - second run: FAIL with current evidence marker, temporary allowlist exit condition and reintroduction guard wording diagnostics.
  - final correction: replaced by the current strict lint results after this review cycle.
  - current review cycle: PASS.

## 26. References

- Source brief: `_story_briefs/cs-224-legacy-runtime-surface-cleanup-guardrails.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-144`, `RG-145`, `RG-146`, `RG-147`, `RG-148`).
- Previous story: `_condamad/stories/CS-223-chart-object-interpretation-input-adapter/00-story.md`.
