# Story CS-391 definir-contrat-narrative-natal-reading-v1: Définir Le Contrat Narratif Natal
Status: done

## Trigger / Source
- Source type: product-contract
- Source reference: `_story_briefs/cs-391-definir-contrat-narrative-natal-reading-v1.md`
- Reason for change: la lecture publique exige un payload stable, lisible et sans détails techniques.

## Objective
Définir `narrative_natal_reading_v1` comme contrat public versionné pour la lecture natale.

## Target State
- Le contrat expose une introduction, cinq chapitres, une synthèse et des sources humaines.
- Les champs techniques restent hors payload public.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-391-definir-contrat-narrative-natal-reading-v1.md` - brief source lu.
- Evidence 2: `backend/docs/narrative-natal-reading-v1-contract.md` - contrat public documenté.

## Domain Boundary
- Domain: natal-public-reading-contract
- In scope:
  - Modèle Pydantic public et documentation du payload.
- Out of scope:
  - UI React, calcul astrologique et entitlement.
- Explicit non-goals:
  - Aucun changement de moteur astrologique.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: le contrat public narratif ne correspond pas à un archétype supporté unique.
- Behavior change allowed: yes
- Behavior change constraints:
  - Exposer uniquement le contrat public versionné.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un champ technique devient nécessaire au rendu public.

Additional validation rules:
- Refuser tout champ hors schéma et conserver des textes humains non vides.

## Required Contracts
| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | La projection est traitée dans CS-392. |
| Baseline Snapshot | no | Aucun snapshot comparatif requis. |
| Ownership Routing | no | Aucun routage modifié. |
| Allowlist Exception | no | Aucun allowlist requis. |
| Contract Shape | no | Le modèle Pydantic porte la forme attendue. |
| Batch Migration | no | Aucune migration de lot. |
| Reintroduction Guard | no | Les gardes arrivent dans CS-395. |
| Persistent Evidence | no | Les tests versionnés suffisent. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le modèle public porte la version `narrative_natal_reading_v1`. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |
| AC2 | Le modèle public exige cinq chapitres. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |
| AC3 | Les champs inattendus sont rejetés. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |
| AC4 | Les sources restent formulées pour un lecteur humain. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |

## Implementation Tasks
- [x] Task 1: Ajouter le modèle Pydantic public. (AC: AC1, AC2, AC3)
- [x] Task 2: Documenter le contrat versionné. (AC: AC4)
- [x] Task 3: Ajouter les tests unitaires du schéma. (AC: AC1, AC2, AC3, AC4)

## Mandatory Reuse / DRY Constraints
- Centraliser la forme publique dans `narrative_natal_reading_v1.py`.
- Réutiliser le même modèle pour validation et sérialisation.

## No Legacy / Forbidden Paths
- Aucun wrapper legacy.
- Aucun chemin compatibility.
- Aucun fallback vers un payload libre.

## Regression Guardrails
- Applicable invariants: `RG-152`.
- Required regression evidence: `pytest -q tests/unit/test_narrative_natal_reading_v1.py`.
- Allowed differences: ajout du contrat public versionné.

## Files to Inspect First
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/docs/narrative-natal-reading-v1-contract.md`

## Expected Files to Modify
Likely files:
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/docs/narrative-natal-reading-v1-contract.md`

Likely tests:
- `backend/tests/unit/test_narrative_natal_reading_v1.py`

Files not expected to change:
- `frontend/src/**`

## Dependency Policy
- New dependencies: none.
- Justification: Pydantic existe déjà dans le backend.

## Validation Plan
- VC1: `pytest -q tests/unit/test_narrative_natal_reading_v1.py`
- VC2: `ruff check .`

## Regression Risks
- Un champ technique pourrait fuiter ; le schéma strict et RG-152 bornent ce risque.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References
- `_story_briefs/cs-391-definir-contrat-narrative-natal-reading-v1.md`
- `_condamad/stories/regression-guardrails.md`
