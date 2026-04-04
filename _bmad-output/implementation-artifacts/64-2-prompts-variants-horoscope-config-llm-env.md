# Story 64.2 — Prompts variants horoscope par plan + config LLM engine via .env

Status: todo

## Story

En tant que système backend,
je veux sélectionner le bon prompt et le bon moteur LLM pour l'horoscope du jour en fonction du `variant_code` résolu par le gate,
afin que la génération LLM produise réellement uniquement ce qu'autorise le plan (et non un contenu complet masqué côté UI).

## Context

Dépend de **Story 64.1** (gate + variant_code résolu).

Le `PROMPT_CATALOG` (`backend/app/prompts/catalog.py`) contient déjà les prompts `guidance_daily`, `natal_interpretation`, etc. avec le pattern `engine_env_key` défini en Epic 59.3.

Pour l'horoscope du jour (`/dashboard/horoscope`), le flow passe par `DailyPredictionService` → `PredictionComputeRunner` → `EngineOrchestrator` (calcul numérique) → couche éditoriale LLM (`PredictionEditorialService`).

**La restriction de plan s'applique au niveau de la couche éditoriale LLM** :
- variant `"summary_only"` → prompt qui ne demande au LLM que `day_climate.summary`
- variant `"full"` → prompt complet actuel (inchangé)

Les calculs numériques de l'engine ne sont PAS modifiés (scores, transits, domaines continuent d'être calculés).

## Acceptance Criteria

**AC1 — Deux nouveaux PromptEntry dans le catalog**
**Given** `backend/app/prompts/catalog.py`  
**When** le fichier est inspecté  
**Then** les clés `"horoscope_daily_free"` et `"horoscope_daily_full"` existent dans `PROMPT_CATALOG`  
**And** chacune a un `engine_env_key` distinct (`OPENAI_ENGINE_HOROSCOPE_DAILY_FREE` et `OPENAI_ENGINE_HOROSCOPE_DAILY_FULL`)

**AC2 — Config .env.example mise à jour**
**Given** `backend/.env.example`  
**When** le fichier est inspecté  
**Then** les clés `OPENAI_ENGINE_HOROSCOPE_DAILY_FREE` et `OPENAI_ENGINE_HOROSCOPE_DAILY_FULL` sont présentes avec des valeurs par défaut documentées (ex: `gpt-4o-mini`)

**AC3 — Sélection du prompt selon variant_code**
**Given** un utilisateur avec `variant_code="summary_only"`  
**When** la couche éditoriale LLM est invoquée  
**Then** le use_case résolu est `"horoscope_daily_free"` (et non `"horoscope_daily_full"`)

**AC4 — Le prompt free ne génère que day_climate.summary**
**Given** le prompt `horoscope_daily_free` invoqué avec le LLM  
**When** la réponse LLM est parsée  
**Then** seul `day_climate.summary` est attendu dans le JSON Schema de sortie  
**And** les autres champs (`domain_ranking`, `time_windows`, `turning_point`, `best_window`, `astro_foundation`, `daily_advice`) ne sont pas demandés au LLM

**AC5 — Le prompt full est inchangé**
**Given** un utilisateur avec `variant_code="full"`  
**When** la couche éditoriale LLM est invoquée  
**Then** le comportement est identique à l'existant — aucune régression

**AC6 — Tests unitaires**
**Given** `backend/app/tests/unit/test_horoscope_daily_prompt_variant.py`  
**When** les tests sont exécutés  
**Then** la sélection `summary_only → horoscope_daily_free` et `full → horoscope_daily_full` est couverte

**AC7 — Zéro régression pytest + ruff**
**When** `pytest backend/` et `ruff check backend/` sont exécutés  
**Then** 0 erreur

## Tasks / Subtasks

- [ ] T1 — Ajouter les nouveaux PromptEntry dans `catalog.py` (AC1)
  - [ ] T1.1 Lire entièrement `backend/app/prompts/catalog.py`
  - [ ] T1.2 Définir le JSON Schema de sortie pour le variant free :
    ```python
    HOROSCOPE_FREE_OUTPUT_SCHEMA = {
        "type": "object",
        "required": ["day_climate"],
        "properties": {
            "day_climate": {
                "type": "object",
                "required": ["summary"],
                "properties": {"summary": {"type": "string"}}
            }
        }
    }
    ```
  - [ ] T1.3 Ajouter à `PROMPT_CATALOG`:
    ```python
    "horoscope_daily_free": PromptEntry(
        name="horoscope-daily-free-v1",
        description="Horoscope du jour restreint au résumé (plan free)",
        use_case_key="horoscope_daily_free",
        engine_env_key="OPENAI_ENGINE_HOROSCOPE_DAILY_FREE",
        max_tokens=500,
        temperature=0.7,
        output_schema=HOROSCOPE_FREE_OUTPUT_SCHEMA,
    ),
    "horoscope_daily_full": PromptEntry(
        name="horoscope-daily-full-v1",
        description="Horoscope du jour complet (plan basic/premium)",
        use_case_key="horoscope_daily_full",
        engine_env_key="OPENAI_ENGINE_HOROSCOPE_DAILY_FULL",
        max_tokens=3000,
        temperature=0.7,
        output_schema=None,  # schéma complet géré par le gateway existant
    ),
    ```

