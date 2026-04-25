# Story 70-20: Auditer et assainir `ai_engine_adapter.py` pour ne conserver qu’une façade applicative utile

Status: done

## Story

As a Platform Architect,  
I want auditer, réduire et assainir `backend/app/application/llm/ai_engine_adapter.py`,  
so that le backend LLM conserve un point d’entrée applicatif clair, DRY, documenté en français, sans logique legacy, sans responsabilité parasite et sans doublon avec le runtime, le prompting, la narration ou les services métier.

## Contexte

Les stories 70-14 et 70-15 ont déjà stabilisé un point important : `app.application.llm.ai_engine_adapter` est le point d’entrée applicatif canonique entre les services métier et le runtime LLM.

L’audit backend post-70-15 confirme cette cible et liste explicitement `backend/app/application/llm/ai_engine_adapter.py` comme façade applicative active.

Cependant, l’état actuel du fichier montre qu’un assainissement structurel reste nécessaire :

- `backend/app/application/llm/ai_engine_adapter.py` contient aujourd’hui environ 918 lignes ;
- le module ne porte pas seulement une façade d’appel au gateway, mais aussi des heuristiques de conversation, de la détection hors scope, du mapping d’erreurs, des fallbacks de test et de la logique de narration ;
- plusieurs helpers top-level semblent relever d’une responsabilité plus spécialisée ;
- certaines docstrings restent en anglais ou sont absentes ;
- les consommateurs nominaux sont nombreux : routeurs API, services `llm_generation`, projection publique, narration et suites de tests ;
- le dépôt ne contient plus de `backend/app/services/ai_engine_adapter.py`, et ce chemin ne doit pas être recréé.

La cible préférentielle initiale de cette story était `split-and-keep`.  
L’implémentation finale a toutefois conclu à `delete`, car l’analyse de `backend/app/services/`, `backend/app/domain/`, `backend/app/api/` et `backend/app/prediction/` a confirmé que `backend/app/domain/llm/runtime/` était déjà le sous-dossier canonique le plus naturel pour recevoir la façade et ses erreurs sans créer de couche redondante.

## Objectif

Obtenir une façade applicative LLM minimale, lisible et stable, qui :

- reste au bon niveau de couche backend ;
- ne duplique pas `domain/llm/runtime/*`, `domain/llm/prompting/*`, `services/llm_generation/*` ou `prediction/*` ;
- ne contient aucun fallback de test ou reliquat de transition dans le chemin nominal ;
- expose uniquement les symboles réellement consommés ;
- documente clairement son intention en français ;
- garde les imports et tests alignés sur la décision structurelle finale.

## Règle de frontière attendue

Si `AIEngineAdapter` est conservé, son rôle doit être limité à :

- recevoir une demande applicative issue d’un routeur ou service métier ;
- construire les paramètres nécessaires à l’appel du runtime LLM ;
- appeler `app.domain.llm.runtime.gateway` ou son point d’entrée canonique ;
- convertir la réponse runtime vers le contrat applicatif attendu ;
- exposer un mapping d’erreurs applicatif stable, sans masquer les erreurs de gouvernance runtime ;
- offrir une surface publique explicitement justifiée par des consommateurs réels.

Le fichier ne doit pas contenir :

- de logique de prompting profonde ;
- de heuristique conversationnelle métier complexe ;
- de logique de narration métier ;
- de fallback de test ;
- de compatibilité avec d’anciens chemins ;
- de résolution runtime concurrente au gateway ;
- de duplicat de règles déjà présentes ailleurs.

## Acceptance Criteria

1. **AC1 - Audit d’utilité explicite**  
   La story produit une décision argumentée sur `backend/app/application/llm/ai_engine_adapter.py`, classée `keep`, `split-and-keep` ou `delete`.  
   La décision doit citer les consommateurs réels, les symboles consommés, les responsabilités conservées et les responsabilités déplacées ou supprimées.

2. **AC2 - Cible préférentielle `split-and-keep` sauf preuve contraire**  
   La décision par défaut est de conserver une façade applicative fine dans `application/llm`.  
   Une suppression complète ou un déplacement n’est accepté que si l’audit démontre un gain structurel supérieur et une migration complète des consommateurs.

