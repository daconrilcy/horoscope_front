# Story CS-051 retirer-surfaces-css-legacy-aliases-compatibility-restants: Retirer les surfaces CSS legacy et aliases compatibility restants

Status: ready-to-dev

## 1. Objective

Classer a 100% les selectors legacy et aliases compatibility restants identifies par `F-006`.
Retirer toutes les entrees ayant un remplacement canonique prouve.
Synchroniser les registres/tests No Legacy dans la meme modification.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-005`
- Reason for change: les surfaces legacy restent controlees mais actives.
  Elles doivent diminuer sans shim ni alias supplementaire.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Classer les selectors legacy et aliases compatibility actuels en `remove-now`, `migrate`, ou `needs-user-decision`.
  - Retirer les entrees dont le remplacement canonique est prouve.
  - Mettre a jour `legacy-style-surface-registry.md`, `token-namespace-registry.md` et les allowlists/tests associes.
  - Prouver par scans cibles que les surfaces retirees ne restent pas actives.
- Out of scope:
  - Refonte visuelle.
  - Suppression d'aliases encore necessaires sans decision produit.
  - Migration globale de hardcoded values non legacy.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-049` ou `RG-050`.
  - Ne pas remplacer un alias compatibility par un autre alias compatibility.
  - Ne pas garder une surface retiree via wrapper, fallback ou re-export CSS.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story eteint des surfaces CSS legacy/compatibility qui font facade vers des owners canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les consommateurs migres doivent utiliser les selectors/tokens canoniques.
  - Les surfaces sans remplacement prouve restent bloquees ou classifiees, pas supprimees.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un alias ou selector semble encore support externe, theming historique, ou contrat produit.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards legacy-style/theme-tokens/design-system prouvent l'etat executable. |
| Baseline Snapshot | yes | Les surfaces legacy doivent etre inventoriees before/after. |
| Ownership Routing | yes | Chaque surface legacy doit pointer vers un owner canonique ou blocker. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre exactes dans les registres. |
| Contract Shape | no | Aucun API, DTO ou schema public n'est modifie. |
| Batch Migration | yes | Les consumers peuvent devoir migrer par lot. |
| Reintroduction Guard | yes | Les selectors/aliases retires ne doivent pas revenir. |
| Persistent Evidence | yes | L'audit de classification et les preuves de retrait doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/token-namespace-registry.md`
- Secondary evidence:
  - Scans `legacy`, `--text-`, `--glass`, `--primary` dans les fichiers cibles.
- Static scans alone are not sufficient for this story because:
  - Une surface legacy peut etre conservee si le registre prouve un blocker; inversement un zero-hit non documente ne prouve pas l'ownership.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/legacy-surfaces-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/legacy-surfaces-after.md`
- Expected invariant:
  - Toute surface retiree a un remplacement canonique ou une preuve de non-consommation; toute surface restante est classifiee.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Selector legacy retire | selector canonique documente | alias/wrapper CSS |
| Alias compatibility token | token canonique classe | alias compatibility nouveau |
| Surface restante | `legacy-style-surface-registry.md` | exception implicite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/legacy-style-surface-registry.md` | selectors/aliases restants | Legacy/compatibility classified. | Must include exit condition or blocker. |
| `frontend/src/styles/token-namespace-registry.md` | compatibility token namespaces | Ownership token classification. | Must shrink or remain justified. |
| `frontend/src/styles/css-fallback-allowlist.md` | fallback affected by alias retirement | Synchronization if touched. | Must remain exact. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| F-006 legacy batch | legacy selectors and aliases | canonical selectors/tokens | referencing files | legacy guards | zero-hit scans | ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before audit | `legacy-surfaces-before.md` | Inventorier et classer toutes les surfaces initiales. |
| After audit | `legacy-surfaces-after.md` | Prouver suppressions, migrations et exceptions restantes. |

## 4i. Reintroduction Guard

- Guard target: retired legacy selectors, compatibility aliases, and registry synchronization.
- Deterministic source: forbidden symbols from `legacy-surfaces-after.md` and the style registries.
- Architecture guard against reintroduction required: `npm run test -- legacy-style theme-tokens design-system`.
- The architecture guard must fail if a retired selector or compatibility alias is reintroduced.
- Guard evidence: Evidence profile: `reintroduction_guard`; targeted scans for `legacy`, `--text-`, `--glass`, `--primary`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-006` - active compatibility and migration-only surfaces remain.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-005` - requires classification and removal of canonical replacements only.
- Evidence 3: `frontend/src/styles/legacy-style-surface-registry.md` - registry for legacy style surfaces.
- Evidence 4: `frontend/src/styles/token-namespace-registry.md` - registry for token namespaces and compatibility aliases.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- 100% des surfaces F-006 sont classifiees.
- Les surfaces `remove-now` sont supprimees, pas repointees.
- Les consumers internes utilisent le canonique ou la story bloque sur decision explicite.
- Les registres et guards refletent exactement l'etat final.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespaces must remain classified.
  - `RG-048` - fallback registry must remain exact if a fallback is touched.
  - `RG-049` - legacy style surfaces must stay owned and classified.
  - `RG-050` - anti-drift tests must remain executable.
- Non-applicable invariants:
  - `RG-047` - inline styles hors scope.
  - `RG-045` - hardcoded value migration covered by `CS-050`.
  - `RG-046` - typography role migration not primary unless alias touches typography.
- Required regression evidence:
  - `npm run test -- legacy-style theme-tokens design-system`, targeted scans, before/after artifacts.
- Allowed differences:
  - Decrease of legacy registry entries and compatibility aliases; consumer migration to canonical selectors/tokens.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Every current F-006 legacy surface is classified. | Evidence profile: `baseline_snapshot`; `rg -n "unclassified|TODO|TBD" legacy-surfaces-before.md`. |
| AC2 | Every `remove-now` surface is deleted. | Evidence profile: `negative_scan`; `rg -n "removed-surface" frontend/src`. |
| AC3 | Every migrated consumer uses the canonical owner. | Evidence profile: `ownership_guard`; `rg -n "Canonical replacement" legacy-surfaces-after.md`. |
| AC4 | Registry files match the final runtime/static state. | Evidence profile: `runtime_guard`; AST guard via `npm run test -- legacy-style theme-tokens design-system`. |
| AC5 | Ambiguous surfaces block deletion. | Evidence profile: `blocker_guard`; `rg -n "needs-user-decision" legacy-surfaces-after.md`. |
| AC6 | No new compatibility alias or legacy selector is introduced. | Evidence profile: `reintroduction_guard`; `rg -n "legacy|--text-|--glass|--primary" src`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier et classifier toutes les surfaces F-006 before (AC: AC1)
- [ ] Task 2 - Identifier owner canonique et consumers pour chaque surface (AC: AC3)
- [ ] Task 3 - Supprimer les surfaces `remove-now` sans shim ni alias (AC: AC2, AC6)
- [ ] Task 4 - Migrer les consumers internes vers le canonique quand prouve (AC: AC3)
- [ ] Task 5 - Mettre a jour registres et allowlists affectees (AC: AC4, AC5)
- [ ] Task 6 - Capturer after et executer validations/scans (AC: AC2, AC4, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/design-tokens.css`
  - Selectors/tokens canoniques deja documentes.
