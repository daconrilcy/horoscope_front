# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La carte rend l'identite avant les badges. | `AstrologerCard.tsx` rend avatar/nom/style avant `.person-card-topline`. | `npm run test -- AstrologersPage design-system visual-smoke` PASS | PASS |
| AC2 | Le badge principal est le seul badge fort. | Badge featured avant metadata provider/default, badges secondaires declasses en CSS. | `npm run test -- AstrologersPage design-system visual-smoke` PASS | PASS |
| AC3 | Le CTA est une action row visible. | `.person-card-cta` pleine largeur avec surface/bordure token-backed. | `npm run test -- AstrologersPage design-system visual-smoke` PASS | PASS |
| AC4 | La carte reste un bouton unique sans enfant interactif. | CTA reste un `span`, aucun `button`/`a` enfant. | `AstrologersPage` DOM assertions PASS | PASS |
| AC5 | La grille `1440x1000` vise trois colonnes. | `.people-page .person-grid` passe a `minmax(min(100%, 340px), 1fr)`. | `design-system`/`visual-smoke` CSS assertions PASS | PASS |
| AC6 | La grille `390x844` reste une colonne. | Media rule mobile `minmax(0, 1fr)` conservee. | `npm run test -- AstrologersPage design-system visual-smoke` PASS | PASS |
| AC7 | Header avec criteres rapides localises. | `AstrologersPage.tsx` + `i18n/astrologers.ts` ajoutent trois criteres. | `AstrologersPage` assertions PASS | PASS |
| AC8 | Empty state avec prochaine action. | `AstrologerGrid.tsx` + i18n ajoutent titre, description, prochaine action. | `AstrologersPage` empty test PASS | PASS |
| AC9 | Effets decoratifs compatibles reduced motion. | `media.css` neutralise orbit animation/transitions sous reduced motion. | `design-system`/`visual-smoke` assertions PASS | PASS |
| AC10 | Destinations interdites zero-hit. | Aucun `App.css`, `.astrologer-*`, inline style, featured fragile. | Scans cibles PASS; scan large heights a deux hits hors catalogue classes non applicables | PASS |
| AC11 | Guardrails applicables satisfaits. | Tests/guards mis a jour pour RG-079/RG-089/RG-090. | Targeted tests + full tests + lint PASS | PASS |
| AC12 | Artefacts before/after existent. | `astrologers-premium-before.md` et `astrologers-premium-after.md`. | `rg -n "390x844|npm run test|rg -n" ...` planned evidence in artifacts | PASS |
