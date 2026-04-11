# Story 66.25: Renforcement de l’observabilité opérationnelle du pipeline canonique et de ses compatibilités

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want to rendre explicitement visibles dans les logs, métriques, dashboards et métadonnées de résultat les discriminants structurels du pipeline LLM réellement exécuté,
so that l’exploitation puisse distinguer immédiatement le chemin canonique du fallback legacy, le provider demandé du provider réellement exécuté, le niveau de `context_quality`, l’application d’une compensation de contexte, et la source finale de `max_output_tokens`, sans devoir reconstruire ces informations depuis le code ou depuis plusieurs signaux partiels.

## Contexte

Les stories 66.21 à 66.24 ont déjà clarifié les règles de gouvernance du pipeline LLM :

- distinction entre chemin nominal canonique et compatibilités legacy ;
- gouvernance explicite des fallbacks avec `FallbackGovernanceRegistry` et la métrique `llm_gateway_fallback_usage_total` ;
- verrouillage des providers nominalement supportés via `NOMINAL_SUPPORTED_PROVIDERS` ;
- calcul et propagation de `context_quality` ;
- injection éventuelle d’une compensation `ContextQualityInjector` ;
- priorité finale de `max_output_tokens` entre `LengthBudget.global_max_tokens`, `ExecutionProfile.max_output_tokens` et la recommandation issue de `verbosity_profile` ;
- distinction de gouvernance `pipeline_kind` entre `nominal_canonical` et `transitional_governance`.

Cette doctrine est désormais bien documentée dans `docs/llm-prompt-generation-by-feature.md`, mais l’exploitation reste encore trop dépendante d’une lecture experte du code ou d’un croisement manuel entre plusieurs événements pour répondre à une question simple :

- quel pipeline réel a été exécuté ;
- quel fallback exact a été utilisé, s’il y en a un ;
- quel provider a été demandé, résolu puis effectivement exécuté ;
- comment le système a traité un contexte `partial` ou `minimal` ;
- d’où vient la borne finale de `max_output_tokens`.

Par clarification de conception, `execution_path_kind` n’est pas un “path” au sens strictement minimal de résolution interne. C’est un discriminant synthétique de runtime décrivant le chemin structurel dominant effectivement observé par l’exploitation. Si l’implémentation introduit des axes séparés tels que `recovery_status` ou `provider_execution_mode`, ils doivent rester dérivés du même snapshot canonique et ne jamais redéfinir localement la lecture principale.

Le dépôt montre déjà plusieurs briques utiles mais encore incomplètes ou hétérogènes :

- `ResolvedExecutionPlan` expose déjà `context_quality`, `context_quality_instruction_injected`, `max_output_tokens` et `max_output_tokens_source` ;
- `GatewayMeta` expose aujourd’hui `execution_path`, `context_quality`, `provider`, `max_output_tokens_source` et des métadonnées de profil ;
- `_build_result()` dans `backend/app/llm_orchestration/gateway.py` enrichit `GatewayResult.meta`, mais avec une taxonomie encore partielle et pas encore alignée sur les discriminants d’exploitation attendus par cette story ;
- `backend/app/llm_orchestration/services/observability_service.py` persiste déjà plusieurs champs techniques, mais pas encore un snapshot canonique et stable couvrant l’ensemble des axes de lecture ;
- les dashboards et rapports de la story 66.24 distinguent déjà `pipeline_kind`, mais pas encore le triplet provider ni le statut de compensation de contexte ni la source canonique d’arbitrage de `max_output_tokens`.

Le problème n’est donc plus de découvrir les mécanismes de gouvernance. Le problème est de transformer ces mécanismes en signaux d’exploitation de premier niveau, homogènes et directement lisibles.

## Acceptance Criteria

