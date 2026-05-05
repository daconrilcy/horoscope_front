# CS-041 inline styles before

## Baseline

- Initial scan: 30 `style={` occurrences in 17 TSX files.
- Static occurrences classified for migration: `NatalInterpretation.tsx`, `PeriodCard.tsx`, `Form.tsx`, `ChatLayout.tsx`, `AstrologerProfilePage.tsx`, `NotFoundPage.tsx`, `AccountSettings.tsx`, and the static layout portion of `Skeleton.tsx`.
- Dynamic/custom-property occurrences classified for retention: score widths, timeline positions, badge/category runtime colors, skeleton dimensions/gap, avatar display bridge, and configurable sidebar width.

## Static migration target

Every static occurrence in the audited lot must move to CSS; remaining inline styles must be runtime-dependent and allowlisted exactly.
