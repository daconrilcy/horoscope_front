# Story 66.32: Versionnement atomique et rollback sûr des artefacts de prompting

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want versionner et activer atomiquement l’ensemble cohérent assembly/profile/contract/persona,
so that une publication cassée puisse être annulée instantanément par retour à `N-1` sans bricolage manuel, sans mélange d’états intermédiaires, et avec une traçabilité explicite de la version réellement exécutée par le runtime.

## Contexte

Les stories 66.29 à 66.31 ont fermé les principaux fallback runtime et introduit une validation de cohérence publish/boot utile, mais la gouvernance reste encore centrée sur des publications unitaires par table ou par artefact :

- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py) sait publier et rollback une `PromptAssemblyConfigModel` de manière atomique **pour une seule cible runtime** (`feature`, `subfeature`, `plan`, `locale`) en basculant des statuts `draft/published/archived`.
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py) sait valider la cohérence transverse assembly -> execution profile -> output contract -> persona au publish et au boot, mais il le fait contre l’état vivant des tables, sans notion de release cohérente identifiée.
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py) versionne implicitement les profils via `status/published_at`, mais la résolution runtime reste basée sur “le dernier `published` applicable”, pas sur une appartenance explicite à un snapshot atomique.
- [backend/app/infra/db/models/llm_persona.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_persona.py) ne porte aujourd’hui ni `status`, ni historique publié, ni rollback canonique ; une persona est modifiée in-place via les routes admin [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py), ce qui empêche de reconstituer proprement un état runtime antérieur.
- [backend/app/infra/db/models/llm_output_schema.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_output_schema.py) dispose bien d’un champ `version`, mais pas d’un cycle `draft/published/archived` ni d’un pointeur d’activation transactionnel ; le runtime peut donc résoudre un contrat par nom ou UUID sans savoir à quelle release cohérente il appartient.
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py), [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py) et [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py) résolvent chacun les artefacts “actifs” depuis leurs tables respectives, ce qui autorise encore un mélange inter-générations si plusieurs artefacts sont publiés à des instants différents.
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) décrit déjà un scan startup borné à l’état publié actif et une gouvernance de cohérence fail-fast, mais ne décrit pas encore comment garantir qu’assembly, execution profile, contrat et persona proviennent d’une **même release cohérente activée en une seule opération**.

Le système sait donc déjà refuser une incohérence visible. En revanche, il ne sait pas encore :

- produire un snapshot immutable de la configuration LLM réellement livrée ;
- activer ce snapshot par un seul basculement transactionnel ;
- revenir à `N-1` en réactivant le snapshot précédent sans republier manuellement chaque artefact ;
- exposer partout quel snapshot exact a servi à l’exécution réelle.

Le risque restant est opérationnel et non théorique :

- publication d’une nouvelle assembly pointant vers un profil juste mis à jour mais pas encore pleinement propagé ;
- persona modifiée in-place après publication d’une assembly, rendant impossible le retour à un état réellement identique ;
- contrat renommé ou remplacé alors qu’une assembly historique continue de le référencer par nom ;
- rollback partiel d’une assembly sans rollback coordonné du profil, de la persona ou du contrat correspondant ;
- démarrage runtime validant un état “cohérent au moment T” mais sans identifiant stable de release à observer, journaliser, comparer ou restaurer.

Cette story ferme ce dernier angle mort en introduisant un **versionnement atomique de release** des artefacts de prompting.

## Cible d'architecture

Introduire une notion explicite de **release snapshot LLM** ou **bundle de configuration publié** qui représente un état cohérent et immutable de l’ensemble runtime :

- assemblies retenues par cible runtime ;
- execution profiles résolus ou explicitement référencés ;
- output contracts consommés ;
- personas requises ;
- et, par transitivité, les références de templates/prompt versions utilisées par ces assemblies.

Cette release doit être :

1. **construite** à partir d’un manifest déterministe des artefacts candidats ;
2. **validée** par le validateur de cohérence central avant activation ;
3. **activée** par un seul pointeur transactionnel, sans mélange possible entre ancien et nouvel état ;
4. **restituable** par rollback à `N-1` en réactivant le snapshot précédent ;
5. **observable** dans le runtime, les logs, la persistance, les dashboards et le boot.

