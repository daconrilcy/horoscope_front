# Story Candidates - backend-docs

## SC-001 - Classify backend docs ownership and artifact types

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Classer `backend/docs` par ownership et type d'artefact
- Suggested archetype: documentation-governance / architecture-guard-hardening
- Primary domain: backend-docs
- Required contracts: No Legacy, DRY, backend structure governance, regression guardrails
- Draft objective: Add a local ownership index for every file under `backend/docs/` and enforce that new files declare whether they are generated, executable registry data, canonical docs, human runbooks, or historical notes.
- Must include: exact inventory, allowed classifications, owner/domain for each file, rule for generated files, and a test/scan that fails on unclassified additions.
- Validation hints: `rg --files backend/docs`; targeted pytest guard for inventory classification.
- Blockers: choose file name (`README.md` vs `ownership-index.md`) and whether JSON registries are allowed to remain under docs.

## SC-002 - Guard or downgrade the entitlement canonical platform document

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Aligner la documentation entitlement canonique avec les contrats runtime
- Suggested archetype: contract-shape-audit / documentation-runtime-parity
- Primary domain: entitlement
- Required contracts: entitlement policy, API route inventory, No Legacy, security guardrails
- Draft objective: Decide whether `backend/docs/entitlements-canonical-platform.md` remains canonical. If yes, add parity guards for critical endpoint, table, review, alert, and security claims. If no, mark and relocate/split it as historical story evidence.
- Must include: route/OpenAPI inventory checks for documented ops endpoints, model/table checks for listed canonical tables, and explicit treatment of security/access-control sections.
- Validation hints: targeted tests around `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py`, entitlement model inventory, and doc line/section checks.
- Blockers: needs user decision if this file is intended as product-facing canonical documentation or only accumulated story notes.

## SC-003 - Normalize LLM documentation governance

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Uniformiser la gouvernance des docs LLM source-of-truth
- Suggested archetype: architecture-guard-hardening / no-legacy-doc-governance
- Primary domain: LLM
- Required contracts: LLM canonical perimeter, DB cleanup registry, prompt/runtime source-of-truth
- Draft objective: Classify each LLM doc under `backend/docs/` and make every normative source-of-truth document either generated from code/registry or guarded by targeted tests.
- Must include: preserve `llm-model-structure.md` generated equality guard, preserve `llm-db-cleanup-registry.json` validator contract, and add explicit status for `llm-runtime-source-of-truth.md` and `llm-canonical-consumption-rebuild.md`.
- Validation hints: existing `test_llm_canonical_perimeter.py`, `test_llm_db_cleanup_registry.py`, plus new doc ownership test.
- Blockers: none if classification keeps current files in place; user decision needed before moving executable registry JSON.

## SC-004 - Converge calibration generated artifact location

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Converger l'emplacement des artefacts de calibration
- Suggested archetype: legacy-surface-removal / artifact-governance
- Primary domain: calibration
- Required contracts: backend structure governance, scheduled tasks ownership, generated artifact policy
- Draft objective: Choose and enforce one canonical location for generated calibration reports and review grids, then remove or migrate `backend/docs/calibration/percentile_report.json`.
- Must include: scan for both `backend/docs/calibration` and `docs/calibration`, update producers or docs consistently, and add a guard preventing future split output paths.
- Validation hints: targeted tests for `compute_calibration_percentiles.py`, `generate_review_grid.py`, and `rg --files backend/docs/calibration docs/calibration`.
- Blockers: decide whether calibration reports belong in repo-root `docs/calibration`, `backend/artifacts`, or another ignored artifact location.
