# Story CS-222 fixed-star-conjunction-runtime-from-chart-objects: Calculer les conjonctions d'etoiles fixes depuis chart objects
Status: done

## 1. Objective

Faire converger les etoiles fixes vers la surface runtime `NatalResult.chart_objects`: les etoiles fixes sont des `ChartObjectRuntimeData`
avec `payloads.fixed_star`, les cibles sont selectionnees par `capabilities.supports_fixed_star_conjunction`, puis les contacts calculatoires
sont rattaches aux cibles via `payloads.fixed_star_conjunctions`. La story preserve les sorties historiques et ne produit aucun texte symbolique.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: `_story_briefs/cs-222-fixed-star-conjunction-runtime-from-chart-objects.md`.
- Reason for change: CS-217 a cree `ChartObjectRuntimeData`, CS-218 a aligne les aspects sur les capacites, CS-219 a ajoute motion/visibility,
  CS-220 a ajoute dignity/dominance et CS-221 a ajoute house/rulership. Les etoiles fixes doivent suivre la meme trajectoire runtime.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment review: le brief demande un runtime calculatoire de conjonctions aux etoiles fixes depuis `chart_objects`, pas une narration,
  pas un moteur d'aspects generalise et pas une refonte du catalogue.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`
- In scope:
  - stabiliser `FixedStarRuntimePayload` comme payload documentaire d'une etoile fixe;
  - stabiliser `FixedStarConjunctionRuntimePayload` comme payload calculatoire de contact;
  - garantir `ChartObjectPayloads.fixed_star_conjunctions` avec un tuple vide par defaut;
  - construire les etoiles fixes catalogue comme `ChartObjectRuntimeData`;
  - selectionner les etoiles fixes via `payloads.fixed_star is not None`;
  - selectionner les cibles via `supports_fixed_star_conjunction=True`;
  - calculer uniquement les conjonctions par distance angulaire normalisee;
  - prendre l'orbe depuis `FixedStarConjunctionRulesRuntimeData` ou une constante centralisee;
  - enrichir immuablement les objets cibles avec les contacts detectes;
  - brancher le calcul dans le flux natal apres creation des `chart_objects` et avant les consommateurs runtime;
  - conserver les sorties historiques si elles existent;
  - ajouter tests unitaires, integration runtime natal, garde architecture et evidence persistante.
- Out of scope:
  - interpretation symbolique, texte astrologique, prompt, narration ou couche LLM;
  - aspects autres que la conjonction, parans, levers heliacaux ou visibilite astronomique reelle;
  - precession dynamique non deja supportee par le runtime;
  - refonte du catalogue, DB, migrations, API publique, frontend ou JSON public volontaire;
  - changement de doctrine d'orbe sans decision explicite.
- Explicit non-goals:
  - ne pas selectionner les cibles par `object_type`;
  - ne pas ajouter de builder parallele `fixed_star_catalog -> fixed_star_builder -> fixed_star_conjunctions`;
  - ne pas coder un seuil d'orbe local comme `orb <= 1.0` hors constante nommee, regle runtime ou test;
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story ajoute ou stabilise une projection runtime interne dans `chart_objects` tout en preservant les contrats historiques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: les objets cible eligibles portent `payloads.fixed_star_conjunctions`;
  - autorise: les etoiles fixes catalogue deviennent des `ChartObjectRuntimeData` documentaires;
  - autorise: le flux natal calcule les contacts depuis `chart_objects`;
  - interdit: changer le JSON public, les routes API, les schemas DB, le frontend ou les sorties historiques sans decision explicite.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la migration exige une nouvelle doctrine d'orbes, une precession dynamique, une migration DB, un changement API public,
  une suppression de sortie historique ou une interpretation narrative.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `NatalResult.chart_objects`, `payloads.fixed_star`, `payloads.fixed_star_conjunctions` et les capacites pilotent la consommation interne. |
