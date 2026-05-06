<!-- Matrice de risques pour l'audit frontend design-system apres refactors. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Frontend guard suite | Guard suite is green and should be preserved. | Low | Monitor |
| F-002 | Info | Low | CSS aliases, consultation labels, fallback and inline-style allowlists | Prior debts are closed or exact; regression risk is controlled by tests. | Low | Monitor |
| F-003 | Medium | High | 101 frontend files | Hardcoded visual decisions can continue to drift away from the token source of truth. | High | P2 |
| F-004 | Medium | Medium | Help and Settings CSS | Cross-page variable reuse can break Help when Settings tokens are changed locally. | Low | P1 |
| F-005 | Medium | Medium | Token registry, Settings, Profile, Astrologer card CSS | Migration-only namespaces and stale registry rows can normalize permanent compatibility debt. | Medium | P1 |
| F-006 | Medium | Medium | Consultation and prediction frontend runtime compatibility | Compatibility code can keep legacy semantics active without owner or exit condition. | Medium | P2 |
| F-007 | Medium | Medium | Admin frontend routing | Historical redirects can become permanent API-like contracts without explicit decision. | Low | P2 |
| F-008 | Low | Medium | Production bundle | Bundle growth remains visible but outside design-system correctness. | Medium | P3 |

## Top Risks

1. `F-004` is the most concrete next fix: `HelpPage.css` currently depends on `--settings-*` variables outside their owner.
2. `F-005` should follow or be combined with `F-004`, because the stale/migration-only namespace registry drives the same ownership ambiguity.
3. `F-003` remains broad and should be split into small clusters to avoid a noisy refactor.
