<!-- Journal de preuves pour l'audit de standardisation de frontend/src/App.css. -->

# Evidence Log - frontend-app-css-standardization

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | source-read | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md` | PASS | workflow read-only et contrats d'audit consultes. |
| E-002 | source-read | `Get-Content .agents/skills/condamad-story-writer/SKILL.md` | PASS | workflow de generation de stories et registre de statuts consultes. |
| E-003 | registry-read | `Get-Content _condamad/stories/regression-guardrails.md` | PASS | invariants frontend `RG-044` a `RG-063` et `RG-059`/`RG-061` applicables. |
| E-004 | prior-audit-read | `Get-Content _condamad/audits/frontend-design-system/2026-05-08-0054/{02-finding-register.md,03-story-candidates.md,05-executive-summary.md}` | PASS | audit precedent ferme la tokenisation mais ne couvre pas l'objectif de classes generiques reutilisables. |
| E-005 | prior-story-read | `Get-Content _condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md` | PASS | story cadree sur valeurs visuelles/typographiques et variables `--app-*`, pas sur la suppression des classes page-specific. |
| E-006 | static-analysis | `@'...analyse css...'@ \| node -` | FAIL | `App.css` contient 4146 lignes, 442 variables `--app-*`, 439 variables `--app-*` utilisees une seule fois, 482 classes uniques, 243 classes contenant un mot de domaine/page. Limitation: analyse lexicale. |
| E-007 | static-analysis | `@'...analyse css...'@ \| node -` | FAIL | principaux prefixes de variables specifiques: `astrologer-card` 66, `astrologer-profile` 21, `consultation-card` 17, `dashboard-summary` 17, `precision-badge` 14, `astrologers-page` 13. |
| E-008 | static-analysis | `@'...analyse css...'@ \| node -` | FAIL | declarations structurelles repetees: `display:flex` 105, `flex-direction:column` 59, `align-items:center` 59, `gap:1rem` 22, `text-align:center` 19. |
| E-009 | static-scan | `rg -n "^\\s*\\.[A-Za-z0-9_-]+" frontend/src/App.css` | FAIL | inventaire reproduit des blocs page/composant tels que `.astrologer-card`, `.consultation-card-premium`, `.wizard-progress`, `.settings-tab`, `.dashboard-summary-card-wrapper`. |
| E-010 | static-scan | `rg -n "OLD\|legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only" frontend/src/App.css` | FAIL | commentaire actif `/* Consultations Page OLD */` ligne 2231 et classes `*-fallback` nominales a classifier. |
| E-011 | guard-read | `Get-Content frontend/src/tests/design-system-guards.test.ts` | PASS | garde `CS-087` bloque les literals non routes et noms mecaniques repetes mais autorise encore des variables specifiques a une page ou un service. |
| E-012 | test | `Push-Location frontend; npm run test -- design-system theme-tokens css-fallback legacy-style --run; Pop-Location` | PASS | 4 fichiers de tests, 125 tests passes; ne valide pas encore la reutilisation de classes generiques. |
| E-013 | lint | `Push-Location frontend; npm run lint; Pop-Location` | PASS | `tsc --noEmit` lint OK. |
| E-014 | git | `git status --short` | PASS | aucune modification utilisateur detectee avant creation des artefacts d'audit/story. |
