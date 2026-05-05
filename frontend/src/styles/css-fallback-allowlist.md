<!-- Registre exact des fallbacks CSS autorises ou migration-only. -->

# CSS Fallback Allowlist

Les tokens canoniques requis doivent etre consommes via `var(--token)` dans les
surfaces migrees. Les fallbacks restants sont des exceptions classees, pas une
deuxieme source de verite.

| File | Token | Literal | Status | Reason | Exit condition |
|---|---|---|---|---|---|
| `frontend/src/App.css` | `--usage-progress` | `0` | dynamic | valeur de progression runtime injectee par propriete CSS | permanent tant que la progression reste runtime |
| `frontend/src/components/NatalInterpretation.css` | `--premium-glass-border-soft` | `rgba(255, 255, 255, 0.2` | compatibility | alias de token historique en transition | remplacer par le token canonique direct |
| `frontend/src/components/NatalInterpretation.css` | `--premium-radius-pill` | `999px` | compatibility | alias de token historique en transition | remplacer par le token canonique direct |
| `frontend/src/components/NatalInterpretation.css` | `--premium-radius-pill` | `999px` | compatibility | alias de token historique en transition | remplacer par le token canonique direct |
| `frontend/src/components/NatalInterpretation.css` | `--space-3` | `0.75rem` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/NatalInterpretation.css` | `--space-4` | `1rem` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/NatalInterpretation.css` | `--font-size-sm` | `0.875rem` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/KeyPointCard.css` | `--shadow-hero-card` | `0 4px 20px rgba(44, 28, 100, 0.15` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/KeyPointCard.css` | `--color-hero-ink` | `var(--color-text-primary` | compatibility | alias de token historique en transition | remplacer par le token canonique direct |
| `frontend/src/components/prediction/KeyPointCard.css` | `--color-hero-ink-accent` | `var(--color-primary` | compatibility | alias de token historique en transition | remplacer par le token canonique direct |
| `frontend/src/components/prediction/PeriodCard.css` | `--color-text-muted` | `rgba(30, 27, 46, 0.45` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/PeriodCard.css` | `--color-error` | `#ff6b81` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/PeriodCard.css` | `--color-text-muted` | `rgba(30, 27, 46, 0.55` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/PeriodCard.css` | `--color-text-secondary` | `rgba(30, 27, 46, 0.72` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/PeriodCard.css` | `--color-text-muted` | `rgba(30, 27, 46, 0.35` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/prediction/PeriodCard.css` | `--color-text-muted` | `rgba(30, 27, 46, 0.5` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/components/SignUpForm.css` | `--danger` | `#ff6b81` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/features/chat/components/ChatWindow.css` | `--premium-radius-pill` | `999px` | compatibility | alias de token historique en transition | remplacer par le token canonique direct |
| `frontend/src/pages/admin/AdminEntitlementsPage.css` | `--glass-heavy` | `#1a1a1a` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/pages/landing/sections/TestimonialsSection.css` | `--success` | `#2ecc71` | migration-only | fallback conserve hors lot CS-044 avant migration de sa surface | supprimer quand la surface est integree a un lot de migration |
| `frontend/src/pages/NatalChartPage.css` | `--premium-text-muted` | `var(--text-muted` | needs-user-decision | alias premium absent de `premium-theme.css`; retrait bloque sans decision produit/theme | declarer un token canonique ou remplacer par une cible produit explicite |
| `frontend/src/pages/NatalChartPage.css` | `--premium-glass-border-soft` | `rgba(255, 255, 255, 0.2` | needs-user-decision | alias premium absent de `premium-theme.css`; retrait bloque sans decision produit/theme | declarer un token canonique ou remplacer par une cible produit explicite |
| `frontend/src/pages/NatalChartPage.css` | `--premium-glass-border-soft` | `rgba(255, 255, 255, 0.3` | needs-user-decision | alias premium absent de `premium-theme.css`; retrait bloque sans decision produit/theme | declarer un token canonique ou remplacer par une cible produit explicite |
| `frontend/src/pages/settings/Settings.css` | `--usage-progress` | `0` | dynamic | valeur de progression runtime injectee par propriete CSS | permanent tant que la progression reste runtime |