3. **AC3 - Aucune suppression sans preuve**  
   Si le fichier est supprimé, tous les consommateurs backend et tests sont migrés vers des chemins canoniques explicites, sans shim durable, sans alias inverse et sans régression fonctionnelle.

4. **AC4 - Façade applicative fine si le fichier est conservé**  
   Si le fichier est conservé, il ne contient plus qu’un rôle de façade applicative entre les cas d’usage métier et le runtime LLM.  
   Les seules responsabilités autorisées sont la construction de requête applicative, l’appel au gateway, l’adaptation de réponse et le mapping d’erreurs applicatif stable.

5. **AC5 - Extraction ou suppression des responsabilités parasites**  
   Toute logique qui n’appartient pas clairement à la façade est extraite ou supprimée.  
   Cela couvre au minimum :
   - la détection hors scope partagée ;
   - les heuristiques d’ouverture ou de cadrage conversationnel ;
   - les helpers de fallback de test ;
   - les blocs de narration ou transformation métier ;
   - les helpers top-level non consommés nominalement ;
   - les duplications avec le runtime, le prompting, les services `llm_generation` ou `prediction`.

6. **AC6 - Destinations d’extraction justifiées**  
   Chaque extraction est placée dans la couche la plus naturelle :
   - logique runtime dans `domain/llm/runtime/*` ;
   - logique prompting dans `domain/llm/prompting/*` ;
   - logique métier de génération dans `services/llm_generation/*` ;
   - logique de narration dans `prediction/*` ou le service narratif canonique ;
   - logique de test dans les tests, fixtures ou helpers de test dédiés ;
   - logique applicative transversale uniquement dans `application/llm/*` si elle reste une orchestration applicative.

7. **AC7 - Aucun legacy réintroduit**  
   Aucun ancien chemin `app.services.ai_engine_adapter` n’est recréé.  
   Aucun wrapper, shim, alias de compatibilité ou import nominal de transition n’est ajouté autour de `AIEngineAdapter`.

8. **AC8 - Repositionnement uniquement si la cible est objectivement meilleure**  
   Si le fichier est déplacé, le nouveau chemin doit appartenir à une couche backend canonique et apporter une responsabilité plus claire que `application/llm`.  
   Si aucun gain net n’est démontré, le fichier reste sous `backend/app/application/llm/`.

9. **AC9 - DRY strict**  
   Aucun helper extrait ne duplique une logique déjà existante.  
   Toute duplication avec `services/llm_generation/*`, `domain/llm/runtime/*`, `domain/llm/prompting/*` ou `prediction/*` est supprimée, remplacée par un appel à l’existant ou factorisée dans un module dédié.

10. **AC10 - Surface publique minimale**  
    Les symboles exportés par `app.application.llm` sont limités aux symboles ayant un consommateur nominal prouvé.  
    `__all__`, le fichier `__init__.py` et les imports publics sont alignés avec cette surface minimale.

11. **AC11 - Pas de logique de test dans le chemin nominal**  
    Aucun fallback de test, helper de mock, comportement artificiel de test ou branche conditionnelle dédiée aux tests ne reste dans `backend/app/application/llm/ai_engine_adapter.py` ni dans un module nominal de production.

12. **AC12 - Documentation française complète et utile**  
    Chaque fichier créé ou significativement modifié contient un commentaire global en français en tête de fichier.  
    Les classes, fonctions publiques et fonctions non triviales ont des docstrings en français décrivant l’intention, les responsabilités et les limites.  
    Les commentaires purement descriptifs ou paraphrasant le code sont supprimés.

13. **AC13 - Tests alignés sur la décision finale**  
    Les tests unitaires et d’intégration liés à `AIEngineAdapter` sont mis à jour pour couvrir :
    - les imports retenus ;
    - les patch targets corrects ;
    - les méthodes publiques conservées ;
    - la disparition des helpers supprimés ;
    - les extractions éventuelles ;
    - les garde-fous anti-réintroduction legacy.

