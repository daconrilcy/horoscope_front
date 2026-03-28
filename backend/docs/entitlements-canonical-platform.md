# Architecture des Entitlements : Plateforme Canonique

Ce document définit la source de vérité pour les droits d'accès (entitlements) aux fonctionnalités B2C de la plateforme.

## Source de Vérité Canonique

Depuis la story 61.16, la source de vérité unique pour les fonctionnalités B2C migrées est le système **Feature Usage Counters** (`feature_usage_counters`).

Le système legacy basé sur les quotas journaliers (`user_daily_quota_usages`) est officiellement déprécié pour ces flux.

## État de Migration des Fonctionnalités

| Fonctionnalité | Story de Migration | État | Fallback Legacy |
|----------------|-------------------|------|-----------------|
| `astrologer_chat` | 61.11 | 100% Canonique | Supprimé (61.15/61.16) |
| `natal_chart_long` | 61.13 | 100% Canonique | Aucun (Natif) |
| `thematic_consultation` | 61.12 | 100% Canonique | Aucun (Natif) |

## Breaking Changes (Story 61.17)

- **Endpoint Supprimé** : `GET /v1/billing/quota` a été décommissionné. Il retourne désormais HTTP 404.
- **Module Supprimé** : `backend/app/services/quota_service.py` (`QuotaService`) a été supprimé. Tout nouveau code doit utiliser `QuotaUsageService` et le système canonique d'entitlements.
- **Refactor Frontend** : Les helpers frontend (`useBillingQuota`, `fetchQuotaStatus`) ont été renommés en `useChatEntitlementUsage`, `fetchChatEntitlementUsage` pour refléter leur usage réel de `GET /v1/entitlements/me`.

## Inventaire des Usages Résiduels (Legacy)

Bien que déprécié et ses services supprimés, certains artefacts subsistent :

### Backend
- **Audit et RGPD** : `privacy_service.py` inclut toujours `user_daily_quota_usages` dans l'export des données personnelles (obligation légale tant que les données existent).
- **Migration** : Le script `migrate_legacy_quota_to_canonical.py` reste archivé pour référence historique.

### Frontend
- (Aucun usage legacy actif identifié après 61.17)

## Trajectoire de Décommission

1. **Audit Final** : (Terminé en 61.17) ✓
2. **Nettoyage Code** : (Terminé en 61.17) ✓
3. **Migration RGPD** : Retirer la table de `privacy_service.py` une fois que les données sont archivées ou supprimées.
4. **Suppression Physique** : Migration Alembic `DROP TABLE user_daily_quota_usages`.

## Contraintes de Sécurité

**NE PAS DROP TABLE** `user_daily_quota_usages` sans avoir validé les étapes ci-dessus. La table sert de filet de sécurité pour les audits (obligation légale RGPD).

## Support B2B (Story 61.18, 61.25)

Depuis la story 61.18, le système d'entitlements canonique s'étend au segment B2B. En story 61.25, le stockage a été découplé pour utiliser une table native B2B.

### Séparation Canonique B2C / B2B

| Segment | Table | Index Primaire | Service |
|---------|-------|----------------|---------|
| **B2C** | `feature_usage_counters` | `user_id` | `QuotaUsageService` |
| **B2B** | `enterprise_feature_usage_counters` | `enterprise_account_id` | `EnterpriseQuotaUsageService` |

### Identifiant de Compteur B2B (Story 61.25)

Le compromis transitoire consistant à utiliser `admin_user_id` comme clé de quota a été supprimé. Les consommations B2B sont désormais indexées directement par `enterprise_account_id` dans la table native `enterprise_feature_usage_counters`.

- **Indépendance** : La consommation quota ne dépend plus de l'existence ou du changement d'un administrateur particulier.
- **Source de Vérité** : `EnterpriseQuotaUsageService` est l'unique service gérant le cycle de vie de ces compteurs.

### Décommissionnement B2B Legacy (Story 61.24)

