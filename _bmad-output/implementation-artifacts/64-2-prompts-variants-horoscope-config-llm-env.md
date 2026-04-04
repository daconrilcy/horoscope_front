# Story 64.2 — Prompts variants horoscope par plan + config LLM engine via .env

Status: done

## Story

En tant que système backend,
je veux sélectionner le bon prompt et le bon moteur LLM pour l'horoscope du jour en fonction du plan de l'utilisateur,
afin de délivrer une expérience "résumé" (free) ou "complète" (basic/premium) avec une maîtrise fine des coûts et de la qualité par segment.

## Context

Cette story s'appuie sur le gate de la 64.1. Le backend doit maintenant utiliser le `variant_code` résolu pour appeler le LLM avec les paramètres adéquats (moteur, max_tokens, schéma de sortie).

**Moteurs cibles (configurables via .env) :**
- `horoscope_daily_free` → `gpt-4o-mini` (par défaut)
- `horoscope_daily_full` → `gpt-4o-mini` (par défaut)

## Acceptance Criteria

- [x] **AC1 — Catalogue des prompts mis à jour** : ajout de `horoscope_daily_free` et `horoscope_daily_full`.
- [x] **AC2 — Configuration via .env** : support des clés `OPENAI_ENGINE_HOROSCOPE_DAILY_FREE` et `OPENAI_ENGINE_HOROSCOPE_DAILY_FULL`.
- [x] **AC3 — Schéma de sortie variant "free"** : restreint à `day_climate.summary`.
- [x] **AC4 — Injection du variant dans la couche éditoriale** : le `LLMNarrator` utilise le `variant_code` pour sélectionner le use-case LLM.
- [x] **AC5 — Testabilité unitaire** : validation du choix du modèle en fonction du variant.
- [x] **AC6 — Testabilité intégrative** : appel du router `/daily` passe le bon variant au narrateur.

## Tasks / Subtasks

- [x] T1 — Ajouter les nouveaux `PromptEntry` dans `backend/app/prompts/catalog.py` (AC1, AC3)
  - [x] T1.1 Définir `HOROSCOPE_FREE_OUTPUT_SCHEMA`
  - [x] T1.2 Ajouter `horoscope_daily_free` (max_tokens=500, engine_env_key="OPENAI_ENGINE_HOROSCOPE_DAILY_FREE")
  - [x] T1.3 Ajouter `horoscope_daily_full` (max_tokens=3000, engine_env_key="OPENAI_ENGINE_HOROSCOPE_DAILY_FULL")

- [x] T2 — Mettre à jour `backend/.env.example` (AC2)
  - [x] T2.1 Ajouter les clés `OPENAI_ENGINE_HOROSCOPE_DAILY_FREE` et `OPENAI_ENGINE_HOROSCOPE_DAILY_FULL`

- [x] T3 — Injecter la sélection du variant dans la couche éditoriale (AC4)
  - [x] T3.1 Mettre à jour `LLMNarrator.narrate()` pour accepter `variant_code`
  - [x] T3.2 Mettre à jour `PublicPredictionAssembler.assemble()` pour accepter `variant_code`
  - [x] T3.3 Mettre à jour le router `predictions.py` pour résoudre le variant via le gate et le passer à l'assembler

- [x] T4 — Tests d'intégration (AC6)
  - [x] T4.1 Créer `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`
  - [x] T4.2 Mocker `LLMNarrator.narrate` et vérifier que le `variant_code` reçu correspond au plan de l'utilisateur

## Dev Agent Record

### File List
- `backend/app/prompts/catalog.py`: Ajout des entrées de catalogue et du schéma de sortie pour le plan free.
- `backend/.env.example`: Ajout des variables d'environnement pour la configuration des moteurs LLM.
- `backend/app/prediction/llm_narrator.py`: Support du `variant_code` pour la narration.
- `backend/app/prediction/public_projection.py`: Transmission du `variant_code` à l'assembler.
- `backend/app/api/v1/routers/predictions.py`: Résolution du variant via le gate au niveau de l'API.
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`: Nouveau test d'intégration validant le flux complet.

### Change Log
- Extension du catalogue de prompts pour supporter les deux variantes d'horoscope quotidien.
- Modification de la signature des méthodes `narrate` et `assemble` pour propager le `variant_code`.
- Intégration du gate d'entitlement dans le router `/daily` pour piloter la génération LLM.
- Validation par test d'intégration simulant des utilisateurs free et basic.
