# Story 66.33: Durcissement opérationnel de l’appel provider OpenAI

Status: completed

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want durcir le runtime opérationnel de l’appel provider OpenAI nominal,
so that le seul provider effectivement exécuté par la plateforme reste exploitable en conditions réelles avec des retries bornés, des timeouts explicites, une gestion propre des rate limits, un mode dégradé maîtrisé, une taxonomie d’erreurs fine et des métriques d’exploitation fiables.

## Contexte

Les stories 66.18, 66.22, 66.25, 66.30, 66.31 et 66.32 ont progressivement convergé vers une doctrine claire :

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) n’exécute effectivement que `openai` dans `_call_provider()` ; tout autre provider est désormais soit interdit sur le périmètre supporté, soit borné à une compatibilité legacy hors nominal.
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) documente explicitement qu’`openai` est le seul provider nominalement supporté et que `_call_provider()` ne route que vers lui.
- [backend/app/llm_orchestration/providers/responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/responses_client.py) porte déjà une première couche de robustesse : timeout enveloppant via `asyncio.wait_for()`, retries bornés via `AI_ENGINE_MAX_RETRIES`, backoff exponentiel avec jitter, mapping partiel de `RateLimitError`, `APITimeoutError` et `APIConnectionError`.
- [backend/app/ai_engine/config.py](/c:/dev/horoscope_front/backend/app/ai_engine/config.py) centralise déjà quelques paramètres globaux (`timeout_seconds`, `max_retries`, `retry_base_delay_ms`, `retry_max_delay_ms`), mais cette granularité est encore trop grossière pour un runtime mature pilotant plusieurs familles (`chat`, `guidance`, `natal`, `horoscope_daily`) avec des profils de latence et d’idempotence différents.
- [backend/app/ai_engine/exceptions.py](/c:/dev/horoscope_front/backend/app/ai_engine/exceptions.py) expose aujourd’hui un socle d’erreurs utile (`UpstreamRateLimitError`, `UpstreamTimeoutError`, `UpstreamError`), mais trop agrégé pour distinguer saturation temporaire, quota épuisé, refus explicite du provider, incident réseau, timeout local, timeout upstream, circuit breaker ouvert ou réponse structurellement invalide.
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py) persiste déjà `requested_provider`, `resolved_provider`, `executed_provider`, `pipeline_kind`, `execution_path_kind`, `fallback_kind` et les identifiants de snapshot actif ; cette base d’observabilité est donc prête à accueillir des signaux plus fins sur la santé opérationnelle du provider.

Le trou restant n’est plus un problème de doctrine provider. C’est un problème d’exploitation runtime :

- les retries actuels ne distinguent pas clairement les erreurs idempotentes retryables des erreurs terminales non retryables ;
- le timeout est transmis comme un scalaire unique par appel, sans politique explicite par famille ni sous-budget par tentative ;
- les rate limits sont remontés, mais pas encore pilotés avec stratégie dédiée (`Retry-After`, fenêtre de refroidissement, saturation visible) ;
- aucun circuit breaker ou mode dégradé canonique ne protège aujourd’hui la plateforme d’un provider OpenAI instable ;
- la taxonomie d’erreurs provider reste trop plate pour supporter un pilotage ops précis ;
- la métrique d’exploitation actuelle sait déjà raconter le chemin d’exécution, mais pas encore la santé de l’appel provider lui-même : saturation, réparations, retries, ouvertures/fermetures du breaker, latence par famille, épuisement budgétaire de tentatives.

Autrement dit : la plateforme a fermé les providers concurrents, mais elle n’a pas encore porté le provider nominal unique au niveau d’un runtime d’exploitation mature.

## Diagnostic exact à préserver

