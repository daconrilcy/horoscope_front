# Story 61.12 : Migration du flux métier thematic_consultation vers les entitlements canoniques

Status: done

## Story

En tant qu'utilisateur B2C authentifié,
je veux que mon accès aux consultations thématiques soit gouverné exclusivement par le moteur d'entitlements canonique,
de sorte que mon quota soit réellement consommé, que les refus soient clairs et que le front puisse afficher mon état de quota restant.

## Acceptance Criteria

1. Une consultation est refusée (HTTP 403) si `final_access=False` avec `reason` parmi : `no_plan`, `billing_inactive`, `canonical_no_binding`, `feature_unknown`
2. Une consultation est refusée (HTTP 403) si un binding canonique existe pour `thematic_consultation` mais est désactivé (`access_mode="disabled"` ou `is_enabled_by_plan=False`) — le `reason` retourné est `"disabled_by_plan"`
3. Une consultation est refusée (HTTP 429) si `final_access=False` avec `quota_exhausted=True` — le quota canonique a épuisé ses compteurs
4. Un chemin canonique `access_mode=quota` consomme exactement 1 unité dans `feature_usage_counters` avant d'appeler `ConsultationGenerationService.generate()`
5. Un chemin canonique `access_mode=unlimited` n'effectue aucune consommation dans `feature_usage_counters`
6. Aucun appel à `QuotaService` legacy n'est effectué — cette feature est gouvernée uniquement par le canonique
7. La réponse du endpoint `POST /v1/consultations/generate` inclut un objet `quota_info` avec les champs `remaining`, `limit`, `window_end` (null si unlimited ou absent)
8. En cas d'exception `ConsultationQuotaExceededError` ou `ConsultationAccessDeniedError`, le routeur appelle `db.rollback()` avant de retourner la `JSONResponse`
9. Les tests existants de `test_consultations_router.py` continuent de passer
10. Les tests d'intégration couvrent explicitement les fenêtres `1/week` (trial/basic) et `2/day` (premium) :
    - deux consultations premium le même jour passent ; la troisième est refusée (429)
    - une consultation basic dans la même semaine refuse la deuxième (429)
11. Si aucun binding canonique n'existe pour `thematic_consultation` → refus 403 avec `reason="canonical_no_binding"` (pas de fallback legacy inventé)

## Tasks / Subtasks

- [x] **Créer `ThematicConsultationEntitlementGate`** dans `backend/app/services/thematic_consultation_entitlement_gate.py` (AC: 1, 2, 3, 4, 5, 6)
  - [x] Définir `FEATURE_CODE = "thematic_consultation"` comme constante de classe
  - [x] Définir `ConsultationAccessDeniedError(Exception)` avec attributs `reason: str`, `billing_status: str`, `plan_code: str`
  - [x] Définir `ConsultationQuotaExceededError(Exception)` avec attributs `quota_key: str`, `used: int`, `limit: int`, `window_end: datetime | None`
  - [x] Définir `ConsultationEntitlementResult` dataclass avec : `path: str` (`"canonical_quota"` | `"canonical_unlimited"`), `usage_states: list[UsageState]`
  - [x] Implémenter `check_and_consume(db, *, user_id) → ConsultationEntitlementResult` (méthode statique) — **respecter cet ordre strict** :
    - [x] Appeler `EntitlementService.get_feature_entitlement(db, user_id=user_id, feature_code=FEATURE_CODE)`
    - [x] **Pas de chemin legacy_fallback** — si `entitlement.reason == "legacy_fallback"` → lever `ConsultationAccessDeniedError(reason="canonical_no_binding", ...)` (AC: 11)
    - [x] Si `entitlement.final_access=False` et `entitlement.quota_exhausted=True` → lever `ConsultationQuotaExceededError` avec infos du premier quota épuisé dans `usage_states` (AC: 3)
    - [x] Si `entitlement.final_access=False` → lever `ConsultationAccessDeniedError(reason=entitlement.reason, ...)` (AC: 1, 2)
    - [x] Si `entitlement.access_mode == "unlimited"` → retourner `ConsultationEntitlementResult(path="canonical_unlimited", usage_states=entitlement.usage_states)` (AC: 5)
    - [x] Si `entitlement.access_mode == "quota"` → pour chaque quota dans `entitlement.quotas` : appeler `QuotaUsageService.consume(db, user_id=user_id, feature_code=FEATURE_CODE, quota=quota, amount=1)` ; propager `QuotaExhaustedError` comme `ConsultationQuotaExceededError` avec `window_end` récupéré depuis `entitlement.usage_states` (AC: 4)
    - [x] Retourner `ConsultationEntitlementResult(path="canonical_quota", usage_states=[...states post-consommation])`

