# Reuse Decision - CS-290

- Rejection workflow owner: `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`.
- Narrative orchestration owner reused: `backend/app/services/llm_generation/natal/interpretation_service.py`.
- Evidence validation owner reused: `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`.
- Audit persistence owner reused: `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py`.
- Audit storage owner reused: `backend/app/infra/db/models/user_natal_interpretation.py`.

No duplicate audit table, duplicate validator, route, frontend path, prompt template or provider adapter was added.
