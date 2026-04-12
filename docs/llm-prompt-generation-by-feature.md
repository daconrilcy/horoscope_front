# Génération des Prompts LLM par Feature

Ce document décrit le pipeline LLM réellement exécuté dans l'application après l'epic 66. Il est volontairement centré sur le runtime observé dans le dépôt, pas sur une architecture cible idéale.

Objectifs :

- donner une source de vérité exploitable par les développeurs ;
- rendre lisible l'ordre exact de résolution dans `LLMGateway.execute_request()` ;
- montrer où vivent les variations `feature/subfeature/plan`, persona, profils d'exécution, budgets, placeholders et fallbacks ;
- éviter de réintroduire des variations concurrentes entre `use_case`, assemblies, `ExecutionProfile` et paramètres provider.

## Portée

Le document couvre :

- les points d'entrée métier qui construisent `LLMExecutionRequest` ;
- la résolution canonique dans `backend/app/llm_orchestration/gateway.py` ;
- la composition assembly ;
- la résolution des profils d'exécution ;
- le verrou provider ;
- la gestion des placeholders, de `context_quality` et des budgets de longueur ;
- l'observabilité runtime ;
- la matrice d'évaluation et la gouvernance documentaire.

Il décrit le fonctionnement réel du backend autour de :

- `backend/app/services/ai_engine_adapter.py`
- `backend/app/services/natal_interpretation_service_v2.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/assembly_resolver.py`
- `backend/app/llm_orchestration/services/execution_profile_registry.py`
- `backend/app/llm_orchestration/services/prompt_renderer.py`
- `backend/app/llm_orchestration/services/context_quality_injector.py`
- `backend/app/llm_orchestration/services/provider_parameter_mapper.py`
- `backend/app/llm_orchestration/services/fallback_governance.py`
- `backend/app/llm_orchestration/supported_providers.py`
- `backend/app/prompts/catalog.py`

## Résumé exécutable

Le pipeline cible exécuté aujourd'hui est :

1. les services métier construisent un `LLMExecutionRequest` canonique ;
2. le gateway normalise tôt `feature`, `subfeature`, `plan` et les alias legacy `use_case -> feature` quand une entrée dépréciée vise une famille supportée ;
3. la prévalidation Stage 0.5 par `UseCaseConfig` n'existe plus que pour les features hors périmètre supporté ;
4. `_resolve_plan()` tente une résolution assembly si `feature/subfeature/plan` est présent ;
5. les familles supportées `chat`, `guidance`, `natal`, `horoscope_daily` échouent explicitement si aucune assembly canonique active n'est trouvée ; le fallback `use_case-first` est éteint sur ce périmètre ;
6. le gateway reconstruit ensuite une config dérivée du plan résolu et valide l'`input_schema` canonique en Stage 1.5 ;
7. le gateway résout ensuite le `ExecutionProfile` depuis l'assembly ou par waterfall. Sur le périmètre supporté (`chat`, `guidance`, `natal`, `horoscope_daily`), tout échec de résolution (profil manquant, provider non supporté, mapping impossible) lève une `GatewayConfigError` ; le fallback historique `resolve_model()` est strictement interdit.
8. au publish et au boot, un validateur de cohérence central contrôle aussi `execution_profile_ref`, waterfall, contrat de sortie, placeholders, persona et `LengthBudget` ; depuis 66.32, au startup, le scan priorise le snapshot de release actif ; sur le périmètre nominal supporté, l’absence de snapshot actif est un état invalide de configuration, pas un second mode nominal de vérité ;
9. le prompt est transformé dans cet ordre : assembly déjà concaténée, injection `context_quality`, injection de verbosité, rendu des placeholders ;
10. l'appel provider passe aujourd'hui nominalement uniquement par `openai` ;
11. la sortie est validée, éventuellement réparée, puis éventuellement basculée vers un `fallback_use_case` legacy uniquement hors périmètre supporté ;
12. le résultat final publie un snapshot d'observabilité canonique qui inclut aussi l'identité de la release active réellement exécutée.

Le `use_case` existe encore, mais il n'est plus la source canonique de variation sur les familles convergées. Il sert surtout de clé de compatibilité, de routage legacy, de sélection de schéma et de fallback résiduel pour les features hors périmètre supporté.

## Vue d'ensemble

```mermaid
flowchart TD
    A["Service métier<br/>AIEngineAdapter / Service V2"] --> B["Construit LLMExecutionRequest"]
    B --> C["LLMGateway.execute_request()"]
    C --> D["Normalisation taxonomie<br/>feature / subfeature / plan<br/>+ mapping legacy use_case"]
    D --> E{"Feature supportée ?"}
    E -->|Oui| F["Skip Stage 0.5"]
    E -->|Non| G["Validation rapide input schema<br/>via UseCaseConfig legacy"]
    F --> H["_resolve_plan()"]
    G --> H

    H --> I{"Assembly active ?"}
    I -->|Oui| J["resolve_assembly() + assemble_developer_prompt()"]
    I -->|Non| K{"Feature supportée ?"}
    K -->|Oui| L["Échec explicite de configuration<br/>+ telemetry de rejet dédiée"]
    K -->|Non| M["resolve_config() / use_case-first"]

    J --> N["Validation input schema canonique<br/>depuis le plan résolu"]
    M --> N

    N --> O["ExecutionProfileRegistry"]
    O --> P["Arbitrage provider / model / max_output_tokens"]
    Q["Transformations texte<br/>context_quality -> verbosity -> render"]
    Q --> R["ResolvedExecutionPlan"]
    R --> S["_build_messages()"]
    S --> T["_call_provider()"]
    T --> T1["ProviderRuntimeManager<br/>Retries + Breaker + RateLimit"]
    T1 --> T2["ResponsesClient.execute()"]
    T2 --> U["validate_output()"]

    U --> V{"Sortie valide ?"}
    V -->|Oui| W["_build_result() + obs_snapshot"]
    V -->|Non| X["_handle_repair_or_fallback()"]
    X --> W
```

