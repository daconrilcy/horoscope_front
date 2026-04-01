# Story 61.67 : Refactorisation du décompte des quotas en tokens LLM

Status: done

## Story

En tant que système de facturation et de pilotage produit,
je veux que les quotas d'usage des features LLM soient comptabilisés en **tokens** (entrée + sortie)
plutôt qu'en nombre de messages ou de consultations,
afin d'avoir une mesure fidèle au coût réel, un journal granulaire par utilisateur/service/période,
et des limites de plan configurables uniquement en base de données.

---

## Contexte

### État actuel

- `astrologer_chat` est aujourd'hui limité par `quota_key="messages"` dans le catalogue canonique.
- `thematic_consultation` est aujourd'hui limitée par `quota_key="consultations"`.
- `QuotaUsageService.consume(amount=N)` supporte déjà `N > 1` et peut donc compter des tokens sans changement structurel.
- `LlmCallLogModel` stocke déjà `tokens_in`, `tokens_out`, `model`, `request_id`, mais ce log n'est pas aujourd'hui relié à l'utilisateur facturé ni au compteur de quota.
- Le point bloquant réel n'est pas `QuotaUsageService`, mais le flux applicatif: `ChatEntitlementGate.check_and_consume()` et `ThematicConsultationEntitlementGate.check_and_consume()` consomment **avant** l'appel LLM, alors que le nombre exact de tokens n'est connu qu'après la réponse.

### Décisions de design pour cette story

1. La migration concerne uniquement les features B2C réellement pilotées par des appels LLM:
   - `astrologer_chat`
   - `thematic_consultation`

2. Les quotas deviennent des quotas de type `tokens`, mais la **source de vérité** reste `PlanFeatureQuotaModel`.

3. Le flux de quota doit devenir **en 2 temps**:
   - **pré-check d'accès** avant appel LLM, sans consommation;
   - **consommation exacte** après appel LLM, à partir des tokens réellement utilisés.

4. Le journal d'usage token doit être **atomique avec la consommation de quota**:
   si le compteur est incrémenté, le log d'usage existe; s'il n'y a pas de log, il n'y a pas de débit.

5. `LlmCallLogModel` reste un log d'observabilité. Le nouveau log utilisateur facturable est séparé.

---

## Acceptance Criteria

### AC1 - Nouveau modèle `UserTokenUsageLogModel`

Une nouvelle table `user_token_usage_logs` stocke chaque débit de quota LLM côté utilisateur:

```text
user_token_usage_logs
  id              UUID PK
  user_id         Integer FK -> users.id, NOT NULL, INDEX
  feature_code    VARCHAR(100) NOT NULL
  provider_model  VARCHAR(100) NOT NULL
  tokens_in       Integer NOT NULL >= 0
  tokens_out      Integer NOT NULL >= 0
  tokens_total    Integer NOT NULL
  request_id      VARCHAR(100) NOT NULL, INDEX
  llm_call_log_id UUID FK -> llm_call_logs.id NULL
  created_at      DateTime(timezone=True) NOT NULL, INDEX
```

- `tokens_total = tokens_in + tokens_out` est garanti par contrainte.
- Table append-only: pas d'UPDATE métier, pas de DELETE métier.
- Index minimum:
  - `(user_id, created_at)`
  - `(user_id, feature_code, created_at)`
  - `(request_id)`
- Une migration Alembic dédiée crée cette table.

### AC2 - Le catalogue canonique migre vers des quotas `tokens`

Le seed `backend/scripts/seed_product_entitlements.py` remplace les unités métier actuelles par des quotas `tokens` pour les features concernées.

Valeurs initiales attendues dans le seed pour cette story:

| Plan | Feature | quota_key | quota_limit | period_unit | reset_mode |
|------|---------|-----------|-------------|-------------|------------|
| basic | astrologer_chat | `tokens` | `50_000` | `month` | `calendar` |
| basic | thematic_consultation | `tokens` | `20_000` | `week` | `calendar` |
| premium | astrologer_chat | `tokens` | `1_500_000` | `month` | `calendar` |
| premium | thematic_consultation | `tokens` | `200_000` | `month` | `calendar` |

