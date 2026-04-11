# Story 66.29: Extinction définitive du fallback `use_case-first` sur tous les chemins supportés

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want supprimer `USE_CASE_FIRST` comme mécanisme réel de résolution sur tous les chemins LLM supportés,
so that le runtime n’accepte plus qu’une composition canonique par assembly obligatoire, suivie uniquement de mécanismes d’exécution canoniques dérivés de cette assembly ou de la taxonomie canonique, et échoue immédiatement quand cette source de vérité est absente au lieu de retomber silencieusement sur un reliquat historique.

## Contexte

La story 66.21 a mis `USE_CASE_FIRST` au statut `à retirer` pour `chat`, `guidance`, `natal`, `horoscope_daily`. Les stories 66.20, 66.23 et 66.28 ont en parallèle fermé ces familles comme chemins nominaux canoniques. Pourtant, le code garde encore aujourd’hui `use_case-first` comme mécanisme de résolution réel dans le gateway :

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) continue d’appeler `_resolve_config()` puis `FallbackGovernanceRegistry.track_fallback(FallbackType.USE_CASE_FIRST, ...)` quand aucune assembly n’est retenue dans `_resolve_plan()`.
- La documentation canonique [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) raconte encore ce chemin comme une étape standard du pipeline (`resolve_config() / use_case-first` après l’échec assembly), tout en disant plus bas que `USE_CASE_FIRST` est `à retirer` sur les familles fermées.
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) classe déjà `USE_CASE_FIRST` comme `TO_REMOVE` avec `forbidden_families={"chat","guidance","natal","horoscope_daily"}`, mais ne fait aujourd’hui que bloquer certains cas nominaux ; il ne supprime pas la dépendance structurelle restante.
- [backend/tests/integration/test_story_66_21_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_21_governance.py) prouve le blocage sur familles fermées, mais conserve aussi l’idée qu’un `other_family` peut encore résoudre en `USE_CASE_FIRST` si l’assembly est absente.
- [backend/tests/evaluation/test_prompt_resolution.py](/c:/dev/horoscope_front/backend/tests/evaluation/test_prompt_resolution.py) et [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py) figent encore une taxonomie où `legacy_use_case_fallback` et `transitional_governance` restent des lectures runtime possibles dès qu’on sort du périmètre canonique, sans distinguer clairement les chemins réellement supportés de ceux qui devraient maintenant échouer.

Le reliquat principal n’est donc plus un vieux feature alias comme `daily_prediction`. C’est le fait qu’en cas d’absence d’assembly/config attendue, le système conserve encore un mécanisme opérationnel de secours basé sur le `use_case` historique au lieu de traiter l’absence comme une anomalie de configuration explicite.

Pour cette story, la cible n’est pas seulement de bloquer quelques familles fermées déjà connues. La cible est plus stricte :

- sur tout chemin **supporté** par la plateforme LLM moderne, la composition doit être canonique via assembly obligatoire ;
- les mécanismes d’exécution aval autorisés doivent rester ceux dérivés de cette assembly ou de la taxonomie canonique, jamais une résolution `use_case-first` ;
- l’absence d’assembly canonique obligatoire doit produire un échec explicite et traçable ;
- la télémétrie ne doit plus raconter un fallback legacy “toléré” là où l’on attend désormais une configuration obligatoire.

## Périmètre supporté à retenir

Pour cette story, un chemin est considéré comme **supporté** s’il remplit au moins une de ces conditions :

- il porte déjà une taxonomie canonique `feature/subfeature/plan` reconnue par le runtime ;
- il appartient à une famille explicitement fermée nominalement dans la documentation (`chat`, `guidance`, `natal`, `horoscope_daily`) ;
- il correspond à un alias legacy immédiatement normalisé vers une de ces familles fermées ;
- il fait partie des campagnes d’évaluation, seeds ou parcours applicatifs réellement maintenus.

Conséquence directe :

- un chemin supporté ne doit plus dépendre de `PromptRegistryV2.get_active_prompt(use_case)` ou des `USE_CASE_STUBS` comme mécanisme de composition nominale ;
- une `UseCaseConfig` historique peut éventuellement subsister comme artefact de validation ou de compatibilité bornée, mais jamais comme source canonique de composition ;
- si l’assembly canonique obligatoire n’existe pas, l’erreur doit être traitée comme défaut de configuration, pas comme compatibilité transitoire.

