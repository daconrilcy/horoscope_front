# Story 30.2: AstroResponse_v2 — Schéma Étendu pour l'Interprétation Premium

Status: done

## Story

As an astrologue premium,
I want générer des interprétations complètes sans troncations arbitraires,
So that l'utilisateur reçoive la pleine profondeur de l'analyse demandée au LLM.

## Contexte et Objectifs

Cette story corrige les limitations du schéma `AstroResponse_v1` qui tronquait systématiquement le contenu généré par le LLM pour les interprétations complètes (payantes).
- Création d'un nouveau schéma `AstroResponse_v2` avec des limites élargies (summary: 2800 chars, content: 6500 chars).
- Mise à jour du use case `natal_interpretation` pour pointer vers ce nouveau schéma.
- Adaptation du service backend pour gérer la désérialisation polymorphique (v1/v2).

**Non-objectifs initiaux (révisés) :**
- Pas de modification du frontend (compatibilité ascendante via les mêmes noms de champs). ✓
- ~~Pas de modification de `AstroResponse_v1`~~ → **Révisé** : les limites de v1 ont été ajustées lors de cette story pour éliminer une troncature observée en production sur les interprétations courtes (summary 1200→2000, content 2500→4000). Ce changement est documenté dans le tableau ci-dessous.

## Acceptance Criteria

### AC1: Nouveau JSON schema en DB après seed
**Given** la base de données existante
**When** le script `seed_30_2_astroresponse_v2.py` est exécuté
**Then** `AstroResponse_v2` est créé dans `llm_output_schemas` avec les limites élargies
**And** `natal_interpretation` pointe vers l'ID de `AstroResponse_v2`
**And** `natal_interpretation_short` reste sur `AstroResponse_v1`

### AC2: Schéma v2 compatible avec OpenAI Structured Outputs (strict=True)
**Given** le schéma JSON v2
**When** envoyé à l'API OpenAI
**Then** il respecte toutes les contraintes de `strict: true` (pas de champs optionnels sans default, additionalProperties: false)

### AC3: Modèle Pydantic AstroResponseV2
**Given** le fichier `schemas.py`
**When** `AstroResponseV2` est défini
**Then** il reflète exactement les contraintes du schéma JSON en base de données

### AC4: Désérialisation dynamique dans NatalInterpretationServiceV2
**Given** un résultat du gateway LLM
**When** le niveau est "complete"
**Then** le service tente de désérialiser en `AstroResponseV2`
**And** il retombe sur `AstroResponseV1` en cas de fallback vers le use case "short"

### AC5: API Response polymorphique
**Given** l'endpoint `/v1/natal/interpretation`
**When** une interprétation est retournée
**Then** le schéma de réponse accepte indifféremment `AstroResponseV1` ou `AstroResponseV2`

## Tasks / Subtasks

### Subtask 30.2.1: Modèles Pydantic (Backend)
- [x] Ajouter `AstroSectionV2` et `AstroResponseV2` dans `backend/app/llm_orchestration/schemas.py`
- [x] Mettre à jour `NatalInterpretationData` dans `backend/app/api/v1/schemas/natal_interpretation.py` pour accepter `Union[AstroResponseV1, AstroResponseV2]`

### Subtask 30.2.2: Logique Service
- [x] Modifier `NatalInterpretationServiceV2.interpret()` pour gérer le mapping v2 pour le niveau `complete`
- [x] Gérer la désérialisation du cache pour être compatible avec les anciennes entrées v1

### Subtask 30.2.3: Persistance & Seed
- [x] Créer le script `backend/scripts/seed_30_2_astroresponse_v2.py`
- [x] S'assurer de l'idempotence du script (UPDATE si déjà existant)

### Subtask 30.2.4: Validation & Tests
- [x] Créer `backend/app/tests/unit/test_astro_response_v2.py`
- [x] Vérifier la validation Pydantic des limites élargies
- [x] Vérifier la coexistence v1/v2 dans le schéma d'API
- [x] Ajouter validation per-item Pydantic (Annotated) pour highlights, advice (360 chars) et evidence (pattern)
- [x] Ajouter tests de routage v1/v2 en isolation (AC4 couvert au niveau logique de service)

