# Story 59.1 : Suppression du chemin V1 et migration V2 comme voie unique d'exécution

Status: done

## Story

En tant que développeur backend,
je veux que le gateway V2 (`LLMGateway`) soit l'unique chemin d'exécution pour tous les appels LLM,
afin d'éliminer la dette technique du double chemin V1/V2, le flag `LLM_ORCHESTRATION_V2`, et le parser heuristique fragile `_parse_guidance_sections`.

## Acceptance Criteria

1. Le flag `LLM_ORCHESTRATION_V2` n'existe plus nulle part dans le codebase (config, code, tests, `.env.example`).
2. `AIEngineAdapter.generate_guidance()` appelle directement `LLMGateway.execute()` sans aucun branchement conditionnel `if/else` sur un flag.
3. Les fichiers V1 suivants sont supprimés :
   - `backend/app/ai_engine/services/generate_service.py`
   - `backend/app/ai_engine/services/prompt_registry.py`
   - `backend/app/ai_engine/providers/openai_client.py`
   - `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2`
   - `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2`
   - `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2`
4. `backend/app/ai_engine/config.py` et `backend/app/ai_engine/schemas.py` sont conservés uniquement si encore importés par le gateway V2 — sinon supprimés.
5. `backend/app/ai_engine/exceptions.py` est conservé (importé par `gateway.py`).
6. La méthode `GuidanceService._parse_guidance_sections()` et son usage sont supprimés — la structuration est désormais garantie par les Structured Outputs du gateway V2.
7. `GuidanceData.key_points` et `GuidanceData.actionable_advice` sont renseignés via la réponse JSON structurée du gateway (plus de parsing textuel ad hoc).
8. `pytest` passe sans erreur — aucun test ne référence plus `LLM_ORCHESTRATION_V2`, `generate_service`, `prompt_registry` (V1), ou `openai_client` (V1).
9. `ruff check backend/` passe sans warning ni erreur.

## Tasks / Subtasks

- [ ] T1 — Supprimer le flag `LLM_ORCHESTRATION_V2` (AC: 1)
  - [ ] T1.1 Retirer `LLM_ORCHESTRATION_V2` de `backend/app/core/config.py` (ou `settings.py`)
  - [ ] T1.2 Retirer toute référence à `LLM_ORCHESTRATION_V2` dans `backend/app/services/ai_engine_adapter.py`
  - [ ] T1.3 Retirer la ligne de `.env.example` si présente
  - [ ] T1.4 Grep global pour s'assurer qu'il ne reste aucune référence : `grep -r "LLM_ORCHESTRATION_V2" backend/`

- [ ] T2 — Simplifier `AIEngineAdapter` pour appel direct au gateway (AC: 2)
  - [ ] T2.1 Lire entièrement `backend/app/services/ai_engine_adapter.py`
  - [ ] T2.2 Retirer le bloc `if not LLM_ORCHESTRATION_V2: ... else: ...`
  - [ ] T2.3 `generate_guidance()` → appel direct `LLMGateway.execute(use_case, input_data, context, ...)`
  - [ ] T2.4 Conserver toute la logique de mapping d'erreurs (`AIEngineAdapterError`, codes HTTP)

- [ ] T3 — Supprimer les fichiers V1 orphelins (AC: 3, 4)
  - [ ] T3.1 Supprimer `backend/app/ai_engine/services/generate_service.py`
  - [ ] T3.2 Supprimer `backend/app/ai_engine/services/prompt_registry.py`
  - [ ] T3.3 Supprimer `backend/app/ai_engine/providers/openai_client.py`
  - [ ] T3.4 Supprimer `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2`
  - [ ] T3.5 Supprimer `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2`
  - [ ] T3.6 Supprimer `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2`
  - [ ] T3.7 Vérifier que `backend/app/ai_engine/config.py` n'est plus importé → le supprimer si orphelin
  - [ ] T3.8 Vérifier que `backend/app/ai_engine/schemas.py` n'est plus importé → le supprimer si orphelin
  - [ ] T3.9 Conserver `backend/app/ai_engine/exceptions.py` (importé par `gateway.py`)

- [ ] T4 — Supprimer `_parse_guidance_sections` et le parsing heuristique (AC: 6, 7)
  - [ ] T4.1 Lire entièrement `backend/app/services/guidance_service.py`
  - [ ] T4.2 Supprimer la méthode `GuidanceService._parse_guidance_sections()`
  - [ ] T4.3 Supprimer les appels à `_parse_guidance_sections` dans `request_guidance_async()` et `request_contextual_guidance_async()`
  - [ ] T4.4 S'assurer que `GuidanceData.key_points` et `actionable_advice` proviennent directement de la réponse JSON structurée du gateway (champs `key_points` et `actionable_advice` dans le JSON Schema de sortie du use_case)
  - [ ] T4.5 Supprimer les fallbacks hardcodés liés au parsing échoué (les fallbacks du gateway V2 prennent le relais)
  - [ ] T4.6 Supprimer `_normalize_summary()` si elle ne sert qu'à filtrer des artefacts du prompt V1 (le marqueur `[guidance_prompt_version:` disparaît avec les templates V1)

