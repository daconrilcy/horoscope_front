<!-- Evidence apres migration des valeurs premium partagees CS-089. -->

# Hardcoded Values After

## Owners finaux

| Valeurs migrees | Owner canonique | Consommateurs |
|---|---|---|
| Background premium app light/dark | `--premium-app-bg` dans `frontend/src/styles/premium-theme.css` | `backgrounds.css` |
| Atmosphere premium app light/dark | `--premium-app-bg-atmosphere` dans `frontend/src/styles/premium-theme.css` | `backgrounds.css` |
| Image noise premium | `--premium-noise-image` dans `frontend/src/styles/premium-theme.css` | `backgrounds.css`, `DailyHoroscopePage.css` |
| Background et halos daily | `--premium-daily-page-bg`, `--premium-daily-bg-atmosphere`, `--premium-daily-bg-depth` dans `premium-theme.css` | `DailyHoroscopePage.css` |
| Surfaces, borders et effets glass | `--glass-surface-*`, `--glass-border*`, `--glass-base-*`, `--glass-card-*` dans `glass.css` | `DailyHoroscopePage.css`, `DailyAdviceCard.css`, cartes glass partagees |
| Halos et badge DailyAdvice | `--premium-daily-advice-*` dans `premium-theme.css` | `DailyAdviceCard.css` |

## Forbidden migrated literals

Ces valeurs et motifs sont interdits dans les consommateurs actifs migres par CS-089. Ils ne sont autorises que dans leur owner canonique documente ci-dessus.

### `backgrounds.css`

- `radial-gradient(720px 520px at 14% 18%, rgba(255, 255, 255, 0.72), transparent 58%)`
- `radial-gradient(1200px 800px at 20% 10%, rgba(247, 210, 201, 0.18), transparent 50%)`
- `radial-gradient(680px 520px at 76% 22%, rgba(182, 154, 255, 0.2), transparent 62%)`
- `radial-gradient(900px 700px at 80% 60%, rgba(6, 61, 112, 0.1), transparent 100%)`
- `radial-gradient(860px 600px at 52% 78%, rgba(255, 255, 255, 0.34), transparent 60%)`
- `radial-gradient(760px 580px at 88% 88%, rgba(150, 125, 255, 0.16), transparent 62%)`
- `radial-gradient(820px 580px at 18% 16%, rgba(244, 236, 255, 0.12), transparent 58%)`
- `radial-gradient(1200px 800px at 20% 10%, rgba(160, 120, 255, 0.22), transparent 55%)`
- `radial-gradient(760px 560px at 74% 18%, rgba(180, 130, 255, 0.18), transparent 58%)`
- `radial-gradient(900px 700px at 80% 60%, rgba(90, 170, 255, 0.14), transparent 60%)`
- `radial-gradient(900px 640px at 46% 82%, rgba(124, 100, 228, 0.16), transparent 62%)`
- `radial-gradient(680px 500px at 88% 78%, rgba(120, 214, 255, 0.1), transparent 64%)`
- `radial-gradient(46% 34% at 50% 30%, rgba(255, 255, 255, 0.3), transparent 72%)`
- `radial-gradient(38% 28% at 72% 62%, rgba(176, 135, 255, 0.18), transparent 76%)`
- `radial-gradient(34% 28% at 24% 72%, rgba(255, 228, 238, 0.18), transparent 74%)`
- `radial-gradient(120% 92% at 50% 50%, transparent 58%, rgba(122, 104, 176, 0.08) 100%)`
- `radial-gradient(44% 32% at 50% 28%, rgba(214, 198, 255, 0.12), transparent 72%)`
- `radial-gradient(34% 26% at 74% 60%, rgba(140, 102, 255, 0.14), transparent 76%)`
- `radial-gradient(30% 24% at 28% 74%, rgba(90, 170, 255, 0.1), transparent 76%)`
- `radial-gradient(120% 92% at 50% 50%, transparent 56%, rgba(10, 7, 32, 0.18) 100%)`
- Motif interdit: `url("data:image/svg+xml,...")` pour le bruit premium; utiliser `var(--premium-noise-image)`.

### `DailyHoroscopePage.css`

- `linear-gradient(180deg, var(--premium-bg-start) 0%, var(--premium-bg-mid) 48%, var(--premium-bg-end) 100%)`
- `radial-gradient(circle at 78% 18%, rgba(144, 117, 240, 0.24) 0%, transparent 36%)`
- `radial-gradient(circle at 16% 88%, rgba(255, 211, 236, 0.18) 0%, transparent 34%)`
- `radial-gradient(circle at 48% 28%, rgba(255, 255, 255, 0.4) 0%, transparent 40%)`
- `radial-gradient(circle at 84% 68%, rgba(147, 117, 235, 0.15) 0%, transparent 28%)`
- `radial-gradient(circle at 30% 8%, rgba(255, 255, 255, 0.24) 0%, transparent 32%)`
- `radial-gradient(circle at 80% 20%, rgba(156, 121, 255, 0.12) 0%, transparent 50%)`
- `radial-gradient(circle at 20% 80%, rgba(100, 80, 200, 0.1) 0%, transparent 50%)`
- `radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 42%)`
- `radial-gradient(circle at 50% 50%, rgba(30, 25, 45, 0.4) 0%, transparent 70%)`
- `linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.38) 100%)`
- `blur(18px) saturate(140%)`
- Motif interdit: `url("data:image/svg+xml,...")` pour le bruit premium; utiliser `var(--premium-noise-image)`.
- Motif interdit: declaration locale `--glass-*`; utiliser l'owner `styles/glass.css`.

### `DailyAdviceCard.css`

- `radial-gradient(circle, rgba(170, 144, 255, 0.22) 0%, transparent 72%)`
- `linear-gradient(180deg, rgba(156, 121, 255, 0.24) 0%, rgba(255, 255, 255, 0.26) 100%)`
- `radial-gradient(circle, rgba(156, 121, 255, 0.28) 0%, transparent 70%)`
- `blur(18px)`
- Motif interdit: declaration locale `--glass-*` ou `--premium-*`; utiliser `styles/glass.css` et `styles/premium-theme.css`.

### `glass.css`

- `--glass-*` est l'owner canonique des surfaces et effets glass.
- Les consommateurs actifs doivent utiliser `var(--glass-...)`; ils ne doivent pas redefinir de `--glass-*` localement.
- Les valeurs visuelles directes `rgba(...)`, `linear-gradient(...)` et `blur(...)` sont autorisees uniquement dans les declarations owner `--glass-*`.

## Scans apres implementation

Commandes executees depuis la racine:

```powershell
rg -n -- "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
```

Resultat: hits limites aux declarations owner `--glass-card-mini-shadow` et `--glass-card-shortcut-shadow` dans `glass.css`.

```powershell
rg -n -- "font-size:|font-weight:|line-height:|letter-spacing:" frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
```

Resultat: toutes les declarations trouvees utilisent des tokens typographiques.

```powershell
rg -n -- "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
```

Resultat: `linear-gradient` reste uniquement dans l'owner `--glass-card-premium-bg`; radius et shadows actifs consomment des variables.

```powershell
rg -n -- "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
```

Resultat: zero hit.

## Guards anti-retour

- `frontend/src/tests/design-system-guards.test.ts` contient la garde `bloque le retour des literals premium partages migres par CS-089`.
- `_condamad/stories/regression-guardrails.md` contient `RG-063`.
