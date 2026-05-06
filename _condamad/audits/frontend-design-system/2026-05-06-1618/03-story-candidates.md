<!-- Story candidates issus de l'audit frontend design-system apres refactors. -->

# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Migrer un prochain cluster de valeurs visuelles hardcodees frontend
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, `RG-048`, `RG-050`, `RG-055`
- Draft objective: reduce one bounded product cluster from the 101-file hardcoded-value inventory by replacing repeated visual and typography literals with existing tokens or documented semantic extensions.
- Must include:
  - choose a coherent subset from the exhaustive `F-002` file list in `00-audit-report.md`;
  - capture before/after literal scans for only the selected files;
  - reuse existing tokens and typography roles before creating new tokens;
  - update `frontend/src/styles/token-namespace-registry.md` only when a new durable namespace is introduced;
  - keep `frontend/src/tests/design-system-allowlist.ts` exact.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke`
  - targeted `rg --pcre2` count on selected files before/after
  - `npm run lint`
- Blockers: choose the first cluster. Recommended first options: prediction timeline CSS, shared UI primitives, admin pages, or natal/profile pages. Do not modify all 101 files in one story.

## SC-002

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Classer ou supprimer les compatibilites runtime frontend restantes
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-compatibility
- Required contracts: `RG-050`, `RG-053`
- Draft objective: converge the remaining explicit frontend legacy/backward-compatibility paths into either canonical behavior or a small documented compatibility registry.
- Must include:
  - inspect and decide each file listed under `F-003` in `00-audit-report.md`;
  - remove stale compatibility comments/branches when the canonical API shape is sufficient;
  - if a compatibility path is still required, document owner, canonical target, reason and exit condition in a new or existing frontend compatibility registry;
  - add exact tests or guard scans for removed vocabulary and allowed retained exceptions.
- Validation hints:
  - `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage`
  - targeted scan: `rg -n "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility" frontend/src`
  - `npm run lint`
- Blockers: user/product decision may be needed for whether legacy prediction codes and natal aspect IDs are still supported external contracts.

## Regression Guardrails

- `RG-044` applies to token namespace ownership.
- `RG-045` and `RG-046` apply to visual and typography literal migration.
- `RG-048` applies to CSS fallback preservation.
- `RG-050` applies to every design-system story candidate above.
- `RG-053` applies to frontend runtime compatibility removal/classification.
- `RG-055` applies if the selected hardcoded-value cluster touches prediction premium surfaces.