## Source de vérité par couche

| Couche | Source de vérité | Rôle | Ne doit pas porter |
|---|---|---|---|
| Point d'entrée métier | `AIEngineAdapter`, `NatalInterpretationServiceV2` | construire `LLMExecutionRequest` à partir des données métier | logique provider, composition de prompt profonde |
| Taxonomie | `ExecutionUserInput.feature/subfeature/plan` + `feature_taxonomy.py` | identifier la famille canonique et normaliser les alias | style, budgets, paramètres provider |
| Compatibilité `use_case` | `backend/app/prompts/catalog.py` | `DEPRECATED_USE_CASE_MAPPING`, `PROMPT_CATALOG`, `resolve_model()` | gouvernance canonique d'une famille convergée |
| Composition | `PromptAssemblyConfig` + `resolve_assembly()` | sélectionner les blocs feature/subfeature/plan/persona/contrat/exécution | choix provider brut en dehors de l'execution config |
| Style | `LlmPersonaModel` + `compose_persona_block()` | ton, voix, vocabulaire, densité stylistique | hard policy, schéma JSON, logique d'accès |
| Exécution | `ExecutionProfileRegistry` + `ProviderParameterMapper` | provider, modèle, reasoning, verbosity, output mode, tool mode | contenu métier des prompts |
| Rendu | `PromptRenderer` | blocs `context_quality`, placeholders, validation de placeholders | choix du provider |
| Garde-fous | `FallbackGovernanceRegistry`, `supported_providers.py` | blocage des fallbacks et des providers interdits | composition métier du prompt |
| Cohérence publish/boot | `ConfigCoherenceValidator`, `run_llm_coherence_startup_validation()` | bloquer une config incohérente avant exécution ou au démarrage runtime, sur le snapshot actif pour le périmètre nominal supporté | simulation complète du métier ou fallback runtime |
| Release runtime | `LlmReleaseSnapshotModel`, `LlmActiveReleaseModel`, `ReleaseService` | figer et activer atomiquement le bundle `assembly/profile/schema/persona` réellement servi ; sur le périmètre nominal supporté, cette release active est obligatoire | édition directe d'artefacts vivants au moment de l'exécution |
| Vérité finale | `ResolvedExecutionPlan` | agrégation immuable de l'exécution courante, y compris la release active et l'entrée de manifest utilisée | persistance admin |

## Stories 66.9 à 66.32

| Story | Apport canonique | Impact runtime observable |
|---|---|---|
| `66.9` | doctrine abonnement | `entitlements` décident l'accès, `plan` module la profondeur |
| `66.10` | bornes persona | la persona reste une couche de style |
| `66.11` | `ExecutionProfile` | séparation texte / exécution |
| `66.12` | `LengthBudget` | consigne éditoriale + arbitrage `max_output_tokens` |
| `66.13` | placeholders | allowlist, classification et blocage sur familles fermées |
| `66.14` | `context_quality` | blocs template + injecteur de compensation |
| `66.15` | convergence assembly | chat, guidance, natal convergent via adapter + gateway |
| `66.16` | matrice d'évaluation | couverture structurée des familles et plans |
| `66.17` | doctrine de responsabilité | répartition explicite des règles |
| `66.18` | profils stables provider | mapping interne -> paramètres provider |
| `66.19` | migration narrator daily | `AIEngineAdapter.generate_horoscope_narration()` devient le chemin principal |
| `66.20` | fermeture nominale | assembly obligatoire pour `chat`, `guidance`, `natal`, `horoscope_daily` |
| `66.21` | gouvernance des fallbacks | blocage des fallbacks `à retirer` sur chemins nominaux |
| `66.22` | verrou provider | `openai` seul provider nominalement supporté |
| `66.23` | taxonomie natal | `feature="natal"` devient l'unique clé nominale |
| `66.24` | matrice daily | `pipeline_kind` distingue nominal et transitoire |
| `66.25` | observabilité | snapshot canonique unique dans `obs_snapshot` |
| `66.26` | gouvernance documentaire | doc et template PR deviennent obligatoires |
| `66.27` | propagation `context_quality` | `context_quality_handled_by_template` est figé dans le plan puis relayé jusqu'au snapshot et à la persistance |
| `66.28` | fermeture canonique daily | `daily_prediction` est absorbé dans `horoscope_daily`, les reliquats d'évaluation sont supprimés et les publications admin legacy sont bloquées |
| `66.29` | extinction fallback | fermeture définitive du fallback `use_case-first` sur le périmètre supporté (`chat`, `guidance`, `natal`, `horoscope_daily`) |
| `66.30` | extinction fallback d'exécution | `ExecutionProfile` devient obligatoire sur le périmètre supporté ; `resolve_model()` ne survit plus qu'hors support avec rejet explicite, `error_code` stable et compteur dédié |
| `66.31` | validation fail-fast de cohérence | publish et startup bloquent désormais les incohérences de configuration sur l'état publié actif, avec `error_code` structurés et scan startup borné à la cible runtime réellement résoluble |
| `66.32` | release snapshot atomique | le runtime nominal lit désormais un snapshot de release actif, activable et rollbackable, avec propagation de `active_snapshot_id/version` et `manifest_entry_id` dans le plan et l'observabilité |

## Familles et points d'entrée réels

