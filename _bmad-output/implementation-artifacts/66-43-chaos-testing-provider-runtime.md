# Story 66.43: Chaos testing du ProviderRuntimeManager et preuve de résilience opérationnelle

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform SRE / Ops Architect,
I want soumettre le `ProviderRuntimeManager` à des scénarios de panne réalistes et contrôlés,
so that la robustesse du runtime provider ne soit plus seulement supposée par le design et les tests unitaires, mais prouvée par des invariants de résilience en conditions dégradées.

## Contexte

Le runtime provider a déjà été structuré par les stories précédentes :

- provider nominal verrouillé sur `openai` ;
- retries bornés ;
- timeouts gouvernés ;
- circuit breaker ;
- taxonomie d’erreurs enrichie ;
- discriminants d’observabilité comme `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`.

Cette base est solide sur le plan architectural, mais elle ne constitue pas encore une **preuve opérationnelle continue**.

Le risque restant est le suivant :

- la résilience est surtout démontrée par le design et quelques tests ciblés ;
- les comportements en panne réelle ou simulée peuvent diverger des hypothèses ;
- un mauvais retry peut masquer une erreur de configuration ;
- un circuit breaker peut devenir incohérent sous panne partielle ;
- un mode dégradé peut, par inadvertance, rouvrir un fallback non nominal.

66.43 doit donc transformer les mécanismes de résilience en **invariants prouvés par campagne de chaos déterministe**, corrélée à l’observabilité et aux snapshots actifs quand cela a du sens.

## Portée exacte

Cette story couvre cinq axes et rien de plus :

1. **matrice de chaos déterministe** sur les principales classes de panne provider ;
2. **preuve d’idempotence logique des retries** ;
3. **preuve de classification correcte** des erreurs de configuration vs erreurs provider ;
4. **preuve de fermeture du nominal sous panne** ;
5. **rapport d’invariants exploitable** pour ops / maintenance.

Elle ne doit pas :

- dépendre d’un provider réel externe pour sa réussite ;
- être confondue avec un test de charge global ;
- ajouter une nouvelle architecture provider ;
- autoriser un fallback nominal interdit au nom de la résilience.

## Diagnostic précis à traiter

Les cas prioritaires à éprouver sont :

1. `rate_limit` ;
2. `timeout` ;
3. `5xx` ;
4. `breaker open` ;
5. `retry budget exhausted` ;
6. panne partielle suivie d’un rétablissement ;
7. erreur de configuration qui ne doit jamais être reclassée en incident provider ;
8. conservation des discriminants d’observabilité et de corrélation snapshot ;
9. absence absolue de réouverture d’un fallback interdit sur les familles nominales.

La priorité d’implémentation est :

- d’abord garantir la rejouabilité déterministe des scénarios ;
- ensuite vérifier classification, breaker et retries ;
- enfin produire un rapport exploitable par les équipes ops.

## Cible d'architecture

Conserver l’architecture provider actuelle :

1. **ProviderRuntimeManager** = orchestration des appels et des politiques ;
2. **client provider** = adaptation protocolaire ;
3. **circuit breaker** = gestion d’état de résilience ;
4. **observabilité** = preuve d’exécution et de classification.

La cible 66.43 est d’ajouter une couche de **preuve déterministe** :

- doubles/stubs pilotables ;
- scénarios de panne rejouables ;
- assertions sur les invariants de résilience ;
- rapport structuré de campagne.

Le résultat attendu n’est pas un framework de chaos générique, mais une campagne bornée, stable et intégrable aux vérifications qualité du runtime provider.

## Acceptance Criteria

1. **AC1 — Matrice de chaos minimale couverte** : la campagne couvre au minimum `rate_limit`, `timeout`, `5xx`, `breaker open` et `retry budget exhausted`.
2. **AC2 — Panne partielle puis rétablissement** : un scénario démontre qu’après une phase d’échec contrôlée puis un retour nominal, l’état du circuit breaker, les retries et les classifications restent cohérents.
3. **AC3 — Erreur de configuration non reclassée** : un scénario d’erreur de configuration prouve qu’elle n’est pas transformée en incident provider ou en panne réseau générique.
4. **AC4 — Retries logiquement idempotents** : les retries sont démontrés idempotents du point de vue logique et observabilité sur les scénarios couverts ; ils n’introduisent pas d’effets de bord ou de double comptage incohérents.
5. **AC5 — Fermeture stricte du nominal** : aucun scénario de panne ne rouvre un fallback interdit sur `chat`, `guidance`, `natal` ou `horoscope_daily`.
6. **AC6 — Corrélation snapshot / observabilité** : chaque scénario expose les discriminants d’observabilité attendus et, quand pertinent, la corrélation au snapshot actif (`active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id` ou équivalent disponible).
7. **AC7 — Rapport d’invariants de résilience** : une sortie structurée et lisible identifie pour chaque scénario le type de panne, l’invariant vérifié, le résultat, et les discriminants observés.
8. **AC8 — Déterminisme local et CI** : les scénarios de chaos sont rejouables localement et en CI sans dépendance à un provider réel ni au réseau externe.
9. **AC9 — Cohérence breaker / retries / classification** : la campagne valide explicitement l’état du breaker, le nombre de tentatives, la taxonomie d’erreur remontée et les métadonnées observables associées.
10. **AC10 — Pas de confusion charge vs chaos** : la campagne reste bornée à la résilience provider ; elle peut réutiliser des surfaces de qualification existantes mais ne les remplace pas.
11. **AC11 — Documentation d’exploitation réalignée** : la doc runtime ou un runbook explicitement référencé décrit les scénarios couverts, la lecture du rapport et les limites connues de la campagne.
12. **AC12 — Windows + PowerShell supportés** : les validations locales requises restent compatibles avec le workflow du dépôt.

