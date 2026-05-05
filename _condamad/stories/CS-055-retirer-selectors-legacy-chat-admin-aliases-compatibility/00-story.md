# Story CS-055 retirer-selectors-legacy-chat-admin-aliases-compatibility: Retirer les selectors legacy chat/admin et aliases compatibility restants

Status: ready-to-dev

## 1. Objective

Classer puis retirer les selectors legacy chat/admin et aliases de compatibilite lorsque leur owner canonique est prouve.
Les styles du shell chat quittent `App.css` quand possible; les aliases tokens disparaissent apres migration vers `--color-*`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-004`
- Reason for change: `F-005` indique que `App.css`, `AdminPromptsPage.css`, `theme.css` et les registres conservent des surfaces legacy ou compatibility actives.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Classer chaque famille legacy/compatibility restante comme `remove-now`, `migrate`, ou `needs-user-decision`.
  - Deplacer les styles du shell chat depuis `App.css` vers les CSS canoniques de composants quand les consumers sont prouves.
  - Retirer les aliases `--text-*`, `--glass*`, `--primary*` ou equivalents seulement apres migration vers `--color-*` canonique.
  - Mettre a jour `legacy-style-surface-registry.md` et `token-namespace-registry.md`.
- Out of scope:
  - Refonte visuelle chat/admin.
  - Suppression d'alias encore consomme ou externe sans decision explicite.
  - Migration globale des hardcoded values, fallbacks CSS ou styles inline.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-049` ou `RG-050`.
  - Ne pas remplacer un alias compatibility par un autre alias.
  - Ne pas garder une surface retiree via wrapper, fallback, selector legacy ou re-export CSS.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: les selectors legacy et aliases compatibility font facade vers des owners CSS/token canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les consommateurs migres doivent utiliser les selectors ou tokens canoniques.
  - Les surfaces sans remplacement prouve restent classees ou bloquent sur decision utilisateur.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un alias ou selector semble supporte par theming externe, historique produit, docs, ou comportement non testable localement.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards `legacy-style`, `theme-tokens` et `design-system` prouvent l'etat executable. |
| Baseline Snapshot | yes | Les surfaces legacy et aliases doivent etre inventories before/after. |
| Ownership Routing | yes | Chaque surface doit pointer vers un owner canonique ou blocker. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre exactes dans les registres. |
| Contract Shape | no | Aucun contrat API, DTO ou schema public n'est modifie. |
| Batch Migration | yes | Les consumers peuvent devoir migrer par lot avant suppression. |
| Reintroduction Guard | yes | Les selectors/aliases retires ne doivent pas revenir. |
| Persistent Evidence | yes | Les audits before/after doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/theme.css`
- Secondary evidence:
  - Scans `legacy`, `--text-`, `--glass`, `--primary` dans `src/styles`, `src/App.css`, et `src/pages/admin/AdminPromptsPage.css`.
- Static scans alone are not sufficient for this story because:
  - Une surface peut etre conservee si le registre prouve un blocker; un zero-hit non documente ne prouve pas l'ownership.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/legacy-surfaces-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/legacy-surfaces-after.md`
- Expected invariant:
  - Toute surface retiree a un remplacement canonique ou une preuve de non-consommation; toute surface restante est classifiee.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Selector legacy chat | CSS du composant chat canonique | `App.css` legacy selector |
