# Story CS-071 retirer-alias-css-astrologer-card: Retirer l'alias CSS astrologer card

Status: done

## Objective

Retirer la surface active `.astrologer-card-alias` et la remplacer par un nom
canonique non legacy. Durcir le guard legacy-style pour detecter et bloquer les
selecteurs nommes `alias`. Aucun alias transitoire et aucune AC livree avec
limitation ne sont acceptables.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-001`
- Reason for change: l'audit `F-005` prouve que `.astrologer-card-alias` reste actif dans `App.css` et consomme par `AstrologerCard.tsx` sans classification registry.

## Domain Boundary

- Domain: `frontend/src/features/astrologers`
- In scope:
  - Renommer `.astrologer-card-alias` dans `frontend/src/App.css` et `frontend/src/features/astrologers/components/AstrologerCard.tsx`.
  - Mettre a jour `frontend/src/tests/legacy-style-policy.test.ts` pour detecter les selecteurs contenant `alias` meme sans `legacy`.
  - Capturer les scans before/after des surfaces `legacy`, `alias` et `--default_dropshadow`.
- Out of scope:
  - Refonte visuelle de la carte astrologue.
  - Migration globale des valeurs hardcodees.
  - Modification des donnees astrologues, routes, API ou i18n.
- Explicit non-goals:
  - Ne pas affaiblir `RG-049` ou `RG-050`.
  - Ne pas conserver `.astrologer-card-alias` dans un registre comme compatibilite approuvee.
  - Ne pas creer un nouveau selecteur contenant `legacy`, `alias`, `compat`, `shim` ou `fallback`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - tout selecteur ou alias legacy frontend restant doit etre retire ou classe; cette story impose la suppression de l'alias actif.
  - `RG-050` - la suite anti-drift design-system doit rester executable et detecter les entrees exactes.
- Non-applicable invariants:
  - `RG-044` - aucun namespace de token CSS n'est cree ou modifie.
  - `RG-045` - aucune migration de valeurs hardcodees n'est incluse.
- Required regression evidence:
  - `npm run test -- legacy-style AstrologersPage`
  - `npm run test -- design-system visual-smoke`
  - scans negatifs exacts pour `.astrologer-card-alias`, `alias`, `legacy` et `--default_dropshadow`.
- Allowed differences:
  - Renommage CSS/TSX de la classe astrologer card uniquement.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime une surface CSS alias active et route le consommateur vers un nom canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu visuel de la carte astrologue doit rester equivalent.
  - Seul le nom de classe non canonique peut changer.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un consommateur externe documente de `.astrologer-card-alias` est trouve; sinon la suppression est obligatoire.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard Vitest legacy-style est la source executable de la politique CSS. |
| Baseline Snapshot | yes | Les scans before/after prouvent la disparition de l'alias. |
| Ownership Routing | yes | Le selecteur doit etre route vers le composant canonique astrologer card. |
| Allowlist Exception | no | Aucune entree d'allowlist alias ou legacy n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route ou type public n'est modifie. |
| Batch Migration | no | La suppression concerne une seule surface CSS et son consommateur. |
| Reintroduction Guard | yes | Le retour de selecteurs alias non classes doit faire echouer le guard. |
| Persistent Evidence | yes | Les preuves before/after et validation doivent rester dans le dossier de story. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/legacy-style-policy.test.ts`
- Secondary evidence:
  - scans `rg` bornes a `frontend/src` pour `astrologer-card-alias`, `legacy`, `alias`, `--default_dropshadow`.
- Static scans alone are not sufficient for this story because:
  - le probleme initial est que le guard executable ne detecte pas tous les alias nommes.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/legacy-style-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/legacy-style-after.md`
- Expected invariant:
  - `.astrologer-card-alias` et tout nouveau selecteur `alias` non classe sont absents des surfaces actives.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Astrologer card class | `AstrologerCard.tsx` plus CSS canonique dans `App.css` | selecteur `alias` ou registre legacy |
| Legacy/alias policy guard | `frontend/src/tests/legacy-style-policy.test.ts` | scan partiel limite au mot `legacy` |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: this story authorizes no allowlist entries.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before alias scan | `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/legacy-style-before.md` | Prouver l'etat initial de l'alias et du guard. |
| After alias scan | `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/legacy-style-after.md` | Prouver la disparition de l'alias et le durcissement du guard. |
| Final validation evidence | `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/generated/10-final-evidence.md` | Persist commands, results and residual risks. |

## Reintroduction Guard

- The implementation must add or update an architecture guard against reintroduction:
  `legacy-style-policy.test.ts` must fail if an active CSS selector contains
  `legacy` or `alias` and is reintroduced without exact allowed classification.
- Deterministic source: forbidden symbols extracted from active CSS selectors.
- Deterministic source: CSS selector extraction from `frontend/src/**/*.css`.
- Required forbidden examples:
  - `.astrologer-card-alias`
  - any new active selector containing `alias` outside an exact registry rule, if the implementation keeps any registry support
  - `--default_dropshadow`
- Guard evidence:
  - Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0932/01-evidence-log.md#E-015`
  - `.astrologer-card-alias` is present in `frontend/src/App.css` and consumed by `AstrologerCard.tsx`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-0932/01-evidence-log.md#E-016` - `legacy-style-surface-registry.md` has no classification row for the alias.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - `RG-049` and `RG-050` consulted before story scope was finalized.

