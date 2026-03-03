# Story 30-5 : Stabilisation Gateway et Prompt Premium

**Status:** done

## 1. Contexte et Objectifs
Stabilisation du Gateway et des schémas Premium (GPT-5) avec un focus sur la robustesse de l'evidence et la parité des contraintes DB/Pydantic.

## 2. Modifications Réalisées

### 2.1 Backend - Evidence Hardening
- **Normalisation des Noms** : `json_schema.name` est désormais lowercase et alphanumérique (conformité SDK).
- **Zéro Faux Positif** : Raffinement du catalogue d'evidence pour exclure les labels trop génériques.
- **Regex Alignée** : Extension de `EVIDENCE_ID_PATTERN` à 80 caractères.
- **Clarification Prompt** : Les IDs doivent être justifiés en langage naturel dans le texte libre.

### 2.2 Robustesse & Schémas
- **Parité DB/Pydantic V2** : Aligné les limites Premium dans `schemas.py` et `fix_schemas_strict.py` sur le seed canonique :
    - `title` : 160 caractères.
    - `heading` : 100 caractères.
    - `sections.maxItems` : 10.
    - `highlights`/`advice.maxItems` : 12.
    - `disclaimers.maxLength` : 300 caractères.
- **UI Error Boundary** : Ajout d'un composant `ErrorBoundary` dans le frontend.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/output_validator.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/app/services/chart_json_builder.py`
- `backend/scripts/fix_schemas_strict.py`
- `backend/scripts/seed_30_3_gpt5_prompts.py`
- `frontend/src/components/ErrorBoundary.tsx`

## 4. Validation
- [x] Tests unitaires robustesse evidence : 14/14 passent.
- [x] Tests parité schémas : validés par parse Pydantic.
- [x] Tests non-régression service natal V2 : 5/5 passent.