- Ces limites sont configurées **en base via le seed canonique**, pas dans le code applicatif.
- `CanonicalEntitlementMutationService.upsert_plan_feature_configuration()` doit bien supprimer les anciens quotas `messages` / `consultations` devenus obsolètes sur les bindings concernés.

### AC3 - Les entitlement gates ne consomment plus avant l'appel LLM

Les flows `chat` et `thematic_consultation` sont refactorés pour séparer:

- un **contrôle d'accès/quota** avant appel LLM, sans incrément du compteur;
- une **consommation exacte en tokens** après obtention de la réponse LLM.

Concrètement:

- `ChatEntitlementGate.check_and_consume()` et `ThematicConsultationEntitlementGate.check_and_consume()` ne doivent plus être le point de débit final pour les features tokenisées.
- La story peut soit:
  - introduire une nouvelle méthode `check_access(...)` / `check_only(...)`,
  - soit refactorer les gates existants pour dissocier explicitement check et consume.
- Aucun débit de quota ne doit être effectué si l'appel LLM n'a pas produit de réponse exploitable.

### AC4 - Les tokens exacts sont récupérés depuis le Gateway ou normalisés en fallback

Le débit de quota utilise les tokens réels issus du runtime LLM:

- source principale: `GatewayResult.usage.input_tokens` et `GatewayResult.usage.output_tokens`;
- fallback si la source ne fournit pas l'usage: estimation conservative documentée.

Règles:

- `tokens_total = tokens_in + tokens_out`
- fallback minimal: `estimate_tokens(text) = max(1, len(text) // 4)`
- si le fallback est utilisé, le log doit rester explicite via logging structuré

La story doit aussi prévoir la propagation de l'usage jusqu'aux services appelants:

- `AIEngineAdapter.generate_chat_reply()` ne peut plus se limiter à renvoyer une `str` si la route doit débiter des tokens exacts;
- le flux chat doit exposer au minimum le texte généré, le modèle, et les compteurs de tokens normalisés;
- le flux guidance/consultation utilise déjà `GatewayResult` et doit conserver cette information jusqu'au point de débit.

### AC5 - Nouveau service applicatif de débit tokenisé

Un service dédié, par exemple `LlmTokenUsageService`, orchestre le débit facturable:

```python
record_usage(
    db,
    *,
    user_id: int,
    feature_code: str,
    quota: QuotaDefinition,
    provider_model: str,
    tokens_in: int,
    tokens_out: int,
    request_id: str,
    llm_call_log_id: UUID | None = None,
    ref_dt: datetime | None = None,
) -> UsageState
```

Ce service:

- calcule `tokens_total`;
- incrémente `FeatureUsageCounterModel.used_count` via `QuotaUsageService.consume(amount=tokens_total)`;
- crée la ligne `UserTokenUsageLogModel`;
- effectue les deux opérations dans la **même transaction DB**.

Si le débit exact dépasse le quota restant:

- l'opération utilisateur est rejetée avec l'erreur de quota backend standard;
- les écritures métier liées à la réponse utilisateur ne sont pas commitées;
- le système ne laisse pas un compteur incrémenté sans log associé.

### AC6 - API d'audit d'usage token

Un endpoint `GET /v1/billing/token-usage` est ajouté.

Réponse cible:

```json
{
  "data": {
    "period": {
      "unit": "month",
      "window_start": "2026-04-01T00:00:00Z",
      "window_end": "2026-05-01T00:00:00Z"
    },
    "summary": {
      "tokens_total": 12450,
      "tokens_in": 8200,
      "tokens_out": 4250
    },
    "by_feature": [
      {
        "feature_code": "astrologer_chat",
        "tokens_total": 10200,
        "tokens_in": 6800,
        "tokens_out": 3400
      },
      {
        "feature_code": "thematic_consultation",
        "tokens_total": 2250,
        "tokens_in": 1400,
        "tokens_out": 850
      }
    ]
  },
  "meta": { "request_id": "..." }
}
```

