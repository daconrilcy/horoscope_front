# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `ThemeNatalReadingSlot` stores public slot state. | `backend/app/infra/db/models/theme_natal_reading_slot.py`, migration `20260601_0142`, service `ThemeNatalReadingSlotService`. | `python -B -m pytest -q --long tests/integration -k "theme_natal and slot" --tb=short`: 7 passed. `evidence/schema-after.txt`: slot columns present. | PASS |
| AC2 | `LlmGenerationRun` stores technical attempt state. | `backend/app/infra/db/models/llm_generation_run.py` stores raw/parsed responses, validation errors, rejection reason and reproducibility hashes. | Same integration suite; `evidence/schema-after.txt`: run columns and indexes present. | PASS |
| AC3 | Slot identity is DB-unique on the full product key. | Partial unique indexes `uq_theme_natal_reading_slots_null_persona` and `uq_theme_natal_reading_slots_with_persona` include product key and nullable persona handling. | `test_theme_natal_slot_schema_exposes_public_and_run_contract`; Alembic upgrade proof in `evidence/schema-after.txt`. | PASS |
| AC4 | Slot status is constrained to the approved lifecycle. | `THEME_NATAL_READING_SLOT_STATUSES` + SQL `CheckConstraint`. | Integration schema test and `ruff check .`: PASS. | PASS |
| AC5 | Rejected run leaves payload unchanged. | `record_rejected_run` updates only `LlmGenerationRunModel`; `publish_accepted_payload` refuses to replace accepted slot payload. | `test_theme_natal_slot_rejected_run_does_not_replace_accepted_payload`; rejected legacy boundary suite: 8 passed. | PASS |
| AC6 | Public GET/list sees accepted slots only. | `get_public_slot_by_key` and `list_public_slots` filter `status == accepted` and never read run payloads. | `test_theme_natal_slot_public_get_and_list_return_accepted_only`. | PASS |
| AC7 | Concurrent claims create one slot per product key. | Claim path uses transaction commits, DB unique indexes, and explicit `IntegrityError` recovery to re-read the existing slot/run. | `test_theme_natal_slot_claims_share_product_slot_without_same_client_id`; Alembic schema unique indexes. | PASS |
| AC8 | Concurrent accepted persistence consumes one quota unit. | `publish_accepted_payload` returns `accepted_now`; `consume_quota_after_publication` debits only when true. | `test_theme_natal_slot_publication_reports_acceptance_once`; `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`: 5 passed. | PASS |
| AC9 | Reused `client_request_id` returns the same logical state. | Run lookup is keyed by `slot_id + client_request_id` before create. | `test_theme_natal_slot_reuses_run_for_same_client_request_id`. | PASS |
| AC10 | Reused `client_request_id` creates no extra run. | Unique run index `uq_llm_generation_runs_slot_client_request` plus `IntegrityError` recovery. | `test_theme_natal_slot_reuses_run_for_same_client_request_id`; run count remains 1. | PASS |
| AC11 | `chart_id` participates in slot identity. | Model, migration and unique indexes include `chart_id`; key object requires `chart_id`. | `test_theme_natal_slot_unique_key_includes_chart_id`; `rg -n "chart_id" backend/app backend/tests` includes new model/service/tests. | PASS |
| AC12 | `created_at` is immutable; `accepted_at` changes only on acceptance. | Service only sets `accepted_at` during first accepted publication and does not mutate `created_at`. | `test_theme_natal_slot_rejected_run_does_not_replace_accepted_payload`. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
