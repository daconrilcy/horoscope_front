# Story 61.69 : Refonte du packaging abonnements free / basic / premium et du modèle de consommation

Status: done

---

## Story

En tant qu'utilisateur B2C et en tant que système backend,
je veux que les abonnements free, basic et premium soient redéfinis avec une logique de packaging claire (découverte / usage régulier / expérience complète), que les quotas du catalogue canonique reflètent ce packaging, et que le frontend présente les plans en termes de valeur perçue sans exposer les tokens bruts,
afin d'avoir un modèle cohérent et lisible côté produit, et un enforcement technique précis et non ambigu côté backend.

---

## Contexte

### Mise à jour post-implémentation

Les décisions ci-dessous reflètent l'état finalement retenu après implémentation et corrections produit. Elles **prévalent** sur les passages plus anciens du document quand il y a contradiction.

- `free.natal_chart_short` : `unlimited`
- `trial.natal_chart_short` : `quota` `1` interprétation `lifetime`
- `basic.natal_chart_short` : `unlimited`
- `premium.natal_chart_short` : `unlimited`
- `free.astrologer_chat` : activé avec `1 message / semaine` (`quota_key="messages"`)
- `basic.astrologer_chat` : **retiré de l'offre** et rendu comme `disabled`
- `basic.thematic_consultation` : double contrainte explicite
  - `1 consultation / semaine` (`quota_key="consultations"`)
  - `20 000 tokens / semaine` (`quota_key="tokens"`)
- `premium.thematic_consultation` : pas de quota de nombre ; règle produit exprimée comme
  - `Consultations thématiques illimitées dans la limite des tokens disponibles`
- `/help/subscriptions`
  - s'appuie sur `GET /v1/entitlements/plans` pour le catalogue
  - s'appuie sur `GET /v1/entitlements/me` pour détecter le plan courant, y compris `free`
  - n'affiche plus le CTA héro dupliqué
  - n'affiche pas de bouton sur la carte du plan courant et rend `Votre plan actuel`
  - affiche `processing_priority` comme badge de présentation

En pratique, cela signifie que certains AC rédigés initialement pour `basic.astrologer_chat` et `basic.thematic_consultation` ont été **supersédés par ces arbitrages finaux**.

### Historique des stories précédentes

- **61-67** : migration des quotas vers les tokens LLM. Cible du seed définie mais non entièrement appliquée pour le plan `basic` (`astrologer_chat` reste `DISABLED` dans le seed actuel).
- **61-68** : page `/help/subscriptions` construite sur le catalogue canonique via `GET /v1/entitlements/plans`. Les valeurs affichées viennent du backend, pas du frontend.
- **Migration `0066`** (fichier `backend/migrations/versions/20260402_0066_add_user_visibility_flags_to_billing_plans.py`) : non commitée mais présente — ajoute `is_visible_to_users` / `is_available_to_users` sur `billing_plans`. Ce contexte est acquis.

### Problèmes produit à résoudre

| Problème actuel | Cible story 61-69 |
|---|---|
| `natal_chart_short` a un quota lifetime 1 interprétation sur tous les plans | Passe en `UNLIMITED` sur free, basic et premium |
| `basic.astrologer_chat` est `DISABLED` | Réactivé avec quotas tokens |
| `basic.thematic_consultation` a un double quota `consultations` + `tokens` | Simplification : tokens uniquement |
| Plan `free` sans accès au chat | 1 message de chat par semaine |
| Aucune notion de priorité de traitement dans le catalogue | Ajout de `processing_priority` dans l'API |
| Frontend trop technique / chiffres exposés de façon fragile | Reformulation orientée valeur perçue, sans budget partagé fictif |

### Point d’architecture à respecter

Cette story **ne met pas en place un vrai budget mutualisé IA**.
Le moteur reste **per-feature** :

- `astrologer_chat` conserve ses propres quotas
- `thematic_consultation` conserve ses propres quotas
- `natal_chart_short` et `natal_chart_long` restent des entitlements distincts hors logique de budget partagé

Conséquence importante :

- **backend** : enforcement par feature, comme aujourd’hui
- **frontend** : wording orienté bénéfice, mais **sans prétendre qu’il existe un unique budget partagé chiffré**

La création d’un véritable pool mutualisé du type `ai_shared_budget` est explicitement **hors scope** et renvoyée à une story ultérieure.

### Modèle produit cible

| Plan | Positionnement | Priorité |
|------|----------------|----------|
| free | Découverte | low |
| basic | Usage régulier | medium |
| premium | Expérience complète | high |

