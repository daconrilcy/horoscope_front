# Epic 59 — Refactorisation du Moteur IA : V2 Exclusif, Centralisation Prompts, Précalcul Astrologique, Socle Commun

Status: in-progress

## Objectif

Consolider et industrialiser le moteur IA de l'application en :
1. **Supprimant le chemin V1** (Jinja2 + openai_client) pour faire du gateway V2 (Epic 28) l'unique voie d'exécution.
2. **Centralisant la gestion des prompts** dans un répertoire dédié `backend/app/prompts/` avec un catalogue unique.
3. **Configurant le modèle OpenAI par prompt** via des clefs `.env` individuelles, sans valeur hardcodée.
4. **Précalculant les données astrales** (transits, aspects actifs, phase lunaire) avant l'injection dans les prompts horoscope.
5. **Définissant un socle commun** (`PromptCommonContext`) injecté automatiquement dans tous les prompts : interprétation ou données natales, profil de l'astrologue, période couverte, date du jour.

## Contexte et motivation

### Problèmes identifiés (audit 2026-03-18)

Le moteur IA souffre de plusieurs dettes techniques critiques :

- **Deux chemins coexistants** : V1 (actif, Jinja2 fichiers) et V2 (désactivé, gateway DB), piloté par `LLM_ORCHESTRATION_V2=False`. La V2 est pleinement opérationnelle depuis Epic 28 mais jamais basculée.
- **Parser fragile** : `_parse_guidance_sections` split sur regex `^\d+\.` — capture les sous-numéros dans le texte LLM, pas de structured output.
- **Modèle hardcodé** : `gpt-4o-mini` dans `backend/app/ai_engine/config.py` — pas de flexibilité par use_case.
- **Prompts éparpillés** : templates Jinja2 dans `ai_engine/prompts/`, config en DB dans `llm_orchestration/`, aucun registre centralisé.
- **Contexte astral absent** : les prompts horoscope ne reçoivent pas les transits du jour, aspects dominants, phase lunaire.
- **Socle incohérent** : thème natal, profil de l'astrologue, date du jour injectés de façon hétérogène selon les prompts.

### Décisions verrouillées (Epic 28, à respecter)
- Composition en 4 couches : `system_core` → `developer_prompt` → `persona` → `user_data`
- Structured Outputs (JSON Schema strict) sur toutes les sorties LLM métier
- Prompt Registry états `draft → published → archived`, un seul `published` par use_case
- Personas paramétriques (champs structurés, pas texte libre)

## Périmètre

### In scope
- Suppression complète du chemin V1 et du flag `LLM_ORCHESTRATION_V2`
- Création de `backend/app/prompts/catalog.py` comme registre unifié
- Configuration engine par prompt via `.env` (`OPENAI_ENGINE_{USE_CASE}`)
- Service `AstroContextBuilder` pour précalcul astrologique avant prompt
- Structure `PromptCommonContext` + `CommonContextBuilder` injecté dans tous les prompts
- Mise à jour des templates de prompts existants pour intégrer le socle commun

### Out of scope
- Modification des règles métier astrologiques
- Nouveau frontend
- Nouveaux use_cases
- RAG / vectordb
- Fine-tuning
- Multi-provider (autres que OpenAI)

## Ordre d'exécution et dépendances

```
59.1 — Suppression V1 + bascule V2 exclusive
  ↓
59.2 — Centralisation prompts + catalogue
  ↓
59.3 — Config engine par .env (dépend 59.2 pour engine_env_key dans PromptEntry)
  ↓
59.4 — Précalcul astral (peut commencer en parallèle de 59.3)
  ↓
59.5 — Socle commun PromptCommonContext (dépend 59.1 + 59.2 + 59.4)
```

## Stories de l'Epic 59

### Story 59.1 — Suppression du chemin V1 et migration V2 comme voie unique d'exécution
- Fichier : `_bmad-output/implementation-artifacts/59-1-suppression-v1-migration-v2.md`
- Scope : retirer `LLM_ORCHESTRATION_V2` flag, supprimer `ai_engine/services/generate_service.py`, `prompt_registry.py`, `openai_client.py`, templates Jinja2 V1, faire de `AIEngineAdapter` une façade directe vers `LLMGateway`

### Story 59.2 — Répertoire centralisé des prompts et catalogue unifié
- Fichier : `_bmad-output/implementation-artifacts/59-2-centralisation-prompts-catalogue.md`
- Scope : créer `backend/app/prompts/catalog.py` avec `PROMPT_CATALOG: dict[str, PromptEntry]`, migrer toutes les définitions, validation au démarrage

### Story 59.3 — Configuration engine OpenAI par prompt via `.env`
- Fichier : `_bmad-output/implementation-artifacts/59-3-config-engine-env.md`
- Scope : `engine_env_key` par `PromptEntry`, résolution dynamique dans le gateway, `.env.example` mis à jour, zéro valeur hardcodée

### Story 59.4 — Précalcul des données astrales avant injection dans les prompts horoscope
- Fichier : `_bmad-output/implementation-artifacts/59-4-precalcul-astral.md`
- Scope : `AstroContextBuilder` service, `AstroContextData` avec transits/aspects/phase lunaire/précision, injection dans `guidance_daily` et `guidance_weekly`

### Story 59.5 — Socle commun des prompts : PromptCommonContext
- Fichier : `_bmad-output/implementation-artifacts/59-5-socle-commun-prompts.md`
- Scope : `PromptCommonContext` (natal interprété ou brut, niveau précision, profil astrologue, période, date), `CommonContextBuilder`, injection automatique dans `LLMGateway.execute()`, mise à jour templates

## Fichiers clés impactés

```
backend/app/ai_engine/          ← la plupart supprimés en 59.1
backend/app/llm_orchestration/  ← gateway V2 conservé et étendu
backend/app/services/ai_engine_adapter.py     ← simplifié en 59.1
backend/app/services/guidance_service.py      ← _parse_guidance_sections retiré en 59.1
backend/app/prompts/            ← créé en 59.2 (nouveau répertoire)
backend/app/prompts/catalog.py  ← créé en 59.2
backend/app/prompts/common_context.py         ← créé en 59.5
backend/app/services/astro_context_builder.py ← créé en 59.4
backend/.env.example            ← mis à jour en 59.3
```
