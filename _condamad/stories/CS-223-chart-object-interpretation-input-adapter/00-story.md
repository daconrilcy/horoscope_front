# Story CS-223 chart-object-interpretation-input-adapter: Adapter l'entree d'interpretation depuis chart objects
Status: done

## 1. Objective

Creer une entree unique, stable et typee pour l'interpretation du theme natal depuis `NatalResult.chart_objects`.
La couche interpretative doit consommer `ChartInterpretationInputRuntimeData` plutot que lire directement les collections specialisees du calcul natal.

## 2. Trigger / Source

- Source type: architecture-decision.
- Source reference: `_story_briefs/cs-223-chart-object-interpretation-input-adapter.md`.
- Reason for change: CS-217 a unifie `ChartObjectRuntimeData`; CS-218 a aligne les aspects; CS-219 a rattache motion/visibility;
  CS-220 a rattache dignity/dominance; CS-221 a rattache house/rulership; CS-222 a rattache fixed star contacts.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment review: le brief demande une frontiere d'entree interpretative, pas des textes d'interpretation, pas une refonte LLM,
  pas un changement du JSON public et pas une action de retrait des collections historiques.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - creer `ChartInterpretationInputRuntimeData`;
  - creer `ChartObjectInterpretationRuntimeData`;
  - creer des sous-contrats legers pour aspects, dignites, dominance, maisons, rulership, motion, visibility et fixed star contacts;
  - creer `ChartObjectInterpretationSelector`;
  - creer `ChartObjectInterpretationProjector`;
  - creer `ChartInterpretationInputBuilder`;
  - selectionner les objets via `capabilities.supports_interpretation`;
  - projeter les payloads utiles depuis `ChartObjectRuntimeData`;
  - projeter les aspects, dignites, positions en maison, maitrises, dominance chart-level et fixed star contacts dans des sections explicites sans recalcul;
  - adapter le service d'interpretation ou le generateur d'assemblage pour consommer le nouveau contrat;
  - isoler une facade legacy seulement si la migration complete est trop large;
  - ajouter tests unitaires, integration et garde architecture.
- Out of scope:
  - ecrire des textes d'interpretation;
  - modifier la doctrine astrologique;
  - modifier les scores, orbes, dignites, dominance, aspects ou fixed star contacts;
  - supprimer `planet_positions`, `houses`, `angles`, `aspects`, `dignity_results`, `dominance_result` ou `advanced_conditions`;
  - ajouter un appel LLM dans le domaine astrology;
  - modifier FastAPI, OpenAPI, DB, migrations, frontend ou contrats HTTP.
- Explicit non-goals:
  - ne pas selectionner les objets par `object_type`, code nominal ou famille planetaire;
  - ne pas recalculer dans l'adaptateur;
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story cree une frontiere d'entree interpretative interne qui combine plusieurs payloads runtime sans devenir API ni calculateur.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: les nouveaux flux interpretatifs consomment `ChartInterpretationInputRuntimeData`;
  - autorise: les collections historiques restent exposees pour compatibilite API, debug et migration progressive;
  - autorise: une facade legacy isolee et documentee peut traduire l'ancien input vers le nouveau contrat;
  - interdit: modifier volontairement schema public, OpenAPI, routes, DB, frontend ou sorties historiques.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la migration exige de supprimer une collection historique, changer un endpoint public, ajouter une dependance,
  changer la doctrine astrologique, modifier un prompt profondement ou coupler le domaine astrology a un provider LLM.
- Additional validation rules:
  - l'adaptateur lit `NatalResult.chart_objects` et les resultats chart-level deja calcules;
  - les objets interpretables sont selectionnes uniquement par `supports_interpretation`;
  - les payloads motion, visibility, dignity, dominance, house_position, rulership et fixed_star_conjunctions sont projetes, pas recalcules;
  - l'input final expose aussi les sections top-level `dignities`, `house_positions` et `rulerships` attendues par le brief, en plus des donnees attachees aux objets;
  - les contrats runtime interpretatifs ne contiennent pas de texte narratif;
  - `app.routes` et `app.openapi()` prouvent l'absence de delta public volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `NatalResult.chart_objects` devient la source de l'input interpretatif. |
