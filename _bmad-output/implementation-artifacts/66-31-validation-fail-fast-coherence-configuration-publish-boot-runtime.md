# Story 66.31: Validation fail-fast de cohérence de configuration au publish et au boot runtime

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want transformer la doctrine LLM en validation de cohérence exécutable au publish et au démarrage runtime,
so that une configuration invalide ou incohérente est bloquée immédiatement avec une erreur stable et traçable, au lieu d’être seulement décrite dans la documentation puis découverte tardivement à l’exécution.

## Contexte

Les stories 66.17 à 66.30 ont progressivement clarifié les sources de vérité du pipeline LLM :

- l’assembly est devenue la source canonique de composition ;
- `ExecutionProfile` est devenue la source canonique d’exécution ;
- les familles supportées (`chat`, `guidance`, `natal`, `horoscope_daily`) ne doivent plus tolérer les reliquats legacy ;
- les placeholders, personas, budgets de longueur et contrats de sortie sont désormais encadrés par une doctrine explicite.

Le dépôt contient déjà plusieurs garde-fous, mais ils restent fragmentés et partiels :

- [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py) revalide les placeholders et le provider au publish d’une assembly, mais ne vérifie pas la cohérence transverse complète entre `execution_profile_ref`, `output_contract_ref`, `persona_ref`, `plan_rules_ref`, `length_budget`, périmètre supporté et dépendances legacy.
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py) bloque déjà certains providers non supportés et certains identifiants legacy au moment du publish d’un `ExecutionProfile`, mais ce contrôle reste isolé du publish des assemblies et ne garantit pas qu’une assembly publiée pointe vers un profil réellement exploitable.
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) orchestre déjà plusieurs validations startup (`feature_scope`, `canonical_db`, `stripe_portal`, `validate_catalog_vs_db`), ce qui fournit un pattern clair pour un nouveau garde-fou de boot ; pourtant aucune validation de cohérence transverse LLM ne scanne aujourd’hui l’ensemble des assemblies/profils/personas/contrats publiés avant d’accepter le démarrage.
- [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py) encode déjà des lints d’architecture sur les templates et les `plan_rules`, mais ces signaux ne sont pas encore intégrés à une validation atomique de publication/configuration.
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py) porte déjà la règle centrale du périmètre supporté et la normalisation des aliases legacy ; cette règle doit devenir la base de décision unique pour les validations publish-time et boot-time.
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) et [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md) décrivent déjà où vivent `ExecutionProfile`, `output_contract_ref`, persona, placeholders et budgets, mais ces documents restent principalement descriptifs.

Le problème n’est donc plus l’absence de doctrine. Le problème est l’absence d’un vérificateur central unique qui affirme automatiquement :

- qu’une assembly active pointe vers un `ExecutionProfile` valide et publiable ;
- qu’un contrat de sortie référencé existe et reste compatible avec la famille ;
- qu’un provider nominalement interdit n’est pas réintroduit au publish ou au boot ;
- que les placeholders exigés par la famille et la persona restent cohérents ;
- que la persona autorisée n’ouvre pas une incohérence fonctionnelle ;
- que `plan_rules` et `LengthBudget` restent dans leur responsabilité ;
- qu’aucune dépendance legacy ne subsiste silencieusement sur une famille nominalement fermée.

Cette story transforme donc la doctrine en garde-fou automatique.

## Cible d'architecture

Introduire une validation centrale de cohérence de configuration LLM, réutilisable par deux moments distincts :

1. **au publish** d’une assembly, d’un prompt ou d’un profil concerné, pour bloquer immédiatement une incohérence locale avant qu’elle n’entre dans l’état publié ;
2. **au boot runtime** pour scanner uniquement l’état publié actif effectivement résoluble par le runtime nominal, et empêcher qu’une incohérence transverse atteigne l’exécution réelle.

Cette validation centrale doit :

