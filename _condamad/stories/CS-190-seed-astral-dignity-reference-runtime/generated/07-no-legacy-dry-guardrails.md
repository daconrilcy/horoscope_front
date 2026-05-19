# No Legacy / DRY Guardrails

- Canonical score profile table is `astral_diginity_score_profiles` per user instruction.
- Do not preserve `astral_essential_dignity_score_profiles` in backend models, seed FKs, migrations or repositories.
- Do not keep `score_profile_code` or `accidental_dignity_type_code` as DB columns when linked IDs are available.
- Reuse existing reference seed mechanics instead of introducing a parallel loader.
- Reuse existing repository/session patterns.
- Required negative evidence:
  - Search `astral_essential_dignity_score_profiles` and `accidental_dignity_type_code` across backend and seed JSON.
  - Search `score_profile_code` only in DB models, migrations and seed JSON; repository input parameters may still accept a profile code and resolve it to `score_profile_id`.