14. **AC14 - Garde-fous structurels anti-régression**  
    La story ajoute ou met à jour des tests de structure qui échouent si :
    - `app.services.ai_engine_adapter` réapparaît ;
    - un import nominal utilise un chemin legacy ou transitoire ;
    - un helper de test est importé dans le code de production ;
    - la façade expose des symboles publics non consommés ;
    - des patterns explicitement interdits de fallback ou de compatibilité sont réintroduits dans la façade.

15. **AC15 - Pas de cycle d’import ni inversion de dépendance**  
    La refactorisation ne crée pas de cycle d’import entre `application`, `services`, `domain`, `prediction` et `api`.  
    La direction des dépendances reste compatible avec la gouvernance backend.

16. **AC16 - Validation backend obligatoire**  
    La story n’est terminée que si les vérifications backend dans le venv ont été exécutées et tracées après refactorisation :
    - `ruff format .`
    - `ruff check .`
    - `pytest -q` ou suites ciblées explicitement justifiées.

17. **AC17 - Cohérence avec la gouvernance backend**  
    La décision finale reste compatible avec `docs/backend-structure-governance.md`, qui classe `application/` comme couche tolérée pour les adaptateurs applicatifs existants et interdit la recréation de couches parallèles inutiles.

18. **AC18 - Suppression complète de `backend/app/application` si la couche n’est plus justifiée**  
    Si l’audit conclut que le dossier `backend/app/application/` n’apporte plus de frontière utile, la story doit supprimer ce dossier.  
    Tous les fichiers encore présents à l’intérieur doivent alors être relocalisés vers une couche canonique plus pertinente (`services/`, `domain/`, `prediction/`, `api/` ou autre cible explicitement justifiée), avec migration complète des imports, sans shim transitoire, sans alias legacy et sans réintroduire une couche parallèle équivalente.

19. **AC19 - Analyse préalable des dossiers cibles de relocalisation**  
    Avant toute relocalisation de fichiers hors de `backend/app/application/`, la story doit analyser `backend/app/services/`, `backend/app/domain/`, `backend/app/api/` et `backend/app/prediction/` afin de vérifier s’il existe déjà des sous-dossiers canoniques prêts à recevoir ces fichiers relocalisés (`llm/`, ou une cible plus spécifique).  
    Cette analyse doit privilégier la réutilisation de l’existant, éviter la création de nouveaux sous-dossiers redondants et documenter explicitement les cibles retenues, les sous-dossiers candidats écartés et l’absence éventuelle de destination adaptée.

## Tasks / Subtasks

- [x] **Task 1: Auditer `ai_engine_adapter.py` et ses consommateurs**  
  AC: 1, 2, 3, 8, 10, 17  
  - [x] Cartographier tous les imports nominaux de `app.application.llm.ai_engine_adapter` dans `backend/app`, `backend/tests` et `backend/app/tests`.
  - [x] Identifier les symboles réellement consommés : `AIEngineAdapter`, `AIEngineAdapterError`, méthodes `generate_*`, helpers top-level, patch targets.
  - [x] Identifier les consommateurs indirects via `app.application.llm.__init__`.
  - [x] Distinguer les usages de production, les usages de test, les patchs de test et les reliquats de compatibilité.
  - [x] Produire une décision `keep`, `split-and-keep` ou `delete` dans les completion notes, avec justification.

- [x] **Task 2: Classer les responsabilités internes du fichier**  
  AC: 4, 5, 6, 9  
  - [x] Lister les blocs fonctionnels présents dans le fichier.
  - [x] Classer chaque bloc dans une catégorie : façade applicative, runtime, prompting, service métier, narration, test, legacy, utilitaire partagé.
  - [x] Identifier les duplications avec les modules existants.
  - [x] Identifier les fonctions publiques qui devraient devenir privées, être déplacées ou être supprimées.