| Baseline Snapshot | yes | Les sorties historiques et le schema public doivent etre compares avant/apres. |
| Ownership Routing | yes | Payloads, selectors, calculator, rules, enricher et orchestration natal ont des owners separes. |
| Allowlist Exception | yes | Aucune compatibilite transitoire, branche `object_type` ou second builder n'est autorise. |
| Contract Shape | yes | La forme typée des payloads et rules est le coeur de la story. |
| Batch Migration | no | Le changement cible un flux runtime natal unique. |
| Reintroduction Guard | yes | Les guards doivent bloquer le retour d'un calcul par catalogue parallele ou par famille d'objet. |
| Persistent Evidence | yes | Baseline, tests, scans et preuve finale doivent etre conserves dans le dossier CS-222. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects`;
  - `ChartObjectPayloads.fixed_star`;
  - `ChartObjectPayloads.fixed_star_conjunctions`;
  - `ChartObjectCapabilities.supports_fixed_star_conjunction`;
  - `FixedStarConjunctionRulesRuntimeData`;
  - selectors, calculator et enricher CS-222.
- Runtime/domain artifacts:
  - tests unitaires des payloads fixed star;
  - tests unitaires des selectors fixed star et target;
  - tests unitaires du calculateur avec conjonction exacte, dans l'orbe, hors orbe et wrap 359/0;
  - tests unitaires de l'enricher immuable;
  - test d'integration `NatalResult.chart_objects`;
  - AST guard: `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - preuve runtime `app.routes` et `app.openapi()` inchanges pour le schema public.
