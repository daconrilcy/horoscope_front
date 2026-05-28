# Dev Log - CS-376

<!-- Commentaire global: ce journal garde les decisions d'implementation et incidents utiles pour la review CS-376. -->

## 2026-05-29

- Preflight: `story-status.md` row CS-376 matched the requested story path and source brief.
- Capsule: required generated files were missing, then repaired with `condamad_prepare.py --repair-generated-only` and validated.
- Incident handled: an initial prepare attempt used a lowercase capsule path; on Windows this resolved to the canonical folder. The tracked story and review files were restored from Git content through patch, then the capsule was repaired.
- Implementation: added `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py` and registered the `provider_smoke` marker.
- Validation: targeted pytest, marker-selected skip, `ruff check .`, standard backend tests excluding provider smoke, guard scans, and `git diff --check` passed.
- Propagation: no-propagation; no reusable skill or guardrail update was needed.