- [x] **Task 3: Exécuter la cible structurelle retenue**  
  AC: 2, 3, 4, 5, 6, 7, 8, 15, 19  
  - [x] Analyser `backend/app/services/`, `backend/app/domain/`, `backend/app/api/` et `backend/app/prediction/` pour identifier les sous-dossiers existants prêts à recevoir d’éventuels fichiers relocalisés.
  - [x] Si la cible est `split-and-keep`, réduire `ai_engine_adapter.py` à une façade applicative fine.
  - [x] Si la cible est `keep`, justifier pourquoi aucune extraction n’apporte de gain structurel réel.
  - [x] Si la cible est `delete`, migrer tous les consommateurs vers les modules canoniques et supprimer le fichier.
  - [x] Si un déplacement est retenu, choisir un chemin canonique sans créer de nouvelle couche parallèle.
  - [x] Vérifier l’absence de cycle d’import après refactorisation.

- [x] **Task 4: Extraire ou supprimer les responsabilités parasites**  
  AC: 5, 6, 9, 11  
  - [x] Extraire ou supprimer la logique hors scope partagée.
  - [x] Extraire ou relocaliser les heuristiques de conversation hors de la façade si elles relèvent d’un service métier ou du prompting.
  - [x] Supprimer les fallbacks de test du chemin nominal.
  - [x] Déplacer les helpers de test vers des fixtures ou helpers de tests explicites.
  - [x] Réévaluer la logique de narration et la déplacer vers la couche narrative canonique si nécessaire.
  - [x] Remplacer toute duplication par un appel au module canonique existant.

- [x] **Task 5: Réduire la surface publique**  
  AC: 9, 10, 13, 14  
  - [x] Réduire `__all__` aux seuls symboles réellement consommés.
  - [x] Mettre à jour `backend/app/application/llm/__init__.py`.
  - [x] Rendre privés les helpers internes conservés.
  - [x] Supprimer les helpers publics non consommés.
  - [x] Mettre à jour les patch targets de tests pour ne plus dépendre d’internals déplacés ou supprimés.

- [x] **Task 6: Documenter en français**  
  AC: 12  
  - [x] Ajouter ou corriger le commentaire global en français en tête de chaque fichier modifié.
  - [x] Réécrire en français les docstrings des classes, fonctions publiques et fonctions non triviales.
  - [x] Documenter la frontière de responsabilité de `AIEngineAdapter`.
  - [x] Supprimer les commentaires cosmétiques qui paraphrasent le code.

- [x] **Task 7: Ajouter ou ajuster les tests de garde-fou**  
  AC: 7, 10, 11, 13, 14, 15  
  - [x] Mettre à jour les tests qui importent ou patchent `app.application.llm.ai_engine_adapter.*`.
  - [x] Ajouter un test échouant si `backend/app/services/ai_engine_adapter.py` réapparaît.
  - [x] Ajouter un test échouant si `app.services.ai_engine_adapter` est importé dans le backend ou les tests nominaux.
  - [x] Ajouter un test de surface publique sur `app.application.llm`.
  - [x] Ajouter un garde-fou contre les helpers de test dans le code de production.
  - [x] Ajouter, si pertinent, un test structurel empêchant la façade de réexposer des responsabilités runtime ou narration.

- [x] **Task 8: Validation finale**  
  AC: 13, 16  
  - [x] Activer le venv avant toute commande Python : `\.\.venv\Scripts\Activate.ps1`
  - [x] Exécuter `cd backend ; ruff format .`
  - [x] Exécuter `cd backend ; ruff check .`
  - [x] Exécuter `cd backend ; pytest -q` ou une campagne ciblée justifiée.
  - [x] Vérifier par recherche globale qu’aucun import nominal n’utilise un chemin legacy ou transitoire autour de `ai_engine_adapter`.
  - [x] Documenter dans les completion notes la décision finale, les fichiers modifiés, les extractions réalisées et les commandes exécutées.

## Dev Notes

### Developer Context

`backend/app/application/llm/ai_engine_adapter.py` est actuellement actif et référencé par des routeurs API, des services `llm_generation`, la prédiction publique et plusieurs suites de tests.

Le chemin `application/llm` a déjà été retenu comme cible canonique pour une façade applicative LLM. Cette story ne doit donc pas rouvrir le débat sur un retour vers `services/ai_engine_adapter.py`.

La question principale n’est pas “où mettre l’adapter ?”, mais plutôt : “quelle surface minimale doit rester dans l’adapter ?”.

