# Acceptance Traceability - CS-055

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Chaque famille legacy/compatibility ciblee est classifiee. | `legacy-surfaces-before.md` and `legacy-surfaces-after.md`. | No unclassified/TBD markers. | PASS |
| AC2 | Chaque surface `remove-now` est supprimee sans shim. | `AdminPromptsPage.css` migrated off local `--glass*`, `--success`, `--danger`, `--warning` aliases. | Alias scan zero hit for local token usages. | PASS |
| AC3 | Chaque consumer migre utilise l'owner canonique. | CSS now uses `--color-glass-*`, `--color-success`, `--color-danger`, `--color-admin-warning-*`. | Targeted scans and guards. | PASS |
| AC4 | La synchronisation des registres legacy passe le guard. | `legacy-style-surface-registry.md` persists admin blocker as `external-active`. | `npm run test -- legacy-style theme-tokens design-system`. | PASS |
| AC5 | Les surfaces ambigues bloquent la suppression. | Active `.admin-prompts-legacy*` selectors remain classified because TSX consumes them. | `legacy-surfaces-after.md` and registry rows. | PASS_WITH_LIMITATIONS |
| AC6 | Aucun nouvel alias compatibility ou selector legacy n'est introduit. | No new alias or selector added. | Final `legacy|--text-|--glass|--primary` scan classified. | PASS |
