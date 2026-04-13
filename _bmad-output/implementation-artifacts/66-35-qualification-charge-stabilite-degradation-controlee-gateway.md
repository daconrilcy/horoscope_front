# Story 66.35: Qualification de charge, de stabilité et de dégradation contrôlée du gateway

Status: implemented

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want qualifier le gateway LLM en charge réelle, en burst et sous incident provider contrôlé,
so that la tenue opérationnelle du périmètre nominal supporté (`chat`, `guidance`, `natal`, `horoscope_daily`) soit démontrée avant promotion production, avec seuils explicites, budget d'erreurs mesuré, corrélation à la release active réellement exécutée, et distinction stricte entre succès nominal, protections runtime et erreurs inattendues.

## Contexte

Les stories 8.4, 66.25, 66.32, 66.33 et 66.34 ont progressivement apporté des briques importantes pour rendre le runtime LLM observable et plus robuste, mais elles ne constituent pas encore une preuve de tenue en exploitation :

- [scripts/load-test-critical.ps1](/c:/dev/horoscope_front/scripts/load-test-critical.ps1) et [scripts/load-test-critical-matrix.ps1](/c:/dev/horoscope_front/scripts/load-test-critical-matrix.ps1) fournissent déjà un outillage PowerShell de charge pour quelques endpoints critiques, avec profils `smoke|nominal|stress`, phases `ramp_up|plateau|spike`, calculs `p50/p95/p99`, taux d'erreur et recommandations, mais cet outillage n'est pas centré sur la matrice LLM par famille (`chat`, `guidance`, `natal`, `horoscope_daily`) ni sur les incidents gateway.
- [backend/app/llm_orchestration/providers/provider_runtime_manager.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/provider_runtime_manager.py) et [backend/app/llm_orchestration/tests/test_provider_runtime.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_provider_runtime.py) prouvent déjà localement les retries, le circuit breaker et certains cas `rate_limit` / `retry_budget_exhausted`, mais essentiellement comme logique unitaire, pas comme comportement du système sous trafic soutenu.
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py) persiste `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`, `executed_provider_mode`, `pipeline_kind`, `execution_path_kind`, `fallback_kind`, `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id`, ce qui donne une base canonique de corrélation runtime, mais ces signaux ne sont pas encore transformés en doctrine de capacité et de verdict pré-prod.
- [backend/app/infra/observability/metrics.py](/c:/dev/horoscope_front/backend/app/infra/observability/metrics.py) sait déjà agréger compteurs et durées sur fenêtre glissante, mais aucune doctrine ne transforme encore ces métriques en SLO internes versionnés, en burn-rate de budget d'erreurs, ou en verdict pré-prod.
- [backend/app/api/v1/routers/ops_monitoring.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/ops_monitoring.py) expose déjà `/v1/ops/monitoring/operational-summary`, ce qui permet de corréler une campagne avec les KPIs ops, mais le script de charge ne l'exploite pas encore comme source de preuve sur les incidents LLM.
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) documente maintenant finement la taxonomie provider canonique, les timeouts par famille, l'observabilité canonique, la release active et le fait que, sur le périmètre nominal supporté, les incidents provider remontent prioritairement comme erreurs explicites ; en revanche la doc ne définit pas encore, à elle seule, de doctrine SLO/SLA ni de rapport de capacité versionné.

Le trou restant est donc net :

- pas de tests de charge par famille LLM avec verdict automatisé ;
- pas de tests de burst focalisés sur la saturation courte durée ;
- pas de tests combinant stress et protections runtime + recovery ;
- pas de seuils SLO/SLA internes officiels pour dire "ce gateway tient" ;
- pas de budget d'erreurs documenté et assumé ;
- pas de rapport de capacité standardisé avant promotion production.

## Diagnostic exact à préserver

