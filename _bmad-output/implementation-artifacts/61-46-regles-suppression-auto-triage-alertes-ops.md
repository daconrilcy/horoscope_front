# Story 61.46 : Règles de suppression réutilisables et auto-triage des alertes ops

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux définir des règles durables de suppression applicables aux futures alertes ops,
afin d'éviter que le même bruit revienne en boucle dans la file, de réduire les retries inutiles et de rendre le triage récurrent traçable et maintenable.

## Contexte

- **61.39** : alerting idempotent, table `canonical_entitlement_mutation_alert_events`
- **61.40** : retry unitaire, table `canonical_entitlement_mutation_alert_delivery_attempts`
- **61.41** : `GET /alerts` + `GET /alerts/summary` — visibilité ops de la file
- **61.42** : `POST /alerts/retry-batch` — retry en masse des alertes `failed`
- **61.43** : handling mutable par `alert_event_id` via `canonical_entitlement_mutation_alert_event_handlings`
- **61.44** : historisation append-only des transitions de handling
- **61.45** : triage batch du backlog existant
- **Gap** : 61.45 permet de nettoyer vite le bruit déjà présent, mais pas d'empêcher le même motif de revenir demain. Le handling actuel reste attaché à un `alert_event_id` unique et ne constitue pas une règle réutilisable sur les futures alertes.

**Décision architecturale :**
- Introduire une table dédiée de règles durables : `canonical_entitlement_mutation_alert_suppression_rules`
- Conserver le modèle actuel de handling par événement comme source de vérité du traitement manuel d'une alerte précise
- Ajouter un moteur central de matching de règles actives, utilisé pour :
  - calculer le handling effectif côté listing/summary
  - exclure les alertes matching des retries unitaires et batch
- **Pas d'auto-réécriture historique** : une règle ne modifie pas l'identité métier (`alert_event_id`, `dedupe_key`) des alertes déjà créées
- **Priorité du manuel sur la règle** : si une alerte a déjà un handling explicite 61.43/61.44, ce handling reste prioritaire sur toute règle réutilisable

**Principe produit 61.46 :**
- 61.45 = nettoyer le backlog courant
- 61.46 = ne plus re-nettoyer les mêmes cas connus

---

## Acceptance Criteria

### AC 1 — Table `canonical_entitlement_mutation_alert_suppression_rules`

1. Migration Alembic créée : `backend/migrations/versions/20260329_0063_add_alert_suppression_rules_table.py`
   - `revision = "20260329_0063"`
   - `down_revision = "20260329_0062"`
2. Nouvelle table `canonical_entitlement_mutation_alert_suppression_rules` avec colonnes :
   - `id` (int, PK, autoincrement)
   - `alert_kind` (String(32), NOT NULL) — critère principal obligatoire
   - `feature_code` (String(64), nullable)
   - `plan_code` (String(64), nullable)
   - `actor_type` (String(32), nullable)
   - `suppression_key` (String(64), nullable) — clé de suppression appliquée quand la règle matche
   - `ops_comment` (Text, nullable) — justification métier durable
   - `is_active` (Boolean, NOT NULL, default=True)
   - `created_by_user_id` (int, nullable)
   - `created_at` (DateTime(timezone=True), NOT NULL, default=`utcnow`)
   - `updated_by_user_id` (int, nullable)
   - `updated_at` (DateTime(timezone=True), NOT NULL, default=`utcnow`)
3. Index non unique sur `is_active`.
4. Index composite sur `(is_active, alert_kind)`.
5. Contrainte d'unicité sur la combinaison normalisée des critères de matching :
   - `alert_kind`
   - `feature_code`
   - `plan_code`
   - `actor_type`
6. Une règle inactive reste conservée en base ; aucune suppression physique requise dans cette story.

### AC 2 — Modèle SQLAlchemy

