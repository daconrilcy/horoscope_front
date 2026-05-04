# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Docs LLM classees. | `llm-doc-governance.md`. | `pytest -q app/tests/unit/test_llm_docs_governance.py`. | PASS |
| AC2 | `llm-model-structure.md` garde conservee. | Registry references canonical perimeter test. | `pytest -q tests/unit/test_llm_canonical_perimeter.py`. | PASS |
| AC3 | Registry cleanup garde conserve. | Registry references cleanup validator test. | `pytest -q tests/integration/test_llm_db_cleanup_registry.py`. | PASS |
| AC4 | Docs non gardees non normatives. | Headers `non-canonical-human-note`. | `test_llm_normative_terms_require_guard_or_non_canonical_status`. | PASS |
| AC5 | Runtime LLM cible passant. | No runtime change. | LLM orchestration tests PASS. | PASS |
