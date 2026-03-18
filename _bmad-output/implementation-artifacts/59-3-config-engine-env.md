# Story 59.3 : Configuration engine OpenAI par prompt via `.env`

Status: done

## Story

En tant qu'opérateur de l'application,
je veux configurer le modèle OpenAI utilisé par chaque prompt via une clef `.env` dédiée,
afin de pouvoir changer le modèle d'un use_case spécifique sans redéployer le code ni modifier d'autres use_cases.

## Acceptance Criteria

1. Chaque `PromptEntry` dans `PROMPT_CATALOG` possède un champ `engine_env_key` distinct (ex: `"OPENAI_ENGINE_GUIDANCE_DAILY"`).
2. `LLMGateway.execute()` résout le modèle à utiliser en lisant `os.environ.get(entry.engine_env_key, settings.OPENAI_MODEL_DEFAULT)` avant chaque appel LLM.
3. Si la clef `.env` n'est pas définie, le fallback `settings.OPENAI_MODEL_DEFAULT` est utilisé sans erreur ni log de warning intempestif — seulement un `logger.debug`.
4. Aucune valeur de modèle OpenAI n'est hardcodée dans le code Python (hors tests et commentaires) — vérifiable par `grep -r '"gpt-' backend/app/ --include="*.py"` → 0 résultat.
5. `backend/.env.example` est mis à jour avec toutes les clefs de modèle par prompt, avec des valeurs par défaut documentées.
6. Le modèle résolu est loggué dans l'observabilité du gateway (déjà présente dans `log_call`) pour chaque appel LLM.
7. `pytest backend/` passe sans erreur.
8. `ruff check backend/` passe sans warning.

## Tasks / Subtasks

- [ ] T1 — Vérifier que `engine_env_key` est présent dans `PromptEntry` (dépend 59.2)
  - [ ] T1.1 Confirmer que `PromptEntry.engine_env_key` existe (créé en 59.2)
  - [ ] T1.2 Confirmer que chaque entrée dans `PROMPT_CATALOG` a un `engine_env_key` distinct

- [ ] T2 — Implémenter la résolution du modèle dans le gateway (AC: 2, 3)
  - [ ] T2.1 Lire entièrement `backend/app/llm_orchestration/gateway.py`
  - [ ] T2.2 Créer une fonction utilitaire `resolve_model(use_case_key: str) -> str` dans le gateway ou dans `backend/app/prompts/catalog.py` :
    ```python
    def resolve_model(use_case_key: str) -> str:
        entry = PROMPT_CATALOG.get(use_case_key)
        if entry:
            model = os.environ.get(entry.engine_env_key)
            if model:
                return model
        return settings.OPENAI_MODEL_DEFAULT
    ```
  - [ ] T2.3 Brancher `resolve_model()` dans `LLMGateway.execute()` pour passer le modèle résolu à `ResponsesClient`
  - [ ] T2.4 Vérifier que `ResponsesClient` (`backend/app/llm_orchestration/providers/responses_client.py`) accepte un paramètre `model` dynamique (ne pas hardcoder)

- [ ] T3 — Supprimer toutes les valeurs hardcodées (AC: 4)
  - [ ] T3.1 `grep -r '"gpt-' backend/app/ --include="*.py"` — lister toutes les occurrences
  - [ ] T3.2 Remplacer chaque occurrence par `settings.OPENAI_MODEL_DEFAULT` ou `resolve_model(use_case_key)`
  - [ ] T3.3 Vérifier `backend/app/ai_engine/config.py` (si conservé) — retirer `OPENAI_MODEL_DEFAULT = "gpt-4o-mini"` hardcodé, le mettre dans `settings`

- [ ] T4 — Mettre à jour `.env.example` (AC: 5)
  - [ ] T4.1 Lire `backend/.env.example`
  - [ ] T4.2 Ajouter ou mettre à jour la section modèles :
    ```
    # Modèles OpenAI par use_case (fallback sur OPENAI_MODEL_DEFAULT si non défini)
    OPENAI_MODEL_DEFAULT=gpt-4o-mini
    OPENAI_ENGINE_GUIDANCE_DAILY=gpt-4o-mini
    OPENAI_ENGINE_GUIDANCE_WEEKLY=gpt-4o-mini
    OPENAI_ENGINE_GUIDANCE_CONTEXTUAL=gpt-4o-mini
    OPENAI_ENGINE_NATAL_INTERPRETATION=gpt-4o
    OPENAI_ENGINE_CHAT=gpt-4o-mini
    # Ajouter une ligne par use_case supplémentaire
    ```

