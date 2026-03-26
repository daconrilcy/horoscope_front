# Story 61.11 : Migration du flux métier astrologer_chat vers les entitlements canoniques

Status: done

## Story

En tant qu'utilisateur B2C authentifié,
je veux que mon accès au chat astrologue soit gouverné par le moteur d'entitlements canonique,
de sorte que mon quota soit réellement consommé, que les refus soient clairs et que le front puisse afficher mon état de quota.

## Acceptance Criteria

1. Un message chat est refusé (HTTP 403) si `final_access=False` avec `reason` parmi : `no_plan`, `billing_inactive`, `canonical_no_binding`, `feature_unknown`
2. Un message chat est refusé (HTTP 403) si un binding canonique existe pour `astrologer_chat` mais est désactivé (`access_mode="disabled"` ou `is_enabled_by_plan=False`) — le `reason` retourné est `"disabled_by_plan"`
3. Un message chat est refusé (HTTP 429) si `final_access=False` avec `quota_exhausted=True` — le chemin canonique quota a épuisé tous ses compteurs
4. Un message chat sur chemin `legacy_fallback` est immédiatement délégué à `QuotaService` — **la gate ne tient pas compte de `final_access` dans ce cas** ; le contrôle réel reste celui de `QuotaService`
5. Un message chat sur chemin canonique `access_mode=quota` consomme exactement 1 unité dans `feature_usage_counters` avant d'appeler `ChatGuidanceService`
6. Un message chat sur chemin canonique `access_mode=unlimited` n'effectue aucune consommation dans `feature_usage_counters`
7. La consommation canonique a lieu une seule fois par message accepté — elle est faite avant l'appel LLM ; aucun mécanisme de remboursement automatique n'est implémenté dans cette story
8. En cas d'exception `ChatQuotaExceededError` ou `ChatAccessDeniedError`, le routeur appelle `db.rollback()` — aucune consommation partielle ne persiste en base
9. La réponse du endpoint `POST /v1/chat/messages` inclut un objet `quota_info` avec les champs `remaining`, `limit`, `window_end` (null si unlimited ou legacy)
10. Les tests d'intégration existants du chat continuent de passer ; les attentes sont alignées sur les nouveaux codes d'erreur canoniques quand le contrat API change
11. `QuotaService.consume_quota_or_raise()` reste utilisé exclusivement sur le chemin `legacy_fallback`

## Tasks / Subtasks

- [x] **Créer `ChatEntitlementGate`** dans `backend/app/services/chat_entitlement_gate.py` (AC: 1, 2, 3, 4, 5, 6)
  - [x] Définir `FEATURE_CODE = "astrologer_chat"` comme constante de classe
  - [x] Définir `ChatAccessDeniedError(Exception)` avec attributs `reason: str`, `billing_status: str`, `plan_code: str`
  - [x] Définir `ChatQuotaExceededError(Exception)` avec attributs `quota_key: str`, `used: int`, `limit: int`, `window_end: datetime | None`
  - [x] Définir `ChatEntitlementResult` dataclass with : `path: str` (`"canonical_quota"` | `"canonical_unlimited"` | `"legacy"`), `usage_states: list[UsageState]`
  - [x] Implémenter `check_and_consume(db, *, user_id) → ChatEntitlementResult` (méthode statique) — **respecter cet ordre strict** :
    - [x] Appeler `EntitlementService.get_feature_entitlement(db, user_id=user_id, feature_code=FEATURE_CODE)`
    - [x] **En premier** : si `entitlement.reason == "legacy_fallback"` → retourner immédiatement `ChatEntitlementResult(path="legacy", usage_states=[])` sans vérifier `final_access` (AC: 4)
    - [x] Si `entitlement.final_access=False` et `entitlement.quota_exhausted=True` → lever `ChatQuotaExceededError` avec infos du premier quota épuisé dans `usage_states` (AC: 3)
    - [x] Si `entitlement.final_access=False` → lever `ChatAccessDeniedError(reason=entitlement.reason, ...)` (AC: 1, 2)
    - [x] Si `entitlement.access_mode == "unlimited"` → retourner `ChatEntitlementResult(path="canonical_unlimited", usage_states=entitlement.usage_states)` (AC: 6)
    - [x] Si `entitlement.access_mode == "quota"` → pour chaque quota dans `entitlement.quotas` : appeler `QuotaUsageService.consume(db, user_id=user_id, feature_code=FEATURE_CODE, quota=quota, amount=1)` ; propager `QuotaExhaustedError` comme `ChatQuotaExceededError` (AC: 5)
    - [x] Retourner `ChatEntitlementResult(path="canonical_quota", usage_states=[...states post-consommation])`