## Acceptance Criteria

1. **AC1 — Suppression du fallback nominal sur chemins supportés** : `_resolve_plan()` n’utilise plus `USE_CASE_FIRST` comme chemin de résolution nominal ou toléré pour tout chemin supporté. Sur ces parcours, la composition effective passe par assembly canonique obligatoire, puis par les mécanismes d’exécution canoniques dérivés de cette assembly ou de la taxonomie canonique, ou échoue explicitement.
2. **AC2 — Échec explicite en absence de source canonique** : lorsqu’un chemin supporté ne trouve pas l’assembly canonique obligatoire attendue, le gateway lève une erreur explicite de configuration/runtime (`GatewayConfigError` ou équivalent stable) au lieu de continuer via `_resolve_config()` ou une `UseCaseConfig` historique comme fallback structurel.
3. **AC3 — Aucune vérité concurrente runtime/doc** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) ne décrit plus `use_case-first` comme étape normale du pipeline sur les chemins supportés ; la doc distingue clairement compat legacy bornée et absence de configuration canonique.
4. **AC4 — Télémétrie de rejet dédiée** : l’absence d’assembly canonique obligatoire sur un chemin supporté émet un signal d’observabilité spécifique et non ambigu, distinct d’un fallback legacy réellement exécuté. La télémétrie doit permettre d’identifier au minimum `feature`, `subfeature`, `plan`, `use_case`, et la raison de rejet.
5. **AC5 — Observabilité d’erreur distincte du fallback** : un chemin supporté rejeté pour absence d’assembly canonique obligatoire publie un signal explicite de type `configuration error` ou taxonomie équivalente stable, distinct de tout fallback runtime réussi. Il ne doit pas être recyclé en `legacy_use_case_fallback`, `transitional_governance` toléré, ni faux succès nominal.
6. **AC6 — Règle centralisée de périmètre supporté** : la détermination du périmètre supporté repose sur une règle centralisée, réutilisée par gateway, gouvernance, observabilité et évaluation. Aucun set local divergent ne doit redéfinir séparément ce périmètre.
7. **AC7 — Non-régression de gouvernance** : `llm_gateway_fallback_usage_total` ne compte plus `USE_CASE_FIRST` comme événement nominal/toléré sur les chemins supportés. Si un usage legacy subsiste hors périmètre supporté, il reste explicitement borné et testé comme tel.
8. **AC8 — Cohérence du snapshot runtime** : `obs_snapshot.execution_path_kind` et `fallback_kind` ne publient plus `legacy_use_case_fallback` pour un chemin supporté qui aurait dû disposer d’une assembly canonique. Le résultat doit être soit `canonical_assembly`, soit une erreur explicite sans faux signal de fallback réussi.
9. **AC9 — Prévalidation sans réintroduction legacy** : la prévalidation amont par `UseCaseConfig` éventuelle ne peut pas servir de mécanisme de résolution, de légitimation ou de poursuite d’exécution sur un chemin supporté dépourvu d’assembly canonique. Si un accès précoce à une config reste nécessaire pour validation, il ne doit jamais autoriser la continuation d’un chemin qui devrait être rejeté.
10. **AC10 — Couverture tests sur les familles fermées** : des tests ciblés couvrent au minimum `chat`, `guidance`, `natal` et `horoscope_daily`, en vérifiant qu’une assembly canonique manquante produit un échec explicite et qu’aucun `USE_CASE_FIRST` n’est consommé comme issue nominale.
11. **AC11 — Couverture tests sur alias legacy normalisés** : lorsqu’un alias legacy est encore accepté en entrée puis normalisé vers une famille fermée, l’absence d’assembly canonique de la famille cible échoue explicitement ; l’alias ne rouvre pas un fallback `use_case-first`.
12. **AC12 — Compatibilité legacy bornée hors support** : si des use cases historiques hors périmètre supporté conservent encore `USE_CASE_FIRST`, cette exception est explicitement documentée, télémétrée et testée comme compatibilité résiduelle non nominale ; elle ne doit pas contaminer les familles supportées ni les métriques canoniques.
13. **AC13 — Matrice, rapports et documentation d’évaluation réalignés** : les suites d’évaluation, rapports, tests d’observabilité et la documentation associée ne considèrent plus `legacy_use_case_fallback` comme résultat acceptable sur un chemin supporté. Une absence de configuration canonique rend le cas bloquant/incomplet ou en erreur explicite selon le niveau de test, tandis que les vrais chemins legacy hors support restent identifiés séparément.