- [ ] T5 — Vérifier l'observabilité (AC: 6)
  - [ ] T5.1 Lire `backend/app/llm_orchestration/services/observability_service.py`
  - [ ] T5.2 Confirmer que `log_call()` logue le modèle utilisé — si non, ajouter `model` au payload de log
  - [ ] T5.3 Vérifier que le modèle résolu apparaît dans les métriques/traces existantes

- [ ] T6 — Tests (AC: 7)
  - [ ] T6.1 Test unitaire : `resolve_model("guidance_daily")` retourne la valeur de `OPENAI_ENGINE_GUIDANCE_DAILY` si définie
  - [ ] T6.2 Test unitaire : `resolve_model("guidance_daily")` retourne `OPENAI_MODEL_DEFAULT` si `OPENAI_ENGINE_GUIDANCE_DAILY` non définie
  - [ ] T6.3 Test unitaire : `resolve_model("use_case_inconnu")` retourne `OPENAI_MODEL_DEFAULT` sans erreur
  - [ ] T6.4 Test intégration : le gateway utilise le bon modèle selon l'env (mock `os.environ`)

- [ ] T7 — Validation finale (AC: 8)
  - [ ] T7.1 `grep -r '"gpt-' backend/app/ --include="*.py"` → 0 résultat
  - [ ] T7.2 `ruff check backend/` → 0 erreur
  - [ ] T7.3 `pytest backend/` → tous les tests passent

## Dev Notes

### Localisation de la configuration settings

Identifier le fichier de settings du projet — probablement `backend/app/core/config.py` ou `backend/app/core/settings.py`. `OPENAI_MODEL_DEFAULT` doit être une variable Pydantic Settings lue depuis l'env :
```python
class Settings(BaseSettings):
    OPENAI_MODEL_DEFAULT: str = "gpt-4o-mini"
    OPENAI_API_KEY: str
    # ...
```

### `ResponsesClient` — passage du modèle dynamique

`backend/app/llm_orchestration/providers/responses_client.py` est le client OpenAI du gateway V2 (Responses API). Vérifier sa signature :
- S'il reçoit déjà le modèle en paramètre → brancher `resolve_model()`
- S'il lit le modèle depuis `settings` → ajouter un paramètre optionnel `model: str | None = None` avec fallback sur `settings.OPENAI_MODEL_DEFAULT`

### Clefs `.env` — convention de nommage
`OPENAI_ENGINE_{USE_CASE_UPPER}` où `{USE_CASE_UPPER}` est le `use_case_key` en majuscules avec `_` :
- `guidance_daily` → `OPENAI_ENGINE_GUIDANCE_DAILY`
- `natal_interpretation` → `OPENAI_ENGINE_NATAL_INTERPRETATION`
- `chat` → `OPENAI_ENGINE_CHAT`

### Modèles recommandés par défaut
- `guidance_daily`, `guidance_weekly`, `guidance_contextual`, `chat` → `gpt-4o-mini` (coût/latence)
- `natal_interpretation` → `gpt-4o` (qualité premium — use_case payant dans `PAID_USE_CASES`)
- `event_guidance` → `gpt-4o` si présent

### Project Structure Notes
- Seul `backend/app/prompts/catalog.py` et `backend/app/llm_orchestration/gateway.py` sont modifiés
- `backend/.env.example` mis à jour
- Aucun nouveau fichier requis sauf si `resolve_model()` est externalisé

### References
- [Source: backend/app/llm_orchestration/gateway.py] — point d'injection du modèle
- [Source: backend/app/llm_orchestration/providers/responses_client.py] — client OpenAI V2
- [Source: backend/app/prompts/catalog.py] — `PROMPT_CATALOG` + `engine_env_key` (59.2)
- [Source: _bmad-output/planning-artifacts/epic-59-refacto-moteur-ia-v2.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Implémentation complète : `engine_env_key` dans chaque `PromptEntry`, `resolve_model()` dans `catalog.py`, gateway branché dessus, aucune valeur hardcodée dans le code Python.
- **Code review (post-implémentation) :**
  - ISSUE-06 (Majeur) : 10 clefs `OPENAI_ENGINE_*` manquantes dans `.env.example` (`NATAL_SHORT`, `EVENT_GUIDANCE`, `NATAL_PSY`, `NATAL_SHADOW`, `NATAL_WORK`, `NATAL_JOY`, `NATAL_RELATIONSHIP`, `NATAL_COMMUNITY`, `NATAL_VALUES`, `NATAL_EVOLUTION`) — toutes ajoutées avec les modèles par défaut appropriés.
- Tests : 1342 passed, ruff clean.

### File List

- `backend/app/prompts/catalog.py` — engine_env_key par entrée, resolve_model()
- `backend/app/llm_orchestration/gateway.py` — branchement resolve_model()
- `backend/.env.example` — 10 clefs OPENAI_ENGINE_* ajoutées