1. **AC1 — Champs canoniques de lecture runtime** : Chaque requête exécutée via le gateway produit des métadonnées structurées contenant au minimum `pipeline_kind`, `execution_path_kind`, `fallback_kind`, `requested_provider`, `resolved_provider`, `executed_provider`, `context_quality`, `context_compensation_status`, `max_output_tokens_source` et `max_output_tokens_final`, pour autant que l’information soit applicable au chemin concerné. Ces champs proviennent d’un snapshot canonique unique produit à la source, puis projeté vers les surfaces avales.
2. **AC2 — Distinction canonique vs legacy lisible sans reconstruction** : Pour un appel passant par assembly canonique, `execution_path_kind=canonical_assembly` et `fallback_kind=null`. Pour un appel passant par une compatibilité legacy, `execution_path_kind` et `fallback_kind` reflètent explicitement le mécanisme utilisé, sans déduction depuis un compteur séparé.
3. **AC3 — Triplet provider cohérent** : Le système expose distinctement `requested_provider`, `resolved_provider` et `executed_provider`. `requested_provider` désigne le provider demandé par la couche d’entrée ou, à défaut, le premier provider explicitement résolu avant tout mécanisme de tolérance runtime. Sur un chemin nominal OpenAI correct, les trois valeurs sont identiques. Sur un chemin non nominal tolérant un fallback runtime OpenAI, la divergence éventuelle est visible sans ambiguïté.
4. **AC4 — Traitement de contexte lisible** : Pour toute requête avec `context_quality` différent de `full`, le système indique explicitement si la variation a été gérée par le template (`template_handled`) ou par injection (`injector_applied`). Pour `context_quality=full`, le statut vaut `not_needed` sauf exception explicitement justifiée. Les statuts `template_handled` et `injector_applied` sont mutuellement exclusifs ; si le template gère explicitement `context_quality`, l’injecteur ne doit pas ajouter une seconde compensation.
5. **AC5 — Source finale de max tokens observable** : Quand `max_output_tokens_final` est défini, `max_output_tokens_source` indique explicitement quelle couche a gagné l’arbitrage final entre `LengthBudget.global_max_tokens`, `ExecutionProfile.max_output_tokens` et la recommandation issue de `verbosity_profile`, conformément à la priorité d’architecture documentée. Cette valeur est déterminée exclusivement au moment du merge final du plan dans le gateway ; aucune couche aval ne doit la recalculer.
6. **AC6 — Logs structurés homogènes** : Les logs structurés du gateway intègrent les champs canoniques définis par cette story avec des noms stables et une taxonomie fermée. Aucun dashboard d’exploitation ne dépend d’un parsing fragile de messages textuels libres pour reconstruire ces axes.
7. **AC7 — Métriques exploitables** : Il existe au minimum un événement structuré canonique ou un snapshot persistant unique portant ces discriminants, ensuite projeté vers les logs et les métriques. La télémétrie issue de cette source unique permet au minimum l’agrégation par `execution_path_kind`, `fallback_kind`, `context_quality`, `context_compensation_status`, `requested_provider`, `resolved_provider`, `executed_provider` et `max_output_tokens_source`, sans régression sur les métriques déjà existantes de 66.21 et 66.22.
8. **AC8 — Dashboards opérationnels mis à jour** : Les dashboards et support reports de run rendent effectivement disponibles, et pas seulement théoriquement requêtables, les vues minimales suivantes : volume par `execution_path_kind`, volume par `fallback_kind`, volume par `context_quality`, volume par `context_compensation_status`, volume par `executed_provider`, volume par `max_output_tokens_source`, avec filtre minimal par `environment`, `feature`, `is_nominal`. Les vues obligatoires sont distinguées des agrégats de support additionnels.
9. **AC9 — Compatibilité avec la matrice d’évaluation** : Quand un cas d’évaluation passe par le gateway, les rapports ou artefacts d’évaluation peuvent recroiser au minimum `pipeline_kind` avec `execution_path_kind`, afin de distinguer la classification de gouvernance attendue du chemin réellement exécuté.
10. **AC10 — Aucune ambiguïté sémantique entre les axes** : La documentation mise à jour explicite la différence entre `pipeline_kind`, `execution_path_kind` et `fallback_kind`, et interdit de réutiliser l’un pour déduire implicitement l’autre.

## Tasks / Subtasks