| Baseline Snapshot | yes | Les consommateurs historiques doivent etre compares avant/apres migration. |
| Ownership Routing | yes | Contrats, selector, projector, builder, services et facade legacy ont des owners separes. |
| Allowlist Exception | yes | Toute facade legacy doit etre nommee, bornee et transitoire. |
| Contract Shape | yes | La forme des contrats interpretatifs est le coeur de la story. |
| Batch Migration | yes | La migration des consommateurs peut etre progressive par flux. |
| Reintroduction Guard | yes | Les guards doivent bloquer les nouvelles lectures directes des collections historiques. |
| Persistent Evidence | yes | Baseline, tests, scans et preuve finale doivent etre conserves dans le dossier CS-223. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects`;
  - `ChartObjectRuntimeData.capabilities.supports_interpretation`;
  - `ChartObjectRuntimeData.payloads`;
  - `NatalResult.aspects` et resultats chart-level deja calcules lorsque le contrat interpretatif en a besoin.
- Runtime/domain artifacts:
  - tests unitaires du selector;
  - tests unitaires du projector;
  - tests unitaires du builder;
  - tests d'integration du service ou assemblage interpretatif;
  - AST guard contre consommation directe de collections historiques dans les nouveaux flux;
  - preuve `app.routes` et `app.openapi()` sans delta public volontaire.
- Secondary evidence:
  - scans anti-recalcul, anti-texte narratif et anti-branches `object_type`;
  - `ruff format .`, `ruff check .` et `pytest -q` apres activation du venv.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la selection par capacite, ni la projection complete des payloads, ni la compatibilite du pipeline existant.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-ChildItem backend/app/domain/astrology/interpretation`;
  - `Select-String` dans `backend/app/domain/astrology/interpretation` sur `planet_positions`, `dignity_results`, `dominance_result` et `advanced_conditions`;
  - `Select-String` dans `backend/app/services` sur `interpretation`, `prompt`, `planet_positions`, `dignity_results` et `dominance_result`;
  - `Select-String "RG-144|RG-145|RG-146|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes lectures et scans cibles apres implementation;
  - tests CS-223 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend et providers LLM.
- Expected invariant:
  - l'input interpretatif est construit depuis `chart_objects`;
  - les contrats restent calculatoires ou structuraux;
  - les collections historiques restent disponibles;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - nouveaux contrats interpretatifs internes;
  - nouveaux selector, projector et builder;
  - adaptation ciblee du service d'interpretation ou facade legacy;
  - tests, guard architecture et evidence persistante;
  - Registry gap: un invariant dedie CS-223 pourra etre ajoute ulterieurement hors generation normale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats d'input interpretatif | `backend/app/domain/astrology/interpretation/*contracts.py` | API, frontend, DB, providers LLM |
| Selection objets interpretables | `ChartObjectInterpretationSelector` | service, prompt builder, branche `object_type` |
| Projection payloads | `ChartObjectInterpretationProjector` | calculateurs dignity, dominance, aspects |
| Assemblage input theme | `ChartInterpretationInputBuilder` | routeur API, frontend, repository |
| Migration pipeline interpretatif | service d'interpretation ou facade legacy isolee | contrats runtime chart object |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucun delta transitoire n'est autorise au premier jet. | Politique permanente sans allowed delta. |

Validation rule:

- Toute lecture directe nouvelle de `planet_positions`, `houses`, `angles`, `dignity_results`, `dominance_result` ou `advanced_conditions`
  depuis un nouveau flux interpretatif bloque l'implementation.

## 4f. Contract Shape

- Contract type:
  - dataclasses immuables `frozen=True, slots=True`;
  - tuples pour les collections;
  - codes, scores, rangs, orbes, sources et classifications;
  - aucun texte narratif utilisateur dans les contrats.
- Fields:
  - `ChartInterpretationInputRuntimeData`;
  - `ChartObjectInterpretationRuntimeData`;
  - `AspectInterpretationRuntimeData`;
  - `DignityInterpretationRuntimeData`;
  - `DominanceInterpretationRuntimeData`;
  - `HousePositionInterpretationRuntimeData`;
  - `RulershipInterpretationRuntimeData`;
  - `MotionInterpretationRuntimeData`;
  - `VisibilityInterpretationRuntimeData`;
  - `FixedStarContactInterpretationRuntimeData`;
  - `ChartInterpretationMetadataRuntimeData`.
- Required fields:
  - `chart_id`;
  - `chart_type`;
  - `locale`;
  - `objects`;
  - `aspects`;
  - `dignities`;
  - `house_positions`;
  - `rulerships`;
  - `dominance`;
  - `fixed_star_contacts`;
  - `metadata`;
  - `code`, `display_name`, `object_type`, `classifications`, `zodiac_position`;
  - `house_number`, `house_modality`, `dignity`, `motion`, `visibility`;
  - `dominance`, `rulership`, `fixed_star_contacts`, `source_codes`.
- Optional fields:
  - `chart_id`, `locale`, `zodiac_position`;
  - `house_number`, `house_modality`;
  - `dignity`, `motion`, `visibility`, `dominance`, `rulership`;
  - `fixed_star_contacts` defaults to an empty tuple.
- Forbidden fields:
  - `meaning`, `narrative`, `psychological`, `prompt`, `llm`, `good`, `bad`, `positive_text`, `negative_text`.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is added by CS-223.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes` and `app.openapi()` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | none | contrats d'input interpretation | aucun | contrats | no re-export | contrat incompatible avec payloads runtime |
| 2 | collections historiques dispersees | `ChartInterpretationInputBuilder` | un consommateur interne | builder + integration | scan consumers | service trop large |
| 3 | usage historique restant | facade legacy isolee | flux non migres | integration pipeline | facade nommee | suppression requise |
| 4 | scans manuels | architecture guard | nouveaux flux | architecture | zero nouveau hit | guard trop fragile |

Completion rule: chaque batch doit conserver `pytest -q`, `app.routes`, `app.openapi()` et les sorties historiques.

## 4h. Reintroduction Guard

- Guard target:
  - empecher le retour d'une entree interpretative dispersee;
  - empecher les branches d'eligibilite par `object_type`;
  - empecher le recalcul de dignity, dominance, aspects, houses, rulership, motion, visibility ou fixed star contacts;
  - empecher le texte narratif dans les contrats runtime d'entree.
- Forbidden examples:
  - `if obj.object_type == ChartObjectType.PLANET`;
  - `if obj.code in ("sun", "moon", "mars")`;
  - `planet_positions` dans un nouveau builder interpretatif;
  - `dignity_results` dans un nouveau flux interpretatif hors facade legacy;
  - `dominance_result` dans un nouveau flux interpretatif hors builder central;
  - appel a un calculateur depuis le projector.
- Required guard evidence:
  - test AST ou scan cible borne a `backend/app/domain/astrology/interpretation` et aux services touches;
  - tests selector/projector/builder;
  - preuve `app.routes` et `app.openapi()`.
- Architecture guard against reintroduced interpretation input debt:
  - interdire les nouvelles lectures directes des collections historiques dans les nouveaux flux interpretatifs;
  - interdire les selectors par `object_type` ou code nominal;
  - interdire les appels calculateurs depuis les projectors.
- Deterministic source: forbidden symbols dans `backend/app/domain/astrology/interpretation` et `backend/app/services`.
- Evidence profile: `reintroduction_guard`.
- Command:
  - `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation CS-223 | `_condamad/stories/CS-223-chart-object-interpretation-input-adapter/evidence/validation.md` | Baseline, scans, tests et preuve finale. |
| Review CS-223 | `_condamad/stories/CS-223-chart-object-interpretation-input-adapter/generated/11-code-review.md` | Resultat de review apres implementation. |

## 5. Current State Evidence

Le codebase actuel indique:

- Repository evidence assumption risk - le brief cible `backend/app/domain/astrology/natal/contracts.py`, absent dans l'arborescence courante.
- Evidence 1: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose `ChartObjectRuntimeData`.
- Evidence 2: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose `ChartObjectCapabilities.supports_interpretation`.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose les payloads motion, visibility, dignity et dominance.
- Evidence 4: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose les payloads fixed star, house_position et rulership.
- Evidence 5: `backend/app/domain/astrology/interpretation` - existe deja avec des builders et contrats d'interpretation.
- Evidence 6: `backend/app/domain/astrology/natal/contracts.py` - n'existe pas dans l'arborescence courante.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - contient `RG-144` a `RG-148`, mais aucun invariant dedie CS-223.

## 6. Target State

After implementation:

- `ChartInterpretationInputRuntimeData` existe dans la couche interpretation.
- `ChartObjectInterpretationRuntimeData` existe dans la couche interpretation.
- Les sous-contrats interpretatifs legers existent pour les faits utiles.
- `ChartObjectInterpretationSelector` filtre uniquement par `supports_interpretation`.
- `ChartObjectInterpretationProjector` projette les payloads sans recalcul.
- `ChartInterpretationInputBuilder` construit l'input depuis `NatalResult.chart_objects`.
- Les aspects, dominance chart-level et fixed star contacts sont representes dans l'input.
- Les sections `dignities`, `house_positions` et `rulerships` sont exposees au niveau de l'input sans recalcul.
- Le service d'interpretation ou l'assemblage de prompt consomme le nouveau contrat.
- Les collections historiques restent disponibles pour compatibilite.
- `app.routes` et `app.openapi()` ne changent pas volontairement.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - backend domain astrology;
  - interpretation input;
  - chart objects runtime;
  - selector, projector, builder;
  - no API, DB, auth, frontend, i18n, style, build or migration scope.
- Applicable guardrails:
  - `RG-144`: `ChartObjectRuntimeData` reste le contrat runtime canonique et les consommateurs lisent les capacites.
  - `RG-145`: les aspects restent issus de la frontiere chart objects deja etablie.
  - `RG-146`: motion/visibility restent des payloads runtime types sans recalcul ni seuil local.
  - `RG-147`: dignity/dominance restent des projections calculatoires sans recalcul par l'interpretation.
  - `RG-148`: house/rulership restent des payloads runtime types sans projection concurrente.
- Non-applicable examples:
  - frontend/style: aucune surface React ou CSS n'est dans le scope.
  - DB/migrations: aucune persistance ou schema DB n'est dans le scope.
  - auth/i18n: aucun comportement d'authentification ou localisation n'est dans le scope.
- Registry gap: aucun `RG-149` dedie CS-223 n'est ajoute dans cette generation normale; l'evidence finale doit recommander son ajout ulterieur.

## 7. Acceptance Criteria

Sauf mention contraire, les commandes de test ci-dessous ciblent les fichiers sous `backend/tests/unit/domain/astrology/interpretation/`.

Alias de preuve:

- `$interp`: `backend/tests/unit/domain/astrology/interpretation`
- `$arch`: `backend/tests/architecture`
- `$int`: `backend/tests/integration/astrology`
- `$astro`: `backend/tests/unit/domain/astrology`

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `ChartInterpretationInputRuntimeData` existe. | Evidence: `pytest -q $interp/test_chart_interpretation_input_contracts.py`; AST guard. |
| AC2 | `ChartObjectInterpretationRuntimeData` existe. | Evidence: `pytest -q $interp/test_chart_interpretation_input_contracts.py`; AST guard. |
| AC3 | Chaque sous-contrat utile reste non narratif. | Evidence: `pytest -q $interp/test_chart_interpretation_input_contracts.py`; scan `rg`. |
| AC4 | Les objets interpretables sont selectionnes par `supports_interpretation`. | Evidence: `pytest -q $interp/test_chart_object_interpretation_selector.py`; AST guard. |
| AC5 | Les objets non interpretables sont exclus de `objects`. | Evidence: `pytest -q $interp/test_chart_object_interpretation_selector.py -k non_interpretable`. |
| AC6 | L'ordre de `chart_objects` est preserve. | Evidence: `pytest -q $interp/test_chart_object_interpretation_selector.py -k order`. |
| AC7 | Un objet interpretable sans zodiac position produit une erreur explicite. | Evidence: `pytest -q $interp/test_chart_object_interpretation_projector.py -k zodiac`. |
| AC8 | Les payloads conditionnels sont projetes depuis les faits existants. | Evidence: `pytest -q $interp/test_chart_object_interpretation_projector.py -k motion_visibility`. |
| AC9 | Les payloads score-rank objet sont projetes sans recalcul. | Evidence: `pytest -q $interp/test_chart_object_interpretation_projector.py -k dignity_dominance`. |
| AC10 | Les payloads maison-maitrise sont projetes sans resolver local. | Evidence: `pytest -q $interp/test_chart_object_interpretation_projector.py -k house_rulership`. |
| AC11 | Fixed star contacts sont projetes depuis les payloads existants. | Evidence: `pytest -q $interp/test_chart_object_interpretation_projector.py -k fixed_star`. |
| AC12 | Sections du brief construites depuis `chart_objects`. | Evidence: `pytest -q $interp/test_chart_interpretation_input_builder.py`; `app.routes`. |
| AC13 | Le service ou assemblage interpretatif consomme le nouveau contrat. | Evidence: `pytest -q $int/test_chart_interpretation_input_pipeline.py`; `app.routes`. |
| AC14 | Les collections historiques restent disponibles. | Evidence: `pytest -q $astro/test_natal_result_contract.py`; `app.routes`; `app.openapi()`. |
| AC15 | Aucun nouveau flux interpretatif ne lit directement les collections historiques. | Evidence: `pytest -q $arch/test_chart_interpretation_input_boundary.py`; scan `rg`. |
| AC16 | Aucun texte narratif n'est introduit dans les contrats d'input. | Evidence: scan `rg`; `pytest -q $interp/test_chart_interpretation_input_contracts.py`. |
| AC17 | Aucun appel LLM ou provider externe n'apparait dans le domaine input. | Evidence: scan `rg`; `pytest -q $arch/test_chart_interpretation_input_boundary.py`. |
| AC18 | L'evidence finale CS-223 est persistee. | Evidence: from story dir, `rg -n "CS-223 Final Evidence" evidence/validation.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les owners existants (AC: AC13, AC14, AC15, AC16, AC17, AC18)
  - [ ] Subtask 1.1 - Executer les commandes de baseline listees en section 4c.
  - [ ] Subtask 1.2 - Creer `evidence/validation.md` avec baseline, scans initiaux et hypotheses.

- [ ] Task 2 - Creer les contrats interpretatifs d'entree (AC: AC1, AC2, AC3, AC16, AC17)
  - [ ] Subtask 2.1 - Ajouter `ChartInterpretationInputRuntimeData`.
  - [ ] Subtask 2.2 - Ajouter `ChartObjectInterpretationRuntimeData`.
  - [ ] Subtask 2.3 - Ajouter les sous-contrats legers.
  - [ ] Subtask 2.4 - Verifier les docstrings et commentaires globaux en francais.

- [ ] Task 3 - Creer selector et projector (AC: AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC16)
  - [ ] Subtask 3.1 - Implementer `ChartObjectInterpretationSelector`.
  - [ ] Subtask 3.2 - Implementer `ChartObjectInterpretationProjector`.
  - [ ] Subtask 3.3 - Ajouter les erreurs explicites pour donnees incoherentes.
  - [ ] Subtask 3.4 - Bloquer les criteres d'eligibilite par type ou code nominal.

- [ ] Task 4 - Creer le builder d'input theme (AC: AC12, AC14, AC15)
  - [ ] Subtask 4.1 - Construire `objects` depuis `NatalResult.chart_objects`.
  - [ ] Subtask 4.2 - Projeter les aspects et resultats chart-level deja calcules.
  - [ ] Subtask 4.3 - Exposer les sections top-level `dignities`, `house_positions` et `rulerships` depuis les payloads existants.
  - [ ] Subtask 4.4 - Ajouter metadata et source codes deterministes.
  - [ ] Subtask 4.5 - Verifier `app.routes` et `app.openapi()`.

- [ ] Task 5 - Adapter le pipeline interpretatif (AC: AC13, AC14, AC15, AC17)
  - [ ] Subtask 5.1 - Brancher le service ou assemblage cible sur `ChartInterpretationInputRuntimeData`.
  - [ ] Subtask 5.2 - Isoler une facade legacy seulement si la migration complete est trop large.
  - [ ] Subtask 5.3 - Garantir que le domaine input ne depend pas de provider LLM.

- [ ] Task 6 - Finaliser tests, scans et evidence (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18)
  - [ ] Subtask 6.1 - Executer tests cibles et `pytest -q`.
  - [ ] Subtask 6.2 - Executer `ruff format .` et `ruff check .`.
  - [ ] Subtask 6.3 - Executer les scans anti-regression.
  - [ ] Subtask 6.4 - Persister `CS-223 Final Evidence`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartObjectRuntimeData`, `ChartObjectCapabilities` et `ChartObjectPayloads`;
  - les payloads runtime motion, visibility, dignity, dominance, house_position, rulership et fixed_star_conjunctions;
  - les contrats d'aspects existants;
  - les resultats chart-level existants;
  - le service d'interpretation ou assemblage existant.
- Do not recreate:
  - un second graphe runtime hors `chart_objects`;
  - un second calculateur d'aspects, dignity, dominance, houses, rulership, motion, visibility ou fixed stars;
  - des builders specialises par planete, luminaire ou angle;
  - une projection API publique ou type frontend.
- Shared abstraction allowed only if:
  - elle centralise une responsabilite concrete de selection, projection ou assemblage;
  - elle reste dans `backend/app/domain/astrology/interpretation` ou un service d'orchestration existant;
  - elle est couverte par tests.

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

- `if obj.object_type == ChartObjectType.PLANET`;
- `if object_type == "planet"`;
- `if obj.code in ("sun", "moon", "mars")`;
- `planet_positions` dans un nouveau flux interpretatif hors facade legacy;
- `houses` dans un nouveau flux interpretatif hors builder central;
- `dignity_results` dans un nouveau flux interpretatif hors facade legacy;
- `dominance_result` dans un nouveau flux interpretatif hors builder central;
- `advanced_conditions` dans un nouveau flux interpretatif hors facade legacy;
- `calculate_aspects`, `calculate_dignity`, `calculate_dominance` depuis le projector;
- `prompt`, `llm`, `OpenAI`, `AIEngineAdapter` dans les contrats d'input;
- modification volontaire de `backend/app/api/**`, `backend/app/infra/**`, `backend/migrations/**` ou `frontend/src/**`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Contrats d'input interpretation | `backend/app/domain/astrology/interpretation/*contracts.py` | API, frontend, DB, provider LLM |
| Selection interpretability | `ChartObjectInterpretationSelector` | branchement service ou prompt |
| Projection objet | `ChartObjectInterpretationProjector` | calculateurs astrologiques |
| Assemblage input theme | `ChartInterpretationInputBuilder` | routeur API, repository, frontend |
| Migration du consommateur | service d'interpretation existant | contrats runtime chart object |

## 14. Delete-Only Rule

- Delete-only rule: not applicable.

## 15. External Usage Blocker

- External usage blocker: not applicable.

## 16. Internal Usage Search

- Required before implementation:
  - rechercher les consommateurs actuels de `planet_positions`, `houses`, `angles`, `aspects`, `dignity_results`, `dominance_result`,
    `advanced_conditions`, `fixed_star_conjunctions`, `interpretation` et `prompt`;
  - identifier quels usages restent historiques et lesquels doivent consommer `ChartInterpretationInputRuntimeData`.
- Required after implementation:
  - prouver dans `evidence/validation.md` que les nouveaux flux interpretatifs passent par l'input central.

## 17. Generated Contract Check

- Generated contract check: required as no-public-delta proof.
- Reason: CS-223 cree un contrat interne de domaine et ne doit pas modifier route, OpenAPI, client genere, migration DB ou schema frontend.
- Required evidence:
  - `app.routes` inspecte par test ou script local;
  - `app.openapi()` inspecte par test ou script local;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/interpretation/__init__.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/chart_signature.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` - contrats d'entree interpretative.
- `backend/app/domain/astrology/interpretation/chart_object_interpretation_selector.py` - selection par `supports_interpretation`.
- `backend/app/domain/astrology/interpretation/chart_object_interpretation_projector.py` - projection des payloads.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - assemblage depuis `NatalResult`.
- service d'interpretation ou assemblage existant - consommation du nouveau contrat.
- `_condamad/stories/CS-223-chart-object-interpretation-input-adapter/evidence/validation.md` - preuve finale.

Likely tests:

- `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_contracts.py`
- `backend/tests/unit/domain/astrology/interpretation/test_chart_object_interpretation_selector.py`
- `backend/tests/unit/domain/astrology/interpretation/test_chart_object_interpretation_projector.py`
- `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py`
- `backend/tests/integration/astrology/test_chart_interpretation_input_pipeline.py`
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`

Files not expected to change:

- `backend/app/api/**` - aucun endpoint modifie.
- `backend/app/infra/**` et `backend/migrations/**` - aucune persistance ou DB.
- `frontend/src/**` - aucune surface React.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - pas de changement attendu sauf import type strictement justifie.
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
pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_contracts.py
pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_object_interpretation_selector.py
pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_object_interpretation_projector.py
pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py
pytest -q backend/tests/integration/astrology/test_chart_interpretation_input_pipeline.py
pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
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
  backend/app/domain/astrology/interpretation backend/app/services -g "*.py"
rg -n "planet_positions|houses|angles|dignity_results|dominance_result|advanced_conditions" `
  backend/app/domain/astrology/interpretation backend/app/services -g "*.py"
rg -n "calculate_aspects|calculate_dignity|calculate_dominance|HouseRulerResolver|FixedStarConjunctionCalculator" `
  backend/app/domain/astrology/interpretation -g "*.py"
rg -n "meaning|narrative|psychological|prompt|llm|OpenAI|AIEngineAdapter" `
  backend/app/domain/astrology/interpretation -g "*.py"
rg -n "CS-223 Final Evidence" _condamad/stories/CS-223-chart-object-interpretation-input-adapter/evidence/validation.md
git diff -- backend/app/api backend/app/infra backend/migrations frontend/src
```

Runtime checks:

```powershell
pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
```

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-223-chart-object-interpretation-input-adapter/00-story.md"
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py $story
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict $story
```

Expected scan results:

- `object_type` scan: zero hit dans les nouveaux selectors, projectors, builders et consommateurs;
- historical collection scan: zero nouveau hit hors facade legacy documentee;
- recalculation scan: zero appel aux calculateurs depuis l'adaptateur;
- anti-narration scan: zero hit dans les contrats d'input;
- adjacent diff: empty unless blocker documented.

Skipped-command rule:

- Toute commande sautee doit etre consignee dans l'evidence finale avec la commande exacte, la raison, le risque et la preuve de remplacement.

## 22. Regression Risks

- Risk: la couche interpretative consomme a la fois `chart_objects` et les collections historiques.
  - Guardrail: AC12, AC13, AC15 et `RG-144`.
- Risk: le selector revient a une logique par type ou par code.
  - Guardrail: AC4, AC5, AC6 et AST guard.
- Risk: le projector recalcule des faits deja calcules.
  - Guardrail: AC8 a AC11, `RG-146`, `RG-147`, `RG-148` et scans anti-recalcul.
- Risk: l'adaptateur commence a produire du texte narratif.
  - Guardrail: AC3, AC16 et scan anti-narration.
- Risk: le domaine interpretation se couple au provider LLM.
  - Guardrail: AC17 et diff adjacent.

## 23. Dev Agent Instructions

- Implement only CS-223.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export, broad allowlist, unresolved marker or hidden residual work.
- Consume `chart_objects` through capabilities and payloads, not `object_type`.
- Keep the adapter deterministic, typed and non-narrative.
- Keep API, DB, migrations and frontend out of scope.
- Use French top-of-file comments/docstrings for new or significantly modified Python files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard deltas, unclassified fallback, compatibility, legacy, migration-only,
  shim, alias, unresolved markers or hidden residual in-domain work.

## 24. CS-223 Final Evidence Template

Create `_condamad/stories/CS-223-chart-object-interpretation-input-adapter/evidence/validation.md` with:

```markdown
## CS-223 Final Evidence

### Interpretation input
- Added ChartInterpretationInputRuntimeData.
- Added ChartObjectInterpretationRuntimeData.
- Interpretation input is built from chart_objects.
- Interpretation input exposes objects, aspects, dominance, dignities, house_positions, rulerships, fixed_star_contacts and metadata.

### Projection
- Objects are selected through supports_interpretation.
- Runtime payloads are projected without recalculation.
- No narrative text is generated.

### Compatibility
- Existing interpretation pipeline remains compatible.
- Legacy adapters, if any, are isolated.
- app.routes and app.openapi() show no public API delta.

### Validation
- ruff format .
- ruff check .
- pytest -q
- targeted interpretation input tests

### Guardrails
- No direct consumption of historical collections by new interpretation flows.
- No LLM/provider dependency in runtime input contracts.
- Registry gap for a future dedicated CS-223 guardrail is documented.
```

## 25. Story Generation Validation Notes

- Story validation command attempted after venv activation:
  - `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad/stories/CS-223-chart-object-interpretation-input-adapter/00-story.md`
- Story validation result:
  - `PASS`.
- Strict lint command attempted after venv activation:
  - `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad/stories/CS-223-chart-object-interpretation-input-adapter/00-story.md`
- Strict lint result:
  - `PASS`.
- Status note: story file and tracker are ready-to-dev after generation validation.

## 26. References

- Source brief: `_story_briefs/cs-223-chart-object-interpretation-input-adapter.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-144`, `RG-145`, `RG-146`, `RG-147`, `RG-148`).
- Previous story: `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/00-story.md`.
