# Story CS-072 retirer-libelles-legacy-consultations: Retirer les libelles legacy consultations

Status: done

## Objective

Retirer le vocabulaire utilisateur `(Legacy)` des libelles de consultation et
adapter les tests au libelle canonique final. La decision produit est deja
prise par l'utilisateur: aucun legacy ne doit rester, aucune compatibilite
approuvee n'est autorisee, et aucune AC ne peut etre livree en
`PASS with limitation`.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-002`
- Reason for change: l'audit `F-006` montre que `frontend/src/i18n/consultations.ts` expose encore des libelles `(Legacy)` visibles utilisateur.

## Domain Boundary

- Domain: `frontend/src/i18n`
- In scope:
  - Renommer les libelles de consultation dans `frontend/src/i18n/consultations.ts` pour supprimer `(Legacy)` dans toutes les langues.
  - Ajouter ou mettre a jour la couverture ciblee de consultation i18n.
  - Prouver zero vocabulaire `legacy` actif sur la surface consultation.
- Out of scope:
  - Modifier les types de consultation, routes, stockage, API ou logique de generation.
  - Refonte UX du parcours consultation.
  - Nettoyage de commentaires historiques hors surface runtime active.
- Explicit non-goals:
  - Ne pas affaiblir `RG-049` ou `RG-050`.
  - Ne pas conserver des libelles legacy comme compatibilite approuvee.
  - Ne pas changer les cles i18n ou valeurs metier si un renommage de texte suffit.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - les surfaces legacy frontend doivent etre retirees ou classifiees; ici la decision utilisateur interdit la classification legacy.
  - `RG-050` - les guards design-system et anti-drift doivent rester executables.
- Non-applicable invariants:
  - `RG-044` - aucun namespace de token CSS n'est modifie.
  - `RG-047` - aucun style inline TSX n'est touche.
- Required regression evidence:
  - `npm run test -- ConsultationMigration consultationStore`
  - `npm run test -- design-system legacy-style`
  - scan negatif de `legacy|Legacy` dans `frontend/src/i18n/consultations.ts`.
- Allowed differences:
  - Suppression de la mention `(Legacy)` dans les libelles utilisateur.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime une surface de vocabulaire legacy visible utilisateur.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les ids, categories, valeurs de formulaire et comportements de consultation restent inchanges.
  - Seuls les textes affiches perdent la mention `(Legacy)`.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une autre decision produit demande explicitement de conserver un libelle legacy; la decision courante impose zero legacy.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests i18n/store prouvent les libelles consommes par le frontend. |
| Baseline Snapshot | yes | Les scans before/after prouvent le retrait du vocabulaire legacy. |
| Ownership Routing | yes | Les libelles consultation restent sous l'owner i18n canonique. |
| Allowlist Exception | no | Aucune entree d'allowlist pour vocabulaire legacy n'est autorisee. |
| Contract Shape | no | Aucun payload, DTO, API ou schema genere n'est modifie. |
| Batch Migration | no | La migration est bornee au fichier i18n consultation. |
| Reintroduction Guard | yes | Le retour de `legacy` dans consultation i18n doit etre detecte. |
| Persistent Evidence | yes | Les scans et resultats doivent etre persistants. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard or focused Vitest test ciblant la consommation de `frontend/src/i18n/consultations.ts`, existant ou nouveau.
- Secondary evidence:
  - scan `rg -n "legacy|Legacy" src/i18n/consultations.ts`.
- Static scans alone are not sufficient for this story because:
  - les tests doivent prouver que le rendu/choix consultation consomme toujours les libelles canoniques.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-072-retirer-libelles-legacy-consultations/consultation-labels-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-072-retirer-libelles-legacy-consultations/consultation-labels-after.md`
- Expected invariant:
  - les cles metier consultation restent stables; seules les mentions `(Legacy)` disparaissent.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Consultation labels | `frontend/src/i18n/consultations.ts` | libelles legacy, copie compatibility, duplicat local dans composant |
| Consultation label tests | focused i18n or consultation migration test under `frontend/src/tests` | assertions encodees comme comportement legacy nominal |

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
| Before consultation vocabulary scan | `_condamad/stories/CS-072-retirer-libelles-legacy-consultations/consultation-labels-before.md` | Documenter les libelles legacy initiaux. |
| After consultation vocabulary scan | `consultation-labels-after.md` | Prouver zero legacy actif dans consultation i18n. |
| Final validation evidence | `_condamad/stories/CS-072-retirer-libelles-legacy-consultations/generated/10-final-evidence.md` | Persist commands, results and residual risks. |

## Reintroduction Guard

- The implementation must add or update an architecture guard against reintroduction:
  a focused test or existing consultation migration test must fail if `(Legacy)`
  is reintroduced in consultation labels.
- Deterministic source: forbidden symbols extracted from `frontend/src/i18n/consultations.ts`.
- Deterministic source: `frontend/src/i18n/consultations.ts`.
- Required forbidden examples:
  - `(Legacy)`
  - `Legacy`
  - `legacy`
- Guard evidence:
  - Evidence profile: `reintroduction_guard`; `npm run test -- ConsultationMigration consultationStore`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0932/01-evidence-log.md#E-017` - `legacy|Legacy` remains in `frontend/src/i18n/consultations.ts`.
