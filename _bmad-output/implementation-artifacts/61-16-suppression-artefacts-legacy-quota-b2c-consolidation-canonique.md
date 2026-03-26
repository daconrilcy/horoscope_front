# Story 61.16 : Suppression des artefacts legacy de quota B2C et consolidation canonique

Status: done

## Story

En tant que développeur de la plateforme,
je veux supprimer les artefacts legacy de quota B2C qui ne sont plus jamais exécutés à l'exécution,
de sorte que le codebase ne contienne plus de code mort lié à l'ancien système de quota et que `feature_usage_counters` soit officiellement documentée comme unique source de vérité pour les features B2C migrées.

## Contexte

61.15 a coupé le fallback runtime sur `astrologer_chat`. La méthode `_legacy_fallback` reste dans `entitlement_service.py` avec `"""DEPRECATED: suppression en 61.16"""` — elle n'est plus jamais appelée. Deux gates (`natal_chart_long`, `thematic_consultation`) contiennent des checks défensifs `if entitlement.reason == "legacy_fallback":` qui ne peuvent plus être déclenchés. Des tests unitaires documentent ce comportement devenu dead code.

Contrainte ferme : **ne pas DROP TABLE `user_daily_quota_usages`** en 61.16 — la table reste en place pour rollback potentiel et pour l'export RGPD (`privacy_service.py`). La story 61.16 est une story de **suppression des usages runtime + dépréciation officielle + audit final**.

## Acceptance Criteria

1. `EntitlementService._legacy_fallback` est supprimée de `entitlement_service.py` — la méthode n'existe plus dans la classe
2. Les checks défensifs `if entitlement.reason == "legacy_fallback":` dans `thematic_consultation_entitlement_gate.py` et `natal_chart_long_entitlement_gate.py` sont supprimés
3. Les tests `test_legacy_fallback_treated_as_no_binding` dans `test_thematic_consultation_entitlement_gate.py` et `test_natal_chart_long_entitlement_gate.py` sont supprimés
4. `quota_service.py` porte un commentaire de module LEGACY indiquant qu'il n'est plus utilisé dans les flows B2C feature-gated et qu'il est en attente de décommission
5. `UserDailyQuotaUsageModel` dans `billing.py` (models) porte un commentaire LEGACY indiquant que la table est read-only, source de données obsolète, non droppée en attente d'audit complet
6. L'endpoint `GET /v1/billing/quota` dans `billing.py` (router) porte un commentaire LEGACY, et `fetchQuotaStatus` dans `frontend/src/api/billing.ts` porte un commentaire LEGACY (dead code front non importé ailleurs)
7. Un fichier de documentation `backend/docs/entitlements-canonical-platform.md` est créé, documentant que `feature_usage_counters` est la source de vérité unique pour les features B2C migrées, avec un inventaire des usages résiduels de `QuotaService` et `user_daily_quota_usages`
8. Tous les tests existants passent : `ruff check .` propre, `pytest` sans régression sur les fichiers modifiés

## Tasks / Subtasks

- [x] **Supprimer `EntitlementService._legacy_fallback`** (AC: 1)
  - [x] Dans `backend/app/services/entitlement_service.py`, supprimer la méthode `_legacy_fallback` (lignes 211-259, environ 49 lignes)
  - [x] Vérifier qu'aucun autre endroit dans le codebase n'appelle `_legacy_fallback` (grep de sécurité)

- [x] **Supprimer les checks défensifs `legacy_fallback` dans les gates** (AC: 2)
  - [x] `backend/app/services/thematic_consultation_entitlement_gate.py` : supprimer le bloc `# Pas de chemin legacy — ...` + `if entitlement.reason == "legacy_fallback": raise ConsultationAccessDeniedError(...)` (lignes 45-52 environ)
  - [x] `backend/app/services/natal_chart_long_entitlement_gate.py` : supprimer le bloc identique (lignes 46-52 environ)
  - [x] S'assurer que la logique suivante (check `final_access`) reste intacte dans les deux gates

- [x] **Supprimer les tests legacy devenu dead code** (AC: 3)
  - [x] `backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py` : supprimer `test_legacy_fallback_treated_as_no_binding` (~lignes 96-110)
  - [x] `backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py` : supprimer `test_legacy_fallback_treated_as_no_binding` (~lignes 112-125)

- [x] **Dépréciation officielle de `quota_service.py`** (AC: 4)
  - [x] Ajouter en tête de `backend/app/services/quota_service.py` un bloc de commentaire LEGACY :

- [x] **Dépréciation officielle de `UserDailyQuotaUsageModel`** (AC: 5)
  - [x] Dans `backend/app/infra/db/models/billing.py`, ajouter avant la classe `UserDailyQuotaUsageModel` :

- [x] **Dépréciation de l'endpoint `/billing/quota` et de `fetchQuotaStatus`** (AC: 6)
  - [x] Dans `backend/app/api/v1/routers/billing.py`, ajouter commentaire avant le décorateur `@router.get("/quota", ...)` :
  - [x] Dans `frontend/src/api/billing.ts`, ajouter commentaire sur `fetchQuotaStatus` :