La cible n’est donc pas d’ajouter un simple champ `version` dispersé dans plusieurs tables. La cible est d’introduire une frontière claire entre :

- des artefacts éditables / publiables individuellement ;
- et la **release runtime réellement servie** au système à un instant donné.

## Périmètre d’activation à verrouiller

La story doit verrouiller noir sur blanc le périmètre couvert par le snapshot actif.

Le pointeur d’activation introduit par 66.32 couvre **au minimum et obligatoirement** le périmètre nominal convergé déjà fermé par les stories 66.29 à 66.31 :

- `chat`
- `guidance`
- `natal`
- `horoscope_daily`

Pour ce périmètre supporté :

- le runtime doit lire **uniquement** le snapshot actif ;
- aucun resolver ne peut continuer à lire “le dernier `published` par cible” directement dans les tables vivantes ;
- aucun chemin hybride “snapshot pour une partie, tables vivantes pour une autre” n’est autorisé.

Pour les chemins legacy hors support, la story impose une décision explicite d’architecture et de documentation :

- soit ils sont inclus dans le snapshot et obéissent au même contrat ;
- soit ils restent explicitement hors snapshot, mais alors cette exception est finie, documentée, télémétrée et **strictement interdite** au périmètre nominal convergé.

L’implémentation ne doit donc pas introduire un pointeur “global plateforme” ambigu. Elle doit documenter explicitement si “global” signifie :

- global au **périmètre nominal convergé** ;
- ou global à **tous** les chemins encore existants.

L’absence de réponse explicite à cette question est considérée comme un défaut d’implémentation de la story.

## Invariants de release à imposer

Pour toute release snapshot activable, les invariants suivants doivent être vrais :

- chaque entrée assembly du snapshot référence explicitement les IDs immutables des artefacts qu’elle consomme ;
- les personas et contrats référencés par le snapshot ne sont plus lus “au fil de l’eau” depuis un état mutable non versionné ;
- le runtime résout toujours assembly/profile/contract/persona à partir du **snapshot actif**, jamais à partir d’un mélange “published le plus récent” dans plusieurs tables ;
- l’activation d’une nouvelle release ne requiert pas de republier ou d’archiver à la main chaque artefact composant ;
- le rollback à `N-1` consiste à réactiver un snapshot antérieur cohérent, pas à rejouer une série d’opérations manuelles sur plusieurs endpoints ;
- toute exécution, validation startup ou audit expose l’identifiant exact de release snapshot utilisé.
- un snapshot est **immutable** : son manifest, ses métadonnées critiques, son contenu figé éventuel et son historique de dépendances ne sont jamais réécrits après création ; activation et rollback ajoutent des événements, ils ne modifient pas le contenu du snapshot.
- toute donnée cacheable utilisée sur le périmètre supporté est partitionnée par `active_snapshot_id` ; une lecture issue d’un cache d’un snapshot précédent après activation/rollback est une violation d’invariant.

## Stratégie par type d’artefact

66.32 doit imposer une décision explicite et non négociable pour chaque type d’artefact porté par la release.

### Artefacts à références immutables suffisantes

Pour les artefacts déjà réellement versionnés et gouvernés par cycle de publication :

- `PromptAssemblyConfigModel`
- `LlmExecutionProfileModel`
- `LlmPromptVersionModel` référencé transitivement par l’assembly

le snapshot peut s’appuyer sur des **références immutables d’artefacts versionnés** à condition que :

- l’ID référencé soit immutable ;
- le contenu référencé ne soit jamais modifié in-place après publication ;
- la résolution runtime se fasse exclusivement à partir de cette référence figée dans le manifest.

### Artefacts nécessitant une fermeture explicite

Pour les artefacts qui sont aujourd’hui encore trop vivants ou insuffisamment gouvernés :

- `LlmPersonaModel`
- `LlmOutputSchemaModel`

la story impose une décision explicite par type :