- **Suppression Physique** : La table `enterprise_daily_usages` a été supprimée via une migration Alembic destructive (`9d73f7af0bf4`).
- **Services Migrés** : `B2BBillingService`, `B2BReconciliationService`, `B2BApiEntitlementGate` et `B2BAuditService` utilisent désormais la table native B2B.

### Outils ops B2B — Alignement post-61.26

Depuis la story 61.26, l'écosystème ops B2B est entièrement aligné sur la table native `enterprise_feature_usage_counters`.

- **Audit Ops** : `GET /v1/ops/b2b/entitlements/audit` lit exclusivement `enterprise_feature_usage_counters`. L'absence d'`admin_user_id` n'est plus un motif de blocage ou d'audit "settings_fallback".
- **Repair Ops** : Les blockers `"set_admin_user"` ont été supprimés. L'outil `POST /repair/set-admin-user` est désormais documenté comme un outil de gestion d'**ownership/authentification**, sans impact sur le quota.
- **admin_user_id** : Ce champ dans `enterprise_accounts` définit l'administrateur du compte (ownership) uniquement. Plus aucun chemin de décision quota/usage B2B n'en dépend.
- **Nettoyage Historique** : Les scripts `verify_b2b_usage_migration.py` et `archive_b2b_legacy_usage_counters.py` fournissent respectivement la vérification de migration et la purge contrôlée des compteurs legacy B2B dans `feature_usage_counters`.

### Invariants du Système (Post-61.27)

| Flux | Table Source | Identifiant Pivot | Service Autorisé |
|------|--------------|-------------------|------------------|
| **Usage B2C** | `feature_usage_counters` | `user_id` | `QuotaUsageService` |
| **Usage B2B** | `enterprise_feature_usage_counters` | `enterprise_account_id` | `EnterpriseQuotaUsageService` |
| **Audit B2B** | `enterprise_feature_usage_counters` | `enterprise_account_id` | `EnterpriseQuotaUsageService` |
| **Ownership B2B** | `enterprise_accounts` | `admin_user_id` | `AuthService` |

## Séparation stricte B2C/B2B — Règle structurelle post-61.27

Depuis la story 61.27, la séparation B2C/B2B entre `feature_usage_counters` et `enterprise_feature_usage_counters` est devenue une règle structurelle du code, impossible à violer par inadvertance.

### Registre de Scope Explicite

Un registre centralisé (`FEATURE_SCOPE_REGISTRY` dans `feature_scope_registry.py`) définit le scope de chaque **feature code soumis aux services de quota** (pas de toutes les features produit) :

- **Scope B2C** : `astrologer_chat`, `thematic_consultation`, `natal_chart_long`.
- **Scope B2B** : `b2b_api_access`.

### Garde-fous Runtime

- **Fail-Closed** : Tout `feature_code` passé à un service de quota qui n'est pas enregistré dans `FEATURE_SCOPE_REGISTRY` provoque une erreur immédiate (`UnknownFeatureCodeError`). Aucun compteur n'est lu ou écrit pour un code inconnu.
- **Validation de Scope** :
  - `QuotaUsageService` lève `InvalidQuotaScopeError` s'il est appelé pour une feature B2B.
  - `EnterpriseQuotaUsageService` lève `InvalidQuotaScopeError` s'il est appelé pour une feature B2C.
- **Zéro Interaction DB en cas d'erreur** : La validation a lieu en début de méthode, avant toute requête SQLAlchemy.

### Non-régression Structurelle

Des tests d'import (`test_scope_separation_imports.py`) vérifient statiquement par analyse d'AST que les services B2C n'importent jamais le service de quota B2B, et inversement.

### Métadonnées de Quota

Les réponses API B2B incluent désormais un objet `quota_info` dans le body JSON :

- `source: "canonical"` : Consommation via le moteur canonique (champs `limit`, `remaining`, `window_end` présents).
- `source: "canonical_unlimited"` : Accès illimité via le moteur canonique.

## Validation de cohérence du registre (Story 61.28)