### Structural Findings Already Known

- `backend/app/application/llm/ai_engine_adapter.py` expose aujourd’hui plusieurs helpers top-level et une classe `AIEngineAdapter`.
- Le fichier contient environ 918 lignes.
- `backend/app/services/ai_engine_adapter.py` n’existe plus.
- `docs/2026-04-21-audit-prompts-backend-post-story-70-15-v2.md` cite `ai_engine_adapter.py` comme façade applicative canonique active.
- `docs/backend-structure-governance.md` classe `backend/app/application/` comme couche tolérée pour les adaptateurs applicatifs existants, tant qu’ils ne dupliquent pas `services/`.

### Refactoring Guidance

La cible naturelle attendue est probablement `split-and-keep` :

- conserver `AIEngineAdapter` comme façade applicative ;
- déplacer la logique hors scope vers une policy ou un helper dédié si elle est réellement partagée ;
- déplacer la narration vers la couche narrative canonique ;
- déplacer les helpers de test vers les tests ;
- supprimer les helpers publics sans consommateur nominal ;
- conserver le chemin `application/llm` sauf preuve forte qu’un autre emplacement est meilleur.

Il faut éviter les micro-modules artificiels. L’extraction doit suivre une vraie responsabilité, pas seulement réduire le nombre de lignes.

### Anti-Patterns to Avoid

- Garder le fichier tel quel en ne changeant que les docstrings.
- Déplacer le fichier pour donner une impression de nettoyage sans gain de responsabilité.
- Recréer `backend/app/services/ai_engine_adapter.py`.
- Ajouter un alias de compatibilité durable.
- Laisser des fallbacks de test dans le code de production.
- Laisser la façade appeler ou réimplémenter une logique runtime déjà portée par le gateway.
- Laisser des tests patcher des détails internes instables.
- Ajouter des commentaires français qui paraphrasent le code.

### Testing Requirements

Vérifier en priorité les fichiers et zones qui importent ou patchent directement `AIEngineAdapter`, notamment :

- `backend/app/tests/unit/test_ai_engine_adapter.py`
- `backend/app/services/tests/test_ai_engine_adapter_refacto.py`
- `backend/tests/llm_orchestration/test_v2_validation.py`
- `backend/tests/llm_orchestration/test_story_66_19_narrator_migration.py`
- les tests `guidance`, `chat`, `natal` et `prediction` qui patchent `AIEngineAdapter.generate_*`

Si la surface publique change, ajuster aussi les imports dans :

- `backend/app/api/v1/routers/ai.py`
- `backend/app/api/v1/routers/natal_interpretation.py`
- `backend/app/services/llm_generation/guidance_service.py`
- `backend/app/services/llm_generation/chat_guidance_service.py`
- `backend/app/services/llm_generation/natal_interpretation_service.py`
- `backend/app/services/llm_generation/natal_interpretation_service_v2.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/llm_narrator.py`

## Completion Notes attendues

À la fin de la story, les notes de complétion doivent inclure :

- la décision finale : `keep`, `split-and-keep` ou `delete` ;
- la justification de cette décision ;
- la liste des consommateurs identifiés ;
- la surface publique finale ;
- les responsabilités supprimées ;
- les responsabilités extraites ;
- les nouveaux fichiers créés le cas échéant ;
- les tests ajoutés ou modifiés ;
- les commandes de validation exécutées ;
- les éventuelles suites ciblées utilisées à la place de `pytest -q`, avec justification.

## References

- [Source: AGENTS.md]
- [Source: docs/backend-structure-governance.md]
- [Source: docs/2026-04-21-audit-prompts-backend-post-story-70-15-v2.md]
- [Source: _bmad-output/implementation-artifacts/70-14-reorganiser-et-consolider-les-fichiers-du-process-llm-backend.md]
- [Source: _bmad-output/implementation-artifacts/70-15-basculer-la-source-de-verite-runtime-llm-vers-les-namespaces-canoniques.md]
- [Source: backend/app/application/llm/ai_engine_adapter.py]
- [Source: backend/app/application/llm/__init__.py]
- [Source: backend/app/api/v1/routers/ai.py]
- [Source: backend/app/api/v1/routers/natal_interpretation.py]
- [Source: backend/app/services/llm_generation/guidance_service.py]
- [Source: backend/app/services/llm_generation/chat_guidance_service.py]
- [Source: backend/app/services/llm_generation/natal_interpretation_service.py]
- [Source: backend/app/services/llm_generation/natal_interpretation_service_v2.py]
- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/prediction/llm_narrator.py]
- [Source: backend/app/domain/llm/runtime/gateway.py]