1. soit l’artefact est rendu **réellement versionné** avec cycle `draft/published/archived` et immutabilité post-publication ;
2. soit le snapshot embarque une **copie figée suffisante** de son contenu pour garantir un rollback fidèle ;
3. toute solution hybride ou implicite est interdite.

Autrement dit, AC7 n’est pas un simple souhait d’alignement. C’est un invariant de conception : aucun artefact mutable non versionné ne peut rester une dépendance vivante d’une release activable sur le périmètre supporté.

## Acceptance Criteria

1. **AC1 — Snapshot cohérent immutable** : le backend introduit un artefact de release snapshot immutable représentant l’ensemble cohérent `assembly/profile/contract/persona` réellement servi au runtime. Le snapshot contient un identifiant stable (`snapshot_id`, `release_id`, `bundle_id` ou équivalent), une version lisible, sa date de création, son auteur, et un manifest explicite des références résolues par cible runtime.
2. **AC2 — Périmètre snapshot explicite et non hybride** : la documentation et le code déclarent explicitement si le snapshot actif couvre seulement le périmètre nominal convergé (`chat`, `guidance`, `natal`, `horoscope_daily`) ou également des chemins legacy hors support. Sur le périmètre nominal convergé, aucun resolver runtime ne peut rester branché sur les tables vivantes hors snapshot.
3. **AC3 — Fermeture transitive du manifest** : construire un snapshot ne consiste pas à stocker uniquement des assemblies. Le manifest doit fermer explicitement les dépendances nécessaires à l’exécution réelle : `execution_profile_ref`, `output_contract_ref`, `persona_ref`, références de templates/prompt versions, et tout identifiant indispensable pour reconstituer exactement la configuration runtime.
4. **AC4 — Décision explicite par type d’artefact** : la story impose et documente, pour chaque type d’artefact embarqué dans le snapshot, s’il est porté par référence immutable vers un artefact réellement versionné ou par contenu figé embarqué dans le snapshot. `LlmPersonaModel` et `LlmOutputSchemaModel` ne peuvent pas rester des dépendances vivantes non gouvernées du snapshot actif.
5. **AC5 — Validation préalable obligatoire à l’activation** : un snapshot candidat doit obtenir un statut explicite de validation (`validated=true`, `status=validated`, ou équivalent stable) avant toute activation. Un snapshot non validé ne peut jamais devenir actif via l’admin.
6. **AC6 — Validation avant activation** : la création d’un snapshot candidat réutilise le validateur central de cohérence introduit par 66.31, mais l’applique au manifest complet de release. Un snapshot incomplet, incohérent ou contenant une dépendance mutable non figée n’est pas activable.
7. **AC7 — Activation atomique par pointeur unique** : l’activation runtime d’une nouvelle version se fait par un basculement transactionnel unique d’un pointeur d’activation (`active_snapshot_id` ou équivalent) global ou de périmètre explicitement défini. Le runtime ne doit jamais pouvoir observer un état partiellement basculé où certaines tables sont en `N` et d’autres en `N-1`.
8. **AC8 — Rollback `N-1` sans bricolage manuel** : le système expose une opération de rollback qui réactive le snapshot actif précédent (`N-1`) ou un snapshot explicitement ciblé, sans republier manuellement assembly, profile, contract et persona. Le rollback doit être transactionnel et idempotent.
9. **AC9 — Rollback seulement vers un snapshot encore activable** : un rollback ne peut cibler qu’un snapshot ayant un statut explicite `activable` ou `previously_activated_and_still_valid` (nom stable équivalent accepté). Si le snapshot `N-1` est corrompu, invalidé, devenu incompatible ou non activable, l’API échoue explicitement avec un `error_code` stable ; aucun rollback best effort n’est autorisé.
10. **AC10 — Le runtime lit le snapshot actif** : le gateway, les registries et les validations startup ne déduisent plus l’état actif uniquement depuis `status == published` sur plusieurs tables autonomes. Sur le périmètre couvert, ils résolvent la release active à partir du snapshot/pointeur d’activation et n’utilisent les tables sources que comme backing store des artefacts versionnés de ce snapshot.
11. **AC11 — Fermeture explicite des resolvers legacy “latest published”** : sur le périmètre supporté couvert par le snapshot, aucun resolver runtime ne peut interroger directement “latest published by target” une fois le snapshot actif introduit. Cette fermeture doit être testable et vérifiée par les suites de non-régression.
12. **AC12 — Observabilité de la version réellement exécutée** : chaque exécution publie dans `ResolvedExecutionPlan`, `GatewayMeta`, `obs_snapshot`, logs structurés et événements de gouvernance au minimum : `active_snapshot_id`, `active_snapshot_version` et un identifiant stable de l’entrée de manifest réellement utilisée (`manifest_entry_id`, `target_entry_id`, ou hash de dépendances résolues). Les dashboards et incidents peuvent donc répondre sans ambiguïté à “quelle release tournait ?” et “quelle entrée de cette release a servi à cette exécution ?”.
13. **AC13 — Startup validation alignée sur la release active** : la validation startup ne scanne plus seulement “les dernières versions publiées par cible”, mais la release snapshot actuellement activée. L’activation admin exige une validation préalable ; le startup revalide défensivement le snapshot actif mais ne remplace jamais la validation d’activation. En mode `strict`, un snapshot actif invalide bloque le boot ; en `warn`, il le journalise ; en `off`, il reste désactivable explicitement.
14. **AC14 — Caches et registries cohérents** : `AssemblyRegistry`, `ExecutionProfileRegistry` et toute cache runtime concernée sont invalidés ou rechargés **post-commit** à l’activation/rollback d’un snapshot. Toute clé de cache dépendant d’un état résolu sur le périmètre supporté est indexée par `active_snapshot_id`.
15. **AC15 — API admin de release dédiée** : l’admin expose un workflow explicite du type `build snapshot` / `validate snapshot` / `activate snapshot` / `rollback snapshot`, distinct des simples endpoints CRUD/publish unitaires. Les réponses d’API et audits transportent des IDs de snapshot stables et non seulement des IDs d’artefacts isolés.
16. **AC16 — Audit trail de release et non-réécriture historique** : chaque activation et rollback enregistre un événement structuré avec au minimum `from_snapshot_id`, `to_snapshot_id`, auteur, raison éventuelle, date et résumé du manifest. Le contenu d’un snapshot et les liens historiques de bascule ne sont jamais mutés rétroactivement ; l’historique est append-only.
17. **AC17 — Couverture tests de non-régression** : des tests couvrent au minimum : création d’un snapshot cohérent, rejet d’un snapshot incomplet, activation atomique sans état intermédiaire observable, rollback `N-1`, échec explicite si `N-1` n’est plus activable, invalidation post-commit des caches, lecture runtime du snapshot actif, fermeture des resolvers `latest published`, et propagation de `active_snapshot_id/version` plus `manifest_entry_id` dans l’observabilité.
18. **AC18 — Documentation et runbook réalignés** : la documentation canonique explique désormais la différence entre artefacts publiés individuellement et release runtime activée, le périmètre exact couvert par le snapshot, la procédure d’activation, la procédure de rollback, et la manière d’identifier la version active réellement exécutée.