- La cible de cette story n’est **pas** de réintroduire un second provider, ni d’assouplir la doctrine “OpenAI only”.
- La cible n’est **pas** non plus de déplacer la robustesse dans `AIEngineAdapter` ou dans les routeurs API. Le durcissement doit vivre au plus près de l’appel provider nominal, puis être propagé proprement au gateway, aux services et à l’observabilité.
- Le retry actuel dans `ResponsesClient._execute_with_retry()` est encore “générique” : il applique la même enveloppe à presque tout, sans distinction fine par famille, sans budget global de tentative et sans lecture structurée des signaux upstream.
- L’unité du circuit breaker ne doit pas être laissée implicite. Un breaker par `provider + family` est la cible nominale la plus sûre pour éviter qu’un incident localisé à `natal` coupe aussi `chat`.
- L’idempotence à retenir ici est une **idempotence produit** sur une opération de génération sans side effect produit interne ; elle ne garantit jamais une sortie modèle bit-à-bit identique entre tentatives.
- `RateLimitError` est aujourd’hui transformée immédiatement en `UpstreamRateLimitError()` avec `retry_after_ms` par défaut, sans tentative d’extraction d’un `Retry-After`, d’un identifiant de requête provider, ni d’une distinction entre burst temporaire et quota/limite plus structurelle.
- `_call_provider()` considère actuellement que `executed_provider == plan.provider`, ce qui reste vrai tant qu’il n’existe pas de mode dégradé plus sophistiqué ; la story 66.33 doit préserver la vérité de cette lecture tout en enrichissant l’axe “mode d’exécution provider” et la télémétrie d’état.
- La réparation de sortie (`repair`) existe déjà au niveau du gateway, mais elle est orthogonale au retry provider. La story 66.33 doit éviter toute confusion entre “réparer une sortie invalide” et “rejouer un appel provider échoué”.
- Le snapshot d’observabilité 66.25 et le snapshot de release 66.32 fournissent déjà la trame de traçabilité. 66.33 doit enrichir cette trame, pas créer un canal parallèle opaque.
- Le `retry_budget_exhausted` est un état opérationnel distinct, utile pour le tuning SRE, et ne doit pas être noyé dans `timeout` ou `connection_error`.
- Le mode dégradé doit être compté comme tel jusque dans les dashboards : jamais comme succès nominal provider.

## Cible d'architecture

Introduire un **Provider Runtime Hardening Layer** centré sur OpenAI, porté par `ResponsesClient` ou un composant dédié voisin, qui devienne la seule frontière de robustesse opérationnelle pour l’appel nominal `responses.create()`.

Cette couche doit :

1. appliquer des retries **bornés, idempotents et explicitement classifiés** ;
2. imposer des **timeouts explicites par famille d’usage** et par tentative ;
3. gérer proprement les **rate limits** avec respect des signaux upstream et exposition de saturation ;
4. introduire un **circuit breaker** et un **mode dégradé** configurables, sans inventer de faux succès ;
5. produire une **taxonomie fine d’erreurs provider** stable et testable ;
6. alimenter les **métriques d’exploitation** sur latence, saturation, retries, erreurs terminales et réparations de disponibilité ;
7. rester compatible avec la doctrine actuelle : `openai` unique provider nominalement exécuté, sans réouverture du multi-provider.

## Invariants opérationnels à imposer

- **Unité de breaker explicite** : l’unité nominale du circuit breaker doit être explicitement définie. La cible recommandée est un breaker par `provider + family`, avec possibilité d’un breaker global OpenAI de dernier recours. Un breaker purement global ne doit pas être la seule granularité nominale.
- **Idempotence produit explicite** : “retries idempotents” signifie ici **idempotence produit** pour une opération `responses.create()` purement générationnelle sans side effect interne côté produit. Cela ne signifie jamais identité binaire de la sortie modèle entre tentatives.
- **Santé provider séparée de la disponibilité** : la taxonomie doit distinguer au minimum connectivité/timeout, saturation rate limit, rejet auth/config, incident serveur provider (`5xx`), breaker ouvert, et budget de retry épuisé.
- **Comptage strict du mode dégradé** : un résultat servi en mode dégradé ne doit jamais incrémenter les métriques de succès nominal provider.
- **Décision `409` explicite** : la story doit imposer une politique explicite sur les `409 Conflict` retryés par défaut par le SDK OpenAI, afin d’éviter de reproduire implicitement ce comportement sans l’assumer.
- **Contrat aval explicite** : les surfaces métier doivent préciser ce qu’elles renvoient en cas de saturation, de breaker ouvert ou de retry budget épuisé : `503` retryable, payload structuré avec `retry_after_ms`, ou code fonctionnel dégradé borné.

