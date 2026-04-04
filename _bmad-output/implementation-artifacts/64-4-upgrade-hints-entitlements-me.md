# Story 64.4 — Upgrade hints dans EntitlementsMeResponse (backward compatible)

Status: done

## Story

En tant que frontend,
je veux que l'endpoint `/v1/entitlements/me` retourne, en plus des droits existants, une liste d'`upgrade_hints` structurés indiquant pour chaque feature bridée quel plan cibler et quel bénéfice débloquer,
afin de piloter les CTA d'upgrade sans contenir aucune logique métier de plan côté frontend.

## Context

Cette story enrichit la réponse `/v1/entitlements/me` de manière additive. Elle permet au backend de suggérer le plan suivant pour chaque feature qui n'est pas pleinement accessible (soit non accordée, soit restreinte par un variant).

**Contrat UpgradeHint :**
- `feature_code`: identifiant de la feature.
- `current_plan_code`: plan actuel.
- `target_plan_code`: plan suggéré (le plan suivant dans la hiérarchie de prix).
- `benefit_key`: clé i18n pour le bénéfice.
- `cta_variant`: type d'affichage (`banner`, `inline`, `modal`).
- `priority`: ordre d'importance.

## Acceptance Criteria

- [x] **AC1 — Nouveau champ upgrade_hints dans EntitlementsMeData** : ajouté avec valeur par défaut `[]`.
- [x] **AC2 — Schéma UpgradeHintResponse défini** : modèle Pydantic complet avec validation `Literal`.
- [x] **AC3 — Hints calculés dynamiquement** : logique implémentée dans `EffectiveEntitlementResolverService`.
- [x] **AC4 — Backward compatibility** : la structure de réponse existante est préservée.
- [x] **AC5 — Hints absents pour les utilisateurs premium** : vérifié via tests unitaires.
- [x] **AC6 — Tests unitaires** : couverture complète de la logique de calcul et de l'endpoint.
- [x] **AC7 — Test d'intégration** : validation du contrat de réponse complet.
- [x] **AC8 — Zéro régression** : tous les tests entitlements existants passent.

## Tasks / Subtasks

- [x] T1 — Définir `UpgradeHintResponse` dans les schémas (AC1, AC2)
  - [x] T1.1 Mettre à jour `backend/app/api/v1/schemas/entitlements.py`

- [x] T2 — Définir le dataclass interne `UpgradeHint` côté services (AC3)
  - [x] T2.1 Ajouter dans `backend/app/services/entitlement_types.py`

- [x] T3 — Implémenter `compute_upgrade_hints()` dans `EffectiveEntitlementResolverService` (AC3, AC5)
  - [x] T3.1 Implémenter la logique de recherche du plan suivant via `PlanCatalogModel` joint à `BillingPlanModel` (pour le prix)
  - [x] T3.2 Gérer les variants restreints (`summary_only`, `free_short`)
  - [x] T3.3 Implémenter les mappings de priorité et de variante de CTA

- [x] T4 — Intégrer dans le router entitlements (AC3, AC4)
  - [x] T4.1 Appeler le calcul des hints dans le handler `GET /me`

- [x] T5 — Tests unitaires (AC6)
  - [x] T5.1 Mettre à jour `backend/app/tests/unit/test_entitlements_me_endpoint.py`
  - [x] T5.2 Créer `backend/app/tests/unit/test_upgrade_hints_service.py`

- [x] T6 — Test d'intégration (AC7)
  - [x] T6.1 Mettre à jour `backend/app/tests/integration/test_entitlements_me_contract.py`

- [x] T7 — Validation finale (AC8)
  - [x] T7.1 `pytest backend/` → 0 régression

## Dev Agent Record

### File List
- `backend/app/api/v1/schemas/entitlements.py`: Ajout du schéma `UpgradeHintResponse` et du champ `upgrade_hints`.
- `backend/app/services/entitlement_types.py`: Ajout du dataclass `UpgradeHint`.
- `backend/app/services/effective_entitlement_resolver_service.py`: Logique de calcul des hints et résolution du plan suivant.
- `backend/app/api/v1/routers/entitlements.py`: Intégration dans l'endpoint `/me`.
- `backend/app/tests/unit/test_upgrade_hints_service.py`: Tests unitaires de la logique métier.
- `backend/app/tests/unit/test_entitlements_me_endpoint.py`: Mise à jour des tests de l'endpoint (support de 5 features et patch des hints).
- `backend/app/tests/integration/test_entitlements_me_contract.py`: Mise à jour du test de contrat.

### Change Log
- Introduction d'un système de recommandation d'upgrade piloté par le backend.
- Résolution dynamique du plan cible en fonction de la hiérarchie des prix en base de données.
- Support du déclenchement des hints sur base de `granted=False` ou de `variant_code` restreint.
- Correction de plusieurs tests existants pour s'adapter au passage à 5 features prioritaires.
- Garantie de la compatibilité ascendante via l'usage de valeurs par défaut pour le nouveau champ.