- [x] **Modifier `backend/app/api/v1/schemas/consultation.py`** (AC: 7)
  - [x] Ajouter `ConsultationQuotaInfo` Pydantic model : `remaining: int | None = None`, `limit: int | None = None`, `window_end: datetime | None = None`
  - [x] Ajouter `quota_info: ConsultationQuotaInfo = Field(default_factory=ConsultationQuotaInfo)` à `ConsultationGenerateResponse`
  - [x] Importer `datetime` depuis `datetime` si non présent

- [x] **Modifier `backend/app/api/v1/routers/consultations.py`** (AC: 1, 2, 3, 4, 5, 7, 8)
  - [x] Importer `ThematicConsultationEntitlementGate`, `ConsultationAccessDeniedError`, `ConsultationQuotaExceededError`, `ConsultationEntitlementResult` depuis `app.services.thematic_consultation_entitlement_gate`
  - [x] Importer `JSONResponse` depuis `fastapi.responses`
  - [x] Importer `ConsultationQuotaInfo` depuis les schémas
  - [x] Ajouter helper `_build_consultation_quota_info(result: ConsultationEntitlementResult) -> ConsultationQuotaInfo`
  - [x] Dans `generate_consultation`, **avant** l'appel à `ConsultationGenerationService.generate()` :
    - Appeler `ThematicConsultationEntitlementGate.check_and_consume(db, user_id=current_user.id)`
    - Construire `quota_info` depuis le résultat
    - Gérer `ConsultationQuotaExceededError` → HTTP 429 avec `db.rollback()`
    - Gérer `ConsultationAccessDeniedError` → HTTP 403 avec `db.rollback()`
  - [x] Modifier `ConsultationGenerateResponse(...)` pour inclure `quota_info=quota_info`
  - [x] **Conserver** `response_model=ConsultationGenerateResponse` sur le décorateur `@router.post("/generate")` — FastAPI permet de retourner des `JSONResponse` d'erreur custom même avec un `response_model`. Ajouter `responses={403: {"description": "Accès refusé"}, 429: {"description": "Quota épuisé"}}` pour documenter les codes d'erreur dans l'OpenAPI.

- [x] **Tests unitaires `ThematicConsultationEntitlementGate`** dans `backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py` (AC: 1, 2, 3, 4, 5, 6, 11)
  - [x] `test_canonical_quota_path_consumes` : binding quota canonique, used=0/1 → `path="canonical_quota"`, `consume()` appelé 1 fois
  - [x] `test_canonical_unlimited_path_no_consume` : binding unlimited → `path="canonical_unlimited"`, `consume()` non appelé
  - [x] `test_legacy_fallback_treated_as_no_binding` : `reason="legacy_fallback"` → `ConsultationAccessDeniedError` levée (AC: 11)
  - [x] `test_access_denied_no_plan` : `final_access=False, reason="no_plan"` → `ConsultationAccessDeniedError`
  - [x] `test_access_denied_billing_inactive` : `final_access=False, reason="billing_inactive"` → `ConsultationAccessDeniedError`
  - [x] `test_canonical_disabled_binding_rejected_403` : `final_access=False, reason="disabled_by_plan"` → `ConsultationAccessDeniedError` avec `reason="disabled_by_plan"`
  - [x] `test_quota_exceeded_raises_consultation_error` : quota épuisé → `ConsultationQuotaExceededError` avec bons attributs
  - [x] `test_no_legacy_quota_service_called` : vérifier qu'aucun appel à `QuotaService` n'est fait dans la gate
  - [x] Utiliser des mocks pour `EntitlementService.get_feature_entitlement` et `QuotaUsageService.consume` — PAS de vraie DB

