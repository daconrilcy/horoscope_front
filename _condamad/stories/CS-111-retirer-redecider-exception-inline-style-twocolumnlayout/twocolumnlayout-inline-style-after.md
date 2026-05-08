<!-- Preuve CS-111 apres convergence de l'exception inline style layout. -->

# CS-111 After

## Removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `TwoColumnLayout.tsx style=` | inline style | `historical-facade` | no active `sidebarWidth` consumers | `TwoColumnLayout.css` with `--layout-sidebar-width` set to the historical `320px` default | `delete` | scans + inline/design-system/theme-token tests | visual drift guarded by token assertion |
| `--sidebar-width` generic token | CSS custom property | `historical-facade` | `ChatPage.css` fixed CSS width | `--chat-sidebar-width` under existing `--chat-*` namespace | `replace-consumer` | scan zero hit for `--sidebar-width` active source | low |
| `TwoColumnLayout` allowlist rows | test exception | `historical-facade` | test guard registries | no row needed after inline style removal | `delete` | `rg` zero hit in allowlists | none |

## Scans

| Command | Result | Evidence |
|---|---|---|
| `rg -n "TwoColumnLayout|sidebarWidth|--sidebar-width|style=" frontend/src` | PASS | No `sidebarWidth`, no `--sidebar-width`, no `TwoColumnLayout` inline style. Remaining `style=` hits are existing non-layout exact allowlists. |
| `rg -n "TwoColumnLayout|--sidebar-width" frontend/src/tests/design-system-allowlist.ts frontend/src/tests/inline-style-allowlist.ts` | PASS | Zero hit expected. |
| `rg -n -e "--layout-sidebar-width" -e "sidebarWidth" -e "TwoColumnLayout" frontend/src/styles/design-tokens.css frontend/src/layouts frontend/src/pages frontend/src/components frontend/src/features` | PASS | `--layout-sidebar-width` is consumed only by `TwoColumnLayout` and preserves `320px`. |

## Conclusion

The arbitrary width branch is not needed. The layout width is CSS-owned and the
generic sidebar token was converged to the existing chat namespace. The
historical `320px` default is preserved by the canonical layout token.
