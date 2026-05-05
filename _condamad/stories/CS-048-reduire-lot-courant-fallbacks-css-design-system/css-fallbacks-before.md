<!-- Inventaire before des fallbacks CSS du lot CS-048. -->

# CS-048 CSS Fallbacks Before

Lot choisi: `App.css`, `AdminPromptsPage.css`, `Settings.css`, `BirthProfilePage.css`.

| Item | Type | Classification | Decision |
|---|---|---|---|
| `App.css --usage-progress, 0` | fallback runtime | dynamic | keep |
| `Settings.css --usage-progress, 0` | fallback runtime | dynamic | keep |
| `AdminPromptsPage.css --color-accent, var(--color-primary)` | alias absent avec canonique clair | dead | delete |
| `BirthProfilePage.css --border-color, #eee` | fallback local | dead | replace by `--color-line` |
| `BirthProfilePage.css --text-secondary, #666` | fallback local | dead | replace by `--color-text-secondary` |
| `BirthProfilePage.css --bg-secondary, #f9f9f9` | fallback local | dead | replace by `--color-bg-2` |
| `BirthProfilePage.css --bg-button-secondary, #eee` | fallback local | dead | replace by `--color-glass-bg-2` |
| `BirthProfilePage.css --text-button-secondary, #333` | fallback local | dead | replace by `--color-text-primary` |
| `BirthProfilePage.css --border-color, #ccc` | fallback local | dead | replace by `--color-line` |
| `BirthProfilePage.css --bg-button-secondary-hover, #ddd` | fallback local | dead | replace by `--color-glass-bg` |