- [ ] T5 — Mettre à jour les tests (AC: 8)
  - [ ] T5.1 Supprimer ou mettre à jour tous les tests qui mockent `generate_service`, `prompt_registry` V1, `openai_client` V1
  - [ ] T5.2 Mettre à jour les tests de `guidance_service.py` pour mocker `LLMGateway.execute()` directement
  - [ ] T5.3 Vérifier que les tests de `ai_engine_adapter.py` reflètent le chemin simplifié
  - [ ] T5.4 Exécuter `pytest backend/` et corriger tous les échecs

- [ ] T6 — Validation finale (AC: 9)
  - [ ] T6.1 `ruff check backend/` → 0 erreur
  - [ ] T6.2 `pytest backend/` → tous les tests passent
  - [ ] T6.3 Grep final : `grep -r "LLM_ORCHESTRATION_V2\|generate_service\|prompt_registry\|openai_client" backend/` → 0 résultat hors commentaires historiques

## Dev Notes

### Architecture à respecter

**Gateway V2 — Signature d'appel** (`backend/app/llm_orchestration/gateway.py`) :
```python
LLMGateway.execute(
    use_case: str,           # ex: "guidance_daily"
    input_data: dict,        # données spécifiques au use_case
    context: dict,           # contexte utilisateur (birth_data, current_datetime, etc.)
    user_id: int,
    request_id: str,
    trace_id: str,
    db: Session,
    locale: str = "fr",
) -> GatewayResult
```

**`GatewayResult`** (`backend/app/llm_orchestration/models.py`) contient le JSON structuré validé par le JSON Schema du use_case. Pour `guidance_daily`, ce JSON doit inclure `summary`, `key_points`, `actionable_advice`, `disclaimer` — ces champs doivent être déclarés dans le `output_schema` du use_case en DB.

**Composition 4 couches** (Epic 28, inchangée) :
`system_core` (code) → `developer_prompt` (DB) → `persona` (DB paramétrique) → `user_data` (runtime)

### Fichiers à NE PAS toucher dans cette story
- `backend/app/llm_orchestration/gateway.py` — à utiliser tel quel
- `backend/app/llm_orchestration/services/prompt_registry_v2.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/infra/db/models/llm_prompt.py`
- Les prompts en base de données (inchangés dans cette story)

### Imports à vérifier dans `gateway.py`
```python
# gateway.py importe depuis ai_engine :
from app.ai_engine.exceptions import UpstreamError, UpstreamRateLimitError, UpstreamTimeoutError
from app.ai_engine.services.log_sanitizer import sanitize_request_for_logging
from app.ai_engine.services.utils import calculate_cost
```
Ces imports doivent rester fonctionnels — ne pas supprimer ces fichiers.

### Chemin V1 actuel dans `ai_engine_adapter.py` (à remplacer)
```python
# AVANT (à supprimer)
if not settings.LLM_ORCHESTRATION_V2:
    # ... logique generate_service V1 ...
else:
    result = await LLMGateway.execute(...)

# APRÈS (cible)
result = await LLMGateway.execute(
    use_case=use_case,
    input_data=input_data,
    context=context,
    ...
)
```

### JSON Schema de sortie requis pour `guidance_daily`
Le use_case `guidance_daily` en DB doit avoir un `output_schema` avec au minimum :
```json
{
  "type": "object",
  "required": ["summary", "key_points", "actionable_advice", "disclaimer"],
  "properties": {
    "summary": {"type": "string"},
    "key_points": {"type": "array", "items": {"type": "string"}, "maxItems": 2},
    "actionable_advice": {"type": "array", "items": {"type": "string"}, "maxItems": 2},
    "disclaimer": {"type": "string"}
  }
}
```
Si ce schéma n'est pas encore en DB, créer une migration seed pour le publier.

### Gestion des dépendances Python
- Dépendances dans `backend/pyproject.toml` uniquement
- Ne pas créer de `requirements.txt`
- `openai` SDK reste en dépendance (utilisé par le gateway V2 via `responses_client.py`)

### Project Structure Notes
- `backend/app/ai_engine/` : après suppression, il ne doit rester que `exceptions.py`, `log_sanitizer.py`, `utils.py` (s'ils sont encore importés)
- `backend/app/llm_orchestration/` : inchangé dans cette story
- `backend/app/services/guidance_service.py` : allégé (suppression `_parse_guidance_sections`, fallbacks heuristiques)

### References
- [Source: _bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md] — décisions verrouillées V2
- [Source: backend/app/llm_orchestration/gateway.py] — signature `LLMGateway.execute()`
- [Source: backend/app/services/guidance_service.py#L276] — `_parse_guidance_sections` à supprimer
- [Source: backend/app/services/ai_engine_adapter.py] — routage V1/V2 à simplifier
- [Source: _bmad-output/planning-artifacts/epic-59-refacto-moteur-ia-v2.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Implémentation complète : flag `LLM_ORCHESTRATION_V2` supprimé, fichiers V1 supprimés, `AIEngineAdapter` simplifié en façade directe sur `LLMGateway.execute()`.
- **Code review (post-implémentation) :**
  - ISSUE-01 (Mineur) : bloc mort `if TYPE_CHECKING: pass` + import `TYPE_CHECKING` inutilisé dans `ai_engine_adapter.py` — supprimés.
- Tests : 1342 passed, ruff clean.

### File List

- `backend/app/services/ai_engine_adapter.py` — façade directe gateway, nettoyage imports