7. Fichier créé : `backend/app/infra/db/models/canonical_entitlement_mutation_alert_suppression_rule.py`
8. Classe `CanonicalEntitlementMutationAlertSuppressionRuleModel(Base)` avec `__tablename__ = "canonical_entitlement_mutation_alert_suppression_rules"`.
9. Pattern SQLAlchemy 2.x avec `Mapped[T]` et `mapped_column()`.
10. Le modèle est enregistré dans `backend/app/infra/db/models/__init__.py`.

### AC 3 — Service central de matching

11. Nouveau fichier créé : `backend/app/services/canonical_entitlement_alert_suppression_rule_service.py`
12. Le service expose au minimum :
    ```python
    @dataclass
    class MatchedAlertSuppressionRule:
        rule_id: int
        suppression_key: str | None
        ops_comment: str | None
        source: str  # "rule"

    class CanonicalEntitlementAlertSuppressionRuleService:
        @staticmethod
        def load_active_rules(
            db: Session,
            *,
            alert_kind: str | None = None,
        ) -> list[CanonicalEntitlementMutationAlertSuppressionRuleModel]: ...

        @staticmethod
        def match_event(
            event: CanonicalEntitlementMutationAlertEventModel,
            *,
            active_rules: list[CanonicalEntitlementMutationAlertSuppressionRuleModel],
        ) -> MatchedAlertSuppressionRule | None: ...

        @staticmethod
        def match_events(
            events: list[CanonicalEntitlementMutationAlertEventModel],
            *,
            active_rules: list[CanonicalEntitlementMutationAlertSuppressionRuleModel],
        ) -> dict[int, MatchedAlertSuppressionRule]: ...
    ```
13. Le matching utilise exclusivement les colonnes déjà présentes sur `CanonicalEntitlementMutationAlertEventModel` :
    - `alert_kind`
    - `feature_code_snapshot`
    - `plan_code_snapshot`
    - `actor_type_snapshot`
14. `alert_kind` est toujours requis pour matcher ; les autres critères sont optionnels et agissent comme des raffinements.
15. Stratégie de priorité :
    - la règle la plus spécifique gagne (`feature_code`, `plan_code`, `actor_type` non nuls = score de spécificité plus élevé)
    - en cas d'égalité parfaite, la plus petite `id` gagne
16. Le service est pur sur le matching : aucun `db.commit()`, aucune écriture dans `alert_events`, `handlings` ou `handling_events`.
17. Le service ne remplace pas un handling manuel existant :
    - `resolved` manuel reste prioritaire
    - `suppressed` manuel reste prioritaire
    - seule l'absence de handling manuel permet une suppression effective issue d'une règle

### AC 4 — Effet sur les endpoints alertes existants

18. `GET /v1/ops/entitlements/mutation-audits/alerts` continue d'exister, mais son handling devient un **handling effectif** :
    - manuel si `canonical_entitlement_mutation_alert_event_handlings` existe
    - sinon `suppressed` via règle si une règle active matche
    - sinon `pending_retry` si `delivery_status == "failed"`
19. `AlertHandlingState` est étendu avec :
    ```python
    source: Literal["manual", "rule", "virtual"]
    suppression_rule_id: int | None = None
    ```
20. Quand une règle matche, la réponse liste expose :
    - `handling.handling_status = "suppressed"`
    - `handling.source = "rule"`
    - `handling.suppression_rule_id = <id de la règle>`
    - `handling.suppression_key` et `handling.ops_comment` venant de la règle
21. `GET /alerts?handling_status=suppressed` inclut :
    - les alertes manuellement `suppressed`
    - les alertes effectivement `suppressed` par règle
22. `GET /alerts?handling_status=resolved` ne retourne que les alertes manuellement `resolved`.
23. `GET /alerts?handling_status=pending_retry` exclut toute alerte matching une règle active.
24. `GET /v1/ops/entitlements/mutation-audits/alerts/summary` calcule :
    - `suppressed_count` = suppressions manuelles + suppressions effectives par règle
    - `resolved_count` = résolutions manuelles uniquement
    - `retryable_count` = alertes `failed` sans handling manuel ni règle active

### AC 5 — Effet sur les retries

