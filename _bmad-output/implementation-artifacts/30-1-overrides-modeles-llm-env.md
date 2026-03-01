# Story 30.1: Surcharge des modèles LLM par variable d'environnement

Status: done

## Story

As a developer or ops,
I want surcharger les modèles LLM utilisés par le gateway via des variables d'environnement,
so that je puisse tester rapidement de nouveaux modèles ou ajuster le ratio coût/qualité par service sans modifier la base de données des prompts.

## Acceptance Criteria

1. [x] Le `LLMGateway` vérifie la présence de variables d'environnement suivant le pattern `LLM_MODEL_OVERRIDE_{USE_CASE_KEY_UPPER}` (ex: `LLM_MODEL_OVERRIDE_NATAL_INTERPRETATION`).
2. [x] Si la variable est présente et non vide, sa valeur outrepasse le champ `model` défini dans la version de prompt active en base de données.
3. [x] Le modèle réellement utilisé (après surcharge éventuelle) est tracé dans `LlmCallLogModel` (champ `model`).
4. [x] Le modèle réellement utilisé est retourné dans `GatewayResult.meta.model`.
5. [x] Le fichier `backend/.env.example` inclut des exemples documentés pour les services principaux (`natal_interpretation`, `natal_interpretation_short`, `chat`).
6. [x] Des tests unitaires valident que la surcharge fonctionne pour différents use cases et que le modèle DB est préservé si aucune variable n'est définie.

## Tasks / Subtasks

- [x] Mettre à jour `backend/app/llm_orchestration/gateway.py` pour implémenter la logique de surcharge.
- [x] Modifier la capture des métadonnées dans le gateway pour utiliser le modèle effectif.
- [x] Documenter les nouvelles variables dans `backend/.env.example`.
- [x] Créer les tests unitaires dans `backend/app/llm_orchestration/tests/test_gateway_model_override.py`.

## Dev Agent Record

### File List
- `backend/app/llm_orchestration/models.py`: Ajout de `model_override_active` dans `GatewayMeta`.
- `backend/app/llm_orchestration/gateway.py`: Implémentation de la logique de surcharge avec normalisation robuste.
- `backend/.env.example`: Documentation des nouvelles variables d'environnement.
- `backend/app/llm_orchestration/tests/test_gateway_model_override.py`: Tests unitaires pour la surcharge et la normalisation.
