# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Replay produces at most one Free preview. | `backend/tests/integration/test_theme_natal_bigbang_replay.py` verifies the second Free preview claim reuses the same slot. | `evidence/replay-free-basic-generate-full.md`; targeted pytest PASS. | PASS |
| AC2 | Replay produces at most one Basic full reading. | `test_free_to_basic_replay_persists_one_preview_and_one_basic_full_reading` groups accepted slots by `chart_id/output_variant`. | `evidence/replay-free-basic-generate-full.md`; targeted pytest PASS. | PASS |
| AC3 | Basic full reading stores contract metadata. | Replay test asserts `generation_contract_key`, `generation_contract_hash`, `output_schema_version`, and `data_hash` on the persisted run. | `evidence/replay-free-basic-generate-full.md`; targeted pytest PASS. | PASS |
| AC4 | Post-upgrade short reading is not created. | Frontend `natalInterpretation.test.tsx` keeps preview disabled after Basic access; backend product-action route rejects old fields. | `pnpm --dir frontend test -- natalInterpretation NatalChartPage natalPublicDomGuard`: PASS; backend targeted pytest PASS. | PASS |
| AC5 | Concurrent `generate_full` keeps one generating slot. | `backend/tests/integration/test_theme_natal_concurrency.py` covers shared slot and serialized claim lock. | `evidence/concurrency-proof.md`; targeted pytest PASS. | PASS |
| AC6 | Paid Basic action resolves with Basic entitlement. | `backend/tests/integration/test_theme_natal_entitlement_freshness.py` asserts the runtime receives the Basic access result. | `evidence/entitlement-freshness-proof.md`; targeted pytest PASS. | PASS |
| AC7 | Old natal symbols have no public generator hit. | `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` guards product-action/runtime owners; scans classify residual hits. | `evidence/legacy-scan-results.md`; targeted pytest PASS. | PASS |
| AC8 | Public DOM exposes no technical leak. | `frontend/src/tests/natalPublicDomGuard.test.tsx` denies technical and legacy-control patterns in rendered public content. | `pnpm --dir frontend test -- natalInterpretation NatalChartPage natalPublicDomGuard`: PASS. | PASS |
| AC9 | Public count grouping uses chart-variant keys. | Replay test groups accepted slots with `Counter((chart_id, output_variant))`. | `evidence/replay-free-basic-generate-full.md`; artifact check PASS. | PASS |
| AC10 | Public GET returns accepted readings only. | `backend/tests/integration/test_theme_natal_public_reads.py` uses TestClient and verifies rejected detail returns 404. | `evidence/public-get-list-accepted-only.md`; runtime route/OpenAPI commands PASS. | PASS |
| AC11 | Public list returns accepted readings only. | Same TestClient test verifies list `total=1` and only the accepted id. | `evidence/public-get-list-accepted-only.md`; targeted pytest PASS. | PASS |
| AC12 | Old public endpoint cannot generate. | Existing product-action integration tests cover 410 old endpoint and OpenAPI action schema; legacy scan classifies readonly hits. | Runtime route/OpenAPI commands PASS; `evidence/legacy-scan-results.md`. | PASS |
| AC13 | Basic paid action logs no `plan=free`. | Entitlement freshness test asserts `caplog.text` lacks `plan=free`. | `evidence/entitlement-freshness-proof.md`; targeted pytest PASS. | PASS |
| AC14 | Quota is debited once after accepted. | `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` adds a two-publication quota guard. | Unit pytest PASS; `evidence/concurrency-proof.md`. | PASS |
| AC15 | `RG-173` Big Bang guardrail is registered. | `_condamad/stories/regression-guardrails.md` contains `RG-173`; scans include contract markers. | VS4 scan PASS; `evidence/legacy-scan-results.md`. | PASS |
| AC16 | Story evidence artifacts are persisted. | `evidence/*.md`, `openapi-before.json`, `openapi-after.json`, and `validation-output.txt` are present. | Artifact check PASS; capsule validation PASS before final gate. | PASS |

All acceptance criteria have implementation and validation evidence for this run.