- [x] **Tests d'intégration endpoint `/v1/consultations/generate`** dans `backend/app/tests/integration/test_thematic_consultation_entitlement.py` (AC: 1, 2, 3, 4, 7, 8, 10, 11)
  - [x] `test_generate_canonical_quota_ok` : binding quota 1/week → 200, `quota_info.remaining=0`, `quota_info.limit=1`
  - [x] `test_generate_canonical_unlimited_ok` : binding unlimited → 200, `quota_info.remaining=None`
  - [x] `test_generate_no_plan_rejected` : user sans plan → 403, `code="consultation_access_denied"`
  - [x] `test_generate_quota_exhausted_rejected` : compteur épuisé → 429, `code="consultation_quota_exceeded"`, `details.window_end` present
  - [x] `test_generate_disabled_binding_returns_disabled_by_plan` : binding désactivé → 403, `details.reason="disabled_by_plan"`
  - [x] `test_generate_no_canonical_binding_returns_no_binding` : `reason="canonical_no_binding"` ou `"legacy_fallback"` → 403 (AC: 11)
  - [x] `test_generate_rolls_back_partial_canonical_consumption` : consommation partielle simulée → 429 et rollback
  - [x] `test_premium_quota_2_per_day` : user premium, 2 consultations ok, 3ème refusée en 429 (AC: 10) — **patcher `datetime.now(timezone.utc)` pour figer la date dans la même journée UTC** (éviter les tests fragiles aux changements de jour)
  - [x] `test_basic_quota_1_per_week` : user basic, 1ère ok, 2ème refusée en 429 dans la même semaine (AC: 10) — **patcher `datetime.now(timezone.utc)` pour figer la date dans la même semaine calendaire ISO**

- [x] **Non-régression** (AC: 9)
  - [x] `pytest backend/app/tests/integration/test_consultations_router.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_consultation_catalogue.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_consultation_third_party.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_entitlement_service.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_quota_usage_service.py` — tous verts

---

## Dev Notes

### Architecture Guardrails

- **Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0 (`Mapped` / `mapped_column`), Pydantic v2
- **Pattern service** : classe statique `@staticmethod`, PascalCase — conforme à `ChatEntitlementGate`, `EntitlementService`, `QuotaUsageService`
- **Session DB** : `Session` depuis `sqlalchemy.orm` — PAS de session async
- **Aucune migration DB** : `feature_usage_counters` existe depuis 61-7, aucune nouvelle table

### Données canoniques thematic_consultation (seed existant)

**Source** : `backend/scripts/seed_product_entitlements.py`

| Plan | access_mode | quota_key | limit | fenêtre |
|------|-------------|-----------|-------|---------|
| free | disabled | — | — | — |
| trial | quota | `consultations` | 1 | 1 semaine (calendar) |
| basic | quota | `consultations` | 1 | 1 semaine (calendar) |
| premium | quota | `consultations` | 2 | 1 jour (calendar) |

**Conséquences pour les tests :**
- `trial` et `basic` : 1 consultation par semaine calendaire — 2ème refusée
- `premium` : 2 consultations par jour calendaire — 3ème refusée

### Différence fondamentale avec 61-11 (ChatEntitlementGate)

**61-11** avait un chemin `legacy_fallback` pour préserver `QuotaService`. **61-12 n'en a pas.**

```
ChatEntitlementGate (61-11) :
  legacy_fallback → path="legacy" → déléguer à QuotaService

ThematicConsultationEntitlementGate (61-12) :
  legacy_fallback → ConsultationAccessDeniedError(reason="canonical_no_binding")
  TOUTES les décisions viennent du canonique uniquement
```

**Ne jamais appeler `QuotaService`** dans ce nouveau gate ou dans `generate_consultation` pour cette feature.

### Localisation des fichiers

```
backend/app/services/thematic_consultation_entitlement_gate.py   ← NOUVEAU
backend/app/api/v1/schemas/consultation.py                        ← MODIFIÉ (+ConsultationQuotaInfo, +quota_info sur ConsultationGenerateResponse)
backend/app/api/v1/routers/consultations.py                       ← MODIFIÉ (gate + error handlers + quota_info)
backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py ← NOUVEAU
backend/app/tests/integration/test_thematic_consultation_entitlement.py ← NOUVEAU
```

### Structure `ThematicConsultationEntitlementGate` — squelette de référence

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import UsageState
from app.services.quota_usage_service import QuotaUsageService, QuotaExhaustedError


class ConsultationAccessDeniedError(Exception):
    def __init__(self, reason: str, billing_status: str, plan_code: str) -> None:
        self.reason = reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        super().__init__(f"Consultation access denied: {reason}")


