# Story CS-067 retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants: Retirer les selectors legacy admin prompts et aliases compatibility restants

Status: ready-to-dev

## Objective

Retirer ou reduire les selectors legacy admin prompts et aliases compatibility restants sans contourner No Legacy.
La migration separe la route admin prompts des aliases `--text-*`, `--glass*` et `--primary*`.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-004`
- Reason for change: faire progresser l'extinction des surfaces CSS legacy et aliases compatibility restants.

## Domain Boundary

- Domain: `frontend/src/styles`
In scope:
- Classer les selectors `.admin-prompts-legacy*` et `.admin-prompts-modal--legacy-rollback` avant toute suppression.
- Migrer le markup/style admin prompts uniquement si une surface canonique route-specific existe.
- Retirer les aliases `--text-*`, `--glass*` et `--primary*` uniquement apres migration des consommateurs vers `--color-*`.
- Synchroniser `legacy-style-surface-registry.md`, `token-namespace-registry.md` et les guards.

Out of scope:
- Suppression de surfaces `external-active` sans decision utilisateur explicite.
- Refonte fonctionnelle d'AdminPrompts.
- Migration generale de `App.css` ou des valeurs hardcodees hors aliases ciblees.

Explicit non-goals:
  - Ne pas changer `RG-044`, `RG-049` ou `RG-050`.
  - Ne pas remplacer un selector legacy par un nouveau selector compatibility.
  - Ne pas garder une surface retiree via alias, wrapper, re-export ou duplication.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime ou bloque des surfaces compatibility/legacy au profit d'owners canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les comportements admin prompts existants doivent rester fonctionnels lorsque les surfaces sont `external-active`.
  - Les aliases ne peuvent disparaitre que si tous les consommateurs actifs utilisent les tokens canoniques `--color-*`.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: legacy admin prompts reste consomme, ou si un alias compatibility a des consommateurs externes non migrables.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les guards legacy/theme/design-system prouvent les surfaces actives |
| Baseline Snapshot | yes | un audit before/after des selectors et aliases est requis |
| Ownership Routing | yes | chaque surface legacy doit pointer vers un owner canonique |
| Allowlist Exception | no | `legacy-facade-removal` ne requiert pas ce contrat; les registres legacy/token restent exigés par AC |
| Contract Shape | no | aucun type/API/DTO ou client genere n'est modifie |
| Batch Migration | no | la story est une suppression/classification legacy, pas une migration par lots independants |
| Reintroduction Guard | yes | les guards doivent echouer si les surfaces retirees reviennent |
| Persistent Evidence | yes | l'audit de classification doit rester dans le dossier de story |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/legacy-style-policy.test.ts` execute par Vitest.
  - AST guard `frontend/src/tests/theme-tokens.test.ts` execute par Vitest.
  - `frontend/src/tests/legacy-style-policy.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/token-namespace-registry.md`
- Secondary evidence:
  - scans `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css`.
