# Finding Register - backend-docs

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | missing-canonical-owner | backend-docs | E-002, E-003, E-010 | Future files can be added under `backend/docs/` without declaring whether they are executable registry data, generated output, human docs, historical notes, or canonical specs. | Add a local ownership/classification index for `backend/docs/` and guard it with a focused test or scan. | yes |
| F-002 | Medium | High | runtime-contract-drift | backend-docs | E-003, E-007, E-008 | The entitlement doc presents canonical/security behavior and many endpoint/table contracts, but can drift from route, schema, model, and service tests without detection. | Either add doc/runtime parity guards for the entitlement spec or mark the document as historical/design notes and move canonical contracts closer to executable tests/OpenAPI. | yes |
| F-003 | Medium | High | duplicate-responsibility | backend-docs | E-004, E-005, E-006, E-008 | LLM documentation has mixed governance: some docs are executable/generated, while other source-of-truth prose can diverge from runtime without the same guardrails. | Classify LLM docs by owner and convert source-of-truth prose into generated/validated artifacts where it is intended to be normative. | yes |
| F-004 | Medium | High | legacy-surface | backend-docs | E-002, E-009, E-010 | Calibration output is split by path: current code writes `docs/calibration`, while a large report remains under `backend/docs/calibration`, creating stale artifact risk. | Decide the canonical calibration artifact location, then move/delete the orphaned report and add a guard preventing split generated-output locations. | yes |
| F-005 | Info | High | observability-gap | backend-docs | E-005, E-006 | The LLM cleanup registry is correctly executable governance data, but this is not visible from folder structure alone. | No immediate fix beyond F-001; preserve the validator and tests when reorganizing docs. | no |

## F-001 - Missing local ownership index for `backend/docs/`

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend-docs
- Evidence: E-002, E-003, E-010.
- Expected rule: a tolerated backend docs folder should declare ownership and artifact type per file when it contains multiple domains and generated/executable material.
- Actual state: `backend/docs/` contains LLM docs, entitlement platform spec, JSON governance registry, and calibration report, with no local index or classification.
- Impact: Future files can be added under `backend/docs/` without declaring whether they are executable registry data, generated output, human docs, historical notes, or canonical specs.
- Recommended action: Add a local ownership/classification index for `backend/docs/` and guard it with a focused test or scan.
- Story candidate: yes
- Suggested archetype: documentation-governance / architecture-guard-hardening

## F-002 - Entitlement canonical spec lacks direct parity guard

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: backend-docs
- Evidence: E-003, E-007, E-008.
- Expected rule: canonical/security documentation should be generated from or checked against runtime contracts when it describes endpoints, tables, state transitions, and access controls.
- Actual state: `backend/docs/entitlements-canonical-platform.md` is large and claims canonical behavior, but targeted scans found no direct active reference to the file from entitlement tests or validators.
- Impact: The entitlement doc presents canonical/security behavior and many endpoint/table contracts, but can drift from route, schema, model, and service tests without detection.
- Recommended action: Either add doc/runtime parity guards for the entitlement spec or mark the document as historical/design notes and move canonical contracts closer to executable tests/OpenAPI.
- Story candidate: yes
- Suggested archetype: contract-shape-audit / documentation-runtime-parity

## F-003 - LLM docs have uneven governance

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: backend-docs
- Evidence: E-004, E-005, E-006, E-008.
- Expected rule: source-of-truth docs should share a consistent governance model.
- Actual state: `llm-model-structure.md` is generated/guarded and `llm-db-cleanup-registry.json` is executable/validated, but `llm-runtime-source-of-truth.md` and `llm-canonical-consumption-rebuild.md` are not directly guarded by active code/tests.
- Impact: LLM documentation has mixed governance: some docs are executable/generated, while other source-of-truth prose can diverge from runtime without the same guardrails.
- Recommended action: Classify LLM docs by owner and convert source-of-truth prose into generated/validated artifacts where it is intended to be normative.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening / no-legacy-doc-governance

## F-004 - Calibration report appears misplaced or stale

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: backend-docs
- Evidence: E-002, E-009, E-010.
- Expected rule: generated reports should have one canonical output location and should not be mixed into backend technical docs without classification.
- Actual state: `backend/docs/calibration/percentile_report.json` exists, but current calibration code writes reports and review grids under repo-root `docs/calibration`.
- Impact: Calibration output is split by path: current code writes `docs/calibration`, while a large report remains under `backend/docs/calibration`, creating stale artifact risk.
- Recommended action: Decide the canonical calibration artifact location, then move/delete the orphaned report and add a guard preventing split generated-output locations.
- Story candidate: yes
- Suggested archetype: legacy-surface-removal / artifact-governance

## F-005 - LLM cleanup registry is a protected executable artifact

- Severity: Info
- Confidence: High
- Category: observability-gap
- Domain: backend-docs
- Evidence: E-005, E-006.
- Expected rule: executable governance data should stay protected when documentation is reorganized.
- Actual state: the registry is consumed by `LlmDbCleanupValidator` and backed by integration tests.
- Impact: The LLM cleanup registry is correctly executable governance data, but this is not visible from folder structure alone.
- Recommended action: No immediate fix beyond F-001; preserve the validator and tests when reorganizing docs.
- Story candidate: no
- Suggested archetype: monitor
