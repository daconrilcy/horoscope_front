# Story 59.2 : Répertoire centralisé des prompts et catalogue unifié

Status: ready-for-dev

## Story

En tant que développeur backend,
je veux un répertoire `backend/app/prompts/` avec un catalogue Python centralisé listant tous les prompts de l'application,
afin d'avoir une source unique de vérité pour les métadonnées de configuration des prompts et détecter au démarrage toute incohérence entre le code et la base de données.

## Acceptance Criteria

1. Le répertoire `backend/app/prompts/` existe avec un `__init__.py` et un `catalog.py`.
2. `catalog.py` expose `PROMPT_CATALOG: dict[str, PromptEntry]` où la clef est le `use_case_key`.
3. `PromptEntry` est un dataclass ou Pydantic model avec les champs :
   - `name: str` — nom unique lisible (ex: `"guidance-daily-v1"`)
   - `description: str` — description courte du prompt
   - `use_case_key: str` — identifiant du use_case (ex: `"guidance_daily"`)
   - `engine_env_key: str` — clef `.env` pour le modèle (ex: `"OPENAI_ENGINE_GUIDANCE_DAILY"`)
   - `max_tokens: int`
   - `temperature: float`
   - `output_schema: dict | None` — JSON Schema de validation de la sortie structurée
4. Les use_cases suivants sont tous présents dans le catalogue :
   - `guidance_daily`, `guidance_weekly`, `guidance_contextual`
   - `natal_interpretation`
   - `chat` (ou le nom exact utilisé en DB)
   - Tout autre use_case existant en DB (vérifier `LlmUseCaseConfigModel`)
5. Au démarrage de l'application (lifespan FastAPI), un check compare les use_cases actifs en DB avec le catalogue et lève une `ConfigurationError` explicite si un use_case DB est absent du catalogue.
6. `LLMGateway` et `PromptRegistryV2` peuvent optionnellement consommer le catalogue pour valider la cohérence, mais ce n'est pas obligatoire dans cette story — l'objectif est de créer le catalogue en premier.
7. `pytest backend/` passe sans erreur.
8. `ruff check backend/` passe sans warning.

## Tasks / Subtasks

- [ ] T1 — Créer le répertoire et les fichiers de base (AC: 1)
  - [ ] T1.1 Créer `backend/app/prompts/__init__.py` (vide ou avec exports)
  - [ ] T1.2 Créer `backend/app/prompts/catalog.py`

