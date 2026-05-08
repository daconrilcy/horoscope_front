<!-- Baseline CS-111 avant suppression de l'exception inline style layout. -->

# CS-111 Before

## Baseline inventory

| Item | Evidence |
|---|---|
| `TwoColumnLayout.tsx` inline style | `style={{ '--sidebar-width': sidebarWidth }}` present before implementation. |
| `sidebarWidth` prop | Present on `TwoColumnLayoutProps`; no first-party component consumer passed it. |
| `--sidebar-width` CSS token | Present in `ChatPage.css` and token namespace registry. |
| Allowlist rows | `TwoColumnLayout` row in `design-system-allowlist.ts` and dynamic entry in `inline-style-allowlist.ts`. |

## Decision from baseline

Current first-party usages are finite CSS-owned widths. No arbitrary runtime
sidebar width requirement is proven.
