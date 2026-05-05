# CS-042 CSS fallbacks before

## Baseline

- Initial global fallback count from audit/story: 165 fallbacks across 30 CSS files.
- Selected shared batch: UI primitives and shared layout surfaces (`Badge`, `EmptyState`, `ErrorState`, `LockedSection`, `UpgradeCTA`, `Modal`, `Select`, `WizardLayout`, `PageLayout`, `TwoColumnLayout`, `ChatQuotaBanner`).
- Batch intent: remove migration-only literals where global tokens already exist.
