# CS-096 before inventory

- line-count: `frontend/src/pages/admin/AdminPromptsPage.tsx` = 3016 lignes avant extraction.
- selected-finite-map-item: helpers, modales et fragments UI de support definis localement avant `AdminPromptsPage`.
- PAGE_SIZE_EXCEPTIONS: `pages/admin/AdminPromptsPage.tsx`, `maxLines: 3200`, raison temporaire de conteneur volumineux.
- Responsabilites locales selectionnees:
  - `ManualLlmExecuteConfirmModal`
  - `ArchiveVersionMetaStrip`
  - `ArchiveRollbackModal`
  - `PromptDisclosure`
  - `AdminPromptsResolvedAssemblyError`
  - helpers `consumptionRowKey`, `formatReleaseSnapshotIdShort`, `formatManifestEntryCatalogHint`,
    `pickPreferredCatalogEntry`, `formatCatalogFeatureLabel`, `releaseDiffAxisBadgeClass`,
    `resolvedAssemblyErrorPresentation`, `placeholderStatusClassName`, `manualExecutionFailureLead`,
    `formatPromptSaveError`, `buildDiffRows`

