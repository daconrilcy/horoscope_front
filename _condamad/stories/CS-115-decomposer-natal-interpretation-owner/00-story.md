# Story CS-115 decomposer-natal-interpretation-owner: Decomposer le composant NatalInterpretation et clarifier son owner

Status: done

## 1. Objective

Decomposer `NatalInterpretation.tsx` en un owner borne: un container unique
clairement classe et des composants/helpers presentational testes. La story
separe formatage, modal/menu, selection de version, tags d'evidence,
skeleton/error states et blocs de contenu du fichier monolithique.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-003`
- Reason for change: `NatalInterpretation.tsx` concentre API hooks, composition feature, entitlement workflow, formatage, modal state et rendu dans 1131 lignes.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components/NatalInterpretation.tsx`
- In scope:
  - Extraction de helpers de formatage et de composants internes de `NatalInterpretation`.
  - Clarification du owner du container natal.
  - Tests focalises pour helpers/composants extraits.
  - CSS associe dans `NatalInterpretation.css` ou fichiers CSS dedies, sans style inline.
- Out of scope:
  - Changement des contrats API natal.
  - Refonte produit du parcours d'interpretation.
  - Suppression de compatibilites runtime hors de cette surface.
- Explicit non-goals:
  - Ne pas creer de default-export alias, re-export stale ou chemin de compatibilite.
  - Ne pas modifier les invariants `RG-050`, `RG-057`, `RG-064`.
  - Ne pas changer l'entitlement ou les actions PDF/historique au-dela de l'extraction.

## 4. Operation Contract

- Operation type: split
- Primary archetype: large-file-split
- Archetype reason: la story extrait un gros fichier multi-responsabilite en modules bornes.
- Behavior change allowed: no
- Behavior change constraints:
  - Les textes, etats loading/error/empty, actions, versions et evidence visibles doivent rester equivalents.
  - Les differences autorisees sont les chemins de fichiers, noms internes et tests.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: il faut choisir entre owner reusable component et feature natal sans preuve d'usage suffisante.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | le guard AST executable devient source de verite du boundary natal. |
| Baseline Snapshot | yes | line-count/import/responsibility before/after obligatoires. |
| Ownership Routing | yes | le container natal et les composants presentational doivent avoir owners distincts. |
| Allowlist Exception | yes | toute exception file-size/API import restante doit etre exacte. |
| Contract Shape | no | aucun DTO/API payload n'est change. |
| Batch Migration | no | le lot est centre sur un fichier owner unique. |
| Reintroduction Guard | yes | guard requis pour eviter le retour d'un container monolithique non classe. |
| Persistent Evidence | yes | les artefacts before/after et diff d'ownership doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/component-architecture-guards.test.ts`, executed by `npm run test -- component-architecture`.
- Secondary evidence:
  - line-count, ownership diff and targeted `rg` scans over natal files.
