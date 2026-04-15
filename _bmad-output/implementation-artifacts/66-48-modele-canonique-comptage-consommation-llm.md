# Story 66.48: Modèle canonique de comptage de consommation LLM

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / finance / plateforme LLM,
I want disposer d'un modèle canonique de comptage tokens/coûts fondé sur la taxonomie runtime,
so that le pilotage des consommations ne dépende plus des anciens agrégats `use_case` et puisse être lu par utilisateur, abonnement, feature et période.

## Contexte

Le dépôt dispose déjà des briques nécessaires, mais elles restent séparées et répondent à des besoins différents :

- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py) stocke déjà `tokens_in`, `tokens_out`, `cost_usd_estimated`, `latency_ms`, `feature`, `subfeature`, `plan`, `requested_provider`, `resolved_provider`, `executed_provider`, `active_snapshot_version`, `manifest_entry_id`.
- [backend/app/services/llm_ops_monitoring_service.py](/c:/dev/horoscope_front/backend/app/services/llm_ops_monitoring_service.py) sait agréger `llm_call_logs` par dimensions canoniques d'exploitation (`feature`, `plan`, `persona`, `execution_path_kind`, `fallback_kind`, provider triplet), mais pas encore par `user_id`, ni sous une forme de pilotage coût/tokens historisée.
- [backend/app/services/llm_token_usage_service.py](/c:/dev/horoscope_front/backend/app/services/llm_token_usage_service.py) et [backend/app/infra/db/models/token_usage_log.py](/c:/dev/horoscope_front/backend/app/infra/db/models/token_usage_log.py) constituent le journal utilisateur facturable, utile pour les quotas et le billing, mais pas encore comme vérité canonique unique d'agrégation admin.
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) expose encore un dashboard agrégé par `use_case`, hérité de 65.14.
- [backend/app/api/v1/routers/billing.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/billing.py) et [61-67-refactorisation-credit-par-token.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/61-67-refactorisation-credit-par-token.md) montrent que le billing utilisateur est déjà tokenisé côté runtime.

Le besoin de cette story n'est donc pas d'inventer une nouvelle source de vérité, mais de **matérialiser un modèle canonique de comptage** qui :

- réutilise les logs/runtime déjà disponibles ;
- expose un axe nominal `user_id / subscription_plan / feature / subfeature / locale / executed_provider / active_snapshot_version` ;
- sépare explicitement l'usage canonique nominal des résidus legacy ;
- fournit les agrégats journaliers et mensuels qui serviront ensuite au dashboard de `66.49`.

Règles de contrat à figer dans cette story :

- `subscription_plan` doit représenter le **plan commercial effectif résolu au moment exact de l'appel**, figé historiquement dans le read model et non recalculé à partir du plan courant de l'utilisateur ;
- `estimated_cost` doit représenter le **coût estimé du provider réellement exécuté au moment réel du call**, tel qu'observé/persisté à l'exécution, et non un recalcul a posteriori selon un barème potentiellement différent ;
- les agrégats journaliers et mensuels utilisent une **timezone unique de référence = UTC**, sans exception locale par utilisateur ou par admin.

## Diagnostic exact à préserver

- Ne pas recréer une seconde taxonomie parallèle de consommation. La vérité nominale doit dériver de `feature`, `subfeature`, `plan`, `locale` et des discriminants runtime déjà normalisés dans `llm_call_logs`.
- Ne pas faire du journal `user_token_usage_logs` la seule source. Il est précieux pour le débit utilisateur, mais il ne remplace pas les signaux opérationnels présents dans `llm_call_logs` (latence, erreurs, snapshot, provider exécuté).
- Ne pas conserver `use_case` comme axe nominal de lecture coût/tokens. Il peut rester en compatibilité ou en diagnostic, mais pas comme regroupement métier principal.
- Ne pas fusionner silencieusement nominal canonique et trafic legacy. Un agrégat `legacy_residual` ou un statut explicite équivalent est nécessaire.
- Ne pas reconstruire les percentiles de latence ou les taux d'erreur dans le frontend. Ils doivent être calculés côté backend/read model.
- Les agrégats doivent rester safe-by-design : pas de contenu de prompt, pas de `raw_output`, pas de `structured_output` complet, pas de payload utilisateur brut.

## Acceptance Criteria