## Target State

- `.astrologer-card-alias` has zero active hits under `frontend/src`.
- `AstrologerCard.tsx` uses a canonical class name that does not contain legacy/alias vocabulary.
- `legacy-style-policy.test.ts` blocks future alias-named CSS selectors with deterministic evidence.
- All validation evidence is final, with no `PASS with limitation`.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before artifact records alias hit. | Evidence profile: `baseline_before_after_diff`; capture AC1 `rg` command from Validation Plan. |
| AC2 | `.astrologer-card-alias` is deleted. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "astrologer-card-alias" src` returns zero. |
| AC3 | Replacement class preserves rendering contract. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage visual-smoke` and lint. |
| AC4 | Alias-named selectors cannot bypass policy. | Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style` covers `alias`. |
| AC5 | No touched legacy/alias/drop-shadow token remains. | Evidence profile: `repo_wide_negative_scan`; AC5 `rg` command in Validation Plan returns zero. |
| AC6 | Final evidence has no limitation language. | Evidence profile: `persistent_evidence`; AC6 story-folder `rg` scan returns zero. |

## Implementation Tasks

- [x] Task 1 - Capture before evidence for the alias surface and guard gap. (AC: AC1)
- [x] Task 2 - Rename the CSS selector and TSX consumer to canonical vocabulary. (AC: AC2, AC3)
- [x] Task 3 - Strengthen `legacy-style-policy.test.ts` so alias-named selectors are detected. (AC: AC4)
- [x] Task 4 - Capture after evidence and exact negative scans. (AC: AC2, AC5, AC6)
- [x] Task 5 - Run focused frontend tests, lint and story validation. (AC: AC3, AC4, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse the existing CSS selector extraction helpers in `frontend/src/tests/legacy-style-policy.test.ts`.
- Reuse existing astrologer card markup and styling; do not introduce a duplicate component.
- Do not create a new registry allowlist entry for this alias.

## No Legacy / Forbidden Paths

- Forbidden: `.astrologer-card-alias`.
- Forbidden: new selectors containing `legacy`, `alias`, `compat`, `shim` or `fallback` in the touched component.
- Forbidden: compatibility wrappers, transitional aliases, fallback CSS, duplicate active selectors, or preserving old paths through comments/tests as nominal runtime behavior.

## Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: the canonical replacement selector in `AstrologerCard.tsx`.
- `external-active`: any documented external consumer of `.astrologer-card-alias`; must block deletion if found.
- `historical-facade`: `.astrologer-card-alias`, if it only preserves old vocabulary.
- `dead`: any alias selector with zero active consumers.
- `needs-user-decision`: unresolved external usage after required scans.

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

- `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/legacy-style-after.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Astrologer card name display styling | `frontend/src/features/astrologers/components/AstrologerCard.tsx` with canonical CSS in `frontend/src/App.css` | `.astrologer-card-alias` |
| Legacy/alias style policy | `frontend/src/tests/legacy-style-policy.test.ts` | unguarded alias selector scans |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving `.astrologer-card-alias` as a wrapper
- adding a compatibility alias
- keeping a deprecated selector active
- preserving the old selector through re-export
- replacing deletion with soft-disable behavior

## External Usage Blocker

If `.astrologer-card-alias` is `external-active`, it must not be deleted
without explicit evidence and user decision. Otherwise, this story requires
deletion of the alias.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path is added, removed or renamed by this frontend CSS story.
- Generated client/schema absence: no generated client, generated schema or generated manifest is affected.
- Route manifest absence: no frontend route manifest or route path is changed.
- Required evidence: `git diff -- frontend/src/App.css frontend/src/features/astrologers/components/AstrologerCard.tsx`
  plus the guard test diff remains limited to CSS class rename and guard hardening.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-0932/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md`
- `frontend/src/App.css`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/legacy-style-policy.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/App.css` - rename the selector.
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - consume the canonical selector.
- `frontend/src/tests/legacy-style-policy.test.ts` - detect alias-named selectors.

Likely tests:
- `frontend/src/tests/legacy-style-policy.test.ts`
- existing focused astrologer page tests if present after inspection.

Files not expected to change:
- `backend/app/main.py` - no backend behavior is in scope.
- `frontend/package.json` - no dependency or script change is required.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- legacy-style AstrologersPage
npm run test -- design-system visual-smoke
npm run lint
rg -n "astrologer-card-alias" src -g "*.css" -g "*.tsx" -g "*.ts"
rg -n "\.([a-zA-Z0-9_-]*(legacy|alias)[a-zA-Z0-9_-]*)|--default_dropshadow" src -g "*.css" -g "*.tsx" -g "*.ts"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-071-retirer-alias-css-astrologer-card/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: the guard keeps checking only `legacy` and misses alias vocabulary again.
  - Guardrail: `RG-049`, `npm run test -- legacy-style`, and alias-specific negative scan.
- Risk: a visual regression is introduced by selector rename.
  - Guardrail: focused `AstrologersPage` and `visual-smoke` tests.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-001`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/02-finding-register.md#F-005`
- `_condamad/stories/regression-guardrails.md`