- [x] **Modifier `backend/app/api/v1/routers/chat.py`** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] Importer `ChatEntitlementGate`, `ChatAccessDeniedError`, `ChatQuotaExceededError` depuis `app.services.chat_entitlement_gate`
  - [x] Ajouter `QuotaInfo` Pydantic model : `remaining: int | None`, `limit: int | None`, `window_end: datetime | None`
  - [x] Modifier `ChatMessageApiResponse` pour inclure `quota_info: QuotaInfo | None = None`
  - [x] Dans `send_chat_message`, **remplacer** `QuotaService.consume_quota_or_raise(...)` par :
    ```python
    entitlement_result = ChatEntitlementGate.check_and_consume(db, user_id=current_user.id)
    if entitlement_result.path == "legacy":
        QuotaService.consume_quota_or_raise(db, user_id=current_user.id, request_id=request_id)
    ```
  - [x] Construire `quota_info` à partir de `entitlement_result.usage_states` : si `usage_states` non vide, prendre le premier état ; sinon `QuotaInfo(remaining=None, limit=None, window_end=None)`
  - [x] Gérer `ChatAccessDeniedError` → HTTP 403 avec code `"chat_access_denied"`, `reason` dans `details`
  - [x] Gérer `ChatQuotaExceededError` → HTTP 429 avec code `"chat_quota_exceeded"`, `quota_key / used / limit / window_end` dans `details`
  - [x] Inclure `quota_info` dans la réponse de succès : `{"data": {..., "quota_info": quota_info.model_dump(mode="json")}, "meta": ...}`

- [x] **Tests unitaires `ChatEntitlementGate`** dans `backend/app/tests/unit/test_chat_entitlement_gate.py` (AC: 1, 2, 3, 4, 5, 6)
  - [x] `test_canonical_quota_path_consumes` : binding quota canonique, used=2/5 → `path="canonical_quota"`, `consume()` appelé 1 fois, `usage_states[0].used=3`
  - [x] `test_canonical_unlimited_path_no_consume` : binding unlimited → `path="canonical_unlimited"`, `consume()` non appelé
  - [x] `test_legacy_fallback_returns_legacy_path` : `reason="legacy_fallback"` → `path="legacy"`, `consume()` non appelé
  - [x] `test_access_denied_no_plan` : `final_access=False, reason="no_plan"` → `ChatAccessDeniedError`
  - [x] `test_access_denied_billing_inactive` : `final_access=False, reason="billing_inactive"` → `ChatAccessDeniedError`
  - [x] `test_canonical_disabled_binding_rejected_403` : `final_access=False, reason="disabled_by_plan"` → `ChatAccessDeniedError` avec `reason="disabled_by_plan"`
  - [x] `test_quota_exceeded_raises_chat_error` : quota épuisé → `ChatQuotaExceededError` avec bons attributs
  - [x] `test_consume_called_once_per_quota` : entitlement avec 2 quotas → `consume()` appelé 2 fois
  - [x] `test_legacy_fallback_final_access_false_still_delegates` : `reason="legacy_fallback"`, `final_access=False` (quota legacy épuisé) → `path="legacy"` retourné sans exception — la gate ne bloque PAS sur `final_access` pour ce chemin
  - [x] Utiliser des mocks pour `EntitlementService.get_feature_entitlement` et `QuotaUsageService.consume` — PAS de vraie DB

- [x] **Tests d'intégration endpoint chat** dans `backend/app/tests/integration/test_chat_entitlement.py` (AC: 1, 2, 3, 4, 5, 7, 8)
  - [x] `test_send_message_canonical_quota_ok` : user with binding quota canonique, message envoyé → 200, `quota_info.remaining < quota_info.limit`
  - [x] `test_send_message_canonical_unlimited_ok` : user with binding unlimited → 200, `quota_info.remaining=None`
  - [x] `test_send_message_no_plan_rejected` : user without plan → 403, `code="chat_access_denied"`
  - [x] `test_send_message_quota_exhausted_rejected` : counter exhausted → 429, `code="chat_quota_exceeded"`, `details.window_end` present
  - [x] `test_send_message_legacy_fallback_still_works` : user without canonical binding → 200 (legacy QuotaService active), behavior unchanged
  - [x] `test_send_chat_message_disabled_canonical_binding_returns_disabled_by_plan` : binding canonique désactivé → 403, `details.reason="disabled_by_plan"`
  - [x] `test_send_chat_message_rolls_back_partial_canonical_consumption` : consommation partielle simulée sur chemin canonique → 429 et compteur rollback à `used_count=0`