- consommer la même règle de périmètre supporté que le runtime ;
- retourner des erreurs structurées stables (`error_code`, `details`) exploitables par API, logs, tests et startup ;
- distinguer clairement erreurs bloquantes sur chemin supporté et tolérances legacy explicitement bornées hors support ;
- éviter les doublons de logique entre routeurs admin, modèles ORM, startup validators, gateway et documentation.

Pour lever toute ambiguïté de périmètre, le scan startup ne doit **pas** analyser :

- l’historique complet ;
- les anciennes versions `published` mais non actives pour une même cible ;
- les brouillons ou archives ;
- des artefacts qui ne peuvent pas être résolus par le runtime nominal courant.

Il doit analyser uniquement :

- l’assembly publiée active par cible réellement résoluble (`feature`, `subfeature`, `plan`, `locale`) ;
- le `ExecutionProfile` explicitement référencé par cette assembly si présent ;
- sinon le `ExecutionProfile` effectivement résolu par la cascade canonique (`feature+subfeature+plan` -> `feature+subfeature` -> `feature`) ;
- le contrat de sortie, la persona et les dépendances référencés par cet état actif.

## Règles de cohérence à valider automatiquement

Pour tout artefact publié ou scanné au boot, le système doit au minimum vérifier :

- `assembly active -> execution_profile_ref` valide et exploitable, ou à défaut une résolution waterfall explicitement autorisée et concluante ;
- `output_contract_ref` valide, publié, résoluble et compatible avec le mode de sortie attendu ;
- provider nominalement supporté ;
- placeholders structurellement compatibles avec la famille canonique et son allowlist ;
- persona autorisée et cohérente avec la stratégie ;
- `plan_rules` et `LengthBudget` cohérents avec leur responsabilité ;
- absence de dépendance legacy sur les familles nominales fermées.

## Périmètre supporté à retenir

La validation doit s’appuyer sur la règle centrale déjà codée dans `is_supported_feature()` après normalisation des aliases legacy. Cela implique :

- `chat`, `guidance`, `natal`, `horoscope_daily` sont des familles nominales fermées ;
- `natal_interpretation` et `daily_prediction` ne sont jamais des clés nominales valides ;
- un alias legacy normalisé vers une famille supportée doit hériter du même niveau d’exigence ;
- toute exception legacy hors support doit être finie, explicitement déclarée et télémétrée.

## Acceptance Criteria

