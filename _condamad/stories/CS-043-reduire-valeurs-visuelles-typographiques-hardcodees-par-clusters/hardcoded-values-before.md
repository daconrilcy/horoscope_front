# CS-043 hardcoded values before

## Baseline

- Source audit F-005 reported broad hardcoded visual debt: 1671 color-like hits, 1570 typography declarations, 2653 spacing/radius/shadow declarations.
- Selected bounded cluster: static inline migrations and feedback/button danger colors in settings and button primitives.
- Cluster count before: static inline visual declarations were present in `AccountSettings.tsx`, `AstrologerProfilePage.tsx`, `NotFoundPage.tsx`, `NatalInterpretation.tsx`, `PeriodCard.tsx`, `Form.tsx`, and `ChatLayout.tsx`; `Button.css` used `#ffffff` for danger text and `Settings.css` used literal success/error feedback colors.