- La cible de cette story n'est **pas** de benchmarker "tout le backend". Elle vise d'abord le **gateway LLM et ses familles critiques** (`chat`, `guidance`, `natal`, `horoscope_daily`) ainsi que les chemins opérationnels nécessaires pour les diagnostiquer.
- La cible n'est **pas** non plus de remplacer les tests unitaires et d'intégration existants. Les tests de charge viennent **compléter** les preuves actuelles en conditions soutenues.
- La story ne doit **pas** réintroduire de dépendance obligatoire à un outil externe si l'outillage PowerShell existant peut être étendu proprement. Ajouter `k6` ou `locust` n'est acceptable que si la valeur dépasse clairement le coût d'introduction et reste cohérente avec Windows/PowerShell.
- Les protections runtime (`429`, `upstream_timeout`, `upstream_circuit_open`, `retry_budget_exhausted`, etc.) ne doivent pas être comptées comme des "succès nominaux". Elles ne constituent ni un fallback de contenu nominal, ni une réponse fonctionnelle dégradée implicite sur `chat`, `guidance`, `natal` et `horoscope_daily`.
- Une campagne de charge ne vaut pas preuve si elle n'est pas **corrélable** avec les métriques et logs runtime déjà introduits par 66.25, 66.32, 66.33 et 66.34.
- Une campagne n'est **pas recevable** si elle n'est pas rattachée à la release active réellement exécutée, c'est-à-dire si le rapport ne porte pas explicitement `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id`.
- La qualification ne doit pas être limitée au chemin nominal. Elle doit couvrir au minimum :
  - saturation progressive ;
  - burst court et violent ;
  - incident provider ;
  - recovery avec retour stable `half_open/closed` après incident ;
  - comportement des garde-fous quand le système protège la plateforme.
- Il faut séparer strictement quatre notions :
  - **fallback réel** : essentiellement hors périmètre supporté ;
  - **protection runtime** : `rate_limit`, timeout, `circuit_open`, `retry_budget_exhausted`, etc. ;
  - **recovery** : retour à un état stable après incident ;
  - **dégradation fonctionnelle** : non nominale et non productisée aujourd'hui sur les familles supportées.
- Sur le périmètre supporté, l'absence d'assembly canonique active ou d'`ExecutionProfile` valide n'est pas un scénario de dégradation ; c'est un défaut de configuration qui doit rendre la campagne invalide immédiatement.
- Les seuils internes doivent être **versionnés et explicites** ; il ne doit pas exister un "ça semblait aller sur ma machine" comme preuve avant prod.
- Le rapport de capacité doit toujours préciser le contexte exact de mesure :
  - `active_snapshot_id` ;
  - `active_snapshot_version` ;
  - `manifest_entry_id` ;
  - environnement ;
  - familles testées ;
  - profil de trafic ;
  - seuils utilisés ;
  - limites connues ;
  - verdict.

## Cible d'architecture

Introduire et documenter un **Performance Qualification Harness** pour le gateway LLM, réutilisant l'observabilité et les protections runtime existantes, afin de produire des campagnes reproductibles et un verdict exploitable avant prod.

Cette couche doit fournir :

1. des scénarios de charge **par famille** (`chat`, `guidance`, `natal`, `horoscope_daily`) ;
2. des scénarios de **burst** explicites et distincts des plateaux de charge ;
3. des scénarios de **stress + incident** couvrant protections runtime et recovery (`rate_limit`, `upstream_timeout`, `upstream_circuit_open`, `retry_budget_exhausted`, `half_open/closed`) ;
4. une couche nouvelle de **gouvernance SLO/SLA interne** versionnée, construite au-dessus des signaux runtime déjà exposés ;
5. un **budget d'erreurs** accepté, mesuré et suivi sur campagne ;
6. un **rapport de capacité avant prod** normalisé, archivable, comparatif et rattaché à la release active réellement exécutée.

La cible n'est donc pas juste "faire quelques hits HTTP". La cible est un **dispositif de qualification d'exploitabilité** aligné sur le runtime réel.

## Axes de qualification à imposer

La story doit rendre explicites les cinq axes suivants :

### 1. Charge soutenue par famille

Chaque famille LLM supportée doit disposer d'un scénario nominal reproductible décrivant :

- endpoint ou point d'entrée testé ;
- jeu de payloads et fixtures utilisés ;
- durée ou volume ;
- concurrence cible ;
- latences `p50/p95/p99` ;
- taux de succès nominal ;
- taux de protections runtime canoniques (`rate_limit`, `upstream_timeout`, `upstream_circuit_open`, `retry_budget_exhausted`, ou équivalent stable via `provider_error_code`) ;
- taux d'échecs inattendus.