### État cible du catalogue seed

| Plan | Feature | `is_enabled` | `access_mode` | Quotas |
|------|---------|---|---|---|
| free | natal_chart_short | true | `unlimited` | — |
| free | natal_chart_long | false | `disabled` | — |
| free | astrologer_chat | true | `quota` | 1 message/semaine (`messages`) |
| free | thematic_consultation | false | `disabled` | — |
| trial | natal_chart_short | true | `quota` | 1 interprétation (`lifetime`) — inchangé |
| trial | natal_chart_long | true | `quota` | 1 interprétation (`lifetime`) — inchangé |
| trial | astrologer_chat | false | `disabled` | — inchangé |
| trial | thematic_consultation | true | `quota` | 5000 tokens/semaine — inchangé |
| basic | natal_chart_short | true | `unlimited` | — |
| basic | natal_chart_long | true | `quota` | 1 interprétation (`lifetime`) |
| basic | astrologer_chat | true | `quota` | 1667 tokens/jour · 12500/semaine · 50000/mois |
| basic | thematic_consultation | true | `quota` | 20000 tokens/semaine |
| premium | natal_chart_short | true | `unlimited` | — |
| premium | natal_chart_long | true | `quota` | 5 interprétations (`lifetime`) |
| premium | astrologer_chat | true | `quota` | 50000 tokens/jour · 375000/semaine · 1500000/mois |
| premium | thematic_consultation | true | `quota` | 200000 tokens/mois |

---

## Acceptance Criteria

### AC1 — `natal_chart_short` passe en `unlimited` pour free, basic et premium

Dans `backend/scripts/seed_product_entitlements.py`, chaque binding `natal_chart_short` pour `free`, `basic` et `premium` est modifié :

```python
"natal_chart_short": {
    "is_enabled": True,
    "access_mode": AccessMode.UNLIMITED,
    "variant_code": None,
    "quotas": [],
},
```

Contraintes :

- `trial.natal_chart_short` reste inchangé (`QUOTA`, 1 interprétation lifetime).
- Tous les quotas `PlanFeatureQuotaModel` associés à `natal_chart_short` pour ces trois plans sont supprimés par le service canonique au prochain seed idempotent.
- L'endpoint `GET /v1/entitlements/plans` retourne `"access_mode": "unlimited"` et `"quotas": []` pour `natal_chart_short` sur free, basic et premium.

---

### AC2 — Plan free : `astrologer_chat` activé avec 1 message par semaine

Dans le seed, `free.astrologer_chat` passe de `DISABLED` à `QUOTA` avec :

```python
"astrologer_chat": {
    "is_enabled": True,
    "access_mode": AccessMode.QUOTA,
    "variant_code": None,
    "quotas": [
        {
            "quota_key": "messages",
            "quota_limit": 1,
            "period_unit": PeriodUnit.WEEK,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        }
    ],
},
```

Contraintes :

- La clé `messages` est intentionnellement distincte de `tokens` — c'est une règle produit explicite propre au free.
- L'enforcement dans `ChatEntitlementGate` doit gérer le quota_key `messages`.

Règle d’implémentation :

- **Pré-check** : vérifier que le quota `messages` restant est strictement supérieur à 0.
- **Débit** : pour un quota `messages`, le débit doit être effectué **avant exécution du call LLM**, via `QuotaUsageService.consume(amount=1)`.
- Si l'appel LLM échoue après ce débit, la story n'impose **aucun mécanisme de rollback** : ce comportement doit être documenté explicitement dans les notes de dev et dans le test.
- Si `quota_key == "tokens"` → conserver le comportement actuel de débit post-LLM via `LlmTokenUsageService`.

Objectif :

- éviter de consommer des ressources LLM alors que le quota message est déjà épuisé
- éviter un faux modèle post-débit pour un coût fixe connu d’avance

---

### AC3 — Plan basic : `astrologer_chat` réactivé avec quotas tokens

Dans le seed, `basic.astrologer_chat` passe de `DISABLED` à `QUOTA` :

```python
"astrologer_chat": {
    "is_enabled": True,
    "access_mode": AccessMode.QUOTA,
    "variant_code": None,
    "quotas": [
        {
            "quota_key": "tokens",
            "quota_limit": 1_667,
            "period_unit": PeriodUnit.DAY,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        },
        {
            "quota_key": "tokens",
            "quota_limit": 12_500,
            "period_unit": PeriodUnit.WEEK,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        },
        {
            "quota_key": "tokens",
            "quota_limit": 50_000,
            "period_unit": PeriodUnit.MONTH,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        },
    ],
},
```

