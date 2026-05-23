# Risk Matrix - Astro Reference Governance

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Advanced conditions, accidental dignity scoring, interpretation payloads | High: seed-only or code-only edits can diverge solar proximity behavior | Medium | P1 |
| F-002 | High | High | Motion payloads, station classification, dignity matching, dominance/interpretation signals | High: unversioned Python profiles can drift from DB reference semantics | Medium | P1 |
| F-003 | Medium | Medium | Sign, house and dominance rankings | Medium: product tuning can duplicate scoring in the wrong layer | Medium | P2 |
| F-004 | Medium | Medium | Interpretation input, advanced condition profiles, DB translations/profiles | Medium: DB and Python catalogs can diverge without ownership tests | Medium | P2 |
| F-005 | Medium | Medium | Reviewability and doctrine traceability for all rule families | Medium: unclear whether changes are doctrine, product tuning or bug fixes | Low | P2 |
| F-006 | High | High | All future astrology threshold, weight and profile changes | High: unclassified sources can be reintroduced silently | Low | P1 |

## Top Risks

- The most urgent closure path is F-001 plus F-002 because active runtime behavior is already split across DB and Python sources.
- F-006 should be handled early enough to prevent new unclassified thresholds while CS-249 and CS-250 are being implemented.
- F-003 to F-005 are governance risks; they should not trigger runtime refactors until source ownership and doctrine decisions are explicit.
