<!-- Story candidates issus de l'audit frontend design-system. -->

# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-005
- Suggested story title: Retirer ou classifier l'alias CSS astrologer card
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-049`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: remove the active `.astrologer-card-alias` surface or classify it with exact ownership and a guard that also detects alias-named selectors.
- Must include:
  - rename `.astrologer-card-alias` in `App.css` and `AstrologerCard.tsx`, or add an explicit registry row with owner, canonical target, and exit condition;
  - update `legacy-style-policy.test.ts` so alias selectors cannot bypass classification when they do not contain `legacy`;
  - before/after scan for `.alias`, `.legacy`, and `--default_dropshadow`.
- Validation hints:
  - `npm run test -- legacy-style AstrologersPage`
  - `npm run test -- design-system visual-smoke`
  - `npm run lint`
- Blockers: none if renamed; if kept, the reason for an alias-named class must be explicitly documented.
- Files to modify:
  - `frontend/src/App.css`
  - `frontend/src/features/astrologers/components/AstrologerCard.tsx`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/tests/legacy-style-policy.test.ts`

## SC-002

- Candidate ID: SC-002
- Source finding: F-006
- Suggested story title: Decider et converger les libelles consultation Legacy
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-049`, `no-legacy-dry-audit-contract.md`
- Draft objective: resolve the user-visible `(Legacy)` labels in consultation i18n after the admin prompts legacy vocabulary migration.
- Must include:
  - product decision: rename `(Legacy)` labels or keep them as approved compatibility copy;
  - before/after scan of `legacy|Legacy` in `frontend/src/i18n/consultations.ts`;
  - focused test coverage for the chosen consultation label behavior.
- Validation hints:
  - `npm run test -- ConsultationMigration consultationStore`
  - `npm run test -- design-system legacy-style`
  - `npm run lint`
- Blockers: needs user/product decision before changing user-visible labels.
- Files to modify:
  - `frontend/src/i18n/consultations.ts`
  - focused tests to update/add with the chosen product decision, likely under `frontend/src/tests/ConsultationMigration.test.tsx` or a new focused consultation i18n test.

## SC-003

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Migrer le prochain cluster de valeurs visuelles hardcodees frontend
- Suggested archetype: duplicate-rule-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-045`, `RG-046`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: reduce the remaining hardcoded visual and typography values through one coherent product cluster, without a repository-wide cleanup.
- Must include:
  - `hardcoded-values-before.md` and `hardcoded-values-after.md`;
  - exact file list for the selected cluster from the 106-file inventory in `00-audit-report.md`;
  - updates to token docs only when a semantic token becomes durable;
  - focused visual smoke or component/page tests for the touched surface.
- Validation hints:
  - `npm run test -- design-system visual-smoke`
  - focused tests for the selected product cluster
  - `npm run lint`
  - `npm run build`
- Blockers: choose one bounded cluster. Recommended first options: `HelpPage.css`, `AdminPromptsPage.css`, `AstrologerProfilePage.css`, or prediction timeline CSS.
- Files to modify:
  - choose a bounded subset from the exhaustive `F-004` list in `00-audit-report.md`; do not touch all 106 files in one story.

## Regression Guardrails

- `RG-044` applies to any token namespace changes.
- `RG-045` and `RG-046` apply to hardcoded visual/typography migration.
- `RG-047` applies if TSX inline styles are touched.
- `RG-048` applies if CSS fallback surfaces are touched.
- `RG-049` applies to `SC-001` and `SC-002`.
- `RG-050` applies to every story candidate above.
