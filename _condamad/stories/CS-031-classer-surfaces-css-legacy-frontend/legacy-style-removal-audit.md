<!-- Audit de classification des surfaces CSS legacy frontend. -->

# Legacy Style Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.chat-layout-legacy*` | selector-family | historical-facade | chat runtime styles in `App.css` | chat component CSS | keep migration-only | `npm run test -- legacy-style` | visual drift if deleted now |
| `.conversation-item-legacy*` | selector-family | historical-facade | conversation list UI | conversation item CSS | keep migration-only | `npm run test -- legacy-style` | visual drift if deleted now |
| `.admin-prompts-legacy*` | selector-family | historical-facade | admin prompt route | route-specific CSS | keep migration-only | `npm run test -- legacy-style` | route regression if deleted now |
| `--text-*` | token-alias | historical-facade | legacy theme consumers | `--color-text-*` | keep compatibility | `npm run test -- legacy-style` | token drift |
| `--glass*` | token-alias | historical-facade | legacy theme consumers | `--color-glass-*` | keep compatibility | `npm run test -- legacy-style` | token drift |
| `--primary*` | token-alias | historical-facade | legacy theme consumers | `--color-primary*` | keep compatibility | `npm run test -- legacy-style` | token drift |
