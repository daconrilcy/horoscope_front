# Story CS-070 retirer-vocabulaire-legacy-admin-prompts-runtime: Retirer le vocabulaire legacy runtime admin prompts

Status: done

## Objective

Supprimer le concept runtime et produit `legacy` restant dans Admin Prompts.
Le vocabulaire cible est une surface canonique archive/history, sans alias ni import legacy.
Aucune AC livrable avec limitation n'est acceptable.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-003`
- Reason for change: Admin Prompts utilisait encore le vocabulaire runtime legacy.

## Domain Boundary

- Domain: `frontend/src/pages/admin`
- In scope:
  - Renommer le tab/state/copy admin prompts `legacy` vers un vocabulaire archive/history canonique.
  - Renommer ou supprimer `frontend/src/i18n/adminPromptsLegacy.ts` sans re-export ni alias compatibility.
  - Mettre a jour `AdminPromptsPage.tsx`, `admin.ts`, tests et ARIA labels dans le meme changement.
  - Capturer before/after scan de `AdminPromptsPage.tsx`, `adminPromptsLegacy.ts`, `admin.ts`, et `AdminPromptsPage.test.tsx`.
- Out of scope:
  - Refonte fonctionnelle Admin Prompts.
  - Changement backend/API prompts.
  - Migration globale des tokens compatibility, couverte par `CS-068`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-049` ou `RG-050`.
  - Ne pas conserver `legacy` comme vocabulary product-approved.
  - Ne pas garder de shim `adminPromptsLegacy`, alias de tab, fallback de route, ou compat import.

## Regression Guardrails

- Applicable invariants:
  - `RG-049` - legacy style/product surfaces must remain owned, classified, and removable by condition.
  - `RG-050` - design-system anti-drift guards must stay executable.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes a runtime legacy facade and replaces product copy with the canonical archive/history vocabulary.
- Behavior change allowed: constrained
- Behavior change constraints:
  - User-visible vocabulary may change from legacy to archive/history.
  - Admin Prompts routing, data loading, permissions and business behavior must remain unchanged.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: an external-active consumer still requires the `legacy` vocabulary or the canonical archive/history term is rejected.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests AdminPrompts prouvent route, labels et ARIA. |
| Baseline Snapshot | yes | Les scans before/after prouvent la disparition. |
| Ownership Routing | yes | Le vocabulaire runtime doit etre route vers l'owner archive canonique. |
| Allowlist Exception | no | Aucun alias ou exception legacy n'est autorise. |
| Contract Shape | no | Aucun contrat API, DTO ou serialization n'est modifie. |
| Batch Migration | no | Le changement porte sur une surface Admin Prompts bornee, pas sur un lot multi-cluster. |
| Reintroduction Guard | yes | Le vocabulaire retire ne doit pas revenir. |
| Persistent Evidence | yes | Les scans before/after et preuves finales doivent rester consultables. |

## Runtime Source of Truth

- Primary source of truth: runtime tests and AST guard coverage in:
  - `frontend/src/tests/AdminPromptsPage.test.tsx`
  - `frontend/src/tests/AdminPromptsRouting.test.tsx`
  - `frontend/src/tests/legacy-style-policy.test.ts`
- Secondary evidence: targeted scans over `frontend/src/pages/admin/AdminPromptsPage.tsx`, `frontend/src/i18n`, and Admin Prompts tests.
- Static scans alone are not sufficient: executable evidence is required through `npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style design-system`.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-070-retirer-vocabulaire-legacy-admin-prompts-runtime/admin-prompts-legacy-before.md`.
- Comparison after implementation: `_condamad/stories/CS-070-retirer-vocabulaire-legacy-admin-prompts-runtime/admin-prompts-legacy-after.md`.
- Expected invariant: every `legacy` Admin Prompts runtime symbol is deleted or replaced by archive/history vocabulary without alias, compatibility fallback, or re-export.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin Prompts archive tab/state | `frontend/src/pages/admin/AdminPromptsPage.tsx` archive/history state | `legacy` tab/state value |
| Admin Prompts archive copy | `frontend/src/i18n/adminPromptsArchive.ts` and `frontend/src/i18n/admin.ts` | `adminPromptsLegacy.ts`, `promptsLegacy`, compatibility import |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: no legacy vocabulary exception or allowlist is allowed for this story.

## Contract Shape

- Contract Shape: not applicable
- Reason: no generated API, DTO, HTTP status, serialization name, or frontend data contract is changed.

## Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: this is a bounded legacy facade removal, not a batch migration archetype.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before legacy vocabulary baseline | `admin-prompts-legacy-before.md` | Classify existing Admin Prompts legacy symbols before removal. |
| After archive vocabulary evidence | `admin-prompts-legacy-after.md` | Prove removed runtime vocabulary and absence of limitations. |
| Final validation evidence | `generated/10-final-evidence.md` | Persist commands, results and residual risks. |

## Reintroduction Guard