- [x] **Non-régression** (AC: 10, 11)
  - [x] `pytest backend/app/tests/integration/test_chat_api.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_chat_multi_persona.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_chat_idempotence.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_entitlement_service.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_quota_usage_service.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_quota_service.py` — tous verts

---

## Dev Notes

### Architecture Guardrails

- **Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0 (`Mapped` / `mapped_column`), Pydantic v2
- **Pattern service** : classe statique `@staticmethod`, PascalCase — conforme à `EntitlementService`, `QuotaUsageService`
- **Session DB** : `Session` depuis `sqlalchemy.orm` — PAS de session async
- **Aucune migration DB** : `feature_usage_counters` existe depuis 61-7, aucune nouvelle table

### Localisation des fichiers

```
backend/app/services/chat_entitlement_gate.py        ← NOUVEAU
backend/app/api/v1/routers/chat.py                   ← MODIFIÉ (imports + logique gate + response)
backend/app/tests/unit/test_chat_entitlement_gate.py ← NOUVEAU
backend/app/tests/integration/test_chat_entitlement.py ← NOUVEAU
```

### Stratégie transitoire — règle fondamentale

**Ne consommer canoniquement QUE sur le chemin canonique.**

**L'ordre de test dans `check_and_consume` est impératif** — le `legacy_fallback` est évalué EN PREMIER, avant tout contrôle de `final_access`.

| Priorité | `reason` retourné | `access_mode` | `final_access` | Action |
|----------|-------------------|---------------|----------------|--------|
| 1 (premier) | `"legacy_fallback"` | — | **peu importe** | Déléguer à `QuotaService` — la gate retourne `path="legacy"` sans exception |
| 2 | `"no_plan"` | — | False | Refus 403 `chat_access_denied` |
| 2 | `"billing_inactive"` | — | False | Refus 403 `chat_access_denied` |
| 2 | `"canonical_no_binding"` | — | False | Refus 403 `chat_access_denied` |
| 2 | `"feature_unknown"` | — | False | Refus 403 `chat_access_denied` |
| 2 | `"disabled_by_plan"` | `"disabled"` | False | Refus 403 `chat_access_denied` |
| 2 | `"canonical_binding"` | `"quota"` | False (`quota_exhausted=True`) | Refus 429 `chat_quota_exceeded` |
| 3 | `"canonical_binding"` | `"quota"` | True | Consume + 200 |
| 3 | `"canonical_binding"` | `"unlimited"` | True | Pas de consume + 200 |

Le fallback legacy reste en **lecture seule du point de vue canonique** — `QuotaUsageService` n'est PAS appelé sur ce chemin.

### Politique de consommation et rollback transactionnel

- La consommation a lieu **avant** l'appel à `ChatGuidanceService.send_message()`
- Si le message est accepté et que le LLM tombe en panne **après** la consommation, la consommation est **conservée** (pas de remboursement dans 61-11)
- Si la validation de la payload échoue **avant** la gate → aucune consommation (l'exception `ValidationError` est levée avant)
- Un seul appel `consume(amount=1)` par quota dans `entitlement.quotas`
- **Consommation partielle** : si `entitlement.quotas` contient plusieurs quotas et que le second `consume()` lève `QuotaExhaustedError`, le routeur appelle `db.rollback()` dans le handler `ChatQuotaExceededError`, ce qui annule aussi la consommation du premier quota — garanti par la transaction SQLAlchemy en cours
- **Règle générale** : tout handler `except` qui retourne une erreur HTTP doit appeler `db.rollback()` avant de retourner la `JSONResponse`

### Imports dans `chat_entitlement_gate.py`

```python
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import UsageState
from app.services.quota_usage_service import QuotaUsageService, QuotaExhaustedError
```

Pas d'import circulaire : `ChatEntitlementGate` ne fait PAS partie du cycle `entitlement_types ↔ entitlement_service ↔ quota_usage_service`.

### Structure `ChatEntitlementGate` — squelette de référence

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import UsageState
from app.services.quota_usage_service import QuotaUsageService, QuotaExhaustedError


class ChatAccessDeniedError(Exception):
    def __init__(self, reason: str, billing_status: str, plan_code: str) -> None:
        self.reason = reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        super().__init__(f"Chat access denied: {reason}")


class ChatQuotaExceededError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, window_end: datetime | None) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end
        super().__init__(f"Chat quota '{quota_key}' exceeded: {used}/{limit}")


@dataclass
class ChatEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited" | "legacy"
    usage_states: list[UsageState] = field(default_factory=list)


