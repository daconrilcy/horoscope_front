# Eligibility After

- Canonical owner added: `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py`.
- `EligibilityContext` exposes `birth_time_status`, `can_use_houses`, `can_use_angles`, `can_use_house_rulers`, `can_use_lunar_nodes_by_house` and public `limitations`.
- Full birth time enables house-dependent families when the surfaces exist.
- Approximate birth time or missing timezone produces cautious public limitations.
- Date-only mode disables house-dependent families and filters prompt-visible houses, position house numbers, house-position signals, ruler signals and angular dominance factors.
- Non-time-dependent signs, sign balances and major aspects remain available in the LLM input.
