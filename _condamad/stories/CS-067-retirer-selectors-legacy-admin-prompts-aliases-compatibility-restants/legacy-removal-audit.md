<!-- Audit No Legacy pour CS-067. -->

# Legacy Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.admin-prompts-legacy*` | selector-family | historical-facade | `AdminPromptsPage.tsx`, `AdminPromptsPage.css` | `.admin-prompts-archive*` | replace-consumer | scan zero-hit apres migration sur `admin-prompts-legacy` | faible, renommage classe a classe |
| `.admin-prompts-modal--legacy-rollback` | selector | historical-facade | `LegacyRollbackModal`, `AdminPromptsPage.css` | `.admin-prompts-modal--rollback` | replace-consumer | scan zero-hit apres migration sur `admin-prompts-modal--legacy-rollback` | faible, renommage classe a classe |
| `--text-*` | token-alias | historical-facade | `theme.css`, `App.css`, `index.css` | `--color-text-*` | delete + replace-consumer | scan zero-hit dans theme/App/index apres migration; tests `theme-tokens` et `AppBgStyles` | faible, migration vers tokens canoniques couverte par tests |
| `--glass*` | token-alias | historical-facade | `theme.css`, `App.css`, `index.css` | `--color-glass-*`, `--surface-glass-blur` | delete + replace-consumer | scan zero-hit aliases globaux apres migration; tokens locaux DailyHoroscope classes exacts | faible, migration vers tokens canoniques couverte par tests |
| `--primary*` | token-alias | historical-facade | `theme.css`, `App.css`, `index.css` | `--color-primary*` | delete + replace-consumer | scan zero-hit dans theme/App/index apres migration; `--color-primary-rgb` ajoute au token source | faible, migration vers tokens canoniques couverte par tests |