| Famille | Point d'entrée observé | Taxonomie injectée | Statut de gouvernance |
|---|---|---|---|
| `chat` | `AIEngineAdapter.generate_chat_reply()` | `feature="chat"`, `subfeature="astrologer"` | `nominal_canonical` |
| `guidance` | `AIEngineAdapter.generate_guidance()` | `feature="guidance"`, `subfeature` dérivée du `use_case` | `nominal_canonical` |
| `natal` | `AIEngineAdapter.generate_natal_interpretation()` | `feature="natal"`, `subfeature` issue du `use_case_key` puis normalisée | `nominal_canonical` |
| `horoscope_daily` | `AIEngineAdapter.generate_horoscope_narration()` | `feature="horoscope_daily"`, `subfeature="narration"` | `nominal_canonical` |
| `support` | aucune orchestration LLM dédiée identifiée dans ce pipeline | aucune | ne pas documenter comme famille LLM active |

### Diagramme de routage par famille

```mermaid
flowchart LR
    A["Service métier"] --> B{"Entrée"}
    B -->|chat| C["generate_chat_reply()"]
    B -->|guidance| D["generate_guidance()"]
    B -->|natal| E["generate_natal_interpretation()"]
    B -->|daily narration| F["generate_horoscope_narration()"]

    C --> G["feature=chat<br/>subfeature=astrologer"]
    D --> H["feature=guidance<br/>subfeature=daily|weekly|contextual|event"]
    E --> I["feature=natal<br/>subfeature canonique"]
    F --> K["feature=horoscope_daily<br/>subfeature=narration"]

    G --> M["LLMGateway.execute_request()"]
    H --> M
    I --> M
    K --> M
```

## Ordre exact de résolution dans le gateway

L'ordre réel, tel qu'il ressort de `execute_request()` et `_resolve_plan()`, est le suivant :

1. lecture du `use_case`, de la taxonomie fournie et des flags de visite/réparation ;
2. mapping de compatibilité `DEPRECATED_USE_CASE_MAPPING` si le `use_case` est déprécié et qu'aucune `feature` n'a été fournie ;
3. normalisation précoce de `feature`, `subfeature` et `plan` ;
4. blocage des boucles de fallback (`visited_use_cases`) ;
5. merge du `context_dict` ;
6. Stage 0.5 : prévalidation `UseCaseConfig` seulement si la feature n'appartient pas au périmètre supporté ;
7. exécution de `_resolve_plan()` ;
8. enrichissement éventuel du common context via `CommonContextBuilder` ;
9. tentative de résolution assembly via `AssemblyRegistry` ;
10. blocage explicite si famille supportée sans assembly active ;
11. fallback `use_case-first` via `_resolve_config()` seulement hors périmètre supporté ;
12. résolution du `ExecutionProfile` par référence assembly, puis waterfall `feature+subfeature+plan`, puis `feature+subfeature`, puis `feature` ; sur le périmètre supporté, cette résolution lit d'abord le bundle du snapshot actif ;
13. arbitrage provider, modèle, timeout et `max_output_tokens` ;
14. résolution du schéma de sortie et du bloc persona si nécessaire, avec priorité au contenu figé du snapshot actif ;
15. gel du `ResolvedExecutionPlan`, y compris `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id` lorsque l'exécution provient d'une release active ;
16. Stage 1.5 : reconstruction d'une config dérivée du plan et validation de l'`input_schema` canonique ;
17. composition des messages ;
18. appel provider ;
19. validation de sortie ;
20. réparation éventuelle puis fallback `fallback_use_case` éventuel, uniquement hors périmètre supporté ;
21. construction du `GatewayResult` final et du snapshot d'observabilité, incluant l'identité de la release active réellement exécutée.

### Diagramme détaillé de `execute_request()` + `_resolve_plan()`

```mermaid
flowchart TD
    A["LLMExecutionRequest"] --> B{"use_case legacy<br/>et feature absente ?"}
    B -->|Oui| C["DEPRECATED_USE_CASE_MAPPING"]
    B -->|Non| D["Continuer"]
    C --> D
    D --> E["Normaliser feature/subfeature/plan"]
    E --> F{"Feature supportée ?"}
    F -->|Non| G["Stage 0.5<br/>_resolve_config() + validate_input()"]
    F -->|Oui| H["Skip Stage 0.5"]
    G --> I["_resolve_plan()"]
    H --> I

    I --> J["Construire/merger common context"]
    J --> K{"assembly_config_id ou feature ?"}
    K -->|Oui| L["AssemblyRegistry.get_active_config_sync()"]
    K -->|Non| M["Pas de branche assembly"]

    L --> N{"Assembly trouvée ?"}
    N -->|Oui| O["resolve_assembly()"]
    N -->|Non| P{"Feature supportée ?"}
    P -->|Oui| Q["GatewayConfigError + supported_perimeter_rejection"]
    P -->|Non| R["_resolve_config()"]

    M --> S{"Feature supportée ?"}
    S -->|Oui| Q
    S -->|Non| R
    O --> T["UseCaseConfig dérivée de l'assembly"]
    R --> U["UseCaseConfig legacy/config/stub"]

    T --> V["ExecutionProfileRegistry"]
    U --> V

    V --> W{"Profile trouvé ?"}
    W -->|Oui| X["provider/model/reasoning/verbosity/output/tool"]
    W -->|Non| Y{"Feature supportée ?"}
    Y -->|Oui| Z["GatewayConfigError + runtime_rejected<br/>reason=missing_execution_profile"]
    Y -->|Non| AA["resolve_model() fallback<br/>hors périmètre supporté"]

    X --> AB["Verrou provider + max_output_tokens"]
    AA --> AB
    AB --> AC["Résoudre persona + schema"]
    AC --> AD["Injecter context_quality"]
    AD --> AE["Injecter verbosité"]
    AE --> AF["PromptRenderer.render()"]
    AF --> AG["ResolvedExecutionPlan"]
    AG --> AH["Stage 1.5 validate_input()"]
```

