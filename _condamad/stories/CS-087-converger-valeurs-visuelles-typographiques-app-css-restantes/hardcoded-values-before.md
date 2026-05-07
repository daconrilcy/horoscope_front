<!-- Baseline avant migration CS-087 de App.css. -->

# CS-087 Hardcoded Values Before

Scope: `frontend/src/App.css` uniquement.

## Scan summary

| Scan | Count before | Decision required |
|---|---:|---|
| `#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(` | 275 | couleurs et gradients a router vers tokens, `--app-*`, `--astro-*`, ou decision finale |
| `font-size:\|font-weight:\|line-height:\|letter-spacing:` | 234 | typographie a router vers tokens `--font-*`, roles `--type-*`, ou `--app-*` typographiques |
| `box-shadow:\|border-radius:\|linear-gradient\|radial-gradient\|var\(\s*--[a-zA-Z0-9_-]+\s*,` | 185 | radius, elevations, gradients et fallbacks a classer |
| `legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only\|TODO\|PASS with limitation` | 6 | hits existants a classifier, aucun elargissement autorise |

## Initial classification

| Surface | Initial state | Target decision |
|---|---|---|
| `#root` `--app-*` declarations | owner App deja documente | `registered-semantic-owner` |
| `--astro-*` declarations | owner App deja documente pour cartes astrologues | `registered-semantic-owner` |
| declarations visuelles hors custom properties | literals actifs dans `App.css` | `migrated` vers `--app-*` ou tokens globaux |
| declarations typographiques hors tokens | literals actifs dans `App.css` | `migrated` vers `--app-*`, `--font-*`, `--line-height-*`, `--letter-spacing-*` |
| animations/keyframes | valeurs de mouvement runtime | `runtime-animation-value` si hors scans visuels/type |
| vocabulaire `fallback` | selecteurs/image fallback existants | `kept-one-off-final` comme etat UI de remplacement d'image, pas mecanisme de compatibilite CSS |

## Guardrails applicables

`RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-052`, `RG-053`, `RG-057`, `RG-059`, `RG-060`.