- [x] Task 1: Introduire un snapshot canonique d’observabilité d’exécution (AC1, AC2, AC3, AC4, AC5, AC10)
  - [x] Définir une petite structure dédiée, par exemple `ExecutionObservabilitySnapshot`, dans `backend/app/llm_orchestration/models.py` ou un module dédié voisin.
  - [x] Y porter une taxonomie fermée pour `execution_path_kind`, `fallback_kind`, `context_compensation_status` et `max_output_tokens_source`.
  - [x] Garantir que cette structure est calculée une seule fois au moment où le plan d’exécution est suffisamment déterminé.
  - [x] Interdire les redéfinitions locales concurrentes des mêmes taxonomies dans le gateway, l’observabilité et les dashboards.

- [x] Task 2: Calculer explicitement le discriminant de chemin runtime (AC1, AC2, AC6, AC10)
  - [x] Introduire `execution_path_kind` comme lecture structurelle du chemin réellement exécuté, distincte de `pipeline_kind`.
  - [x] Couvrir a minima les valeurs `canonical_assembly`, `legacy_use_case_fallback`, `legacy_execution_profile_fallback`, `repair` et `non_nominal_provider_tolerated`.
  - [x] Aligner ce calcul sur les signaux déjà présents dans `LLMGateway.execute_request()`, `RecoveryResult`, la gouvernance des fallbacks et le verrou provider.
  - [x] Vérifier que `execution_path_kind` n’écrase pas la sémantique historique de `execution_path` tant que la migration n’est pas terminée ; prévoir coexistence contrôlée ou remplacement explicite.
  - [x] Si l’équipe juge que `repair` et `non_nominal_provider_tolerated` doivent sortir de cet axe, documenter explicitement l’alternative (`recovery_status`, `provider_execution_mode`) tout en conservant une lecture synthétique unique depuis le snapshot canonique.

- [x] Task 3: Rendre le fallback lisible comme cause explicite (AC1, AC2, AC6, AC7, AC10)
  - [x] Introduire `fallback_kind` comme champ nullable distinct du simple booléen `fallback_triggered`.
  - [x] Réutiliser la gouvernance 66.21 pour les types attendus, par exemple `deprecated_use_case_mapping`, `use_case_first_resolution`, `resolve_model`, `openai_runtime_compat`, `test_local`, `legacy_feature_alias`.
  - [x] Garantir l’absence de `fallback_kind` sur un chemin canonique strict sans fallback.
  - [x] Aligner les valeurs avec `llm_gateway_fallback_usage_total` pour éviter toute divergence entre labels de métriques et champs de résultat.
  - [x] Définir explicitement si `fallback_kind` est mono-valeur ou multi-valeur. Si mono-valeur, documenter une règle de priorité stable représentant le fallback structurellement le plus significatif ; si multi-valeur, ajouter un champ résumé primaire pour les dashboards.

- [x] Task 4: Exposer le triplet provider demandé / résolu / exécuté (AC1, AC3, AC6, AC7, AC8)
  - [x] Identifier le point de vérité de `requested_provider` comme provider demandé par la couche d’entrée ou, à défaut, premier provider explicitement résolu avant toute tolérance runtime.
  - [x] Récupérer `resolved_provider` depuis le `ResolvedExecutionPlan` final avant toute tolérance runtime non nominale.
  - [x] Renseigner `executed_provider` avec le provider techniquement appelé par `_call_provider()` ou son équivalent.
  - [x] Garantir qu’un fallback runtime OpenAI non nominal ne masque plus le provider demandé/résolu initial.

- [x] Task 5: Rendre visible le traitement effectif de `context_quality` (AC1, AC4, AC6, AC7, AC8)
  - [x] Introduire `context_compensation_status` avec les valeurs `not_needed`, `template_handled`, `injector_applied`, `unknown`.
  - [x] Déterminer ce statut à partir des blocs `context_quality` gérés par le renderer et de l’injection éventuelle du `ContextQualityInjector`.
  - [x] Conserver `context_quality_instruction_injected` uniquement comme signal technique dérivé ou le faire converger vers ce nouveau champ, sans double vérité durable.
  - [x] Vérifier les cas `full`, `partial` et `minimal` avec et sans gestion template explicite.
  - [x] Verrouiller l’exclusivité entre `template_handled` et `injector_applied` ; si le template gère explicitement `context_quality`, l’injecteur ne doit pas ajouter une seconde compensation.

