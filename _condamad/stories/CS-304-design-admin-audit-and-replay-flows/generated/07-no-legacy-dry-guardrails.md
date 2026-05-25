# No Legacy / DRY Guardrails

## Canonical owner

- Admin UX/API design contract: `docs/architecture/admin-audit-replay-flows.md`
- Runtime endpoint proof: `app.routes`, `app.openapi()` and `backend/tests/api/admin/**`
- Sensitive-data policy source: existing replay security documents and answer-audit access-log evidence

## Forbidden for this story

- New backend routes, serializers, models, migrations or generated clients
- React admin screens or CSS changes
- Compatibility route paths, aliases, shims or silent fallbacks
- Public, B2C or broad support access to replay/audit flows
- Massive export as part of the minimal future UI
- Raw prompts, raw provider/model payloads, raw AI answers, raw birth data, exact coordinates, secrets or unmasked direct identifiers in UI-visible fields

## Guard evidence

- `evidence/route-absence.txt` proves forbidden replay public/support route families are absent.
- `evidence/sensitive-field-scan.txt` proves forbidden raw terms are documented as excluded and do not appear in a `visible_fields` declaration.
- `evidence/route-inventory.txt` and `evidence/openapi-admin-paths.txt` prove the consumed runtime endpoints are the existing admin endpoints.

## Broad guard note

The initial broad token scan for every path containing `audit` was intentionally replaced with a focused consumed-surface guard because unrelated pre-existing ops routes include `audit` outside this story domain. No runtime change was made to those unrelated routes.
