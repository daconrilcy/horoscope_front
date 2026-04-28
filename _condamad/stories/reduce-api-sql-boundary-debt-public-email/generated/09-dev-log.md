# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Source story: `_condamad/stories/reduce-api-sql-boundary-debt-public-email/00-story.md`
- Initial dirty files: `?? _condamad/stories/reduce-api-sql-boundary-debt-public-email/`
- `AGENTS.md` read: yes
- Regression guardrails read: yes
- Applicable guardrails: `RG-006`, `RG-008`

## Search evidence

- `public/email.py` contains direct SQL/session debt before implementation.
- `router-sql-allowlist.md` contains seven rows for `app/api/v1/routers/public/email.py`.
- `EmailService` is the existing canonical service owner for unsubscribe token generation and email decisions.

## Decisions

- Persist unsubscribe state in `EmailService` to avoid a new email namespace.
- Remove all seven allowlist rows for `public/email.py` after the route stops importing/calling SQL/session.

## Validation summary

- `ruff format .` PASS.
- `ruff check .` PASS.
- Targeted architecture guards PASS, 3 tests.
- `pytest -q tests/integration/test_email_unsubscribe.py` PASS, 7 tests.
- `pytest -q app/tests/unit/test_api_router_architecture.py` PASS, 53 tests.
- Full `pytest -q` timed out after 10 minutes without exploitable output.