- Static scans alone are not sufficient for this story because:
  - the AST guard must enforce that API imports remain in the classified owner and not in presentational modules.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/natal-interpretation-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/natal-interpretation-after.md`
- Expected invariant:
  - `NatalInterpretation.tsx` ne possede plus simultanement helpers de formatage, modal internals, selection feature, et rendu principal.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| API orchestration natal | one classified container or `frontend/src/features/natal/**` if chosen | presentational subcomponent |
| Evidence formatting helpers | tested helper module | React render body |
| Modal/menu/version selector/evidence tags | focused presentational components | monolithic `NatalInterpretation.tsx` |
| CSS styling | `.css` file using existing variables | inline `style` attributes |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `component-architecture-allowlist.ts` | container/file-size exact | if natal remains in `components` | owner, reason, command and exit |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before snapshot | `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/natal-interpretation-before.md` | line count, import map, responsibilities before split |
| after snapshot | `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/natal-interpretation-after.md` | prove responsibilities are split and owner classified |
| ownership diff | `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/natal-import-ownership-diff.md` | prove API imports remain only in the owner |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- unclassified API/feature imports in natal presentational components
- file-size exception for `NatalInterpretation.tsx` without exact owner and exit condition
- default-export compatibility aliases for moved natal modules

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- component-architecture natalInterpretation` checks owner and split constraints.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-003`
- Closure proof required: before/after responsibility evidence, ownership diff, focused tests, targeted line-count/import scans.
- Known residual in-domain work: none
- Deferred non-domain concerns: broader page route ownership remains under `frontend-react-pages`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md` - `F-003` records the multi-owner component.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-08-2303/01-evidence-log.md` - `E-005` records 1131 TSX lines and 913 CSS lines.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- `NatalInterpretation.tsx` is a narrow container or is moved to a natal feature owner.
- Presentational natal components are API-free and tested where non-trivial.
- Formatting helpers such as `formatEvidenceId` and `_categorizeEvidence` live in a focused tested helper module.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - design-system and architecture guards must remain executable.
  - `RG-057` - no compatibility vocabulary, mapper, fallback or alias should be recreated.
  - `RG-064` - page architecture must not absorb unclassified natal ownership.
- Non-applicable invariants:
  - `RG-068` - no layout hierarchy change is required.
- Required regression evidence:
  - `npm run test -- natalInterpretation NatalChartPage design-system inline-style legacy-style`
  - targeted line-count/import scans.
- Allowed differences:
  - File split and import ownership only; user-visible behavior must remain equivalent.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | After evidence records the final import inventory. | Evidence profile: `baseline_before_after_diff`; `rg -n 'apiFetch' frontend/src/components/NatalInterpretation.tsx`. |
| AC2 | Formatting helpers move to a focused tested module. | Evidence profile: `ast_architecture_guard`; `npm run test -- natalInterpretation`. |
| AC3 | Internal UI subcomponents are extracted from the container. | Evidence profile: `ast_architecture_guard`; `npm run test -- natalInterpretation NatalChartPage`. |
| AC4 | API orchestration stays in the owner; children are API-free. | Evidence profile: `reintroduction_guard`; AST guard via `npm run test -- component-architecture`. |
| AC5 | No forbidden presentation escape hatch is added. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- inline-style`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture current natal baseline (AC: AC1)
  - [ ] Record line counts, imports and responsibilities.
- [ ] Task 2 - Extract helpers and tests (AC: AC2)
  - [ ] Move evidence formatting/categorization into a tested helper.
- [ ] Task 3 - Extract focused UI components (AC: AC3, AC5)
  - [ ] Extract modal/menu, selector, tags, content blocks and states.
  - [ ] Keep styles in CSS files only.
- [ ] Task 4 - Classify owner and guard imports (AC: AC4)
  - [ ] Record final owner and any exact exception.
  - [ ] Add/update component architecture coverage when the final owner remains under `components`.
- [ ] Task 5 - Persist after evidence and validate (AC: AC1, AC5)
  - [ ] Write after artifact and run tests/lint/scans.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - existing natal API hooks and existing page tests.
  - existing CSS variables from `NatalInterpretation.css` or shared style sheets.
- Do not recreate:
  - duplicate feature selection logic.
  - duplicate evidence formatting helpers across components.
- Shared abstraction allowed only if:
  - extracted helper has a concrete caller in the natal flow.

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

- default-export compatibility alias for moved natal components
- stale barrel re-export preserving a removed internal path
- inline `style=` added to natal components
- comments or code containing unclassified `legacy`, `compatibility`, `fallback`, `alias`, or `shim`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Natal interpretation orchestration | classified container or `frontend/src/features/natal/**` | presentational child components |
| Natal interpretation rendering | focused components under the chosen owner | API hooks and feature decisions |
| Evidence formatting | helper module with tests | render body of `NatalInterpretation.tsx` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/design-system-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/NatalInterpretation.tsx` - reduce to container/composition.
- `frontend/src/components/NatalInterpretation.css` - keep or split CSS without inline styles.
- new files under `frontend/src/components/natal-interpretation/**` or `frontend/src/features/natal/**` - extracted helpers/components.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - preserve behavior coverage.
- new focused helper/component tests if extracted logic is non-trivial.
- `frontend/src/tests/component-architecture-guards.test.ts` - owner guard when required by final classification.

Files not expected to change:

- `backend/app/**` - no backend/API change.
- `frontend/src/pages/**` except direct import updates required by the final owner.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- natalInterpretation NatalChartPage design-system inline-style legacy-style
npm run lint
rg -n 'apiFetch|fetch|axios|from .*api|from .*features' src/components/NatalInterpretation.tsx src/components -g '*.ts' -g '*.tsx'
```

## 22. Regression Risks

- Risk: extraction changes entitlement/PDF/history behavior.
  - Guardrail: targeted natal and page tests.
- Risk: split creates compatibility re-exports or duplicate helpers.
  - Guardrail: ownership diff plus No Legacy scans.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass the split through wrappers, aliases, fallback modules or stale re-exports.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work because this story is `full-closure`.

## 24. References

- `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-003` - source finding.
- `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-003` - story candidate contract.
- `_condamad/stories/regression-guardrails.md` - regression invariants.