## Dev Agent Record

### Implementation Plan

- Auditer les consommateurs nominaux de `app.application.llm.ai_engine_adapter` pour isoler la surface réellement utile.
- Extraire les responsabilités non applicatives vers les couches naturelles (`domain/llm/prompting`, `prediction`, `services/llm_generation`, `app/tests`).
- Réduire `AIEngineAdapter` à quatre méthodes publiques métier plus `AIEngineAdapterError`.
- Réaligner les services et les tests sur les nouveaux modules d’extraction et sur une infrastructure de doubles de tests dédiée.
- Ajouter des garde-fous structurels puis valider avec Ruff et Pytest ciblé.

### Debug Log

- Audit des consommateurs nominaux effectué par recherche globale sur `backend/app`, `backend/tests` et `backend/app/tests`.
- Décision retenue : `delete`.
- `build_opening_chat_user_data_block` déplacé vers `backend/app/domain/llm/prompting/chat_opening.py` pour supprimer la dépendance runtime -> application.
- La narration horoscope gateway a été déplacée vers `backend/app/prediction/llm_gateway_narrator.py`.
- Les hooks de tests `set_test_*` / `reset_test_generators` ont été sortis de la prod vers `backend/app/tests/helpers/llm_adapter_stub.py` et branchés via `backend/app/tests/conftest.py`.
- L’analyse des dossiers cibles a retenu `backend/app/domain/llm/runtime/` comme destination canonique, a écarté `services/llm_generation/` car consommateur direct de la façade, `api/` car couche transport, et `prediction/` car trop spécifique à la narration.
- Les mappings d’erreurs et l’exception applicative ont été relocalisés dans `backend/app/domain/llm/runtime/adapter_errors.py`.

### Completion Notes

- Décision finale : `delete`.
- Justification : les consommateurs nominaux réels restent centrés sur `AIEngineAdapter` et `AIEngineAdapterError`, mais l’analyse AC19 a montré qu’un sous-dossier canonique existait déjà sous `backend/app/domain/llm/runtime/`. Garder `backend/app/application/` n’apportait plus de frontière utile et entretenait une couche parallèle redondante.
- Consommateurs identifiés : routeurs API (`backend/app/api/v1/routers/ai.py`, `backend/app/api/v1/routers/natal_interpretation.py`), services métier (`backend/app/services/llm_generation/chat_guidance_service.py`, `guidance_service.py`, `natal_interpretation_service.py`, `natal_interpretation_service_v2.py`), projection publique (`backend/app/prediction/public_projection.py`) et suites de tests patchant `AIEngineAdapter.generate_*`.
- Surface publique finale : `app.domain.llm.runtime.__all__ = ["AIEngineAdapter", "AIEngineAdapterError"]`.
- Responsabilités supprimées de la façade : hooks de test globaux, fallback nominal dépendant d’un provider non configuré, helpers top-level publics non justifiés.
- Responsabilités extraites :
  - ouverture de chat vers `backend/app/domain/llm/prompting/chat_opening.py` ;
  - narration horoscope via gateway vers `backend/app/prediction/llm_gateway_narrator.py` ;
  - détection hors-scope partagée vers `backend/app/services/llm_generation/off_scope_policy.py` ;
  - mappings d’erreurs applicatives vers `backend/app/domain/llm/runtime/adapter_errors.py` ;
  - infrastructure de doubles de tests vers `backend/app/tests/helpers/llm_adapter_stub.py` et `backend/app/tests/conftest.py`.
