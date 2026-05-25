# Dev Log

## 2026-05-25

- Initial worktree was already dirty with many unrelated story/review files; CS-280 changes were kept scoped.
- Capsule generated files were missing; `condamad_prepare.py --repair-generated-only` and `condamad_validate.py` were run after venv activation.
- A mistaken helper call created `_condamad/stories/cs-280`; the agent-owned parallel capsule was removed immediately and the target capsule was repaired.
- One baseline command was first launched from `backend` with the wrong relative venv path; the backend-local `_condamad` artifact was removed and the command rerun correctly from repo root with venv activation.
- Full backend pytest still fails on pre-existing ownership registry drift for `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`; CS-280 targeted tests and architecture guards pass.
- Implementation review found fixed-star capability leakage in the transit runtime output; `supports_fixed_star_conjunction` is now stripped from CS-280 payloads and tested.
- Full backend pytest blocker was closed by adding the missing security ownership registry row for `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`.
- Final validations passed: ruff format check, ruff check, targeted CS-280 tests, ownership guard, CONDAMAD validations and full backend pytest.
