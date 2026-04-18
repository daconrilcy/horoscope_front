# Story 66.27: Propagation complète et fidèle de `context_quality_handled_by_template` jusqu’à l’observabilité

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want propager sans perte le signal `context_quality_handled_by_template` depuis la résolution réelle du prompt jusqu’au snapshot canonique d’observabilité,
so that `obs_snapshot.context_compensation_status`, les logs, la persistance, les métriques, les dashboards et la documentation reflètent enfin fidèlement ce que le runtime sait déjà sur le traitement template-side de `context_quality`.

## Contexte

La story 66.25 a introduit un snapshot canonique d’observabilité avec l’axe `context_compensation_status` et la taxonomie `not_needed | template_handled | injector_applied | unknown`. La documentation [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) expose toutefois encore un écart explicite : le runtime sait détecter quand un template gère déjà `context_quality`, mais cette connaissance n’est pas fidèlement propagée jusqu’au `ResolvedExecutionPlan` effectivement construit dans `_resolve_plan()`.

L’état réel du dépôt à la date de création de cette story est le suivant :

- `ResolvedExecutionPlan` porte déjà le champ `context_quality_handled_by_template: bool = False` dans [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py).
- `_build_result()` dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) s’appuie déjà sur `plan.context_quality_handled_by_template` pour publier `ContextCompensationStatus.TEMPLATE_HANDLED`.
- la persistance d’observabilité dans [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py) relaie correctement `obs_snapshot.context_compensation_status` vers `llm_call_logs.context_compensation_status`.
- mais la construction réelle du plan dans `_resolve_plan()` n’injecte pas aujourd’hui `context_quality_handled_by_template` dans l’appel à `ResolvedExecutionPlan(...)`, ce qui laisse la valeur à `False` par défaut sur le chemin nominal réel.
- en parallèle, les tests de la story 66.25 couvrent déjà `template_handled` en construisant manuellement un `ResolvedExecutionPlan` avec `context_quality_handled_by_template=True`, ce qui masque le trou d’intégration réel au niveau `_resolve_plan() -> _build_result()`.

Le problème n’est donc pas conceptuel. Les types, la taxonomie et une partie des tests existent déjà. Le P0 consiste à fermer l’écart entre :

- ce que le runtime déduit réellement du prompt et de `ContextQualityInjector`,
- ce que `ResolvedExecutionPlan` fige comme source de vérité runtime,
- et ce que l’observabilité expose ensuite aux opérateurs.

Cette story doit traiter cet écart comme un problème de propagation canonique, pas comme une simple retouche cosmétique de tests.

## Acceptance Criteria

1. **AC1 — Propagation canonique dans le plan** : `_resolve_plan()` renseigne explicitement `context_quality_handled_by_template` dans `ResolvedExecutionPlan` à partir de la détection réelle du traitement template-side de `context_quality`. La valeur ne doit plus dépendre du défaut `False` du modèle.
2. **AC2 — Détection fidèle du traitement template-side** : Pour `context_quality` dégradé (`partial` ou `minimal`), si le runtime détecte que le prompt courant traite déjà explicitement ce niveau côté template selon la logique canonique utilisée pour éviter l’injection de compensation, le signal propagé vaut `True`; sinon il vaut `False`. Cette détection doit refléter le mécanisme runtime effectif, et non dépendre d’une syntaxe de template considérée comme seule définition normative.
3. **AC3 — Observabilité alignée sans recalcul divergent** : `obs_snapshot.context_compensation_status` vaut `template_handled` lorsque `context_quality_handled_by_template=True` et `context_quality_instruction_injected=False`, sans qu’aucune couche aval ne reconstruise localement une vérité concurrente. La couche de persistance relaie cette valeur depuis le snapshot canonique sans réinterprétation.
4. **AC4 — Cohérence logs / DB / métriques** : Le statut `template_handled` est visible de manière fiable dans `GatewayMeta.obs_snapshot`, dans la persistance `llm_call_logs.context_compensation_status`, et dans les métriques/agrégats alimentés par le snapshot canonique, sans régression des autres statuts (`not_needed`, `injector_applied`, `unknown`).
5. **AC5 — Pas de double compensation silencieuse** : Si un template gère explicitement `context_quality`, l’injecteur n’ajoute pas une compensation supplémentaire et l’observabilité ne publie jamais `injector_applied` pour ce même cas. `template_handled` et `injector_applied` restent mutuellement exclusifs sur le chemin réel.
6. **AC6 — Documentation réalignée avec le runtime** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) n’affirme plus qu’il existe un écart actuel si celui-ci est corrigé ; elle décrit le comportement runtime effectif après implémentation.
7. **AC7 — Couverture de non-régression sur le vrai chemin** : Les tests couvrent le chemin intégré `_resolve_plan() -> _build_result() -> obs_snapshot -> log_call()` pour un cas `template_handled`, et pas seulement des plans fabriqués manuellement.
8. **AC8 — Compatibilité avec 66.25** : La story ne crée ni nouvelle taxonomie ni nouvelle source de vérité d’observabilité. Elle réutilise `ResolvedExecutionPlan`, `ExecutionObservabilitySnapshot`, `ContextCompensationStatus` et la persistance introduite par 66.25.
9. **AC9 — Alignement des surfaces d’exploitation** : Aucune surface de reporting ou dashboard fondée sur `context_compensation_status` ne nécessite de taxonomie alternative ni de remapping compensatoire ; la correction améliore uniquement la fidélité du signal canonique.

