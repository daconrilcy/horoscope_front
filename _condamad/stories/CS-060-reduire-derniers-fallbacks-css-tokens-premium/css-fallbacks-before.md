# CS-060 - CSS fallbacks before

Baseline capture avant migration.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `App.css --usage-progress, 0` | CSS fallback | canonical-active | runtime progress width | custom property runtime | keep | `rg var(--usage-progress, 0)` | requis pour valeur runtime |
| `Settings.css --usage-progress, 0` | CSS fallback | canonical-active | runtime progress width | custom property runtime | keep | `rg var(--usage-progress, 0)` | requis pour valeur runtime |
| `AdminEntitlementsPage.css --glass-heavy, #1a1a1a` | CSS fallback | external-active | admin entitlement surface | none in current lot | keep | allowlist existante | migration hors scope |
| `NatalInterpretation.css --premium-glass-border-soft` | CSS fallback | dead | premium CSS | `premium-theme.css` | delete | token ajoutable au theme premium | faible |
| `SignUpForm.css --danger` | CSS fallback | dead | form CSS | `--danger` deja defini | delete | `index.css` | faible |
| `ChatWindow.css --premium-radius-pill` | CSS fallback | dead | chat CSS | `--premium-radius-pill` deja defini | delete | `premium-theme.css` | faible |
| `TestimonialsSection.css --success` | CSS fallback | dead | landing CSS | `--success` deja defini | delete | `theme.css` / `index.css` | faible |
| `NatalChartPage.css --premium-text-muted` | CSS fallback | needs-user-decision -> resolved | premium chart CSS | `--premium-text-muted` | delete | token ajoute dans `premium-theme.css` | faible |
| `NatalChartPage.css --premium-glass-border-soft` x2 | CSS fallback | needs-user-decision -> resolved | premium chart CSS | `--premium-glass-border-soft` | delete | token ajoute dans `premium-theme.css` | convergence visible bordure 0.3 vers soft |

Count before: 10 fallbacks.
