# Story CS-063 retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants: Retirer les selectors legacy admin prompts et aliases compatibility restants

Status: ready-to-dev

## Objective

Retirer ou reduire les selectors legacy admin prompts et aliases compatibility restants du design-system frontend.
La migration doit separer la route admin prompts des aliases globaux, et bloquer toute suppression `external-active` sans decision explicite.

## Source

- Audit: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-004`
- Finding: F-005

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-004`
- Reason for change: réduire les surfaces legacy et aliases compatibility restants.

## Domain Boundary

- Domain: `frontend/src/styles`

In scope:
- Classer les selectors admin prompts et aliases restants.
- Supprimer seulement les surfaces sans consommation active.

Out of scope:
- Suppression de surfaces `external-active` sans décision.
- Migration globale de `App.css`.

Explicit non-goals:
- Ne pas affaiblir `RG-044`, `RG-049` ou `RG-050`.
- Ne pas créer de selector compatibility de remplacement.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Behavior change allowed: constrained
- Deletion allowed: yes
- Replacement allowed: no

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | legacy-style/theme/design-system guards |
| Baseline Snapshot | yes | before/after requis |
| Ownership Routing | yes | registres legacy et tokens |
| Allowlist Exception | yes | surfaces external-active exactes |

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-004`.
- Evidence 2: `frontend/src/styles/legacy-style-surface-registry.md`.
- Evidence 3: `_condamad/stories/regression-guardrails.md`.

## Target State

- Les surfaces supprimables sont retirées.
- Les surfaces external-active restent bloquées et documentées.

## Scope

In scope:
- Separer migration markup/style admin prompts et retrait des aliases globaux.
- Retirer `.admin-prompts-legacy*` seulement si le markup canonique existe.
- Retirer les aliases `--text-*`, `--glass*` et `--primary*` seulement apres migration des consommateurs vers `--color-*`.
- Synchroniser `legacy-style-surface-registry.md`, `token-namespace-registry.md` et les tests.

Out of scope:
- Suppression de surfaces `external-active` sans decision utilisateur.
- Refonte fonctionnelle AdminPrompts.
- Migration des hardcoded values, fallbacks CSS ou styles inline hors surfaces touchees.

## Regression Guardrails

- `RG-044`: les namespaces de tokens restent classes.
- `RG-049`: les surfaces legacy restent owned, classees et avec sortie.
- `RG-050`: les guards design-system restent executables.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe chaque famille legacy/alias restante. | `npm run test -- legacy-style` et inventaire before. |
| AC2 | Les selectors admin prompts ne sont retires que si le markup canonique existe. | `npm run test -- AdminPromptsPage`. |
| AC3 | Les aliases retires n'ont plus de consommateurs. | scan `rg -n "legacy|--text-|--glass|--primary" src`. |
| AC4 | Les surfaces external-active restent bloquees. | evidence dans `legacy-style-after.md`. |
| AC5 | Les registres restent synchronises. | `npm run test -- legacy-style theme-tokens design-system`. |

## Validation Plan

```powershell
Push-Location frontend
npm run test -- legacy-style theme-tokens design-system AdminPromptsPage
npm run lint
rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-063-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-063-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/00-story.md
```

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline.
- [ ] Task 2 - Classer les surfaces.
- [ ] Task 3 - Supprimer uniquement les surfaces sans consommateur actif.
- [ ] Task 4 - Valider.

## Removal Classification Rules

- `canonical-active`: garder.
- `external-active`: garder ou bloquer sans décision utilisateur.
- `historical-facade`: supprimer si aucun consommateur actif.
- `dead`: supprimer.
- `needs-user-decision`: bloquer.

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles admin prompts | `AdminPromptsPage.css` canonique | selectors legacy |
| Tokens couleur | `--color-*` | aliases compatibility |

## Delete-Only Rule

- Ne pas remplacer un selector legacy par un alias équivalent.
- Ne pas conserver une surface retirée via duplication.

## External Usage Blocker

- Toute surface `external-active` reste bloquée sans décision utilisateur explicite.

## Reintroduction Guard

- `npm run test -- legacy-style theme-tokens design-system AdminPromptsPage`
- scan `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css`

## Generated Contract Check

- Aucun contrat API ou client généré n'est modifié.

## Mandatory Reuse / DRY Constraints

- Réutiliser `legacy-style-surface-registry.md` et `token-namespace-registry.md`.
- Ne pas créer de registre parallèle.

## No Legacy / Forbidden Paths

- Aucun nouveau selector `legacy`.
- Aucun nouvel alias compatibility.

## Files to Inspect First

- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/styles/token-namespace-registry.md`

## Expected Files to Modify

Likely files:
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/styles/token-namespace-registry.md`

Likely tests:
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

Files not expected to change:
- `backend/`

## Dependency Policy

- New dependencies: none.

## Regression Risks

- Risque: suppression d'une surface external-active.
- Garde: blocage documenté et tests legacy-style.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, record the blocker.
- Do not preserve legacy behavior for convenience.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-004`
- `_condamad/stories/regression-guardrails.md`