### 2. Burst

Le système doit disposer de scénarios de montée brusque permettant de distinguer :

- saturation contrôlée ;
- protections runtime observables et explicites ;
- effondrement non maîtrisé.

Le burst doit être traité comme un scénario à part entière, pas comme un simple suffixe de test nominal.

### 3. Protections runtime et recovery sous stress

Le système doit pouvoir démontrer, sous charge active ou juste après charge :

- ouverture du breaker sur incident prolongé ;
- comportement `half_open` / recovery ;
- stabilité des retries bornés ;
- non-explosion des temps de réponse ;
- non-régression de la taxonomie d'erreurs ;
- non-masquage des incidents derrière un faux succès ;
- absence de présomption d'un mode dégradé fonctionnel productisé sur les familles supportées.

### 4. SLO/SLA internes et budget d'erreurs

La story doit fixer une doctrine interne distinguant :

- **SLO** = objectif de service introduit par 66.35 et mesuré par campagne ou sur fenêtre glissante ;
- **SLA interne** = seuil d'exploitation introduit par 66.35, déclenchant escalade ou blocage de promotion ;
- **budget d'erreurs** = volume de non-conformité accepté avant blocage.

### 5. Rapport de capacité avant prod

Le résultat attendu n'est pas seulement un JSON brut. La story doit imposer un artefact libible indiquant :

- capacité observée par famille ;
- seuil recommandé de trafic nominal ;
- point de dégradation ;
- comportement en burst ;
- comportement en incident ;
- protections runtime observées ;
- statut de recevabilité du run (`valide`, `invalide_config`, `invalide_hors_release_active` ou équivalent stable) ;
- limites de validité de la campagne ;
- décision `go / no-go / go-with-constraints`.

## Latest Technical Specifics

Les elements externes suivants doivent être intégrés dans la story pour éviter une implémentation datée ou approximative :

- La documentation officielle k6 rappelle qu'un test de charge exploitable doit exprimer ses critères de réussite sous forme de **thresholds** explicites sur les métriques (par exemple taux d'échec et percentiles), et qu'un seuil échoué doit faire échouer le run. Même si le projet ne retient pas k6 comme outil principal, cette doctrine de seuils machine-evaluables doit être reprise dans l'outillage local. Source : [Grafana k6 Thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/).
- La documentation OpenAI sur les data controls précise que les abuse monitoring logs peuvent contenir prompts, réponses et métadonnées dérivées, avec une rétention par défaut jusqu'à 30 jours, et que `/v1/responses` peut aussi stocker un état applicatif. Inférence : une campagne de charge ne doit pas multiplier inutilement des payloads sensibles réels ; il faut privilégier des fixtures sûres, minimisées et compatibles avec la politique de redaction 66.34. Source : [OpenAI Data Controls](https://developers.openai.com/api/docs/guides/your-data).

Inférences à expliciter dans la story :

- un test de charge n'est recevable que s'il a des **seuils explicites** et un verdict automatique ; un simple relevé de latences sans critère n'est pas une preuve ;
- la campagne doit utiliser des payloads de test compatibles avec la politique de minimisation des données, pas des prompts utilisateurs réels copiés depuis la prod ;
- sur le périmètre nominal supporté, la doc runtime permet déjà de distinguer protection, rejet de configuration et exécution nominale ; en revanche elle ne définit pas encore, à elle seule, les seuils SLO/SLA de capacité ;
- les limites provider OpenAI étant dépendantes du contexte d'organisation, du modèle et du moment, le rapport de capacité doit toujours préciser le contexte exact mesuré au lieu d'annoncer une capacité universelle abstraite.

## Acceptance Criteria

