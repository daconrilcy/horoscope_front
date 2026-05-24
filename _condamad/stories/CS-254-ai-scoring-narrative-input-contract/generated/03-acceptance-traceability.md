# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The AI input contract is versioned. | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` defines `AI_NARRATIVE_INPUT_CONTRACT_VERSION` and `AINarrativeInputContract.contract_version`. | `python -B -m pytest -q tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py` PASS. | PASS |
| AC2 | Structural facts are separated. | `AINarrativeStructuralFacts` is a top-level section assembled by `AINarrativeInputBuilder` from `ChartInterpretationInputRuntimeData`. | Contract unit test PASS; `evidence/contract-after.md` records top-level fields. | PASS |
| AC3 | Interpretive signals are separated. | `AINarrativeInterpretiveSignals` keeps dignity, dominance, house, rulership, fixed-star and advanced-condition codes outside structural facts. | Contract unit test PASS. | PASS |
| AC4 | Prompt text is not a truth source. | Builder consumes `ChartInterpretationInputBuilder` output only; architecture guard checks forbidden source fields on AI contract modules. | `python -B -m pytest -q tests/architecture/test_ai_narrative_input_boundary.py` PASS. Broad runtime/interpretation scan is zero-hit after converging the astral-point narrative context naming. | PASS |
| AC5 | Provider integration is not added. | No provider imports or gateway code in new AI input modules. | Provider scan on `backend/app/domain/astrology/interpretation` returned no matches. | PASS |
| AC6 | Public projection links stay controlled. | `AINarrativePublicProjectionLink` stores owner/primitive/projection references only; no API/router/schema file touched. | `test_api_contract_neutrality.py` PASS; `openapi-before.json` and `openapi-after.json` hashes match. | PASS |
| AC7 | Calculation modules reject narrative tokens. | `test_ai_narrative_input_boundary.py` prevents calculation roots importing AI input, narration, LLM or provider layers. | Architecture guard PASS and full backend pytest PASS. | PASS |
| AC8 | Evidence artifacts are persisted. | Evidence folder contains before/after contract, before/after OpenAPI, validation and boundary-scan artifacts. | Capsule validation PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
