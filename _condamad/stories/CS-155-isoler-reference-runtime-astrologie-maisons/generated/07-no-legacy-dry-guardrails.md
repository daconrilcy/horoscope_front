# No Legacy / DRY Guardrails

- Canonical runtime owner: `backend/app/domain/astrology/runtime/house_runtime_data.py`.
- Forbidden: product symbols in `domain/astrology`, duplicate house strength owner, chart-side ruler recalculation.
- Evidence: zero-hit product scan; runtime builder delegates interpretation instead of duplicating strength logic.
