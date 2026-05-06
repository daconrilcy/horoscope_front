# CS-062 - Hardcoded values after

Chosen cluster: `frontend/src/components/prediction/PeriodCard.css`.

Migrated:
- main glass surface, borders and shadows now use existing token sources through `color-mix()`;
- metadata/label font sizes now use `--type-metadata-size` and `--type-label-size`;
- repeated `4px` / `8px` dot spacing moved to `--space-1` / `--space-2`;
- tone colors migrated to `--color-success`, `--color-admin-warning-ink` and `--color-primary-strong`.

Remaining classified literals:
- period icon colors remain product-specific period accents.
- `18px` pivot geometry remains exact icon geometry.
- `rgb(206 187 255 / 78%)` selected glow remains a local visual accent pending a dedicated token decision.
- commented historical CSS remains unchanged.

No registry update required: no new token namespace or typography role was introduced.
