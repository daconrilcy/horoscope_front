<!-- Inventaire initial des namespaces CSS avant garde CS-026. -->

# Token Namespace Inventory Before

Baseline capture: `rg -n "--[a-z0-9-]+\s*:" src -g "*.css"` depuis `frontend`.

Les namespaces detectes etaient non classes de maniere durable avant cette story.
Les familles principales etaient `--color-*`, `--font-*`, `--space-*`,
`--radius-*`, `--shadow-*`, `--text-*`, `--bg-*`, `--glass*`, `--premium-*`,
`--settings-*`, `--profile-*`, `--landing-*`, `--result-*`, `--astro-*` et
plusieurs variables dynamiques de layout/progression.
