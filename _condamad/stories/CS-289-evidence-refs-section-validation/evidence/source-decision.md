# CS-289 Source Decision

- Evidence refs validation owner: `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`.
- Audit persistence owner reused: `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py`.
- Stored audit row owner reused: `backend/app/infra/db/models/user_natal_interpretation.py`.
- Projection hash anchor reused from persisted audit fields: `projection_version` + `projection_hash`.
- LLM input hash anchor reused from persisted audit fields: `llm_input_version` + `llm_input_hash`.
- No new route, serializer, DB table, migration, frontend helper or generated client was introduced.