- [x] Task 6: Normaliser la source finale de `max_output_tokens` (AC1, AC5, AC6, AC7, AC8)
  - [x] Faire converger les valeurs existantes `length_budget`, `execution_profile`, `verbosity_default` vers une taxonomie canonique stable telle que `length_budget_global`, `execution_profile`, `verbosity_fallback`, `unset`.
  - [x] Exposer aussi `max_output_tokens_final` dans `GatewayMeta` ou dans le snapshot propagé.
  - [x] Calculer ce champ uniquement à l’endroit où l’arbitrage final est décidé, sans reconstruction avale en dashboard, export ou reporting.
  - [x] Préserver la compatibilité des assertions existantes de 66.18, ou documenter explicitement une migration de labels de test/rapport.

- [x] Task 7: Propager le snapshot vers `GatewayResult`, logs et persistance d’observabilité (AC1, AC6, AC7)
  - [x] Étendre `GatewayMeta` et, si nécessaire, `GatewayResult.to_log_dict()` pour exposer le snapshot complet.
  - [x] Mettre à jour `backend/app/llm_orchestration/services/observability_service.py` et le modèle persistant associé pour stocker les nouveaux champs utiles au diagnostic.
  - [x] Vérifier que les champs sont disponibles sans lecture du prompt brut ni parsing textuel libre.
  - [x] Éviter toute duplication entre métadonnées de résultat, log structuré et stockage DB.

- [x] Task 8: Mettre à jour métriques, dashboards et reporting d’évaluation (AC7, AC8, AC9, AC10)
  - [x] Étendre les métriques ou labels existants de manière compatible avec `llm_gateway_requests_total`, `llm_gateway_fallback_usage_total` et `llm_governance_event_total`.
  - [x] Mettre à jour `backend/tests/evaluation/report_generator.py` et les artefacts de campagne pour rendre visible au moins `pipeline_kind × execution_path_kind`.
  - [x] Préparer les agrégats opérationnels nécessaires pour `feature × execution_path_kind`, `feature × fallback_kind`, `feature × context_quality`, `feature × context_compensation_status`, `feature × executed_provider` et `feature × max_output_tokens_source`.
  - [x] Documenter explicitement toute nouvelle dépendance dashboard ou export.

- [x] Task 9: Ajouter la couverture de non-régression dédiée (AC1 à AC10)
  - [x] Créer une suite dédiée, par exemple `backend/tests/integration/test_story_66_25_execution_observability.py`.
  - [x] Couvrir au minimum : chemin canonique nominal, mapping `deprecated_use_case`, fallback `resolve_model()`, tolérance provider OpenAI non nominale, contexte `full`, contexte `partial` géré par template, contexte `minimal` compensé par injecteur, et les trois variantes d’arbitrage `max_output_tokens`.
  - [x] Vérifier la cohérence entre `GatewayResult.meta`, logs/événements et reporting d’évaluation.
  - [x] Protéger la sémantique de `pipeline_kind` introduite par 66.24.

## Dev Notes

### Objectif technique exact

Cette story ne change pas la doctrine métier ni la gouvernance existante. Elle transforme des distinctions déjà présentes en un socle d’observabilité unique et réutilisable.

Le but est qu’un opérateur puisse répondre immédiatement, pour une requête donnée :

- est-ce un chemin canonique ou une compat legacy ;
- quel fallback exact a été utilisé ;
- quel provider a été demandé, résolu et réellement exécuté ;
- quel était le niveau de `context_quality` ;
- si une compensation de contexte a été appliquée, et comment ;
- d’où vient la borne finale de `max_output_tokens`.

### Points d’attention d’implémentation

