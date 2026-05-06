<!-- Registre des findings pour l'audit frontend design-system apres refactors. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003 | The current frontend guard suite remains executable and green after CS-071, CS-072 and CS-073. | Keep `RG-044` to `RG-050` mandatory for future frontend style stories. | no |
| F-002 | Info | High | legacy-surface | frontend-design-system | E-005, E-006, E-007, E-008, E-009 | The prior alias CSS and visible consultation-label legacy findings are closed; fallback and inline-style debt is reduced to exact classified exceptions. | Preserve the existing allowlists and continue zero-hit scans for alias selectors and consultation i18n legacy labels. | no |
| F-003 | Medium | High | duplicate-responsibility | frontend-design-system | E-010 | 101 non-test frontend files still contain hardcoded visual or typography values, so local declarations continue to compete with token ownership. | Continue bounded hardcoded-value migrations by coherent clusters, with before/after inventories and focused tests. | yes |
| F-004 | Medium | High | dependency-direction-violation | frontend-design-system | E-011 | `HelpPage.css` depends on `--settings-*` variables owned by `Settings.css`, creating a cross-page style dependency and weakening page ownership. | Replace the `--settings-*` consumption in HelpPage with Help-owned or global semantic tokens, then guard against cross-page token imports. | yes |
| F-005 | Medium | High | legacy-surface | frontend-design-system | E-011 | `--settings-*`, `--profile-*`, `--astro-*` remain migration-only namespaces and `--default_dropshadow` remains registered despite zero active usage. | Converge the migration-only token registry: remove stale rows and either promote, rename, or retire active page-scoped namespaces. | yes |
| F-006 | Medium | Medium | legacy-surface | frontend-compatibility | E-012, E-014 | Runtime compatibility paths for legacy consultation and prediction payloads remain active without a shared frontend compatibility registry or exit decisions. | Create a frontend compatibility registry, classify each kept compatibility path, and remove or rename paths that no longer need legacy semantics. | yes |
| F-007 | Medium | High | legacy-surface | frontend-routing | E-013 | Legacy admin redirects remain active and tested, but are not tied to an explicit frontend route compatibility policy. | Decide whether the redirects are permanent product routes or removable compatibility shims; update route tests and registry accordingly. | yes |
| F-008 | Low | High | observability-gap | frontend-performance | E-004 | Build passes but the main JS chunk remains above Vite's 500 kB warning threshold. | Track bundle splitting in a separate frontend performance story; keep it outside design-system cleanup scope. | no |

## Finding Details

### F-001

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003
- Expected rule: design-system governance is protected by executable guardrails and future stories cite `RG-044` to `RG-050`.
- Actual state: targeted guard tests and lint pass after the refactors.
- Impact: The current frontend guard suite remains executable and green after CS-071, CS-072 and CS-073.
- Recommended action: Keep `RG-044` to `RG-050` mandatory for future frontend style stories.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-005, E-006, E-007, E-008, E-009
- Expected rule: retired aliases and visible legacy labels stay absent; remaining fallback and inline-style exceptions are exact and classified.
- Actual state: alias CSS and consultation i18n legacy scans are zero-hit; CSS fallback and inline-style scans match allowlists.
- Impact: The prior alias CSS and visible consultation-label legacy findings are closed; fallback and inline-style debt is reduced to exact classified exceptions.
- Recommended action: Preserve the existing allowlists and continue zero-hit scans for alias selectors and consultation i18n legacy labels.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-003

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-010
- Expected rule: repeated visual decisions should use canonical tokens or documented semantic owner variables.
- Actual state: 101 non-test frontend files outside `src/styles/**` still contain hardcoded visual or typography literals.
- Impact: 101 non-test frontend files still contain hardcoded visual or typography values, so local declarations continue to compete with token ownership.
- Recommended action: Continue bounded hardcoded-value migrations by coherent clusters, with before/after inventories and focused tests.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal

### F-004

- Severity: Medium
- Confidence: High
- Category: dependency-direction-violation
- Domain: frontend-design-system
- Evidence: E-011
- Expected rule: page-scoped CSS variables are owned and consumed by their page or promoted to a shared/global namespace before reuse.
- Actual state: `HelpPage.css` consumes `--settings-card-border` and `--settings-card-shadow-soft`.
- Impact: `HelpPage.css` depends on `--settings-*` variables owned by `Settings.css`, creating a cross-page style dependency and weakening page ownership.
- Recommended action: Replace the `--settings-*` consumption in HelpPage with Help-owned or global semantic tokens, then guard against cross-page token imports.
- Story candidate: yes
- Suggested archetype: dependency-direction-audit

### F-005

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-011
- Expected rule: migration-only token namespaces have concrete exit conditions and stale removed aliases are not kept in the active registry.
- Actual state: the registry still lists `--settings-*`, `--profile-*`, `--astro-*` as migration-only and still lists unused `--default_dropshadow`.
- Impact: `--settings-*`, `--profile-*`, `--astro-*` remain migration-only namespaces and `--default_dropshadow` remains registered despite zero active usage.
- Recommended action: Converge the migration-only token registry: remove stale rows and either promote, rename, or retire active page-scoped namespaces.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-006

- Severity: Medium
- Confidence: Medium
- Category: legacy-surface
- Domain: frontend-compatibility
- Evidence: E-012, E-014
- Expected rule: active frontend compatibility paths are classified with owner, canonical replacement and exit condition.
- Actual state: consultation and prediction compatibility paths remain active, but classification is scattered across comments, tests and mapper names.
- Impact: Runtime compatibility paths for legacy consultation and prediction payloads remain active without a shared frontend compatibility registry or exit decisions.
- Recommended action: Create a frontend compatibility registry, classify each kept compatibility path, and remove or rename paths that no longer need legacy semantics.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-007

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-routing
- Evidence: E-013
- Expected rule: legacy routes are removed or explicitly classified as product-supported redirects with owner and exit condition.
- Actual state: `/admin/pricing`, `/admin/monitoring` and `/admin/personas` redirects remain active in `routes.tsx` and tested in `AdminPage.test.tsx`.
- Impact: Legacy admin redirects remain active and tested, but are not tied to an explicit frontend route compatibility policy.
- Recommended action: Decide whether the redirects are permanent product routes or removable compatibility shims; update route tests and registry accordingly.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-008

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-004
- Expected rule: design-system validation should not hide build-performance warnings.
- Actual state: build passes but Vite reports a main chunk larger than 500 kB.
- Impact: Build passes but the main JS chunk remains above Vite's 500 kB warning threshold.
- Recommended action: Track bundle splitting in a separate frontend performance story; keep it outside design-system cleanup scope.
- Story candidate: no
- Suggested archetype: observability-audit
