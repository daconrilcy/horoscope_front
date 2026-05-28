# Acceptance Traceability - CS-358

| AC | Requirement | Status | Implementation evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | Required example folder contains five deliverables. | PASS | Five deliverables created under `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/`. | `evidence/json-validation.txt`; `evidence/baseline-before.txt`; `evidence/baseline-after.txt`. |
| AC2 | All example JSON files parse successfully. | PASS | Four JSON files are static provider-handoff/intermediate examples. | `python -B -m json.tool` for each JSON file in `evidence/json-validation.txt`. |
| AC3 | Each plan payload is distinct. | PASS | `free`, `basic`, and `premium` payloads differ by plan, user prompt-visible data, response schema, and provider parameters. | Distinct payload assertion in `evidence/json-validation.txt`. |
| AC4 | Message roles follow provider handoff. | PASS | Each provider payload uses ordered roles `system`, `developer`, `developer`, `user`, aligned with `LLMGateway.compose_structured_messages`. | Role assertion in `evidence/json-validation.txt`; runtime source inspection recorded in `generated/09-dev-log.md`. |
| AC5 | No provider call is represented. | PASS | `provider_call_performed` is `false`; examples are marked `synthetic_example`; no runtime provider path was called. | `evidence/forbidden-scan.txt`; `evidence/provider-boundary-test.txt` (`4 passed`). |
| AC6 | User messages contain prompt-visible blocks only. | PASS | User message content contains only `facts`, `signals`, `limits`, and `shaping`. | Prompt-boundary assertion in `evidence/json-validation.txt`. |
| AC7 | Audit-only exclusions are listed outside prompt content. | PASS | `audit_excluded_from_prompt` lists `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, and `observability`. | Exclusion assertion in `evidence/json-validation.txt`. |
| AC8 | Missing birth time is documented as a convention. | PASS | README and JSON document `12:00:00`, `Europe/Paris`, and `synthetic_example`, including unverified houses/Ascendant/MC. | Positive marker scan in `evidence/forbidden-scan.txt`. |
| AC9 | README explains generation method. | PASS | README explains static synthetic generation and source alignment. | Positive marker scan in `evidence/forbidden-scan.txt`. |
| AC10 | Forbidden provider artifacts are absent. | PASS | No provider result body, token, API key, Bearer marker, credential wording, or access material is present. The exact string `provider_response` appears only because AC7 requires it in `audit_excluded_from_prompt`. | `evidence/forbidden-scan.txt` records the expected exclusion-label assertion and validates `provider_response` is absent from prompt messages. |

## Guardrail Evidence

- RG-002: no `backend/app/api/**` or backend runtime source changed; see `evidence/runtime-frontend-status.txt`.
- RG-022: validation plan executed with JSON checks, prompt-boundary assertion, no-provider-call tests, differentiation test, and `ruff check backend`.