- Do not recreate:
  - Alias compatibility sous un autre nom.
  - Selector legacy equivalent.
  - Fallback CSS pour simuler l'ancien alias.
- Shared abstraction allowed only if:
  - Elle est deja canonique ou documentee dans le registre; aucune abstraction speculative.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- Nouveau selector contenant `legacy`.
- Nouveau token alias compatibility non registre.
- Nouvelle valeur `--text-*`, `--glass*`, ou `--primary*` si elle preserve une surface legacy sans classification.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is the canonical owner and must stay.
- `external-active`: item is referenced by external docs, theming, client, or product surface.
- `historical-facade`: item delegates to a canonical surface for compatibility only.
- `dead`: item has zero active consumers and no external blocker.
- `remove-now`: canonical replacement exists and no active blocker remains.
- `migrate`: consumers must be changed to canonical owner before deletion.
- `needs-user-decision`: external/product/theming ambiguity blocks deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Delete only when no blocker remains. |
| `dead` | `delete` | Must be deleted. |
| `remove-now` | `delete` | Must be deleted, not repointed. |
| `migrate` | `replace`, `delete-after-migration` | Consumers must move first; no shim. |
| `needs-user-decision` | `needs-user-decision` | Must remain classified and block deletion. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `delete`
- `replace-consumer`
- `needs-user-decision`
- `keep`

Audit output path when applicable:

- `_condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/legacy-surfaces-before.md`
- `_condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/legacy-surfaces-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Legacy selectors | `legacy-style-surface-registry.md` until removed, then canonical CSS selector | unregistered legacy selector |
| Compatibility token aliases | `token-namespace-registry.md` until removed, then canonical token | unregistered alias |
| Fallbacks affected by alias removal | `css-fallback-allowlist.md` | implicit fallback |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical selector through alias
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated style active
- preserving the old path through fallback behavior
- preserving the old path through re-export

## 15. External Usage Blocker

If an item is `external-active` or `needs-user-decision`, it must not be deleted.
The dev agent must stop or record explicit user decision with evidence and risk.

## 17. Generated Contract Check

Generated contract check: active

Required generated-contract evidence:

- CSS registry absence for retired surfaces in `legacy-style-surface-registry.md`.
- Token namespace absence for retired aliases in `token-namespace-registry.md`.
- Executable guard absence via `npm run test -- legacy-style theme-tokens design-system`.

## 18. Files to Inspect First

- `frontend/src/App.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - remove or migrate legacy surfaces when canonical replacement is proven.
- `frontend/src/pages/admin/AdminPromptsPage.css` - remove or migrate legacy surfaces when canonical replacement is proven.
- `frontend/src/styles/theme.css` - retire compatibility aliases when safe.
- `frontend/src/styles/token-namespace-registry.md` - synchronize alias classification.
- `frontend/src/styles/legacy-style-surface-registry.md` - synchronize legacy surface state.
- `frontend/src/styles/css-fallback-allowlist.md` - only if alias retirement changes fallbacks.
- `_condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/legacy-surfaces-before.md` - baseline.
- `_condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/legacy-surfaces-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- Existing legacy-style guard test selected by `npm run test -- legacy-style`.

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- Components unrelated to migrated consumers - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- legacy-style theme-tokens design-system
npm run lint
rg -n "legacy|--text-|--glass|--primary" src -g "*.css" -g "*.md" -g "*.ts"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict `
  _condamad/stories/CS-051-retirer-surfaces-css-legacy-aliases-compatibility-restants/00-story.md
```

## 22. Regression Risks

- Risk: supprimer un alias encore consomme par theming ou surface externe.
  - Guardrail: `needs-user-decision` bloque sans preuve canonique.
- Risk: remplacer un legacy par un autre alias.
  - Guardrail: AC2 et AC6 interdisent shim, wrapper et alias.
- Risk: registres desynchronises.
  - Guardrail: AC4 exige tests legacy/theme/design-system.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-005` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/02-finding-register.md#F-006` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-006` - current files and risk.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