- [ ] T2 — Définir `PromptEntry` (AC: 3)
  - [ ] T2.1 Choisir Pydantic `BaseModel` (cohérence avec le reste du backend)
  - [ ] T2.2 Implémenter `PromptEntry` avec les 7 champs requis
  - [ ] T2.3 Ajouter une validation : `name` doit être unique dans le catalogue (validator `@model_validator` ou vérification à l'initialisation)

- [ ] T3 — Peupler `PROMPT_CATALOG` (AC: 4)
  - [ ] T3.1 Lire `backend/app/llm_orchestration/seeds/use_cases_seed.py` pour identifier les use_cases existants
  - [ ] T3.2 Lire `backend/app/llm_orchestration/services/prompt_registry_v2.py` pour les clefs utilisées
  - [ ] T3.3 Créer une entrée `PromptEntry` pour chaque use_case identifié
  - [ ] T3.4 Utiliser des valeurs de `max_tokens` et `temperature` cohérentes avec les configs existantes (ex: `guidance_daily` → 1200 tokens, 0.7 temp)
  - [ ] T3.5 Laisser `output_schema=None` pour les use_cases sans structured output, renseigner le JSON Schema pour ceux qui en ont un

- [ ] T4 — Validation au démarrage (AC: 5)
  - [ ] T4.1 Identifier le lifespan FastAPI (`backend/app/main.py` ou `backend/app/core/lifespan.py`)
  - [ ] T4.2 Créer `backend/app/prompts/validators.py` avec `validate_catalog_vs_db(db: Session) -> None`
  - [ ] T4.3 La fonction charge tous les `LlmUseCaseConfigModel` en DB, compare avec `PROMPT_CATALOG.keys()`, lève `ConfigurationError` si écart
  - [ ] T4.4 Brancher `validate_catalog_vs_db` dans le lifespan (après création des tables DB, avant premier appel LLM)
  - [ ] T4.5 Logger un résumé positif si tout est cohérent : `logger.info("Prompt catalog OK — %d use_cases validated", n)`

- [ ] T5 — Tests unitaires (AC: 7)
  - [ ] T5.1 Test : `PROMPT_CATALOG` contient tous les use_cases attendus
  - [ ] T5.2 Test : toutes les clefs `name` sont uniques dans le catalogue
  - [ ] T5.3 Test : `validate_catalog_vs_db` lève `ConfigurationError` si un use_case DB est absent du catalogue (mock DB)
  - [ ] T5.4 Test : `validate_catalog_vs_db` ne lève pas d'erreur si tout est cohérent

- [ ] T6 — Validation finale (AC: 8)
  - [ ] T6.1 `ruff check backend/` → 0 erreur
  - [ ] T6.2 `pytest backend/` → tous les tests passent

## Dev Notes

### Structure cible de `catalog.py`

```python
# backend/app/prompts/catalog.py
from __future__ import annotations
from pydantic import BaseModel, model_validator
from typing import Any

class PromptEntry(BaseModel):
    name: str                          # Nom unique lisible
    description: str                   # Description courte
    use_case_key: str                  # Clef use_case (clef du dict PROMPT_CATALOG)
    engine_env_key: str                # Clef .env pour le modèle OpenAI
    max_tokens: int
    temperature: float
    output_schema: dict[str, Any] | None = None

PROMPT_CATALOG: dict[str, PromptEntry] = {
    "guidance_daily": PromptEntry(
        name="guidance-daily-v1",
        description="Guidance astrologique quotidienne personnalisée",
        use_case_key="guidance_daily",
        engine_env_key="OPENAI_ENGINE_GUIDANCE_DAILY",
        max_tokens=1200,
        temperature=0.7,
        output_schema={...},   # JSON Schema structuré (summary, key_points, etc.)
    ),
    "guidance_weekly": PromptEntry(...),
    "guidance_contextual": PromptEntry(...),
    "natal_interpretation": PromptEntry(...),
    "chat": PromptEntry(...),
    # + autres use_cases existants en DB
}
```

### Use_cases à identifier dans la DB

Lire `backend/app/llm_orchestration/seeds/use_cases_seed.py` et les migrations pour la liste exhaustive. Les use_cases connus d'après l'audit :
- `guidance_daily`
- `guidance_weekly`
- `guidance_contextual`
- `natal_interpretation`
- `chat` (ou `chat_astrologue`)
- `event_guidance` (si présent — vérifier `PAID_USE_CASES` dans `gateway.py`)

### Cohérence avec `PromptRegistryV2`

`PromptRegistryV2` (`backend/app/llm_orchestration/services/prompt_registry_v2.py`) résout actuellement le prompt publié par `use_case_key` depuis la DB avec un cache 60s. Le catalogue ne remplace pas cette résolution DB — il complète avec les métadonnées de config (engine_env_key, etc.) que la DB ne stocke pas.

### Modèle DB des use_cases

`LlmUseCaseConfigModel` est dans `backend/app/infra/db/models/`. Vérifier les champs disponibles pour comprendre ce qui est déjà en DB vs ce qui doit être dans le catalogue.

### `ConfigurationError`

Utiliser une exception existante du projet si elle existe, sinon créer `backend/app/core/exceptions.py` ou `backend/app/prompts/exceptions.py` avec :
```python
class ConfigurationError(RuntimeError):
    """Raised when the prompt catalog is inconsistent with the database."""
```

### Project Structure Notes

```
backend/app/prompts/
  __init__.py
  catalog.py          ← PROMPT_CATALOG + PromptEntry
  validators.py       ← validate_catalog_vs_db()
  exceptions.py       ← ConfigurationError (si pas déjà dans core)
```

Pas de fichiers de templates dans ce répertoire dans cette story — les prompts restent en DB. Ce répertoire est uniquement pour les métadonnées Python.

### References
- [Source: backend/app/llm_orchestration/gateway.py#L44] — `PAID_USE_CASES` liste de référence
- [Source: backend/app/llm_orchestration/seeds/use_cases_seed.py] — use_cases seedés en DB
- [Source: backend/app/llm_orchestration/services/prompt_registry_v2.py] — résolution DB actuelle
- [Source: _bmad-output/planning-artifacts/epic-59-refacto-moteur-ia-v2.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

### File List