## Tasks / Subtasks

- [ ] Task 1: Définir et implémenter la règle d’extinction runtime (AC1, AC2, AC7)
  - [ ] Identifier précisément dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) tous les endroits où `_resolve_config()` peut encore servir de résolution effective après échec assembly.
  - [ ] Séparer clairement les responsabilités “validation d’input” et “résolution de plan” pour éviter qu’une config `use_case` historique ne masque l’absence d’assembly/config canonique attendue.
  - [ ] Introduire une règle explicite de détection du périmètre supporté, centralisée et réutilisable par gateway, gouvernance, observabilité et évaluation, au lieu de recalculer localement des familles fermées par sets hardcodés multiples.
  - [ ] Faire échouer immédiatement les chemins supportés sans source canonique, avec message stable et détails structurés.

- [ ] Task 2: Réaligner la gouvernance et la télémétrie de `USE_CASE_FIRST` (AC4, AC5, AC7, AC8, AC12)
  - [ ] Mettre à jour [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) pour que `USE_CASE_FIRST` ne soit plus enregistré comme fallback “réussi” sur les chemins supportés.
  - [ ] Ajouter un signal de rejet explicite côté gateway/observability quand une assembly canonique obligatoire manque, au lieu de recycler `legacy_use_case_fallback`.
  - [ ] Décider explicitement si ce rejet vit hors `GatewayResult` nominal ou via une taxonomie dédiée stable ; dans les deux cas, interdire tout recyclage de `transitional_governance` ou de `legacy_use_case_fallback` pour ce scénario.
  - [ ] Vérifier la cohérence entre `FallbackType`, `ExecutionPathKind`, `obs_snapshot`, logs structurés et métriques existantes.
  - [ ] S’assurer qu’aucune lecture aval ne transforme un rejet de configuration en `transitional_governance` tolérée.

- [ ] Task 3: Réaligner la documentation canonique et les garde-fous de lecture (AC3, AC6, AC13)
  - [ ] Corriger [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) dans les sections pipeline, fallback, observabilité et matrice d’évaluation.
  - [ ] Retirer du diagramme nominal la branche `resolve_config() / use_case-first` pour les chemins supportés, ou la requalifier explicitement comme compat résiduelle hors support.
  - [ ] Documenter la différence entre “chemin supporté sans assembly canonique” et “vrai chemin legacy encore toléré hors support”.
  - [ ] Réaligner aussi la documentation des rapports/matrices pour que l’erreur de configuration canonique ne soit plus racontée comme simple `transitional_governance`.

- [ ] Task 4: Ajouter la couverture de non-régression sur le vrai comportement attendu (AC7, AC8, AC10, AC11, AC13)
  - [ ] Étendre [backend/tests/integration/test_story_66_21_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_21_governance.py) avec des cas intégrés `_resolve_plan()` / `execute_request()` où l’assembly/config canonique manque sur `chat`, `guidance`, `natal`, `horoscope_daily`.
  - [ ] Adapter [backend/tests/evaluation/test_prompt_resolution.py](/c:/dev/horoscope_front/backend/tests/evaluation/test_prompt_resolution.py) et les suites liées pour qu’un chemin supporté sans source canonique soit bloquant, et non une simple variante `transitional_governance`.
  - [ ] Ajouter un test d’observabilité qui prouve l’absence de `legacy_use_case_fallback` dans `obs_snapshot` sur un chemin supporté rejeté.
  - [ ] Ajouter un test sur alias legacy normalisé (par exemple requête historiquement `daily_prediction`) pour vérifier qu’il n’ouvre pas `USE_CASE_FIRST`.

- [ ] Task 5: Vérification locale obligatoire (AC1 à AC11)
  - [ ] Après activation du venv PowerShell, exécuter `ruff format .` puis `ruff check .` dans `backend/`.
  - [ ] Exécuter `pytest -q` dans `backend/`.
  - [ ] Exécuter au minimum les suites ciblées liées à 66.21, 66.24, 66.25, 66.28 et à la nouvelle story 66.29.
  - [ ] Vérifier que les métriques/logs produits sur les cas de test reflètent bien “rejet canonique explicite” et non “fallback legacy toléré”.