25. `CanonicalEntitlementAlertBatchRetryService._load_batch_candidates()` exclut aussi les alertes couvertes par une règle active.
26. `CanonicalEntitlementAlertRetryService.retry_failed_alerts()` refuse aussi le retry unitaire d'une alerte couverte par une règle active.
27. L'erreur métier du retry unitaire reste cohérente :
    - code HTTP `409`
    - code API stable (ex. `alert_event_not_retryable`)
    - message explicite indiquant qu'une suppression effective manuelle ou par règle bloque le retry
28. Le `dry_run` du retry batch reflète déjà l'exclusion des règles actives.

### AC 6 — API ops de gestion des règles

29. Nouveaux endpoints ajoutés dans `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` :
    - `GET /mutation-audits/alerts/suppression-rules`
    - `POST /mutation-audits/alerts/suppression-rules`
    - `PATCH /mutation-audits/alerts/suppression-rules/{rule_id}`
30. Rôle requis : `ops` ou `admin` via `_ensure_ops_role()`.
31. Rate limits dédiés via `_enforce_limits()` :
    - `"list_alert_suppression_rules"`
    - `"create_alert_suppression_rule"`
    - `"update_alert_suppression_rule"`
32. Schémas Pydantic à ajouter :
    ```python
    class AlertSuppressionRuleItem(BaseModel):
        id: int
        alert_kind: str
        feature_code: str | None = None
        plan_code: str | None = None
        actor_type: str | None = None
        suppression_key: str | None = None
        ops_comment: str | None = None
        is_active: bool
        created_by_user_id: int | None = None
        created_at: datetime
        updated_by_user_id: int | None = None
        updated_at: datetime

    class CreateAlertSuppressionRuleRequestBody(BaseModel):
        alert_kind: str
        feature_code: str | None = None
        plan_code: str | None = None
        actor_type: str | None = None
        suppression_key: str | None = None
        ops_comment: str | None = None
        is_active: bool = True

    class UpdateAlertSuppressionRuleRequestBody(BaseModel):
        is_active: bool | None = None
        ops_comment: str | None = None
        suppression_key: str | None = None
    ```
33. `GET /alerts/suppression-rules` supporte au minimum les filtres query :
    - `is_active`
    - `alert_kind`
    - pagination `page` / `page_size`
34. `POST /alerts/suppression-rules` :
    - crée la règle si elle n'existe pas
    - est idempotent sur le corps normalisé complet
    - retourne `201` si création réelle
    - retourne `200` avec la règle existante si le même corps existe déjà
35. Si une règle active existe avec la même combinaison de critères mais un `suppression_key` ou `ops_comment` différent, l'API retourne `409` `suppression_rule_conflict`.
36. `PATCH /alerts/suppression-rules/{rule_id}` permet au minimum :
    - d'activer/désactiver la règle
    - de mettre à jour `ops_comment`
    - de mettre à jour `suppression_key`
37. `PATCH` ne supprime jamais la ligne ; désactiver passe par `is_active = false`.
38. `PATCH` met à jour `updated_by_user_id` et `updated_at`.
39. `GET`, `POST`, `PATCH` retournent le format API standard `{data, meta}`.

### AC 7 — Ordre des routes dans le router

40. Les routes statiques `/alerts/suppression-rules...` sont déclarées avant les routes paramétriques `/alerts/{alert_event_id}/...`.
41. L'ordre cible minimal devient :
    1. `GET /mutation-audits/alerts/summary`
    2. `GET /mutation-audits/alerts`
    3. `GET /mutation-audits/alerts/suppression-rules`
    4. `POST /mutation-audits/alerts/suppression-rules`
    5. `PATCH /mutation-audits/alerts/suppression-rules/{rule_id}`
    6. `POST /mutation-audits/alerts/retry-batch`
    7. `POST /mutation-audits/alerts/handle-batch`
    8. `POST /mutation-audits/alerts/{alert_event_id}/handle`
    9. `GET /mutation-audits/alerts/{alert_event_id}/handling-history`
    10. `GET /mutation-audits/alerts/{alert_event_id}/attempts`
    11. `POST /mutation-audits/alerts/{alert_event_id}/retry`

