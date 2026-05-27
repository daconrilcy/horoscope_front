# Acceptance Traceability

<!-- Commentaire global: cette trace relie chaque critere d'acceptation CS-338 aux preuves locales. -->

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The final closure report exists. | `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`; `evidence/legacy-scan-before.txt`; `evidence/legacy-scan-after.txt` | Capsule validation PASS; report path present | PASS |
| AC2 | The report proves a single natal LLM input path. | Report section `Preuves du chemin unique llm_astrology_input_v1`; guards in `backend/tests/integration/test_llm_legacy_extinction.py` | `python -B -m pytest -q --long tests\integration\test_llm_legacy_extinction.py --tb=short` PASS, 7 tests | PASS |
| AC3 | Remaining legacy terms are classified. | Report table `References restantes et justification`; scan artifacts under `evidence/` | `rg ... "chart_json\|natal_data\|evidence_catalog\|legacy\|fallback\|transition-condition"` PASS with classified occurrences | PASS |
| AC4 | Backend tests run without obsolete natal LLM mocks. | No compatibility mock added; new tests are negative guards only | `python -B -m pytest -q --long tests --tb=short` PASS, 1420 passed, 9 skipped | PASS |
| AC5 | Modern guards cover `llm_astrology_input_v1`. | New guards verify modern schema, prompt payload, and validation payload ownership | `python -B -m pytest -q --long tests\integration\test_llm_legacy_extinction.py --tb=short` PASS | PASS |
| AC6 | Documentation stops presenting old carriers as active. | Final report classifies historical `_condamad` and `_story_briefs` occurrences as archive-documentaire, not active runtime | Documentation scan persisted in `evidence/legacy-scan-after.txt` and classified in report | PASS |
| AC7 | Reintroduction guard blocks old carriers. | `test_natal_validation_payload_ignores_declared_legacy_carriers`; `test_natal_user_payload_ignores_legacy_carriers_when_modern_input_exists` | Targeted integration test PASS; runtime suppression test PASS | PASS |
| AC8 | External ambiguity blocks closure. | Report states no `decision-utilisateur-requise`; non-natal `event_guidance` and generic runtime fields are ownerised | Manual classification in report plus scoped `rg` evidence | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
