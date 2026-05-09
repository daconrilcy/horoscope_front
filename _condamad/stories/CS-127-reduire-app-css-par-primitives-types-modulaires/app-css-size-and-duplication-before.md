# App CSS baseline before CS-127

Mesure capturee avant extraction modulaire.

| Metric | Value | Evidence |
|---|---:|---|
| `frontend/src/App.css` lines | 4094 | `(Get-Content frontend/src/App.css).Count` / raw split count |
| Flat selector blocks | 512 | Node CSS block inventory |
| Unique declaration bodies | 472 | Node CSS block inventory |
| Duplicate declaration bodies | 27 | Node CSS block inventory |
| Selectors participating in duplicate bodies | 67 | Node CSS block inventory |
| `--app-*` custom property declarations | 415 | regex inventory |

Known duplicates called out by story:

- `.skeleton-line` appears as an active selector in `frontend/src/App.css`.
- `.people-page-header h1` and `.people-page-header p` appear in base and responsive/header sections.
- Mechanical variables include page/component-specific names such as `--app-chat-error-border-radius`, `--app-message-bubble-border-radius`, and `--app-person-panel-info-p-font-size`.

Top duplicate declaration bodies before migration:

| Selector count | Body summary |
|---:|---|
| 6 | `width: 100%;` |
| 4 | `grid-template-columns: 1fr;` |
| 4 | `margin-bottom: 2rem;` |
| 3 | `display: flex; flex-direction: column; gap: 0.25rem;` |
| 3 | `display: none;` |
| 3 | `flex: 1;` |
| 3 | `outline: none; border-color: var(--color-primary);` |
| 3 | `grid-template-columns: 1fr 1fr;` |
