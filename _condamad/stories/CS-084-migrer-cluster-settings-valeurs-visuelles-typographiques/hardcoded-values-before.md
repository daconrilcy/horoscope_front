# Hardcoded Values Before

## Scope

- File: `frontend/src/pages/settings/Settings.css`
- Captured during preflight for story `CS-084`.

## Commands

| Purpose | Command | Result |
|---|---|---|
| Visual literals | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" frontend/src/pages/settings/Settings.css` | Hits found across Settings palette, backgrounds, borders, shadows and statuses. |
| Typography literals | `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" frontend/src/pages/settings/Settings.css` | Hits found across headings, badges, cards, stat labels and feedback text. |
| Shape/elevation/fallback literals | `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/pages/settings/Settings.css` | Hits found for radius, shadows and one runtime fallback `--usage-progress`. |
| No Legacy vocabulary | `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" frontend/src/pages/settings/Settings.css` | Zero active hits. |

## Initial Classification

| Surface | Examples observed | Initial decision route |
|---|---|---|
| Settings semantic palette | `--settings-purple`, `--settings-gold`, `--settings-card-*`, `--settings-text-*` | keep as page-scoped semantic owner or map to global token when equivalent already exists |
| Background atmospheres | radial/linear gradients and rgba literals | migrate behind documented `--settings-*` semantic variables |
| Borders and shadows | rgba borders, `box-shadow` declarations | use global shape/shadow tokens or `--settings-*` semantic variables |
| Typography | clamp sizes, px/rem sizes, weights, line heights, letter spacing | use `--type-*`, `--font-*`, `--line-height-*`, or documented `--settings-*` typography roles |
| Runtime progress | `width: calc(var(--usage-progress, 0) * 1%)` | keep as exact runtime custom property already allowlisted |
| Spacing and layout | repeated paddings, margins, gaps, offsets, fixed dimensions and mobile values | route to global `--space-*` when equivalent, otherwise centralize as page-scoped `--settings-*` semantic variables |

## Baseline Literal Families

The complete baseline was captured by the `rg` commands above before editing.
For reviewer audit, the affected repeated families were:

| Family | Representative baseline literals | Final route expected |
|---|---|---|
| Page layout | `860px`, `24px 24px 96px`, `16px 16px 80px` | `--settings-page-*` |
| Card layout | `28px 32px`, `22px 26px`, `20px` stack offsets | `--settings-card-*`, `--space-*` |
| Section headings | `18px`, `24px`, `14px`, `46px`, `3px` | `--settings-section-*` |
| Overview and plans | `22px`, `28px`, `8px`, `10px`, `16px`, `18px`, `160px`, negative glow offsets | `--settings-overview-*`, `--settings-plan-*`, `--settings-inline-*` |
| Badges and controls | `42px`, `38px`, `3px 10px`, `5px 12px`, `8px 16px` | `--settings-tab-*`, `--settings-badge-*`, `--settings-profile-badge-*` |
| Usage/progress | `140px`, `180px`, `56px`, `8px`, `12px`, `1px`, `-1px` | `--settings-usage-*`, `--settings-progress-*`, `--settings-sr-only-*` |

## Baseline Outcome

- The cluster starts with many direct visual and typographic declarations in `Settings.css`.
- Repeated spacing declarations are part of the migrated cluster and require final owner decisions in the after artifact.
- The only pre-existing CSS variable fallback in scope is `--usage-progress`, already listed in `frontend/src/styles/css-fallback-allowlist.md`.
- The final after artifact must classify each remaining literal without TODO, limitation, legacy or compatibility wording.