## Tasks / Subtasks

- [ ] Task 1: Introduire le modèle de release snapshot LLM (AC1, AC2, AC7, AC13)
  - [ ] Définir les nouvelles tables/modèles de snapshot et de pointeur actif dans `backend/app/infra/db/models/` et les migrations associées.
  - [ ] Documenter explicitement le périmètre exact couvert par le pointeur d’activation : nominal convergé uniquement ou extension assumée à d’autres chemins.
  - [ ] Décider explicitement du périmètre du snapshot : global à toute la plateforme LLM ou scoped d’une manière strictement documentée, sans ambiguïté de lecture runtime.
  - [ ] Encoder un manifest immutable listant les targets runtime et les IDs exacts d’assembly/profile/contract/persona/templates retenus.
  - [ ] Prévoir l’historisation (`created_by`, `created_at`, `activated_at`, `rolled_back_from`, `reason`) pour audit et runbook.
  - [ ] Interdire toute mutation post-création du manifest et des métadonnées critiques du snapshot.

- [ ] Task 2: Construire et valider un snapshot candidat (AC2, AC3, AC8)
  - [ ] Créer un service dédié de build de snapshot dans `backend/app/llm_orchestration/services/` qui collecte l’état candidat à partir des artefacts publiés/désignés.
  - [ ] Réutiliser `ConfigCoherenceValidator` comme noyau de validation, mais en l’adaptant pour travailler sur un manifest de release complet plutôt que sur le seul état vivant de tables isolées.
  - [ ] Imposer une stratégie explicite par type d’artefact : référence immutable pour les objets réellement versionnés, contenu figé embarqué ou versionnement explicite pour les personas et output contracts.
  - [ ] Vérifier que le snapshot ferme transitivement toutes les dépendances runtime nécessaires, y compris les personas et contrats aujourd’hui non réellement versionnés.
  - [ ] Produire des erreurs structurées stables pour les snapshots non activables.
  - [ ] Introduire un statut de validation explicite nécessaire avant activation.

