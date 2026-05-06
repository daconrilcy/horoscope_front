<!-- Baseline before des surfaces legacy pour CS-067. -->

# Legacy Style Before

Selectors admin prompts:

```text
AdminPromptsPage.tsx et AdminPromptsPage.css consommaient `.admin-prompts-legacy*`
et `.admin-prompts-modal--legacy-rollback`.
```

Aliases token critiques:

```text
`--text-*`, `--glass*` et `--primary*` restent declares dans `frontend/src/styles/theme.css`
et largement consommes par `frontend/src/App.css`.
```

Decision:

| Item | Classification | Decision |
|---|---|---|
| `.admin-prompts-legacy*` | historical-facade | replace-consumer vers `.admin-prompts-archive*` |
| `.admin-prompts-modal--legacy-rollback` | historical-facade | replace-consumer vers `.admin-prompts-modal--rollback` |
| `--text-*` | external-active | keep, migration globale `App.css` hors scope |
| `--glass*` | external-active | keep, migration globale `App.css` hors scope |
| `--primary*` | external-active | keep, migration globale `App.css` hors scope |
