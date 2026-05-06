<!-- Audit before du vocabulaire CSS actif. -->

# CS-083 CSS No Legacy Vocabulary Before

Scope: commentaires CSS actifs sous `frontend/src/**/*.css`.

## Hits avant implementation

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `Route legacy : investigation hors catalogue` | CSS comment | dead | none | `Route d'investigation hors catalogue` | delete | `AdminPromptsPage.css:1792` | stale vocabulary could remain unguarded |
| `Dynamic background fallback using theme variables` | CSS comment | dead | none | `Fond dynamique de secours via variables de theme` | delete | `AstroMoodBackground.css` | new guard would fail if retained |