- endpoint protégé comme `/v1/billing/subscription`
- agrégation basée sur `user_token_usage_logs`
- paramètres minimum: `period=current_month|current_week|current_day|all`
- l'API d'audit ne remplace pas `FeatureUsageCounterModel` pour l'enforcement

### AC7 - `GET /v1/billing/subscription` expose explicitement l'unité du quota courant

Le DTO `CurrentQuotaData` doit être enrichi pour que le contrat backend indique l'unité utilisée.

Additif attendu:

- `quota_key: str`

Pour un plan tokenisé, `current_quota` retourne par exemple:

```json
{
  "feature_code": "astrologer_chat",
  "quota_key": "tokens",
  "quota_limit": 50000,
  "consumed": 12450,
  "remaining": 37550,
  "period_unit": "month"
}
```

Important:

- aujourd'hui `CurrentQuotaData` n'expose pas `quota_key`;
- cette story doit donc **ajouter** ce champ au contrat, pas seulement "mettre à jour" un champ existant.

### AC8 - Frontend: affichage en tokens avec delta minimal

Le frontend continue à consommer `subscription.current_quota`, sans nouvelle source.

Changements attendus:

- `SubscriptionSettings.tsx` affiche l'unité `tokens` au lieu de `msg`
- les libellés i18n existants sont mis à jour avec le plus petit delta cohérent
- pas de style inline

Cette story n'impose pas la refonte du tab "usage" si celui-ci n'est pas encore branché sur l'API de billing token.

### AC9 - Préservation du comportement upgrade basic -> premium pour `astrologer_chat`

La non-régression d'upgrade en cours de période reste requise pour la feature billing principale exposée dans `current_quota`, soit `astrologer_chat`.

Invariants:

- même `feature_code`
- même `quota_key="tokens"`
- même `period_unit="month"`
- même `period_value=1`
- même `reset_mode="calendar"`

Conséquence:

- le compteur courant `FeatureUsageCounterModel` de `astrologer_chat` reste partagé lors d'un upgrade basic -> premium intra-mois;
- `remaining = max(0, premium_limit - tokens_deja_consomes)`.

Cette AC ne s'applique pas à `thematic_consultation`, dont la période cible peut rester différente.

### AC10 - Tests

Tests minimum à couvrir:

- unit: `QuotaUsageService.consume(amount=N)` avec `N > 1`
- unit: nouveau service de débit tokenisé crée le compteur et le log dans la même transaction
- unit: fallback d'estimation de tokens
- unit: gates refactorés n'incrémentent plus le compteur pendant le pré-check seul
- integration: `POST /v1/chat/messages` débite des tokens et non plus `1`
- integration: `POST /v1/consultations/generate` débite des tokens et non plus `1`
- integration: `GET /v1/billing/token-usage`
- integration: `GET /v1/billing/subscription` retourne `current_quota.quota_key == "tokens"`
- non-régression: upgrade basic -> premium sur `astrologer_chat` conserve le compteur intra-mois
- mise à jour des tests existants qui assertent `messages` / `consultations`

---

## Tasks / Subtasks

- [ ] **T1 - Créer `UserTokenUsageLogModel` et sa migration** (AC: 1)
  - [ ] Ajouter `backend/app/infra/db/models/token_usage_log.py`
  - [ ] Exporter le modèle dans `backend/app/infra/db/models/__init__.py`
  - [ ] Créer la migration Alembic dédiée

- [ ] **T2 - Mettre à jour le catalogue canonique** (AC: 2)
  - [ ] Remplacer les quotas `messages` / `consultations` par `tokens` dans `backend/scripts/seed_product_entitlements.py`
  - [ ] Mettre à jour les tests du mutation service et des seeds

