# No Legacy / DRY Guardrails CS-191

- No compatibility wrapper, alias, fallback, re-export or duplicate active path introduced.
- `backend/app/domain/astrology/dignities/**` does not import infra, services, API, DB sessions, SQLAlchemy selectors, prediction or LLM runtime.
- Scoring values are read from `AstrologyRuntimeReference.dignity_reference` score weights; no local score mapping is defined in calculators.
- Conditions for houses, motion, joys and solar state are read from accidental dignity runtime rules.
- Applicable guardrails: RG-095, RG-107, RG-108, RG-112, RG-114, RG-115, RG-116, RG-118.
