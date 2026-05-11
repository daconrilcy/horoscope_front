# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Desktop sans carte pleine largeur vide. | `AstrologerGrid.tsx` ne passe plus `featured`; `cards.css` supprime le span catalogue. | Playwright `1440x1000`: 4 colonnes, `hasFeaturedClass=false`; `npm run test -- AstrologersPage design-system visual-smoke`. | PASS |
| AC2 | Mobile `390x844` en une colonne. | `.people-page .person-grid` utilise auto-fit et un override mobile scope. | Playwright `390x844`: `columnsInFirstRow=1`. | PASS |
| AC3 | Mobile sans scroll horizontal. | Grille `minmax(min(100%, 280px), 1fr)` + override `minmax(0, 1fr)`. | Playwright `390x844`: `horizontalOverflow=false`, `scrollWidth=390`. | PASS |
| AC4 | CTA visuel localise par carte. | `AstrologerCard.tsx` rend `.person-card-cta`; `astrologers.ts` ajoute `view_profile_cta`. | `AstrologersPage.test.tsx` + Playwright `ctaCount=6`. | PASS |
| AC5 | Signaux de choix visibles. | Badges provider/default/editorial rendus et visibles dans `cards.css`. | Tests DOM + Playwright `providerBadgeCount=6`, `defaultBadgeCount=1`. | PASS |
| AC6 | Pas de hauteur fixe 244/256 sur cartes catalogue. | `cards.css` remplace `height` fixe par `min-height` robuste et clamps. | Scan scope CS-148 zero-hit. | PASS |
| AC7 | Clic carte vers `/astrologers/:id`. | Navigation existante conservee dans `AstrologersPage.tsx`. | Test navigation + Playwright URL `/astrologers/c0a80101-...`. | PASS |
| AC8 | Typo `mix-alend-mode` absente. | `media.css` utilise `mix-blend-mode`. | Scan scope CS-148 zero-hit + design guard. | PASS |
| AC9 | Destinations interdites zero-hit. | Aucun changement `App.css`, aucun inline style, aucun `.astrologer-*`. | Scans `App.css`, `.astrologer-*`, `style=`: PASS. | PASS |
| AC10 | Guardrails applicables satisfaits. | Tests et RG-089 ajoutes. | `npm run test -- AstrologersPage design-system visual-smoke` PASS. | PASS |
| AC11 | Bottom nav ne masque pas le CTA final. | Cartes sans hauteur fixe, CTA en bas de flux carte. | Playwright mobile: `lastCtaVisibleAboveBottomNav=true`. | PASS |
| AC12 | Carte sans enfant interactif. | CTA rendu comme `span`; pas de bouton imbrique. | Test DOM + Playwright `nestedInteractiveCount=0`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
