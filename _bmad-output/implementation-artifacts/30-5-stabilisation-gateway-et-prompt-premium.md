# Story 30-5 : Stabilisation Gateway et Prompt Premium (Phase 0)

**Status:** done

## 1. Contexte et Objectifs
Cette story vise à corriger les écarts critiques identifiés lors de l'audit de production du Gateway LLM afin de stabiliser le service avant le refactor global.

## 2. Modifications Réalisées

### 2.1 Backend - LLM Gateway (`gateway.py`)
- **Correction `schema.name`** : Le champ `name` du payload `json_schema` utilise désormais `schema_model.name` (ex: `AstroResponse_v2`) au lieu de la clé générique du use-case.
- **Blocage Schema Manquant** : Levée d'une `GatewayConfigError` si un use-case dans `_SCHEMA_REQUIRED_USE_CASES` est appelé sans schéma configuré.
- **Guard générique schema (M1)** : Second guard couvrant tout use-case avec `output_schema_id` configuré mais schema absent en DB.
- **Constantes reasoning dédupliquées (M2)** : `_REASONING_PREFIXES`, `_REASONING_EXACT` et `_SCHEMA_REQUIRED_USE_CASES` extraits au niveau module.
- **Fallback locale-aware (L2)** : `build_user_payload` retourne désormais un message en français pour `locale="fr"` au lieu de l'anglais hardcodé.
- **Validation evidence catalog (M3)** : `validate_output` accepte maintenant un `evidence_catalog` optionnel. Quand fourni (via `context["evidence_catalog"]`), tout identifiant dans le champ `evidence` absent du catalogue est signalé comme warning (hallucination potentielle).

### 2.2 Prompts - GPT-5 Premium (`seed_30_3_gpt5_prompts.py`)
- **Règle Evidence Bidirectionnelle** : "TOUT IDENTIFIANT PRÉSENT DANS evidence DOIT ÊTRE MENTIONNÉ AU MOINS UNE FOIS DANS summary/sections/highlights/advice."
- Fichier commité (M4) avec message explicite traçant l'ajout de la règle.

### 2.3 Service Natal (`natal_interpretation_service_v2.py`)
- **Suppression du bruit "question"** : Le champ `question` n'est plus transmis dans `user_input` pour le use-case `natal_interpretation` (niveau `complete`).

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/output_validator.py`
- `backend/scripts/seed_30_3_gpt5_prompts.py` (créé + commité)
- `backend/app/services/natal_interpretation_service_v2.py`
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py` (créé en code review)
- `backend/app/tests/unit/test_gateway_modes.py` (assertions mises à jour)

## 4. Validation
- [x] Vérification manuelle des payloads sortants vers l'AI Engine.
- [x] Test de non-régression sur le service natal (3 tests automatisés — `test_natal_interpretation_service_v2.py`).
- [x] Tests gateway modes : 6/6 passent.
- [x] Validation du seed de prompt optimisé (commité — M4).
- [x] Suite complète 11/11 tests verts.
