# Dev Log

## 2026-06-01

- Preflight: `git status --short` showed pre-existing dirty files `_condamad/run-state.json` and `_condamad/stories/regression-guardrails.md`.
- Capsule: generated files were missing; ran `condamad_prepare.py` and `condamad_validate.py` after venv activation. Validation PASS.
- Note: one baseline command was first attempted from `backend/` with the wrong relative venv activation path; rerun immediately from repository root with `.\.venv\Scripts\Activate.ps1` before recording evidence.
- Baselines: persisted `basic-payload-before.json` and `basic-public-contract-before.json`.
- Implementation: added `BasicNatalEditorialBrief`, provider payload editorial fields, localized plan public evidence, stronger Basic validator, fallback prose, and deduplicated `synthesis` public projection.
- Tests: updated payload, public evidence, validator, provider payload, and integration tests.
- Guardrails: added `RG-169` for Basic natal editorial quality.
- Evidence: persisted after snapshots and AC traceability.

Propagation decision: no-propagation; the durable learning was captured as `RG-169` in the canonical guardrail registry.