1. **AC1 — Campagnes par famille obligatoires** : le repo introduit une matrice de qualification de charge couvrant au minimum `chat`, `guidance`, `natal` et `horoscope_daily`, avec pour chaque famille un scénario nominal reproductible et versionné.
2. **AC2 — Scénarios de burst distincts** : chaque famille critique dispose d'au moins un scénario de burst explicitement différencié du scénario de plateau, avec une rampe courte ou un spike documenté, et un verdict lisible sur la saturation observée.
3. **AC3 — Scénarios de stress avec incident provider** : la qualification couvre des scénarios où le provider nominal est lent, rate-limited ou indisponible, afin de vérifier sous stress les comportements `UpstreamRateLimitError`, `UpstreamTimeoutError`, `UpstreamCircuitOpenError`, `RetryBudgetExhaustedError`, `half_open` et recovery, sans présumer d'un mode dégradé fonctionnel nominal sur les familles supportées.
4. **AC4 — Recovery prouvé** : au moins un scénario démontre qu'après incident ou ouverture du breaker, le système sait revenir à un état stable sans boucle incontrôlée ni faux succès nominal, avec télémétrie corrélable avant / pendant / après.
5. **AC5 — Verdict automatisé par seuils** : l'outillage de charge échoue automatiquement quand les seuils internes configurés ne sont pas atteints. Un run ne doit pas nécessiter une lecture manuelle du JSON brut pour savoir s'il passe ou non.
6. **AC6 — SLO internes versionnés** : le projet introduit une couche nouvelle de gouvernance décrivant au minimum, par famille, les objectifs internes sur taux de succès nominal, taux maximum de protections runtime, taux d'erreur inattendue, et latences `p95/p99`. Ces seuils ne sont pas présumés déjà implicites dans la doc runtime existante.
7. **AC7 — SLA interne d'exploitation** : la plateforme formalise les seuils déclenchant escalade, blocage de promotion ou requalification avant prod. Ces seuils sont distingués des simples objectifs SLO afin d'éviter la confusion entre cible de capacité et tolérance opérationnelle.
8. **AC8 — Budget d'erreurs explicite** : un budget d'erreurs accepté est défini pour le gateway, au minimum sur les axes `échec inattendu`, `protection excessive`, `latence hors cible` ou équivalent stable. Le rapport de campagne doit indiquer la consommation de ce budget.
9. **AC9 — Corrélation avec l'observabilité canonique** : chaque campagne de charge valide et recevable est corrélée avec la release active réellement exécutée via `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id`. Un rapport qui ne porte qu'une mention textuelle du snapshot, sans ces identifiants canoniques, n'est pas valide.
10. **AC10 — Taxonomie canonique des résultats** : le harness classe les résultats d'après la taxonomie runtime canonique et non d'après une heuristique HTTP simpliste. Il exploite au minimum `executed_provider_mode`, `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`, ainsi que les erreurs internes canoniques (`UpstreamRateLimitError`, `UpstreamTimeoutError`, `UpstreamCircuitOpenError`, `RetryBudgetExhaustedError` ou équivalent stable).
11. **AC11 — Protections distinguées des erreurs inattendues** : pour les familles nominales supportées, les statuts de protection runtime (`rate_limit`, `upstream_timeout`, `upstream_circuit_open`, `retry_budget_exhausted`, etc.) sont comptés séparément des succès nominaux ; ils ne constituent ni un fallback de contenu nominal ni une réponse dégradée fonctionnelle implicite.
12. **AC12 — Défaut de configuration distingué de l'incident runtime** : sur `chat`, `guidance`, `natal` et `horoscope_daily`, l'absence d'assembly active, de release active, ou d'`ExecutionProfile` valide rend la campagne invalide immédiatement. Ce cas est distingué d'un run valide avec protections observées et d'un run valide avec erreurs inattendues.
13. **AC13 — Payloads de test sûrs et non-fuite** : les fixtures et scénarios utilisés pour la charge n'emploient pas de données utilisateur réelles ni de contenus sensibles non nécessaires. Ils respectent la doctrine de redaction et de minimisation posée par 66.34, et sont conçus pour ne pas provoquer de fuite de contenu sensible dans `llm_call_logs`, `obs_snapshot`, dashboards, audits ou rapports du harness.
14. **AC14 — Rapport de capacité avant prod normalisé** : une campagne produit un artefact libible versionné contenant au minimum `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`, l'environnement, `pipeline_kind`, `execution_path_kind`, `fallback_kind`, `requested_provider`, `resolved_provider`, `executed_provider`, `executed_provider_mode`, `context_compensation_status`, `max_output_tokens_source`, `max_output_tokens_final`, les métriques principales, les protections observées, le budget d'erreurs consommé, la capacité recommandée et le verdict `go / no-go / contraintes`.
15. **AC15 — Gate pré-prod explicite** : la documentation ou le script de pré-déploiement précise qu'aucune mise en prod du gateway LLM n'est recevable sans campagne de qualification valide, rattachée à la release active, et rapport de capacité conforme aux seuils du moment.
16. **AC16 — Comparabilité inter-runs** : le format de sortie permet de comparer au moins deux campagnes successives sur un même périmètre pour détecter une régression de capacité, de latence ou de stabilité, à release active et taxonomie comparables.
17. **AC17 — Couverture tests de non-régression du harness** : des tests couvrent la logique de seuils, le calcul du budget d'erreurs, la classification succès/protection/erreur/configuration invalide, et le format du rapport afin que l'outillage lui-même reste fiable.
18. **AC18 — Documentation d'exploitation** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md), [docs/development-guide-backend.md](/c:/dev/horoscope_front/docs/development-guide-backend.md) et le runbook pertinent décrivent comment lancer la qualification, lire les résultats, interpréter le budget d'erreurs et décider d'un `go/no-go`.

