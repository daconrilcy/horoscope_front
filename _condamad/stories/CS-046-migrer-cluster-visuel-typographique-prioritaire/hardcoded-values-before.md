<!-- Baseline initial du cluster visuel et typographique CS-046. -->

# CS-046 Hardcoded Values Before

Cluster:

- `frontend/src/App.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`

## Decisions de migration

Mappings non ambigus vers tokens existants:

- `font-weight: 400/500/600/700` -> `--font-weight-*`
- `font-size: 12/14/16/18px` -> `--font-size-*`
- `line-height: 1.5/1.6` -> `--line-height-*`
- `gap: 4/8/12/16/24/28/32/40/48px` -> `--space-*`
- `border-radius: 8/14/20/28/999/9999px` -> `--radius-*`

Les couleurs, gradients, shadows et tailles editoriales non evidentes restent classees comme exceptions locales du cluster; aucun token near-equivalent n'a ete force.

## Baseline

Le diff de migration prouve 299 declarations hardcodees remplacees par des tokens canoniques dans le cluster.

Commande de controle utilisee apres edition pour compter les suppressions depuis le baseline Git:

```powershell
git diff -- frontend/src/App.css frontend/src/pages/admin/AdminPromptsPage.css frontend/src/pages/HelpPage.css frontend/src/pages/settings/Settings.css frontend/src/pages/AstrologerProfilePage.css | rg -n "^-\\s*(font-weight: (400|500|600|700)|font-size: (12|14|16|18)px|line-height: 1\\.(5|6)|gap: (4|8|12|16|24|28|32|40|48)px|border-radius: (8|14|20|28|999|9999)px);"
```