## Assemblies et composition

`resolve_assembly()` est volontairement simple. Il ne fait pas tout le pipeline ; il produit un artefact intermédiaire `ResolvedAssembly`.

Composition réellement observée :

1. bloc `feature_template` ;
2. bloc `subfeature_template` si présent ;
3. bloc `plan_rules` si activé ;
4. injection éventuelle `LengthBudgetInjector` ;
5. injection éventuelle `ContextQualityInjector` ;
6. la persona n'est pas concaténée dans le developer prompt assembly ; elle reste un bloc séparé dans les messages ;
7. la hard policy est résolue à part via `get_hard_policy()`.

### Diagramme de composition assembly

```mermaid
flowchart LR
    A["PromptAssemblyConfig"] --> B["feature_template"]
    A --> C["subfeature_template"]
    A --> D["plan_rules_ref"]
    A --> E["persona_ref"]
    A --> F["execution_config"]
    A --> G["output_contract_ref"]
    A --> H["length_budget"]

    B --> I["assemble_developer_prompt()"]
    C --> I
    D --> I
    H --> I
    I --> J["Prompt après LengthBudget"]
    J --> K["ContextQualityInjector.inject()"]
    K --> L["developer_prompt assembly"]
    E --> M["compose_persona_block()"]
    F --> N["ExecutionConfigAdmin"]
    G --> O["Contrat de sortie"]
```

## Doctrine d'abonnement et normalisation de plan

La règle officielle reste :

1. `entitlements` décident si l'appel a le droit d'exister ;
2. `plan` module la profondeur, la longueur et certains réglages d'exécution ;
3. un `use_case` distinct n'est justifié que si le contrat métier ou le schéma de sortie change réellement.

Normalisation runtime actuellement codée dans `_normalize_plan_for_assembly()` :

- `premium`, `pro`, `ultra`, `full` -> `premium`
- toute autre valeur, absence comprise -> `free`

Conséquence importante :

- `horoscope_daily` (nommé ainsi depuis Story 66.19) absorbe désormais systématiquement les anciennes `daily_prediction`.
- Le gateway normalise le `plan` en `free` s'il est absent.
- La famille est désormais considérée comme nominale fermée.
- l'alias `daily_prediction` n'est toléré qu'en compatibilité d'entrée ; il ne peut plus être republié nominalement via l'admin.

## Taxonomie canonique natal

Depuis 66.23 :

- `feature="natal"` est l'unique identifiant nominal autorisé ;
- `feature="natal_interpretation"` est interdit sur les chemins nominaux ;
- les subfeatures canoniques natal sont non préfixées ;
- `normalize_subfeature()` convertit encore l'alias historique `natal_interpretation` vers `interpretation`.

En pratique côté adapter :

- `generate_natal_interpretation()` alimente `subfeature` à partir de `use_case_key` ;
- pour `natal_interpretation_short`, l'adapter remplace d'abord la valeur par `natal_interpretation` ;
- le gateway normalise ensuite cette valeur en `interpretation`.

## Placeholders et rendu

Le rendu effectif est porté par `PromptRenderer.render()` :

1. résolution des blocs `{{#context_quality:VALUE}}...{{/context_quality}}` ;
2. chargement de l'allowlist de placeholders ;
3. classification des placeholders (`required`, `optional`, `optional_with_fallback`) ;
4. remplissage ou blocage selon la feature et la politique ;
5. substitution finale `{{variable}}`.

### Règles observées

- les placeholders universels sont `locale`, `use_case`, `persona_name`, `last_user_msg` ;
- les familles nominales `chat`, `guidance`, `natal`, `horoscope_daily` bloquent les placeholders non autorisés ;
- l'allowlist hardcodée de `assembly_resolver.py` couvre explicitement `chat`, `guidance`, `natal` ;
- les chemins daily passent surtout leur contexte principal dans `question`, donc dépendent moins de placeholders assembly spécialisés.

## Context Quality

Le traitement de `context_quality` repose sur deux mécanismes distincts :

1. les blocs conditionnels dans les templates ;
2. l'injecteur `ContextQualityInjector`.

Le runtime essaye d'éviter la double compensation :

- si le prompt contient déjà `{{#context_quality:partial}}` ou `{{#context_quality:minimal}}`, l'injecteur ne rajoute rien ;
- sinon il ajoute une consigne de compensation adaptée à la feature.

### Observabilité et Propagation

Depuis 66.27, `ContextQualityInjector.inject()` ne se contente plus de signaler si une compensation a été injectée ; il remonte aussi si le niveau de qualité dégradé est déjà pris en charge par le prompt/template courant.

Le code calcule et propage donc `context_quality_handled_by_template` dans `_resolve_plan()`. Ce booléen est figé dans le `ResolvedExecutionPlan` et sert de source de vérité pour l'observabilité.

Conséquences runtime observées :

- `template_handled` est publié dans `obs_snapshot.context_compensation_status` quand le template courant gère explicitement `partial` ou `minimal` ;
- `injector_applied` est publié uniquement lorsqu'une consigne de compensation a réellement été ajoutée ;
- la persistance `llm_call_logs.context_compensation_status` relaie la valeur du snapshot canonique, sans recalcul concurrent dans la couche d'observabilité.

## Profils d'exécution

Le profil d'exécution est résolu dans cet ordre :

1. `execution_profile_ref` de l'assembly active ;
2. waterfall `feature + subfeature + plan` ;
3. waterfall `feature + subfeature` ;
4. waterfall `feature` ;
5. fallback `resolve_model()` uniquement hors périmètre supporté et seulement pour une compatibilité legacy explicitement bornée par la gouvernance centrale.

Les abstractions internes stables exposées sont :

