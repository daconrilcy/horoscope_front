# Story Candidates

## SC-001 Correct Final Theme Astral Example Birth Context

- Source finding: F-001
- Suggested story title: Corriger les exemples provider theme_astral pour porter le birth_context structure
- Suggested archetype: contract-shape-audit-remediation
- Primary domain: theme-astral-prompt-contract
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: make the official `1973-04-24-1100-paris-theme-astral-v1` provider examples match the runtime `birth_context` contract by carrying structured Paris birth data in `input_data.birth_context`, while keeping commercial plan labels backend-only and old carriers inactive.
- Closure intent: full-closure
- Must include: regenerate or correct all three provider payload JSON files; update example README or structure comparison only if their statements need exact alignment; add or update the existing example validator so known scenario metadata cannot be present only in `chart_id`; keep source material disclosure unchanged unless validation proves it stale.
- Validation hints: run target JSON validation; run provider payload builder tests; run persistence tests; run bigbang tests; run architecture guard; run scan for `chart_json`, `natal_data`, `llm_astrology_input_v1`, `legacy`, `free`, `basic`, `premium`, and `"plan"` in backend target paths and target examples; run a JSON assertion that each provider payload has `birth_date=1973-04-24`, `birth_time_local=11:00`, `city=Paris`, `country=France`, `timezone=Europe/Paris`, and non-null coordinates when scenario metadata is known.
- Blockers: stop if the product decision is that examples intentionally demonstrate missing birth precision; in that case rename the scenario and documentation so it no longer claims a complete Paris birth context.

## Exhaustive Files To Modify

Source finding: F-001

Application files: none expected.

Governance and example files:

- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` if wording changes are needed after payload correction
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` if wording changes are needed after payload correction
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py` or the current canonical example validator if it has moved

Tests or guards:

- Prefer updating the existing example validator over adding a new test file.
- Add no wildcard allowlist for null `birth_context` values.

Before evidence required:

- JSON inspection showing null structured fields and scenario-carrying `chart_id`.
- Current targeted pytest and ruff status.

After evidence required:

- JSON inspection showing all three provider payloads carry structured Paris values.
- `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short`
- Targeted forbidden-value scan over backend target paths and target examples.

Stop condition:

- F-001 is closed when no known-scenario provider payload keeps all structured birth fields null and validation fails on reintroduction.

## Deferred Non-Domain Context

- Broad old-carrier and plan hits in natal generation, admin sample payloads, entitlement/API tests, chat/guidance flows, and historical prompt-generation docs belong to other domains and do not require a story candidate in this audit.
- F-002 is not an implementation candidate because real provider calls require explicit opt-in and credentials.
- F-003 is not an implementation candidate because current source fixture status is disclosed and representative enough for the final audit threshold.