### Review Follow-ups (AI)
- [x] [AI-Review][HIGH] Ajouter try/except sur désérialisation V2 fresh gateway [natal_interpretation_service_v2.py:194]
- [x] [AI-Review][HIGH] Validation per-item highlights/advice manquante en Pydantic [schemas.py:54-55]
- [x] [AI-Review][MEDIUM] disclaimers minItems discordance JSON schema vs Pydantic [seed_30_2:72]
- [x] [AI-Review][MEDIUM] evidence pattern absent en Pydantic V2 [schemas.py:56]
- [x] [AI-Review][MEDIUM] Tests de routage v1/v2 service absents [test_astro_response_v2.py]
- [x] [AI-Review][MEDIUM] Fix UUID persona non documenté [natal_interpretation_service_v2.py:129]

## Dev Notes

### Différences de limites v1 vs v2

| Champ | AstroResponse_v1 (avant story) | AstroResponse_v1 (après story) | AstroResponse_v2 |
|-------|-------------------------------|-------------------------------|------------------|
| `summary` | 1200 chars | **2000 chars** (ajusté) | 2800 chars |
| `sections[].content` | 2500 chars | **4000 chars** (ajusté) | 6500 chars |
| `highlights[]` item | non validé | non validé | **360 chars** (Pydantic + JSON schema) |
| `advice[]` item | non validé | non validé | **360 chars** (Pydantic + JSON schema) |
| `evidence[]` pattern | non validé | non validé | **`^[A-Z0-9_\\.:-]{3,80}$`** (Pydantic + JSON schema) |

### Implémentation technique
La désérialisation dans `NatalInterpretationServiceV2` utilise désormais une vérification explicite :
```python
if level == "complete" and not gateway_result.meta.fallback_triggered:
    interpretation = AstroResponseV2(**gateway_result.structured_output)
else:
    interpretation = AstroResponseV1(**gateway_result.structured_output)
```

## Project Structure Notes
- Aucun changement de structure majeur.
- Le nouveau script de seed doit être exécuté APRES les seeds du chapitre 29.

## Alignment avec l'architecture existante
- Utilisation du pattern `Structured Output` introduit au chapitre 28.
- Respect du versioning des schémas de réponse sans casser la compatibilité frontend.

## References
- [Source: docs/agent/story-30-2-astroresponse-v2.md]
- [Source: backend/app/llm_orchestration/schemas.py]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Completion Notes List
- Schéma v2 implémenté et testé.
- Script de seed opérationnel et idempotent.
- Service mis à jour pour supporter les deux versions.
- Tests unitaires validant les nouvelles limites.
- **[Code Review]** Limites AstroResponseV1 ajustées dans la même PR : summary 1200→2000, content 2500→4000.
- **[Code Review]** Bug fix UUID persona query (`LlmPersonaModel.id == uuid.UUID(persona_id)`) inclus dans ce diff.
- **[Code Review]** Validation Pydantic per-item ajoutée (Annotated) pour highlights/advice (360 chars) et evidence (pattern).
- **[Code Review]** try/except ajouté sur désérialisation V2 dans le chemin fresh gateway (fallback V1).
- **[Code Review]** disclaimers minItems corrigé à 0 dans le seed JSON schema (alignement avec Pydantic).
- **[Code Review]** Tests de routage v1/v2 ajoutés.

### File List
- `backend/app/llm_orchestration/schemas.py` (Modifié)
- `backend/app/api/v1/schemas/natal_interpretation.py` (Modifié)
- `backend/app/services/natal_interpretation_service_v2.py` (Modifié)
- `backend/scripts/seed_30_2_astroresponse_v2.py` (Nouveau)
- `backend/app/tests/unit/test_astro_response_v2.py` (Nouveau)