| Champ | Valeurs |
|---|---|
| `reasoning_profile` | `off`, `light`, `medium`, `deep` |
| `verbosity_profile` | `concise`, `balanced`, `detailed` |
| `output_mode` | `free_text`, `structured_json` |
| `tool_mode` | `none`, `optional`, `required` |

Le mapper provider traduit ensuite ces profils :

- OpenAI : `reasoning_effort`, `response_format`, `tool_choice`
- Anthropic : mapping préparé dans le code, mais non nominalement supporté par la plateforme

Sur le périmètre supporté :

- absence de profil -> `GatewayConfigError` avec `error_code="missing_execution_profile"` ;
- provider non supporté -> `GatewayConfigError` avec `error_code="unsupported_execution_provider"` ;
- échec de mapping provider -> `GatewayConfigError` avec `error_code="provider_mapping_failed"` ;
- ces rejets publient un événement `runtime_rejected` et incrémentent le compteur dédié `llm_runtime_rejection_total`.
- un `ResolvedExecutionPlan` supporté ne peut plus être construit avec `execution_profile_source="fallback_resolve_model"` ou `"fallback_provider_unsupported"`, même via mock ou injection incohérente.

## Validation fail-fast publish et startup

Depuis 66.31, la doctrine n'est plus seulement documentaire. Une validation centrale `ConfigCoherenceValidator` est exécutée :

- au publish d'une assembly via `AssemblyAdminService.publish_config()` ;
- au boot runtime via `run_llm_coherence_startup_validation()` appelé depuis `main.py` ;
- avec un mode startup `strict|warn|off` piloté par `LLM_COHERENCE_VALIDATION_MODE`.

Depuis 66.32, ce scan startup suit une hiérarchie explicite :

- s'il existe un `active_snapshot_id`, le boot revalide d'abord le manifest complet du snapshot actif ;
- cette revalidation travaille sur le bundle figé du snapshot pour `assembly`, `profile`, `schema` et `persona`, sans fallback silencieux vers les tables vivantes sur le périmètre supporté ;
- le scan des tables publiées “les plus récentes par cible” ne reste qu'un fallback pour les chemins hors périmètre supporté ou pour une phase transitoire explicitement non nominale.

Le scan startup reste volontairement borné :

- il ne parcourt pas l'historique complet ;
- il ignore les snapshots non actifs, les archives, brouillons et anciennes versions `published` non retenues comme état actif ;
- s'il n'y a pas de snapshot actif, il ne peut pas considérer le périmètre nominal supporté comme correctement configuré ;
- hors périmètre nominal supporté, il peut encore dédupliquer par cible runtime (`feature`, `subfeature`, `plan`, `locale`) et ne valider que la version publiée la plus récente par cible ;
- il ne contrôle donc que les artefacts effectivement résolubles par le runtime nominal courant.

### Ce que valide concrètement 66.31 puis 66.32

- `execution_profile_ref` explicite si présent, sinon waterfall canonique `feature+subfeature+plan -> feature+subfeature -> feature` ;
- absence de retour à `resolve_model()` comme issue de validation sur le périmètre supporté ;
- `output_contract_ref` résolu par UUID ou par nom, pour rester aligné avec les seeds et avec la résolution runtime, avec contrôle documentaire attendu de cohérence avec `output_mode` du profil effectivement résolu ;
- placeholders validés statiquement contre l'allowlist et la structure attendue de la famille canonique, sans mini-runtime ;
- persona existante et activée lorsqu'elle est référencée ;
- invariants `plan_rules` / `LengthBudget` ;
- interdiction des dépendances legacy sur les familles nominales fermées.

Depuis 66.32, la nuance critique est la suivante :

- la validation d'un snapshot actif ou candidat se fait sur le manifest et le bundle gelé, pas sur un recalcul opportuniste à partir des lignes live ;
- si un bundle est fourni au validateur, l'absence d'un `profile`, `schema` ou `persona` requis dans ce bundle est une erreur de release, pas une invitation à relire la table source ;
- cela garantit qu'une release activable reste auto-suffisante pour son périmètre nominal supporté et qu'un rollback réactive bien un état cohérent `N-1`.

## Release snapshot active et rollback

Depuis 66.32, le périmètre nominal convergé (`chat`, `guidance`, `natal`, `horoscope_daily`) ne lit plus une simple constellation de lignes `published`. Il lit une release active explicite :

- `LlmReleaseSnapshotModel` stocke un manifest immutable des bundles runtime par cible ;
- `LlmActiveReleaseModel` porte le pointeur d'activation courant ;
- `ReleaseService` expose `build_snapshot`, `validate_snapshot`, `activate_snapshot` et `rollback` ;
- l'activation invalide les caches runtime post-commit ;
- le rollback `N-1` réactive le snapshot précédent au lieu de republier manuellement chaque artefact.

Sur le périmètre nominal convergé, cette release active n'est pas optionnelle :

- `chat`, `guidance`, `natal` et `horoscope_daily` doivent disposer d'un snapshot actif pour être considérés comme exécutablement cohérents ;
- l'absence de snapshot actif y est un défaut de configuration à rejeter au boot et au runtime ;
- il n'y a donc plus deux modes de vérité nominaux, mais une seule vérité runtime canonique : la release active.

### Nature du gel par artefact

Le manifest ne se contente pas de stocker des pointeurs abstraits. Il capture, artefact par artefact, ce qui est nécessaire pour rejouer fidèlement l'exécution :

