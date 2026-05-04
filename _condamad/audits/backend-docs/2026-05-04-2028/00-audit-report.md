# CONDAMAD Audit Report - backend-docs

## Scope

- Domain target: `backend/docs/`
- Archetype: `legacy-surface-audit` applied to backend documentation placement, executable registries, generated docs, and historical notes.
- Mode: read-only for application code and existing documentation; only audit artifacts under `_condamad/audits/**` are created.
- Trigger: follow-up after `_condamad/audits/backend-docs/2026-05-04-1826` to verify which remaining files should move to root `docs/` and which can be deleted as legacy.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`, especially `RG-040`, `RG-041`, `RG-042`, and `RG-043`.

## Executive Verdict

`backend/docs/` is now governed and materially cleaner than the previous audit. The calibration legacy artifact is gone, every remaining file is listed in `backend/docs/ownership-index.md`, and focused tests exist for backend-docs ownership, LLM doc governance, entitlement doc status/runtime parity, and calibration artifact location.

The remaining problem is placement, not uncontrolled drift. Three LLM prose files and the entitlement historical note are non-canonical human documentation. They do not need to remain under `backend/docs/` and should be repositioned under root `docs/` if retained. The executable/generated LLM assets should stay in `backend/docs/` unless their consuming code and guards are deliberately migrated.

No current file is an unconditional safe-delete candidate. The only delete-eligible item is `backend/docs/entitlements-canonical-platform.md`, because it is explicitly historical and guarded as non-source-of-truth, but it still contains decommissioning, RGPD, ops, endpoint, and security context. Deleting it should be a user decision after extracting any still-useful operational warnings.

## Findings

| ID | Severity | Summary | Status |
|---|---|---|---|
| F-001 | Medium | Non-canonical LLM prose remains under `backend/docs/` even though its active truth is code, tests, registries, and story governance. | active |
| F-002 | Medium | The entitlement platform document is explicitly historical but remains in backend technical docs with a canonical-looking filename and title. | active |
| F-003 | Info | `llm-model-structure.md` and `llm-db-cleanup-registry.json` are not legacy docs; they are generated/executable assets with active guards. | monitor |
| F-004 | Info | The previous calibration legacy surface under `backend/docs/calibration` has been removed and is guarded against reintroduction. | resolved |

## Current Placement Decision Matrix

| Surface | Current classification | Audit decision | Rationale |
|---|---|---|---|
| `backend/docs/ownership-index.md` | governance-doc / canonical-guarded | keep in `backend/docs/` | It governs the remaining backend docs folder and is checked by `test_backend_docs_ownership.py`. |
| `backend/docs/llm-model-structure.md` | generated-doc / canonical-guarded | keep in `backend/docs/` | It is generated from `llm_canonical_perimeter` and compared by `test_llm_canonical_perimeter.py`. |
| `backend/docs/llm-db-cleanup-registry.json` | executable-registry / canonical-guarded | keep in `backend/docs/` | It is loaded by `LlmDbCleanupValidator`; moving it requires code and test migration. |
| `backend/docs/llm-db-governance.md` | human-runbook / non-canonical-human-note | move to `docs/llm/` if retained | It is prose governance referenced by the JSON registry, not active runtime truth. Moving it requires updating the registry reference and guards. |
| `backend/docs/llm-runtime-source-of-truth.md` | historical-note / non-canonical-human-note | move to `docs/llm/` if retained | It declares non-canonical status and points to runtime sources elsewhere. |
| `backend/docs/llm-canonical-consumption-rebuild.md` | historical-note / non-canonical-human-note | move to `docs/llm/` if retained | It is rebuild strategy prose, not executable source of truth. |
| `backend/docs/entitlements-canonical-platform.md` | historical-note / historical-note | move to `docs/architecture/` or delete with user decision | It is explicitly historical but still contains operational and security context. |

## No Legacy / DRY / Boundary Assessment

- No Legacy: previous uncontrolled legacy artifact `backend/docs/calibration/percentile_report.json` is absent and guarded. Remaining legacy wording is intentionally documented as non-canonical or historical.
- DRY: root `docs/` already owns human-facing architecture, runbook, and product documentation. Keeping non-canonical prose in `backend/docs/` duplicates that responsibility.
- Mono-domain: `backend/docs/` should be narrowed to backend-owned generated docs, executable registries, and its local governance index.
- Dependency direction: code currently reads `backend/docs/llm-db-cleanup-registry.json`; do not move that file without updating `REGISTRY_RELATIVE_PATH`, registry tests, and story guardrails.

## Recommended Order

1. Move retained non-canonical LLM prose to a root `docs/llm/` area and update references/guards.
2. Decide whether `entitlements-canonical-platform.md` is still useful as historical architecture documentation. If yes, move it under root `docs/architecture/` with its historical status preserved. If no, delete it after extracting any still-needed decommission/security warnings.
3. Keep `llm-model-structure.md`, `llm-db-cleanup-registry.json`, and `ownership-index.md` under `backend/docs/`.
4. Preserve the existing guards: backend docs ownership, LLM docs governance, entitlement doc parity/status, LLM canonical perimeter, LLM cleanup registry, and calibration artifact location.

## Validation Notes

- Application code and existing docs were not changed.
- Python validation commands must be run after activating `.venv`.