- Evidence 2: `frontend/src/i18n/consultations.ts` - lines with `(Legacy)` exist for dating, professional choice, important event and free question labels.
- Evidence 3: user decision on 2026-05-06 - "Aucun legacy ne doit rester" and "Aucune AC ne doit rester en PASS with limitation apres implementation".
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-049` and `RG-050` consulted before story scope was finalized.

## Target State

- `frontend/src/i18n/consultations.ts` has zero active `legacy|Legacy` hits.
- Consultation choices keep the same identifiers and behavior.
- Tests assert the final non-legacy labels.
- Final evidence has no limitation or deferred decision.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before artifact records every `(Legacy)` consultation label. | Evidence profile: `baseline_before_after_diff`; capture `rg -n "legacy\|Legacy" src/i18n/consultations.ts`. |
| AC2 | Consultation labels remove legacy vocabulary. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "legacy\|Legacy" src/i18n/consultations.ts` returns zero. |
| AC3 | Consultation identifiers remain stable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- ConsultationMigration consultationStore`. |
| AC4 | Tests assert final canonical labels. | Evidence profile: `reintroduction_guard`; `npm run test -- ConsultationMigration consultationStore` fails if `(Legacy)` returns. |
| AC5 | Design-system legacy policy remains green. | Evidence profile: `runtime_guard`; `npm run test -- design-system legacy-style` and `npm run lint`. |
| AC6 | Final evidence has no deferred decision or limitation. | Evidence profile: `persistent_evidence`; AC6 story/i18n `rg` scan returns zero. |

## Implementation Tasks

- [x] Task 1 - Capture before evidence for consultation legacy labels. (AC: AC1)
- [x] Task 2 - Remove `(Legacy)` from all consultation labels without changing ids or values. (AC: AC2, AC3)
- [x] Task 3 - Add or update focused tests for final canonical labels. (AC: AC3, AC4)
- [x] Task 4 - Capture after evidence and negative scans. (AC: AC2, AC6)
- [x] Task 5 - Run focused frontend tests, lint and story validation. (AC: AC3, AC4, AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/i18n/consultations.ts` as the single source of consultation labels.
- Reuse existing consultation tests when they already cover label behavior.
- Do not duplicate consultation labels in components or test fixtures beyond focused assertions.

## No Legacy / Forbidden Paths

- Forbidden: `(Legacy)`, `Legacy`, `legacy` in active consultation labels.
- Forbidden: approved compatibility copy, alias labels, fallback labels, duplicate i18n source.
- Forbidden: tests that keep legacy labels as expected behavior.

## Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: final non-legacy consultation label.
- `external-active`: documented external requirement to show legacy wording; current user decision says none is approved.
- `historical-facade`: `(Legacy)` wording preserved from an older vocabulary.
- `dead`: legacy label after canonical label replacement.
- `needs-user-decision`: only if evidence contradicts the current explicit user decision.

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

- `_condamad/stories/CS-072-retirer-libelles-legacy-consultations/consultation-labels-after.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Consultation option labels | `frontend/src/i18n/consultations.ts` | legacy label suffixes and component-local duplicate labels |
| Consultation label behavior tests | `frontend/src/tests/ConsultationMigration.test.tsx` or focused i18n test | assertions that preserve `(Legacy)` |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving `(Legacy)` behind a wrapper
- adding compatibility labels
- keeping a deprecated label active
- preserving the old label through alias or re-export
- replacing deletion with hidden fallback wording

## External Usage Blocker

If a label is `external-active`, it must not be deleted without explicit
evidence and user decision. The current user decision is explicit: no legacy
wording may remain.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path is added, removed or renamed by this frontend i18n story.
- Generated client/schema absence: no generated client, generated schema or generated manifest is affected.
- Route manifest absence: no frontend route manifest or route path is changed.
- Required evidence: `git diff -- frontend/src/i18n/consultations.ts frontend/src/tests` remains limited to consultation labels and focused tests.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-0932/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/tests/ConsultationMigration.test.tsx`
- consultation store tests discovered by `rg -n "consultationStore|consultations" frontend/src/tests frontend/src -g "*.test.ts" -g "*.test.tsx"`

## Expected Files to Modify

Likely files:
- `frontend/src/i18n/consultations.ts` - remove legacy suffixes from labels.

Likely tests:
- `frontend/src/tests/ConsultationMigration.test.tsx` - update or add label assertions.
- `frontend/src/tests/consultation-i18n.test.ts` - acceptable new focused test if no existing test fits.

Files not expected to change:
- `backend/app/main.py` - no backend behavior is in scope.
- `frontend/package.json` - no dependency or script change is required.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- ConsultationMigration consultationStore
npm run test -- design-system legacy-style
npm run lint
rg -n "legacy|Legacy" src/i18n/consultations.ts
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-072-retirer-libelles-legacy-consultations/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: changing text accidentally changes consultation ids or store behavior.
  - Guardrail: `npm run test -- ConsultationMigration consultationStore`.
- Risk: legacy vocabulary returns in i18n because no focused assertion exists.
  - Guardrail: dedicated label assertion and negative scan.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not create compatibility copy, alias labels, fallback labels or duplicate i18n sources.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-002`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/02-finding-register.md#F-006`
- `_condamad/stories/regression-guardrails.md`
