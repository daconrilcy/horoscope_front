# Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `ReferenceDataService.get_active_reference_data` in natal flow | service call | historical-facade for this flow | none in `services/natal` or `domain/astrology` | `AstrologyRuntimeReferenceRepository.load` | replace-consumer | negative scan zero-hit | none |
| `reference_data: dict` business input | signature | active legacy removed | tests migrated | `AstrologyRuntimeReference` | replace-consumer | guard test on `build_natal_result` signature | none |
| Partial business dict fixtures | tests | active legacy removed | natal/aspect tests | `tests.factories.astrology_runtime_reference_factory` | replace-consumer | domain subset tests PASS | none |
| Forbidden DB-backed constants in natal runtime | constants | active legacy removed for touched flow | none in natal/domain runtime scans | DB/runtime contracts | delete | negative scans zero-hit | none |
| `phase="unknown"` aspect runtime sentinel | sentinel | active legacy removed | aspect runtime builder | `phase=None` | delete | aspect runtime tests PASS | none |
| SwissEph to simplified implicit fallback | fallback | active legacy removed | none | explicit simplified option/test config or explicit unavailable error | delete | natal service tests + scan zero-hit | default SwissEph disabled now fails explicitly |
