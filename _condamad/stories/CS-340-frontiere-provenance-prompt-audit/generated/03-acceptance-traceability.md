# Acceptance Traceability

<!-- Commentaire global: cette matrice relie chaque critere d'acceptation CS-340 aux preuves runtime, scans et rapport de cloture. -->

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The boundary validation report exists in a `YYYY-MM-DD-HHMM` directory. | `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` | `python -B -c "...root.glob..."` PASS in `evidence/validation-output.txt`. | PASS |
| AC2 | Tests no longer require `provenance.llm_input_hash` in the prompt. | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` asserts prompt payload keys equal canonical `PROMPT_VISIBLE_BLOCKS` and audit-only nested keys are absent. | Targeted pytest PASS; boundary scans saved before/after. | PASS |
| AC3 | Provider handoff payload excludes audit-only fields. | `test_gateway_provider_handoff_uses_local_double_and_prompt_boundary` inspects `mock_client.execute` messages and rejects nested `provenance`, hashes, `grounding_status`, `validation_owner`, and `evidence_refs`. | `python -B -m pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py ...` PASS. | PASS |
| AC4 | Persistent audit keeps the full brief-required audit field set. | `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` checks `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status`, `evidence_refs`. | Targeted audit pytest PASS. | PASS |
| AC5 | Modern natal use cases avoid hash provenance placeholders. | Registry/prompt placeholder scan found no `{{provenance}}`, `{{projection_hash}}`, or `{{llm_input_hash}}` in `backend/app` or `backend/tests`. | `rg -n "{{provenance}}|{{projection_hash}}|{{llm_input_hash}}" app tests` returned no matches and is recorded as PASS. | PASS |
| AC6 | Backend validation commands pass. | Runtime projection now removes nested audit/validation keys before provider handoff; guards prove the corrected boundary. | `ruff format --check app tests`, `ruff check .`, targeted pytest, and full `python -B -m pytest -q tests --tb=short` PASS. | PASS |
| AC7 | Remaining prompt/audit terms are classified. | Report section `Resultats de scans` classifies audit/persistence owned, internal non-prompt contract, guard test, historical evidence, and debt. | `boundary-scan-before.txt`, `boundary-scan-after.txt`, and report section check PASS. | PASS |
| AC8 | CS-339 is complete before closure execution. | `_condamad/stories/story-status.md` row `CS-339` is `done`. | `python -B -c "...CS-339..."` PASS in `validation-output.txt`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
