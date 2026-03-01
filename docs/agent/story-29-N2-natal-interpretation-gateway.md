# Story 29-N2 — NatalInterpretationService (SIMPLE + COMPLETE) branché sur LLMGateway

## Contexte & Périmètre

**Epic NATAL-3 / Story N2**
**Chapitre 29** — Interprétation natale via LLMGateway

L'actuel `NatalInterpretationService` (fichier `backend/app/services/natal_interpretation_service.py`) :
- Utilise `USE_CASE = "natal_chart_interpretation"` (use case inexistant dans le catalogue 28.5)
- En mode V2, appelle `AIEngineAdapter.generate_guidance()` (intermédiaire non-standard) et wraps la réponse en `MockResponse`
- Retourne un `NatalInterpretationData` avec champs textuels parsés (text, summary, key_points, advice, disclaimer)
- **N'utilise pas** le `GatewayResult.structured_output` (AstroResponse_v1)

Cette story **refactorise ce service** pour :
1. Appeler directement `LLMGateway.execute()` avec les use cases canoniques du chapitre 28
2. Supporter 2 niveaux : `natal_interpretation_short` (SIMPLE/gratuit) et `natal_interpretation` (COMPLETE/payant)
3. Retourner `AstroResponse_v1` structuré au lieu d'un texte parsé
4. Créer un endpoint dédié `POST /v1/natal/interpretation`

**Dépend de :** Story N1 (build_chart_json + build_evidence_catalog)

---

## Architecture cible

```
Frontend
    └─ POST /v1/natal/interpretation
           │
           ▼
    NatalInterpretationRouter (nouveau ou existant étendu)
           │
           ▼
    NatalInterpretationServiceV2.interpret()
       ├─ Step A: récupère le dernier natal chart (UserNatalChartService)
       ├─ Step B: build_chart_json() + build_evidence_catalog()  [N1]
       ├─ Step C: choisit use_case selon entitlement (short | complete)
       ├─ Step D: appelle LLMGateway.execute(use_case, user_input, context, db)
       └─ Step E: retourne AstroInterpretationResult (structured_output + meta)
```

---

## Hypothèses & Dépendances

- Les use cases `natal_interpretation` et `natal_interpretation_short` sont seédés en DB (Epic 28.5)
- L'`AstroResponse_v1` schema est seédé en DB (seed_28_4.py)
- `LLMGateway` est importable depuis `app.llm_orchestration.gateway`
- `build_chart_json` et `build_evidence_catalog` sont disponibles depuis N1
- L'entitlement (simple vs complete) est déterminé par un flag dans l'endpoint (`use_case_level: "short" | "complete"`)
  - En prod, cela sera lié au plan utilisateur ; pour cette story, un paramètre de requête suffit
- Le paramètre `persona_id` est optionnel pour SIMPLE, requis pour COMPLETE (le gateway le valide)
- La convention gateway : si `context["chart_json"]` est présent, il overwrite `user_input["chart_json"]` dans les template_vars
- `chart_json` doit être une **chaîne JSON sérialisée** dans les template_vars (pour le rendu `{{chart_json}}`) mais un **dict** dans `user_input` (pour la validation de schéma JSON Schema)

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Brancher le service natal sur le gateway V2 (Epic 28)
- Avoir un endpoint REST propre et testable
- Retourner `AstroResponse_v1` structuré au lieu de texte parsé
- Garder la rétrocompatibilité avec le flag `llm_orchestration_v2`

