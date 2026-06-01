# No Legacy / DRY Guardrails

## Applied stance

- No compatibility shim, alias, facade table, fallback write path, or duplicate active public persistence path was added.
- `UserNatalInterpretationModel` remains only as existing historical persistence outside the new slot/run ownership.
- New public slot reads use `ThemeNatalReadingSlotModel.status == "accepted"` and do not infer public state from LLM run rows.
- Rejected technical runs update `LlmGenerationRunModel` only and do not mutate accepted public payloads.

## Regression guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-011 | Applicable: new backend tests and DB persistence. | AST guard for direct `SessionLocal`/`engine` imports: PASS; `app/tests/unit/test_backend_db_test_harness.py`: PASS. |
| RG-150 | Applicable: rejected payloads excluded from public reads. | Rejected boundary suite: PASS; slot accepted-only tests: PASS. |
| RG-152 | Applicable: technical traces must not leak publicly. | Run traces stay in `LlmGenerationRunModel`; public methods return accepted slots only; public boundary tests: PASS. |
| RG-155 | Applicable: no fallback/padding path added. | `rg -n "fallback = response\.sections\[0\]" backend/app/services/llm_generation/natal`: no matches. |
| RG-157 | Applicable: quota after acceptance only. | Atomic accepted publication + quota unit tests: PASS; `rg -n "check_and_consume" ...`: no matches. |
| RG-168 | Applicable: product dimensions from CS-427 retained. | Uses `ThemeNatalOutputVariant`, `ThemeNatalReadingKind`, `THEME_NATAL_READING_FEATURE`; Basic contract guard tests: PASS. |

## Negative scans

- `rg -n "UserNatalInterpretationModel\.user_id == user_id,[\s\S]*UserNatalInterpretationModel\.level" backend/app/services/llm_generation/natal`: no matches.
- `rg -n "_slot_lock_for_key|_publication_lock_for_slot|status != THEME_NATAL_SLOT_STATUS_ACCEPTED" backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`: lock and atomic accepted-publication guard present.
- No new frontend, API DTO, provider, prompt, or legacy deletion surface was introduced.
