# Story CS-118 relocate-natal-interpretation-feature-owner: Relocate natal interpretation to the canonical natal feature owner

Status: done

## 1. Objective

Relocaliser le container `NatalInterpretationSection` et le sous-container
`PersonaSelector` hors de `frontend/src/components/**` vers un owner canonique
`frontend/src/features/natal-chart/**`. Le comportement utilisateur du parcours
theme natal doit rester identique. La story ferme la condition de sortie de
l'audit: les composants partages ne doivent plus etre owners d'orchestration
API/feature pour l'interpretation natale.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-09-0031/03-story-candidates.md#Deferred-Non-Component-Context`
- Reason for change: l'audit de cloture composants indique que
  `NatalInterpretation` est deja decompose. Le container et
  `NatalInterpretationPersonaSelector` restent toutefois des exceptions
  API/feature sous `components`; l'action differee est de les deplacer vers un
  owner natal canonique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/features/natal-chart/**`
- In scope:
  - Creer ou utiliser le namespace feature `frontend/src/features/natal-chart/**` comme owner canonique de l'orchestration d'interpretation natale.
  - Deplacer `frontend/src/components/NatalInterpretation.tsx` vers ce namespace en conservant l'export `NatalInterpretationSection`.
  - Deplacer `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` avec le container parce qu'il consomme `useAstrologers` et `AstrologerGrid`.
  - Mettre a jour les imports runtime, tests et guards vers le nouveau chemin canonique.
  - Retirer les exceptions `COMPONENT_API_IMPORT_EXCEPTIONS` devenues stale pour le container natal et le persona selector.
  - Persister un inventaire before/after prouvant le deplacement, l'absence de shim et la stabilite de l'ownership.
- Out of scope:
  - Modifier les endpoints, hooks ou contrats de `frontend/src/api/natalChart.ts`.
  - Modifier le comportement produit: entitlement, historique, selection d'astrologue, PDF, erreurs, loading ou redirections abonnement.
  - Conserver `NatalInterpretationContent`, `NatalInterpretationEvidence` et
    `NatalInterpretationMenus` comme composants presentational API-free, sauf si
    ils sont deplaces avec le meme owner pour supprimer un import non canonique.
  - Modifier la page `NatalChartPage` hors import et wiring strictement necessaires.
  - Changer le backend, les migrations ou l'OpenAPI.
- Explicit non-goals:
  - Ne pas changer `RG-071`: le container natal ne doit pas redevenir monolithique.
  - Ne pas affaiblir `RG-069`: `frontend/src/components/**` doit rester garde contre les owners API/feature implicites.
  - Ne pas ajouter d'alias, re-export de compatibilite ou wrapper sous l'ancien chemin `frontend/src/components/NatalInterpretation.tsx`.
  - Ne pas introduire de styles inline; conserver ou deplacer le CSS dans un fichier `.css` dedie.

## 4. Operation Contract

- Operation type: move
- Primary archetype: legacy-facade-removal
- Archetype reason: la story deplace le module owner vers un namespace
  canonique et supprime l'ancien chemin d'import comme surface legacy. Aucun
  wrapper ou re-export de compatibilite ne peut rester.
- Behavior change allowed: no
- Behavior change constraints:
  - Les textes, etats loading/error/empty, actions PDF, suppression, historique, redirections abonnement et selection d'astrologue doivent rester equivalents.
  - Les differences autorisees sont les chemins d'import, le namespace de fichiers et les entries de guard/allowlist qui deviennent caduques.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le repo contient deja un autre owner natal canonique
  concurrent qui rend `frontend/src/features/natal-chart/**` ambigu; dans ce
  cas, stopper et documenter le choix necessaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les tests React et le guard AST executable sont la source observable de preservation du comportement UI et de l'ownership import. |
| Baseline Snapshot | yes | le move doit prouver before/after imports, owners et exceptions retirees. |
| Ownership Routing | yes | la responsabilite API/feature doit etre routee de `components` vers `features/natal-chart`. |
| Allowlist Exception | yes | les exceptions natal existantes doivent etre auditees puis retirees sans remplacement broad. |
| Contract Shape | no | aucun DTO/API payload/type public n'est change. |
| Batch Migration | no | un seul owner runtime et son sous-container sont migres. |
| Reintroduction Guard | yes | le retour de l'ancien chemin ou d'une exception stale doit echouer. |
| Persistent Evidence | yes | les preuves before/after et no-shim doivent etre conservees dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - React/Vitest behavior tests for `NatalInterpretationSection` and `NatalChartPage`, executed by `npm run test -- natalInterpretation NatalChartPage`.
  - AST guard in `frontend/src/tests/component-architecture-guards.test.ts`, executed by `npm run test -- component-architecture`.
- Secondary evidence:
  - before/after owner artifacts and targeted no-shim scans for removed component paths.
- Static scans alone are not sufficient for this story because:
  - the moved feature must still render and handle history/PDF/delete/persona flows, not merely satisfy import text scans.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-after.md`
- Expected invariant:
  - `NatalInterpretationSection` reste consomme par `NatalChartPage` avec
    comportement equivalent.
  - L'orchestration API/feature natale n'est plus sous
    `frontend/src/components/**`.
- Allowed differences:
  - Chemins de fichiers/imports, suppression des anciennes exceptions exactes, ajout d'un guard anti-retour.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Orchestration API natale | `frontend/src/features/natal-chart/**` | `frontend/src/components/**` |
| Selection d'astrologue consommatrice de feature/API | `frontend/src/features/natal-chart/**` avec le container parent | composant presentational partage sous `components/**` |
| Rendu presentational API-free | fichier presentational existant ou deplace | module avec `api`, `features`, `apiFetch`, `fetch` ou `axios` |
| Styles de l'interpretation natale | `.css` existant ou deplace avec la feature, utilisant les variables existantes | `style=` inline ou nouveau systeme de tokens non justifie |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/NatalInterpretation.tsx` | current exact natal owner exception | must be deleted by this story |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | selector | delete |

Rules:

- no wildcard;
- no folder-wide exception;
- no replacement exception for `features/natal-chart/**`;
- every retained exception outside this story must remain exact and validated by `npm run test -- component-architecture`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export DTO, OpenAPI contract, generated client, or serialized frontend/backend contract is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: this is one bounded module move with one production consumer (`NatalChartPage`) and related tests/guards.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before snapshot | `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-before.md` | chemins, imports et exceptions avant move |
| after snapshot | `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-after.md` | owner canonique et exceptions retirees |
| no-shim scan | `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-no-shim.md` | absence de wrapper, alias ou re-export |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` when it still imports API/feature code
- `components/NatalInterpretation.tsx` or `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` entries in `COMPONENT_API_IMPORT_EXCEPTIONS`
- imports from `../components/NatalInterpretation` or `@/components/NatalInterpretation`
- compatibility wrapper, alias, fallback module or re-export preserving the old path

Guard evidence:

- Deterministic source:
  - AST guard inventory from `frontend/src/tests/component-architecture-guards.test.ts`.
  - forbidden symbols scan over `frontend/src`.
- Evidence profile: `reintroduction_guard`;
  `npm run test -- component-architecture natalInterpretation NatalChartPage`
  must fail if the old component owner or stale exception returns.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md#F-003`
- Closure proof required: before/after owner inventory, component architecture guard, natal behavior tests, no-shim scan, removal of stale allowlist entries.
- Known residual in-domain work: none
- Deferred non-domain concerns: none
- Full-closure rule: `PASS with limitation`, broad allowlists, wildcard
  exceptions, unclassified fallback, compatibility, legacy, migration-only,
  shim, alias, TODO, and hidden residual in-domain work are forbidden.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md` - current owner is `components/NatalInterpretation.tsx`.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md#F-003` - feature relocation is deferred.
- Evidence 3: `_condamad/audits/frontend-components/2026-05-09-0031/03-story-candidates.md#L64` - `frontend-natal` must move container and selector.
- Evidence 4: `frontend/src/components/NatalInterpretation.tsx` - current container imports natal API hooks and composes the interpretation section.
- Evidence 5: `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` - current sub-container imports `useAstrologers` and `AstrologerGrid`.
- Evidence 6: `frontend/src/tests/component-architecture-allowlist.ts` - exact natal exceptions still exist with feature-move exit conditions.
- Evidence 7: `frontend/src/pages/NatalChartPage.tsx` - production consumer imports `NatalInterpretationSection` from `../components/NatalInterpretation`.
- Evidence 8: `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/00-story.md` - prior story decomposed the monolith.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - `RG-069`, `RG-071` and new `RG-073` consulted before story scope was finalized.

## 6. Target State

- `NatalInterpretationSection` lives under `frontend/src/features/natal-chart/**` as the canonical owner for natal interpretation orchestration.
- `PersonaSelector` lives under the same feature owner or an immediately adjacent feature subfolder, not under `components/**` while importing API/feature code.
- `NatalChartPage` and tests import from the canonical feature owner.
- `COMPONENT_API_IMPORT_EXCEPTIONS` no longer contains natal interpretation entries.
- `component-architecture` guards fail if the old component paths, stale allowlist entries, or compatibility wrappers return.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-069` - the story removes two API/feature ownership exceptions from `frontend/src/components/**`.
  - `RG-071` - the move must preserve the decomposed `NatalInterpretation` boundary from CS-115.
  - `RG-073` - the canonical owner for natal interpretation orchestration must remain under `frontend/src/features/natal-chart/**`.
- Non-applicable invariants:
  - `RG-070` - no TypeScript suppression is added or changed.
  - `RG-072` - the story does not classify unused components; it changes a known used runtime surface.
- Required regression evidence:
  - `npm run test -- component-architecture natalInterpretation NatalChartPage`
  - before/after owner artifacts and no-shim scan in this story folder.
  - targeted scan proving no import of `components/NatalInterpretation` remains outside historical `_condamad` evidence.
- Allowed differences:
  - Canonical file paths and imports only; UI behavior and API contracts must not change.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `NatalInterpretationSection` lives under `frontend/src/features/natal-chart/**`. | `rg -n "export function NatalInterpretationSection" frontend/src/features/natal-chart`. |
| AC2 | `NatalChartPage` imports the section from the canonical feature owner. | `rg -n "features/natal-chart" frontend/src/pages/NatalChartPage.tsx`; after artifact. |
| AC3 | The old `components/NatalInterpretation` import path is absent. | `rg -n "components/NatalInterpretation" frontend/src`; persist result. |
| AC4 | Selector with astrologer dependency is no longer under `components/**`. | Evidence profile: `ast_architecture_guard`; AST guard `npm run test -- component-architecture`. |
| AC5 | `COMPONENT_API_IMPORT_EXCEPTIONS` has no natal entries or broad replacement. | Evidence profile: `allowlist_register_validated`; `npm run test -- component-architecture`. |
| AC6 | The natal interpretation interaction contract remains equivalent. | `npm run test -- natalInterpretation`; `npm run lint`. |
| AC7 | CS-115 split invariant is preserved; presentational children stay API-free. | AST guard `npm run test -- component-architecture`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture baseline ownership evidence (AC: AC1, AC5, AC7)
  - [x] Write `natal-feature-owner-before.md` with current file paths, line counts, imports, consumers and allowlist entries.
  - [x] Record the exact current production consumer import in `NatalChartPage`.

- [x] Task 2 - Move the container to the natal feature owner (AC: AC1, AC2, AC3, AC6)
  - [x] Create `frontend/src/features/natal-chart/**` if it does not exist.
  - [x] Move `NatalInterpretation.tsx` into the feature namespace and update relative imports.
  - [x] Update `NatalChartPage` and tests to import `NatalInterpretationSection` from the feature owner.

- [x] Task 3 - Move or rehome the persona selector with the feature owner (AC: AC4, AC6)
  - [x] Move `NatalInterpretationPersonaSelector.tsx` out of `components/**`.
  - [x] Keep `useAstrologers` and `AstrologerGrid` imports in the feature-owned sub-container, not in presentational components.

- [x] Task 4 - Harden architecture guards and remove stale exceptions (AC: AC3, AC4, AC5, AC7)
  - [x] Remove natal interpretation entries from `COMPONENT_API_IMPORT_EXCEPTIONS`.
  - [x] Update `component-architecture-guards.test.ts` so it expects the canonical feature owner and rejects the old component paths.
  - [x] Ensure presentational natal files that remain under `components/natal-interpretation/**` are API-free.

- [x] Task 5 - Persist after/no-shim evidence and validate (AC: AC1, AC2, AC3, AC6, AC7)
  - [x] Write `natal-feature-owner-after.md`.
  - [x] Write `natal-feature-owner-no-shim.md`.
  - [x] Run targeted tests, lint and negative scans from the validation plan.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/api/natalChart.ts` hooks and API functions; do not duplicate API clients.
  - `frontend/src/features/astrologers` exports for astrologer cards/grid.
  - Existing `NatalInterpretation.css` classes or a moved CSS file; do not introduce inline styles.
  - Existing tests `frontend/src/tests/natalInterpretation.test.tsx` and `frontend/src/tests/NatalChartPage.test.tsx`.
- Do not recreate:
  - a second `NatalInterpretationSection` wrapper under `components`.
  - duplicated persona selection logic.
  - duplicated PDF/history/delete handlers outside the moved owner.
- Shared abstraction allowed only if:
  - it has at least two concrete feature consumers after this story and does not create a compatibility path for the old component owner.

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

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` if it imports API/feature code
- `components/NatalInterpretation.tsx` in `COMPONENT_API_IMPORT_EXCEPTIONS`
- `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` in `COMPONENT_API_IMPORT_EXCEPTIONS`
- `from "../components/NatalInterpretation"`
- `from "@/components/NatalInterpretation"`
- any file whose only purpose is to re-export the moved feature owner from the old component path

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, generated clients, analytics/event contracts, or explicit external evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old import path or UI surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

Story-specific classification targets:

- `frontend/src/features/natal-chart/**` after move: `canonical-active`, decision `keep`.
- `frontend/src/components/NatalInterpretation.tsx` after move: `historical-facade`
  if preserved as wrapper/re-export, otherwise `dead`; decision `delete`.
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`
  after move: `historical-facade` if preserved as wrapper/re-export, otherwise
  `dead`; decision `delete`.
- `components/NatalInterpretation.tsx` and `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` allowlist entries: `dead` after move, decision `delete`.

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path:

- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-no-shim.md`

The audit must include at minimum:

- old component file path;
- old persona selector file path;
- old import path from `NatalChartPage`;
- stale allowlist entries;
- canonical feature replacement path.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Natal interpretation orchestration | `frontend/src/features/natal-chart/**` | `frontend/src/components/NatalInterpretation.tsx` |
| Persona selector with API/feature imports | `frontend/src/features/natal-chart/**` | old selector under `components/natal-interpretation` |
| Presentational interpretation rendering | API-free presentational modules | API hooks or feature selection inside presentational components |
| Natal page composition | `frontend/src/pages/NatalChartPage.tsx` consumes the feature owner | duplicated orchestration in the page |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting imports through the old component file;
- preserving a wrapper;
- adding a compatibility alias;
- preserving the old path through re-export;
- replacing deletion with a soft-disabled file;
- keeping a stale allowlist entry after the source no longer violates the guard.

## 15. External Usage Blocker

If a removed import path or file is classified as `external-active`, it must not be deleted silently. The dev agent must stop and record:

- exact external evidence;
- impacted consumer;
- deletion risk;
- required user decision.

Expected result for this story: no external-active frontend component import is
expected, because the source audit identifies only first-party runtime consumers.
If evidence contradicts that assumption, implementation must stop.

## 17. Generated Contract Check

- Generated contract impact:
  - no OpenAPI path is changed;
  - no generated API client schema is changed;
  - no public API contract is changed.
- Required generated artifact absence:
  - prove no generated route manifest, generated schema or generated client contains the old frontend import path `components/NatalInterpretation`.
  - if the repo has no generated frontend route manifest or generated client artifact for component imports, record that absence in `natal-feature-owner-no-shim.md`.
- Validation evidence:
  - `rg -n "components/NatalInterpretation|components/natal-interpretation/NatalInterpretationPersonaSelector" frontend -g "*.ts" -g "*.tsx" -g "*.json"`
    must have zero active generated/client hits after implementation, excluding
    historical `_condamad` evidence.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationMenus.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - new canonical location for the moved container.
- `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx` - new canonical location for the API/feature-consuming selector.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - canonical style location if the container CSS is moved with the owner.
- `frontend/src/pages/NatalChartPage.tsx` - update import to the feature owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - update import and preserve behavior tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - update mocks/import expectations when imports change.
- `frontend/src/tests/component-architecture-guards.test.ts` - reject old component owner and guard the feature owner/presentational split.
- `frontend/src/tests/component-architecture-allowlist.ts` - remove natal interpretation exceptions.
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-before.md` - baseline evidence.
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-after.md` - after evidence.
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-no-shim.md` - no legacy/shim proof.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - behavior preservation for the moved section.
- `frontend/src/tests/NatalChartPage.test.tsx` - page integration remains wired.
- `frontend/src/tests/component-architecture-guards.test.ts` - ownership and anti-reintroduction guard.

Files not expected to change:

- `backend/app/**` - no backend/API change.
- `frontend/src/api/natalChart.ts` - API hooks remain canonical and reused.
- `frontend/src/api/astrologers.ts` - astrologer API hook remains reused.
- `frontend/src/i18n/**` - no copy or translation behavior change.
- `frontend/src/styles/**` - no design-system token change.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
npm --prefix frontend run test -- component-architecture natalInterpretation NatalChartPage
npm --prefix frontend run lint
rg -n "components/NatalInterpretation|components/natal-interpretation/NatalInterpretationPersonaSelector" frontend/src -g "*.ts" -g "*.tsx"
rg -n "NatalInterpretation|NatalInterpretationPersonaSelector" frontend/src/tests/component-architecture-allowlist.ts
if (Test-Path frontend/src/components/natal-interpretation) {
  rg -n "apiFetch\\(|fetch\\(|axios|from [\"'](?:.*api|.*features)" frontend/src/components/natal-interpretation -g "*.ts" -g "*.tsx"
}
```

Expected scan results:

- The old component import/path scan has zero active hits under `frontend/src` after implementation.
- The allowlist scan has zero natal interpretation hits.
- The presentational subfolder scan has zero API/feature hits when the folder remains.

## 22. Regression Risks

- Risk: import rewiring changes the natal page integration or test mocks.
  - Guardrail: `npm run test -- natalInterpretation NatalChartPage`.
- Risk: a wrapper under `components` keeps the old path alive and hides the migration.
  - Guardrail: no-shim artifact and targeted old-path scans.
- Risk: removing allowlist entries without a guard allows a future API owner under `components`.
  - Guardrail: `npm run test -- component-architecture` and `RG-069`.
- Risk: the move recombines extracted responsibilities into the container.
  - Guardrail: `RG-071`, after line/import inventory and focused natal tests.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not add a compatibility export from `frontend/src/components/NatalInterpretation.tsx`.
- Do not create a barrel whose only effect is to keep the old component import valid.
- Do not move API hooks into presentational children.
- Do not change user-visible natal interpretation behavior while moving files.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work because this story is `full-closure`.

## 24. References

- `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md` - latest same-domain audit closure evidence and exit condition.
- `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md#F-003` - source finding and deferred action.
- `_condamad/audits/frontend-components/2026-05-09-0031/03-story-candidates.md` - finite closure map for `frontend-natal`.
- `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/00-story.md` - prior decomposition story and invariant.
- `_condamad/stories/regression-guardrails.md` - shared regression invariants.
- `frontend/src/tests/component-architecture-allowlist.ts` - current stale exceptions to remove.