## Dev Notes

### Diagnostic exact à préserver

- Le reliquat historique principal est dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py), où la résolution assembly échouée peut encore se transformer en résolution `_resolve_config()` + `USE_CASE_FIRST`.
- La dette n’est pas seulement technique ; elle est aussi narrative. La documentation continue de raconter `use_case-first` comme branche normale du pipeline, ce qui entretient une ambiguïté sur ce qui est réellement supporté.
- La présence de `USE_CASE_STUBS` et de `PromptRegistryV2.get_active_prompt()` n’est pas en soi le bug ; le bug est leur usage comme mécanisme de composition nominale tolérée là où une assembly canonique devrait être obligatoire.
- `daily_prediction` n’est plus le problème principal après 66.28. Le vrai problème restant est la persistance d’un modèle mental `assembly si possible, sinon use_case`, incompatible avec la fermeture canonique annoncée.
- La story doit faire la différence entre :
  - compatibilité legacy explicitement bornée hors support ;
  - et défaut de configuration sur un chemin supporté, qui doit être un échec.
- La zone la plus sensible est la prévalidation précoce par `UseCaseConfig` avant `_resolve_plan()` : elle peut subsister pour certaines validations techniques, mais ne doit jamais légitimer ni prolonger l’exécution d’un chemin supporté sans assembly canonique.

### Ce que le dev ne doit pas faire

