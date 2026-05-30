# Story CS-392 implementer-generation-narrative-natal-reading-v1: Générer La Lecture Narrative
Status: done

## Trigger / Source
- Source type: implementation
- Source reference: `_story_briefs/cs-392-implementer-generation-narrative-natal-reading-v1.md`
- Reason for change: le contrat public doit être construit depuis la réponse natale premium.

## Objective
Construire et valider la lecture narrative publique depuis les sections natales disponibles.

## Target State
- Le builder produit les cinq chapitres publics.
- Une réponse invalide est rejetée proprement.
- Le payload stocké est relu sans erreur serveur.

## Current State Evidence
- Evidence 1: `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - projection publique inspectée.
- Evidence 2: `backend/tests/unit/test_narrative_natal_reading_v1.py` - couverture unitaire inspectée.

## Domain Boundary
- Domain: natal-public-reading-generation
- In scope:
  - Projection, validation et relecture du payload narratif.
- Out of scope:
  - Rendu React et calcul astrologique.
- Explicit non-goals:
  - Aucun second appel fournisseur.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: la projection et sa validation forment un delta applicatif ciblé.
- Behavior change allowed: yes
- Behavior change constraints:
  - Réutiliser la réponse premium déjà générée.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une nouvelle source fournisseur devient nécessaire.

Additional validation rules:
- Une lecture stockée malformée doit demander une régénération au lieu de lever une erreur serveur.

## Required Contracts
| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | La source reste la réponse premium existante. |
| Baseline Snapshot | no | Aucun snapshot comparatif requis. |
| Ownership Routing | no | Aucun routage modifié. |
| Allowlist Exception | no | Aucun allowlist requis. |
| Contract Shape | no | Le modèle CS-391 valide la projection. |
| Batch Migration | no | Aucune migration de lot. |
| Reintroduction Guard | no | Les gardes arrivent dans CS-395. |
| Persistent Evidence | no | Les tests versionnés suffisent. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le builder produit cinq chapitres ordonnés. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |
| AC2 | Le validateur refuse un contenu incomplet. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |
| AC3 | Un payload stocké malformé demande une régénération. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py`. |
| AC4 | Le prompt premium cite les cinq sections sources. | `pytest -q app/tests/unit/test_seed_30_8_v3_prompt_contract.py`. |

## Implementation Tasks
- [x] Task 1: Construire la projection narrative. (AC: AC1)
- [x] Task 2: Valider le contrat public. (AC: AC2)
- [x] Task 3: Durcir la relecture stockée. (AC: AC3)
- [x] Task 4: Aligner le prompt premium. (AC: AC4)

## Mandatory Reuse / DRY Constraints
- Réutiliser `AstroResponseV3`.
- Centraliser le mapping dans le builder.

## No Legacy / Forbidden Paths
- Aucun wrapper legacy.
- Aucun chemin compatibility.
- Aucun fallback public vers la réponse brute.

## Regression Guardrails
- Applicable invariants: `RG-152`.
- Required regression evidence: `pytest -q tests/unit/test_narrative_natal_reading_v1.py`.
- Allowed differences: ajout de la projection narrative.

## Files to Inspect First
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`

## Expected Files to Modify
Likely files:
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`

Likely tests:
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/app/tests/unit/test_seed_30_8_v3_prompt_contract.py`

Files not expected to change:
- `frontend/src/**`

## Dependency Policy
- New dependencies: none.
- Justification: les briques existantes suffisent.

## Validation Plan
- VC1: `pytest -q tests/unit/test_narrative_natal_reading_v1.py`
- VC2: `pytest -q app/tests/unit/test_seed_30_8_v3_prompt_contract.py`
- VC3: `ruff check .`

## Regression Risks
- Une projection partielle pourrait être exposée ; le validateur et RG-152 bornent ce risque.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References
- `_story_briefs/cs-392-implementer-generation-narrative-natal-reading-v1.md`
- `_condamad/stories/regression-guardrails.md`