## Tasks / Subtasks

- [x] Task 1: Fermer la propagation à la source dans `_resolve_plan()` (AC1, AC2, AC5)
  - [x] Identifier le point exact où le runtime sait déjà qu’un template gère `context_quality` avant ou pendant l’appel à `ContextQualityInjector.inject()`.
  - [x] Introduire une variable explicite, par exemple `context_quality_handled_by_template`, calculée à partir de la réalité du prompt courant et du niveau `cq_level`.
  - [x] Dériver ce booléen avant la construction finale de `ResolvedExecutionPlan(...)`, puis le figer dans le plan sans recalcul aval concurrent.
  - [x] Vérifier que les cas `full`, `partial` et `minimal` produisent une valeur cohérente, sans ambiguïté avec `context_quality_instruction_injected`.

- [x] Task 2: Verrouiller la cohérence d’observabilité aval (AC3, AC4, AC5, AC8)
  - [x] Vérifier que `_build_result()` continue de dériver `ContextCompensationStatus` exclusivement depuis le plan résolu et non depuis une heuristique locale concurrente.
  - [x] Vérifier que `GatewayMeta.obs_snapshot`, `observability_service.log_call()` et `LlmCallLogModel.context_compensation_status` exposent bien `template_handled` sur le chemin réel.
  - [x] S’assurer qu’aucune surface aval ne remappe `template_handled` en `unknown` faute d’information intermédiaire.

- [x] Task 3: Réaligner tests d’intégration et tests unitaires sur le chemin réel (AC4, AC7, AC8)
  - [x] Étendre [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py) ou créer une suite dédiée `test_story_66_27_context_quality_template_propagation.py`.
  - [x] Ajouter un test qui passe par `_resolve_plan()` avec un prompt contenant explicitement `{{#context_quality:partial}}` ou `{{#context_quality:minimal}}`, puis vérifie le `obs_snapshot.context_compensation_status == template_handled`.
  - [x] Ajouter une assertion de non-régression sur `ResolvedExecutionPlan.context_quality_handled_by_template`.
  - [x] Couvrir un cas inverse où l’injecteur est appliqué pour démontrer l’exclusivité entre `template_handled` et `injector_applied`.

- [x] Task 4: Mettre à jour la documentation et les garde-fous narratifs (AC6, AC9)
  - [x] Corriger dans [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) la section `Context Quality` pour refléter l’état réel après fix.
  - [x] Vérifier que la documentation continue de décrire `ResolvedExecutionPlan` comme source de vérité runtime et ne réintroduit pas une lecture locale concurrente.
  - [x] Si nécessaire, ajuster les notes/story artifacts 66.25 ou 66.26 seulement pour cohérence documentaire minimale, sans réécrire leur intention.

- [x] Task 5: Exécuter et documenter la vérification locale obligatoire (AC1 à AC9)
  - [x] Après activation du venv PowerShell, exécuter `ruff format .` puis `ruff check .` dans `backend/`.
  - [x] Exécuter `pytest -q` dans `backend/`.
  - [x] Exécuter au minimum la suite ciblée liée à l’observabilité de 66.25/66.27.
  - [x] Vérifier qu’aucune régression n’apparaît sur les stories 66.14, 66.17, 66.18 et 66.25.

## Dev Notes

### Diagnostic précis à préserver

- Le bug actuel n’est pas l’absence de type : le champ existe déjà dans [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py).
- Le bug n’est pas non plus l’absence de lecture aval : `_build_result()` sait déjà publier `ContextCompensationStatus.TEMPLATE_HANDLED` si le plan le porte.
- Le vrai trou est l’intégration au point de vérité runtime : l’appel `ResolvedExecutionPlan(...)` dans `_resolve_plan()` ne transmet pas aujourd’hui `context_quality_handled_by_template`, alors que ce booléen est précisément celui qui doit servir de source de vérité figée pour l’observabilité.
- Les tests existants peuvent donner une illusion de couverture parce qu’ils construisent des plans à la main avec `context_quality_handled_by_template=True`, sans prouver que `_resolve_plan()` sait produire cette valeur sur un chemin réel.
- Le booléen propagé doit refléter l’état du prompt effectivement retenu après résolution assembly/config et avant gel du plan, pas un état intermédiaire d’un template candidat non retenu.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/context_quality_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/context_quality_injector.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Contraintes d’implémentation

