# Evidence Log - backend-docs

| ID | Evidence type | Command / Source | Target | Result | Notes |
|---|---|---|---|---|---|
| E-001 | previous-audit | Read `_condamad/audits/backend-docs/2026-05-04-1826/*` | prior backend-docs audit | PASS | Prior findings targeted ownership index, entitlement parity/status, LLM governance, calibration artifact location, and executable LLM registry preservation. |
| E-002 | guardrails-consulted | Read `_condamad/stories/regression-guardrails.md` | regression guardrails | PASS | `RG-040` through `RG-043` directly cover backend docs ownership, entitlement doc status/runtime parity, LLM source-truth governance, and calibration artifact placement. |
| E-003 | current-inventory | `rg --files backend/docs docs/calibration` | current docs inventory | PASS | `backend/docs` has seven root files and no `backend/docs/calibration` file. Root `docs/calibration` contains the canonical calibration artifacts. |
| E-004 | ownership-index | Read `backend/docs/ownership-index.md` and `backend/app/tests/unit/test_backend_docs_ownership.py` | backend docs governance | PASS | Every current `backend/docs` file is classified with owner, artifact type, canonical status, and targeted pytest guard. |
| E-005 | llm-doc-governance | Read `backend/app/tests/unit/test_llm_docs_governance.py` and LLM doc headers | LLM docs | PASS | LLM prose with normative wording must be guarded or marked `non-canonical-human-note`; current prose files include explicit non-canonical status. |
| E-006 | llm-executable-assets | Read `backend/tests/unit/test_llm_canonical_perimeter.py`, `backend/app/ops/llm/db_cleanup_validator.py`, and registry references | LLM generated/executable assets | PASS | `llm-model-structure.md` is generated/compared; `llm-db-cleanup-registry.json` is loaded from `backend/docs` by runtime validation code. |
| E-007 | entitlement-doc-status | Read `backend/docs/entitlements-canonical-platform.md` header and `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py` | entitlement doc | PASS | The doc explicitly says `Document status: historical-note` and the test checks critical route/table parity plus historical status. |
| E-008 | calibration-location | Read `backend/app/tests/unit/test_calibration_artifact_locations.py`; `rg --files backend/docs/calibration docs/calibration` | calibration artifacts | PASS | `backend/docs/calibration` is absent; root `docs/calibration` is the guarded canonical location. |
| E-009 | placement-scan | `rg -n "Document status" backend/docs`; `rg -n "canonical" backend/docs`; `rg -n "legacy" backend/docs` | remaining backend docs | PASS | Non-canonical/historical status is visible in LLM prose and entitlement prose; generated/executable assets still contain canonical runtime terms by design. |

## Limitations

- This was a documentation placement audit, not a content accuracy audit of each historical claim.
- Runtime tests were executed separately as validation evidence, but no application code was modified.
