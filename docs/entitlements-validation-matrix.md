# Matrice de validation métier des droits produit (Entitlements)

Ce document définit la source de vérité pour la validation end-to-end des offres commerciales. Il est synchronisé avec le script `backend/scripts/seed_product_entitlements.py`.

## Légende des colonnes
- **granted** : Accès accordé au runtime.
- **access_mode** : Mode d'accès (`unlimited`, `quota`, `disabled`).
- **quota_limit** : Valeur limite du quota (si applicable).
- **reason_code** : Code de justification retourné par l'API.
- **variant_code** : Code de variante métier (ex: `single_astrologer`).

---

## 1. Cas : Utilisateur sans abonnement (`plan_code="none"`)

Dans ce cas, `BillingService` ne retourne aucun plan actif. Le resolver considère que l'utilisateur n'est rattaché à aucun plan canonique.

| Feature | granted | access_mode | quota_limit | variant_code | reason_code |
|---|---|---|---|---|---|
| `natal_chart_short` | false | null | null | null | `feature_not_in_plan` |
| `natal_chart_long` | false | null | null | null | `feature_not_in_plan` |
| `astrologer_chat` | false | null | null | null | `feature_not_in_plan` |
| `thematic_consultation` | false | null | null | null | `feature_not_in_plan` |

---

## 2. Plan : `free` (Abonnement actif au plan "free")

| Feature | granted | access_mode | quota_limit | variant_code | reason_code |
|---|---|---|---|---|---|
| `natal_chart_short` | **true** | `unlimited` | null | null | `granted` |
| `natal_chart_long` | false | `disabled` | null | null | `binding_disabled` |
| `astrologer_chat` | false | `disabled` | null | null | `binding_disabled` |
| `thematic_consultation` | false | `disabled` | null | null | `binding_disabled` |

---

## 3. Plan : `trial` (Statut de facturation : `trialing`)

| Feature | granted | access_mode | quota_limit | variant_code | Période / Reset |
|---|---|---|---|---|---|
| `natal_chart_short` | **true** | `unlimited` | null | null | - |
| `natal_chart_long` | **true*** | `quota` | 1 | `single_astrologer` | Lifetime |
| `astrologer_chat` | false | `disabled` | null | null | - |
| `thematic_consultation` | **true*** | `quota` | 1 | null | 1 semaine (CALENDAR) |

*\* Accès accordé si le quota n'est pas épuisé.*

---

## 4. Plan : `basic` (Statut de facturation : `active`)

| Feature | granted | access_mode | quota_limit | variant_code | Période / Reset |
|---|---|---|---|---|---|
| `natal_chart_short` | **true** | `unlimited` | null | null | - |
| `natal_chart_long` | **true*** | `quota` | 1 | `single_astrologer` | Lifetime |
| `astrologer_chat` | **true*** | `quota` | 5 | null | 1 jour (CALENDAR) |
| `thematic_consultation` | **true*** | `quota` | 1 | null | 1 semaine (CALENDAR) |

---

## 5. Plan : `premium` (Statut de facturation : `active`)

| Feature | granted | access_mode | quota_limit | variant_code | Période / Reset |
|---|---|---|---|---|---|
| `natal_chart_short` | **true** | `unlimited` | null | null | - |
| `natal_chart_long` | **true*** | `quota` | 5 | `multi_astrologer` | Lifetime |
| `astrologer_chat` | **true*** | `quota` | 2000 | null | 1 mois (CALENDAR) |
| `thematic_consultation` | **true*** | `quota` | 2 | null | 1 jour (CALENDAR) |

---

## Invariants de cohérence (Contrat Frontend)

L'API `GET /v1/entitlements/me` doit respecter les invariants suivants :
1. Si `granted == false`, un `reason_code` doit être présent.
2. Si `access_mode == "unlimited"`, `quota_limit` et `quota_remaining` doivent être `null`.
3. Si `access_mode == "quota"`, `quota_limit` et `quota_remaining` doivent être des entiers (>= 0).
4. `variant_code` n'est exposé que s'il apporte une distinction métier (ex: type d'astrologue).
