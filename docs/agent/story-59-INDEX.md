# Epic 59 — Refactorisation du Moteur IA V2 : Index des Stories

**Epic :** [epic-59-refacto-moteur-ia-v2.md](../../_bmad-output/planning-artifacts/epic-59-refacto-moteur-ia-v2.md)

## Contexte

Cet epic consolide le moteur IA en supprimant le chemin V1 hérité, en centralisant la gestion des prompts, en configurant les modèles OpenAI par use_case via `.env`, en précalculant les données astrales avant injection dans les prompts horoscope, et en définissant un socle commun de contexte pour tous les prompts.

**Audit source :** réalisé le 2026-03-18 sur le codebase — voir audit complet dans la conversation Cyril/Claude.

## Dépendances d'exécution

```
59.1 ──► 59.2 ──► 59.3
                    │
         59.2 ──► 59.4 ──► 59.5
```

**59.1 doit être complète avant 59.2.** Les stories 59.3, 59.4 peuvent être développées en parallèle après 59.2. La story 59.5 dépend de 59.1 + 59.2 + 59.4.

## Stories

| Story | Titre | Fichier | Statut |
|-------|-------|---------|--------|
| 59.1 | Suppression V1 + migration V2 exclusive | [59-1-suppression-v1-migration-v2.md](../../_bmad-output/implementation-artifacts/59-1-suppression-v1-migration-v2.md) | ready-for-dev |
| 59.2 | Centralisation prompts + catalogue unifié | [59-2-centralisation-prompts-catalogue.md](../../_bmad-output/implementation-artifacts/59-2-centralisation-prompts-catalogue.md) | ready-for-dev |
| 59.3 | Config engine OpenAI par prompt via `.env` | [59-3-config-engine-env.md](../../_bmad-output/implementation-artifacts/59-3-config-engine-env.md) | ready-for-dev |
| 59.4 | Précalcul des données astrales | [59-4-precalcul-astral.md](../../_bmad-output/implementation-artifacts/59-4-precalcul-astral.md) | ready-for-dev |
| 59.5 | Socle commun des prompts — PromptCommonContext | [59-5-socle-commun-prompts.md](../../_bmad-output/implementation-artifacts/59-5-socle-commun-prompts.md) | ready-for-dev |

## Fichiers impactés (synthèse)

### Supprimés (59.1)
- `backend/app/ai_engine/services/generate_service.py`
- `backend/app/ai_engine/services/prompt_registry.py`
- `backend/app/ai_engine/providers/openai_client.py`
- `backend/app/ai_engine/prompts/guidance_*_v1.jinja2` (3 fichiers)

### Modifiés
- `backend/app/services/ai_engine_adapter.py` (59.1 — simplifié)
- `backend/app/services/guidance_service.py` (59.1 — suppression parser heuristique)
- `backend/app/llm_orchestration/gateway.py` (59.3, 59.5 — résolution modèle + socle commun)
- `backend/.env.example` (59.3)

### Créés
- `backend/app/prompts/__init__.py` (59.2)
- `backend/app/prompts/catalog.py` (59.2)
- `backend/app/prompts/validators.py` (59.2)
- `backend/app/prompts/common_context.py` (59.5)
- `backend/app/services/astro_context_builder.py` (59.4)

## Décisions d'architecture

- Le gateway V2 (`LLMGateway`) est l'unique chemin d'exécution — pas de flag feature.
- Structured Outputs (JSON Schema) pour toutes les sorties LLM — pas de parsing heuristique.
- Composition 4 couches inchangée : `system_core` → `developer_prompt` → `persona` → `user_data`.
- `PromptCommonContext` fusionné en tête du context, avec priorité au contexte use_case en cas de conflit.
- `AstroContextBuilder` est un aggregateur/adaptateur — ne réimplémente aucune logique de calcul.
