# Mapping familles visuelles App apres CS-123

| Famille | Surface canonique | Preuve |
|---|---|---|
| Cards / panels | `.app-card`, `.app-panel` | `frontend/src/App.css` |
| Lists / items | `.app-list`, `.app-list--compact` | `frontend/src/App.css` |
| Badges / pills | `.app-badge`, `.app-pill` | `frontend/src/App.css` |
| Avatars / media | `.app-avatar` | `frontend/src/App.css` |
| Modal / overlay | `.app-modal`, `.app-overlay` | `frontend/src/App.css` et review composer |

Scans apres implementation:

- `rg -n "alias|compat|shim|migration-only" src/App.css` depuis `frontend`: zero hit.
- `npm run test -- AstrologersPage ConsultationsPage SettingsPage DashboardPage visual-smoke`: couvert par validations ciblees et suite complete.