Contraintes :

- Aucun changement au flux de débit tokens de basic/premium : le comportement de la story 61-67 reste en place.
- Les valeurs sont strictement celles déjà cadrées par 61-67.

---

### AC4 — Plan basic : `thematic_consultation` simplifié (tokens uniquement)

Dans le seed, `basic.thematic_consultation` passe de 2 quotas (`consultations` + `tokens`) à 1 seul quota :

```python
"thematic_consultation": {
    "is_enabled": True,
    "access_mode": AccessMode.QUOTA,
    "variant_code": None,
    "quotas": [
        {
            "quota_key": "tokens",
            "quota_limit": 20_000,
            "period_unit": PeriodUnit.WEEK,
            "period_value": 1,
            "reset_mode": ResetMode.CALENDAR,
        }
    ],
},
```

Contraintes :

- `CanonicalEntitlementMutationService.upsert_plan_feature_configuration()` supprime le quota `consultations` obsolète lors de l'upsert.
- Aucun changement au `ThematicConsultationEntitlementGate`.

---

### AC5 — Endpoint `GET /v1/entitlements/plans` expose `processing_priority`

Le DTO `PlanCatalogData` dans `backend/app/api/v1/schemas/entitlements.py` est enrichi :

```python
class PlanCatalogData(BaseModel):
    plan_code: str
    plan_name: str
    monthly_price_cents: int
    currency: str
    is_active: bool
    processing_priority: str  # "low" | "medium" | "high"
    features: list[PlanFeatureData]
```

Le mapping de priorité est calculé dans le routeur `backend/app/api/v1/routers/entitlements.py` :

```python
_PLAN_PRIORITY: dict[str, str] = {
    "free": "low",
    "basic": "medium",
    "premium": "high",
}
# fallback : "medium"
```

Contraintes :

- Pas de nouveau champ en base.
- `processing_priority` est **un champ dérivé de présentation catalogue uniquement** dans cette story.
- Cette story **n’ajoute aucun impact runtime** sur les files, workers, modèles LLM, ordonnancement ou SLA.

---

### AC6 — Cohérence du comptage de quotas seed après double exécution idempotente

Après double exécution idempotente du seed :

- le nombre total de quotas persistés est de **14**
- ce total inclut explicitement `trial.natal_chart_short` (`interpretations`, `lifetime`)
- mais surtout, les tests doivent valider la **structure précise** des quotas persistés

Attendus minimaux :