- Nouveaux fichiers créés :
  - `backend/app/domain/llm/runtime/adapter.py`
  - `backend/app/domain/llm/runtime/adapter_errors.py`
  - `backend/app/domain/llm/prompting/chat_opening.py`
  - `backend/app/prediction/llm_gateway_narrator.py`
  - `backend/app/services/llm_generation/off_scope_policy.py`
  - `backend/app/tests/helpers/llm_adapter_stub.py`
  - `backend/app/tests/unit/test_ai_engine_adapter_structure.py`
- Tests ajoutés ou modifiés :
  - garde-fous structurels sur la surface publique et le legacy ;
  - réalignement des tests `chat`, `guidance`, `narrator migration`, `v2 validation` et des intégrations API qui utilisaient l’ancien backdoor de tests.
  - ajout d’un garde-fou unitaire sur `GuidanceService` pour normaliser les sorties structurées LLM mal typées (`str` au lieu de `list[str]`) sur les flux périodiques et contextuels.
- Commandes exécutées :
  - `.\.venv\Scripts\Activate.ps1 ; cd backend ; ruff format .`
  - `.\.venv\Scripts\Activate.ps1 ; cd backend ; ruff check` ciblé sur les fichiers touchés
  - `.\.venv\Scripts\Activate.ps1 ; cd backend ; pytest -q app/tests/unit/test_ai_engine_adapter.py app/tests/unit/test_ai_engine_adapter_structure.py app/services/tests/test_ai_engine_adapter_refacto.py tests/llm_orchestration/test_llm_gateway_routing.py tests/llm_orchestration/test_story_66_19_narrator_migration.py tests/llm_orchestration/test_v2_validation.py app/tests/unit/test_chat_guidance_service.py app/tests/unit/test_guidance_service.py app/tests/integration/test_chat_idempotence.py app/tests/integration/test_chat_persona_prompting.py app/tests/integration/test_chat_api.py app/tests/integration/test_guidance_api.py`
  - `.\.venv\Scripts\Activate.ps1 ; cd backend ; pytest -q app/tests/integration/test_guidance_api.py app/tests/integration/test_consultations_router.py app/tests/integration/test_consultation_catalogue.py app/tests/integration/test_consultation_third_party.py app/tests/integration/test_ops_monitoring_api.py -q`
  - `.\.venv\Scripts\Activate.ps1 ; cd backend ; pytest -q`
- Validation finale : suite backend complète verte (`3033 passed, 12 skipped`).

## File List

- backend/app/domain/llm/runtime/__init__.py
- backend/app/domain/llm/runtime/adapter.py
- backend/app/domain/llm/runtime/adapter_errors.py
- backend/app/domain/llm/prompting/chat_opening.py
- backend/app/domain/llm/runtime/gateway.py
- backend/app/prediction/llm_gateway_narrator.py
- backend/app/services/llm_generation/chat_guidance_service.py
- backend/app/services/llm_generation/guidance_service.py
- backend/app/services/llm_generation/off_scope_policy.py
- backend/app/tests/conftest.py
- backend/app/tests/helpers/llm_adapter_stub.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/integration/test_chat_idempotence.py
- backend/app/tests/integration/test_chat_persona_prompting.py
- backend/app/tests/integration/test_guidance_api.py
- backend/app/tests/unit/test_ai_engine_adapter.py
- backend/app/tests/unit/test_ai_engine_adapter_structure.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/app/tests/unit/test_guidance_service.py
- backend/tests/llm_orchestration/test_llm_gateway_routing.py
- backend/tests/llm_orchestration/test_story_66_19_narrator_migration.py
- backend/tests/llm_orchestration/test_v2_validation.py

## Change Log

- 2026-04-25: refactor `split-and-keep` initial de `ai_engine_adapter.py`, extraction des responsabilités parasites, suppression des hooks de test nominaux et ajout de garde-fous structurels.
- 2026-04-25: mise en oeuvre de l'AC18/AC19, suppression du dossier `backend/app/application/`, relocalisation de la façade vers `backend/app/domain/llm/runtime/` et migration complète des imports nominaux.
- 2026-04-25: stabilisation finale de `GuidanceService` sur les sorties structurées LLM mal typées, complétion de la validation backend complète et passage de la story en `done`.