class ConsultationQuotaExceededError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, window_end: datetime | None) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end
        super().__init__(f"Consultation quota '{quota_key}' exceeded: {used}/{limit}")


@dataclass
class ConsultationEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited"
    usage_states: list[UsageState] = field(default_factory=list)


class ThematicConsultationEntitlementGate:
    FEATURE_CODE = "thematic_consultation"

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> ConsultationEntitlementResult:
        entitlement = EntitlementService.get_feature_entitlement(
            db, user_id=user_id, feature_code=ThematicConsultationEntitlementGate.FEATURE_CODE
        )

        # Pas de chemin legacy — thematic_consultation est 100% canonique
        # Si legacy_fallback retourné → traiter comme canonical_no_binding
        if entitlement.reason == "legacy_fallback":
            raise ConsultationAccessDeniedError(
                reason="canonical_no_binding",
                billing_status=entitlement.billing_status,
                plan_code=entitlement.plan_code,
            )

        if not entitlement.final_access:
            if entitlement.quota_exhausted and entitlement.usage_states:
                exhausted_state = next((s for s in entitlement.usage_states if s.exhausted), None)
                if exhausted_state:
                    raise ConsultationQuotaExceededError(
                        quota_key=exhausted_state.quota_key,
                        used=exhausted_state.used,
                        limit=exhausted_state.quota_limit,
                        window_end=exhausted_state.window_end,
                    )
            raise ConsultationAccessDeniedError(
                reason=entitlement.reason,
                billing_status=entitlement.billing_status,
                plan_code=entitlement.plan_code,
            )

        if entitlement.access_mode == "unlimited":
            return ConsultationEntitlementResult(
                path="canonical_unlimited",
                usage_states=entitlement.usage_states,
            )

        # access_mode == "quota" — consommer
        consumed_states: list[UsageState] = []
        for quota in entitlement.quotas:
            try:
                state = QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code=ThematicConsultationEntitlementGate.FEATURE_CODE,
                    quota=quota,
                    amount=1,
                )
                consumed_states.append(state)
            except QuotaExhaustedError as exc:
                window_end = next(
                    (s.window_end for s in entitlement.usage_states if s.quota_key == exc.quota_key),
                    None,
                )
                raise ConsultationQuotaExceededError(
                    quota_key=exc.quota_key,
                    used=exc.used,
                    limit=exc.limit,
                    window_end=window_end,
                ) from exc

        return ConsultationEntitlementResult(path="canonical_quota", usage_states=consumed_states)
```

### Modification du schéma consultation.py

Ajouter dans `backend/app/api/v1/schemas/consultation.py` :

```python
# Ajouter cet import si absent
from datetime import date, datetime  # datetime déjà importé ? vérifier

class ConsultationQuotaInfo(BaseModel):
    remaining: int | None = None
    limit: int | None = None
    window_end: datetime | None = None


# Modifier ConsultationGenerateResponse :
class ConsultationGenerateResponse(BaseModel):
    data: ConsultationGenerateData
    meta: ConsultationPrecheckMeta
    quota_info: ConsultationQuotaInfo = Field(default_factory=ConsultationQuotaInfo)
```

### Modification du routeur consultations.py — generate_consultation

```python
# Nouveaux imports à ajouter dans consultations.py :
from fastapi.responses import JSONResponse
from app.services.thematic_consultation_entitlement_gate import (
    ConsultationAccessDeniedError,
    ConsultationEntitlementResult,
    ConsultationQuotaExceededError,
    ThematicConsultationEntitlementGate,
)
from app.api.v1.schemas.consultation import ConsultationQuotaInfo  # si pas déjà importé


def _build_consultation_quota_info(result: ConsultationEntitlementResult) -> ConsultationQuotaInfo:
    if result.path in ("canonical_quota", "canonical_unlimited") and result.usage_states:
        state = result.usage_states[0]
        return ConsultationQuotaInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,
        )
    return ConsultationQuotaInfo()


