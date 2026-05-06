<!-- Inventaire after des surfaces legacy pour CS-067. -->

# Legacy Style After

Selectors admin prompts:

```text
`admin-prompts-legacy` et `admin-prompts-modal--legacy-rollback` sont absents
de `AdminPromptsPage.tsx` et `AdminPromptsPage.css`.
```

Surfaces canoniques retenues:

- `.admin-prompts-archive*`
- `.admin-prompts-modal--rollback`

Aliases token critiques:

- `--text-*`, `--glass*` et `--primary*` ne sont plus actifs dans le theme global, `App.css`, `index.css` ou les registres legacy.
- Les consommateurs globaux utilisent les tokens canoniques `--color-text-*`, `--color-glass-*`, `--surface-glass-blur`, `--color-primary*`.
- Les tokens `--glass-*` / `--text-*` restants sont des extensions semantiques locales exactes de `DailyHoroscopePage.css`, declarees dans `token-namespace-registry.md`, pas des aliases de compatibilite du theme global.