## Tasks / Subtasks

- [ ] Task 1: Définir la matrice de chaos et ses invariants (AC1, AC2, AC3, AC9)
  - [ ] Lister les scénarios couverts et l’invariant attendu pour chacun.
  - [ ] Distinguer explicitement erreurs provider, erreurs de configuration et transitions breaker.
  - [ ] Formaliser la taxonomie de résultats attendus.

- [ ] Task 2: Mettre en place des doubles déterministes et rejouables (AC1, AC8)
  - [ ] Ajouter des stubs ou hooks pilotables pour simuler les classes de panne visées.
  - [ ] Garantir l’absence de dépendance à un provider réel.
  - [ ] Vérifier la stabilité locale/CI de la campagne.

- [ ] Task 3: Vérifier classification, retries et breaker (AC2, AC3, AC4, AC9)
  - [ ] Ajouter des assertions sur `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`.
  - [ ] Vérifier l’idempotence logique des retries.
  - [ ] Vérifier qu’une erreur de configuration reste correctement classifiée.

- [ ] Task 4: Verrouiller la fermeture du nominal sous panne (AC5, AC6)
  - [ ] Ajouter des assertions empêchant tout fallback interdit.
  - [ ] Vérifier la corrélation snapshot/observabilité quand applicable.
  - [ ] Vérifier que les familles nominales restent dans la voie canonique même en mode dégradé.

- [ ] Task 5: Produire un rapport de campagne exploitable (AC7, AC10, AC11)
  - [ ] Définir un format de sortie structuré lisible par les ops.
  - [ ] Documenter la lecture du rapport et le périmètre de preuve couvert.
  - [ ] Réutiliser les surfaces de qualification existantes quand cela simplifie l’exploitation.

- [ ] Task 6: Validation locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .`.
  - [ ] Dans `backend/`, exécuter `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblant provider runtime, qualification et observabilité LLM.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- 66.43 ne cherche pas une nouvelle couche de résilience ; elle cherche une preuve répétable de la résilience déjà conçue.
- Les scénarios doivent être déterministes et rejouables, sinon ils ne seront pas tenables en CI.
- Un retry “qui finit par marcher” ne suffit pas ; il faut vérifier sa classification, son idempotence logique et son observabilité.
- Le nominal supporté ne doit jamais se réouvrir vers des fallbacks historiques sous prétexte de panne provider.

### Ce que le dev ne doit pas faire

- Ne pas dépendre du réseau réel ou d’un provider distant pour les scénarios.
- Ne pas confondre campagne de chaos et campagne de charge.
- Ne pas masquer une erreur de configuration sous une étiquette provider.
- Ne pas tolérer des assertions floues ou uniquement textuelles sur les erreurs.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/providers/provider_runtime_manager.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/provider_runtime_manager.py)
- [backend/app/llm_orchestration/providers/responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/responses_client.py)
- [backend/app/llm_orchestration/providers/circuit_breaker.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/circuit_breaker.py)
- [backend/app/llm_orchestration/simulation_context.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/simulation_context.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- Les stories récentes ont déjà verrouillé le provider nominal, les retries, les timeouts et l’observabilité enrichie.
- Le runtime semble désormais gouverné ; le manque principal est la preuve continue hors cas unitaires simples.
- 66.43 doit donc être pensée comme une story de validation opérationnelle et non comme une refonte de `ProviderRuntimeManager`.

### Git Intelligence

Le chantier LLM récent montre une progression vers :

- davantage de déterminisme ;
- davantage de gouvernance ;
- davantage de corrélation observabilité / snapshot ;
- davantage de quality gates.

Signal utile :

- une campagne de chaos non déterministe ou mal corrélée serait en contradiction avec cette trajectoire ;
- la story doit donc privilégier un design testable, borné et stable.

### Testing Requirements

- Couvrir `rate_limit`, `timeout`, `5xx`, `breaker open`, `retry budget exhausted`.
- Couvrir un scénario panne partielle puis retour nominal.
- Couvrir une erreur de configuration non reclassée.
- Couvrir l’absence absolue de fallback interdit sur les familles nominales.
- Vérifier les discriminants `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`.
- Vérifier la corrélation snapshot/manifest lorsque disponible.

### Project Structure Notes

- Zone principale : `backend/app/llm_orchestration/providers/`
- Zones adjacentes : `backend/app/llm_orchestration/services/`, `backend/tests/`
- Les doubles déterministes doivent rester proches du runtime provider ou de ses tests, pas dans une boîte à outils générique sans lien métier.

### References

- [backend/app/llm_orchestration/providers/provider_runtime_manager.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/provider_runtime_manager.py)
- [backend/app/llm_orchestration/providers/responses_client.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/responses_client.py)
- [backend/app/llm_orchestration/providers/circuit_breaker.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/circuit_breaker.py)
- [backend/app/llm_orchestration/simulation_context.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/simulation_context.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
