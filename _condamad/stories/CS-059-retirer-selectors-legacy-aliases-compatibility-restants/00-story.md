# Story CS-059 retirer-selectors-legacy-aliases-compatibility-restants: Retirer les selectors legacy et aliases compatibility restants

Status: ready-to-dev

## 1. Objective

Retirer ou reduire les selectors legacy et aliases compatibility restants du design-system frontend.
Le lot priorise les styles chat shell encore presents dans `App.css`.
`admin-prompts-legacy` reste bloque tant que son statut external-active n'a pas de decision.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-004`
- Reason for change: `F-005` indique 17 lignes actives dans `legacy-style-surface-registry.md`, incluant des selectors migration-only chat et des aliases compatibility.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Classer chaque famille legacy restante comme `remove-now`, `migrate` ou `needs-user-decision`.
  - Deplacer les styles chat shell de `App.css` vers les CSS canoniques chat quand possible.
  - Retirer les aliases de tokens seulement apres migration des consommateurs vers les tokens `--color-*` canoniques.
  - Mettre a jour `legacy-style-surface-registry.md` et `token-namespace-registry.md`.
- Out of scope:
  - Suppression de `admin-prompts-legacy` sans decision utilisateur, car l'audit le marque external-active.
  - Refonte admin prompts.
  - Migration des hardcoded values ou fallbacks CSS hors surfaces touchees.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-049` ou `RG-050`.
  - Ne pas creer de selector compatibility ou alias de remplacement.
  - Ne pas conserver une surface legacy en la repointant silencieusement.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story eteint des surfaces compatibility/legacy classees et impose delete-only pour les items removables.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les surfaces canoniques conservees doivent garder le rendu attendu.
  - Les surfaces external-active ne sont pas supprimees sans decision.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une surface est `external-active`, un alias est consomme par une surface non migree, ou un selector admin prompt reste public.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests `legacy-style`, `theme-tokens` et `design-system` prouvent l'etat executable. |
| Baseline Snapshot | yes | Les 17 lignes legacy/alias doivent etre inventoriees avant/apres. |
| Ownership Routing | yes | Les selectors doivent appartenir aux composants canoniques ou au registre legacy. |
| Allowlist Exception | yes | Les exceptions legacy restantes doivent rester exactes avec condition de sortie. |
| Contract Shape | no | Aucun contrat API ou type public n'est modifie. |
| Batch Migration | yes | Le retrait peut migrer plusieurs selectors ou aliases en un lot borne. |
| Reintroduction Guard | yes | Les surfaces retirees ne doivent pas revenir. |
| Persistent Evidence | yes | Les audits before/after doivent rester persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/tests/design-system-allowlist.ts`
  - tests `legacy-style`, `theme-tokens` et `design-system`.
- Secondary evidence:
  - `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css`
