<!-- Story candidates issus de l'audit frontend design-system apres refactors. -->

# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-004
- Suggested story title: Isoler HelpPage des tokens page-scoped Settings
- Suggested archetype: dependency-direction-audit
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: remove the cross-page dependency from `HelpPage.css` to `--settings-*` variables and replace it with Help-owned or global semantic tokens.
- Must include:
  - replace `--settings-card-border` and `--settings-card-shadow-soft` usages in `frontend/src/pages/HelpPage.css`;
  - update `frontend/src/styles/token-namespace-registry.md` if a shared namespace is promoted or a Help semantic token is added;
  - add or extend a guard that fails when page-scoped namespaces are consumed outside their owner file;
  - include before/after scan for `--settings-` in `HelpPage.css`.
- Validation hints:
  - `npm run test -- HelpPage design-system theme-tokens visual-smoke`
  - `npm run lint`
- Blockers: none if Help owns the replacement tokens; product/design decision needed only if promoting a shared settings/profile card namespace.
- Files to modify:
  - `frontend/src/pages/HelpPage.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - optionally `frontend/src/tests/design-system-policy.ts` if the page-scoped-token scan is centralized.

## SC-002

- Candidate ID: SC-002
- Source finding: F-005
- Suggested story title: Converger les namespaces CSS migration-only restants
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-049`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: resolve active and stale migration-only token namespaces so the token registry no longer preserves obsolete or ambiguous compatibility rows.
- Must include:
  - remove the stale `--default_dropshadow` row if zero active usage remains;
  - decide per namespace whether `--settings-*`, `--profile-*`, and `--astro-*` become semantic extensions or are migrated to global/page canonical tokens;
  - update owner CSS and registry rows consistently;
  - add exact no-return scans for removed migration-only names.
- Validation hints:
  - `npm run test -- design-system theme-tokens legacy-style visual-smoke`
  - `npm run lint`
- Blockers: design decision required for `--settings-*`, `--profile-*`, and `--astro-*` target status.
- Files to modify:
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/App.css`
  - `frontend/src/pages/settings/Settings.css`
  - `frontend/src/pages/AstrologerProfilePage.css`
  - `frontend/src/tests/design-system-guards.test.ts`
  - optionally `frontend/src/tests/theme-tokens.test.ts`

## SC-003

- Candidate ID: SC-003
- Source finding: F-006
- Suggested story title: Classer les compatibilites runtime frontend restantes
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-compatibility
- Required contracts: `RG-049`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: create a single frontend compatibility registry for retained legacy payload and route-shape handling, then remove or rename unneeded legacy code paths.
- Must include:
  - classify consultation `isLegacy`, `mapLegacyConsultationKey`, `buildLegacyBlocks` and prediction older-payload mappers;
  - document owner, canonical replacement, supported input shape and exit condition;
  - update tests so retained compatibility is asserted without leaking user-facing legacy vocabulary;
  - remove dead compatibility paths if evidence shows no supported payload still requires them.
- Validation hints:
  - `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system`
  - `npm run lint`
- Blockers: user/product decision required before removing support for historical consultation or prediction payloads.
- Files to modify:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/features/consultations/components/ConsultationTypeStep.tsx`
  - `frontend/src/features/consultations/components/ConsultationFormStep.tsx`
  - `frontend/src/utils/bestWindowCardMapper.ts`
  - `frontend/src/utils/domainRankingCardMapper.ts`
  - `frontend/src/utils/dayClimateHeroMapper.ts`
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/utils/turningPointCardMapper.ts`
  - `frontend/src/components/prediction/DayTimeline.tsx`
  - `frontend/src/components/prediction/TurningPointsList.tsx`
  - `frontend/src/tests/ConsultationMigration.test.tsx`
  - `frontend/src/tests/consultationStore.test.ts`
  - likely add `frontend/src/styles/frontend-compatibility-registry.md` or a better named registry under `frontend/src/docs/` if that docs location already exists.

## SC-004

- Candidate ID: SC-004
- Source finding: F-007
- Suggested story title: Decider les redirects legacy admin frontend
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-routing
- Required contracts: `RG-049`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: decide whether `/admin/pricing`, `/admin/monitoring`, and `/admin/personas` redirects are permanent supported routes or removable compatibility shims.
- Must include:
  - classify each redirect with owner and exit condition, or remove it;
  - update `AdminPage.test.tsx` to assert the chosen policy;
  - add a route compatibility registry or include the redirects in the shared frontend compatibility registry from SC-003.
- Validation hints:
  - `npm run test -- AdminPage`
  - `npm run lint`
- Blockers: user/product decision required if historical admin URLs must remain supported.
- Files to modify:
  - `frontend/src/app/routes.tsx`
  - `frontend/src/tests/AdminPage.test.tsx`
  - likely the same compatibility registry created by SC-003.

## SC-005

- Candidate ID: SC-005
- Source finding: F-003
- Suggested story title: Migrer le prochain cluster de valeurs visuelles hardcodees frontend
- Suggested archetype: duplicate-rule-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-045`, `RG-046`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: reduce the remaining hardcoded visual and typography values through one coherent cluster, without a repository-wide cleanup.
- Must include:
  - `hardcoded-values-before.md` and `hardcoded-values-after.md`;
  - exact subset from the exhaustive `F-003` file list in `00-audit-report.md`;
  - token docs update only when a semantic owner becomes durable;
  - focused visual smoke or component/page tests for the touched surface.
- Validation hints:
  - `npm run test -- design-system visual-smoke`
  - focused tests for the selected cluster
  - `npm run lint`
  - `npm run build`
- Blockers: choose one bounded cluster. Recommended first options: `DailyHoroscopePage` prediction components, admin CSS pages, landing sections, or shared UI primitives.
- Files to modify:
  - choose a bounded subset from the exhaustive `F-003` list in `00-audit-report.md`; do not touch all 101 files in one story.

## Regression Guardrails

- `RG-044` applies to token namespace changes.
- `RG-045` and `RG-046` apply to hardcoded visual and typography migrations.
- `RG-047` applies if TSX inline styles are touched.
- `RG-048` applies if CSS fallback surfaces are touched.
- `RG-049` applies to legacy, compatibility, alias and redirect surfaces.
- `RG-050` applies to every story candidate above.
