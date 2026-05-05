<!-- Baseline du drift visual-smoke avant CS-047. -->

# CS-047 Visual Smoke Before

Ancien contrat observe dans `frontend/src/tests/visual-smoke.test.tsx`:

| Item | Classification | Decision |
|---|---|---|
| `.section-header__title` attendait `font-size: 18px` | assertion obsolete | remplacer par `var(--font-size-lg)` |
| `.bottom-nav__label` attendait `font-size: 12px` | assertion obsolete | remplacer par `var(--font-size-xs)` |
| `.bottom-nav__label` attendait `font-weight: 500` | assertion obsolete | remplacer par `var(--font-weight-medium)` |
| Assertions `opacity` | contrat actif | conserver |

