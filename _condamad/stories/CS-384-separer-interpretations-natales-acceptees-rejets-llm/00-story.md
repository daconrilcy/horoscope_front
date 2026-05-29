# Story CS-384: Séparer interprétations natales acceptées et rejets LLM persistés

Status: implemented

## Objective

Empêcher qu'un rejet LLM (`status="rejected"`) soit relu ou exposé comme une interprétation natale valide (`AstroFreeResponseV1` / `AstroResponseV1`), tout en conservant la persistance audit CS-290.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-002` — la logique reste dans `interpretation_service`, pas dans les routeurs API.
  - `RG-004` — réponses HTTP via `_raise_error` / exceptions service homogènes.
  - `RG-005` — pas de persistance métier dans la couche API.
  - `RG-022` — tests sous chemins pytest collectés (`backend/tests/`).
  - `RG-150` — invariant créé par cette story : rejected ≠ AstroResponse, audit séparé du cache public.
- Non-applicable invariants:
  - `RG-128` / `RG-379-*` — pas de changement du contrat JSON du thème natal calculé.
  - `RG-047` / `RG-052` — pas de changement frontend/CSS.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_natal_interpretation_stored_payload.py`
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
  - `pytest -q backend/tests/integration/test_rejected_narrative_answer_audit.py`
  - `pytest -q backend/tests/architecture/test_rejected_narrative_answer_boundary.py`
- Allowed differences: none

## Acceptance Criteria

- [x] AC1: `_deserialize_persisted_interpretation` refuse les payloads rejected avant Pydantic.
- [x] AC2: Les lignes legacy rejected en cache public sont purgées à la lecture.
- [x] AC3: `list_interpretations` et `get_interpretation_by_id` excluent `narrative_answer_audit_v1`.
- [x] AC4: Un rejet live persiste via `NarrativeAnswerAuditRepository` sans cache utilisateur.
- [x] AC5: `AstroResponseV1` / `AstroFreeResponseV1` restent `extra="forbid"`.

## Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py tests/integration/test_rejected_narrative_answer_audit.py tests/architecture/test_rejected_narrative_answer_boundary.py
```