1. **AC1 — Validateur central unique** : une API/fonction centrale unique valide la cohérence d’une configuration LLM publiée ou sur le point d’être publiée. Elle est consommée par les chemins admin de publish pertinents et par une validation startup dédiée ; aucun composant ne redéfinit localement sa propre version des règles.
2. **AC2 — Règle explicite `execution_profile_ref` vs waterfall`** : pour toute assembly publiée d’une famille supportée, le validateur applique explicitement la même hiérarchie que le runtime.
   - Si l’assembly porte `execution_profile_ref`, cette référence doit exister, cibler un profil publié, compatible avec la taxonomie résolue (`feature`, `subfeature`, `plan`) et exploitable sans fallback legacy.
   - Si l’assembly ne porte pas `execution_profile_ref`, l’absence de référence explicite n’est acceptable que si la cascade canonique `feature+subfeature+plan` -> `feature+subfeature` -> `feature` résout effectivement un profil publié et valide pour cette cible.
   - Sur le périmètre supporté, l’absence de référence explicite **et** l’échec de la cascade provoquent un rejet bloquant ; `resolve_model()` n’est jamais une issue de validation acceptable.
3. **AC3 — Contrat de sortie valide et opérationnel** : tout `output_contract_ref` référencé par une assembly publiée doit satisfaire simultanément les conditions suivantes :
   - la référence existe et pointe vers un contrat publié/actif ;
   - le schéma est résoluble par le runtime au publish comme au boot ;
   - il n’est pas contradictoire avec `output_mode` du profil d’exécution effectivement résolu ;
   - il reste compatible avec la forme de sortie attendue de la famille concernée.
   Toute référence cassée, absente ou contradictoire provoque un rejet explicite avec `error_code` stable.
4. **AC4 — Provider nominalement supporté end-to-end** : la validation publish-time et boot-time réutilise la même règle centrale de provider supporté. Un provider non nominalement supporté est rejeté sur le périmètre supporté, même si un morceau du pipeline pourrait encore le tolérer hors support.
5. **AC5 — Validation statique forte des placeholders, sans mini-runtime** : la validation de cohérence vérifie statiquement :
   - la compatibilité structurelle entre placeholders déclarés/utilisés, placeholders requis du use case et blocs assembly concernés ;
   - la conformité à l’allowlist de la famille canonique ;
   - l’absence de placeholder interdit ou structurellement incohérent sur une famille nominale fermée.
   En revanche, elle ne doit pas tenter de simuler toute l’exécution métier ni rejouer le runtime complet de `PromptRenderer.render()`.
6. **AC6 — Persona autorisée et cohérente** : si une assembly référence une persona ou implique une stratégie de persona, la validation vérifie que la persona existe, reste autorisée, n’est pas désactivée lorsqu’elle est requise, et n’introduit pas une incohérence connue avec les bornes de responsabilité ou la famille ciblée.
7. **AC7 — Invariants testables pour `plan_rules` et `LengthBudget`** : la validation échoue si l’un des invariants suivants est violé :
   - `plan_rules` ne modifie jamais la taxonomie `feature/subfeature/plan` ;
   - `LengthBudget` ne porte que des consignes éditoriales et un plafond technique de sortie, sans redéfinir provider, famille ou taxonomie ;
   - `LengthBudget.global_max_tokens`, s’il est présent, reste cohérent avec le contrat de sortie et avec les bornes techniques/documentaires admises par la plateforme ;
   - la priorité documentaire `LengthBudget.global_max_tokens` > `ExecutionProfile.max_output_tokens` > defaults runtime reste préservée.
8. **AC8 — Aucune dépendance legacy sur famille nominale fermée** : sur `chat`, `guidance`, `natal`, `horoscope_daily`, la validation publish-time et boot-time rejette toute dépendance active à un artefact ou identifiant legacy interdit (`daily_prediction`, `natal_interpretation`, fallback implicite, clé legacy gelée, publication réanimant un reliquat historique).
9. **AC9 — Publish fail-fast avec erreurs structurées** : les endpoints admin de publish concernés échouent immédiatement avec un code HTTP cohérent et un payload d’erreur structuré contenant au minimum `error_code`, `message`, `details`, `feature`, `subfeature`, `plan`, `config_id/profile_id` ou équivalent stable selon l’artefact.
10. **AC10 — Boot runtime fail-fast avec mode strict/warn** : une validation startup dédiée scanne l’état publié effectif avant acceptation du runtime. En mode `strict`, une incohérence bloque le démarrage ; en mode `warn`, elle est logguée/télémétrée sans bloquer ; en mode `off`, elle est désactivée explicitement.
11. **AC11 — Observabilité dédiée de cohérence** : publish et startup émettent des événements structurés dédiés de gouvernance/validation avec une taxonomie distincte du fallback runtime nominal. Les rejets de cohérence ne doivent jamais être requalifiés en succès ou en `execution_path_kind` nominal.
12. **AC12 — Taxonomie minimale d’`error_code` imposée** : la validation de cohérence utilise au minimum les codes stables suivants, réutilisés par l’API, les tests et la télémétrie : `missing_execution_profile`, `invalid_execution_profile_ref`, `unsupported_execution_provider`, `missing_output_contract`, `invalid_output_contract_ref`, `placeholder_policy_violation`, `persona_not_allowed`, `plan_rules_scope_violation`, `length_budget_scope_violation`, `legacy_dependency_forbidden`.
13. **AC13 — Couverture tests non-régression** : des tests couvrent au minimum un rejet publish-time et un rejet boot-time pour chacun des axes suivants : profil manquant/invalide, contrat de sortie cassé, provider non supporté, placeholder incompatible, persona invalide, incohérence `plan_rules`/`LengthBudget`, dépendance legacy interdite sur famille supportée.
14. **AC14 — Documentation réalignée** : la documentation canonique décrit explicitement cette validation fail-fast, ses points d’invocation (publish, startup), le périmètre exact du scan startup, la règle explicite `execution_profile_ref` vs waterfall, la nature statique de la validation de placeholders, et les incompatibilités legacy désormais bloquantes.

## Tasks / Subtasks

- [x] Task 1: Introduire un validateur central de cohérence LLM (AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)
  - [x] Créer une API/fonction/service dédié dans `backend/app/llm_orchestration/` pour valider une configuration assembly/profil/contrat/persona de façon transverse.
  - [x] Réutiliser `is_supported_feature()` et la normalisation canonique au lieu de redéfinir localement le périmètre supporté.
  - [x] Définir une structure d’erreur stable avec `error_code`, `message` et `details`.
  - [x] Encoder explicitement la règle `execution_profile_ref` puis waterfall canonique, sans jamais accepter `resolve_model()` comme issue de validation sur le périmètre supporté.
  - [x] Prévoir un mode “single target” (publish) et un mode “scan global” (startup).

- [x] Task 2: Brancher la validation au publish admin (AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9)
  - [x] Étendre [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py) pour appeler le validateur central avant publication.
  - [x] Auditer les points de publish liés aux prompts et profils ([backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py), [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py)) afin d’y raccrocher le même garde-fou, directement ou via service dédié.
  - [x] Uniformiser les réponses d’erreur API pour les rejets de cohérence.
  - [x] Éviter que des validations dispersées divergent entre routeur, service et ORM model.

- [x] Task 3: Ajouter la validation startup dédiée (AC1, AC8, AC10, AC11)
  - [x] Introduire un module startup dédié dans `backend/app/startup/` sur le pattern de `feature_scope_validation.py` et `canonical_db_validation.py`.
  - [x] Scanner uniquement les artefacts publiés actifs effectivement résolubles par le runtime nominal, et exclure explicitement l’historique, les archives et les anciennes versions publiées mais non actives.
  - [x] Intégrer cette validation dans [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) avec un mode configurable `strict|warn|off`.
  - [x] Propager des logs et métriques de rejet distincts des chemins de fallback runtime.

- [x] Task 4: Réaligner la doctrine et l’observabilité (AC4, AC8, AC11, AC13)
  - [x] Documenter la nouvelle validation fail-fast dans [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md).
  - [x] Vérifier la cohérence avec [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md).
  - [x] Ajouter une télémétrie structurée dédiée de type `configuration_validation_failed`, `publish_rejected` ou taxonomie stable équivalente.
  - [x] S’assurer qu’aucun rejet de cohérence n’est recyclé en faux succès nominal.

- [x] Task 5: Ajouter la couverture de tests ciblée (AC9, AC10, AC12)
  - [x] Ajouter des tests unitaires du validateur central pour chaque règle de cohérence.
  - [x] Ajouter des tests d’intégration admin publish sur les cas bloquants.
  - [x] Ajouter des tests startup validant les modes `strict`, `warn` et `off`.
  - [x] Couvrir au moins un alias legacy normalisé vers famille supportée afin de prouver qu’il hérite bien du rejet nominal.

- [x] Task 6: Vérification locale obligatoire
  - [x] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [x] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [x] Exécuter `pytest -q`.
  - [x] Exécuter au minimum les suites ciblées liées à l’admin LLM, aux validations startup et aux stories 66.17, 66.22, 66.28, 66.29, 66.30 et à la nouvelle story 66.31.

## Dev Notes

### Diagnostic exact à préserver

- La doctrine actuelle est déjà bien codée par morceaux, mais aucune validation unique ne relie aujourd’hui assembly, `ExecutionProfile`, contrat de sortie, persona, placeholders, `plan_rules`, `LengthBudget` et taxonomie supportée.
- Le scan startup doit porter sur l’état publié **actif** effectivement résoluble par le runtime nominal, pas sur tout l’historique des versions publiées. Sinon le boot peut être bloqué par une vieille configuration inactive.
- Le dépôt possède déjà un pattern startup clair avec `run_feature_scope_startup_validation()`, `run_canonical_db_startup_validation()` et `validate_catalog_vs_db(db)` dans [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py). La story 66.31 doit réutiliser ce pattern au lieu d’inventer un bootstrap parallèle.
- `AssemblyAdminService.publish_config()` revalide déjà placeholders et provider. La story 66.31 doit étendre cette logique, pas la contourner.
- La doc runtime encode déjà la hiérarchie `execution_profile_ref` puis waterfall canonique. 66.31 doit fermer explicitement ce point pour éviter deux lectures concurrentes.
- `LlmExecutionProfileModel.validate_status_change()` protège déjà certains cas de publish. Cette logique ne doit pas diverger de la future validation centrale.
- Les lints d’architecture dans [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py) existent déjà pour les templates et `plan_rules`; ils doivent être valorisés comme entrées d’une validation plus globale.
- La validation placeholders attendue ici est une validation statique forte de cohérence et d’allowlist, pas une simulation complète du runtime métier.
- La règle du périmètre supporté est déjà centralisée dans [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py). Elle doit rester la seule source de vérité sur ce point.
- L’observabilité de gouvernance existe déjà dans [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py). La nouvelle validation doit enrichir cette taxonomie, pas créer un canal concurrent opaque.

### Ce que le dev ne doit pas faire

- Ne pas dupliquer la logique de cohérence dans plusieurs routeurs, modèles ORM et startup scripts sans service central partagé.
- Ne pas traiter cette story comme un simple ajout de documentation ou de warnings non bloquants.
- Ne pas redéfinir localement le périmètre supporté avec de nouveaux sets hardcodés.
- Ne pas scanner tout l’historique des versions publiées au boot ; seules les configurations actives réellement résolubles par le runtime doivent compter.
- Ne pas confondre validation de cohérence publish/boot avec fallback runtime : un rejet de cohérence n’est pas un chemin d’exécution toléré.
- Ne pas se limiter au seul provider ou au seul `execution_profile_ref` ; la cible est la cohérence transverse complète.
- Ne pas imposer implicitement un `execution_profile_ref` explicite partout si la règle retenue reste `ref explicite sinon waterfall canonique réussi` ; cette décision doit être codée noir sur blanc et testée comme telle.
- Ne pas laisser les familles nominales fermées dépendre encore d’un artefact legacy gelé sous prétexte qu’un alias est normalisé en entrée.
- Ne pas introduire des erreurs libres non structurées impossibles à asserter proprement dans les tests.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py)
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py)
- [backend/app/startup/feature_scope_validation.py](/c:/dev/horoscope_front/backend/app/startup/feature_scope_validation.py)
- [backend/app/startup/canonical_db_validation.py](/c:/dev/horoscope_front/backend/app/startup/canonical_db_validation.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)

### Previous Story Intelligence

- **66.17** a formalisé la responsabilité de chaque couche et introduit les lints d’architecture sur les templates et `plan_rules`. 66.31 doit transformer ces règles en validation exécutable.
- **66.22** a verrouillé les providers nominalement supportés entre admin et runtime. 66.31 doit faire de cette règle un invariant de cohérence, au publish comme au boot.
- **66.28** a gelé des identifiants legacy nominaux (`daily_prediction`) et interdit leur résurrection via admin publish/rollback. 66.31 doit généraliser cette logique de non-résurrection à la cohérence de configuration globale.
- **66.29** a rendu l’assembly obligatoire sur le périmètre supporté. 66.31 doit empêcher qu’une assembly publiée soit structurellement incohérente avant même l’exécution.
- **66.30** a rendu `ExecutionProfile` obligatoire et a supprimé `resolve_model()` comme vérité finale sur le périmètre supporté. 66.31 doit faire en sorte qu’un profil manquant ou incohérent soit détecté plus tôt, au publish et au boot.

### Git Intelligence

Commits récents pertinents observés :

- `d87e4fc2` : `fix(llm): harden story 66.30 runtime invariants`
- `affb4f69` : `fix(llm): align story 66.30 observability and docs`
- `d950c901` : `fix(llm): end-to-end error_code, sync admin models and discriminant telemetry (Story 66.30 fix)`
- `1d343866` : `feat(llm): remove resolve_model fallback for supported perimeter (Story 66.30)`
- `1a8e85db` : `docs(llm): clarify canonical rejection observability`

Pattern à réutiliser :

- fermer l’incohérence dans le code avant d’aligner la documentation ;
- produire des `error_code` stables et des détails structurés ;
- distinguer nettement rejet de configuration et fallback runtime ;
- prouver la fermeture par tests d’intégration et observabilité.

### Testing Requirements

- Ajouter un test publish-time rejetant une assembly supportée sans `execution_profile_ref` valide.
- Ajouter un test publish-time acceptant une assembly supportée sans `execution_profile_ref` explicite uniquement si la cascade canonique résout réellement un profil publié valide.
- Ajouter un test publish-time rejetant une assembly supportée sans `execution_profile_ref` explicite lorsque la cascade échoue.
- Ajouter un test publish-time rejetant une assembly avec `output_contract_ref` cassé ou absent quand il est requis.
- Ajouter un test publish-time rejetant un provider non supporté ou une dépendance legacy interdite sur famille nominale.
- Ajouter un test publish-time couvrant une incohérence `persona_ref` / persona désactivée / stratégie requise.
- Ajouter un test publish-time couvrant une incohérence `plan_rules` / `LengthBudget`.
- Ajouter un test startup en mode `strict` bloquant le boot sur une incohérence d’artefact publié actif, sans tenir compte d’une ancienne version publiée mais inactive.
- Ajouter un test startup en mode `warn` journalisant sans bloquer.
- Ajouter un test sur alias legacy normalisé (`daily_prediction -> horoscope_daily` ou équivalent) pour prouver qu’il hérite de la validation nominale.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest backend/app/llm_orchestration/tests -q`
  - `pytest backend/tests/integration -q`
  - ajouter la suite dédiée 66.31 si elle est créée