| Plan | Feature | `quota_key` | Fenêtres attendues |
|------|---------|-------------|--------------------|
| free | astrologer_chat | `messages` | `week` |
| trial | natal_chart_short | `interpretations` | `lifetime` |
| trial | natal_chart_long | `interpretations` | `lifetime` |
| trial | thematic_consultation | `tokens` | `week` |
| basic | natal_chart_long | `interpretations` | `lifetime` |
| basic | astrologer_chat | `tokens` | `day`, `week`, `month` |
| basic | thematic_consultation | `tokens` | `week` |
| premium | natal_chart_long | `interpretations` | `lifetime` |
| premium | astrologer_chat | `tokens" | `day`, `week`, `month` |
| premium | thematic_consultation | `tokens` | `month` |

Contraintes :

- Le test peut vérifier aussi le total global `14`, mais **ce total ne suffit pas**.
- Les assertions doivent porter au minimum sur le couple `(plan_code, feature_code, quota_key, period_unit)`.

---

### AC7 — Frontend : wording orienté valeur perçue dans `/help/subscriptions`

La page `frontend/src/pages/SubscriptionGuidePage.tsx` et les traductions `frontend/src/i18n/support.ts` sont mises à jour pour :

1. **Taglines des plans** :
   - `free.tagline` : "Découverte — explorez l'astrologie à votre rythme"
   - `basic.tagline` : "Usage régulier — vivez l'astrologie au quotidien"
   - `premium.tagline` : "Expérience complète — priorité, profondeur, confort"

2. **Labels de features** :
   - `astrologer_chat` → "Chat astrologique"
   - `thematic_consultation` → "Consultations thématiques"
   - `natal_chart_short` → "Thème natal"
   - `natal_chart_long` → "Interprétation complète du thème natal"

3. **Affichage du chat free** :
   - si `quota.quota_key === "messages"` → afficher "1 message par semaine"
   - ne jamais afficher ce quota comme un quota token

4. **Affichage des plans basic et premium** :
   - ne pas exposer les tokens bruts sous forme de promesse marketing principale
   - ne pas afficher un faux message de type "budget partagé mensuel"
   - privilégier un wording qualitatif du type :
     - basic : "Capacité IA incluse pour un usage régulier"
     - premium : "Capacité IA étendue pour un usage intensif"

5. **Affichage de la priorité** :
   - chaque `PlanCard` affiche la priorité via `plan.processing_priority`
   - libellé i18n `priority.low` / `priority.medium` / `priority.high`
   - affichage discret

6. **Affichage d’`unlimited`** :
   - `access_mode === "unlimited"` est rendu côté UI comme "Inclus"
   - sans afficher de faux quota

7. **Règles CSS** :
   - aucun style inline
   - nouvelles classes préfixées `help-subscriptions-`
   - réutiliser les variables de design existantes

Contraintes :

- Les **taglines** et les **labels métier** peuvent être définis dans `support.ts`.
- Les **valeurs quantitatives issues du catalogue** ne doivent **pas** être recopiées en dur dans `support.ts`.
- Si un chiffre doit être affiché, il doit venir de l’API ou être dérivé dynamiquement des quotas reçus.

---

### AC8 — Tests backend

Tests minimum à couvrir ou mettre à jour :

- **Seed**
  - vérifier la présence structurée des 14 quotas attendus
  - vérifier `natal_chart_short` en `unlimited` pour free/basic/premium
- **Gate free / messages**
  - pre-check refuse si quota épuisé
  - débit `QuotaUsageService.consume(amount=1)` appelé avant exécution LLM
  - `LlmTokenUsageService` non appelé pour la voie `messages`
- **Entitlements plans**
  - `GET /v1/entitlements/plans` retourne `processing_priority = low / medium / high`
  - `astrologer_chat` est activé pour free et basic
  - `natal_chart_short` est `unlimited` pour free, basic, premium
- **Non-régression**
  - les tests existants sur le débit tokens de basic/premium ne régressent pas

---

### AC9 — Tests frontend

Dans `frontend/src/tests/SubscriptionGuidePage.test.tsx` :

- mise à jour des mocks pour inclure `processing_priority`
- vérification que le badge de priorité est affiché pour chaque plan
- vérification que le plan free affiche "1 message par semaine"
- vérification que `natal_chart_short` affiche "Inclus" sans quota
- vérification qu’aucune chaîne de type faux budget mutualisé n’est affichée pour basic/premium

---

## Tasks / Subtasks

- [x] **T1 — Seed : `natal_chart_short` → unlimited** (AC: 1)
  - [x] modifier `free`, `basic`, `premium` dans `seed_product_entitlements.py`
  - [x] laisser `trial.natal_chart_short` inchangé

- [x] **T2 — Seed : `free.astrologer_chat` → 1 message/semaine** (AC: 2)
  - [x] ajouter le binding `quota_key="messages"`, `quota_limit=1`, `period_unit=WEEK`

- [x] **T3 — Seed : `basic.astrologer_chat` → tokens réactivés** (AC: 3)
  - [x] passer de `DISABLED` à `QUOTA` avec les 3 quotas tokens

- [x] **T4 — Seed : `basic.thematic_consultation` → tokens uniquement** (AC: 4)
  - [x] supprimer le quota `consultations`, garder uniquement `tokens`

- [x] **T5 — `ChatEntitlementGate` : voie `messages` pré-débit, voie `tokens` inchangée** (AC: 2)
  - [x] identifier la branche du gate où le débit est déclenché
  - [x] pour `messages`, consommer avant call LLM
  - [x] pour `tokens`, conserver le débit post-LLM actuel
  - [x] documenter explicitement l’absence de rollback si échec du LLM après débit `messages`

- [x] **T6 — Entitlements plans endpoint : `processing_priority`** (AC: 5)
  - [x] ajouter `processing_priority: str` à `PlanCatalogData`
  - [x] ajouter le mapping `_PLAN_PRIORITY` dans le routeur

- [x] **T7 — i18n : wording orienté valeur perçue** (AC: 7)
  - [x] mettre à jour les taglines des plans
  - [x] ajouter `priority.low`, `priority.medium`, `priority.high`
  - [x] ajouter les labels métier nécessaires
  - [x] ne pas hardcoder de chiffres catalogues dans `support.ts`

- [x] **T8 — `SubscriptionGuidePage` : refonte wording + affichage priorité** (AC: 7)
  - [x] afficher la tagline par plan
  - [x] afficher la priorité depuis `plan.processing_priority`
  - [x] gérer `quota_key === "messages"` → "1 message par semaine"
  - [x] rendre `access_mode === "unlimited"` → "Inclus"
  - [x] supprimer toute formulation suggérant un budget partagé unique chiffré

- [x] **T9 — Tests backend** (AC: 6, 8)
  - [x] mettre à jour les tests seed avec assertions structurelles
  - [x] ajouter / mettre à jour les tests gate free `messages`
  - [x] ajouter / mettre à jour les tests entitlements plans

- [x] **T10 — Tests frontend** (AC: 9)
  - [x] mettre à jour les mocks
  - [x] vérifier priorité, free chat, unlimited natal
  - [x] vérifier l’absence de faux message de budget mutualisé

---

## Dev Notes

### Fichiers à modifier

```text
backend/scripts/seed_product_entitlements.py
backend/app/services/chat_entitlement_gate.py
backend/app/api/v1/schemas/entitlements.py
backend/app/api/v1/routers/entitlements.py
backend/app/tests/integration/test_entitlements_plans.py
backend/app/tests/integration/test_billing_api.py
backend/app/tests/unit/test_chat_entitlement_gate.py
backend/app/tests/unit/test_chat_entitlement_gate_v2.py
frontend/src/pages/SubscriptionGuidePage.tsx
frontend/src/i18n/support.ts
frontend/src/pages/HelpPage.css
frontend/src/tests/SubscriptionGuidePage.test.tsx
```

### Fichiers à NE PAS modifier (sauf découverte bloquante)

```text
backend/app/services/llm_token_usage_service.py
backend/app/services/thematic_consultation_entitlement_gate.py
backend/app/services/quota_usage_service.py
backend/app/services/quota_window_resolver.py
frontend/src/app/routes.tsx
```

### Pattern `ChatEntitlementGate`

Remarque de localisation de tests :

- selon l’état réel de la base de tests, les nouveaux cas `messages` peuvent devoir être ajoutés dans `test_chat_entitlement_gate.py`, `test_chat_entitlement_gate_v2.py`, ou les deux
- la story ne présume pas qu’un seul de ces deux fichiers soit la source de vérité


Le gate distingue désormais deux logiques :

- **quota `messages`** : coût fixe connu d’avance → pré-check puis débit avant exécution
- **quota `tokens`** : coût réel connu après réponse LLM → pré-check puis débit post-LLM via `LlmTokenUsageService`

Pseudo-code attendu :

```python
if binding_quota.quota_key == "messages":
    quota_usage_service.consume(
        db=db,
        user_id=user_id,
        feature_code=feature_code,
        quota=binding_quota,
        amount=1,
        ref_dt=now,
    )
    # puis seulement après : call LLM