1. **AC1 — Dimensions minimales** : le modèle canonique de consommation expose au minimum `user_id`, `subscription_plan`, `feature`, `subfeature`, `locale`, `executed_provider`, `active_snapshot_version`.
2. **AC2 — Mesures minimales** : le modèle expose au minimum `input_tokens`, `output_tokens`, `total_tokens`, `estimated_cost`, `call_count`, `latency_p50`, `latency_p95`, `error_rate`.
3. **AC3 — Historisation journalière** : une agrégation journalière en bornes UTC est disponible sans devoir relire tous les logs bruts côté admin.
4. **AC4 — Historisation mensuelle** : une agrégation mensuelle en bornes UTC est disponible avec les mêmes dimensions canoniques.
5. **AC5 — Séparation nominal / legacy** : les appels relevant d'aliases ou d'activations legacy résiduelles sont identifiés explicitement et exclus des agrégats nominaux par défaut.
6. **AC6 — Normalisation canonique avant agrégation** : un appel legacy encore toléré est reclassé sur `feature/subfeature/plan` avant agrégation nominale, ou marqué `legacy_residual` si le mapping nominal n'est pas autorisé.
7. **AC7 — Source de vérité unique d'agrégation** : le read model de consommation réutilise les sources existantes (`llm_call_logs`, `user_token_usage_logs`, plan/runtime canonique) sans taxonomie concurrente.
8. **AC8 — Cohérence avec billing** : `subscription_plan` correspond au plan commercial/runtime effectivement résolu au moment du call et reste figé historiquement dans les agrégats.
9. **AC9 — Cohérence avec observabilité** : `executed_provider`, `active_snapshot_version`, `feature`, `subfeature`, `plan`, `locale` reprennent les champs canoniques déjà utilisés par 66.25 à 66.37.
10. **AC10 — Coût figé à l'exécution** : `estimated_cost` correspond au coût estimé observé au moment de l'appel pour le provider exécuté, sans recalcul rétroactif nominal.
11. **AC11 — Safe-by-design** : aucune nouvelle projection de consommation ne fuit de contenu sensible ou des identifiants non nécessaires au pilotage.

## Tasks / Subtasks

- [x] Task 1: Définir le contrat du modèle canonique de consommation (AC: 1, 2, 7, 9)
  - [x] Choisir le support technique: read model SQL, vue matérialisée, table agrégée journalière/mensuelle ou service d'agrégation gouverné, sans créer de double vérité.
  - [x] Définir explicitement les dimensions et mesures minimales.
  - [x] Définir la stratégie de calcul des percentiles et du taux d'erreur.

- [x] Task 2: Cartographier les sources existantes vers le modèle canonique (AC: 1, 2, 6, 7, 8, 9)
  - [x] Relire `LlmCallLogModel`, `UserTokenUsageLogModel`, les services billing et la taxonomie 66.x.
  - [x] Définir la priorité des champs pour `subscription_plan`, `locale`, `executed_provider`, `active_snapshot_version`.
  - [x] Verrouiller que `subscription_plan` et `estimated_cost` sont figés à l'instant du call et non recalculés a posteriori.
  - [x] Documenter les cas où une source est absente et la stratégie de fallback autorisée.

- [x] Task 3: Implémenter la séparation nominal / legacy résiduel (AC: 5, 6, 9)
  - [x] Introduire un indicateur stable du type `usage_scope`, `taxonomy_scope`, `is_legacy_residual` ou équivalent.
  - [x] Reclassifier les aliases legacy sur la feature canonique lorsque le mapping nominal est connu.
  - [x] Garder les résidus legacy visibles mais exclus des agrégats nominaux par défaut.

- [x] Task 4: Matérialiser les agrégats journaliers et mensuels (AC: 3, 4, 7)
  - [x] Définir les fenêtres et bornes temporelles en UTC, unique référence métier pour tous les agrégats.
  - [x] Produire un agrégat journalier et un agrégat mensuel avec les mêmes colonnes canoniques.
  - [x] Prévoir l'actualisation du read model sans scheduler opportuniste ambigu.

- [x] Task 5: Exposer un service backend réutilisable par les surfaces admin (AC: 1 à 9)
  - [x] Créer un service/query layer dédié pour requêter les agrégats par dimensions canoniques.
  - [x] Préparer l'API qui sera consommée par le dashboard 66.49.
  - [x] Prévoir une projection drill-down vers les `llm_call_logs` corrélés.

- [x] Task 6: Couverture tests et documentation (AC: 1 à 10)
  - [x] Ajouter des tests sur la normalisation canonique vs legacy résiduel.
  - [x] Ajouter des tests sur les agrégats journaliers et mensuels.
  - [x] Ajouter des tests de cohérence plan/runtime/provider/snapshot.
  - [x] Documenter la source de vérité et la séparation nominal / legacy.

## Dev Notes

### Ce que le dev doit retenir avant d'implémenter

- Le modèle à construire est un **read model de pilotage**, pas un remplacement des journaux existants.
- `llm_call_logs` contient déjà la plupart des discriminants runtime canoniques utiles au pilotage.
- `user_token_usage_logs` apporte le lien utilisateur/facturation, mais il doit être combiné au runtime LLM plutôt que traité isolément.
- Le périmètre nominal doit parler `feature/subfeature/plan`, pas `use_case`.
- Les agrégats de cette story doivent devenir la base de la story UI 66.49.
- `subscription_plan` n'est pas "le plan actuel de l'utilisateur" mais le plan effectif résolu au moment du call.
- `estimated_cost` n'est pas un coût recalculé après coup ; c'est la valeur observée à l'exécution pour le provider exécuté.
- La timezone de référence des agrégats est UTC et doit rester unique sur tout le périmètre.

### Ce que le dev ne doit pas faire