- `PromptAssemblyConfigModel` : copie figée complète de l'assembly runtime, y compris ses références et dépendances de composition sérialisées ;
- `LlmExecutionProfileModel` : copie figée complète du profil effectivement résolu pour la cible, même si ce profil existe aussi comme artefact versionné en table ;
- `LlmOutputSchemaModel` : copie figée complète du contrat runtime nécessaire à l'exécution, stockée comme bundle `schema` ;
- `LlmPersonaModel` : copie figée complète de la persona runtime nécessaire à l'exécution, portée dans l'assembly sérialisée ;
- `LlmPromptVersionModel` transitivement requis : contenu figé déjà capturé dans les blocs de template sérialisés de l'assembly.

Autrement dit :

- le runtime peut s'appuyer sur des IDs immutables comme métadonnées de traçabilité ;
- mais le rollback fidèle ne dépend pas d'une relecture live de ces objets sur le périmètre nominal supporté ;
- la règle de sûreté est “bundle exécutable auto-suffisant”, pas “liste de références à recharger plus tard”.

Conséquences de lecture runtime :

- `AssemblyRegistry` résout d'abord l'assembly depuis le snapshot actif ;
- `ExecutionProfileRegistry` et le gateway réutilisent le bundle attaché à l'assembly résolue pour éviter tout mélange avec les tables vivantes ;
- `ConfigCoherenceValidator.scan_active_configurations()` revalide d'abord le snapshot actif au boot ;
- les tables sources restent un backing store d'édition et de build, pas la vérité finale de l'exécution nominale quand un snapshot actif existe.

### Taxonomie minimale des erreurs de cohérence

Les erreurs stables de cohérence à utiliser côté publish/startup sont les suivantes :

- `missing_execution_profile`
- `invalid_execution_profile_ref`
- `unsupported_execution_provider`
- `missing_output_contract`
- `invalid_output_contract_ref`
- `placeholder_policy_violation`
- `persona_not_allowed`
- `plan_rules_scope_violation`
- `length_budget_scope_violation`
- `legacy_dependency_forbidden`

### Surface API admin

En cas de rejet au publish assembly, l'API admin renvoie un payload d'erreur structuré dédié :

- `error.code = "coherence_validation_failed"` ;
- `error.details.errors[*].error_code` contient les codes de cohérence détaillés ;
- cette erreur reste distincte des rejets runtime et ne doit pas être interprétée comme un `execution_path_kind` nominal.

## Durcissement Provider OpenAI (Story 66.33)

Depuis 66.33, l'appel nominal à OpenAI est protégé par un **Provider Runtime Hardening Layer** porté par `ProviderRuntimeManager`.

### 1. Politique de Retry Bornée
- Les retries implicites du SDK OpenAI sont désactivés (`max_retries=0`).
- Le retry est piloté par l'application avec un backoff exponentiel et jitter.
- Classification explicite des erreurs :
    - **Retryable** : Timeouts, erreurs de connexion, erreurs 5xx, erreurs 409 (Conflict).
    - **Terminal** : Quota épuisé, erreurs d'authentification, Bad Request (400).
- Budget de retry global épuisé -> `RetryBudgetExhaustedError`.

### 2. Timeouts par Famille
Le runtime n'utilise plus un timeout global unique. Les timeouts sont résolus par `feature` (famille) :
- `chat` : 30s
- `guidance` : 30s
- `natal` : 120s
- `horoscope_daily` : 60s
- Valeur par défaut : 30s

### 3. Circuit Breaker
Un circuit breaker est maintenu par couple `provider:family` (ex: `openai:chat`).
- État **OPEN** si le seuil d'échecs (`AI_ENGINE_CB_FAILURE_THRESHOLD`, défaut 5) est atteint.
- Blocage immédiat des requêtes suivantes pendant une période de cooldown (`AI_ENGINE_CB_RECOVERY_TIMEOUT_SEC`, défaut 60s) -> `UpstreamCircuitOpenError`.
- Passage en **HALF_OPEN** pour laisser passer une sonde après le cooldown.
- L'évaluation d'ouverture repose sur une fenêtre glissante de défaillances ; un historique ancien ne doit pas garder durablement le breaker en posture défensive.

### 4. Gestion fine des Rate Limits
- Utilisation de `.with_raw_response` pour accéder aux headers HTTP.
- Extraction du header `Retry-After` pour caler le délai de retry applicatif.
- Distinction nette entre rate limit passager et épuisement définitif du quota.
- Les erreurs serveur provider (`5xx`) sont séparées des timeouts, des erreurs de connexion et de `retry_budget_exhausted`.

### 5. Contrat aval et taxonomie propagée
Le runtime provider n'est plus écrasé en un unique `llm_unavailable`.
- `UpstreamCircuitOpenError` est mappée en `503` avec `code="upstream_circuit_open"`.
- `RetryBudgetExhaustedError` est mappée en `502` avec `code="retry_budget_exhausted"`.
- `UpstreamRateLimitError` conserve `429` et propage `retry_after_ms`.
- `UpstreamTimeoutError` conserve `504`.
- Les erreurs `bad_request`, `auth/config`, `connection_error` et `server_error` restent distinguables via `details` et la taxonomie adapter/runtime.

### 6. Observabilité Opérationnelle
Le snapshot d'observabilité et les logs `llm_call_logs` sont enrichis :
- `executed_provider_mode` : nominal ou dégradé.
- `attempt_count` : nombre total de tentatives pour l'appel.
- `provider_error_code` : code d'erreur brut renvoyé par OpenAI.
- `breaker_state` / `breaker_scope` : état du circuit au moment de l'appel.
- Ces champs sont aussi persistés sur le chemin d'erreur `log_call(error=...)`, y compris pour `circuit_open`.
- Un résultat servi en mode dégradé ne doit jamais compter comme succès nominal provider.

## Verrou provider

Le support provider nominal est porté par une source de vérité unique :

- `backend/app/llm_orchestration/supported_providers.py`
- `NOMINAL_SUPPORTED_PROVIDERS = ["openai"]`