class ChatEntitlementGate:
    FEATURE_CODE = "astrologer_chat"

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> ChatEntitlementResult:
        entitlement = EntitlementService.get_feature_entitlement(
            db, user_id=user_id, feature_code=ChatEntitlementGate.FEATURE_CODE
        )

        # PRIORITÉ 1 : legacy_fallback — déléguer immédiatement, final_access ignoré
        if entitlement.reason == "legacy_fallback":
            return ChatEntitlementResult(path="legacy", usage_states=[])

        # PRIORITÉ 2 : refus canoniques
        if not entitlement.final_access:
            if entitlement.quota_exhausted and entitlement.usage_states:
                exhausted_state = next(s for s in entitlement.usage_states if s.exhausted)
                raise ChatQuotaExceededError(
                    quota_key=exhausted_state.quota_key,
                    used=exhausted_state.used,
                    limit=exhausted_state.quota_limit,
                    window_end=exhausted_state.window_end,
                )
            raise ChatAccessDeniedError(
                reason=entitlement.reason,
                billing_status=entitlement.billing_status,
                plan_code=entitlement.plan_code,
            )

        if entitlement.access_mode == "unlimited":
            return ChatEntitlementResult(path="canonical_unlimited", usage_states=entitlement.usage_states)

        # access_mode == "quota" — consommer
        consumed_states: list[UsageState] = []
        for quota in entitlement.quotas:
            try:
                state = QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code=ChatEntitlementGate.FEATURE_CODE,
                    quota=quota,
                    amount=1,
                )
                consumed_states.append(state)
            except QuotaExhaustedError as exc:
                raise ChatQuotaExceededError(
                    quota_key=exc.quota_key,
                    used=exc.used,
                    limit=exc.limit,
                    window_end=None,  # récupérer depuis usage_states si besoin
                ) from exc

        return ChatEntitlementResult(path="canonical_quota", usage_states=consumed_states)
```

### Enrichissement de la réponse — `QuotaInfo`

Ajouter dans `chat.py` (dans le router, pas dans le service) :

```python
class QuotaInfo(BaseModel):
    remaining: int | None = None
    limit: int | None = None
    window_end: datetime | None = None
```

Construction à partir du résultat de la gate :

```python
def _build_quota_info(result: ChatEntitlementResult) -> QuotaInfo:
    if result.path in ("canonical_quota", "canonical_unlimited") and result.usage_states:
        state = result.usage_states[0]
        return QuotaInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,
        )
    return QuotaInfo()  # tous None → chemin legacy ou unlimited sans states
```

Modifier `ChatMessageApiResponse` :

```python
class ChatMessageApiResponse(BaseModel):
    data: ChatReplyData
    meta: ResponseMeta
    quota_info: QuotaInfo = Field(default_factory=QuotaInfo)
```

La réponse de succès devient :

```python
return {
    "data": response.model_dump(mode="json"),
    "meta": {"request_id": request_id},
    "quota_info": quota_info.model_dump(mode="json"),
}
```

### Gestion des erreurs dans `send_chat_message`

Insérer les nouveaux handlers **avant** `QuotaServiceError` (qui reste pour le chemin legacy) :

```python
except ChatQuotaExceededError as error:
    db.rollback()
    return JSONResponse(
        status_code=429,
        content={"error": {
            "code": "chat_quota_exceeded",
            "message": "quota de messages chat épuisé",
            "details": {
                "quota_key": error.quota_key,
                "used": error.used,
                "limit": error.limit,
                "window_end": error.window_end.isoformat() if error.window_end else None,
            },
            "request_id": request_id,
        }},
    )
except ChatAccessDeniedError as error:
    db.rollback()
    return JSONResponse(
        status_code=403,
        content={"error": {
            "code": "chat_access_denied",
            "message": "accès au chat refusé",
            "details": {"reason": error.reason, "billing_status": error.billing_status},
            "request_id": request_id,
        }},
    )
