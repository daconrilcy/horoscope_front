# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Repository loads four attributes. | `AstrologyRuntimeReferenceRepository._load_sign_profiles()` joins CS-234 taxonomies and emits `seasonal_quadrant`, `fertility`, `voice`, `form`. | Targeted pytest PASS; repository assertions include all four values. | PASS |
| AC2 | Mapper rejects missing structural sign values. | `AstrologyRuntimeReferenceMapper` uses `_required_str` for all four added fields; `SignReferenceData` also rejects blank/`unknown`. | Targeted pytest PASS through repository and factory construction; missing profile path still fails without fallback. | PASS |
| AC3 | `SignReferenceData` exposes four required fields. | `runtime_reference.py` adds required dataclass fields and validation. | Targeted pytest PASS. | PASS |
| AC4 | `SignRuntimeData` receives values from references. | `sign_runtime_data.py` adds required fields; `sign_runtime_builder.py` copies them from `SignReferenceData`. | `tests/unit/domain/astrology/test_sign_runtime_builder.py` PASS. | PASS |
| AC5 | Public `signs_runtime` exposes additive fields. | `_serialize_signs_runtime()` projects all four fields. | `app/tests/unit/test_chart_json_builder.py` PASS; `evidence/signs-runtime-json.txt`. | PASS |
| AC6 | Factories avoid production sign mappings. | Test factory records are explicit and guard forbids production mapping symbols. | `app/tests/unit/test_astrology_runtime_reference_guard.py` PASS. | PASS |
| AC7 | Domain astrology has no forbidden mappings. | No production mapping symbols added. | Targeted `rg` exit 1, PASS no matches. | PASS |
| AC8 | Natal services have no forbidden mappings. | No natal service files changed. | Targeted `rg` exit 1, PASS no matches. | PASS |
| AC9 | Story evidence artifacts are persisted. | `evidence/*.json`, `evidence/*.txt`, `generated/10-final-evidence.md`. | Evidence directory and `validation.txt` checks PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