**Non-Objectifs :**
- Pas de gestion de paiement/Stripe dans cette story (entitlement = paramètre simple)
- Pas de modification de l'UI (c'est N4)
- Pas de modification des prompts (c'est N3)

---

## Acceptance Criteria

### AC1 — Endpoint `POST /v1/natal/interpretation`

Request body (Pydantic) :
```python
class NatalInterpretationRequest(BaseModel):
    use_case_level: Literal["short", "complete"] = "short"
    persona_id: str | None = None  # UUID string, optionnel pour short, recommandé pour complete
    locale: str = "fr-FR"
    question: str | None = None  # Si absent, valeur par défaut "Interprète mon thème natal"
```

Response body `200 OK` :
```json
{
  "data": {
    "chart_id": "uuid-...",
    "use_case": "natal_interpretation_short",
    "interpretation": {
      "title": "...",
      "summary": "...",
      "sections": [{"key": "overall", "heading": "...", "content": "..."}],
      "highlights": ["..."],
      "advice": ["..."],
      "evidence": ["SUN_TAURUS", "SUN_H10"],
      "disclaimers": []
    },
    "meta": {
      "prompt_version_id": "uuid-...",
      "persona_id": null,
      "model": "gpt-4o-mini",
      "latency_ms": 1234,
      "validation_status": "valid",
      "repair_attempted": false,
      "fallback_triggered": false
    },
    "degraded_mode": null
  }
}
```

### AC2 — Choix du use_case selon `use_case_level`
- `use_case_level == "short"` → use_case = `natal_interpretation_short`
- `use_case_level == "complete"` → use_case = `natal_interpretation`

### AC3 — Construction correcte de `user_input` et `context` pour le gateway

**Pour `natal_interpretation_short` :**
```python
user_input = {
    "chart_json": chart_json_dict,  # dict pour validation schéma
}
context = {
    "locale": locale,
    "chart_json": json.dumps(chart_json_dict),  # string pour rendu prompt
    "use_case": "natal_interpretation_short",
}
```

**Pour `natal_interpretation` :**
```python
user_input = {
    "question": question or "Interprète mon thème natal",
    "chart_json": chart_json_dict,  # dict pour validation schéma
}
context = {
    "locale": locale,
    "chart_json": json.dumps(chart_json_dict),  # string pour rendu prompt
    "use_case": "natal_interpretation",
    "persona_id": persona_id,  # gateway gère la résolution persona_name
}
```

> **Important :** `context["chart_json"]` (string) overwrite `user_input["chart_json"]` (dict) dans les template_vars du gateway. C'est intentionnel et documenté dans la convention Epic 28.1.

### AC4 — `GatewayResult.structured_output` mappé sur le modèle de réponse
Si `gateway_result.structured_output` est un dict valide (AstroResponse_v1), il est retourné tel quel dans `data.interpretation`.
Si `gateway_result.structured_output is None` (fallback déclenché mais sans output structuré) → retourner HTTP 502.

### AC5 — Gestion des erreurs gateway
| Erreur | HTTP | Code API |
|--------|------|----------|
| `UnknownUseCaseError` | 500 | `gateway_config_error` |
| `GatewayConfigError` | 500 | `gateway_config_error` |
| `InputValidationError` | 422 | `natal_input_invalid` |
| `OutputValidationError` (pas de fallback) | 502 | `interpretation_failed` |
| `UpstreamError` / `UpstreamTimeoutError` | 503 | `llm_upstream_error` |
| `UpstreamRateLimitError` | 429 | `llm_rate_limited` |
| Natal chart not found | 404 | `natal_chart_not_found` |

### AC6 — `degraded_mode` propagé dans la réponse
Le `degraded_mode` calculé lors de `build_chart_json()` est inclus dans la réponse pour que le frontend puisse adapter l'affichage.

### AC7 — Rétrocompatibilité `llm_orchestration_v2`
- Si `settings.ai_engine.llm_orchestration_v2 == False` : retourner HTTP 501 avec code `feature_disabled`
- La nouvelle logique est dans `NatalInterpretationServiceV2` (nouvelle classe, ne pas modifier l'ancienne)

### AC8 — Tests d'intégration minimaux
- `test_endpoint_short_success` : mock gateway retourne un `GatewayResult` valide → 200
- `test_endpoint_complete_success` : même avec `use_case_level=complete` → 200
- `test_endpoint_no_chart` : pas de natal chart en DB → 404
- `test_endpoint_gateway_config_error` : gateway lève `GatewayConfigError` → 500

---

## Tâches Techniques

### T1 — Créer `NatalInterpretationServiceV2`

**Fichier :** `backend/app/services/natal_interpretation_service_v2.py`

```python
class AstroInterpretationResult(BaseModel):
    chart_id: str
    use_case: str
    interpretation: dict  # AstroResponse_v1 structured
    meta: dict            # GatewayMeta fields
    degraded_mode: str | None

class NatalInterpretationServiceV2:
    @staticmethod
    async def interpret(
        *,
        chart: UserNatalChartReadData,
        birth_profile: UserBirthProfileData,
        use_case_level: Literal["short", "complete"],
        persona_id: str | None,
        locale: str,
        question: str | None,
        user_id: int,
        request_id: str,
        trace_id: str | None,
        db: Session,
    ) -> AstroInterpretationResult:
        # Step A: degraded_mode
        # Step B: build_chart_json + build_evidence_catalog
        # Step C: use_case selection
        # Step D: build user_input + context
        # Step E: gateway.execute()
        # Step F: handle GatewayResult
        ...
```

**Import du gateway :**
```python
from app.llm_orchestration.gateway import LLMGateway
gateway = LLMGateway()
```

**Gestion de `persona_name` dans context :**
Le gateway compose lui-même la persona block à partir du `persona_id`. Cependant, le prompt utilise `{{persona_name}}` comme variable de rendu. Le service doit donc résoudre le nom de la persona depuis la DB et le passer dans le context si `use_case_level == "complete"`.

```python
# Si use_case_level == "complete" et persona_id fourni:
# 1. Charger LlmPersonaModel depuis DB par persona_id
# 2. Ajouter context["persona_name"] = persona.name
# Sinon, le gateway gèrera l'erreur si persona_strategy=required
```

### T2 — Créer le router/endpoint

**Fichier :** `backend/app/api/v1/routers/natal_interpretation.py`

```python
router = APIRouter(prefix="/v1/natal", tags=["natal-interpretation"])

@router.post("/interpretation", response_model=NatalInterpretationResponse)
async def interpret_natal_chart(
    body: NatalInterpretationRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NatalInterpretationResponse:
    ...
```

Ce router récupère le dernier natal chart depuis `UserNatalChartService.get_latest(db, user_id)` et appelle `NatalInterpretationServiceV2.interpret()`.

### T3 — Enregistrer le router dans l'app

**Fichier :** `backend/app/api/v1/router.py` (ou l'équivalent)

Chercher où les routers sont inclus (`app.include_router(...)`) et ajouter :
```python
from app.api.v1.routers.natal_interpretation import router as natal_interpretation_router
app.include_router(natal_interpretation_router)
```

### T4 — Schémas Pydantic

**Fichier :** `backend/app/api/v1/schemas/natal_interpretation.py`

```python
class NatalInterpretationRequest(BaseModel):
    use_case_level: Literal["short", "complete"] = "short"
    persona_id: str | None = None
    locale: str = Field("fr-FR", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    question: str | None = Field(None, max_length=500)

class InterpretationMeta(BaseModel):
    prompt_version_id: str | None
    persona_id: str | None
    model: str
    latency_ms: int
    validation_status: str
    repair_attempted: bool
    fallback_triggered: bool

class NatalInterpretationData(BaseModel):
    chart_id: str
    use_case: str
    interpretation: dict  # AstroResponse_v1
    meta: InterpretationMeta
    degraded_mode: str | None

class NatalInterpretationResponse(BaseModel):
    data: NatalInterpretationData
```

### T5 — Tests

**Fichier :** `backend/app/tests/integration/test_natal_interpretation_endpoint.py`

Utiliser `httpx.AsyncClient` + `pytest-asyncio`, mocker `LLMGateway.execute` avec `AsyncMock`.

Fixture `mock_gateway_result_valid` :
```python
GatewayResult(
    use_case="natal_interpretation_short",
    request_id="test-req-id",
    trace_id="test-trace-id",
    raw_output='{"title": "Test", "summary": "...", ...}',
    structured_output={
        "title": "Thème natal test",
        "summary": "Résumé de test...",
        "sections": [
            {"key": "overall", "heading": "Vue d'ensemble", "content": "Contenu..."},
            {"key": "career", "heading": "Carrière", "content": "Contenu..."}
        ],
        "highlights": ["Point 1", "Point 2", "Point 3"],
        "advice": ["Conseil 1", "Conseil 2", "Conseil 3"],
        "evidence": ["SUN_TAURUS", "MOON_SCORPIO"]
    },
    usage=UsageInfo(input_tokens=100, output_tokens=200, total_tokens=300, estimated_cost_usd=0.001),
    meta=GatewayMeta(
        latency_ms=500,
        cached=False,
        prompt_version_id="uuid-v1",
        persona_id=None,
        model="gpt-4o-mini",
        output_schema_id="uuid-s1",
        validation_status="valid",
        repair_attempted=False,
        fallback_triggered=False,
    )
)
```

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| CRÉER | `backend/app/services/natal_interpretation_service_v2.py` |
| CRÉER | `backend/app/api/v1/routers/natal_interpretation.py` |
| CRÉER | `backend/app/api/v1/schemas/natal_interpretation.py` |
| CRÉER | `backend/app/tests/integration/test_natal_interpretation_endpoint.py` |
| MODIFIER | `backend/app/api/v1/router.py` (inclure le nouveau router) |

---

## Critères de "Done"

- [ ] `NatalInterpretationServiceV2.interpret()` implémentée
- [ ] Endpoint `POST /v1/natal/interpretation` accessible
- [ ] Tests passent (`pytest backend/app/tests/integration/test_natal_interpretation_endpoint.py`)
- [ ] `http POST /v1/natal/interpretation use_case_level=short` retourne 200 (ou 501 si feature flag off)
- [ ] `http POST /v1/natal/interpretation use_case_level=complete persona_id=<uuid>` retourne 200
- [ ] Logs observabilité visibles (LlmCallLogModel créé en DB)
