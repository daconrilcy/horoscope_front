# Validation evidence - CS-150

<!-- Preuves de cloture pour la correction UX/UI du catalogue astrologues. -->

## Audit before

- Source: `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json`
- Finding 1: `768x1024` rendait `columnsFirstRow: 1` avec des cartes de `686px`.
- Finding 2: le header restait volontairement concis; la correction conserve le sous-titre sans liste redondante.

## Implementation summary

- `cards.css` rend une colonne mobile, deux colonnes tablette et trois colonnes desktop.
- Les tests `AstrologersPage`, `design-system-guards` et `visual-smoke` gardent le contrat.

## Audit after

- Source: `.codex-artifacts/astrologers-audit-2026-05-12/after-metrics.json`
- `390x844`: `columnsFirstRow: 1`, `horizontalOverflow: false`.
- `768x1024`: `columnsFirstRow: 2`, `horizontalOverflow: false`.
- `1440x1000`: `columnsFirstRow: 3`, `horizontalOverflow: false`.
- Nested interactive controls in cards: `activeElementRoleCount: 0`.

## Commands

| Command | Result | Notes |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-150-clarifier-comparaison-tablette-catalogue-astrologers/00-story.md` | PASS | Story contract valid before implementation. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-150-clarifier-comparaison-tablette-catalogue-astrologers/00-story.md` | PASS | Strict story lint valid before implementation. |
| `npm run test -- AstrologersPage design-system visual-smoke` | PASS | 3 files, 87 tests. |
| Playwright inline measurement script from `frontend/` | PASS | Wrote after metrics and screenshots. |
| `npm run lint` | PASS | TypeScript lint configs pass. |
| `npm run test` | PASS | 115 files, 1245 passed, 8 skipped. |

## Guard scans

| Scan | Result | Notes |
|---|---|---|
| `rg -n "people-page\|person-card" src/App.css` | PASS | Zero hits. |
| `rg -n "astrologer-" src/styles/app src/features/astrologers` | PASS | Zero hits. |
| `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers` | PASS | Zero hits. |
| `rg -n "(^|[^-])height:\s*24[0-9]px\|(^|[^-])height:\s*25[0-9]px\|featured=\{index === 0\}\|person-card--featured" src/features/astrologers src/styles/app src/tests` | PASS | Zero hits. |
| `rg -n "\bany\b\|style=\{\|fetch\(\|axios\." frontend/src/pages/AstrologersPage.tsx frontend/src/features/astrologers frontend/src/i18n/astrologers.ts` | PASS | Zero hits. |

## Review result

- UX/UI: no residual issue on `/astrologers` for the audited scope.
- React: route-only rendering change, no duplicated data flow or nested action.
- Styling: token-backed CSS owners preserved, no inline style, no `App.css` drift.
- Regression guardrails: `RG-079`, `RG-089`, `RG-090` preserved.