- Architecture guard: forbidden Admin Prompts legacy symbols must fail if reintroduced.
- Deterministic source: forbidden symbols `adminPromptsLegacy`, `AdminPromptsLegacyStrings`, `adminPromptsLegacyByLang`, `promptsLegacy`, and tab/state value `legacy`.
- Evidence profile: `reintroduction_guard`; command `npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style design-system`.
- Additional executable evidence: targeted `rg` scans in the Validation Plan must remain clean.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-003` - audit source for the remaining Admin Prompts legacy vocabulary.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - shared guardrails for legacy surfaces and executable design guards.

## Target State

- Admin Prompts utilise `archive/history` en runtime, i18n, labels, ARIA et tests.
- Aucun shim ou import `adminPromptsLegacy` ne reste actif.
- Le vocabulaire `legacy` n'est plus accepte comme surface produit Admin Prompts.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before artifact classifies `legacy` occurrences. | Evidence profile: `baseline_snapshot`; `rg -n "unclassified" admin-prompts-legacy-before.md` returns zero hits. |
| AC2 | Runtime drops `legacy`. | Evidence profile: `runtime_guard`; AST guard plus `npm run test -- AdminPromptsPage`. |
| AC3 | I18n uses archive/history vocabulary. | Evidence profile: `ownership_routing`; `rg -n "promptsLegacy" src/i18n` returns zero hits. |
| AC4 | AdminPrompts tests assert canonical vocabulary. | Evidence profile: `runtime_guard`; `npm run test -- AdminPromptsPage AdminPromptsRouting`. |
| AC5 | Reintroduction is guarded. | Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style design-system`. |
| AC6 | The after artifact has no limitation. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation" admin-prompts-legacy-after.md` returns zero hits. |

## Implementation Tasks

- [ ] Task 1 - Capture before scan and removal audit for Admin Prompts legacy vocabulary. (AC: AC1)
- [ ] Task 2 - Rename tab/state/type/import ownership from legacy to archive/history. (AC: AC2)
- [ ] Task 3 - Rename or delete i18n legacy module without shim or re-export. (AC: AC3)
- [ ] Task 4 - Update visible copy, ARIA labels and AdminPrompts tests. (AC: AC4)
- [ ] Task 5 - Update legacy/design-system guard expectations. (AC: AC5)
- [ ] Task 6 - Capture after evidence and run validation. (AC: AC2, AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse the existing Admin Prompts page and i18n aggregation.
- Do not add a compatibility route or alias.
- Do not duplicate archive/history strings in component logic.

## No Legacy / Forbidden Paths

- Forbidden compatibility fallback vocabulary and legacy imports:
  - `frontend/src/i18n/adminPromptsLegacy.ts`
  - `AdminPromptsLegacyStrings`
  - `adminPromptsLegacyByLang`
  - `promptsLegacy`
  - Admin Prompts tab/state value `legacy`.
- Forbidden: wrapper, fallback, alias, or re-export preserving old legacy vocabulary.

## Removal Classification Rules

- `canonical-active`: archive/history vocabulary after rename.
- `external-active`: public or generated consumer still requires legacy vocabulary and blocks deletion.
- `historical-facade`: legacy file/import/type/state/label/test expectation.
- `dead`: unused legacy vocabulary with zero consumers.
- `needs-user-decision`: ambiguity remains after scans and must block implementation.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `delete`, `keep`, `replace-consumer`, `needs-user-decision`.
Persisted audit artifact: `_condamad/stories/CS-070-retirer-vocabulaire-legacy-admin-prompts-runtime/admin-prompts-legacy-after.md`.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin prompts archive tab | `AdminPromptsPage.tsx` | legacy tab/state |
| Admin prompts archive copy | `adminPromptsArchive.ts` and `admin.ts` | `adminPromptsLegacy.ts`, `promptsLegacy` |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden replacements include preserving a wrapper, adding a compatibility alias, preserving the old path through re-export, or replacing deletion with fallback vocabulary.

## External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.
The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path is added, removed or renamed by this Admin Prompts vocabulary story.
- Generated client/schema absence: no generated client, generated schema or generated manifest is affected.
- Required evidence: `git diff -- frontend` remains limited to Admin Prompts frontend/i18n/tests and no generated API artifact is changed.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-0806/01-evidence-log.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/i18n/adminPromptsLegacy.ts`
- `frontend/src/i18n/admin.ts`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-removal-audit.md`

## Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/i18n/admin.ts`
- `frontend/src/i18n/adminPromptsArchive.ts`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`

Likely tests:
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/legacy-style-policy.test.ts`

Files not expected to change:
- `backend/app/main.py`
- `frontend/package.json`

## Dependency Policy

- New dependencies: none.
- Justification: no dependency change is required.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style design-system
npm run lint
rg -n "adminPromptsLegacy" src/pages/admin/AdminPromptsPage.tsx src/i18n src/tests/AdminPromptsPage.test.tsx
rg -n "AdminPromptsLegacyStrings" src/pages/admin/AdminPromptsPage.tsx src/i18n src/tests/AdminPromptsPage.test.tsx
rg -n "promptsLegacy" src/pages/admin/AdminPromptsPage.tsx src/i18n src/tests/AdminPromptsPage.test.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-070-retirer-vocabulaire-legacy-admin-prompts-runtime/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-070-retirer-vocabulaire-legacy-admin-prompts-runtime/00-story.md
```

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not keep compatibility exports, aliases, or fallback vocabulary.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Hidden compatibility enum accepts `legacy`.
- Tests keep legacy vocabulary as nominal.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-003`
- `_condamad/stories/regression-guardrails.md`
