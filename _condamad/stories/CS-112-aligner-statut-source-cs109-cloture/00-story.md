# Story CS-112 aligner-statut-source-cs109-cloture: Aligner le statut source de CS-109 avec sa cloture

Status: done

## 1. Objective

Aligner le statut de la story source CS-109 avec le registre canonique et les
preuves de cloture deja presentes, sans modifier le code runtime frontend.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md#SC-303`
- Reason for change: `_condamad/stories/story-status.md` marque CS-109 `done`
  alors que son fichier `00-story.md` indique encore `Status: ready-to-dev`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-layouts-governance`
- In scope:
  - Mettre a jour le header de CS-109 pour qu'il corresponde au registre.
  - Aligner la checklist ou ajouter une note historique explicite.
  - Verifier que `story-status.md`, CS-109 et les preuves finales ne se contredisent plus.
- Out of scope:
  - Modifier `frontend/src/**`.
  - Reexecuter ou reecrire l'implementation CS-109.
  - Changer le statut canonique d'autres stories.
  - Modifier les audits layout historiques sauf preuve directement contradictoire avec CS-109.
- Explicit non-goals:
  - Ne pas affaiblir `RG-068`.
  - Ne pas masquer une contradiction par une compatibility note vague.
  - Ne pas introduire de legacy status, fallback documentaire, alias ou doublon de registre.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: custom
- Archetype reason: aucun archetype supporte ne cible seulement l'alignement de
  statut et checklist d'une story CONDAMAD deja close.
- Additional validation rules:
  - Le registre `story-status.md` reste la source canonique.
  - Aucune modification runtime frontend n'est autorisee.
  - La preuve doit etre un scan cible de CS-109 et du registre.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: la convention projet interdit de modifier une story
  apres cloture et impose une note historique au lieu du changement de header.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Un guard de source markdown et diff frontend prouve que seul l'etat gouvernance change. |
| Baseline Snapshot | yes | Il faut prouver l'avant/apres du statut contradictoire. |
| Ownership Routing | no | Aucun fichier applicatif ne change de proprietaire. |
| Allowlist Exception | no | Aucun registre d'exception applicatif n'est touche. |
| Contract Shape | no | Aucun API, DTO, type public ou contrat genere n'est touche. |
| Batch Migration | no | Une seule story source est alignee. |
| Reintroduction Guard | yes | Les contradictions de statut CS-109 ne doivent pas rester actives. |
| Persistent Evidence | yes | La preuve de gouvernance doit rester dans CS-109 ou les scans de validation. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard equivalent for markdown state: targeted `rg` scans over CS-109 and
    `_condamad/stories/story-status.md`.
- Secondary evidence:
  - `git diff --name-only -- frontend/src` to prove the frontend source tree is
    not part of the governance change.
- Static scans alone are not sufficient because:
  - the story must compare both canonical registry and source story, not one
    isolated status line.
- Command:
  - `rg -n "CS-109|Status:" _condamad/stories/story-status.md _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - command output from `rg -n "Status: ready-to-dev" _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
- Comparison after implementation:
  - command output from `rg -n "CS-109|Status:" _condamad/stories/story-status.md _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
- Required baseline content:
  - CS-109 source story header status.
  - CS-109 registry row status.
- Expected invariant:
  - CS-109 source story and registry no longer disagree.
- Allowed differences:
  - header status update to `done`;
  - checklist ticks or an explicit historical checklist note.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no ownership boundary or runtime module is moved.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no allowlist or exception registry is changed by this governance story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, HTTP response, payload, generated client, export contract, DTO
  or frontend public type is changed.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: exactly one source story is aligned.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source story | `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | Canonical source story header and checklist alignment. |
| Registry | `_condamad/stories/story-status.md` | Canonical story status row for CS-109 remains `done`. |

## 4i. Reintroduction Guard

The implementation must prove that the stale CS-109 status is absent from the
active source story.

Deterministic guard sources:

- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
- `_condamad/stories/story-status.md`

Required forbidden examples:

- `Status: ready-to-dev` in CS-109 after closure
- registry row for `CS-109` with any status other than `done`

Guard evidence:

- targeted `rg` scans listed in the validation plan

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md#F-303`
- Closure proof required: scan proving the stale source status is absent and
  scan proving the CS-109 registry row remains `done`.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md` - E-008 records the contradiction between CS-109 and `story-status.md`.
- Evidence 2: `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md` - F-303 recommends aligning the CS-109 source story status.
- Evidence 3: `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` - current header says `Status: ready-to-dev`.
- Evidence 4: `_condamad/stories/story-status.md` - current CS-109 row says `done`.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - `RG-068` was consulted before scope was finalized.

## 6. Target State

After implementation:

- CS-109 source story status matches `story-status.md`.
- CS-109 checklist is marked consistently with final evidence or explicitly
  labelled as historical.
- No runtime frontend file changes.
- Future layout audits cannot cite an active CS-109 status contradiction.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-068` - CS-109 belongs to the layout closure trail protecting route-level ownership.
- Non-applicable invariants:
  - `RG-047` - no inline style surface is touched.
  - `RG-050` - no design-system guard or allowlist is touched.
  - `RG-064` - no page architecture test or registry is touched.
- Required regression evidence:
  - targeted scans for `CS-109` status in source story and registry
  - git diff proving no `frontend/src/**` runtime file changed for this story
- Allowed differences:
  - governance markdown updates only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-109 source story no longer says `ready-to-dev`. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -n "ready-to-dev" _condamad/stories/CS-109-*`. |
| AC2 | CS-109 status is `done` in both files. | Evidence profile: `baseline_before_after_diff`; command `rg -n "CS-109|Status:" _condamad/stories`. |
| AC3 | Frontend source files remain outside the CS-112 change set. | Evidence profile: `repo_wide_negative_scan`; command `rg -n "frontend/src" _condamad/stories/CS-112-*`. |
| AC4 | Story validation remains green. | Command `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture the status contradiction. (AC: AC1, AC2)
  - [x] Run the before scans from the validation plan.

- [x] Task 2 - Align CS-109 source story. (AC: AC1, AC2)
  - [x] Update the header to `Status: done`, or add a historical immutability note if project convention blocks header edits.
  - [x] Mark tasks consistently with final evidence or label the checklist historical.

- [x] Task 3 - Prove runtime isolation. (AC: AC3)
  - [x] Verify no `frontend/src/**` file is part of this story's diff.

- [x] Task 4 - Validate the new story contract. (AC: AC4)
  - [x] Run story validate and strict lint with the venv active.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `_condamad/stories/story-status.md` as the canonical status registry.
  - Existing CS-109 final evidence files as proof of closure.
- Do not recreate:
  - a second story status registry;
  - a duplicate CS-109 closure note outside the source story;
  - a runtime guard for a markdown-only contradiction.
- Shared abstraction allowed only when:
  - none; this is a direct governance alignment.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `Status: ready-to-dev` in `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
- `CS-109` registry status other than `done`
- changes under `frontend/src/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/generated/10-final-evidence.md`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` - align status and checklist wording.

Likely tests:

- `_condamad/stories/CS-112-aligner-statut-source-cs109-cloture/00-story.md` - validate and strict lint this story contract.

Files not expected to change:

- `frontend/src/app/routes.tsx` - runtime route tree untouched.
- `frontend/src/layouts/PageLayout.css` - belongs to CS-110.
- `frontend/src/layouts/TwoColumnLayout.tsx` - belongs to CS-111.
- `_condamad/stories/story-status.md` - existing CS-109 row remains canonical; only CS-112 creation row is added.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
rg -n "Status: ready-to-dev" _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md
rg -n "CS-109|Status:" _condamad/stories/story-status.md _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md
git diff --name-only -- frontend/src
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-112-aligner-statut-source-cs109-cloture/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-112-aligner-statut-source-cs109-cloture/00-story.md
```

## 22. Regression Risks

- Risk: CS-109 becomes inconsistent with final evidence while only the header changes.
  - Guardrail: AC2 requires source story and registry scan together.
- Risk: runtime code is changed during governance cleanup.
  - Guardrail: AC3 requires no `frontend/src/**` diff.
- Risk: future audits still cite stale status text.
  - Guardrail: AC1 forbids the stale status in the CS-109 source story.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not edit runtime frontend code for this governance-only story.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md#SC-303` - source story candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md#F-303` - source finding.
- `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md#E-008` - status contradiction evidence.
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` - source story to align.
- `_condamad/stories/story-status.md` - canonical status registry.