- [x] **Créer la documentation canonique** (AC: 7)
  - [x] Créer `backend/docs/entitlements-canonical-platform.md` avec :

- [x] **Non-régression** (AC: 8)
  - [x] `ruff check .` depuis `backend/` — aucune erreur
  - [x] `pytest backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_entitlement_service.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_entitlements_me.py` — tous verts (inclut `test_no_legacy_fallback_reason_in_response`)
  - [x] `pytest backend/app/tests/integration/test_natal_chart_long_entitlement.py` — tous verts

## Dev Notes

### Localisation précise des artefacts à supprimer

```
backend/app/services/entitlement_service.py        ← SUPPRIMER méthode _legacy_fallback (ll. 211-259)
backend/app/services/thematic_consultation_entitlement_gate.py  ← SUPPRIMER bloc ll. 45-52
backend/app/services/natal_chart_long_entitlement_gate.py       ← SUPPRIMER bloc ll. 46-52
backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py  ← SUPPRIMER test ll. 96-110
backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py       ← SUPPRIMER test ll. 112-125

backend/app/services/quota_service.py              ← AJOUTER commentaire LEGACY en tête
backend/app/infra/db/models/billing.py             ← AJOUTER commentaire LEGACY avant UserDailyQuotaUsageModel (l. 74)
backend/app/api/v1/routers/billing.py              ← AJOUTER commentaire LEGACY avant @router.get("/quota")
frontend/src/api/billing.ts                        ← AJOUTER commentaire LEGACY sur fetchQuotaStatus
backend/docs/entitlements-canonical-platform.md    ← CRÉER (nouveau)
```

### Suppression de `_legacy_fallback` — diff cible

```python
# AVANT (entitlement_service.py:211-259)
@staticmethod
def _legacy_fallback(
    subscription: SubscriptionStatusData, feature_code: str
) -> FeatureEntitlement:
    """DEPRECATED: suppression en 61.16"""
    ...  # ~49 lignes à supprimer en totalité

# APRÈS : méthode absente. Aucun code ne l'appelle depuis 61.15.
```

### Suppression des checks défensifs dans les gates — diff cible

```python
# AVANT (thematic_consultation_entitlement_gate.py:45-52 / natal_chart_long_entitlement_gate.py:46-52)
        # Pas de chemin legacy — xxx est 100% canonique
        # Si legacy_fallback retourné → traiter comme canonical_no_binding
        if entitlement.reason == "legacy_fallback":
            raise XxxAccessDeniedError(
                reason="canonical_no_binding",
                billing_status=entitlement.billing_status,
            )

# APRÈS : ces 6 lignes sont supprimées. Le check final_access qui suit reste intact.
```

### Usages résiduels de QuotaService après 61.16 (à documenter)

| Fichier | Usage | Action 61.16 | Suite |
|---------|-------|--------------|-------|
| `billing.py` (router) | `GET /v1/billing/quota` endpoint | Commentaire LEGACY | Décommission après audit front |
| `quota_service.py` | Module lui-même | Commentaire LEGACY | Suppression avec l'endpoint |
| `migrate_legacy_quota_to_canonical.py` | Script one-shot | Conserver tel quel | Archive après usage |
| `test_quota_service.py` | Tests unitaires | Ne pas toucher | Suppression avec le module |

### Usages résiduels de `user_daily_quota_usages` après 61.16 (à documenter)

| Fichier | Usage | Action 61.16 |
|---------|-------|--------------|
| `models/billing.py` | Modèle SQLAlchemy | Commentaire LEGACY |
| `privacy_service.py:475` | Export RGPD (liste de tables) | Conserver obligatoirement |
| `migrations/versions/20260219_0007_...py` | Migration Alembic | Conserver (historique) |
| `migrate_legacy_quota_to_canonical.py` | Lecture legacy usage | Conserver (script) |

### Audit front de `fetchQuotaStatus`

**Résultat de l'audit après code review** : la première implémentation de 61.16 documentait à tort `fetchQuotaStatus` comme dead code. En réalité, le frontend web consommait encore `useBillingQuota()` dans plusieurs écrans. Le correctif de review a conservé le nom historique `fetchQuotaStatus`, mais l'a rerouté vers `GET /v1/entitlements/me` afin que le web lise désormais la source canonique sans dépendre de l'endpoint legacy `/billing/quota`.

### Politique de suppression de la table `user_daily_quota_usages`

La table **ne doit pas être droppée en 61.16** car :
1. `privacy_service.py` l'inclut dans l'export RGPD — obligation légale
2. Le script `migrate_legacy_quota_to_canonical.py` en a besoin pour les runs futurs
3. Un rollback de 61.15 en production nécessiterait que la table soit intacte