### AC 8 — Tests unitaires

42. Fichier créé : `backend/app/tests/unit/test_canonical_entitlement_alert_suppression_rule_service.py`
43. Tests à implémenter :
    - `test_match_event_returns_none_when_no_rule_matches`
    - `test_match_event_matches_on_alert_kind_only`
    - `test_match_event_prefers_more_specific_rule`
    - `test_match_event_tie_breaks_on_lowest_rule_id`
    - `test_match_events_returns_mapping_by_alert_event_id`
    - `test_manual_handling_still_has_priority_over_rule`
    - `test_load_active_rules_excludes_inactive_rules`
44. Fichier créé : `backend/app/tests/unit/test_canonical_entitlement_alert_query_service.py`
45. Nouveaux tests de non-régression à ajouter :
    - `test_list_alert_events_includes_rule_suppressed_handling`
    - `test_summary_counts_rule_suppressed_alerts`
    - `test_pending_retry_excludes_rule_suppressed_alerts`
46. Fichier créé ou enrichi : `backend/app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py`
47. Nouveaux tests :
    - `test_batch_retry_excludes_rule_suppressed_alerts`
    - `test_batch_retry_dry_run_excludes_rule_suppressed_alerts`
48. Fichier créé ou enrichi : `backend/app/tests/unit/test_canonical_entitlement_alert_retry_service.py`
49. Nouveau test :
    - `test_retry_failed_alerts_raises_not_retryable_when_rule_matches`

### AC 9 — Tests d'intégration

50. Fichier créé : `backend/app/tests/integration/test_ops_alert_suppression_rules_api.py`
51. Tests API rules :
    - `test_list_suppression_rules_returns_empty_state`
    - `test_create_suppression_rule_returns_201`
    - `test_create_suppression_rule_is_idempotent_on_same_body`
    - `test_create_suppression_rule_returns_409_on_conflicting_same_criteria`
    - `test_patch_suppression_rule_can_deactivate_rule`
    - `test_patch_suppression_rule_updates_comment_and_key`
    - `test_rules_api_requires_ops_role`
    - `test_rules_api_requires_authentication`
    - `test_rules_api_returns_429_when_rate_limited`
52. Fichier créé : `backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py`
53. Tests d'effet métier :
    - `test_list_alerts_marks_matching_future_alert_as_rule_suppressed`
    - `test_list_alerts_manual_resolved_wins_over_rule`
    - `test_summary_includes_rule_suppressed_count`
    - `test_retry_batch_excludes_matching_rule_suppressed_alert`
    - `test_retry_unitary_returns_409_when_rule_matches`
    - `test_handling_status_filter_suppressed_includes_rule_matches`
    - `test_handling_status_filter_pending_retry_excludes_rule_matches`
    - `test_disabling_rule_restores_retryability_and_visibility`

### AC 10 — Non-régression et limites explicites

54. Aucune modification des tables existantes `canonical_entitlement_mutation_alert_events`, `..._alert_event_handlings`, `..._alert_event_handling_events`, `..._alert_delivery_attempts`.
55. Aucune réécriture automatique des alertes historiques n'est effectuée dans cette story.
56. L'identité métier des alertes (`alert_event_id`, `dedupe_key`) reste inchangée.
57. Les endpoints 61.43, 61.44 et 61.45 conservent leur contrat HTTP ; seules des métadonnées de handling effectif peuvent être enrichies côté listing.
58. `resolved` reste un concept manuel lié à une alerte précise ; aucune règle durable de type `resolved` n'est introduite dans 61.46.
59. Les tests 61.39–61.45 restent verts.

### AC 11 — Documentation