## Latest Technical Specifics

Les informations externes à intégrer dans la story pour éviter une implémentation datée sont les suivantes :

- Le SDK officiel [`openai-python`](https://github.com/openai/openai-python) documente que les requêtes sont **retried twice by default** et que les timeouts sont, par défaut, de **10 minutes** ; il accepte aussi un `timeout` plus fin basé sur `httpx.Timeout`. Cette story doit donc éviter le double-jeu “SDK retry implicite + retry applicatif maison non coordonné” et expliciter si l’on désactive ou encadre `max_retries` côté SDK pour garder une seule politique de vérité. Source : [openai/openai-python README](https://github.com/openai/openai-python).
- Le même SDK documente l’accès aux **raw response headers** via `.with_raw_response`, ce qui ouvre une voie canonique pour capter `Retry-After`, `x-request-id` et d’autres headers utiles à l’exploitation. Source : [openai/openai-python README](https://github.com/openai/openai-python).
- Le SDK expose des erreurs typées (`RateLimitError`, `APITimeoutError`, `APIConnectionError`). La story 66.33 doit donc mapper proprement ces signaux typés vers une taxonomie interne plus fine au lieu de les réécraser immédiatement en erreurs génériques.

Inférence à partir de ces sources officielles :

- si le projet conserve un retry applicatif explicite dans `ResponsesClient`, il doit vraisemblablement **neutraliser ou cadrer** les retries implicites du SDK afin que les métriques, le budget temporel et le circuit breaker reflètent la réalité opérationnelle ;
- l’accès aux headers upstream permet de rendre la gestion des rate limits bien plus précise qu’un `retry_after_ms=60000` codé en dur.

## Acceptance Criteria

1. **AC1 — Politique de retry unique, bornée et idempotente** : le runtime OpenAI applique une seule politique de retry de vérité, explicitement documentée et testée. Elle ne retry que les erreurs classées retryables/idempotentes au sens de l’idempotence produit (ex: timeout réseau, connection reset, 429 temporaire admissible, et `409` uniquement si la plateforme décide explicitement de le traiter comme retryable dans ce contexte), avec un nombre maximal de tentatives borné, un budget temporel global borné et sans double retry implicite non maîtrisé entre SDK et couche applicative.
2. **AC2 — Classification retryable vs terminale explicite** : avant toute nouvelle tentative, la couche provider classe l’échec en au minimum `retryable_transient`, `retryable_rate_limited`, `non_retryable_provider_rejection`, `non_retryable_bad_request`, `non_retryable_auth_config`, ou taxonomie stable équivalente. Cette décision est testable et observable.
3. **AC3 — Timeouts explicites par famille** : la configuration expose des timeouts distincts au minimum pour `chat`, `guidance`, `natal`, `horoscope_daily`, ainsi qu’un budget de tentative cohérent avec ces familles. Le runtime ne dépend plus d’un seul timeout global indistinct pour tous les appels OpenAI.
4. **AC4 — Timeouts multi-niveaux cohérents** : l’implémentation distingue explicitement au moins : timeout enveloppe globale d’appel, timeout par tentative provider, et éventuel timeout de lecture/connexion si le client HTTP le permet. La documentation précise la priorité entre ces niveaux et interdit les contradictions silencieuses.
5. **AC5 — Gestion propre des rate limits et erreurs serveur** : un `RateLimitError` ou équivalent est converti en erreur interne stable transportant au minimum `error_code`, `retry_after_ms` quand disponible, `provider_request_id` si récupérable, et un discriminant distinguant une saturation temporaire d’un quota/blocage plus structurel lorsque le signal upstream le permet. Les erreurs serveur provider (`5xx`) sont aussi classées explicitement comme incidents upstream distincts.
6. **AC6 — Backoff conforme à la saturation** : la stratégie de retry sur rate limit utilise un backoff borné avec jitter, respecte `Retry-After` lorsqu’il est disponible, et arrête explicitement de retry lorsque le budget maximal de tentative ou de temps est dépassé.
7. **AC7 — Circuit breaker provider** : un circuit breaker dédié au runtime OpenAI existe avec au minimum les états `closed`, `open`, `half_open` ou équivalent stable, des seuils configurables d’ouverture, une fenêtre glissante d’évaluation, une fenêtre de cooldown, et une stratégie de sondage/réouverture explicite. L’unité nominale du breaker est `provider + family`, avec possibilité d’un breaker global OpenAI de dernier recours explicitement distinct.
8. **AC8 — Mode dégradé explicite sans faux succès** : lorsque le circuit breaker est ouvert ou que la stratégie d’exploitation décide de court-circuiter l’appel provider, le runtime n’invente pas une réponse nominale. Il retourne soit une erreur explicite et retryable côté produit, soit un mode dégradé explicitement borné et déjà supporté par le produit, avec télémétrie dédiée. Aucun succès silencieux ne masque l’état dégradé.
9. **AC9 — Taxonomie fine des erreurs provider** : la couche provider publie une taxonomie d’erreurs stable couvrant au minimum : `provider_rate_limited`, `provider_quota_exhausted`, `provider_timeout`, `provider_connection_error`, `provider_server_error`, `provider_circuit_open`, `provider_response_invalid`, `provider_auth_error`, `provider_bad_request`, `retry_budget_exhausted`, `provider_internal_error`. Les codes retenus peuvent varier, mais la séparation sémantique doit être équivalente et testée.
10. **AC10 — Propagation propre jusqu’aux surfaces avales** : le gateway, `AIEngineAdapter`, les routeurs API et l’observabilité consomment cette taxonomie fine sans la réécraser immédiatement en un unique `llm_unavailable`. Une agrégation produit reste possible, mais les détails exploitables demeurent disponibles dans `details`, logs et métriques. Le contrat de surface aval est explicité pour les scénarios de saturation, `breaker_open` et `retry_budget_exhausted`.
11. **AC11 — Métriques de saturation, latence, erreurs et réparations** : la plateforme émet des métriques dédiées au provider OpenAI couvrant au minimum :
    - volume d’appels ;
    - latence par famille et par statut ;
    - histogramme `attempt_count` ;
    - nombre de retries et tentatives moyennes ;
    - ratio `success_after_retry` ;
    - taux de rate limit ;
    - ouvertures, demi-ouvertures et fermetures du circuit breaker ;
    - erreurs terminales par catégorie ;
    - réparations/opérations de recovery liées à la disponibilité provider.
12. **AC12 — Logs structurés provider-centric** : chaque appel provider logué expose au minimum `request_id`, `trace_id`, `feature`, `subfeature`, `active_snapshot_id`, `model`, `attempt_count`, `timeout_budget_ms`, `retry_classification`, `provider_request_id` si disponible, `breaker_scope`, `breaker_state`, `error_code` final et latence finale.
13. **AC13 — Observabilité canonique enrichie** : `obs_snapshot`, `GatewayMeta` ou une structure voisine stable relaient au moins le `executed_provider_mode` (nominal, breaker_open, degraded, rate_limited_terminal ou équivalent), le `attempt_count`, le `provider_error_code` final, l’état du breaker et le scope du breaker, sans casser la sémantique 66.25/66.32 existante.
14. **AC14 — Configuration centralisée et bornée** : les paramètres opérationnels OpenAI (timeouts par famille, retries max, backoff, seuils de breaker, cooldown, sondes half-open) sont centralisés dans la configuration applicative, documentés et validés au boot. Les valeurs incohérentes ou dangereuses sont bloquées fail-fast.
15. **AC15 — Couverture tests non-régression** : des tests couvrent au minimum :
    - timeout retryable puis succès ;
    - timeout jusqu’à épuisement du budget ;
    - rate limit avec `Retry-After` ;
    - rate limit terminal sans retry additionnel ;
    - erreur d’auth/config non retryable ;
    - erreur de connexion ouvrant le circuit breaker ;
    - état `half_open` refermant le breaker après succès ;
    - état `half_open` réouvrant le breaker après échec ;
    - propagation des métriques/logs/erreurs structurées jusqu’au gateway.
16. **AC16 — Documentation d’exploitation réalignée** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) et [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md) documentent explicitement la politique de retry, les timeouts par famille, la gestion des rate limits, le circuit breaker, le mode dégradé, et la taxonomie d’erreurs provider.

## Tasks / Subtasks

- [x] Task 1: Introduire une couche de robustesse provider OpenAI explicite (AC1, AC2, AC9, AC14)
  - [x] Créer ou extraire un composant dédié de politique runtime provider dans `backend/app/llm_orchestration/providers/` ou `services/`.
  - [x] Y centraliser la classification des erreurs retryables vs terminales.
  - [x] Décider explicitement si les retries implicites du SDK OpenAI sont désactivés, conservés à zéro ou strictement encapsulés.

- [x] Task 2: Timeouts et budgets par famille (AC3, AC4, AC14)
  - [x] Étendre [backend/app/ai_engine/config.py](/c:/dev/horoscope_front/backend/app/ai_engine/config.py) avec des timeouts explicites par famille ou par classe d’appel.
  - [x] Documenter la relation entre timeout global d’appel, timeout par tentative et timeout HTTP fin si utilisé.
  - [x] Valider ces paramètres au boot avec garde-fous fail-fast.

- [x] Task 3: Gestion propre des rate limits (AC5, AC6, AC9, AC12)
  - [x] Extraire `Retry-After` et, si accessible, un identifiant de requête provider depuis la réponse brute.
  - [x] Introduire une erreur structurée dédiée aux rate limits temporaires et une autre pour les cas assimilables à quota terminal si le signal upstream le permet.
  - [x] Décider explicitement du traitement des `409 Conflict` retryés par défaut par le SDK OpenAI.
  - [x] Aligner backoff, jitter et arrêt des retries sur cette classification.

- [x] Task 4: Circuit breaker et mode dégradé (AC7, AC8, AC11, AC13)
  - [x] Introduire un circuit breaker dédié à l’appel OpenAI nominal.
  - [x] Figer explicitement l’unité nominale du breaker (`provider + family`) et la place éventuelle d’un breaker global de dernier recours.
  - [x] Exposer son état dans les logs et métriques.
  - [x] Définir le comportement applicatif exact quand le breaker est `open` : erreur explicite, signal retryable, ou mode dégradé déjà supporté et tracé.

- [x] Task 5: Taxonomie fine et propagation des erreurs (AC9, AC10, AC12, AC13)
  - [x] Enrichir [backend/app/ai_engine/exceptions.py](/c:/dev/horoscope_front/backend/app/ai_engine/exceptions.py) ou un module dédié voisin avec des sous-types/`error_code` plus fins.
  - [x] Réaligner le mapping dans [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py) et dans les routeurs consommateurs pour éviter l’écrasement prématuré de l’information.
  - [x] Propager `attempt_count`, `provider_error_code`, `breaker_state` et `provider_request_id` jusqu’à `GatewayMeta`/`obs_snapshot` quand disponible.

- [x] Task 6: Observabilité et métriques d’exploitation (AC11, AC12, AC13)
  - [x] Étendre [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py) et la persistance associée pour stocker les discriminants provider runtime supplémentaires.
  - [x] Ajouter des compteurs/histogrammes dédiés à la saturation, à la latence et aux transitions de circuit breaker.
  - [x] Vérifier que ces signaux restent corrélables avec `feature`, `subfeature`, `executed_provider`, `active_snapshot_id` et `manifest_entry_id`.

- [x] Task 7: Documentation et runbook (AC8, AC14, AC16)
  - [x] Mettre à jour [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) avec la politique runtime OpenAI durcie.
  - [x] Réaligner [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md).
  - [x] Ajouter un runbook d’incident “OpenAI saturation / breaker open / recovery”.

- [x] Task 8: Couverture de tests ciblée (AC1 à AC16)
  - [x] Étendre [backend/app/tests/unit/test_responses_client_exceptions.py](/c:/dev/horoscope_front/backend/app/tests/unit/test_responses_client_exceptions.py), [backend/app/llm_orchestration/tests/test_responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_responses_client.py) et les suites gateway associées.
  - [x] Ajouter des tests d’intégration couvrant propagation des erreurs, métriques et observabilité.
  - [x] Ajouter des tests dédiés au circuit breaker.

- [ ] Task 9: Vérification locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblées du provider runtime, du gateway et de l’observabilité liées à 66.25, 66.30, 66.31, 66.32 et 66.33.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- `ResponsesClient` est aujourd’hui le meilleur point de fermeture opérationnelle : c’est là que vivent déjà timeout enveloppant, retries, mapping des erreurs OpenAI et transmission des headers applicatifs (`x-request-id`, `x-trace-id`, `x-use-case`).
- Le périmètre nominal supporté est déjà fermé par 66.22 et 66.30 ; il ne faut pas rouvrir un fallback provider concurrent sous prétexte d’ajouter un mode dégradé.
- La story doit séparer clairement :
  - retry provider ;
  - repair de sortie ;
  - fallback use case legacy ;
  - rejet runtime canonique ;
  - mode dégradé piloté par breaker.
- L’observabilité 66.25 et la release active 66.32 existent déjà. 66.33 doit s’y brancher, pas inventer une journalisation parallèle impossible à corréler.

### Ce que le dev ne doit pas faire

- Ne pas laisser coexister deux politiques de retry non coordonnées entre SDK OpenAI et `ResponsesClient`.
- Ne pas transformer tout échec OpenAI en simple `UpstreamError` générique.
- Ne pas traiter un circuit breaker ouvert comme un succès nominal.
- Ne pas implémenter un breaker purement global comme seule granularité nominale.
- Ne pas recoder la gestion des retries/rate limits dans `AIEngineAdapter` ou dans les routeurs HTTP.
- Ne pas réintroduire `resolve_model()` ou un fallback multi-provider pour “sauver” un incident OpenAI sur le périmètre nominal supporté.
- Ne pas perdre l’identifiant `request_id` / `trace_id` / `provider_request_id` à travers les retries.
- Ne pas produire de métriques sans labels stables ou non corrélables avec `feature/subfeature`.
- Ne pas compter un résultat dégradé dans les métriques de succès nominal provider.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/providers/responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/responses_client.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/ai_engine/config.py](/c:/dev/horoscope_front/backend/app/ai_engine/config.py)
- [backend/app/ai_engine/exceptions.py](/c:/dev/horoscope_front/backend/app/ai_engine/exceptions.py)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/tests/test_responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_responses_client.py)
- [backend/app/tests/unit/test_responses_client_exceptions.py](/c:/dev/horoscope_front/backend/app/tests/unit/test_responses_client_exceptions.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)

