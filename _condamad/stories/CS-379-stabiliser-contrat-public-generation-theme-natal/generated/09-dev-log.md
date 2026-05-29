# Dev Log

- Initial git status showed pre-existing untracked `_condamad/run-state.json`.
- Capsule generated files were missing and were repaired with `condamad_prepare.py --repair-generated-only`.
- Baseline evidence captured before code edits: POST/latest/OpenAPI.
- Implementation centralized public `traditional_conditions` projection in `json_builder.py` and wired POST/latest serializers through service data models.
- Validation evidence captured after code edits: POST/latest/OpenAPI, targeted pytest, provider pytest, route/OpenAPI runtime check, scoped negative prompt-carrier scan, Ruff.