else:
    await llm_token_usage_service.record_usage(
        db=db,
        user_id=user_id,
        feature_code=feature_code,
        quota=binding_quota,
        provider_model=gateway_result.model,
        tokens_in=gateway_result.usage.input_tokens,
        tokens_out=gateway_result.usage.output_tokens,
        request_id=request_id,
        llm_call_log_id=llm_call_log_id,
    )
```

### Décision explicitement hors scope

Les éléments suivants ne doivent **pas** être mis en œuvre dans cette story :

- création d’une feature `ai_shared_budget`
- mutualisation backend des quotas chat + consultations
- changement runtime réel de priorité selon le plan
- nouveau resolver global d’état de consommation d’abonnement
- migration Alembic dédiée

### Convention wording frontend

| Ce qu'on évite | Ce qu'on dit à la place |
|---|---|
| "50 000 tokens par mois" comme promesse marketing principale | "Capacité IA incluse pour un usage régulier" |
| "1 token/semaine" | "1 message par semaine" |
| "Unlimited access_mode" | "Inclus" |
| "Priority: low" | "Traitement standard" |

Remarque :

- si l’UI choisit d’afficher des chiffres détaillés issus du catalogue, ils doivent être dérivés dynamiquement de l’API
- aucun chiffre catalogue ne doit être dupliqué en dur dans les traductions

### Références

- `backend/scripts/seed_product_entitlements.py`
- `backend/app/services/chat_entitlement_gate.py`
- `backend/app/api/v1/routers/entitlements.py`
- `backend/app/api/v1/schemas/entitlements.py`
- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/i18n/support.ts`
- Story 61-67 — contexte quotas tokens
- Story 61-68 — contexte page `/help/subscriptions`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
