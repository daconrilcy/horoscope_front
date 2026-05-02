# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le fichier cible est classifie dans `removal-audit.md`. | Added `removal-audit.md` and `reference-baseline.txt`. | `rg -n "validate_route_removal_audit.py\|validate_route_removal_audit" . -g '!artifacts/**' -g '!.codex-artifacts/**'`; audit row classifies the item `dead`. | PASS |
| AC2 | Un item `dead` est supprime sans wrapper ni alias. | Deleted `scripts/validate_route_removal_audit.py`; no replacement command added. | `rg -n "validate_route_removal_audit.py" scripts backend frontend docs` returned no active consumer hit after deletion. | PASS |
| AC3 | La story historique ne cite plus la commande racine. | Updated `remove-historical-facade-routes` story/generated references away from the removed executable command. | `rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes` returned no root command citation. | PASS |
| AC4 | Un garde echoue si le chemin racine revient. | Added `backend/app/tests/unit/test_scripts_ownership.py` and registered it in `ops-quality-test-ownership.md`. | `pytest -q app/tests/unit/test_scripts_ownership.py` and `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` passed. | PASS |
| AC5 | La story valide. | Updated `00-story.md` status/tasks and completed capsule evidence. | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-root-route-removal-audit-validator/00-story.md` and strict lint passed. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