- [ ] T2 — Mettre à jour `.env.example` (AC2)
  - [ ] T2.1 Ajouter dans `backend/.env.example` :
    ```
    OPENAI_ENGINE_HOROSCOPE_DAILY_FREE=gpt-4o-mini
    OPENAI_ENGINE_HOROSCOPE_DAILY_FULL=gpt-4o-mini
    ```

- [ ] T3 — Injecter la sélection de variant dans la couche éditoriale (AC3, AC4, AC5)
  - [ ] T3.1 Lire `backend/app/prediction/engine_orchestrator.py` et identifier où `PredictionEditorialService` est appelé
  - [ ] T3.2 Passer `variant_code` depuis `DailyPredictionService` jusqu'à l'appel éditorial
  - [ ] T3.3 Dans la couche éditoriale, mapper `variant_code → use_case_key` :
    ```python
    def _resolve_editorial_use_case(variant_code: str) -> str:
        return "horoscope_daily_free" if variant_code == "summary_only" else "horoscope_daily_full"
    ```
  - [ ] T3.4 Appeler `HoroscopeDailyEntitlementGate.check_and_get_variant()` dans le router `/predictions` avant le compute (ou dans `DailyPredictionService`)
  - [ ] T3.5 Propager `variant_code` jusqu'à la sélection du prompt éditorial

- [ ] T4 — Créer le template de prompt `horoscope_daily_free` dans le système de prompt DB (seed use_case)
  - [ ] T4.1 Vérifier comment les use_cases sont seedés (cf. `backend/app/llm_orchestration/seeds/use_cases_seed.py`)
  - [ ] T4.2 Ajouter le use_case `horoscope_daily_free` avec le system prompt limité au résumé

- [ ] T5 — Tests unitaires (AC6)
  - [ ] T5.1 Créer `backend/app/tests/unit/test_horoscope_daily_prompt_variant.py`
  - [ ] T5.2 Tester la résolution `summary_only → horoscope_daily_free`
  - [ ] T5.3 Tester la résolution `full → horoscope_daily_full`

- [ ] T6 — Validation finale (AC7)
  - [ ] T6.1 `pytest backend/` → 0 régression
  - [ ] T6.2 `ruff check backend/` → 0 erreur

## Dev Notes

### Architecture du flow éditorial

```
DailyPredictionService.compute()
  → HoroscopeDailyEntitlementGate.check_and_get_variant(db, user_id)  ← NOUVEAU
  → PredictionComputeRunner.run_with_timeout(...)           ← inchangé (calculs numériques)
  → PredictionEditorialService.generate(variant_code=...)   ← MODIFIÉ
      → _resolve_editorial_use_case(variant_code)
      → LLMGateway.execute(use_case="horoscope_daily_free"|"horoscope_daily_full", ...)
```

### Payload public selon variant

Pour `summary_only` : le `PublicPredictionAssembler` ne doit inclure dans la réponse API que `day_climate.summary`. Les autres champs sont omis ou null — **pas générés, pas seulement masqués**. Vérifier comment `PublicPredictionAssembler` construit le payload depuis le bundle.

### Cohérence avec le cache de prédiction

Si la prédiction est mise en cache (`was_reused=True`), vérifier que le cache est segmenté par `variant_code` pour éviter qu'un cache "full" serve une requête "free" ou vice versa. Si le cache ne supporte pas la segmentation, invalider le cache ou ajouter `variant_code` comme clé de cache.

### Prompt system pour horoscope_daily_free

Le system prompt de `horoscope_daily_free` doit explicitement indiquer au LLM de ne générer que le résumé du climat du jour (`day_climate.summary`), sans les sections détaillées, avec le même ton et la même qualité éditoriale que le prompt complet — simplement plus court et centré sur l'essentiel.