Conséquences runtime :

- `openai` est le seul provider nominalement autorisé ;
- un provider non supporté sur un chemin nominal provoque un échec explicite ;
- un provider non supporté sur un chemin non nominal peut être toléré avec fallback vers OpenAI ;
- `_call_provider()` n'exécute effectivement que `openai`.

### Diagramme de verrou provider

```mermaid
flowchart TD
    A["ExecutionProfile résolu"] --> B["provider demandé"]
    B --> C{"provider dans NOMINAL_SUPPORTED_PROVIDERS ?"}
    C -->|Oui| D["ProviderParameterMapper.map()"]
    C -->|Non| E{"Chemin nominal ?"}
    E -->|Oui| F["GatewayConfigError<br/>error_code=unsupported_execution_provider<br/>+ runtime_rejected"]
    E -->|Non| G["log_governance_event(non_nominal_tolerated)"]
    G --> H["Fallback vers resolve_model() + provider=openai"]
    D --> I["_call_provider()"]
    H --> I
    I --> J["ResponsesClient.execute()"]
```

## Pilotage de la longueur

Deux couches distinctes coexistent :

### 1. Couche éditoriale

`LengthBudget` injecte une consigne de longueur dans le developer prompt :

- `target_response_length`
- `section_budgets`
- `global_max_tokens`

### 2. Couche technique

L'exécution provider arbitre `max_output_tokens` dans cet ordre :

1. `LengthBudget.global_max_tokens`
2. `ExecutionProfile.max_output_tokens`
3. recommandation issue de `verbosity_profile`
4. sinon valeur héritée de la config/stub

## Fallbacks et gouvernance

Le registre de gouvernance est `FallbackGovernanceRegistry`.

Points structurants observés :

- `USE_CASE_FIRST` est `à retirer` sur `chat`, `guidance`, `natal`, `horoscope_daily` ;
- sur ces familles supportées, l'absence d'assembly canonique obligatoire n'est plus racontée comme un fallback : c'est un rejet explicite de configuration avec télémétrie dédiée ;
- `RESOLVE_MODEL` est désormais `à retirer` sur `chat`, `guidance`, `natal`, `horoscope_daily` ;
- `NARRATOR_LEGACY` est interdit sur `horoscope_daily` ;
- `TEST_LOCAL` est interdit en production ;
- un fallback `à retirer` sur un chemin nominal lève une `GatewayError`, même si la famille n'est pas explicitement listée comme interdite ;
- chaque fallback réel passe par la métrique `llm_gateway_fallback_usage_total`.
- l'alias legacy `daily_prediction` peut encore être accepté en entrée, mais il est remappé immédiatement vers `horoscope_daily` et ne peut plus être réactivé via `publish` ou `rollback` admin.
- l'input schema canonique des assemblies supportées est désormais persisté dans `llm_assembly_configs.input_schema`, backfillé par la migration `8b2d52442493` et réaligné par `seed_66_20_taxonomy()`.

## Observabilité runtime

Depuis 66.25, le gateway publie un snapshot canonique unique dans `result.meta.obs_snapshot`.

Champs observés :

- `pipeline_kind`
- `execution_path_kind`
- `fallback_kind`
- `requested_provider`
- `resolved_provider`
- `executed_provider`
- `context_quality`
- `context_compensation_status`
- `max_output_tokens_source`
- `max_output_tokens_final`
- `active_snapshot_id`
- `active_snapshot_version`
- `manifest_entry_id`

### Axes de lecture

| Axe | Sens |
|---|---|
| `pipeline_kind` | statut de gouvernance attendu de la famille |
| `execution_path_kind` | chemin structurel effectivement emprunté |
| `fallback_kind` | cause dominante de fallback si fallback réel |
| provider triplet | provider demandé, résolu, exécuté |
| `context_compensation_status` | compensation de contexte observée |
| `max_output_tokens_source` | source finale de l'arbitrage de sortie |
| `active_snapshot_id/version` | release active réellement exécutée |
| `manifest_entry_id` | entrée de manifest exacte utilisée pour cette exécution |

Pour l'axe `context_compensation_status`, la lecture correcte est désormais :

- `not_needed` : `context_quality=full` ;
- `template_handled` : le prompt courant gère déjà explicitement le niveau dégradé ;
- `injector_applied` : une consigne additionnelle a été injectée ;
- `unknown` : l'information n'est pas déterminable sur le chemin considéré.

### Taxonomies actuellement exposées

#### `pipeline_kind`

- `nominal_canonical` pour `chat`, `guidance`, `natal`, `horoscope_daily`
- `transitional_governance` pour le reste (ex: use cases legacy non encore migrés)

#### `execution_path_kind`

- `canonical_assembly`
- `legacy_use_case_fallback`
- `legacy_execution_profile_fallback`
- `repair`
- `non_nominal_provider_tolerated`

Important :

- un chemin supporté rejeté faute d'assembly canonique obligatoire n'émet pas de `GatewayResult` de succès avec `legacy_use_case_fallback` ;
- un chemin supporté rejeté faute d'`ExecutionProfile` valide n'émet pas de `GatewayResult` de succès avec `legacy_execution_profile_fallback` ni `non_nominal_provider_tolerated` ;
- ce scénario est visible via l'erreur explicite et la télémétrie de rejet (`supported_perimeter_rejection`), pas via un faux chemin nominal.

### Garde-fou de maintenance

Toute future PR doit préserver l'invariant suivant :

- aucune valeur legacy interdite (`fallback_resolve_model`, `fallback_provider_unsupported`, `legacy_execution_profile_fallback`, `non_nominal_provider_tolerated`) ne doit réapparaître comme état acceptable pour `chat`, `guidance`, `natal`, `horoscope_daily` ;
- cette interdiction vaut autant pour les enums et modèles runtime que pour les fixtures admin, plans mockés, snapshots d'observabilité et assertions de tests ;
- si une compatibilité hors support est encore testée, elle doit rester explicitement bornée à un chemin non nominal ou legacy hors périmètre supporté.