60. `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Story 61.46 — Règles de suppression réutilisables"** :
    - nouvelle table
    - moteur de matching
    - endpoints rules
    - priorité manuel > règle
    - effet sur listing / summary / retry
61. `backend/README.md` est mis à jour avec mention des endpoints :
    - `GET /v1/ops/entitlements/mutation-audits/alerts/suppression-rules`
    - `POST /v1/ops/entitlements/mutation-audits/alerts/suppression-rules`
    - `PATCH /v1/ops/entitlements/mutation-audits/alerts/suppression-rules/{rule_id}`

---

## Tasks / Subtasks

- [x] AC 1+2 — Migration et modèle de règles durables
  - [x] Créer `backend/migrations/versions/20260329_0063_add_alert_suppression_rules_table.py`
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_alert_suppression_rule.py`
  - [x] Enregistrer le modèle dans `backend/app/infra/db/models/__init__.py`

- [x] AC 3 — Service central de matching
  - [x] Créer `backend/app/services/canonical_entitlement_alert_suppression_rule_service.py`
  - [x] Implémenter `load_active_rules()`
  - [x] Implémenter `match_event()` et `match_events()`
  - [x] Verrouiller priorité de spécificité et tie-break sur `id`

- [x] AC 4+5 — Brancher le handling effectif et les exclusions retry
  - [x] Étendre `AlertHandlingState` avec `source` et `suppression_rule_id`
  - [x] Mettre à jour `_compute_alert_handling_state()` ou son équivalent pour intégrer les règles
  - [x] Mettre à jour `CanonicalEntitlementAlertQueryService` pour compter/filtrer les suppressions effectives
  - [x] Mettre à jour `CanonicalEntitlementAlertBatchRetryService`
  - [x] Mettre à jour `CanonicalEntitlementAlertRetryService`

- [x] AC 6+7 — API ops de gestion des règles
  - [x] Ajouter les schémas Pydantic rules dans `ops_entitlement_mutation_audits.py`
  - [x] Ajouter `GET /alerts/suppression-rules`
  - [x] Ajouter `POST /alerts/suppression-rules`
  - [x] Ajouter `PATCH /alerts/suppression-rules/{rule_id}`
  - [x] Respecter l'ordre des routes avant `/{alert_event_id}/...`

- [x] AC 8+9 — Tests unitaires et d'intégration
  - [x] Ajouter la suite unitaire du service de matching
  - [x] Ajouter les non-régressions query/retry
  - [x] Ajouter la suite d'intégration des endpoints rules
  - [x] Ajouter la suite d'intégration des effets métier

- [x] AC 11 — Documentation
  - [x] Mettre à jour `backend/docs/entitlements-canonical-platform.md`
  - [x] Mettre à jour `backend/README.md`

---

## Dev Notes

### Pattern métier à respecter

- **Handling manuel** et **règle durable** sont deux concepts distincts :
  - `canonical_entitlement_mutation_alert_event_handlings` = état courant d'une alerte précise
  - `canonical_entitlement_mutation_alert_suppression_rules` = politique réutilisable pour les alertes futures ou non encore retraitées
- Ne pas détourner la table de handlings pour stocker des règles globales.
- Ne pas créer d'événements append-only 61.44 pour chaque match de règle dans cette story.

### Modèle de priorité

Ordre d'évaluation à conserver partout :
1. handling manuel `resolved`
2. handling manuel `suppressed`
3. règle active matching → handling effectif `suppressed`
4. `delivery_status == "failed"` sans match → `pending_retry`
5. sinon `None`

Cette logique doit être centralisée pour éviter trois variantes concurrentes entre listing, summary et retry.

### Contrainte importante sur `suppression_key`

Dans 61.46, `suppression_key` est **la clé appliquée par la règle** quand elle matche.
Ce n'est pas un critère de matching provenant de `CanonicalEntitlementMutationAlertEventModel`, qui ne porte pas ce champ aujourd'hui.

### SQL vs matching pur

Le service de matching doit rester la source de vérité métier.
Si des optimisations SQL sont nécessaires dans `CanonicalEntitlementAlertQueryService` ou `CanonicalEntitlementAlertBatchRetryService`, elles doivent répliquer exactement les mêmes critères et priorités.

