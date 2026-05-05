# CSS fallbacks before CS-056

Scan command: `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` from `frontend`.

Initial allowlist count: 24 entries.
Priority lot entries: 14 entries across `PeriodCard.css`, `NatalInterpretation.css`, `KeyPointCard.css`, `NatalChartPage.css`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `PeriodCard.css` `--color-text-muted` fallbacks | css-fallback | dead | period text labels | `--color-text-muted` from `design-tokens.css` | delete | token defined in `design-tokens.css` light/dark | low |
| `PeriodCard.css` `--color-error` fallback | css-fallback | dead | negative tone dot | `--color-error` from `design-tokens.css` | delete | token defined in `design-tokens.css` light/dark | low |
| `PeriodCard.css` `--color-text-secondary` fallback | css-fallback | dead | selected tone label | `--color-text-secondary` from `design-tokens.css` | delete | token defined in `design-tokens.css` light/dark | low |
| `KeyPointCard.css` `--shadow-hero-card` fallback | css-fallback | dead | key card surface | `--shadow-hero-card` from `design-tokens.css` | delete | token defined in `design-tokens.css` light/dark | low |
| `KeyPointCard.css` `--color-hero-ink` fallback | css-fallback | dead | key card label | `--color-hero-ink` from `design-tokens.css` | delete | token defined in `design-tokens.css` light/dark | low |
| `KeyPointCard.css` `--color-hero-ink-accent` fallback | css-fallback | dead | key card gauge | `--color-hero-ink-accent` from `design-tokens.css` | delete | token defined in `design-tokens.css` light/dark | low |
| `NatalInterpretation.css` `--premium-radius-pill` fallbacks | css-fallback | dead | selector/action controls | `--premium-radius-pill` from `premium-theme.css` | delete | token defined in `premium-theme.css` | low |
| `NatalInterpretation.css` `--space-3`, `--space-4`, `--font-size-sm` fallbacks | css-fallback | dead | locked accordion and teaser | canonical spacing/type tokens | delete | tokens defined in `design-tokens.css` | low |
| `NatalInterpretation.css` `--premium-glass-border-soft` fallback | css-fallback | needs-user-decision | section border | none guaranteed | keep | token absent from `premium-theme.css` | deletion could remove fallback for absent token |
| `NatalChartPage.css` premium fallbacks | css-fallback | needs-user-decision | natal page premium surfaces | none guaranteed | keep | story marks premium ambiguity blocked | deletion needs product/theme decision |
