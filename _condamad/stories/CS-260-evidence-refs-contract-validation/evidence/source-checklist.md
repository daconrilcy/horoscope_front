# Source checklist - CS-260

## Source brief alignment

- `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md`: source brief matched by tracker row and story reference.
- Objective covered: `docs/architecture/evidence-refs-contract.md` defines the versioned `evidence_refs` contract and validation vocabulary.
- Included scope covered: proof reference structure, audited section linkage, authorized source kinds, validation errors, admin/client separation
  and validated hashed source requirement.
- Out of scope preserved: no admin viewer, semantic engine, client technical proof exposure or astrology calculation change.

## Dependency coverage

- CS-256 `structured_facts_v1`: reused as the stable hashable factual source base.
- CS-259 `narrative_answer_audit_v1`: reused as the narrative audit and grounding parent.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`: inspected as existing AI source vocabulary owner.
- `docs/architecture/official-product-primitives-public-projections.md`: reused for public projection and client-facing masking boundaries.

## Contract primitive coverage

- `evidence_ref_id`: documented as a stable proof reference identifier.
- `section_id`: documented as the audited section owner.
- `source_type`: constrained to `structured_fact`, `interpretive_signal` and `projection_version`.
- `source_id`, `source_version`, `source_hash`: documented as mandatory validated source anchors.
- `validation_state`: documents `validated`, `missing_source`, `unsupported_source_type`, `missing_hash` and `hash_mismatch`.
- `grounding_status`: documents `grounded`, `partial`, `unfounded` and `not_checked`.
- `admin_proof` and `client_support`: documented as separate internal and client-facing surfaces.

## Non-drift evidence

- Runtime/API neutrality is recorded in `evidence/openapi-routes.txt`.
- Application-surface neutrality is recorded in `evidence/app-surface-status.txt`.
- Backend test evidence is recorded in `evidence/pytest.txt`.
