# Acceptance Traceability - CS-052

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le baseline couvre 100% des fallbacks du lot choisi. | `css-fallbacks-before.md` inventorie le lot `NatalChartPage.css`. | `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src/pages/NatalChartPage.css` before/after. | PASS |
| AC2 | Chaque fallback supprime a une preuve de token canonique garanti. | `NatalChartPage.css` consomme directement les tokens declares dans `premium-theme.css`. | `npm run test -- css-fallback design-system theme-tokens` + audit after. | PASS |
| AC3 | La synchronisation des registres fallback passe le guard. | `css-fallback-allowlist.md` et `design-system-allowlist.ts` ne gardent que 3 exceptions NatalChart. | `npm run test -- css-fallback design-system theme-tokens`. | PASS |
| AC4 | Les fallbacks premium ambigus sont bloques ou justifies. | `--premium-text-muted` et `--premium-glass-border-soft` restent classes `needs-user-decision`. | `rg -n "needs-user-decision\|premium" css-fallbacks-*.md`. | PASS_WITH_LIMITATIONS |
| AC5 | Aucun nouveau fallback non classe n'est introduit. | Aucun nouveau fallback ajoute; le scan final montre seulement des exceptions allowlistees. | Scan final CSS fallback global. | PASS |
| AC6 | Le frontend reste valide sur le scope touche. | Aucun changement runtime hors CSS/allowlists. | Tests ciblés + `npm run lint`. | PASS |
