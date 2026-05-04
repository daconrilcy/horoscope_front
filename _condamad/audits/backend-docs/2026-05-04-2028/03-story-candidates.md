# Story Candidates - backend-docs

## SC-001 - Move non-canonical LLM prose to root docs

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Repositionner les notes LLM non canoniques hors `backend/docs`
- Suggested archetype: documentation-boundary-convergence
- Primary domain: backend-docs / docs-llm
- Required contracts: `RG-040`, `RG-042`, backend docs ownership index, LLM docs governance registry, LLM cleanup registry references.
- Draft objective: Move retained LLM prose documents from `backend/docs/` to root `docs/llm/` while preserving generated/executable LLM assets under `backend/docs/`.
- Must include: update `backend/docs/ownership-index.md`; update `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`; update `governance_doc` and any references in `llm-db-cleanup-registry.json` if `llm-db-governance.md` moves; keep `llm-model-structure.md` and `llm-db-cleanup-registry.json` in place.
- Validation hints: `pytest -q app/tests/unit/test_backend_docs_ownership.py`; `pytest -q app/tests/unit/test_llm_docs_governance.py`; `pytest -q tests/integration/test_llm_db_cleanup_registry.py`; `rg -n "llm-db-governance|llm-runtime-source-of-truth|llm-canonical-consumption-rebuild" backend docs _condamad/stories`.
- Blockers: choose final root location, recommended `docs/llm/`.

## SC-002 - Decide retention of entitlement historical platform note

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Repositionner ou supprimer la note historique entitlement canonique
- Suggested archetype: historical-doc-reposition-or-delete
- Primary domain: backend-docs / docs-architecture
- Required contracts: `RG-040`, `RG-041`, entitlement doc runtime parity/status guard.
- Draft objective: Decide whether `backend/docs/entitlements-canonical-platform.md` remains useful historical architecture documentation. If retained, move it to root `docs/architecture/` with historical status preserved. If deleted, first extract any still-useful decommission, RGPD, security, and ops warnings into active runtime tests or root docs.
- Must include: update `backend/docs/ownership-index.md`; update `test_entitlement_docs_runtime_parity.py` or replace it with a guard that no canonical-looking entitlement doc remains under `backend/docs`; preserve OpenAPI/table parity checks if still valuable.
- Validation hints: `pytest -q app/tests/unit/test_backend_docs_ownership.py`; `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`; targeted `rg -n "entitlements-canonical-platform|Document status: historical-note" backend docs _condamad`.
- Blockers: deletion is not automatic; the file contains operational/security history that may still be useful.