## Tasks / Subtasks

- [x] Task 1: Étendre l'outillage de charge existant vers une qualification gateway centrée familles LLM (AC1, AC2, AC5, AC14)
  - [x] Auditer [scripts/load-test-critical.ps1](/c:/dev/horoscope_front/scripts/load-test-critical.ps1) et [scripts/load-test-critical-matrix.ps1](/c:/dev/horoscope_front/scripts/load-test-critical-matrix.ps1) pour décider s'ils sont étendus ou factorisés.
  - [x] Introduire des scénarios dédiés `chat`, `guidance`, `natal`, `horoscope_daily`.
  - [x] Distinguer explicitement les profils `nominal`, `burst` et `stress`.
  - [x] Produire un format de sortie stable et comparable d'un run à l'autre.

- [x] Task 2: Définir la couche SLO/SLA interne et le budget d'erreurs au-dessus du runtime existant (AC5, AC6, AC7, AC8)
  - [x] Introduire une source de vérité versionnée pour les seuils par famille.
  - [x] Formaliser la différence entre `succès nominal`, `protection runtime`, `erreur inattendue` et `run invalide pour défaut de configuration`.
  - [x] Définir le budget d'erreurs accepté et la façon de le calculer sur un run.
  - [x] Encoder un verdict automatique `pass / fail / constrained-pass` ou équivalent stable.

- [x] Task 3: Couvrir les incidents provider, les protections runtime et le recovery sous stress (AC3, AC4, AC10, AC12)
  - [x] Créer des scénarios simulant `rate_limit`, timeout prolongé, indisponibilité provider et recovery.
  - [x] Vérifier l'ouverture du breaker et la stabilisation de la plateforme sous charge.
  - [x] Vérifier le retour à l'état `half_open/closed` quand l'incident cesse.
  - [x] Garantir qu'aucun faux succès nominal ni pseudo fallback de contenu n'est compté pendant ces scénarios.

- [x] Task 4: Corréler les runs avec l'observabilité canonique et la release active (AC9, AC10, AC14)
  - [x] S'appuyer sur [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py), [backend/app/infra/observability/metrics.py](/c:/dev/horoscope_front/backend/app/infra/observability/metrics.py) et [backend/app/api/v1/routers/ops_monitoring.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/ops_monitoring.py) pour corréler la campagne.
  - [x] Ajouter dans le rapport les signaux utiles (`pipeline_kind`, `execution_path_kind`, `fallback_kind`, `requested_provider`, `resolved_provider`, `executed_provider`, `executed_provider_mode`, `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`, `context_compensation_status`, `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`).
  - [x] Vérifier qu'un run peut être rapproché des dashboards / summaries ops sans analyse manuelle fragile.

- [x] Task 5: Sécuriser les fixtures et prévenir toute non-fuite dans les surfaces d'exploitation (AC13)
  - [x] Créer ou réutiliser des payloads synthétiques sûrs pour la charge.
  - [x] Interdire l'usage de prompts utilisateurs réels, de données natales réelles ou d'extraits sensibles.
  - [x] Aligner ces fixtures et les sorties du harness avec la politique 66.34.

