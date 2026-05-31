Browser QA:
- In-app browser unavailable in this session: `iab` was not exposed by the browser connector.
- Playwright terminal QA ran against `http://127.0.0.1:5173/natal` with `daconrilcy@hotmail.com`.
- Authenticated `/natal` loaded successfully.
- Live account state exposed compact actions (`.ni-actions--compact`) and astrologer mode collapsed by default.
- Live account state did not expose a current `narrative_natal_reading_v1` accordion surface, so accordion toggles were not browser-verified on this dataset.
- Compensating executable evidence: Vitest/Testing Library renders the target React surfaces and verifies accordion, source collapse, public DOM guard, compact actions, and page states.