### Previous Story Intelligence

- **66.18** a encapsulé les options OpenAI derrière des profils internes stables ; 66.33 doit faire la même chose pour la robustesse opérationnelle, sans exposer directement une logique de retry brute dans les couches amont.
- **66.22** a fermé le support nominal aux seuls providers autorisés ; 66.33 doit assumer OpenAI comme seul provider nominal, puis le traiter comme une dépendance critique à exploiter proprement.
- **66.25** a introduit le snapshot canonique d’observabilité ; 66.33 doit y brancher `attempt_count`, état du breaker, saturation et taxonomie d’erreurs provider.
- **66.30** a supprimé `resolve_model()` comme vérité finale sur le périmètre supporté ; 66.33 ne doit réintroduire aucun “sauvetage” implicite du même genre au niveau availability.
- **66.31** a introduit la validation fail-fast de cohérence ; 66.33 doit rester au niveau runtime opérationnel et non brouiller cohérence de configuration et incident provider.
- **66.32** a imposé la release active comme vérité runtime ; 66.33 doit garder la corrélation entre incident provider et `active_snapshot_id/version`.

### Git Intelligence

Commits récents pertinents observés :

- `f9c6012e` : `docs(llm): tighten story 66.32 snapshot scope and freeze model`
- `182000fa` : `docs(llm): close story 66.32 artifact and release snapshot docs`
- `d92be25f` : `fix(llm): strictly decouple snapshot validation from live tables and fix async delete await`
- `546f2585` : `fix(llm): decouple snapshot validation from live tables and prioritize snapshot at boot`
- `8238dccf` : `fix(llm): harden story 66.32 frozen contract and observability traceability`