| Selector legacy admin | CSS admin canonique | alias selector ou wrapper |
| Alias compatibility token | token `--color-*` classe | nouvel alias compatibility |
| Surface restante | `legacy-style-surface-registry.md` ou `token-namespace-registry.md` | exception implicite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/legacy-style-surface-registry.md` | selectors legacy restants | Surfaces legacy classifiees. | Must include exit condition or blocker. |
| `frontend/src/styles/token-namespace-registry.md` | aliases compatibility restants | Classification token. | Must shrink or remain justified. |
| `frontend/src/tests/design-system-allowlist.ts` | exceptions si impactees | Guard executable. | Must match final static state. |

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
| Chat/admin legacy batch | legacy selectors and aliases | canonical CSS and `--color-*` | referencing files | guards | zero-hit scans | ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before audit | `legacy-surfaces-before.md` | Inventorier et classer toutes les surfaces initiales. |
| After audit | `legacy-surfaces-after.md` | Prouver suppressions, migrations et exceptions restantes. |

## 4i. Reintroduction Guard

- Guard target: selectors legacy retires, aliases compatibility retires, et synchronisation des registres.
- Deterministic source: forbidden symbols from `legacy-surfaces-after.md` and the style registries.
- Architecture guard against reintroduction required: `npm run test -- legacy-style theme-tokens design-system`.
- The architecture guard must fail if a retired selector or compatibility alias is reintroduced.
- Guard evidence: Evidence profile: `reintroduction_guard`; scans cibles `legacy|--text-|--glass|--primary`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-005` - surfaces legacy actives.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-004` - extinction chat/admin legacy et aliases compatibility demandee.
- Evidence 3: `frontend/src/styles/legacy-style-surface-registry.md` - registre des surfaces legacy.
- Evidence 4: `frontend/src/styles/token-namespace-registry.md` - registre des namespaces et aliases tokens.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- 100% des surfaces ciblees sont classifiees.
- Les surfaces `remove-now` sont supprimees, pas repointees.
- Les consumers internes utilisent les selectors/tokens canoniques ou la story bloque sur decision explicite.
- Les registres et guards refletent exactement l'etat final.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens restent classes.
  - `RG-049` - les surfaces CSS legacy restent owned et classifiees.
  - `RG-050` - les guards anti-drift restent executables.
- Non-applicable invariants:
  - `RG-047` - styles inline hors scope.
  - `RG-048` - fallbacks CSS hors scope sauf si alias retirement les impacte.
  - `RG-045` et `RG-046` - hardcoded values/typographie hors scope sauf migration directe d'un consumer.
- Required regression evidence:
  - `npm run test -- legacy-style theme-tokens design-system`, scans cibles, artefacts before/after.
- Allowed differences:
  - Diminution des entrees legacy/compatibility et migration des consumers vers selectors/tokens canoniques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Chaque famille legacy/compatibility ciblee est classifiee. | Evidence profile: `baseline_snapshot`; `rg -n "unclassified|TODO|TBD" legacy-surfaces-before.md`. |
| AC2 | Chaque surface `remove-now` est supprimee sans shim. | Evidence profile: `negative_scan`; `rg -n "removed-surface" frontend/src`. |
| AC3 | Chaque consumer migre utilise l'owner canonique. | Evidence profile: `ownership_guard`; `rg -n "Canonical replacement" legacy-surfaces-after.md`. |
| AC4 | La synchronisation des registres legacy passe le guard. | Evidence profile: `runtime_guard`; `npm run test -- legacy-style theme-tokens design-system`. |
| AC5 | Les surfaces ambigues bloquent la suppression. | Evidence profile: `blocker_guard`; `rg -n "needs-user-decision|external-active" legacy-surfaces-after.md`. |
| AC6 | Aucun nouvel alias compatibility ou selector legacy n'est introduit. | Evidence profile: `reintroduction_guard`; `rg -n "legacy|--text-|--glass|--primary" src`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier et classifier toutes les surfaces legacy/compatibility ciblees (AC: AC1)
- [ ] Task 2 - Identifier owner canonique et consumers pour chaque surface (AC: AC3)
- [ ] Task 3 - Migrer consumers vers selectors/tokens canoniques avant suppression (AC: AC3, AC6)
- [ ] Task 4 - Supprimer les surfaces `remove-now` sans shim ni alias (AC: AC2, AC6)
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
  - Elle est deja canonique ou documentee dans le registre.

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
- Nouvelle valeur `--text-*`, `--glass*`, ou `--primary*` qui preserve une surface legacy sans classification.

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
- `keep`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/legacy-surfaces-before.md`
- `_condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/legacy-surfaces-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Legacy selectors chat/admin | canonical component/page CSS | unregistered legacy selector |
| Compatibility token aliases | `--color-*` tokens + `token-namespace-registry.md` | unregistered alias |
| Remaining exceptions | style registries | implicit legacy surface |

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

If an item is `external-active` or `needs-user-decision`, it must not be deleted. The dev agent must stop or record explicit user decision with evidence and risk.

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
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - remove or migrate chat shell legacy selectors when canonical replacement is proven.
- `frontend/src/pages/admin/AdminPromptsPage.css` - remove or migrate admin legacy selectors when proven.
- `frontend/src/styles/theme.css` - retire compatibility aliases when consumers use canonical tokens.
- `frontend/src/styles/token-namespace-registry.md` - synchronize alias classification.
- `frontend/src/styles/legacy-style-surface-registry.md` - synchronize legacy surface state.
- `_condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/legacy-surfaces-before.md` - baseline.
- `_condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/legacy-surfaces-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- Existing legacy-style guard tests selected by `npm run test -- legacy-style`.

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
rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict `
  _condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/00-story.md
```

## 22. Regression Risks

- Risk: supprimer un alias encore consomme par theme externe.
  - Guardrail: `needs-user-decision` bloque sans preuve canonique.
- Risk: remplacer legacy par un autre alias.
  - Guardrail: AC2 et AC6 interdisent shim, wrapper et alias.
- Risk: registres desynchronises.
  - Guardrail: AC4 exige guards legacy/theme/design-system.

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

- `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-005` - current files and risk.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