- Ne pas simplement ajouter `other_family` à une liste d’interdiction sans traiter le mécanisme structurel restant.
- Ne pas masquer l’absence d’assembly canonique derrière un stub, un prompt publié par `use_case`, ou une pseudo “config canonique” dérivée d’une `UseCaseConfig` historique.
- Ne pas convertir un rejet de configuration en nouveau `execution_path_kind` opportuniste sans clarifier sa place dans le snapshot canonique.
- Ne pas corriger uniquement la documentation ou uniquement les tests : le runtime doit cesser d’utiliser `USE_CASE_FIRST` sur les chemins supportés.
- Ne pas réintroduire un hardcode concurrent de familles supportées dans plusieurs fichiers ; la règle de périmètre doit être centralisée ou au minimum cohérente.
- Ne pas conserver une chaîne de secours legacy du type `UseCaseConfig -> ExecutionProfileRegistry -> resolve_model() fallback` sur un chemin supporté en prétendant que `USE_CASE_FIRST` a disparu. La fermeture doit être end-to-end.
- Ne pas utiliser la prévalidation `UseCaseConfig` comme mécanisme de légitimation silencieuse d’un chemin sans assembly canonique.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/llm_orchestration/services/prompt_registry_v2.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_registry_v2.py)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/tests/integration/test_story_66_21_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_21_governance.py)
- [backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py)
- [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py)
- [backend/app/llm_orchestration/tests/test_story_66_28_closure.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_28_closure.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.20** a rendu l’assembly obligatoire sur `chat`, `guidance`, `natal`, `horoscope_daily`, mais le mécanisme `_resolve_config()` subsiste encore comme issue structurelle hors du cas assembly réussi.
- **66.21** a classé `USE_CASE_FIRST` comme `à retirer` sur les familles fermées, sans supprimer totalement sa place dans le pipeline.
- **66.22** a déjà montré le pattern attendu : un chemin nominal supporté manquant doit être rejeté explicitement, pas toléré silencieusement.
- **66.24** a introduit `pipeline_kind` dans la matrice d’évaluation ; cette story doit éviter qu’un chemin supporté sans assembly/config se présente encore comme simple cas `transitional_governance`.
- **66.25** a imposé un snapshot canonique unique d’observabilité ; la télémétrie de 66.29 doit s’aligner sur cette doctrine, pas créer une lecture concurrente.
- **66.28** a absorbé `daily_prediction` dans `horoscope_daily` ; un alias legacy normalisé ne doit pas rouvrir la porte à `USE_CASE_FIRST`.

### Git Intelligence

Commits récents pertinents observés :

- `85d2741b` : `docs(llm): finalize story 66.28 canonical guide`
- `8b48912a` : `test(llm): cover legacy daily admin lockout`
- `4acc5dd1` : `docs(llm): Update governance reference SHA for 66.28 ULTIMATE closure`
- `a511293c` : `feat(llm): Story 66.28 ULTIMATE closure - block resurrection via rollback and fix admin HTTP codes`
- `d02c7bbc` : `docs(llm): Update governance reference SHA for 66.28 FINAL closure`

Pattern à réutiliser :

- fermer la divergence au runtime avant de réécrire la doc ;
- traiter les reliquats legacy comme compatibilités bornées ou rejets explicites, pas comme chemins nominaux cachés ;
- accompagner la correction de tests ciblés et de télémétrie prouvant la fermeture.

### Testing Requirements

- Ajouter au minimum un test intégré par famille fermée (`chat`, `guidance`, `natal`, `horoscope_daily`) où l’assembly/config canonique est absente et où l’issue attendue est une erreur explicite, sans `USE_CASE_FIRST`.
- Ajouter un test prouvant qu’aucun compteur `llm_gateway_fallback_usage_total{fallback_type="use_case_first"}` n’est émis comme chemin nominal/toléré sur ces cas.
- Ajouter un test d’observabilité prouvant qu’un chemin supporté rejeté ne publie ni `execution_path_kind=legacy_use_case_fallback` ni `fallback_kind=deprecated_use_case`.
- Vérifier explicitement le cas d’un alias legacy normalisé vers une famille fermée.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest tests/integration/test_story_66_21_governance.py -q`
  - `pytest tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py -q`
  - `pytest tests/integration/test_story_66_25_observability.py -q`
  - `pytest app/llm_orchestration/tests/test_story_66_28_closure.py -q`
  - ajouter la suite dédiée 66.29 si elle est créée

### Project Structure Notes

- Travail backend + documentation uniquement.
- Aucun changement frontend n’est attendu.
- Les modifications doivent rester concentrées dans `backend/app/llm_orchestration/`, `backend/app/services/`, `backend/tests/` et `docs/`.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/llm_orchestration/services/prompt_registry_v2.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_registry_v2.py)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/tests/integration/test_story_66_21_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_21_governance.py)
- [backend/tests/evaluation/test_prompt_resolution.py](/c:/dev/horoscope_front/backend/tests/evaluation/test_prompt_resolution.py)
- [backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py)
- [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py)
- [backend/app/llm_orchestration/tests/test_story_66_28_closure.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_28_closure.py)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)
- [66-21.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-21.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-28-fermeture-canonique-daily-prediction-ou-suppression-statut-transitoire.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-28-fermeture-canonique-daily-prediction-ou-suppression-statut-transitoire.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story créée à partir des objectifs utilisateur et réalignée sur l’état réel du code après 66.28.
- Le diagnostic central est la persistance de `_resolve_config()` + `USE_CASE_FIRST` comme mécanisme de résolution réel après échec assembly sur des chemins que la doc déclare déjà supportés/canoniques.
- La story impose quatre garde-fous visibles : assembly canonique obligatoire comme source de composition, règle centralisée de périmètre supporté, erreur explicite si la source canonique manque, et télémétrie dédiée de rejet/non-régression.
- Implémentation fermée avec suppression effective du fallback `use_case-first` sur le périmètre supporté, propagation canonique de `input_schema` via assembly et rejet explicite si l’assembly obligatoire manque.
- La migration `8b2d52442493` ajoute la colonne `input_schema` sur `llm_assembly_configs` et backfill les assemblies déjà publiées depuis les `UseCaseConfig` legacy pour éviter une perte silencieuse de validation Stage 1.5.
- L’auto-heal du registre LLM relance désormais `seed_66_20_taxonomy()` pour réaligner les assemblies existantes avec les métadonnées canoniques (`input_schema`, `output_contract_ref`, `interaction_mode`, `user_question_policy`).
- Une couverture d’intégration Alembic vérifie désormais le backfill réel sur une base arrêtée juste avant `8b2d52442493`, afin de réduire le risque de régression entre migration DB et runtime canonique.

### File List

- `_bmad-output/implementation-artifacts/66-29-extinction-definitive-fallback-use-case-first-tous-chemins-supportes.md`
- `backend/tests/integration/test_story_66_29_extinction.py`
- `backend/app/tests/integration/test_migration_8b2d52442493_add_input_schema_to_assembly.py`
- `backend/migrations/versions/8b2d52442493_add_input_schema_to_assembly.py`
- `backend/app/main.py`
