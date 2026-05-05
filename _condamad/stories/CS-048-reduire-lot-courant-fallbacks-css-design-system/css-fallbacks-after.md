<!-- Inventaire after des fallbacks CSS du lot CS-048. -->

# CS-048 CSS Fallbacks After

Lot choisi: `App.css`, `AdminPromptsPage.css`, `Settings.css`, `BirthProfilePage.css`.

| Item | Type | Classification | Decision | Proof |
|---|---|---|---|---|
| `App.css --usage-progress, 0` | fallback runtime | dynamic | keep | progression runtime |
| `Settings.css --usage-progress, 0` | fallback runtime | dynamic | keep | progression runtime |
| `AdminPromptsPage.css --color-accent` | alias absent | dead | deleted | scan final zero-hit |
| `BirthProfilePage.css` fallbacks locaux | tokens canoniques existants | dead | deleted | scan final zero-hit |

Scan final du lot: seuls `--usage-progress` restent. Registres `css-fallback-allowlist.md` et `design-system-allowlist.ts` synchronises.