- [ ] Task 3: Basculer le runtime sur la release active atomique (AC4, AC6, AC10, AC11)
  - [ ] Introduire un résolveur central de `active_snapshot`.
  - [ ] Faire lire `AssemblyRegistry`, `ExecutionProfileRegistry`, le gateway et la validation startup depuis ce snapshot actif au lieu de se fier uniquement aux `status == published` distribués.
  - [ ] Supprimer ou isoler explicitement tout resolver `latest published by target` du périmètre supporté une fois le snapshot introduit.
  - [ ] Garantir l’invalidation des caches après activation/rollback et seulement après commit réussi.
  - [ ] Partitionner toutes les clés de cache concernées par `active_snapshot_id`.
  - [ ] S’assurer qu’aucune lecture runtime ne peut observer un état mixte pendant une bascule.

- [ ] Task 4: Exposer l’admin release et le rollback `N-1` (AC5, AC12, AC13)
  - [ ] Ajouter des endpoints admin dédiés pour créer/valider/activer/rollback un snapshot.
  - [ ] Implémenter le rollback `N-1` comme réactivation du snapshot précédent, sans republier manuellement les artefacts unitaires.
  - [ ] Rejeter explicitement un rollback vers un snapshot non activable, invalide ou incompatible, avec `error_code` stable.
  - [ ] Journaliser chaque bascule dans l’audit trail et la gouvernance LLM avec des IDs de snapshot stables.
  - [ ] Prévoir une réponse API claire indiquant `from_snapshot`, `to_snapshot`, `activation_mode`, `warnings`.

- [ ] Task 5: Propager la version réellement exécutée dans l’observabilité (AC9, AC13, AC15)
  - [ ] Étendre `ResolvedExecutionPlan`, `GatewayMeta`, `ExecutionObservabilitySnapshot` et la persistance associée pour porter `active_snapshot_id`, `active_snapshot_version` et un identifiant stable de l’entrée de manifest réellement utilisée.
  - [ ] Ajouter les mêmes informations aux logs startup, logs d’activation, logs de rollback et événements `publish_rejected`/`runtime_rejected` si le snapshot actif est impliqué.
  - [ ] Vérifier que les surfaces d’exploitation peuvent corréler une exécution, un incident et une release sans introspection manuelle multi-table.

- [ ] Task 6: Réaligner la documentation et les runbooks (AC10, AC13, AC15)
  - [ ] Mettre à jour [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) pour documenter le concept de release snapshot active.
  - [ ] Vérifier la cohérence avec [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md).
  - [ ] Ajouter ou compléter un runbook incident sur “rollback release LLM” et “identifier la version active réellement exécutée”.

- [ ] Task 7: Ajouter la couverture de tests ciblée (AC4, AC5, AC9, AC10, AC11, AC14)
  - [ ] Ajouter des tests unitaires du service de build/validation de snapshot.
  - [ ] Ajouter des tests d’intégration d’activation atomique et rollback `N-1`.
  - [ ] Ajouter un test prouvant que le runtime lit bien le snapshot actif et non un mélange de `published` récents.
  - [ ] Ajouter un test d’observabilité prouvant que `active_snapshot_id/version` sont propagés dans la réponse et la persistance.