```

### Point critique : ordre de gestion des erreurs

L'ordre dans le `try/except` de `send_chat_message` doit être :

1. `ValidationError` (payload invalide)
2. `ChatQuotaExceededError` (quota canonique épuisé → 429)
3. `ChatAccessDeniedError` (accès refusé → 403)
4. `QuotaServiceError` (quota legacy → 429/403 existant)
5. `ChatGuidanceServiceError` (erreur LLM → 503/404/403)

### Éviter les régressions critiques

- **Ne pas supprimer `QuotaService`** de `chat.py` — il reste actif sur le chemin `legacy_fallback`
- **Ne pas modifier `ChatGuidanceService`** — aucun changement dans ce service
- **Ne pas modifier `ChatReplyData`** — l'enrichissement quota est dans la réponse API, pas dans le data object
- **Ne pas appeler `EntitlementService` depuis `ChatGuidanceService`** — la gate est dans le router
- **`QuotaService` et `ChatEntitlementGate` sont mutuellement exclusifs** — jamais tous les deux sur le même chemin

### Pattern de test unitaire avec mocks

```python
# test_chat_entitlement_gate.py
from unittest.mock import patch, MagicMock
from app.services.chat_entitlement_gate import ChatEntitlementGate, ChatAccessDeniedError, ChatQuotaExceededError
from app.services.entitlement_types import FeatureEntitlement, QuotaDefinition, UsageState

def make_entitlement(**kwargs) -> FeatureEntitlement:
    defaults = dict(
        plan_code="essai", billing_status="active",
        is_enabled_by_plan=True, access_mode="quota",
        variant_code=None, quotas=[], final_access=True,
        reason="canonical_binding", usage_states=[], quota_exhausted=False,
    )
    return FeatureEntitlement(**{**defaults, **kwargs})

def test_canonical_quota_path_consumes(db_session):
    quota = QuotaDefinition(quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar")
    entitlement = make_entitlement(access_mode="quota", quotas=[quota])

    with patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement), \
         patch.object(QuotaUsageService, "consume", return_value=MagicMock(used=3, remaining=2)) as mock_consume:
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_quota"
    mock_consume.assert_called_once_with(db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=1)
```

### Prérequis 61-10 — contrat déjà publié

61-11 dépend directement des livrables de 61-10. **Ces champs existent déjà en production** dans `app.services.entitlement_types` :

```python
# app/services/entitlement_types.py — livré en 61-10
@dataclass
class FeatureEntitlement:
    ...
    usage_states: list[UsageState] = field(default_factory=list)  # ← présent
    quota_exhausted: bool = False                                   # ← présent

@dataclass(frozen=True)
class UsageState:
    feature_code: str
    quota_key: str
    quota_limit: int
    used: int
    remaining: int
    exhausted: bool
    period_unit: str
    period_value: int
    reset_mode: str
    window_start: datetime
    window_end: datetime | None  # None si reset_mode="lifetime"
```

Ne pas les recréer — ils existent. `QuotaExhaustedError` est dans `app.services.quota_usage_service`.

### Intelligence de la story 61-10

- `UsageState` est importé depuis `app.services.entitlement_types` (pas depuis `quota_usage_service`)
- `QuotaExhaustedError` est dans `app.services.quota_usage_service`
- `QuotaDefinition` est dans `app.services.entitlement_types`
- Les tests unitaires de services utilisent SQLite in-memory avec `Base.metadata.create_all(engine)`
- `db.flush()` (pas `db.commit()`) dans les services — le commit est dans le routeur

### Périmètre strict de 61-11

**Inclus** :
- `astrologer_chat` uniquement
- Chemin canonique quota et unlimited
- Chemin legacy (délégation sans modification)
- Exposition de `quota_info` dans la réponse API

**Exclus** :
- `thematic_consultation`
- `natal_chart_long`
- `B2BUsageService`
- Mécanisme de remboursement automatique
- Nouveaux endpoints de quota
- Modification de la logique de billing

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fixed `ResponseValidationError` in integration tests by providing complete `ChatReplyData` mock.
- Updated `test_chat_api.py` to expect `chat_access_denied` instead of `no_active_subscription` as per the new ACs.
- Code review follow-up: fixed canonical disabled binding reason to `disabled_by_plan`.
- Code review follow-up: added real integration coverage for canonical disabled binding and rollback of partial canonical consumption.

### Completion Notes List

- Implemented `ChatEntitlementGate` with strict priority rules.
- Integrated the gate in `chat.py` router.
- Added `quota_info` to `ChatMessageApiResponse`.
- Verified all canonical and legacy paths via unit and integration tests.
- Fixed `EntitlementService` to emit `disabled_by_plan` when a canonical binding exists but is not enabled.
- Added integration coverage on the real API flow for `disabled_by_plan` and canonical rollback behavior.
- All targeted backend tests passing after review fixes.

### File List

- `backend/app/services/chat_entitlement_gate.py`
- `backend/app/api/v1/routers/chat.py`
- `backend/app/tests/unit/test_chat_entitlement_gate.py`
- `backend/app/tests/integration/test_chat_entitlement.py`
- `backend/app/tests/integration/test_chat_api.py`
- `backend/app/tests/unit/test_entitlement_service.py`