- Static scans alone are not sufficient for this story because:
  - les surfaces `external-active` doivent etre preservees ou bloquees selon registre, pas seulement supprimees au grep.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-style-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-style-after.md`
- Expected invariant:
  - aucune surface `external-active` n'est supprimee sans decision; les registres restent synchronises avec le code.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin prompts route styles | canonical route-specific markup | `.admin-prompts-legacy*` compatibility |
| Text color tokens | `--color-text-*` in canonical token source | aliases `--text-*` as active consumers |
| Glass tokens | `--color-glass-*` in canonical token source | aliases `--glass*` as active consumers |
| Primary tokens | `--color-primary*` in canonical token source | aliases `--primary*` as active consumers |

## Allowlist / Exception Register

- Allowlist exception contract: not applicable
- Reason: no separate allowlist register is created; the canonical exception registries are `legacy-style-surface-registry.md` and `token-namespace-registry.md`, validated by AC5.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

- Batch migration: not applicable
- Reason: this is a legacy-facade removal/classification story; consumer migration is a blocker condition, not a silent compatibility batch.

## Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| legacy baseline | `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-style-before.md` | classer avant suppression |
| legacy result | `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-style-after.md` | prouver resultats et blocages |
| removal audit | `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-removal-audit.md` | table de classification No Legacy |

## Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `.admin-prompts-legacy*` quand la famille est classee supprimable.
- `.admin-prompts-modal--legacy-rollback` quand la surface est classee supprimable.
- `--text-*`, `--glass*`, `--primary*` comme aliases actifs apres migration de leurs consommateurs.
- deterministic source: forbidden symbols.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style theme-tokens design-system AdminPromptsPage` checks legacy selectors, aliases and registries.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-004` - le candidat signale les blockers `external-active`.
- Evidence 2: `frontend/src/styles/legacy-style-surface-registry.md` - classe `.admin-prompts-legacy*` et `.admin-prompts-modal--legacy-rollback` comme `external-active`.
- Evidence 3: `frontend/src/styles/token-namespace-registry.md` - classe `--text-*`, `--glass*` et `--primary*` comme compatibility.
- Evidence 4: `frontend/src/pages/admin/AdminPromptsPage.tsx` - consomme encore des classes et libelles legacy admin prompts.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants `RG-044`, `RG-049` et `RG-050` consultes avant cadrage.

## Target State

- Chaque selector legacy et alias compatibility restant est garde, supprime ou bloque avec classification deterministe.
- Les surfaces supprimables sont supprimees, pas repointees.
- Les registres legacy/token et les tests design-system restent exacts.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens doivent rester classes.
  - `RG-049` - les surfaces CSS legacy doivent rester owned, classees et avec condition de sortie.
  - `RG-050` - les guards anti-drift design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline ne sont pas dans le scope.
  - `RG-048` - les fallbacks CSS ne sont pas dans le scope.
- Required regression evidence:
  - `npm run test -- legacy-style theme-tokens design-system AdminPromptsPage`
  - scan cible `legacy|--text-|--glass|--primary`.
- Allowed differences:
  - les surfaces legacy ou aliases peuvent diminuer; les surfaces `external-active` non tranchees doivent rester documentees.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe les surfaces legacy. | Evidence profile: `external_usage_blocker`; `npm run test -- legacy-style` + `legacy-removal-audit.md` |
| AC2 | Les selectors admin legacy sortent apres migration markup. | Evidence profile: `no_legacy_contract`; `npm run test -- AdminPromptsPage` + scan legacy |
| AC3 | Les aliases compatibility sortent apres migration. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "--text-|--glass" src` + theme test |
| AC4 | Toute surface `external-active` non migrable bloque. | Evidence profile: `external_usage_blocker`; `npm run test -- legacy-style` + after artifact |
| AC5 | Les registres restent synchronises. | Evidence profile: `allowlist_register_validated`; `npm run test -- legacy-style theme-tokens design-system` |
| AC6 | Aucun doublon legacy n'est cree. | Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style design-system` + scan |

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline des selectors legacy et aliases compatibility. (AC: AC1)
- [ ] Task 2 - Classer chaque item dans `legacy-removal-audit.md` avec consommateurs, preuve et decision. (AC: AC1, AC4)
- [ ] Task 3 - Migrer ou bloquer la surface admin prompts selon existence du markup canonique. (AC: AC2, AC4)
- [ ] Task 4 - Migrer ou bloquer les aliases token selon consommation `--color-*`. (AC: AC3, AC4)
- [ ] Task 5 - Synchroniser les registres legacy/token et executer les guards. (AC: AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/legacy-style-surface-registry.md` pour les surfaces legacy.
  - `frontend/src/styles/token-namespace-registry.md` pour les aliases token.
  - `frontend/src/tests/legacy-style-policy.test.ts`, `theme-tokens.test.ts` et `design-system-guards.test.ts`.
- Do not recreate:
  - un second registre legacy.
  - des aliases `--text-*`, `--glass*`, `--primary*` sous un autre nom compatibility.
- Shared abstraction allowed only if:
  - non attendu; cette story doit supprimer ou bloquer, pas abstraire.

## No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- nouveau selector contenant `legacy`.
- nouvel alias compatibility vers `--color-*`.
- conservation d'un selector retire via duplication sous un autre nom.

## Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item referenced by first-party production code or canonical owner.
- `external-active`: item referenced by docs, generated links, explicit audit evidence or active route markup.
- `historical-facade`: compatibility surface preserving an old selector or token alias.
- `dead`: zero production/test/doc/registry consumers after scans.
- `needs-user-decision`: ambiguity remains after required scans.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-removal-audit.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin prompts route styles | `frontend/src/pages/admin/AdminPromptsPage.css` canonical selectors | `.admin-prompts-legacy*`, `.admin-prompts-modal--legacy-rollback` |
| Text colors | `--color-text-*` tokens | `--text-*` aliases |
| Glass colors | `--color-glass-*` tokens | `--glass*` aliases |
| Primary colors | `--color-primary*` tokens | `--primary*` aliases |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- wrapper
- redirecting a selector to a canonical selector through duplication
- preserving a wrapper selector
- adding a compatibility alias
- keeping a deprecated class active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior
- re-export

## External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## Generated Contract Check

Required generated-contract evidence:

- generated artifact absence: no removed legacy selector appears in any generated route manifest, snapshot, public style contract, or generated client if such artifact exists.
- OpenAPI path absence: CSS selectors do not expose API paths; the implementation must record that no API OpenAPI surface was touched.
- generated client/schema absence: no frontend generated client or schema should mention removed selectors or aliases.

## Files to Inspect First

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/App.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

## Expected Files to Modify

Likely files:

- `frontend/src/pages/admin/AdminPromptsPage.tsx` - only if legacy route markup is migrated.
- `frontend/src/pages/admin/AdminPromptsPage.css` - remove or keep selectors according to classification.
- `frontend/src/App.css` - migrate alias consumers only if in scope and safely bounded.
- `frontend/src/styles/theme.css` - retire aliases only after consumers migrate.
- `frontend/src/styles/token-namespace-registry.md` - update alias status/exit condition.
- `frontend/src/styles/legacy-style-surface-registry.md` - update legacy selector classification.
- `frontend/src/tests/legacy-style-policy.test.ts` - keep guard exact.
- `frontend/src/tests/theme-tokens.test.ts` - keep token guard exact.
- `frontend/src/tests/design-system-guards.test.ts` - keep registry guard exact.

Likely tests:

- `frontend/src/tests/AdminPromptsPage.test.tsx` - route-specific behavior.
- `frontend/src/tests/legacy-style-policy.test.ts` - legacy registry guard.
- `frontend/src/tests/theme-tokens.test.ts` - alias/token guard.
- `frontend/src/tests/design-system-guards.test.ts` - anti-drift guard.

Files not expected to change:

- `backend/` - aucun contrat backend n'est touche.
- `frontend/src/tests/inline-style-allowlist.ts` - styles inline hors scope.
- `frontend/src/styles/css-fallback-allowlist.md` - fallbacks CSS hors scope.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- legacy-style theme-tokens design-system AdminPromptsPage
npm run lint
rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py `
  _condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict `
  _condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/00-story.md
```

## Regression Risks

- Risk: suppression d'une surface admin prompts encore `external-active`.
  - Guardrail: classification audit + AC4 blocker.
- Risk: retrait d'un alias token encore consomme par `App.css`.
  - Guardrail: scan cible et `npm run test -- theme-tokens`.
- Risk: remplacement d'un legacy selector par une compatibility cachee.
  - Guardrail: delete-only rule et scan `legacy|--text-|--glass|--primary`.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-004` - source du candidat.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-044`, `RG-049`, `RG-050`.
- `frontend/src/styles/legacy-style-surface-registry.md` - registre legacy.
- `frontend/src/styles/token-namespace-registry.md` - registre token namespace.
