# Story Candidates - prompt-generation-cartography - 2026-05-27-1809

## SC-001 Converge output schema configuration ownership

- Source finding: F-002
- Suggested story title: Converger le proprietaire nominal des schemas de sortie LLM
- Suggested archetype: contract-shape-audit
- Primary domain: backend LLM configuration
- Required contracts: Runtime Source of Truth; Contract Shape; Ownership Routing; Reintroduction Guard; Persistent Evidence
- Draft objective: Select and enforce one nominal runtime owner for output schema resolution while keeping catalog and seeds as explicit fallback/provisioning inputs only.
- Closure intent: full-closure
- Must include: exact inventory of `CanonicalOutputSchemaDefinition`, `output_schema_name`, `output_schema_id`, `get_output_schema`, seed schema definitions and tests importing bootstrap schemas; before/after schema owner matrix; no wildcard allowlist; No Legacy scan for new fallback schema paths; classification changes for fallback catalog and bootstrap schema surfaces.
- Validation hints: run targeted scans for `output_schema_name`, `output_schema_id`, `get_output_schema`, `ASTRO_RESPONSE_V3_JSON_SCHEMA`; run `pytest -q backend/tests/evaluation/test_output_contract.py`; run coherence validator tests; run `git diff --quiet -- backend/app backend/tests frontend/src` for unrelated roots.
- Blockers: stop if product must decide whether catalog fallback schemas remain supported public behavior.

## SC-002 Make prompt-resolution evaluation non-mutating

- Source finding: F-003
- Suggested story title: Rendre le test de resolution de prompt executable sans modifier `backend/tests`
- Suggested archetype: test-guard-hardening
- Primary domain: backend LLM evaluation tests
- Required contracts: Baseline Snapshot; Reintroduction Guard; Persistent Evidence
- Draft objective: Split or parameterize `test_prompt_resolution.py` so pytest validation can prove resolution behavior without writing `evaluation_report.md` unless explicitly requested.
- Closure intent: full-closure
- Must include: exact treatment of `backend/tests/evaluation/test_prompt_resolution.py`, `backend/tests/evaluation/report_generator.py`, and `backend/tests/evaluation/evaluation_report.md`; before/after git status evidence; no new dependency; no prompt runtime change.
- Validation hints: run `pytest -q backend/tests/evaluation/test_prompt_resolution.py`; run `git diff --quiet -- backend/tests/evaluation`; run the CS-344 report validation scans.
- Blockers: stop if the team intentionally wants pytest to regenerate the report artifact by default.

## Exhaustive Files To Modify

### F-002

- Application files: `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/prompting/catalog.py`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/domain/llm/configuration/config_coherence_validator.py`, `backend/app/ops/llm/bootstrap/use_cases_seed.py`, `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`.
- Governance/test files: `backend/tests/evaluation/test_output_contract.py`, `backend/tests/llm_orchestration/test_config_coherence_validator.py`.
- Audit/story artifacts: before/after schema-owner matrix and validation evidence.
- Stop condition: one nominal schema owner remains for runtime resolution and fallback/provisioning schema sources are explicitly non-nominal.

### F-003

- Application files: none.
- Governance/test files: `backend/tests/evaluation/test_prompt_resolution.py`, `backend/tests/evaluation/report_generator.py`, `backend/tests/evaluation/evaluation_report.md`.
- Audit/story artifacts: before/after no-delta evidence.
- Stop condition: `pytest -q backend/tests/evaluation/test_prompt_resolution.py` passes and leaves `backend/tests/evaluation` unchanged unless a report-generation option is explicitly selected.

## Deferred Non-Domain Context

- Provider handoff and provider fallback classification remain deferred to CS-345.
- Full `llm_astrology_input_v1` source completeness remains deferred to CS-346.
- Persistence and observability output validation remain deferred to CS-347.