- [ ] **T3 - Refactorer le flux d'entitlement B2C pour les features tokenisées** (AC: 3)
  - [ ] Introduire un pré-check sans consommation pour `astrologer_chat`
  - [ ] Introduire un pré-check sans consommation pour `thematic_consultation`
  - [ ] Mettre à jour les routeurs `chat.py` et `consultations.py`

- [ ] **T4 - Propager les usages tokens depuis le runtime LLM** (AC: 4)
  - [ ] Chat: faire remonter texte + modèle + tokens normalisés jusqu'au routeur
  - [ ] Consultation: conserver et exploiter `GatewayResult.usage`
  - [ ] Ajouter le fallback d'estimation si l'usage est absent

- [ ] **T5 - Implémenter le service de débit tokenisé** (AC: 5)
  - [ ] Créer `backend/app/services/llm_token_usage_service.py`
  - [ ] Garantir atomicité compteur + log utilisateur

- [ ] **T6 - Ajouter l'API `GET /v1/billing/token-usage`** (AC: 6)
  - [ ] Ajouter le routeur / schéma de réponse
  - [ ] Agréger `user_token_usage_logs` par période et par feature

- [ ] **T7 - Enrichir `CurrentQuotaData`** (AC: 7)
  - [ ] Ajouter `quota_key` au DTO backend
  - [ ] Vérifier `_resolve_current_quota()` et les tests associés

- [ ] **T8 - Mettre à jour le frontend** (AC: 8)
  - [ ] Ajuster les labels i18n existants
  - [ ] Mettre à jour `SubscriptionSettings.tsx`

- [ ] **T9 - Compléter la couverture de tests** (AC: 10)
  - [ ] Backend unit + integration
  - [ ] Frontend si l'affichage change

---

## Dev Notes

### Point de correction majeur par rapport à la version initiale de la story

La version précédente de la story était incomplète sur un point critique:

- elle supposait qu'il suffisait de remplacer `consume(amount=1)` par `consume(amount=tokens_total)`;
- en réalité, le débit a lieu aujourd'hui **avant** l'appel LLM dans les entitlement gates;
- la story doit donc obligatoirement inclure la dissociation **pré-check** / **débit post-réponse**.

Sans cette refactorisation de flux, la story n'était pas implémentable proprement.

### Atomicité attendue

Le log utilisateur facturable n'est pas un log best-effort.

Règle:

- `FeatureUsageCounterModel` et `UserTokenUsageLogModel` doivent être cohérents transactionnellement.
- En revanche, le lien vers `LlmCallLogModel` peut rester optionnel.

### Sur les anciens compteurs

Le passage de `messages` / `consultations` vers `tokens` crée de nouvelles clés de compteur.

Conséquences acceptées:

- les anciens compteurs restent en base pour audit;
- ils ne doivent plus être utilisés pour l'enforcement des features migrées;
- aucune suppression destructive n'est requise.

### Fichiers probablement impactés

- `backend/scripts/seed_product_entitlements.py`
- `backend/app/services/chat_entitlement_gate.py`
- `backend/app/services/thematic_consultation_entitlement_gate.py`
- `backend/app/api/v1/routers/chat.py`
- `backend/app/api/v1/routers/consultations.py`
- `backend/app/api/v1/routers/billing.py`
- `backend/app/services/billing_service.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/app/services/chat_guidance_service.py`
- `backend/app/services/consultation_generation_service.py`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/i18n/settings.ts`

---

## Review Notes

Corrections apportées à la story d'origine:

- suppression de l'hypothèse fausse "remplacer juste `amount=1`"
- suppression de la contradiction entre AC "month partagé" et tableau de quotas
- suppression de la mention `natal_chart_long if applicable`, hors scope ici
- correction du contrat `current_quota`: `quota_key` n'existe pas aujourd'hui et doit être ajouté explicitement
- correction du modèle de logging: journal utilisateur facturable atomique, pas best-effort
- clarification du vrai point d'intégration: propagation des tokens depuis le Gateway jusqu'aux routeurs métier
