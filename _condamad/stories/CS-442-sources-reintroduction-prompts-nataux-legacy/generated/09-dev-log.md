# Dev Log

## 2026-06-01

- Preflight: `.git` present; initial dirty file was `_condamad/run-state.json` and was left untouched.
- Capsule repair: generated files were missing; ran `condamad_prepare.py --repair-generated-only` and `condamad_validate.py` under `.venv`.
- Implementation: removed legacy natal prompt seed sources, admin `natal_long_free` derivation, old catalog/registry prompt source entries, and old seed calls from local bootstrap paths.
- Tests/guards: converted old positive seed/admin/orchestration tests into absence or rejection guards; preserved `theme_astral` as modern owner for `basic_natal_prompt_payload`.
- Evidence: persisted before/after scan, removal audit, residual allowlist, validation log, traceability and final evidence.