La suppression définitive de la table est une story post-61.16 qui nécessite :
- Confirmation que `migrate_legacy_quota_to_canonical.py` a été joué en production
- Retrait de la table de `privacy_service.py` avec remplacement par `feature_usage_counters`
- Migration Alembic DROP TABLE

### Architecture canonique — état final après 61.16

Features B2C **100% canoniques** (`feature_usage_counters`) :
- `astrologer_chat` — migré en 61.11, fallback supprimé en 61.15, artefacts en 61.16
- `natal_chart_long` — migré en 61.13 (jamais eu de legacy runtime)
- `thematic_consultation` — migré en 61.12 (jamais eu de legacy runtime)

`EntitlementService.get_feature_entitlement` ne peut plus retourner `reason="legacy_fallback"` après 61.16 — la méthode `_legacy_fallback` n'existera plus. Le test d'intégration `test_no_legacy_fallback_reason_in_response` dans `test_entitlements_me.py` reste comme garde-fou permanent.

### Stack et conventions

- Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2
- `reason` dans `FeatureEntitlement` est typée `str` (pas de Literal) — aucune modification de type nécessaire
- Les suppressions sont des `str`-match — pas de changement de contrat API
- `ruff check .` doit passer sans `# noqa`

### Garde-fous de non-régression critiques

- **Ne pas toucher** `QuotaUsageService` — utilisé par les gates canoniques
- **Ne pas toucher** `ChatEntitlementGate`, `NatalChartLongEntitlementGate`, `ThematicConsultationEntitlementGate` au-delà de la suppression du bloc legacy
- **Ne pas toucher** `quota_service.py` au-delà du commentaire de tête (les tests unitaires existants de `test_quota_service.py` doivent continuer à passer)
- **Ne pas toucher** `privacy_service.py` — l'usage RGPD est obligatoire
- **`test_no_legacy_fallback_reason_in_response`** dans `test_entitlements_me.py` doit rester — c'est un garde-fou permanent

### Contexte stories précédentes

- **61-9** : `EntitlementService._legacy_fallback` introduite comme fallback temporaire
- **61-11** : `ChatEntitlementGate` — chemin hybride legacy/canonique
- **61-12** : `ThematicConsultationEntitlementGate` — 100% canonique, check défensif ajouté
- **61-13** : `NatalChartLongEntitlementGate` — 100% canonique, check défensif ajouté
- **61-14** : `GET /v1/entitlements/me` — remplace `GET /v1/billing/quota` pour l'UX front
- **61-15** : Suppression runtime du fallback sur `astrologer_chat`, `_legacy_fallback` marquée DEPRECATED

### Project Structure Notes

- `backend/docs/` : dossier à créer si inexistant (vérifier avec `ls backend/docs/` ou glob)
- Fichier de doc : markdown pur, pas de frontmatter requis
- Aucune nouvelle table, aucune migration Alembic dans cette story

### References

- `EntitlementService._legacy_fallback` : [entitlement_service.py:211](backend/app/services/entitlement_service.py#L211)
- Check défensif thematic : [thematic_consultation_entitlement_gate.py:45](backend/app/services/thematic_consultation_entitlement_gate.py#L45)
- Check défensif natal : [natal_chart_long_entitlement_gate.py:46](backend/app/services/natal_chart_long_entitlement_gate.py#L46)
- Test legacy thematic : [test_thematic_consultation_entitlement_gate.py:96](backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py#L96)
- Test legacy natal : [test_natal_chart_long_entitlement_gate.py:112](backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py#L112)
- `UserDailyQuotaUsageModel` : [models/billing.py:74](backend/app/infra/db/models/billing.py#L74)
- Endpoint quota legacy : [billing.py:323](backend/app/api/v1/routers/billing.py#L323)
- `fetchQuotaStatus` dead code : [billing.ts:138](frontend/src/api/billing.ts#L138)
- Garde-fou intégration : [test_entitlements_me.py:525](backend/app/tests/integration/test_entitlements_me.py#L525)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List
- Code review BMAD : correction d'un finding HIGH. Le frontend web utilisait encore `/v1/billing/quota` via `useBillingQuota()`, contrairement à la story et à la documentation.
- `fetchQuotaStatus` conserve son nom legacy mais lit maintenant `GET /v1/entitlements/me` pour l'usage `astrologer_chat`.
- Documentation backend et commentaires LEGACY ajustés pour refléter l'état réel après correction.
- `UsageSettings.tsx` nettoyé pour supprimer les styles inline et respecter les règles du dépôt.

### File List
- backend/app/api/v1/routers/billing.py
- backend/docs/entitlements-canonical-platform.md
- frontend/src/api/billing.ts
- frontend/src/pages/settings/Settings.css
- frontend/src/pages/settings/UsageSettings.tsx
- frontend/src/tests/App.test.tsx
- frontend/src/tests/AppShell.test.tsx
- frontend/src/tests/SettingsPage.test.tsx
- frontend/src/tests/router.test.tsx