@router.post(
    "/generate",
    response_model=ConsultationGenerateResponse,
    responses={403: {"description": "Accès refusé"}, 429: {"description": "Quota épuisé"}},
)
async def generate_consultation(
    request: Request,
    payload: ConsultationGenerateRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
):
    request_id = getattr(request.state, "request_id", "unknown")
    payload.consultation_type = ConsultationCatalogueService.map_legacy_key(payload.consultation_type)

    try:
        entitlement_result = ThematicConsultationEntitlementGate.check_and_consume(
            db, user_id=current_user.id
        )
    except ConsultationQuotaExceededError as error:
        db.rollback()
        return JSONResponse(
            status_code=429,
            content={"error": {
                "code": "consultation_quota_exceeded",
                "message": "quota de consultations thématiques épuisé",
                "details": {
                    "quota_key": error.quota_key,
                    "used": error.used,
                    "limit": error.limit,
                    "window_end": error.window_end.isoformat() if error.window_end else None,
                },
                "request_id": request_id,
            }},
        )
    except ConsultationAccessDeniedError as error:
        db.rollback()
        return JSONResponse(
            status_code=403,
            content={"error": {
                "code": "consultation_access_denied",
                "message": "accès aux consultations thématiques refusé",
                "details": {"reason": error.reason, "billing_status": error.billing_status},
                "request_id": request_id,
            }},
        )

    quota_info = _build_consultation_quota_info(entitlement_result)

    data = await ConsultationGenerationService.generate(db, current_user.id, payload, request_id)

    return ConsultationGenerateResponse(
        data=data,
        meta=ConsultationPrecheckMeta(request_id=request_id),
        quota_info=quota_info,
    )
```

### Politique de consommation et rollback transactionnel

**Politique retenue : rollback complet si `generate()` échoue après la consommation.**

- La consommation a lieu **avant** l'appel à `ConsultationGenerationService.generate()`
- Si `generate()` lève une exception non gérée après la consommation, la consommation est **annulée** avec le reste de la requête (rollback implicite de la session SQLAlchemy en fin de request lifecycle) — pas de remboursement explicite nécessaire dans 61-12
- `db.rollback()` est appelé **explicitement** uniquement dans les handlers `ConsultationQuotaExceededError` et `ConsultationAccessDeniedError` (avant l'appel à `generate()`, donc la consommation n'a pas encore eu lieu dans ces cas)
- La gate ne gère que l'entitlement — les erreurs business (données manquantes, safeguards) restent dans `ConsultationGenerationService`

> **Pourquoi ce choix ?** Garantir la conservation de la consommation même si `generate()` échoue nécessiterait un `db.commit()` juste après la gate, dans une transaction distincte, avant l'appel à `generate()`. C'est possible mais ajoute de la complexité (deux transactions, gestion des savepoints). La politique "rollback complet" est plus simple, cohérente avec 61-11, et acceptable pour cette story. Un `db.commit()` post-gate pourra être introduit en 61-13 si la politique produit l'exige.

### Pattern de test unitaire — squelette

```python
# test_thematic_consultation_entitlement_gate.py
from unittest.mock import patch, MagicMock
from app.services.thematic_consultation_entitlement_gate import (
    ThematicConsultationEntitlementGate,
    ConsultationAccessDeniedError,
    ConsultationQuotaExceededError,
)
from app.services.entitlement_types import FeatureEntitlement, QuotaDefinition, UsageState


def make_entitlement(**kwargs) -> FeatureEntitlement:
    defaults = dict(
        plan_code="basic", billing_status="active",
        is_enabled_by_plan=True, access_mode="quota",
        variant_code=None,
        quotas=[QuotaDefinition(
            quota_key="consultations", quota_limit=1,
            period_unit="week", period_value=1, reset_mode="calendar"
        )],
        final_access=True,
        reason="canonical_binding",
        usage_states=[],
        quota_exhausted=False,
    )
    return FeatureEntitlement(**{**defaults, **kwargs})


def test_canonical_quota_path_consumes(db_session):
    entitlement = make_entitlement()
    mock_state = MagicMock(used=1, remaining=0)

    with patch("app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
               return_value=entitlement), \
         patch("app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume",
               return_value=mock_state) as mock_consume:
        result = ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_quota"
    mock_consume.assert_called_once()

def test_legacy_fallback_treated_as_no_binding(db_session):
    entitlement = make_entitlement(reason="legacy_fallback", final_access=False)
    with patch("app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
               return_value=entitlement):
        with pytest.raises(ConsultationAccessDeniedError) as exc_info:
            ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "canonical_no_binding"