- Ne pas recalculer séparément les mêmes axes dans `GatewayMeta`, `observability_service.py`, les métriques et les dashboards. Une seule source de vérité est attendue.
- Ne pas réutiliser `pipeline_kind` comme substitut de `execution_path_kind`. `pipeline_kind` décrit la gouvernance de la famille ou de la cellule de matrice ; `execution_path_kind` décrit la réalité du chemin runtime de la requête.
- Ne pas confondre `fallback_kind` avec un booléen de fallback ni avec `execution_path_kind`. Ces axes sont complémentaires, pas interchangeables.
- Si plusieurs fallbacks s’enchaînent dans une même requête, l’implémentation doit appliquer la règle d’arbitrage documentée par la story ; aucun ordre implicite ne doit être laissé au hasard.
- Ne pas masquer un fallback provider non nominal derrière `provider="openai"` sans exposer le triplet `requested/resolved/executed`.
- Ne pas laisser coexister durablement deux taxonomies pour `max_output_tokens_source` (`length_budget` vs `length_budget_global`, `verbosity_default` vs `verbosity_fallback`, etc.). Si migration il y a, elle doit être explicitement encadrée.
- `max_output_tokens_source` et `max_output_tokens_final` doivent être figés exclusivement au moment du merge final du plan dans le gateway ; les couches aval ne doivent jamais les reconstituer localement.
- Si une coexistence temporaire est conservée avec `GatewayMeta.execution_path`, la compatibilité sémantique de cet ancien champ doit être explicitement testée jusqu’à sa dépréciation.
- La story doit privilégier une propagation d’objet ou de snapshot, pas une reconstruction à partir de messages de logs.

### Fichiers à inspecter en priorité

- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/observability_service.py`
- `backend/app/llm_orchestration/services/fallback_governance.py`
- `backend/app/llm_orchestration/providers/responses_client.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/tests/evaluation/evaluation_matrix.yaml`
- `backend/tests/evaluation/report_generator.py`
- `backend/tests/evaluation/test_prompt_resolution.py`
- `backend/tests/integration/test_story_66_21_governance.py`
- `backend/tests/integration/test_story_66_22_provider_locking.py`
- `backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py`
- `docs/llm-prompt-generation-by-feature.md`

### État actuel du code à garder en tête

- `ResolvedExecutionPlan` porte déjà `max_output_tokens`, `max_output_tokens_source`, `context_quality` et `context_quality_instruction_injected`.
- `GatewayMeta` expose encore `execution_path` avec une taxonomie ancienne (`nominal`, `repaired`, `fallback_use_case`, `test_fallback`) qui ne couvre pas toute la lecture d’exploitation attendue par cette story.
- `_build_result()` dans `backend/app/llm_orchestration/gateway.py` est aujourd’hui le point naturel pour assembler un snapshot unifié de métadonnées.
- `log_call()` dans `backend/app/llm_orchestration/services/observability_service.py` persiste déjà des dimensions techniques et constitue l’endroit naturel pour propager les nouveaux champs sans parsing fragile.
- `test_prompt_resolution.py` et `report_generator.py` portent déjà le discriminant `pipeline_kind` issu de 66.24 ; il faut capitaliser dessus sans casser leur sémantique.

### Testing Requirements

- Ajouter des tests couvrant explicitement :
  - `execution_path_kind=canonical_assembly` avec `fallback_kind=null` ;
  - `execution_path_kind=legacy_use_case_fallback` et `fallback_kind=deprecated_use_case_mapping` ;
  - `execution_path_kind=legacy_execution_profile_fallback` et `fallback_kind=resolve_model` ;
  - `execution_path_kind=non_nominal_provider_tolerated` avec divergence visible entre `requested_provider`, `resolved_provider` et `executed_provider` ;
  - `context_quality=full` avec `context_compensation_status=not_needed` ;
  - `context_quality=partial` avec `context_compensation_status=template_handled` ;
  - `context_quality=minimal` avec `context_compensation_status=injector_applied` ;
  - arbitrage `max_output_tokens` gagné par `LengthBudget.global_max_tokens` ;
  - arbitrage gagné par `ExecutionProfile.max_output_tokens` ;
  - arbitrage gagné par la recommandation issue de `verbosity_profile`.
- Ajouter un test explicite de non-régression sur la compatibilité sémantique de l’ancien `GatewayMeta.execution_path` si sa coexistence est conservée temporairement.
- Vérifier aussi la cohérence de taxonomie entre :
  - `GatewayResult.meta` ;
  - log structuré ;
  - métriques / événements ;
  - reporting d’évaluation.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest tests/integration/test_story_66_25_execution_observability.py -q`
  - `pytest -m evaluation -q`

