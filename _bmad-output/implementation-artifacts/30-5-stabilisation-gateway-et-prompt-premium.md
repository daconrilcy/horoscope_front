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

## 5. Correctifs Post-Validation (runtime réel)

Date: 2026-03-03

Après vérification en exécution réelle (backend lancé + scénario `curl` bout-en-bout), des écarts runtime non couverts initialement ont été corrigés.

### 5.1 Erreurs upstream préservées (plus de 500 générique)
- Fichier: `backend/app/llm_orchestration/gateway.py`
- Correctif: ne plus encapsuler `UpstreamRateLimitError` / `UpstreamTimeoutError` / `UpstreamError` dans `GatewayError`.
- Impact: le router renvoie les codes HTTP corrects (timeout/rate-limit) au lieu d'un `500 internal_error`.

### 5.2 Robustesse chart_json (valeurs null)
- Fichier: `backend/app/services/chart_json_builder.py`
- Correctif: gestion de `speed_longitude=None` et fallback `orb_used <- orb` quand `orb_used` est absent/null.
- Impact: suppression d'un crash de sérialisation sur certains charts (plus de `500` sur build contexte natal).

### 5.3 Seed use-case court natal réparé
- Fichier: `backend/scripts/seed_natal_short.py`
- Correctifs:
  - accès ID use-case existant corrigé
  - valeurs par défaut ajoutées pour les champs obligatoires du catalogue use-case.
- Impact: création/publishing fiable de `natal_interpretation_short`.

### 5.4 Seed GPT-5 rendu robuste sur UUID schema
- Fichier: `backend/scripts/seed_30_3_gpt5_prompts.py`
- Correctif: parsing explicite `output_schema_id` string -> `UUID` avant `db.get(...)`.
- Impact: évite les échecs silencieux de liaison prompt/schema.

### 5.5 Vérifications effectuées
- `pytest -q backend/app/llm_orchestration/tests/test_gateway_errors.py` : OK
- `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/llm_orchestration/tests/test_gateway_errors.py` : OK
- Scénario `curl` réel: register -> checkout -> geocoding -> birth-data -> natal-chart -> `/v1/natal/interpretation` : OK (200 final avec payload interprétation).

### 5.6 Correctif validation evidence (502 en complet)
- Symptôme observé (2026-03-03): `gateway_validation_failed_starting_repair` avec erreurs `Hallucinated evidence` / `Orphan evidence` provoquant un `502` sur `/v1/natal/interpretation`.
- Fichier: `backend/app/llm_orchestration/services/output_validator.py`
- Correctifs:
  - normalisation d'aliases evidence (`*_IN_*`, `CONJUNCTION_*`, formes `ASPECT_*` legacy, suffixes ponctuation),
  - matching texte accent-insensitive (`Vénus` vs `Venus`),
  - règle `Orphan evidence` abaissée en warning non bloquant.
- Validation:
  - `pytest -q backend/app/tests/unit/test_output_validator.py` : OK.
