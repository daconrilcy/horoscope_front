# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Free short returns `meta.level=short`. | `NatalInterpretationService` coerces free-short public meta to `short`. | `test_free_short_public_contract_exposes_short_astro_free_payload` PASS. | PASS |
| AC2 | Free short returns readable `AstroFreeResponseV1` content. | Free short still deserializes as `AstroFreeResponseV1` and serializes title, summary, sections, highlights, advice. | Public contract test PASS; `public-contract-after.json`. | PASS |
| AC3 | Free short exposes canonical disclaimers. | Free short response keeps `get_disclaimers(locale)` in response and interpretation payload. | Public contract test asserts interpretation disclaimers equal response disclaimers. | PASS |
| AC4 | Free short does not require `narrative_natal_reading_v1`. | Free short deserializer is keyed by `variant_code=free_short` / `natal_long_free`, not by narrative payload presence. | Public contract test asserts `narrative_natal_reading_v1 is None`. | PASS |
| AC5 | Basic complete returns non-null Basic V2 payload. | Basic V2 payload continues to load through `load_basic_natal_interpretation_v2_from_payload`. | Public contract test and Basic V2 pipeline/cache tests PASS. | PASS |
| AC6 | Basic complete returns the complete Basic V2 version block. | `BasicNatalInterpretationV2` remains canonical response field. | Public contract test asserts locale, level, engine, schema, taxonomy, salience, prompt and validator versions. | PASS |
| AC7 | Basic complete returns the required public synthesis body. | Basic V2 `interpretation` body is emitted under `data.basic_natal_interpretation_v2`. | Public contract test asserts introduction, themes and public evidence. | PASS |
| AC8 | Basic complete exposes coherent public disclaimers. | Basic V2 disclaimers remain serialized from the contract. | Public contract test asserts non-empty Basic disclaimers. | PASS |
| AC9 | `data.interpretation` remains a free compatibility surface. | Free short keeps `data.interpretation` as the readable `AstroFreeResponseV1` compatibility surface. | Public contract test PASS. | PASS |
| AC10 | Accepted public payloads exclude technical markers. | Public serializer still removes evidence; tests assert denylisted markers absent from accepted public JSON. | Public contract test PASS; targeted scans recorded in `evidence/validation.txt`. | PASS |
| AC11 | Before snapshot is persisted. | `evidence/public-contract-before.json` written before code changes. | Snapshot file exists and captures pre-change free public `complete`/`natal_long_free`. | PASS |
| AC12 | After snapshot is persisted. | `evidence/public-contract-after.json` written after implementation. | Snapshot file exists and captures free public `short`/`natal_interpretation_short`. | PASS |
| AC13 | Runtime API contract remains registered. | Public FastAPI route still uses `NatalInterpretationResponse`. | TestClient/OpenAPI test PASS; python route/openapi assertions PASS. | PASS |
| AC14 | Free short keeps `data.basic_natal_interpretation_v2=null`. | Free short public response does not attach Basic V2 payload. | Public contract test asserts `basic_natal_interpretation_v2 is None`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