- Secondary evidence:
  - scans anti-branches `object_type`, anti-orbes magiques et anti-texte narratif;
  - `ruff format .`, `ruff check .` et `pytest -q` apres activation du venv.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni l'enrichissement de `NatalResult.chart_objects`, ni la distance angulaire normalisee, ni l'immutabilite des payloads.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/chart_object_runtime_builder.py`;
  - `Get-Content backend/app/domain/astrology/fixed_stars/contracts.py`;
  - `Get-Content backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py`;
  - `Get-Content backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py`;
  - `Get-Content backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py`;
  - `Select-String` dans `natal_calculation.py` sur `fixed_stars`, `chart_objects`, `FixedStarConjunctionCalculator` et `NatalResult`;
  - `Select-String "RG-144|RG-145|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes lectures et scans cibles apres implementation;
  - tests CS-222 du Validation Plan;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`;
  - preuve `app.openapi()` et `app.routes` sans delta public non autorise;
  - diff adjacent sur API, DB, migrations, frontend, prediction et interpretation.
- Expected invariant:
  - les etoiles fixes sont des objets runtime documentaires;
  - les cibles sont choisies par capacite;
  - le calculateur consomme `chart_objects`;
  - les payloads sont calculatoires et non narratifs;
  - les sorties historiques restent disponibles.
- Allowed differences:
  - payloads fixed star stabilises;
  - selectors, rules, calculator et enricher nouveaux ou ajustes;
  - branchement natal minimal;
  - tests, guards et evidence persistante;
  - Registry gap: un invariant dedie CS-222 pourra etre ajoute ulterieurement hors generation normale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats chart-object fixed star | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | API, frontend, DB, prediction |
| Regles d'orbe fixed star | `backend/app/domain/astrology/fixed_stars/contracts.py` | calculateur, tests hors constante nommee |
| Selection des etoiles | `backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py` | branches `object_type` dans orchestrateur |
| Calcul des contacts | `backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py` | API, prediction, builder catalogue |
| Enrichissement des cibles | `backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py` | mutation en place, calculateur |
| Orchestration natal | `backend/app/domain/astrology/natal_calculation.py` | services chart, frontend, repositories |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune allowed delta transitoire n'est autorisee pour CS-222. | Politique permanente sans allowed delta. |

Validation rule:

- Tout retour a une eligibilite par `object_type`, tout second calculateur catalogue ou tout texte narratif dans les payloads bloque l'implementation.

## 4f. Contract Shape

- Contract type:
  - dataclasses immuables `frozen=True, slots=True`;
  - tuples pour collections de contacts;
  - strings de codes/sources;
  - aucune phrase interpretative dans les payloads runtime.
- Fields:
  - `FixedStarRuntimePayload`;
  - `FixedStarConjunctionRuntimePayload`;
  - `ChartObjectPayloads.fixed_star`;
  - `ChartObjectPayloads.fixed_star_conjunctions`;
  - `FixedStarConjunctionRulesRuntimeData`.
- Required fields:
  - fixed star: `catalog_code`, `display_name`, `reference_system`, `source_code`;
  - contact: `fixed_star_code`, `fixed_star_display_name`, `target_code`, `target_display_name`;
  - contact numeric: `fixed_star_longitude_deg`, `target_longitude_deg`, `orb_deg`, `max_orb_deg`;
  - contact provenance: `rule_code`, `source`.
- Optional fields:
  - `constellation_code`, `magnitude`, `reference_epoch`, `categories`;
  - `applying`, `separating`, `confidence` seulement si un contrat runtime existant les supporte deja.
- Forbidden fields:
  - `meaning`, `interpretation`, `narrative`, `prompt`, `good`, `bad`, `malefic`, `benefic` comme texte libre.
- Status codes:
  - aucun status code HTTP n'est ajoute ou modifie par CS-222.
- Serialization names:
  - noms internes conserves: `fixed_star`, `fixed_star_conjunctions`, `supports_fixed_star_conjunction`.
  - aucune nouvelle cle publique JSON n'est autorisee.
- Frontend type impact:
  - aucun type frontend n'est modifie; `frontend/src/**` reste hors scope.
- Generated contract impact:
  - `app.routes` et `app.openapi()` doivent rester sans delta public volontaire.

## 4g. Batch Migration Plan

- Not applicable.
- Reason: CS-222 cible un flux runtime natal unique et ne migre pas une collection de surfaces historiques par lots.

## 4h. Reintroduction Guard

- Architecture guard against reintroduced fixed star debt:
  - verifier les forbidden symbols `object_type ==`, `ChartObjectType.PLANET`, `ChartObjectType.FIXED_STAR`,
    `FixedStarBuilder` et `PlanetFixedStarConjunctionBuilder` sur les surfaces runtime fixed star.
- Deterministic source:
  - forbidden symbols dans `backend/app/domain/astrology/fixed_stars` et `backend/app/domain/astrology/builders`;
  - importable python modules sous `backend/app/domain/astrology/fixed_stars`.
- Evidence profile: `reintroduction_guard`.
- Command:
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`.
- Command:
  - `rg -n "object_type ==|ChartObjectType\\." backend/app/domain/astrology/fixed_stars backend/app/domain/astrology/builders -g "*.py"`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation CS-222 | `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/evidence/validation.md` | Baseline, scans, tests et preuve finale. |
| Review CS-222 | `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/generated/11-code-review.md` | Resultat de review apres implementation. |

## 5. Current State Evidence

Le codebase actuel indique:

- Evidence 1: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - contient `ChartObjectType.FIXED_STAR`.
- Evidence 2: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose `supports_fixed_star_conjunction`.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose `FixedStarRuntimePayload`.
- Evidence 4: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose `FixedStarConjunctionRuntimePayload`.
- Evidence 5: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - expose `fixed_star_conjunctions`.
- Evidence 6: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - accepte `fixed_stars`.
- Evidence 7: `backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py` - contient les selectors attendus.
- Evidence 8: `backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py` - contient le calculateur attendu.
- Evidence 9: `backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py` - contient l'enricher attendu.
- Evidence 10: `backend/app/domain/astrology/natal_calculation.py` - appelle calculator et enricher fixed star.
- Evidence 11: `backend/tests/unit/domain/astrology/` - contient les tests cibles fixed star.

## 6. Target State

After implementation:

- Les etoiles fixes catalogue sont presentes dans `NatalResult.chart_objects`.
- Chaque etoile fixe porte `object_type=FIXED_STAR`, `source_type=CATALOG` et `payloads.fixed_star`.
- Les etoiles fixes ne sont pas cibles de leurs propres conjonctions dans CS-222.
- Les cibles eligibles sont selectionnees uniquement par `supports_fixed_star_conjunction=True`.
- Les contacts sont calcules par distance angulaire normalisee entre `0` et `180`.
- L'orbe maximum vient de `FixedStarConjunctionRulesRuntimeData` ou d'une constante nommee.
- Les objets cibles sont enrichis par nouvelles instances et conservent leurs payloads existants.
- `NatalResult.chart_objects` porte les contacts detectes.
- Les anciennes sorties et projections restent disponibles.
- `app.routes` et `app.openapi()` ne changent pas volontairement.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - backend domain astrology;
  - runtime chart objects;
  - fixed stars;
  - selectors/calculator/enricher;
  - no API, DB, auth, frontend, i18n, style, build or migration scope.
- Applicable guardrails:
  - `RG-144`: contrat runtime unifie et consommation par `ChartObjectCapabilities`.
  - `RG-145`: le moteur d'aspects ne doit pas redevenir consommateur direct de `fixed_stars`.
  - `RG-147`: dignity/dominance restent stables et ne recoltent pas de logique fixed star.
  - `RG-148`: house/rulership restent stables et sans projection fixed star.
- Non-applicable examples:
  - DB/migrations: aucune persistance ou schema DB n'est dans le scope.
  - frontend/style: aucune surface React ou CSS n'est dans le scope.
  - auth/i18n: aucun comportement d'authentification ou localisation n'est dans le scope.
- Registry gap: aucun `RG-149` dedie CS-222 n'est ajoute dans cette generation normale; l'evidence finale doit recommander son ajout ulterieur.

## 7. Acceptance Criteria

Sauf mention contraire, les commandes de test ci-dessous ciblent les fichiers sous `backend/tests/unit/domain/astrology/`.

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `FixedStarRuntimePayload` reste non narratif. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_runtime.py -k fixed_star_payload`. |
| AC2 | `FixedStarConjunctionRuntimePayload` reste calculatoire. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_runtime.py -k conjunction_payload`. |
| AC3 | `ChartObjectPayloads.fixed_star_conjunctions` vaut `()` par defaut. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_runtime.py`. |
| AC4 | Les etoiles fixes sont construites comme `ChartObjectRuntimeData`. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`. |
| AC5 | Les etoiles fixes sont selectionnees par `payloads.fixed_star`. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_selectors.py`; AST guard. |
| AC6 | Les cibles sont selectionnees par `supports_fixed_star_conjunction`. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_selectors.py`; AST guard. |
| AC7 | Une etoile fixe sans longitude declenche une erreur explicite. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_selectors.py -k no_longitude`. |
| AC8 | Une cible eligible sans longitude declenche une erreur explicite. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_selectors.py -k target`. |
| AC9 | La conjonction exacte produit un orbe `0.0`. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py -k exact`. |
| AC10 | Une conjonction dans l'orbe respecte la regle appliquee. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py`. |
| AC11 | Une cible hors orbe ne produit aucun contact. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py -k outside`. |
| AC12 | La distance angulaire normalisee gere le passage 359/0. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py -k wrap`. |
| AC13 | L'enricher retourne de nouvelles instances. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_fixed_star_enricher.py`. |
| AC14 | `NatalResult.chart_objects` porte les contacts fixed star. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`; `app.routes`. |
| AC15 | Les sorties historiques restent disponibles. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`; `app.openapi()`. |
| AC16 | Aucun calcul fixed star ne depend d'une branche `object_type`. | Evidence: `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`. |
| AC17 | Aucun seuil d'orbe magique n'est introduit hors rules/constants/tests. | Evidence: scan `rg` du Validation Plan. |
| AC18 | Aucun texte symbolique n'est ajoute au runtime. | Evidence: scan `rg`; `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`. |
| AC19 | L'evidence finale CS-222 est persistee. | Evidence: from story dir, `rg -n "CS-222 Final Evidence" evidence/validation.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les owners existants (AC: AC14, AC15, AC16, AC17, AC18, AC19)
  - [ ] Subtask 1.1 - Executer les commandes de baseline listees en section 4c.
  - [ ] Subtask 1.2 - Creer `evidence/validation.md` avec baseline, scans initiaux et hypotheses.

- [ ] Task 2 - Stabiliser les contrats fixed star runtime (AC: AC1, AC2, AC3, AC18)
  - [ ] Subtask 2.1 - Verifier ou ajuster `FixedStarRuntimePayload`.
  - [ ] Subtask 2.2 - Verifier ou ajuster `FixedStarConjunctionRuntimePayload`.
  - [ ] Subtask 2.3 - Verifier `ChartObjectPayloads.fixed_star_conjunctions=()`.
  - [ ] Subtask 2.4 - Verifier la validation capacites/payloads.

- [ ] Task 3 - Stabiliser la construction et les selectors (AC: AC4, AC5, AC6, AC7, AC8, AC16)
  - [ ] Subtask 3.1 - Construire les etoiles fixes catalogue comme `ChartObjectRuntimeData`.
  - [ ] Subtask 3.2 - Selectionner les etoiles par `payloads.fixed_star`.
  - [ ] Subtask 3.3 - Selectionner les cibles par `supports_fixed_star_conjunction`.
  - [ ] Subtask 3.4 - Ajouter les erreurs explicites sur longitudes absentes.

- [ ] Task 4 - Stabiliser le calculateur et les regles d'orbe (AC: AC9, AC10, AC11, AC12, AC17, AC18)
  - [ ] Subtask 4.1 - Centraliser `FixedStarConjunctionRulesRuntimeData`.
  - [ ] Subtask 4.2 - Utiliser une distance angulaire normalisee.
  - [ ] Subtask 4.3 - Trier les contacts de maniere deterministe.
  - [ ] Subtask 4.4 - Bloquer aspects autres que conjonction et textes narratifs.

- [ ] Task 5 - Stabiliser l'enrichissement et l'orchestration natal (AC: AC13, AC14, AC15, AC16)
  - [ ] Subtask 5.1 - Enrichir uniquement les cibles connues et eligibles.
  - [ ] Subtask 5.2 - Conserver les payloads existants.
  - [ ] Subtask 5.3 - Brancher le flux dans `natal_calculation.py` sans changer API ou JSON public.
  - [ ] Subtask 5.4 - Verifier `app.routes` et `app.openapi()`.

- [ ] Task 6 - Finaliser tests, scans et evidence (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19)
  - [ ] Subtask 6.1 - Executer les tests cibles et `pytest -q`.
  - [ ] Subtask 6.2 - Executer `ruff format .` et `ruff check .`.
  - [ ] Subtask 6.3 - Executer les scans anti-regression.
  - [ ] Subtask 6.4 - Persister `CS-222 Final Evidence`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ChartObjectRuntimeData`, `ChartObjectCapabilities` et `ChartObjectPayloads`;
  - `FixedStarRuntimePayload` et `FixedStarConjunctionRuntimePayload`;
  - `FixedStarConjunctionRulesRuntimeData`;
  - `FixedStarChartObjectSelector` et `FixedStarConjunctionTargetSelector`;
  - `angular_distance_deg` ou helper canonique equivalent;
  - `build_chart_object_runtime_data`;
  - `runtime_reference.fixed_stars.items`.
- Do not recreate:
  - un second builder de catalogue fixed star;
  - un second calculateur de conjonctions hors `fixed_stars`;
  - une table locale d'orbes;
  - une selection par planete, luminaire, angle ou nom d'objet;
  - une projection API publique ou type frontend.
- Shared abstraction allowed only if:
  - elle centralise une responsabilite concrete de selection, calcul ou enrichment;
  - elle reste dans `backend/app/domain/astrology/fixed_stars` ou runtime voisin;
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

- `if object_type == "planet"` dans fixed star;
- `if object_type == "fixed_star"` comme critere de selection metier;
- `if obj.object_type == ChartObjectType.PLANET` dans calculator/selectors/enrichers;
- `if obj.object_type == ChartObjectType.FIXED_STAR` comme critere de selection;
- `FixedStarBuilder`;
- `PlanetFixedStarConjunctionBuilder`;
- `orb <= 1.0` hors constante nommee, rules ou tests;
- payload contenant `interpretation`, `narrative`, `prompt`, `llm`, `meaning`, `good`, `bad`, `malefic`, `benefic` comme texte libre.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Objet runtime du theme | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | DTO API, frontend, prediction |
| Projection initiale des etoiles fixes | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | fixed star calculator |
| Regles d'orbe | `backend/app/domain/astrology/fixed_stars/contracts.py` | constantes locales dispersees |
| Selection fixed star/target | `backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py` | orchestrateur natal |
| Calcul des contacts | `backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py` | API, prediction |
| Enrichissement immuable | `backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py` | mutation du builder |
| Orchestration du theme natal | `backend/app/domain/astrology/natal_calculation.py` | services chart, frontend |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Internal Usage Search

- Required before implementation:
  - rechercher les consommateurs actuels de `fixed_stars`, `payloads.fixed_star`, `fixed_star_conjunctions`,
    `supports_fixed_star_conjunction`, `FixedStarConjunctionCalculator` et `runtime_reference.fixed_stars`;
  - identifier quels usages historiques restent dans prediction et lesquels doivent lire `ChartObjectRuntimeData`.
- Required after implementation:
  - prouver dans `evidence/validation.md` que les nouveaux consommateurs fixed star passent par les payloads runtime.

## 17. Generated Contract Check

- Generated contract check: required as no-public-delta proof
- Reason: `chart_objects` reste exclu du schema public; aucune route, OpenAPI, migration DB, client genere ou schema frontend ne doit changer.
- Required evidence:
  - `app.routes` inspecte par test ou script local;
  - `app.openapi()` inspecte par test ou script local;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/fixed_stars/contracts.py`
- `backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py`
- `backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py`
- `backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_runtime.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_selectors.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_enricher.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - payloads fixed star et validation.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - projection des etoiles fixes.
- `backend/app/domain/astrology/fixed_stars/contracts.py` - regles d'orbe.
- `backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py` - selectors par payload/capacite.
- `backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py` - calcul de conjonctions.
- `backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py` - enrichment immuable.
- `backend/app/domain/astrology/natal_calculation.py` - orchestration.
- `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/evidence/validation.md` - preuve finale.

Likely tests:

- `backend/tests/unit/domain/astrology/test_fixed_star_runtime.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_selectors.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py`
- `backend/tests/unit/domain/astrology/test_fixed_star_enricher.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`

Files not expected to change:

- `backend/app/api/**` - aucun endpoint modifie.
- `backend/app/infra/**` et `backend/migrations/**` - aucune persistance ou DB.
- `frontend/src/**` - aucune surface React.
- `backend/app/domain/prediction/**` - sortie historique preservee, pas de refonte.
- `backend/app/domain/astrology/interpretation/**` - aucun texte narratif fixed star.

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
pytest -q backend/tests/unit/domain/astrology/test_fixed_star_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_fixed_star_selectors.py
pytest -q backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_fixed_star_enricher.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
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
rg -n "object_type ==|\\.object_type ==|ChartObjectType\\.PLANET|ChartObjectType\\.FIXED_STAR" `
  backend/app/domain/astrology/fixed_stars backend/app/domain/astrology/builders -g "*.py"
rg -n "\\borb\\s*<=\\s*1\\.0\\b|\\b1\\.0\\b|\\b1\\.5\\b|\\b2\\.0\\b" `
  backend/app/domain/astrology/fixed_stars -g "*.py"
rg -n "meaning|interpretation|narrative|prompt|llm|good|bad|malefic|benefic" `
  backend/app/domain/astrology/runtime backend/app/domain/astrology/fixed_stars -g "*.py"
rg -n "fixed_star_catalog|FixedStarBuilder|PlanetFixedStarConjunctionBuilder" backend/app/domain/astrology -g "*.py"
rg -n "CS-222 Final Evidence" _condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/evidence/validation.md
git diff -- backend/app/api backend/app/infra backend/migrations frontend/src backend/app/domain/prediction backend/app/domain/astrology/interpretation
```

Commandes de validation de la story:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/00-story.md"
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py $story
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict $story
```

Expected scan results:

- `object_type` scan: zero hit dans selectors/calculator/enricher, sauf tests ou projection builder explicitement documente;
- orb scan: zero seuil magique dans le calculateur, hors rules/constants/tests;
- anti-narration scan: zero hit dans runtime payloads et fixed_stars;
- duplicate builder scan: zero second builder ou calculateur parallele;
- adjacent diff: empty unless blocker documented.

Skipped-command rule:

- Toute commande sautee doit etre consignee dans l'evidence finale avec la commande exacte, la raison, le risque et la preuve de remplacement.

## 22. Regression Risks

- Risk: les etoiles fixes restent une famille parallele au lieu de passer par `chart_objects`.
  - Guardrail: AC4, AC5, AC14 et `RG-144`.
- Risk: les cibles sont filtrees par planete/luminaire/angle.
  - Guardrail: AC6, AC16 et AST guard.
- Risk: les orbes sont codees localement.
  - Guardrail: AC10, AC17 et `FixedStarConjunctionRulesRuntimeData`.
- Risk: les payloads deviennent interpretatifs.
  - Guardrail: AC1, AC2, AC18.
- Risk: fuite vers JSON public, API, DB ou frontend.
  - Guardrail: AC15, generated contract check et diff adjacent.

## 23. Dev Agent Instructions

- Implement only CS-222.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not preserve old behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export, broad allowlist, unresolved marker or hidden residual work.
- Reuse `ChartObjectRuntimeData`, `FixedStarConjunctionRulesRuntimeData`, selectors, calculator and enricher.
- Keep fixed star contacts calculatory and non-narrative.

## 24. CS-222 Final Evidence Template

Create `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/evidence/validation.md` with:

```markdown
## CS-222 Final Evidence

### Runtime
- Fixed stars are represented as ChartObjectRuntimeData.
- FixedStarRuntimePayload and FixedStarConjunctionRuntimePayload are available.
- Eligible targets receive fixed_star_conjunctions payloads.

### Calculation
- Conjunctions are computed from chart_objects.
- Targets are selected through supports_fixed_star_conjunction.
- Orbs are driven by rules, not magic values.

### Compatibility
- Existing outputs are preserved.
- No interpretation text is introduced.
- app.routes and app.openapi() show no public API delta.

### Validation
- ruff format .
- ruff check .
- pytest -q
- targeted fixed star tests

### Guardrails
- No object_type-driven eligibility.
- No duplicate fixed star calculators.
- No hardcoded orb thresholds outside rules/constants/tests.
- Registry gap for a future dedicated CS-222 guardrail is documented.
```

## 25. Story Generation Validation Notes

- Story validation command attempted after venv activation:
  - `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-222-fixed-star-conjunction-runtime-from-chart-objects\00-story.md`
- Story validation result:
  - `PASS` apres corrections de review redactionnelle.
- Strict lint command attempted after venv activation:
  - `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-222-fixed-star-conjunction-runtime-from-chart-objects\00-story.md`
- Strict lint result:
  - `PASS` apres corrections de review redactionnelle.
- Status note: story file and tracker are done after implementation and brief-alignment review.

## 26. References

- Source brief: `_story_briefs/cs-222-fixed-star-conjunction-runtime-from-chart-objects.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-144`, `RG-145`, `RG-147`, `RG-148`).