### Project Structure Notes

- Travail backend + documentation uniquement.
- Aucun changement frontend n’est attendu.
- Les modifications doivent rester concentrées dans `backend/app/llm_orchestration/`, `backend/app/startup/`, `backend/tests/` et `docs/`.

### References

- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py)
- [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py)
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)
- [66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- `ConfigCoherenceValidator` est branché au publish et au startup, avec structure d’erreur stable et hiérarchie explicite `execution_profile_ref -> waterfall canonique`.
- Le validateur résout désormais `output_contract_ref` à la fois par UUID et par nom, pour rester cohérent avec les seeds et avec la résolution runtime dans le gateway.
- Le scan startup ne parcourt plus tout l’historique `published` ; il retient uniquement la configuration publiée la plus récente par cible runtime (`feature`, `subfeature`, `plan`, `locale`).
- La route admin de publish assembly renvoie un payload d’erreur structuré stable (`error.code=coherence_validation_failed`) au lieu d’un `HTTPException.detail` ad hoc.
- La couverture de tests a été ajoutée pour le waterfall sans `execution_profile_ref`, les références UUID de contrats de sortie, le scan startup limité à l’état actif et les rejets API structurés.
- Les suites ciblées du validateur, du startup validator et de l’API admin ont été relancées sous venv après correction des régressions du review.

### File List

- `_bmad-output/implementation-artifacts/66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md`
- `backend/app/api/v1/routers/admin_llm_assembly.py`
- `backend/app/llm_orchestration/services/config_coherence_validator.py`
- `backend/app/llm_orchestration/tests/test_config_coherence_validator.py`
- `backend/app/tests/integration/test_admin_llm_config_api.py`
- `backend/app/tests/unit/test_llm_coherence_startup_validation.py`
- `docs/llm-prompt-generation-by-feature.md`
