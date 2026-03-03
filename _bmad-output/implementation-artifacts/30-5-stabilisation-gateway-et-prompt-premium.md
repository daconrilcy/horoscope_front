# Story 30-5 : Stabilisation Gateway et Prompt Premium

**Status:** done

## 1. Contexte et Objectifs
Stabilisation du Gateway et des schémas Premium (GPT-5) avec un focus sur la robustesse de l'evidence, la parité totale des contraintes DB/Pydantic, et le refactor pour la maintenabilité.

## 2. Modifications Réalisées

### 2.1 Backend - Gateway & Validation
- **Refactor `execute()`** : Décomposition de la méthode massive en helpers spécialisés (`_resolve_config`, `_resolve_persona`, `_resolve_schema`, `_handle_validation`) pour réduire la complexité cyclomatique.
- **Evidence Hardening** : Utilisation de regex avec word boundaries (`\b`) pour la validation bidirectionnelle, évitant les faux positifs sur les termes courts (ex: "sun" dans "sunday").
- **Centralisation Regex** : Unification du pattern d'evidence via `EVIDENCE_ID_REGEX` dans `models.py`.
- **Logging UUID** : Ajout de logs explicites pour les UUIDs de personas malformés.

### 2.2 Robustesse & Schémas (Parité 100% Strict)
- **Enforcement Pydantic** : Tous les champs marqués `required` en DB sont désormais obligatoires dans Pydantic (`Field(...)`).
- **Astro V2 (Premium)** : Title (160), Heading (100), Sections (10), Highlights/Advice (12), Disclaimers (3 max, 300 chars).
- **Astro V1 (Standard)** : Evidence obligatoire, Disclaimers (3 max, 200 chars).
- **Chat V1/V2** : `suggested_replies` (min 1), `intent` (enum stricte en V2), `safety_notes` (200 chars max).
- **UI Error Boundary** : Remplacement des classes Tailwind par du CSS Vanilla (inline styles) dans `ErrorBoundary.tsx` pour compatibilité avec le projet.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/app/llm_orchestration/services/output_validator.py`
- `backend/app/llm_orchestration/tests/test_responses_client.py`
- `frontend/src/components/ErrorBoundary.tsx`

## 4. Validation
- [x] Tests unitaires robustesse evidence : 14/14 passent.
- [x] Tests parité schémas V1/V2 : 100% alignés.
- [x] Tests ResponsesClient : 2/2 passent (mocks OpenAI corrigés).