- [ ] Task 8: Vérification locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblées liées aux stories 66.29, 66.30, 66.31 et à la nouvelle story 66.32.

## Dev Notes

### Diagnostic exact à préserver

- Le dépôt sait déjà faire du publish/rollback unitaire sur les assemblies et les prompts, mais cela ne garantit pas un rollback cohérent multi-artefacts.
- Le vrai trou d’architecture n’est pas l’absence de validation de cohérence ; 66.31 l’a déjà introduite. Le vrai trou est l’absence de **version de release active unique** qui fige ensemble assembly/profile/contract/persona.
- Aujourd’hui, `ConfigCoherenceValidator.scan_active_configurations()` choisit la dernière assembly publiée par cible, puis valide ses dépendances en live. Ce scan ne suffit pas à prouver qu’une exécution réelle et un rollback futur retomberont exactement sur le même ensemble d’artefacts.
- `LlmPersonaModel` est particulièrement problématique car il est modifié in-place et seulement protégé par `enabled`; un rollback fidèle est impossible tant qu’aucune version figée ou capture de snapshot n’existe.
- `LlmOutputSchemaModel` a un `version` métier, mais pas de cycle d’activation canonique. Une story 66.32 incomplète qui ne traite pas ce point ne livrerait qu’un pseudo versionnement.
- Le rollback cible doit être un changement de pointeur de release, pas une séquence “archive ceci / republie cela / réactive la persona / remets l’ancien contrat”.
- Les caches existants d’assembly et d’execution profiles sont des risques de cohérence majeurs si l’invalidation n’est pas alignée avec le commit d’activation.
- La présence future d’un snapshot actif ne suffit pas si une partie du runtime continue à interroger `latest published by target` directement ; la story doit fermer cette échappatoire de manière testable.
- La validation startup doit devenir une **revalidation défensive** du snapshot déjà validé pour activation, pas un second mécanisme mental susceptible d’accepter ou refuser arbitrairement ce que l’admin a rendu actif.
- En incident, connaître `active_snapshot_id` seul ne suffit pas ; il faut aussi pouvoir identifier l’entrée exacte du manifest qui a servi à une exécution donnée.

### Ce que le dev ne doit pas faire

- Ne pas ajouter seulement un champ `release_version` cosmétique sur les tables existantes sans introduire de snapshot activable.
- Ne pas conserver un runtime qui résout encore les artefacts “actifs” via plusieurs tables indépendantes une fois la story réalisée.
- Ne pas traiter le rollback comme un script manuel ou une suite d’appels admin best effort.
- Ne pas laisser personas ou contrats hors du périmètre au motif qu’ils sont “déjà stables” ; ce sont précisément les maillons aujourd’hui non atomiques.
- Ne pas réutiliser `published_at` comme seul mécanisme de vérité de release.
- Ne pas rouvrir les fallbacks runtime ou les exceptions legacy déjà fermés par 66.29 à 66.31.
- Ne pas faire dépendre l’observabilité de la version active d’un recalcul a posteriori basé sur les tables courantes.
- Ne pas se contenter d’une invalidation de cache globale non partitionnée ; les caches doivent être cohérents par `active_snapshot_id`.
- Ne pas permettre l’activation d’un snapshot non validé puis compter sur le startup pour rattraper l’erreur.
- Ne pas muter rétroactivement le contenu d’un snapshot déjà créé ou déjà activé.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/infra/db/models/llm_assembly.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_assembly.py)
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py)
- [backend/app/infra/db/models/llm_persona.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_persona.py)
- [backend/app/infra/db/models/llm_output_schema.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_output_schema.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)

### Previous Story Intelligence