### Fichiers concernés

```text
# NOUVEAUX
backend/app/infra/db/models/canonical_entitlement_mutation_alert_suppression_rule.py
backend/app/services/canonical_entitlement_alert_suppression_rule_service.py
backend/migrations/versions/20260329_0063_add_alert_suppression_rules_table.py
backend/app/tests/unit/test_canonical_entitlement_alert_suppression_rule_service.py
backend/app/tests/integration/test_ops_alert_suppression_rules_api.py
backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py

# MODIFIÉS
backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
backend/app/services/canonical_entitlement_alert_query_service.py
backend/app/services/canonical_entitlement_alert_batch_retry_service.py
backend/app/services/canonical_entitlement_alert_retry_service.py
backend/app/infra/db/models/__init__.py
backend/docs/entitlements-canonical-platform.md
backend/README.md
```

### Références de patterns existants

- `backend/app/services/canonical_entitlement_alert_batch_handling_service.py`
  - pattern batch + dry_run + no-op
- `backend/app/services/canonical_entitlement_alert_query_service.py`
  - pattern summary/list/filtering des alertes
- `backend/app/services/canonical_entitlement_alert_handling_service.py`
  - priorité du handling manuel par `alert_event_id`
- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
  - schémas Pydantic, `_ensure_ops_role()`, `_enforce_limits()`, ordre des routes
- `_bmad-output/implementation-artifacts/61-43-triage-ops-alertes-delivery-suppression-bruit.md`
- `_bmad-output/implementation-artifacts/61-44-historisation-append-only-transitions-handling-alertes-ops.md`
- `_bmad-output/implementation-artifacts/61-45-triage-batch-pilote-alertes-ops.md`

### Structure Notes

- Respecter les conventions API `/v1` et enveloppes `{data, meta}` définies dans l'architecture.
- Conserver la séparation `api -> services -> infra`.
- Pas de logique métier importante dans le router au-delà du wiring, auth, rate limit, commit et mapping réponse.

### References

- [Source: _bmad-output/implementation-artifacts/61-43-triage-ops-alertes-delivery-suppression-bruit.md]
- [Source: _bmad-output/implementation-artifacts/61-44-historisation-append-only-transitions-handling-alertes-ops.md]
- [Source: _bmad-output/implementation-artifacts/61-45-triage-batch-pilote-alertes-ops.md]
- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py]
- [Source: backend/app/services/canonical_entitlement_alert_query_service.py]
- [Source: backend/app/services/canonical_entitlement_alert_batch_retry_service.py]
- [Source: backend/app/services/canonical_entitlement_alert_handling_service.py]
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py]
- [Source: _bmad-output/planning-artifacts/architecture.md]
- [Source: _bmad-output/planning-artifacts/prd.md]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

### Completion Notes List

- Implémentation revue et durcie après code review ciblée.
- Contrat API des suppression rules réaligné sur la story: routes prévues uniquement, pagination du listing, messages métier retry explicites.
- Unicité normalisée fiabilisée pour les critères nullable via index unique `coalesce(...)` et normalisation des champs optionnels.
- Couverture de tests complétée sur listing, summary, retry unitaires/batch et effets métier des règles actives/inactives.

### File List

- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/infra/db/models/canonical_entitlement_mutation_alert_suppression_rule.py`
- `backend/app/services/canonical_entitlement_alert_batch_retry_service.py`
- `backend/app/services/canonical_entitlement_alert_query_service.py`
- `backend/app/services/canonical_entitlement_alert_suppression_rule_service.py`
- `backend/app/tests/integration/test_ops_alert_suppression_rules_api.py`
- `backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_query_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_retry_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_suppression_rule_service.py`
- `backend/docs/entitlements-canonical-platform.md`
- `backend/README.md`
- `backend/migrations/versions/20260329_0063_add_alert_suppression_rules_table.py`
- `_bmad-output/implementation-artifacts/61-46-regles-suppression-auto-triage-alertes-ops.md`
