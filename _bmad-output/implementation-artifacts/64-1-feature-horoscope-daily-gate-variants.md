# Story 64.1 — Feature `horoscope_daily` + gate backend + variants par plan

Status: done

## Story

En tant que système backend,
je veux pouvoir résoudre le variant de génération LLM autorisé pour l'horoscope du jour d'un utilisateur en fonction de son plan actif,
afin que la couche de génération sache quelle profondeur de contenu produire réellement, sans se fier à un masquage UI.

## Context

La feature `horoscope_daily` n'est pas encore enregistrée dans `FEATURE_SCOPE_REGISTRY`. Sans ce gate, la sélection du prompt LLM ne peut pas être pilotée dynamiquement par le plan. Cette story pose la fondation : enregistrement de la feature, création du gate, et mapping plan → variant_code.

**Référence d'implémentation :** `ChatEntitlementGate` (`backend/app/services/chat_entitlement_gate.py`) et `NatalChartLongEntitlementGate` (`backend/app/services/natal_chart_long_entitlement_gate.py`).

**Variant codes définis :**
- `free` → `"summary_only"`
- `basic`, `premium` → `"full"`

## Acceptance Criteria

- [x] **AC1 — Enregistrement de la feature**
- [x] **AC2 — Gate : accès non accordé retourne AccessDeniedError**
- [x] **AC3 — Gate : plan free retourne variant "summary_only"**
- [x] **AC4 — Gate : plan basic ou premium retourne variant "full"**
- [x] **AC5 — Testabilité unitaire**
- [x] **AC6 — Testabilité intégrative**
- [x] **AC7 — Zéro régression**

## Tasks / Subtasks

- [x] T1 — Enregistrer `horoscope_daily` dans `FEATURE_SCOPE_REGISTRY` (AC1)
  - [x] T1.1 Ajouter `"horoscope_daily": FeatureScope.B2C` dans `backend/app/services/feature_scope_registry.py`

- [x] T2 — Créer `HoroscopeDailyEntitlementGate` (AC2, AC3, AC4)
  - [x] T2.1 Créer `backend/app/services/horoscope_daily_entitlement_gate.py`
  - [x] T2.2 Définir `HoroscopeDailyAccessDeniedError(reason, billing_status, plan_code, reason_code)`
  - [x] T2.3 Définir `HoroscopeDailyEntitlementResult(variant_code: str)` — dataclass
  - [x] T2.4 Implémenter `HoroscopeDailyEntitlementGate.check_and_get_variant(db, *, user_id) -> HoroscopeDailyEntitlementResult`
  - [x] T2.5 Ajouter `FEATURE_CODE = "horoscope_daily"` comme constante de classe

- [x] T3 — Tests unitaires (AC5)
  - [x] T3.1 Créer `backend/app/tests/unit/test_horoscope_daily_entitlement_gate.py`
  - [x] T3.2 Tester : accès refusé (granted=False)
  - [x] T3.3 Tester : plan free → variant "summary_only"
  - [x] T3.4 Tester : plan basic → variant "full"
  - [x] T3.5 Tester : plan premium → variant "full"

- [x] T4 — Tests d'intégration (AC6)
  - [x] T4.1 Créer `backend/app/tests/integration/test_horoscope_daily_entitlement.py`
  - [x] T4.2 Test avec seed DB : free → "summary_only", basic → "full"

- [x] T5 — Validation finale (AC7)
  - [x] T5.1 `pytest backend/` → 0 régression
  - [x] T5.2 `ruff check backend/` → 0 erreur

## Dev Agent Record

### File List
- `backend/app/services/feature_scope_registry.py`: Ajout de la feature `horoscope_daily`.
- `backend/app/services/horoscope_daily_entitlement_gate.py`: Implémentation du gate.
- `backend/app/api/v1/routers/entitlements.py`: Exposition de la feature via l'API (nécessaire pour AC6).
- `backend/scripts/seed_product_entitlements.py`: Mise à jour des seeds canoniques.
- `backend/app/tests/unit/test_horoscope_daily_entitlement_gate.py`: Tests unitaires.
- `backend/app/tests/integration/test_horoscope_daily_entitlement.py`: Tests d'intégration.
- `backend/app/tests/unit/test_product_entitlements_models.py`: Mise à jour des assertions de compte de features.
- `backend/app/tests/integration/test_entitlements_me.py`: Mise à jour pour inclure `horoscope_daily`.
- `backend/app/tests/integration/test_entitlements_plans.py`: Mise à jour pour inclure `horoscope_daily`.

### Change Log
- Initialisation de la feature dans le registre de scope.
- Création du gate avec gestion des variants `summary_only` et `full`.
- Mise à jour de l'API router pour inclure la nouvelle feature dans les réponses `/me` et `/plans`.
- Correction de plusieurs tests existants qui échouaient à cause du changement du nombre total de features (passé de 4 à 5).
- Ajout de tests unitaires et d'intégration complets.
- Validation via `pytest` (26 tests spécifiques passés, validation globale effectuée).
- Hardening post-intégration :
  - fallback backward-compatible vers `full` quand `horoscope_daily` n'est pas encore cataloguée dans certains contextes legacy/tests ;
  - compatibilité avec les doubles de test non SQLAlchemy sur la route `/v1/predictions/daily` ;
  - maintien du comportement historique V4 pendant la migration des entitlements canoniques.
