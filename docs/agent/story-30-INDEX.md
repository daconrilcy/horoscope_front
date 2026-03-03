# Chapitre 30 — AstroResponse_v2 & Orchestration GPT-5

## Vue d'ensemble

Le chapitre 30 étend l'infrastructure LLM du chapitre 29 pour lever les blocages de troncation sur l'interprétation natale complète, et adapter le gateway au format natif GPT-5 (Responses API : typed content blocks, `verbosity`, `reasoning.effort`).

**Problème central identifié :**

Le prompt `natal_interpretation` (NATAL_COMPLETE_PROMPT dans `seed_29_prompts.py`) demande `content: 7–12 phrases, max 4000 chars` par section, mais le JSON schema `AstroResponse_v1` en base de données plafonne `sections.content` à **2500 chars** et `summary` à **1200 chars**. Résultat : le LLM génère du contenu riche, le schema strict le rejette, le repair loop retourne une version tronquée. Les `advice` et `highlights` (maxLength=160) forcent les conseils en phrases ultra-courtes, sans nuance.

**Solution en deux stories :**

| Story | Scope | Priorité |
|-------|-------|----------|
| [30-2 — AstroResponse_v2](./story-30-2-astroresponse-v2.md) | Nouveau schema JSON étendu + Pydantic V2, pointé par le use case `natal_interpretation` (payant) uniquement | P0 |
| [30-3 — Gateway GPT-5](./story-30-3-gateway-gpt5.md) | Colonnes `reasoning_effort`/`verbosity` en DB, adaptation `responses_client.py` aux typed content blocks et aux paramètres GPT-5, nouveaux prompts optimisés | P1 |

**Non inclus dans le chapitre 30 :**
- Modification du frontend (l'API response reste compatible : même shape, limites plus larges)
- Refactoring de la structure 3-rôles (system/developer/user avec chart_json en user msg) — reporté
- Mise à jour du use case `natal_interpretation_short` (reste sur v1 + gpt-4o-mini)

---

## Contexte : Discordances v1 identifiées

### Comparaison AstroResponse_v1 (schema DB) vs NATAL_COMPLETE_PROMPT

| Champ | maxLength schema DB (`fix_schemas_strict.py`) | Ce que le prompt demande | Effet |
|-------|----------------------------------------------|--------------------------|-------|
| `summary` | 1200 chars | "10–18 phrases, max 2000 chars" | Troncation systématique |
| `sections[].content` | 2500 chars | "7–12 phrases, max 4000 chars" | Troncation sur toutes les sections |
| `sections[].heading` | 80 chars | "évocateur, max 80 chars" | Limite tendue |
| `highlights[]` item | 160 chars | "6–10 phrases complètes" | Phrases raccourcies |
| `advice[]` item | 160 chars | "6–10 conseils actionnables, nuancés" | Conseils tronqués |
| `evidence[]` item pattern | 3–60 chars | identifiants UPPER_SNAKE_CASE | Identifiants longs rejetés |

### Pydantic `AstroResponseV1` vs JSON schema DB

Le modèle Pydantic dans `backend/app/llm_orchestration/schemas.py` a des limites différentes du JSON schema DB (`fix_schemas_strict.py`). C'est le JSON schema DB qui est envoyé au LLM et governe la troncation — pas le Pydantic. `AstroSection.content` est à 4000 côté Pydantic mais à 2500 dans le JSON schema DB.

---

## Dépendances

```
Story 30-1 (model override via env) : déjà implémenté (gateway.py:214)
    ↓
Story 30-2 (AstroResponse_v2 schema + Pydantic)
    ↓
Story 30-3 (GPT-5 reasoning/verbosity + prompts v2 optimisés)
```

Story 30-3 **dépend** de 30-2 : les nouveaux prompts GPT-5 sont conçus pour remplir les champs v2.

---

## Nouveaux Fichiers par Story

### 30-2 (Backend — Schéma + Pydantic)
- `backend/scripts/seed_30_2_astroresponse_v2.py` ← CRÉER
- `backend/app/llm_orchestration/schemas.py` ← MODIFIER (ajouter `AstroSectionV2`, `AstroResponseV2`)
- `backend/app/api/v1/schemas/natal_interpretation.py` ← MODIFIER (Union type)
- `backend/app/services/natal_interpretation_service_v2.py` ← MODIFIER (désérialiser v2 pour complete)
- `backend/app/tests/unit/test_astro_response_v2.py` ← CRÉER

### 30-3 (Backend — DB + Gateway + Client + Prompts)
- `backend/migrations/versions/YYYYMMDD_0030_add_reasoning_effort_verbosity_to_prompts.py` ← CRÉER (Alembic)
- `backend/app/infra/db/models/llm_prompt.py` ← MODIFIER (colonnes `reasoning_effort`, `verbosity`)
- `backend/app/llm_orchestration/models.py` ← MODIFIER (`UseCaseConfig` + champs GPT-5)
- `backend/app/llm_orchestration/gateway.py` ← MODIFIER (passer `reasoning_effort`/`verbosity` au client)
- `backend/app/llm_orchestration/providers/responses_client.py` ← MODIFIER (typed content blocks + params GPT-5)
- `backend/scripts/seed_30_3_gpt5_prompts.py` ← CRÉER
- `backend/app/tests/unit/test_responses_client_gpt5.py` ← CRÉER
- `backend/app/tests/integration/test_gateway_gpt5_params.py` ← CRÉER

---

## Checklist de Validation Finale

**Story 30-2 :**
- [ ] `python backend/scripts/seed_30_2_astroresponse_v2.py` sans erreur
- [ ] `LlmOutputSchemaModel(name="AstroResponse_v2")` visible en DB
- [ ] `LlmUseCaseConfigModel(key="natal_interpretation").output_schema_id` → id de v2
- [ ] `POST /v1/natal/interpretation?level=complete` → summary > 1200 chars accepté
- [ ] `POST /v1/natal/interpretation?level=short` → schema v1 toujours utilisé
- [ ] `AstroResponseV1` (short) et `AstroResponseV2` (complete) coexistent dans l'API

**Story 30-3 :**
- [ ] Migration Alembic appliquée sans erreur
- [ ] `LlmPromptVersionModel` pour `natal_interpretation` a `reasoning_effort="low"`, `verbosity="high"`
- [ ] `ResponsesClient` inclut `reasoning` et `verbosity` dans le payload pour gpt-5
- [ ] `ResponsesClient` formate le content en typed content blocks pour gpt-5
- [ ] Prompts v2 passent le lint
- [ ] Appel gateway sur `natal_interpretation` avec modèle gpt-5 → résultat non tronqué
