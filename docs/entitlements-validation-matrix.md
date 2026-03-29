# Matrice de validation métier des droits produit

Cette matrice documente les offres commerciales B2C à partir de
`backend/scripts/seed_product_entitlements.py`, puis les traduit dans le contrat
exposé par `GET /v1/entitlements/me`.

## Colonnes

- `granted`: accès effectif attendu.
- `access_mode`: `unlimited`, `quota`, `disabled` ou `null`.
- `quota_limit`: limite exposée au top-level du payload, sinon `null`.
- `quota_key` / `period_unit` / `period_value` / `reset_mode`: détails exacts du seed si quota.
- `reason_code`: vocabulaire frontend normalisé.
- `variant_code`: variante métier exposée si pertinente.
- `Comportement API`: lecture attendue du payload `GET /v1/entitlements/me`.

## Utilisateur sans abonnement (`plan_code="none"`, `billing_status="none"`)

| Feature | granted | access_mode | quota_limit | quota_key | period_unit | period_value | reset_mode | reason_code | variant_code | Comportement API |
|---|---|---|---|---|---|---|---|---|---|---|
| `natal_chart_short` | false | null | null | null | null | null | null | `feature_not_in_plan` | null | Feature présente, `quota_remaining=null`, `usage_states=[]` |
| `natal_chart_long` | false | null | null | null | null | null | null | `feature_not_in_plan` | null | Feature présente, `quota_remaining=null`, `usage_states=[]` |
| `astrologer_chat` | false | null | null | null | null | null | null | `feature_not_in_plan` | null | Feature présente, `quota_remaining=null`, `usage_states=[]` |
| `thematic_consultation` | false | null | null | null | null | null | null | `feature_not_in_plan` | null | Feature présente, `quota_remaining=null`, `usage_states=[]` |

## Plan `free` actif (`plan_code="free"`, `billing_status="active"`)

| Feature | granted | access_mode | quota_limit | quota_key | period_unit | period_value | reset_mode | reason_code | variant_code | Comportement API |
|---|---|---|---|---|---|---|---|---|---|---|
| `natal_chart_short` | true | `unlimited` | null | null | null | null | null | `granted` | null | `quota_remaining=null`, `usage_states=[]` |
| `natal_chart_long` | false | `disabled` | null | null | null | null | null | `binding_disabled` | null | `quota_remaining=null`, `usage_states=[]` |
| `astrologer_chat` | false | `disabled` | null | null | null | null | null | `binding_disabled` | null | `quota_remaining=null`, `usage_states=[]` |
| `thematic_consultation` | false | `disabled` | null | null | null | null | null | `binding_disabled` | null | `quota_remaining=null`, `usage_states=[]` |

## Plan `trial` actif (`plan_code="trial"`, `billing_status="trialing"`)

| Feature | granted | access_mode | quota_limit | quota_key | period_unit | period_value | reset_mode | reason_code | variant_code | Comportement API |
|---|---|---|---|---|---|---|---|---|---|---|
| `natal_chart_short` | true | `unlimited` | null | null | null | null | null | `granted` | null | `quota_remaining=null`, `usage_states=[]` |
| `natal_chart_long` | true* | `quota` | 1 | `interpretations` | `lifetime` | 1 | `lifetime` | `granted` | `single_astrologer` | `quota_remaining=1` hors consommation, `usage_states[0]` aligné |
| `astrologer_chat` | false | `disabled` | null | null | null | null | null | `binding_disabled` | null | `quota_remaining=null`, `usage_states=[]` |
| `thematic_consultation` | true* | `quota` | 1 | `consultations` | `week` | 1 | `calendar` | `granted` | null | `quota_remaining=1` hors consommation, `usage_states[0]` aligné |

## Plan `basic` actif (`plan_code="basic"`, `billing_status="active"`)

| Feature | granted | access_mode | quota_limit | quota_key | period_unit | period_value | reset_mode | reason_code | variant_code | Comportement API |
|---|---|---|---|---|---|---|---|---|---|---|
| `natal_chart_short` | true | `unlimited` | null | null | null | null | null | `granted` | null | `quota_remaining=null`, `usage_states=[]` |
| `natal_chart_long` | true* | `quota` | 1 | `interpretations` | `lifetime` | 1 | `lifetime` | `granted` | `single_astrologer` | `quota_remaining=1` hors consommation, `usage_states[0]` aligné |
| `astrologer_chat` | true* | `quota` | 5 | `messages` | `day` | 1 | `calendar` | `granted` | null | `quota_remaining=5` hors consommation, `usage_states[0]` aligné |
| `thematic_consultation` | true* | `quota` | 1 | `consultations` | `week` | 1 | `calendar` | `granted` | null | `quota_remaining=1` hors consommation, `usage_states[0]` aligné |

## Plan `premium` actif (`plan_code="premium"`, `billing_status="active"`)

| Feature | granted | access_mode | quota_limit | quota_key | period_unit | period_value | reset_mode | reason_code | variant_code | Comportement API |
|---|---|---|---|---|---|---|---|---|---|---|
| `natal_chart_short` | true | `unlimited` | null | null | null | null | null | `granted` | null | `quota_remaining=null`, `usage_states=[]` |
| `natal_chart_long` | true* | `quota` | 5 | `interpretations` | `lifetime` | 1 | `lifetime` | `granted` | `multi_astrologer` | `quota_remaining=5` hors consommation, `usage_states[0]` aligné |
| `astrologer_chat` | true* | `quota` | 2000 | `messages` | `month` | 1 | `calendar` | `granted` | null | `quota_remaining=2000` hors consommation, `usage_states[0]` aligné |
| `thematic_consultation` | true* | `quota` | 2 | `consultations` | `day` | 1 | `calendar` | `granted` | null | `quota_remaining=2` hors consommation, `usage_states[0]` aligné |

## Cas transverse: billing inactif

Quand le plan existe mais que `billing_status` sort de `active` / `trialing`
par exemple `past_due`, toute feature activée par le plan reste exposée avec:

- `granted=false`
- `reason_code="billing_inactive"`
- `access_mode` inchangé
- `quota_limit` et `usage_states` toujours renseignés pour les features à quota

## Invariants frontend à vérifier

- `granted=false` implique toujours un `reason_code` dans
  `binding_disabled`, `feature_not_in_plan`, `billing_inactive`, `quota_exhausted`.
- `access_mode="unlimited"` implique `quota_limit=null` et `quota_remaining=null`.
- `access_mode="quota"` implique `quota_limit` et `quota_remaining` non nuls.
- `variant_code` n'est exposé que pour `natal_chart_long` en `trial`, `basic` et `premium`.

\* Hors quota épuisé.
