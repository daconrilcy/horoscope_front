# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `llm_input_hash` is stable. | `build_llm_input_hash_material` centralise les blocs prompt-visible dans `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`. | `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_hash.py --tb=short`; `evidence/hash-cases.json`. | PASS |
| AC2 | Prompt-visible signals alter the hash. | Test de mutation `interpretive_signals.dignity_codes` via `LLMAstrologyInputV1Builder`. | `test_prompt_visible_signal_change_alters_llm_input_hash`; `changed_prompt_visible_signal_hash` dans `evidence/hash-cases.json`. | PASS |
| AC3 | Runtime-only changes preserve `llm_input_hash`. | `request_id`, `trace_id`, `chart_json`, `natal_data` sont classés `runtime_only` hors matériau de hash. | `test_runtime_only_request_identity_preserves_llm_input_hash`; test d'audit request_id dans `tests/integration/llm/test_natal_llm_astrology_input_audit.py`. | PASS |
| AC4 | Hash identities stay distinct. | `projection_hash` vient de la provenance factuelle; `llm_input_hash` vient du matériau prompt-visible; l'audit natal importe la version du contrat LLM. | `python -B -m pytest -q tests/architecture/test_llm_astrology_input_audit_boundary.py --tb=short`; scan négatif `llm_input_identity`. | PASS |
| AC5 | `evidence_refs` match exposed sources. | Le bloc evidence du contrat référence le `projection_hash` autorisé et conserve le validator canonique. | `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short`; `evidence/evidence-coherence.txt`. | PASS |
| AC6 | Invalid evidence refs are rejected. | Les refs avec hash incohérent restent `ungrounded` via `evidence_refs_validation.py`. | `test_invalid_evidence_ref_hash_is_rejected`. | PASS |
| AC7 | Audit payload stores both hashes coherently. | `_apply_narrative_answer_audit` persiste version/hash LLM, projection hash, grounding status et evidence refs du contrat. | `python -B -m pytest --long -q tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`; `evidence/audit-payload.json`. | PASS |
| AC8 | Data role classes are tested. | `LLM_ASTROLOGY_INPUT_DATA_ROLES` distingue prompt-visible, runtime-only, validation-only et audit-only. | Unit hash + integration audit tests. | PASS |
| AC9 | Public API surface stays unchanged. | Aucun fichier API/frontend/OpenAPI n'est modifié; garde `TestClient` et checks runtime. | `python -B -c "from app.main import app; assert 'llm_input_hash' not in str(app.openapi())"`; route check; architecture test. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/hash-cases.json`, `evidence/evidence-coherence.txt`, `evidence/audit-payload.json`, `evidence/validation.txt` créés. | `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py ...`; présence vérifiée par la capsule et diff. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