```

### Pattern de test d'intégration — squelette

```python
# test_thematic_consultation_entitlement.py
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.thematic_consultation_entitlement_gate import (
    ConsultationEntitlementResult,
    ConsultationAccessDeniedError,
    ConsultationQuotaExceededError,
)
from app.services.entitlement_types import UsageState

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_auth(mock_user):
    from app.api.dependencies.auth import require_authenticated_user
    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(require_authenticated_user, None)


def _make_quota_state(used=1, limit=1, period_unit="week"):
    return UsageState(
        feature_code="thematic_consultation",
        quota_key="consultations",
        quota_limit=limit,
        used=used,
        remaining=max(0, limit - used),
        exhausted=used >= limit,
        period_unit=period_unit,
        period_value=1,
        reset_mode="calendar",
        window_start=None,
        window_end=None,
    )


def test_generate_no_plan_rejected(mock_user):
    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        side_effect=ConsultationAccessDeniedError(reason="no_plan", billing_status="none", plan_code=""),
    ), patch("app.infra.db.session.get_db_session"):
        response = client.post("/v1/consultations/generate", json={
            "consultation_type": "career",
            "question": "Quelle direction prendre ?"
        })
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "consultation_access_denied"
```

### Éviter les régressions critiques

- **Ne pas modifier `ConsultationGenerationService`** — la gate est dans le routeur
- **Ne pas toucher `precheck_consultation`** — le precheck ne consomme pas de quota
- **Ne pas appeler `QuotaService`** — ni dans la gate ni dans le routeur pour cette feature
- **`ConsultationGenerateResponse` change de forme** (ajout de `quota_info`) — les tests existants qui vérifient la réponse de `/v1/consultations/generate` doivent être mis à jour si nécessaire (les champs existants ne changent pas)
- **Conserver `response_model=ConsultationGenerateResponse`** — FastAPI accepte `JSONResponse` custom même avec `response_model`. Ajouter `responses={403: ..., 429: ...}` pour la doc OpenAPI. Ne pas supprimer le `response_model` (contrairement à ce que `chat.py` fait — ce n'est pas une obligation).

### Imports dans `thematic_consultation_entitlement_gate.py`

```python
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import UsageState
from app.services.quota_usage_service import QuotaUsageService, QuotaExhaustedError
```

Pas d'import circulaire : `ThematicConsultationEntitlementGate` ne fait pas partie du cycle entitlements.

### Hypothèse valide : `usage_states[0]` pour `quota_info`

`thematic_consultation` n'a qu'**un seul quota par plan** (quota_key=`"consultations"`). Prendre `result.usage_states[0]` pour construire `quota_info` est donc correct et non arbitraire. Documenter cette hypothèse dans le code avec un commentaire :

```python
def _build_consultation_quota_info(result: ConsultationEntitlementResult) -> ConsultationQuotaInfo:
    # thematic_consultation a un seul quota par plan (quota_key="consultations")
    if result.usage_states:
        state = result.usage_states[0]
        return ConsultationQuotaInfo(...)
    return ConsultationQuotaInfo()
```

Si un jour `thematic_consultation` avait plusieurs quotas (day + lifetime), la logique `[0]` serait à revoir.

### Figer le temps dans les tests de fenêtre (premium/day, basic/week)

Les tests `test_premium_quota_2_per_day` et `test_basic_quota_1_per_week` doivent patcher `datetime.now` pour éviter les échecs en fin de journée/semaine :

```python
from unittest.mock import patch
from datetime import datetime, timezone

FIXED_NOW = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)  # mercredi

def test_premium_quota_2_per_day(...):
    with patch("app.services.quota_window_resolver.datetime") as mock_dt:
        mock_dt.now.return_value = FIXED_NOW
        # deux appels ok, troisième → 429