### Rejets canoniques

Lorsqu'un chemin supporté échoue faute d'assembly canonique obligatoire ou faute d'`ExecutionProfile` exploitable :

- le runtime lève une erreur explicite de configuration au lieu de produire un `GatewayResult` nominal ;
- le scénario n'est donc pas encodé comme `execution_path_kind` de succès ;
- la lecture ops passe par la télémétrie de rejet dédiée, en particulier l'événement structuré (`supported_perimeter_rejection` ou `runtime_rejected`), les logs structurés associés, et pour 66.30 le compteur dédié `llm_runtime_rejection_total` avec un label `reason` discriminant ;
- l'absence volontaire de `execution_path_kind` dédié évite de confondre un rejet canonique avec un chemin d'exécution réellement complété.

#### `fallback_kind`

- nullable quand aucun fallback réel n'est observé ;
- sinon résumé dominant aligné sur la gouvernance.

### Diagramme de lecture de l'observabilité

```mermaid
flowchart LR
    A["ResolvedExecutionPlan"] --> B["pipeline_kind"]
    A --> C["execution_path_kind"]
    A --> D["provider triplet"]
    A --> E["max_output_tokens_source"]
    A --> F["context_quality"]
    A --> G["context_compensation_status"]
    H["RecoveryResult"] --> C
    H --> I["fallback_kind"]
    B --> J["obs_snapshot"]
    C --> J
    D --> J
    E --> J
    F --> J
    G --> J
    I --> J
    J --> K["GatewayMeta"]
    J --> L["llm_call_logs"]
    J --> M["métriques"]
    J --> N["rapports d'évaluation"]
```

## Matrice d'évaluation

La validation ne repose pas seulement sur les tests unitaires. Une matrice d'évaluation croise :

- `feature`
- `plan`
- `persona`
- `context_quality`
- `pipeline_kind`

Elle vérifie notamment :

- absence de placeholders survivants ;
- application des budgets ;
- différenciation de persona ;
- stabilité des contrats ;
- cohérence entre gouvernance attendue et chemin observé.

Depuis 66.24 (mis à jour en 66.28) :

- `horoscope_daily` est évalué comme `nominal_canonical` ;
- `daily_prediction` a été absorbé dans `horoscope_daily` et n'apparaît plus comme famille autonome ;
- un chemin obligatoire manquant rend la campagne incomplète ou bloquante.

## Où mettre une nouvelle règle

| Besoin | Endroit correct |
|---|---|
| varier la profondeur free/premium sans changer le schéma | `plan_rules` + `LengthBudget` |
| changer le provider ou le modèle | `ExecutionProfile` |
| rendre le style plus empathique | persona |
| changer la structure JSON de sortie | contrat / schéma de sortie |
| injecter une donnée utilisateur | placeholder autorisé + politique de résolution |
| adapter le ton à un contexte incomplet | `context_quality` |

## Violations fréquentes à éviter

- mettre un nom de modèle dans un template métier ;
- demander du JSON dans une persona ;
- encoder une logique de feature dans des `plan_rules` ;
- utiliser `max_output_tokens` comme substitut d'une consigne éditoriale ;
- créer un nouveau `use_case_free` alors que seul le niveau de détail change ;
- documenter comme “nominal” un chemin qui n'est observé qu'en compatibilité ou en test.

## Règle de lecture

- une affirmation n'est présente ici que si elle est appuyée par une source explicite du dépôt ;
- lorsqu'un comportement est supporté par les types/tests mais pas complètement propagé par le runtime, cette nuance est écrite explicitement ;
- si le code diverge, le code fait foi jusqu'à mise à jour de cette documentation.

## Maintenance de cette documentation

Ce document constitue une **règle d'ingénierie explicite**. Sa maintenance est **obligatoire** et **traçable**.

### Discipline de mise à jour et règle de PR

Toute Pull Request modifiant la structure ou la gouvernance du pipeline LLM doit :

1. Soit mettre à jour ce document dans le même change set pour refléter la nouvelle réalité technique.
2. Soit justifier explicitement dans la description de la PR pourquoi ce document reste valide sans changement.

### Zones à impact documentaire obligatoire

La revue de ce document est **obligatoire** pour toute modification portant sur :

- **Gateway & Orchestration** : `_resolve_plan()`, `execute_request()`, `_call_provider()`, `_handle_repair_or_fallback()`, `_build_messages()`
- **Composition & Rendu** : `PromptRenderer`, `PromptAssemblyConfig`, `context_quality`, `ContextQualityInjector`, budgets de longueur
- **Paramétrage & Fallbacks** : `ProviderParameterMapper`, `FallbackGovernanceRegistry`, `NOMINAL_SUPPORTED_PROVIDERS`
- **Taxonomie & Profils** : taxonomie canonique `feature/subfeature/plan`, `ExecutionProfile`
- **Doctrine & Contrats** : toute logique modifiant la source de vérité décrite dans les sections précédentes

### Vérification et Traçabilité

Toute mention de vérification ci-dessous atteste d'une **revue manuelle effective** contre le code réel à la référence indiquée. Les références flottantes (`HEAD`, `main`, etc.) sont interdites.

Dernière vérification manuelle contre le pipeline réel du gateway :

- **Date** : `2026-04-12`
- **Référence stable (Commit SHA)** : `affb4f69`

Si le code diverge, le pipeline réel du gateway fait foi jusqu'à mise à jour de cette documentation, mais l'absence de mise à jour constitue une **dette de gouvernance**.