Pour garantir la pérennité de la séparation B2C/B2B introduite en 61.27, un validateur central vérifie automatiquement la cohérence entre le code et le registre.

### But
Protection du design au moment du développement et en CI, complémentaire aux garde-fous runtime de 61.27. Il assure qu'aucun `feature_code` quota ne peut être ajouté dans une gate sans être correctement enregistré et routé.

### Commande de validation
```powershell
.\.venv\Scripts\Activate.ps1
python backend/scripts/check_feature_scope_registry.py
```

### Vérifications effectuées
Le validateur `FeatureRegistryConsistencyValidator` effectue 4 points de contrôle :
1. **Exhaustivité registre ↔ gates** : Tous les `FEATURE_CODE` déclarés dans les 4 gates quota (`ChatEntitlementGate`, `ThematicConsultationEntitlementGate`, `NatalChartLongEntitlementGate`, `B2BApiEntitlementGate`) doivent être présents dans `FEATURE_SCOPE_REGISTRY`.
2. **Scopes canoniques imposés** : Les features connues doivent avoir leur scope exact (`B2C` pour le chat, les consultations et le natal long ; `B2B` pour l'accès API).
3. **Cohérence seed B2C** : Les 3 features `is_metered=True` du seed canonique B2C doivent être présentes dans le registre avec le scope `B2C`.
4. **Validité du registre** : Toutes les entrées du registre doivent utiliser des valeurs valides de l'enum `FeatureScope`.

## Enforcement startup + CI (Story 61.29)

Depuis la story 61.29, la validation de cohérence du registre de scope n'est plus optionnelle. Elle est devenue un **enforcement systématique** au démarrage de l'application et une étape obligatoire de validation CI.

### Validation au démarrage (Startup)
L'application backend exécute automatiquement `FeatureRegistryConsistencyValidator.validate()` dans son cycle de vie `_app_lifespan`.

Le comportement en cas d'erreur dépend du mode de validation configuré via la variable d'environnement `FEATURE_SCOPE_VALIDATION_MODE`.

#### Modes de validation
| Mode | Variable d'env | Comportement | Usage recommandé |
|------|----------------|--------------|------------------|
| **strict** | `strict` | Succès → démarrage OK ; Échec → **crash immédiat** au boot. | Production, Staging, CI |
| **warn** | `warn` | Succès → démarrage OK ; Échec → log ERROR structuré, le démarrage continue. | Transition, Debug local |
| **off** | `off` | La validation n'est pas exécutée. Log WARNING émis. | Cas d'urgence uniquement |

*Valeur par défaut : `strict`*

### Commande CI obligatoire
Pour détecter les incohérences le plus tôt possible, la commande suivante doit être intégrée dans la pipeline de validation statique :

```powershell
.\.venv\Scripts\Activate.ps1
python backend/scripts/check_feature_scope_registry.py
```

Cette commande retourne un code de sortie `0` en cas de succès et `1` en cas d'incohérence détectée.
Elle est également exécutée par `scripts/quality-gate.ps1`.

### Séquence de protection complète
Le système de protection des entitlements repose désormais sur quatre couches complémentaires :

1. **Design-time / CI** (61.28/61.29) : La commande CLI bloque le merge si le registre est incohérent avec le code des gates.
2. **Boot-time** (61.29) : Le backend refuse de démarrer en mode `strict` si une incohérence est détectée au chargement des modules.
3. **DB-time / Startup** (61.30) : Le backend valide au démarrage la cohérence des données canoniques en DB avec le registre.
4. **Runtime** (61.27) : Les services de quota lèvent des exceptions si une feature inconnue ou hors-scope est appelée.

## Validation DB canonique (Story 61.30)

Pour combler la dernière faille (données DB incohérentes avec le code), un validateur contrôle la cohérence des tables `feature_catalog`, `plan_catalog` et `plan_feature_bindings` par rapport au registre de scope.

### But
Empêcher toute configuration incohérente en base (ex: feature B2B liée à un plan B2C) même si le code applicatif est correct. Cette validation s'exécute au démarrage de l'app et peut être déclenchée via CLI.

### Commande de validation
```powershell
.\.venv\Scripts\Activate.ps1
python backend/scripts/check_canonical_entitlement_db_consistency.py
```
Précondition : migrations appliquées et seed canonique minimal présent dans la base ciblée par `DATABASE_URL`.

### Intégration quality gate
Le script [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1) n'exécute ce contrôle que si `CANONICAL_DB_QUALITY_GATE_READY=1`.
Cette variable doit uniquement être positionnée dans une phase où la DB de validation a déjà été provisionnée, migrée et seedée avec le catalogue canonique minimal.

### Vérifications effectuées
Le validateur `CanonicalEntitlementDbConsistencyValidator` réalise les contrôles suivants :
1. **Registre ↔ DB (Présence)** : Toute feature du registre doit avoir une entrée active dans `feature_catalog`.
2. **DB ↔ Registre (Metered)** : Toute feature active `is_metered=True` impliquée dans un binding `QUOTA` doit être enregistrée dans le registre.
3. **DB ↔ Registre (Bindings)** : Toute feature utilisée dans un binding de plan doit être connue du registre.
4. **Cohérence Scope/Audience** :
   - Features scope `B2C` → Uniquement liées à des plans d'audience `B2C`.
   - Features scope `B2B` → Uniquement liées à des plans d'audience `B2B`.
5. **Intégrité des Quotas** :
   - Binding `access_mode = QUOTA` → Doit posséder au moins une règle de quota.
   - Binding `UNLIMITED` ou `DISABLED` → Ne doit posséder aucun quota parasite.
6. **Features Obligatoires** : Les features critiques (`astrologer_chat`, `thematic_consultation`, `natal_chart_long`, `b2b_api_access`) doivent être présentes, actives et `is_metered=True` en DB.

### Modes de validation (Startup)
Le comportement au démarrage est piloté par `CANONICAL_DB_VALIDATION_MODE` (défaut: `strict`) :
- **strict** : Crash immédiat au boot si une incohérence est trouvée.
- **warn** : Log ERROR structuré, mais l'app démarre.
- **off** : Validation désactivée (Log WARNING).

## Validation write-time canonique (Story 61.31)

Depuis la story 61.31, les protections canoniques ne sont plus limitées au démarrage et à la CI. Toute écriture de binding/quota canonique doit passer par `CanonicalEntitlementMutationService`.

### Point d'entrée unique

- `CanonicalEntitlementMutationService.upsert_plan_feature_configuration(...)` est l'unique point d'entrée public autorisé pour créer ou modifier un `PlanFeatureBindingModel` et ses `PlanFeatureQuotaModel`.
- Le service opère dans la transaction SQLAlchemy courante et n'exécute jamais de `commit`.
- Le helper `_replace_plan_feature_quotas(...)` reste interne au service.

### Invariants appliqués avant écriture

Avant toute mutation DB, le service agrège puis valide les règles suivantes :

1. `feature_code` connu du `FEATURE_SCOPE_REGISTRY`.
2. Feature présente et active dans `feature_catalog`.
3. Compatibilité `scope` feature ↔ `audience` du plan (`B2C` avec `B2C`, `B2B` avec `B2B`).
4. `access_mode=QUOTA` : au moins un quota et chaque `quota_limit > 0`.
5. `access_mode=UNLIMITED` ou `DISABLED` : aucun quota.
6. `access_mode=QUOTA` : `feature_catalog.is_metered=True`.
7. Cohérence stricte `is_enabled` ↔ `access_mode`.

Si une violation est détectée, le service lève `CanonicalMutationValidationError` et aucune écriture partielle n'est persistée.

### Consommateurs migrés

Les écritures canoniques des chemins suivants ont été centralisées vers ce service :

- `backend/scripts/seed_product_entitlements.py`
- `backend/scripts/backfill_plan_catalog_from_legacy.py`
- `backend/app/services/b2b_entitlement_repair_service.py`

Le mode `dry_run` du repair B2B exécute la validation canonique dans un savepoint annulé afin de garantir le même verdict métier qu'en exécution réelle, sans persistance effective.

## Traçabilité write-time des mutations canoniques (Story 61.32)

Depuis la story 61.32, toute mutation effective effectuée via `CanonicalEntitlementMutationService` laisse une trace d'audit structurée et transactionnelle dans la table `canonical_entitlement_mutation_audits`.

### Fonctionnement de l'audit trail

1. **Transactionnel** : L'écriture de l'audit est faite dans la même transaction SQLAlchemy que la mutation du binding/quota. Si la transaction rollback (ex: erreur ultérieure ou dry-run via savepoint), l'audit rollback aussi.
2. **Snapshot Before/After** : Chaque ligne d'audit contient un snapshot JSON complet (`before_payload` et `after_payload`) du binding et de ses quotas.
3. **Règle No-Op** : Si un appel à `upsert_plan_feature_configuration` est idempotent (aucun changement réel détecté après normalisation des snapshots), **aucune ligne d'audit n'est créée**. Cela évite le bruit inutile en base.
4. **Pas d'audit sur échec** : Si la validation canonique (Story 61.31) échoue, aucune ligne d'audit n'est générée.

### Contexte de mutation obligatoire

Chaque appelant doit fournir un `CanonicalMutationContext` explicite précisant l'origine du changement :

- **actor_type** : `"script" | "service" | "ops" | "system"`.
- **actor_identifier** : Nom du script ou du service (ex: `seed_product_entitlements.py`, `b2b_entitlement_repair_service`).
- **request_id** : Optionnel, pour corréler avec les logs applicatifs.

### Normalisation des snapshots

Pour garantir des diffs stables et une détection no-op fiable, les snapshots sont normalisés avant comparaison :
- Les enums sont sérialisés par leur `.value` (chaîne).
- Les quotas sont triés de manière déterministe par `(quota_key, period_unit, period_value, reset_mode)`.
- Un dictionnaire vide `{}` représente un binding absent.

### Audit des consommateurs migrés

L'audit trail est activé pour tous les consommateurs canoniques :
- **Seed initial** : `seed_product_entitlements.py`
- **Backfill legacy** : `backfill_plan_catalog_from_legacy.py`
- **Repair B2B** : `b2b_entitlement_repair_service.py` (inclut la classification manuelle des plans à zéro unité).

## Story 61.33 — Exposition ops de l'audit trail (endpoint de consultation)

Depuis la story 61.33, les mutations auditées dans `canonical_entitlement_mutation_audits` sont consultables via une API ops sécurisée, paginée et filtrable.

### Endpoints de consultation

- **Liste paginée** : `GET /v1/ops/entitlements/mutation-audits`
  - Retourne les audits triés par `occurred_at DESC, id DESC`.
  - Pagination via `page` et `page_size` (max 100).
  - Filtres optionnels : `plan_id`, `plan_code`, `feature_code`, `actor_type`, `actor_identifier`, `source_origin`, `request_id`, `date_from`, `date_to`.
  - **Payloads** : Par défaut, `before_payload` et `after_payload` sont **omis** pour alléger la réponse. Passer `include_payloads=true` pour les inclure.

- **Détail par ID** : `GET /v1/ops/entitlements/mutation-audits/{audit_id}`
  - Retourne l'audit complet incluant systématiquement `before_payload` et `after_payload`.
  - Retourne 404 si l'ID n'existe pas.

### Contrôle d'accès et sécurité

- **Rôles autorisés** : `ops`, `admin` uniquement.
- **Rate limiting** : Appliqué par utilisateur, rôle et globalement (clés `ops_entitlement_mutation_audits:*`).
- **Read-only** : Aucun de ces endpoints ne permet de modifier, rollback ou supprimer une ligne d'audit. Logic de consultation encapsulée dans `CanonicalEntitlementMutationAuditQueryService`.



