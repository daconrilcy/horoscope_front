# Execution Brief

- Story key: `deversionner-referentiels-astrologiques`
- Objective: remove version ownership from invariant astrology structure tables while preserving versioning for prediction profiles, weights, categories and rulesets.
- Boundaries: backend SQLAlchemy models, repositories, seed, Alembic migrations, backend tests, CONDAMAD evidence.
- Non-goals: no frontend changes, no API redesign, no dependency changes, no broad formatting.
- Preflight: protect existing dirty `.codex-artifacts/**` and `output/` changes.
- Completion: all ACs have code and validation evidence; Python commands run after `.\.venv\Scripts\Activate.ps1`; final evidence and story status updated.
- Halt: stop only if migration cannot safely deduplicate existing structural rows or validation reveals an unclear destructive data loss risk.
