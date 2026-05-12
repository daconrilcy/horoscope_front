# Story CS-149 optimiser-hierarchie-premium-catalogue-astrologers: Optimiser la hierarchie premium du catalogue /astrologers

Status: ready-to-review

## 1. Objective

Mettre a jour la page `/astrologers` pour transformer le catalogue actuel en surface de choix plus premium et plus comparable: cartes centrees sur l'identite, CTA pleine largeur, grille desktop moins dense, signaux hierarchises, decoration reduite et etat vide utile.

## 2. Domain Boundary

- Domain: `frontend-astrologers-catalog`
- In scope:
  - `AstrologerCard.tsx`: avatar, nom et style avant les badges.
  - `AstrologerGrid.tsx`: empty state plus utile.
  - `AstrologersPage.tsx`: header avec criteres rapides localises.
  - `i18n/astrologers.ts`: libelles visibles du catalogue.
  - `styles/app/cards.css`, `media.css`, `tokens.css`: grille, CTA, badges, effets subtils.
  - Tests `AstrologersPage`, `visual-smoke`, `design-system`.
- Out of scope:
  - backend, API, route `/astrologers/:id`, route globale, `RootLayout`, `PageLayout`, `App.css`, nouvelles dependances.

## 3. Regression Guardrails

- Applicable: `RG-079`, `RG-081`, `RG-083`, `RG-084`, `RG-087`, `RG-089`, `RG-090`.
- Evidence required:
  - `npm run test -- AstrologersPage design-system visual-smoke`
  - `npm run lint`
  - scans zero-hit sur `App.css`, `.astrologer-*`, `style=`, `featured={index === 0}`, `.person-card--featured`, hauteurs fixes fragiles.
  - artefacts before/after dans ce dossier.

## 4. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La carte rend l'identite avant les badges. | Test DOM `AstrologersPage` et smoke DOM. |
| AC2 | Le badge principal est le seul badge fort. | Tests `AstrologersPage` / `visual-smoke` et CSS guard. |
| AC3 | Le CTA est une action row visible. | Test DOM + CSS guard `.person-card-cta`. |
| AC4 | La carte reste un bouton unique sans enfant interactif. | Test DOM anti enfant interactif. |
| AC5 | La grille `1440x1000` vise trois colonnes. | CSS guard sur `minmax(min(100%, 340px), 1fr)` + evidence after. |
| AC6 | La grille `390x844` reste une colonne. | CSS guard mobile + evidence after. |
| AC7 | Le header expose des criteres rapides de choix localises. | Test `AstrologersPage`. |
| AC8 | L'etat vide affiche une prochaine action. | Test `AstrologersPage` liste vide. |
| AC9 | Les effets decoratifs respectent `prefers-reduced-motion`. | CSS/design-system guard. |
| AC10 | Les destinations interdites restent zero-hit. | Scans `rg` du plan de validation. |
| AC11 | Les guardrails applicables restent satisfaits. | Tests cibles + lint. |
| AC12 | Les artefacts before/after existent. | Fichiers markdown de preuve. |

## 5. Files to Inspect First

- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 6. Validation Plan

```powershell
cd frontend
npm run lint
npm run test -- AstrologersPage design-system visual-smoke
rg -n "people-page|person-card" src/App.css
rg -n "astrologer-" src/styles/app src/features/astrologers
rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers
rg -n "featured=\{index === 0\}|person-card--featured|height:\s*24[0-9]px|height:\s*25[0-9]px" src/features/astrologers src/styles/app src/tests
```

Runtime/manual evidence: start the frontend and check `390x844`, `768x1024`, `1440x1000`, card click, dark mode, and reduced motion.
