# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Free preview has its own contract. | `backend/app/domain/theme_natal/generation_contracts.py` defines `theme_natal.reading.free_preview.v1`. | `python -B -m pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py --tb=short` PASS. | PASS |
| AC2 | Basic full has its own contract. | `generation_contracts.py` defines `theme_natal.reading.basic_full_reading.v1`. | Unit contract tests PASS. | PASS |
| AC3 | Premium full has its own contract. | `generation_contracts.py` defines `theme_natal.reading.premium_full_reading.v1`. | Unit contract tests PASS. | PASS |
| AC4 | Engine profiles are versioned. | `ThemeNatalEngineProfile.version` is populated per variant. | `test_contract_sections_are_versioned_and_store_ready` PASS. | PASS |
| AC5 | Data visibility classes are explicit. | `ThemeNatalDataContract` separates `prompt_visible`, `validation_only`, and `audit_only`. | Unit contract tests PASS. | PASS |
| AC6 | Prompt contract versions are pinned. | `ThemeNatalPromptContract.version` is pinned per variant. | Unit contract tests PASS. | PASS |
| AC7 | Raw schemas differ from public schemas. | `generation_schemas.py` defines separate raw provider and public projected Pydantic models/schemas. | `test_raw_and_public_schemas_are_distinct_and_recursively_closed` PASS. | PASS |
| AC8 | Unknown fields are recursively rejected. | Strict Pydantic models use `extra="forbid"` and exported JSON schemas are checked recursively. | `python -B -m pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py --tb=short` PASS; evidence `evidence/strict-schema-after.txt`. | PASS |
| AC9 | Snapshot metadata is store-ready. | `ThemeNatalResolvedGenerationContractSnapshot` exposes all required version/hash fields. | Unit snapshot metadata test PASS; evidence `evidence/snapshot-after.txt`. | PASS |
| AC10 | Resolved snapshots stay immutable. | `resolve_theme_natal_generation_contract` deep-copies the resolved contract before hashing/snapshotting. | `test_resolved_snapshot_is_not_changed_by_registry_mutation` PASS. | PASS |
| AC11 | Basic avoids old schema keys. | Basic contract does not contain old schema/prompt tokens and differs from Premium raw/public schemas. | Anti-collision pytest PASS; scan persisted in `evidence/basic-collision-scan-after.txt`. | PASS |
| AC12 | Contract modules stay pure. | `backend/app/domain/theme_natal/**` imports only pure domain/Pydantic/stdlib dependencies. | AST import guard in `test_generation_contracts.py` PASS. | PASS |
| AC13 | Story evidence artifacts are persisted. | `evidence/contracts-before.txt`, `contracts-after.txt`, `strict-schema-after.txt`, `snapshot-after.txt`, and scan outputs are present. | `condamad_validate.py <capsule>` PASS before implementation evidence; final validation rerun after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
