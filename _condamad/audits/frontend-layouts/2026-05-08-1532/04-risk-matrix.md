<!-- Matrice de risques de l'audit CONDAMAD de suivi frontend-layouts. -->

# Risk Matrix - frontend-layouts follow-up

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-101 | Medium | Medium | Medium | Medium | Medium | P2 |

## Closed Risk Notes

- Previous High risk `RootLayout` unmounted: closed by route tree and guard.
- Previous High risk landing bypass: closed by route tree, symbol scan, and guard.
- Previous High risk direct auth routes: closed by route tree and guard.
- Previous Medium risk missing layout guard: closed by `page-architecture-guards.test.ts`.
- Previous High risk unclassified page files: converted to exact classification with decision blockers.
- Stale CS-103 to CS-107 story status risk: closed by setting each story to `Status: done`.
