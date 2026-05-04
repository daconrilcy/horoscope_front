# CONDAMAD Audit Report - backend-docs

## Scope

- Domain target: `backend/docs/`
- Archetype: `legacy-surface-audit` applied to documentation, executable registries, and generated documentation artifacts.
- Mode: read-only for application code; only audit artifacts under `_condamad/audits/**` are created.
- Trigger: user concern that `backend/docs` is becoming a catch-all folder.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`; relevant adjacent invariants include `RG-015`, `RG-018`, `RG-021`, and entitlement/prediction No Legacy guardrails by domain adjacency.

## Executive Verdict

The concern is valid. `backend/docs/` currently groups four different responsibilities without a local ownership index: guarded LLM technical documentation, an executable LLM cleanup registry consumed by validators, an entitlement platform specification that claims canonical/security behavior, and a calibration report artifact that is not produced by the current calibration paths.

The folder is not pure dead weight. Two LLM files are actively guarded: `llm-model-structure.md` must match code-generated markdown, and `llm-db-cleanup-registry.json` is consumed by `app.ops.llm.db_cleanup_validator` and integration tests. The problem is that this protected subset sits beside unguarded canonical-looking docs and a likely misplaced generated artifact.

## Findings

| ID | Severity | Summary | Status |
|---|---|---|---|
| F-001 | Medium | `backend/docs/` has no local ownership/classification index despite mixing docs, executable registries, specs, and generated artifacts. | active |
| F-002 | Medium | `backend/docs/entitlements-canonical-platform.md` is a large canonical/security platform spec with no direct doc/runtime parity guard found. | active |
| F-003 | Medium | LLM docs are inconsistently governed: `llm-model-structure.md` and the cleanup registry are guarded, while other source-of-truth docs are only conventionally referenced. | active |
| F-004 | Medium | `backend/docs/calibration/percentile_report.json` appears orphaned or misplaced because current calibration producers target `docs/calibration`, not `backend/docs/calibration`. | active |
| F-005 | Info | `backend/docs/llm-db-cleanup-registry.json` is correctly treated as executable governance data, not passive prose. | monitor |

## Current Surface Classification

| Surface | Classification | Evidence |
|---|---|---|
| `backend/docs/llm-model-structure.md` | generated / guarded technical doc | E-004, E-006 |
| `backend/docs/llm-db-cleanup-registry.json` | executable governance registry | E-005, E-006 |
| `backend/docs/llm-db-governance.md` | human governance doc referenced by registry | E-005, E-006 |
| `backend/docs/llm-runtime-source-of-truth.md` | unguarded source-of-truth prose | E-006, E-008 |
| `backend/docs/llm-canonical-consumption-rebuild.md` | unguarded rebuild strategy prose | E-006, E-008 |
| `backend/docs/entitlements-canonical-platform.md` | large entitlement platform specification | E-003, E-007 |
| `backend/docs/calibration/percentile_report.json` | generated calibration artifact with no current producer found | E-002, E-009 |

## No Legacy / DRY / Boundary Assessment

- DRY: the folder duplicates the repository-level `docs/` role and also contains generated artifacts, but only part of that role is explicit in `docs/backend-structure-governance.md`.
- No Legacy: legacy language is intentional in LLM and entitlement docs, but only the LLM cleanup registry has executable allowlist enforcement.
- Mono-domain: `backend/docs/` is not a bounded domain today; it mixes LLM, entitlement, and calibration concerns.
- Dependency direction: code legitimately reads the LLM cleanup registry, but code writing calibration output under `docs/calibration` conflicts with the existing artifact under `backend/docs/calibration`.

## Recommended Order

1. Create a small `backend/docs/README.md` or ownership index that classifies each file as `guarded-doc`, `executable-registry`, `runbook/spec`, `generated-artifact`, or `historical`.
2. Decide the canonical home for calibration generated outputs, then move or delete `backend/docs/calibration/percentile_report.json` with a guard that prevents split locations.
3. Add doc/runtime parity or route/schema snapshots for entitlement docs that are intended to remain canonical.
4. Convert unguarded LLM source-of-truth prose either into generated/validated docs or explicitly mark them as human design notes.

## Validation Notes

- Application code was not changed.
- Python validation commands were run after activating `.venv`.
- The audit folder passed the CONDAMAD validator and linter.
