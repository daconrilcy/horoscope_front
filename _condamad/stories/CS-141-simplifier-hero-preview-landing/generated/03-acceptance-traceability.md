# Traceability CS-141

| AC | Statut | Preuve code | Preuve validation |
|---|---|---|---|
| AC1 | PASS | `HeroSection.tsx` ne contient plus de timer. | Scan timers zero-hit; test visual-smoke. |
| AC2 | PASS | Preview statique + animation CSS-only. | Captures Playwright top light/dark. |
| AC3 | PASS | Handlers CTA conserves. | `LandingPage.test.tsx` clique les CTA et assert `track`. |
| AC4 | PASS | CSS sous `prefers-reduced-motion: no-preference`; reduce global conserve. | `visual-smoke` PASS. |
| AC5 | PASS | Pas de nouvelle dependance, canvas, WebGL ou style inline. | `npm run lint` PASS; scans PASS. |
