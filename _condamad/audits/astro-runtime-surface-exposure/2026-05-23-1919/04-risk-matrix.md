# Risk Matrix - Astro Runtime Surface Exposure

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Public API and frontend contracts if raw runtime is exposed | High: violates existing no-raw-runtime guard expectations | Medium | P0 |
| F-002 | Medium | Medium | Public natal projection and interpretation handoff | Medium: could expose unstable fixed-star payload fields | Medium | P1 |
| F-003 | Medium | Low | Admin/debug and public route boundaries | High: unsafe if built without authz | High | P2 blocked |
| F-004 | Low | Medium | Future guardrail vocabulary only | Low: adjacent guards already exist | Low | P3 |
| F-005 | Info | Medium | Product detail granularity | Low: current projections remain stable | Low | P3 decision |

## Risk Notes

- Stability: raw runtime payloads are allowed to evolve with internal graph needs; public projections need separate stable names and reduced fields.
- Security: the main security risk is not secret exposure, but accidental unauthenticated access to admin/debug traces or internal calculation graph details.
- Frontend coupling: direct `chart_objects` consumption would bind UI code to domain implementation rather than product facts.
- Product confusion: internal concepts such as condition profiles, aspect hints and dignity breakdowns need editorial framing before public exposure.
