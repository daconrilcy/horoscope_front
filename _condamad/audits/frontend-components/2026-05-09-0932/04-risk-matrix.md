<!-- Matrice de risques du nouvel audit CONDAMAD frontend components. -->

# Risk Matrix - frontend-components

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Components, pages, layouts, settings, dashboard | Medium: multiple route/page owners must preserve behavior while moving imports | Medium | P1 |
| F-002 | Info | Low | Auth and natal feature owners | Low: old-path scans and tests pass | Low | Low |
| F-003 | Info | Low | Deleted test-only component surfaces | Low: zero active hits and guards pass | Low | Low |
| F-004 | Info | Low | Component guard suite | Low: tests and lint pass | Low | Low |