### Contraintes d’architecture

- Ne pas ajouter de nouveau provider.
- Ne pas assouplir les verrouillages nominaux existants.
- Ne pas réintroduire un fallback silencieux.
- Ne pas changer la hiérarchie d’arbitrage sur `max_output_tokens`.
- Ne pas créer une seconde matrice d’évaluation ni un second modèle de dashboard concurrent.

### Previous Story Intelligence

- **66.21** a déjà centralisé la gouvernance des fallbacks et défini `llm_gateway_fallback_usage_total`. Cette story doit réutiliser ce vocabulaire comme base de `fallback_kind`, pas créer une taxonomie concurrente.
- **66.22** a durci le verrou provider et introduit la distinction nominal / non nominal pour la tolérance OpenAI. Cette story doit transformer cette distinction en lecture explicite `requested_provider / resolved_provider / executed_provider`.
- **66.23** a montré le pattern attendu pour une source de vérité transversale consommée par runtime, admin, logs et tests.
- **66.24** a introduit `pipeline_kind` dans la matrice d’évaluation et le reporting. Cette story doit compléter cette lecture avec `execution_path_kind`, sans altérer la gouvernance de campagne déjà en place.

### Git Intelligence

- `e6e59fa3` : `docs: finalize story 66.24 evaluation governance`
- `091cf204` : `feat(llm): implement evaluation gating and verified pipeline_kind (Story 66.24 fix)`
- `13aba6d5` : `feat(llm): extend evaluation matrix to daily paths and transitional governance (Story 66.24)`
- `494b45e1` : `docs(llm): align prompt generation doc with story 66.23`
- `7c9062b7` : `fix(llm): finalize story 66.23 taxonomy hardening`

Ces commits indiquent que le pattern récent privilégie :

- une source de vérité explicite ;
- des tests d’intégration dédiés par story ;
- un reporting d’évaluation enrichi plutôt qu’un mécanisme parallèle ;
- une synchronisation stricte entre documentation et runtime.

### References

- `docs/llm-prompt-generation-by-feature.md`
- `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- `_bmad-output/implementation-artifacts/66-21.md`
- `_bmad-output/implementation-artifacts/66-22.md`
- `_bmad-output/implementation-artifacts/66-23.md`
- `_bmad-output/implementation-artifacts/66-24.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Implémentation du snapshot canonique `ExecutionObservabilitySnapshot` dans le gateway avec projection vers `GatewayMeta`, persistance DB et télémétrie structurée.
- Ajout des taxonomies fermées pour `execution_path_kind`, `context_compensation_status` et `max_output_tokens_source`, avec alignement des labels legacy vers la taxonomie `66.25`.
- Exposition et persistance du triplet `requested_provider / resolved_provider / executed_provider` ainsi que de `fallback_kind`.
- Ajout de tests d’intégration ciblés sur l’observabilité runtime, dont le cas legacy `length_budget_global`.

### File List

- `_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/infra/db/models/llm_observability.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/services/observability_service.py`
- `backend/migrations/versions/8a839be9fea4_add_story_66_25_observability_fields.py`
- `backend/tests/evaluation/report_generator.py`
- `backend/tests/evaluation/test_prompt_resolution.py`
- `backend/tests/integration/test_story_66_22_provider_locking.py`
- `backend/tests/integration/test_story_66_25_observability.py`
- `backend/app/llm_orchestration/tests/test_story_66_18_stable_profiles.py`