- **66.17** a verrouillé la responsabilité canonique des couches ; 66.32 doit éviter qu’une release runtime relise des artefacts vivants hors de cette vérité.
- **66.22** a fermé les providers non supportés comme dérive locale ; 66.32 doit garantir que le rollback ne réactive jamais silencieusement un bundle incohérent ou legacy.
- **66.25** a imposé un snapshot canonique d’observabilité ; 66.32 doit lui donner un identifiant de release réellement exploitable.
- **66.29** a imposé l’assembly canonique obligatoire sur le périmètre supporté ; 66.32 doit maintenant imposer la **release canonique obligatoire** sur ce même périmètre.
- **66.30** a rendu `ExecutionProfile` obligatoire comme source finale de vérité d’exécution ; 66.32 doit faire en sorte que ce profil fasse partie d’un bundle atomique et rollbackable.
- **66.31** a introduit la validation fail-fast publish/boot ; 66.32 ne remplace pas cette validation, elle lui donne une cible de release immutable et activable.

### Git Intelligence

Commits récents pertinents observés :

- `e9bf0a37` : `docs(llm): tighten story 66.31 coherence documentation`
- `c921e337` : `fix(llm): harden story 66.31 coherence validation`
- `66acba63` : `feat(llm): implement story 66.31 central configuration coherence validator and startup validation`
- `d87e4fc2` : `fix(llm): harden story 66.30 runtime invariants`
- `affb4f69` : `fix(llm): align story 66.30 observability and docs`

Pattern à réutiliser :

- fermer l’ambiguïté runtime d’abord, puis réaligner la doc ;
- produire des IDs stables et des erreurs structurées testables ;
- distinguer nettement activation canonique, rollback canonique et publication d’artefacts unitaires ;
- prouver la fermeture par tests d’intégration et par observabilité.

### Testing Requirements

- Ajouter un test qui construit un snapshot cohérent à partir d’artefacts publiés et vérifie qu’il est activable.
- Ajouter un test qui rejette un snapshot candidat contenant une persona mutable/inexistante, un contrat cassé ou un profil non aligné avec le manifest.
- Ajouter un test d’activation atomique où aucune lecture concurrente ne peut observer un état mixte entre deux releases.
- Ajouter un test de rollback `N-1` prouvant que le runtime reconsomme immédiatement l’ancien snapshot sans republier individuellement les artefacts.
- Ajouter un test d’échec explicite quand `N-1` n’est plus activable ou validable.
- Ajouter un test d’invalidation de cache post-commit après activation/rollback.
- Ajouter un test montrant qu’une clé de cache issue du snapshot `N` ne peut pas être réutilisée sous `N-1`.
- Ajouter un test prouvant que les resolvers runtime du périmètre supporté n’interrogent plus `latest published by target`.
- Ajouter un test d’observabilité où `result.meta.obs_snapshot` expose `active_snapshot_id`, `active_snapshot_version` et l’identifiant d’entrée de manifest utilisée.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest backend/app/llm_orchestration/tests -q`
  - `pytest backend/tests/integration -q`
  - ajouter la suite dédiée 66.32 si elle est créée

### Project Structure Notes

- Travail backend + documentation + migrations.
- Aucun changement frontend n’est attendu.
- Les modifications doivent rester concentrées dans `backend/app/llm_orchestration/`, `backend/app/infra/db/models/`, `backend/migrations/`, `backend/tests/` et `docs/`.

### References

- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/infra/db/models/llm_assembly.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_assembly.py)
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py)
- [backend/app/infra/db/models/llm_persona.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_persona.py)
- [backend/app/infra/db/models/llm_output_schema.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_output_schema.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [66-29-extinction-definitive-fallback-use-case-first-tous-chemins-supportes.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-29-extinction-definitive-fallback-use-case-first-tous-chemins-supportes.md)
- [66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md)
- [66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story créée à partir du besoin utilisateur et réalignée sur l’état réel post-66.31 du code de publish/rollback/cohérence.
- Le diagnostic central figé dans la story est l’absence d’une release snapshot atomique partagée entre assembly, execution profile, output contract et persona.
- La story impose un rollback `N-1` par réactivation de snapshot, pas par bricolage multi-endpoints.
- L’observabilité exigée inclut explicitement l’identifiant et la version du snapshot réellement exécuté.

### File List

- `_bmad-output/implementation-artifacts/66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md`
