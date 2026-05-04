# Executive Summary - backend-docs

`backend/docs` is no longer an uncontrolled catch-all. The previous audit findings were mostly addressed: there is an ownership index, LLM docs are governed, entitlement prose is explicitly historical, and the stale calibration artifact under `backend/docs/calibration` is gone.

The remaining cleanup is a placement decision:

- Keep in `backend/docs`: `ownership-index.md`, `llm-model-structure.md`, `llm-db-cleanup-registry.json`.
- Move if retained: `llm-db-governance.md`, `llm-runtime-source-of-truth.md`, `llm-canonical-consumption-rebuild.md`, preferably to `docs/llm/`.
- Move or delete with user decision: `entitlements-canonical-platform.md`, preferably to `docs/architecture/` if retained.

There is no unconditional delete candidate in the current inventory. The entitlement document is delete-eligible only after a product/architecture decision because it is historical but still contains decommission, RGPD, ops, endpoint, and security context.

Story candidates:

- SC-001: Move non-canonical LLM prose to root docs.
- SC-002: Decide retention, relocation, or deletion of the entitlement historical platform note.