- Ne pas exposer `use_case` comme axe primaire de regroupement.
- Ne pas recalculer en frontend la logique d'agrégation, de percentile ou de séparation nominal/legacy.
- Ne pas introduire de taxonomie concurrente à celle de 66.25 / 66.37.
- Ne pas mélanger données facturables utilisateur et observabilité technique sans contrat clair.
- Ne pas faire dépendre la vérité historique de métriques en mémoire `instance_local`.

### Fichiers à inspecter en priorité

- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [backend/app/services/llm_ops_monitoring_service.py](/c:/dev/horoscope_front/backend/app/services/llm_ops_monitoring_service.py)
- [backend/app/services/llm_token_usage_service.py](/c:/dev/horoscope_front/backend/app/services/llm_token_usage_service.py)
- [backend/app/infra/db/models/token_usage_log.py](/c:/dev/horoscope_front/backend/app/infra/db/models/token_usage_log.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/api/v1/routers/billing.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/billing.py)
- [61-67-refactorisation-credit-par-token.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/61-67-refactorisation-credit-par-token.md)
- [65-14-supervision-ia-tableau-bord-metier.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-14-supervision-ia-tableau-bord-metier.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)

### Previous Story Intelligence

- **61.67** a déjà basculé le billing utilisateur en tokens. Cette story doit réutiliser cette base au lieu de recréer un journal parallèle.
- **65.14** a livré un dashboard admin par `use_case`. Cette story sert précisément à dépasser cette lecture.
- **66.25** a stabilisé les discriminants d'observabilité runtime.
- **66.37** a créé la surface ops par dimensions canoniques, utile comme base de service/agrégation.
- **66.45 à 66.47** ont réaligné l'admin LLM sur la vérité runtime canonique ; la consommation doit suivre la même logique.

### Testing Requirements

- Ajouter un test de normalisation d'un alias legacy vers `feature/subfeature/plan` canonique.
- Ajouter un test séparant un agrégat nominal d'un bucket `legacy_residual`.
- Ajouter un test sur les agrégats journaliers.
- Ajouter un test sur les agrégats mensuels.
- Ajouter un test de cohérence `subscription_plan` / `executed_provider` / `active_snapshot_version`.
- Ajouter un test garantissant que `subscription_plan` reste figé historiquement même si le plan courant utilisateur change après coup.
- Ajouter un test garantissant que `estimated_cost` n'est pas recalculé rétroactivement.
- Ajouter un test garantissant qu'aucun contenu sensible n'est exposé dans la projection de consommation.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`

### Project Structure Notes

- Travail principalement backend + documentation.
- La surface UI viendra en 66.49 ; ici il faut d'abord produire le read model et le service/query layer.
- Réutiliser les modèles existants avant d'introduire une nouvelle table.
- Si une table d'agrégats est introduite, la garder strictement dédiée au read model canonique de consommation.

### References

- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [backend/app/services/llm_ops_monitoring_service.py](/c:/dev/horoscope_front/backend/app/services/llm_ops_monitoring_service.py)
- [backend/app/services/llm_token_usage_service.py](/c:/dev/horoscope_front/backend/app/services/llm_token_usage_service.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/api/v1/routers/billing.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/billing.py)
- [61-67-refactorisation-credit-par-token.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/61-67-refactorisation-credit-par-token.md)
- [65-14-supervision-ia-tableau-bord-metier.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-14-supervision-ia-tableau-bord-metier.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

 - Implémentation du service `LlmCanonicalConsumptionService` avec normalisation taxonomy et agrégation UTC.
 - Ajout d'un endpoint admin `/v1/admin/llm/consumption/canonical` pour consommation du dashboard 66.49.
 - Ajout de tests unitaires et d'intégration couvrant nominal/legacy, agrégats day/month, invariants plan/coût/provider/snapshot.

### Completion Notes List

- Story créée pour établir la base canonique de comptage consommation LLM avant la surface admin de pilotage.
- Read model canonique livré sur base `llm_call_logs` + jointure `user_token_usage_logs`, sans source concurrente.
- Les agrégats exposent `user_id`, `subscription_plan`, `feature`, `subfeature`, `locale`, `executed_provider`, `active_snapshot_version` avec mesures tokens/coût/latence/erreur.
- La séparation nominal/legacy résiduel est explicite via `taxonomy_scope` et `is_legacy_residual`, avec exclusion par défaut des résidus sur le scope `nominal`.
- Les bornes temporelles journalières et mensuelles sont exclusivement en UTC.
- Validation locale exécutée: `ruff format .`, `ruff check .`, `pytest -q app/tests/unit/test_llm_canonical_consumption_service.py app/tests/integration/test_admin_llm_canonical_consumption_api.py`.

### File List

- `_bmad-output/implementation-artifacts/66-48-modele-canonique-comptage-consommation-llm.md`
- `backend/app/services/llm_canonical_consumption_service.py`
- `backend/app/api/v1/routers/admin_llm_consumption.py`
- `backend/app/main.py`
- `backend/app/tests/unit/test_llm_canonical_consumption_service.py`
- `backend/app/tests/integration/test_admin_llm_canonical_consumption_api.py`

### Change Log

- 2026-04-15: Implémentation du modèle canonique de comptage LLM (service + endpoint admin + tests) avec séparation nominal/legacy et agrégats UTC day/month.