```

> **Où patcher ?** `QuotaWindowResolver.compute_window()` appelle `datetime.now(timezone.utc)`. C'est le point à patcher. Vérifier le chemin exact dans `backend/app/services/quota_window_resolver.py` avant d'écrire le patch.

### Point critique : `disabled_by_plan` est déjà produit par `EntitlementService`

**Prérequis 61-9 déjà livré** — `EntitlementService.get_feature_entitlement()` retourne `reason="disabled_by_plan"` (avec `final_access=False`) dans les cas suivants :
- `binding.is_enabled=False` ou `binding.access_mode=DISABLED`
- `access_mode=QUOTA` mais aucun quota défini (`is_enabled_by_plan` forcé à `False`)
- quota avec `reset_mode="rolling"` (non supporté → `is_enabled_by_plan` forcé à `False`)

**La gate n'a donc pas à produire ce `reason` elle-même.** Elle le propage simplement via `raise ConsultationAccessDeniedError(reason=entitlement.reason, ...)` dans le bloc `if not entitlement.final_access:`. AC 2 est couvert sans logique ad hoc dans la gate.

De même, le cas `access_mode="quota"` avec `quotas=[]` est déjà géré par `EntitlementService` qui retourne `final_access=False, reason="disabled_by_plan"`. La gate n'atteindra jamais la boucle `for quota in entitlement.quotas` avec une liste vide ET `final_access=True` simultanément.

### Point important : `datetime` dans schemas/consultation.py

Le fichier `consultation.py` importe déjà `from datetime import date, datetime`. L'ajout de `ConsultationQuotaInfo` n'ajoute pas de dépendance nouvelle.

### Contexte stories précédentes

**61-11 (done)** : Migration `astrologer_chat` — a établi le pattern `ChatEntitlementGate`. **La différence majeure de 61-12** est l'absence totale de chemin legacy. Tout `legacy_fallback` est traité comme `canonical_no_binding`.

**61-9 (done)** : `EntitlementService.get_feature_entitlement()` retourne `FeatureEntitlement` avec `reason`, `final_access`, `quota_exhausted`, `usage_states`, `access_mode`, `quotas`.

**61-10 (done)** : `QuotaUsageService.consume()` retourne `UsageState` et lève `QuotaExhaustedError`. `QuotaWindowResolver` gère les fenêtres calendaires week/day.

**61-7 (done)** : `feature_usage_counters` table existe. Seed canonical existe dans `backend/scripts/seed_product_entitlements.py`.

### Références

- Pattern gate : `backend/app/services/chat_entitlement_gate.py` (61-11)
- Pattern routeur : `backend/app/api/v1/routers/chat.py` (quota_info, JSONResponse errors, db.rollback)
- Schémas consultation : `backend/app/api/v1/schemas/consultation.py`
- Routeur cible : `backend/app/api/v1/routers/consultations.py`
- Seed canonical : `backend/scripts/seed_product_entitlements.py`
- Types entitlements : `backend/app/services/entitlement_types.py`

---

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- `pytest -q app/tests/integration/test_thematic_consultation_entitlement.py app/tests/unit/test_thematic_consultation_entitlement_gate.py app/tests/integration/test_consultations_router.py app/tests/integration/test_consultation_catalogue.py app/tests/integration/test_consultation_third_party.py app/tests/unit/test_entitlement_service.py app/tests/unit/test_quota_usage_service.py` → 77 passed.
- `ruff check app/api/v1/routers/consultations.py app/tests/integration/test_thematic_consultation_entitlement.py app/tests/unit/test_thematic_consultation_entitlement_gate.py` → OK.

### Completion Notes List

- Implemented `ThematicConsultationEntitlementGate` as a 100% canonical gate (no legacy fallback).
- Updated `generate_consultation` endpoint to enforce entitlements and return quota info.
- Handled `403` and `429` errors with explicit `db.rollback()`.
- Added unit tests for gate logic.
- Added real integration tests for `/generate` with canonical bindings, persisted counters, `canonical_no_binding`, rollback checks, and fixed window scenarios (`2/day`, `1/week`).
- Fixed a persistence bug by committing the SQLAlchemy session after successful generation so canonical quota consumption survives across requests.
- Fixed non-regression tests by mocking the entitlement gate.

### File List

- `backend/app/services/thematic_consultation_entitlement_gate.py` (New)
- `backend/app/api/v1/schemas/consultation.py` (Modified)
- `backend/app/api/v1/routers/consultations.py` (Modified)
- `backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py` (New)
- `backend/app/tests/integration/test_thematic_consultation_entitlement.py` (New)
- `backend/app/tests/integration/test_consultations_router.py` (Modified - mocks)
- `backend/app/tests/integration/test_consultation_catalogue.py` (Modified - mocks)
- `backend/app/tests/integration/test_consultation_third_party.py` (Modified - mocks)
