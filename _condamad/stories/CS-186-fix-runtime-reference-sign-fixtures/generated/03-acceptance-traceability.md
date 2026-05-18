# Acceptance Traceability - CS-186

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Listed tests no longer fail on missing sign profile fields. | Partial sign payloads replaced in affected tests. | `pytest -q ...affected files... app/tests/unit/test_astrology_runtime_reference_guard.py` passed. | PASS |
| AC2 | Runtime factory remains strict and no silent completion returns. | `_complete_sign_payload()` strict missing-field error unchanged. | Existing guard passed; full backend suite passed. | PASS |
| AC3 | Callers use one explicit test helper for complete sign payloads. | `complete_sign_payloads()` added and imported by affected tests. | Diff review and targeted pytest passed. | PASS |
| AC4 | Guardrails RG-107/RG-108/RG-112/RG-114 remain respected. | No production astrology/runtime files changed by this story. | RG scans passed; guard file hit for `SIGN_PROFILE_DATA` classified as expected self-check. | PASS |
| AC5 | Validations pass with venv activated. | No code impact beyond tests/fixtures/capsule. | Ruff format/check and `pytest -q` passed. | PASS |
