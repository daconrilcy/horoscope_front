# No Legacy / DRY Guardrails

## Canonical Ownership

- `docs/architecture/structured-facts-v1-contract.md` is the only canonical `structured_facts_v1` contract document added by CS-256.
- `docs/architecture/official-product-primitives-public-projections.md` remains the existing owner for the broader `structured_facts` product primitive.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` remains the owner for `AINarrativeInputContract`.
- `backend/app/domain/astrology/runtime/**` remains the source owner for runtime facts.

## Negative Guardrails

- No compatibility wrapper, alias, shim or fallback projection was added.
- No backend builder, service, serializer, route, OpenAPI schema, DB model or migration was added.
- No frontend source, generated client, style file or browser-facing route was added.
- Raw runtime names are cited only as excluded internal surfaces, not as public payload fields.
- Narrative text, prompt text, advice and LLM output are forbidden from the `structured_facts_v1` projection.

## Validation Evidence

- `git status --short -- backend\app frontend\src`: PASS, no output.
- `app.openapi()` assertion: PASS, `structured_facts_v1` is absent from public OpenAPI.
- `app.routes` assertion: PASS, no route path contains `structured_facts`.
- Targeted contract scans: PASS for required families, hash rules, AI linkage and raw-surface exclusions.

## Review Questions Answered

- Legacy path deleted or moved: not applicable; CS-256 adds documentation only.
- Temporary compatibility preserved: no.
- Duplicate active implementation introduced: no.
- Old namespace imported by tests: not applicable; no runtime or test code changed.
- Registry/config drift: no application registry or config changed.
