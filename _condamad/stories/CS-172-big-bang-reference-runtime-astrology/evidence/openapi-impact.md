# OpenAPI Impact

No public API schema change was introduced by this story.

The runtime reference switch is internal to backend infra/services/domain. Existing public
projection names remain owned by API/service serialization, not by `domain/astrology`.

Evidence:

- No frontend files changed.
- No API router or schema file changed.
- Backend startup smoke passed with `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765`.
