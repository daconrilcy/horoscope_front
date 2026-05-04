# No Legacy / DRY Guardrails

- Canonical path: `backend/docs/ownership-index.md`.
- Forbidden: unclassified file under `backend/docs/**`, vague type (`misc`, `todo`, `unknown`, `other`), duplicate ownership registry for backend docs.
- Guard: `pytest -q app/tests/unit/test_backend_docs_ownership.py`.
- Regression guardrails: RG-015, RG-040.