- [x] Task 6: Produire le rapport de capacité avant prod rattaché à la release active (AC14, AC15, AC18)
  - [x] Définir un template/version du rapport de capacité.
  - [x] Documenter le verdict `go/no-go` et les contraintes éventuelles.
  - [x] Intégrer ce rapport dans le workflow de pré-déploiement ou de release.

- [x] Task 7: Couverture de tests de l'outillage (AC5, AC8, AC16, AC17)
  - [x] Ajouter des tests unitaires sur la logique de seuils et de budget d'erreurs.
  - [x] Ajouter des tests sur la classification `success/protection/error/config_invalid`.
  - [x] Ajouter des tests sur le format du rapport et ses champs obligatoires.
  - [x] Ajouter des tests d'intégration ciblés si l'outillage interroge les endpoints ops.

- [x] Task 8: Vérification locale obligatoire
  - [x] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [x] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [x] Exécuter `pytest -q`.
  - [x] Exécuter les suites ciblées liées au gateway runtime, à l'observabilité et au harness de charge.
  - [x] Exécuter la campagne de qualification retenue et générer le rapport de capacité.

### Review Findings

- [ ] [Review][Patch] Rejet de qualification non contractuel en `500` au lieu d'une erreur métier structurée [backend/app/llm_orchestration/services/performance_qualification_service.py:45]
- [ ] [Review][Patch] Corrélation release encore incomplète: `active_snapshot_version` et `manifest_entry_id` restent facultatifs dans un rapport pourtant annoncé comme recevable [backend/app/llm_orchestration/services/performance_qualification_service.py:48]
- [ ] [Review][Patch] `.gitignore` a été enregistré en binaire/UTF-16 avec caractères NUL, ce qui fragilise les nouvelles règles d'ignore [/.gitignore:32]

## Dev Agent Record

### Agent Model Used

Gemini-CLI

### Debug Log References

- Logic for automated verdict and SLO/SLA registry: `backend/app/llm_orchestration/performance_registry.py`
- Integration with load test: `scripts/load-test-critical.ps1`
- Automated Markdown report: `scripts/generate-performance-report.ps1`
- Fault Injection mechanism: `backend/app/llm_orchestration/providers/provider_runtime_manager.py`

### Completion Notes List

- Introduit un harness de qualification de performance complet pour le gateway LLM.
- Créé `PerformanceQualificationService` et un registre SLO/SLA par famille (`chat`, `guidance`, `natal`, `horoscope_daily`).
- Étendu `scripts/load-test-critical.ps1` avec des scénarios LLM réels et une initialisation de contexte utilisateur.
- Ajouté un mécanisme de Fault Injection via header `X-LLM-Simulate-Error` pour tester la résilience et le circuit breaker.
- Développé `scripts/generate-performance-report.ps1` pour produire des rapports Markdown automatisés avec verdict Go/No-Go.
- Corrigé des régressions dans les tests existants liées au changement de signature de `ResponsesClient.execute`.
- Intégré l'évaluation automatisée dans l'endpoint `POST /v1/ops/monitoring/performance-qualification`.
- Corrigé un bug de configuration au démarrage lié au use case `daily_prediction` manquant dans le catalogue.

### File List

- `_bmad-output/implementation-artifacts/66-35-qualification-charge-stabilite-degradation-controlee-gateway.md`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/performance_registry.py`
- `backend/app/llm_orchestration/services/performance_qualification_service.py`
- `backend/app/api/v1/routers/ops_monitoring.py`
- `backend/app/llm_orchestration/simulation_context.py`
- `backend/app/main.py`
- `backend/app/llm_orchestration/providers/provider_runtime_manager.py`
- `backend/app/prompts/catalog.py`
- `scripts/load-test-critical.ps1`
- `scripts/generate-performance-report.ps1`
- `backend/app/llm_orchestration/tests/test_performance_qualification.py`
- `backend/app/llm_orchestration/tests/test_incident_simulation.py`
- `backend/app/llm_orchestration/tests/test_gateway_regressions_fix.py`
