# Token namespaces before

Baseline reconstructed from SC-001 and pre-change scans.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `--bg-*` | namespace | historical-facade | background/app consumers | `--color-bg-*` | replace-consumer | pre-change rg hits in App/backgrounds | visual drift low |
| `--cta-*` | namespace | historical-facade | CTA/button consumers | `--color-cta-*` | replace-consumer | pre-change rg hits | low |
| `--badge-*` | namespace | historical-facade | Badge, cards, tests | `--color-badge-*` | replace-consumer | pre-change rg hits | low |
| `--nav-*` | namespace | historical-facade | bottom nav | `--color-nav-*` | replace-consumer | pre-change rg hits | low |
| `--line`, `--success`, `--danger`, `--btn-text`, `--purple_base` | aliases | historical-facade | CSS/TS consumers | `--color-*` | replace-consumer | pre-change rg hits | low |
| `--background-*`, `--ni-*`, `--result-*`, `--timeline-*`, `--page-*`, `--inner-light`, `--accent-purple*` | namespaces | migration-only | component/page CSS | semantic non-legacy local names or premium tokens | replace-consumer | pre-change rg hits | medium |