- Static scans alone are not sufficient for this story because:
  - Une surface legacy peut etre external-active et ne doit pas etre supprimee sans decision.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-after.md`
- Expected invariant:
  - Les surfaces retirees disparaissent du CSS et des registres; les surfaces conservees gardent owner, statut et sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Styles chat shell | `frontend/src/features/chat/components/*.css` | `frontend/src/App.css` legacy selector |
| Tokens couleur canoniques | `--color-*` dans sources token | aliases `--text-*`, `--glass`, `--primary` non necessaires |
| Surface admin external-active | `AdminPromptsPage.css` plus registre | suppression sans decision |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/legacy-style-surface-registry.md` | selectors legacy restants | Registre canonique No Legacy. | Doit diminuer ou conserver une condition de sortie. |
| `frontend/src/styles/token-namespace-registry.md` | aliases compatibility restants | Classification des namespaces. | Doit pointer vers tokens canoniques ou decision. |
| `frontend/src/tests/design-system-allowlist.ts` | exceptions executees | Guard anti-drift. | Doit rester exact. |

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
| Legacy batch | chat selectors and aliases | chat CSS and `--color-*` tokens | selected CSS | legacy-style guard | registry diff | external-active surface |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `legacy-style-before.md` | Capturer selectors, aliases, owners et classifications initiales. |
| After inventory | `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-after.md` | Prouver suppressions, migrations et restants. |

## 4i. Reintroduction Guard

- Guard target: selectors legacy et aliases compatibility retires.
- Architecture guard against reintroduction required: `npm run test -- legacy-style theme-tokens design-system`.
- Reintroduced forbidden symbols source: `legacy`, `--text-*`, `--glass`, `--primary` in `src/styles`, `src/App.css`, and `src/pages/admin/AdminPromptsPage.css`.
- Guard evidence: Evidence profile: `reintroduction_guard`; command `npm run test -- legacy-style theme-tokens design-system`.
- Forbidden symbols scan: `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-005` - 17 rows actives.
  Chat selectors vivent dans `App.css`; admin reste external-active; aliases vivent dans `theme.css`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-004` - demande classification et retrait/narrowing.
- Evidence 3: `frontend/src/styles/legacy-style-surface-registry.md` - registre canonique legacy style.
- Evidence 4: `frontend/src/styles/token-namespace-registry.md` - registre des aliases compatibility.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les selectors chat migrables vivent dans les CSS canoniques des composants chat.
- Les aliases compatibility retires n'ont plus de consommateurs.
- Les surfaces external-active restent explicites et bloquees jusqu'a decision.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens restent classes.
  - `RG-049` - les surfaces legacy restent owned, classees et avec sortie.
  - `RG-050` - les guards design-system restent executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline ne sont pas le scope.
  - `RG-048` - les fallbacks CSS ne sont pas le scope.
- Required regression evidence:
  - `npm run test -- legacy-style theme-tokens design-system`
  - scan legacy/alias final
  - artifacts before/after.
- Allowed differences:
  - Diminution des lignes legacy/alias et migration de selectors chat vers CSS canoniques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe chaque famille legacy/alias restante. | Evidence profile: `baseline_before_after_diff`; `rg -n "legacy|--text-|--glass" src/styles src/App.css`. |
| AC2 | Les selectors chat migrables quittent `App.css`. | Evidence profile: `ast_architecture_guard`; `npm run test -- legacy-style`. |
| AC3 | Les aliases retires n'ont plus de consommateurs. | Evidence profile: `repo_wide_negative_scan`; `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css`. |
| AC4 | Les surfaces external-active restent bloquees. | Evidence profile: `external_usage_blocker`; `rg -n "external-active|needs-user-decision" _condamad/stories/CS-059*`. |
| AC5 | Les registres restent synchronises. | Evidence profile: `allowlist_register_validated`; `npm run test -- legacy-style theme-tokens design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et classifier chaque surface legacy/alias (AC: AC1, AC4)
- [ ] Task 2 - Migrer les selectors chat eligible de `App.css` vers les CSS chat canoniques (AC: AC2)
- [ ] Task 3 - Migrer les consommateurs d'aliases vers les tokens `--color-*` avant suppression (AC: AC3)
- [ ] Task 4 - Synchroniser `legacy-style-surface-registry.md`, `token-namespace-registry.md` et allowlist executable (AC: AC5)
- [ ] Task 5 - Capturer l'after et executer les validations (AC: AC1, AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/features/chat/components/ChatComposer.css`
  - `frontend/src/features/chat/components/ChatWindow.css`
  - `frontend/src/features/chat/components/ConversationItem.css`
  - `frontend/src/features/chat/components/ConversationList.css`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/token-namespace-registry.md`
- Do not recreate:
  - selector legacy de remplacement.
  - alias compatibility equivalent.
  - registre legacy parallele.
- Shared abstraction allowed only if:
  - Elle remplace une duplication identifiee dans les CSS chat et reste dans le namespace canonique.

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

- Nouveau selector `legacy`.
- Nouvel alias `--text-*`, `--glass` ou `--primary` non classe.
- Conservation d'un selector retire via duplication dans `App.css`.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: selector or alias still has active canonical ownership.
- `external-active`: external or route-specific surface requiring decision.
- `historical-facade`: compatibility selector or alias preserving an old surface.
- `dead`: no active consumers remain.
- `needs-user-decision`: ambiguity remains after scans.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation for that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions for the audit: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-before.md`
- `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chat shell styles | `frontend/src/features/chat/components/*.css` | `frontend/src/App.css` legacy chat selectors |
| Color tokens | `--color-*` tokens | compatibility aliases non necessaires |
| Admin prompts legacy surface | `AdminPromptsPage.css` plus decision produit | deletion without decision |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving through re-export
- preserving a wrapper selector
- adding a compatibility alias
- keeping a deprecated selector active
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: no generated frontend/API artifact is expected to expose these CSS legacy selectors or token aliases.
- Required generated-contract evidence:
  - OpenAPI path absence: unchanged because CSS selectors are not API routes.
  - generated client/schema absence: unchanged because no generated client consumes selectors.
  - generated manifest absence: `npm run test -- legacy-style theme-tokens design-system` remains the executable manifest guard.

## 18. Files to Inspect First

- `frontend/src/App.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - retirer les selectors chat migrables.
- `frontend/src/features/chat/components/ChatComposer.css` - recevoir les styles canoniques du composer.
- `frontend/src/features/chat/components/ChatWindow.css` - recevoir les styles canoniques de la fenetre.
- `frontend/src/features/chat/components/ConversationItem.css` - recevoir les styles canoniques d'un item.
- `frontend/src/features/chat/components/ConversationList.css` - recevoir les styles canoniques de la liste.
- `frontend/src/styles/theme.css` - retirer les aliases sans consommateurs.
- `frontend/src/styles/token-namespace-registry.md` - synchroniser les aliases restants.
- `frontend/src/styles/legacy-style-surface-registry.md` - synchroniser les surfaces restantes.
- `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-before.md` - baseline.
- `_condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/legacy-style-after.md` - evidence finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/pages/admin/AdminPromptsPage.css` - ne doit changer que si decision utilisateur explicite existe pour `admin-prompts-legacy`.

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
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-059-retirer-selectors-legacy-aliases-compatibility-restants/00-story.md
```

## 22. Regression Risks

- Risk: suppression d'une surface admin external-active.
  - Guardrail: AC4 bloque toute deletion sans decision.
- Risk: reintroduction d'alias compatibility.
  - Guardrail: AC3 et AC5 imposent scan et guards.
- Risk: duplication des styles chat.
  - Guardrail: AC2 impose ownership chat CSS canonique.

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

- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-005` - current registry state.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