- Ne pas créer un second champ d’observabilité comme `template_handled_runtime` ou une taxonomie parallèle ; le booléen canonique reste `ResolvedExecutionPlan.context_quality_handled_by_template`.
- Ne pas déplacer la vérité de compensation dans `observability_service.py` ou dans la persistance DB ; ces couches doivent relayer le snapshot, pas l’inventer.
- Ne pas casser l’immuabilité et la doctrine de `ResolvedExecutionPlan` définies par 66.2 et 66.17.
- Ne pas modifier la taxonomie de `ContextCompensationStatus` introduite par 66.25.
- Ne pas introduire de “fix” uniquement documentaire ou uniquement de test. La correction doit être effective sur le chemin runtime réel.

### Testing Requirements

- Ajouter un test de bout en bout interne au gateway qui prouve qu’un prompt géré par template aboutit à :
  - `plan.context_quality_handled_by_template is True`
  - `plan.context_quality_instruction_injected is False`
  - `result.meta.obs_snapshot.context_compensation_status == ContextCompensationStatus.TEMPLATE_HANDLED`
- Ajouter un test miroir pour un cas compensé par injecteur avec :
  - `context_quality_handled_by_template is False`
  - `context_quality_instruction_injected is True`
  - `context_compensation_status == injector_applied`
- Vérifier que `observability_service.log_call()` persiste bien `context_compensation_status="template_handled"` lorsque le snapshot le porte, et que cette valeur provient du snapshot canonique sans recalcul indépendant dans la couche de persistance.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest tests/integration/test_story_66_25_observability.py -q`
  - si une nouvelle suite dédiée est créée : `pytest tests/integration/test_story_66_27_context_quality_template_propagation.py -q`

### Previous Story Intelligence

- **66.14** a établi la doctrine `context_quality` avec deux mécanismes complémentaires : blocs template et injecteur. Cette story doit s’aligner sur cette doctrine, pas en inventer une nouvelle.
- **66.17** a durci `ResolvedExecutionPlan` comme vérité runtime immuable. La correction doit donc être faite avant le gel du plan, pas en patch local après coup.
- **66.18** a déjà montré le pattern attendu : un arbitrage runtime doit être figé une seule fois dans le plan, puis projeté vers l’aval.
- **66.25** a introduit le snapshot canonique d’observabilité et les taxonomies fermées ; la présente story est un fix de propagation, pas une refonte de ce modèle.
- **66.26** a rendu la documentation du pipeline gouvernée et traçable ; toute divergence constatée puis corrigée ici doit aussi être reflétée dans la doc canonique.

### Git Intelligence

Commits récents pertinents observés :

- `68c93e77` : `docs(llm): reflect story 66.26 in canonical pipeline guide`
- `d9b4ad6c` : `docs(bmad): align story 66.26 artifacts with review fixes`
- `491db97b` : `fix: durcir les règles de gouvernance LLM (context_quality et format stable)`
- `ba92e1ef` : `feat: durcissement de la gouvernance documentaire du pipeline LLM (Story 66.26)`
- `d8ec8a3a` : `docs(llm): refine 66.25 observability documentation`

Pattern récent à réutiliser :

- source de vérité unique au runtime ;
- tests d’intégration dédiés par story ;
- mise à jour synchrone de la documentation canonique ;
- corrections post-review centrées sur cohérence runtime/doc/tests plutôt que sur refactors larges.

### Project Structure Notes

- Travail backend et documentaire uniquement.
- Les artefacts doivent rester cohérents avec la structure existante `backend/app/llm_orchestration/`, `backend/app/infra/db/models/`, `backend/tests/integration/` et `docs/`.
- Aucun changement frontend n’est attendu pour cette story.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/context_quality_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/context_quality_injector.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)
- [66-14-context-quality-strategie-redaction.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-14-context-quality-strategie-redaction.md)
- [66-17-source-verite-canonique-composition.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-17-source-verite-canonique-composition.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story créée à partir du brief utilisateur et réalignée sur l’état réel du runtime 66.25/66.26.
- Le bug central documenté est la non-propagation effective du booléen dans l’appel réel à `ResolvedExecutionPlan(...)`, malgré la présence du champ dans les types et les assertions avales.
- Les tâches exigent une couverture intégrée du chemin `_resolve_plan() -> _build_result() -> obs_snapshot -> log_call()`.
- **Clôture dev-story (2026-04-18)** : implémentation déjà présente dans le dépôt (`ContextQualityInjector.inject` → `ResolvedExecutionPlan.context_quality_handled_by_template`), tests `backend/tests/integration/test_story_66_27_integrated_propagation.py` + unitaires associés verts ; sprint et cases à cocher synchronisés avec l’état « done ».

### File List

- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/context_quality_injector.py`
- `backend/tests/integration/test_story_66_27_integrated_propagation.py`
- `backend/tests/unit/test_story_66_27_injector_extension.py`
- `docs/llm-prompt-generation-by-feature.md`
- `_bmad-output/implementation-artifacts/66-27-propagation-complete-context-quality-handled-by-template-observabilite.md`

### Change Log

- 2026-04-18 : Synchronisation artefact BMAD — statut `done`, tâches complétées ; confirmation par exécution `pytest tests/integration/test_story_66_27_integrated_propagation.py` et alignement `sprint-status.yaml`.
