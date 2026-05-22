<!-- Matrice de tracabilite generee pour CS-217. -->

# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Define canonical chart-object runtime contracts. | `chart_object_runtime_data.py` dataclasses/enums. | Runtime builder tests and contract assertions. | PASS |
| AC2 | Expose required enum values and dataclass fields. | `ChartObjectType`, `ChartObjectSourceType`, payload/source/capability dataclasses. | Contract shape tests. | PASS |
| AC3 | Keep contract minimal and extensible by typed payloads. | Payload slots instead of monolithic optional business fields. | Contract tests and diff review. | PASS |
| AC4 | Project planets and luminaries. | `chart_object_runtime_builder.py`. | Builder tests. | PASS |
| AC5 | Project configured astral points. | Builder maps `NatalAstralPointPosition`-like inputs. | Builder and natal integration tests. | PASS |
| AC6 | Project angles from house data. | Builder maps ASC/DSC/MC/IC from cusp houses. | Builder tests. | PASS |
| AC7 | Project house cusps. | Builder maps 12 `HOUSE_CUSP` objects. | Builder tests. | PASS |
| AC8 | Add `NatalResult.chart_objects`. | `natal_calculation.py` field and pipeline call. | Natal integration tests. | PASS |
| AC9 | Preserve historical collections. | Existing fields untouched. | Natal non-regression tests. | PASS |
| AC10 | Avoid public schema/output change. | `SkipJsonSchema` + `exclude=True`. | Schema/model dump tests. | PASS |
| AC11 | Missing payload for declared capability raises explicit error. | `ChartObjectRuntimeData.__post_init__`. | Negative contract test. | PASS |
| AC12 | Objects are filterable by `supports_aspects`. | Capabilities populated. | Builder tests. | PASS |
| AC13 | Objects are filterable by `supports_dignities`. | Dignity capability remains false without payload. | Builder tests. | PASS |
| AC14 | Objects are filterable by `supports_house_position`. | Capabilities populated and validated by `house_position` payload. | Builder tests. | PASS |
| AC15 | New modules remain pure. | Runtime/builder avoid IO, DB, API, services, Pydantic. | Architecture guard and scans. | PASS |
| AC16 | Business calculators avoid `object_type` branches. | AST guard over calculator domains. | Architecture guard and scans. | PASS |
| AC17 | Out-of-scope surfaces unchanged. | No edits to API/infra/frontend/json builder/scoring domains. | Diff and scan review. | PASS |
| AC18 | `RG-144` is registered. | Regression guardrail remains present. | `Select-String "RG-144" ...`. | PASS |