Pattern à réutiliser :

- fermer l’ambiguïté runtime dans le code avant d’élargir la documentation ;
- introduire des discriminants stables et testables ;
- garder une seule source de vérité par axe d’exploitation ;
- prouver la robustesse par suites ciblées, pas par intuition.

### Testing Requirements

- Ajouter un test unitaire où une première tentative lève `asyncio.TimeoutError`, la seconde réussit, et les métriques/logs reflètent `attempt_count=2`.
- Ajouter un test unitaire où `RateLimitError` fournit un `Retry-After` exploitable et vérifier qu’il est propagé dans l’erreur structurée.
- Ajouter un test unitaire sur la décision `409 retryable` ou `409 non retryable`, selon la politique retenue.
- Ajouter un test unitaire où une erreur d’auth/config OpenAI est classée non retryable et n’ouvre pas de boucle de retry.
- Ajouter un test unitaire où des erreurs de connexion répétées ouvrent le circuit breaker.
- Ajouter un test unitaire `half_open -> success -> close`.
- Ajouter un test unitaire `half_open -> failure -> reopen`.
- Ajouter un test unitaire où l’épuisement du budget de retry produit explicitement `retry_budget_exhausted`.
- Ajouter un test d’intégration où `GatewayMeta`/`obs_snapshot` exposent `provider_error_code`, `attempt_count` et `breaker_state`.
- Ajouter un test d’intégration où `GatewayMeta`/`obs_snapshot` exposent aussi le scope du breaker.
- Ajouter un test d’intégration où le mode dégradé reste explicite et n’est pas compté comme succès nominal.
- Ajouter un test garantissant qu’un appel supporté OpenAI ne subit pas un double budget de retry caché.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest app/llm_orchestration/tests/test_responses_client.py -q`
  - `pytest app/tests/unit/test_responses_client_exceptions.py -q`
  - ajouter les suites dédiées 66.33 si elles sont créées

### Project Structure Notes

- Travail backend + documentation uniquement.
- Aucun changement frontend n’est attendu.
- Les modifications doivent rester concentrées dans `backend/app/llm_orchestration/providers/`, `backend/app/ai_engine/`, `backend/app/llm_orchestration/services/`, `backend/tests/` et `docs/`.

### References

- [backend/app/llm_orchestration/providers/responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/responses_client.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/ai_engine/config.py](/c:/dev/horoscope_front/backend/app/ai_engine/config.py)
- [backend/app/ai_engine/exceptions.py](/c:/dev/horoscope_front/backend/app/ai_engine/exceptions.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [66-18-encapsuler-options-openai-profils-stables.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-18-encapsuler-options-openai-profils-stables.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md)
- [66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md)
- [66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md)
- [openai/openai-python README](https://github.com/openai/openai-python)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Introduction d’un `ProviderRuntimeManager` dédié entre `gateway._call_provider()` et `ResponsesClient` pour porter retries, breaker, budgets temporels et classification d’erreurs.
- Les retries implicites du SDK OpenAI sont neutralisés afin de garder une seule politique applicative de vérité, avec extraction des headers upstream via `with_raw_response`.
- Le circuit breaker est désormais piloté par scope `provider:family`, avec fenêtre glissante, `half_open` explicite et signalement `circuit_open` distinct en observabilité.
- La taxonomie provider est propagée jusqu’à `AIEngineAdapter`, au snapshot canonique et à `llm_call_logs`, y compris sur le chemin d’erreur.
- Couverture ajoutée pour les métadonnées d’observabilité en cas d’échec provider et pour le mapping applicatif structuré de `upstream_circuit_open` et `retry_budget_exhausted`.

### File List

- `_bmad-output/implementation-artifacts/66-33-durcissement-operationnel-appel-provider-openai.md`
