# Story 30-5 : Stabilisation Gateway et Prompt Premium

**Status:** done

## 1. Contexte et Objectifs
Stabilisation du Gateway et des schémas Premium (GPT-5) avec un focus sur la robustesse de l'evidence et la parité des contraintes DB/Pydantic.

## 2. Modifications Réalisées

### 2.1 Backend - Evidence Hardening
- **Normalisation des Noms** : `json_schema.name` est désormais lowercase et alphanumérique (conformité SDK).
- **Zéro Faux Positif** : Raffinement du catalogue d'evidence pour exclure les labels trop génériques (ex: "Lion", "carré"). La validation exige désormais des mentions composées (ex: "Soleil en Lion") pour justifier une evidence technique.
- **Regex Alignée** : Extension de `EVIDENCE_ID_PATTERN` à 80 caractères pour correspondre aux schémas de production.
- **Clarification Prompt** : Mise à jour de `seed_30_3_gpt5_prompts.py` : les IDs doivent être justifiés en langage naturel dans le texte libre.

### 2.2 Robustesse & Schémas
- **Parité DB/Pydantic** : Aligné `AstroSectionV2.heading` à **100 caractères** (était 80) pour correspondre à la définition de la base de données.
- **UI Error Boundary** : Ajout d'un composant `ErrorBoundary` dans le frontend pour isoler les erreurs de rendu des interprétations.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/output_validator.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/app/services/chart_json_builder.py`
- `backend/scripts/seed_30_3_gpt5_prompts.py`
- `frontend/src/components/ErrorBoundary.tsx`

## 4. Validation
- [x] Tests unitaires robustesse evidence : 14/14 passent.
- [x] Tests parité schémas : validés par parse Pydantic.
- [x] Tests non-régression service natal V2 : 5/5 passent.
