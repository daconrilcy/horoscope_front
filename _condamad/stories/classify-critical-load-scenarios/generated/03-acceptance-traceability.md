# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les groupes de scenarios attendus existent. | `scripts/load-test-critical.ps1` exposes explicit scenario groups for smoke, llm, b2b, destructive privacy, and stress incidents. | `pytest -q app/tests/unit/test_load_test_critical_script.py` | PASS |
| AC2 | Le groupe par defaut exclut `privacy_delete_request`. | Default selected groups omit `destructive-privacy`; delete scenario remains only in that explicit group. | `pytest -q app/tests/unit/test_load_test_critical_script.py` | PASS |
| AC3 | Les marqueurs story/legacy audites sont absents. | Remove active comments/labels containing `Story 66.35` and `Legacy critical scenarios`. | `rg -n "Story 66\\.35|Legacy critical scenarios" scripts/load-test-critical.ps1` | PASS |
| AC4 | Les rapports JSON/Markdown restent produits. | Preserve `ConvertTo-Json` report write and `generate-performance-report.ps1` invocation. | `pytest -q app/tests/unit/test_load_test_critical_script.py` | PASS |
| AC5 | La story valide. | Keep story source structurally valid and update capsule evidence. | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/classify-critical-load-scenarios/00-story.md` | PASS |
