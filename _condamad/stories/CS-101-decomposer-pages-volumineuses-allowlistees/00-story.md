# Story CS-101 decomposer-pages-volumineuses-allowlistees: Decomposer les pages volumineuses encore allowlistees

Status: done

## 1. Objective

Fermer la dette `PAGE_SIZE_EXCEPTIONS` hors `AdminPromptsPage.tsx`.
Chaque page cible doit recevoir une decision explicite:
route-only permanent, extraction vers owner canonique, exception stale a supprimer,
ou blocker utilisateur documente.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-002`
- Reason for change: `F-002` indique que le guard page architecture passe, mais que des exceptions exactes restent pour des pages surdimensionnees hors AdminPrompts.

## 3. Domain Boundary

- Domain: `frontend-react-pages/page-size`
- In scope:
  - Capturer les line-counts et l'etat courant de `PAGE_SIZE_EXCEPTIONS`.
  - Traiter la carte finie: `AstrologerProfilePage.tsx`, `BirthProfilePage.tsx`, `SubscriptionSettings.tsx`, `AdminSamplePayloadsAdmin.tsx` si encore au-dessus du seuil ou stale.
  - Classer pour chaque page les responsabilites route-only et extractables.
  - Extraire les sections UI/feature vers des owners canoniques locaux, `frontend/src/components/**` ou `frontend/src/features/**` selon l'architecture existante.
  - Supprimer les exceptions stale ou temporaires fermees.
- Out of scope:
  - Modifier `AdminPromptsPage.tsx`, couvert par `CS-100`.
  - Centraliser le formatage date/heure inline, couvert par `CS-102`.
  - Changer le backend, les contrats API, les prix, quotas ou droits.
  - Reconcevoir visuellement les pages au-dela d'un deplacement de composants equivalent.
- Explicit non-goals:
  - Ne pas augmenter le seuil global ou les `maxLines` existants.
  - Ne pas ajouter d'exception wildcard, dossier ou "temporary" sans sortie.
  - Ne pas affaiblir `RG-064`.
  - Ne pas rouvrir les protections design-system `RG-044` a `RG-063`.

## 4. Operation Contract

- Operation type: split
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime les entrees `PAGE_SIZE_EXCEPTIONS` stale
  ou temporaires apres classification.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une page doit conserver une exception malgre une
  responsabilite extractable, ou si une extraction exige une decision produit.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard Vitest AST `page-architecture` est la source executable de la politique page-size. |
| Baseline Snapshot | yes | Les line-counts, exceptions et decisions par page doivent etre compares before/after. |
| Ownership Routing | no | L'archetype removal n'active pas ce contrat; la classification d'ownership reste documentee dans Canonical Ownership. |
| Allowlist Exception | yes | `PAGE_SIZE_EXCEPTIONS` est la surface principale a fermer. |
| Contract Shape | no | Aucun contrat API, DTO ou schema n'est change. |
| Batch Migration | no | La story supprime ou conserve des exceptions exactes apres classification, sans migration multi-namespace. |
| Reintroduction Guard | yes | Les exceptions larges/stale et la croissance silencieuse ne doivent pas revenir. |
| Persistent Evidence | yes | L'inventaire page-size et les decisions doivent etre persistes. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard runtime artifact: `frontend/src/tests/page-architecture-guards.test.ts`.
  - Exact exception register: `frontend/src/tests/page-architecture-allowlist.ts`.
- Secondary evidence:
  - `npm run test -- page-architecture`
  - before/after line-count inventories.
- Static scans alone are not sufficient because:
  - la croissance des pages et les exceptions stale doivent echouer dans Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/page-size-before.md`.
- Comparison after implementation: `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/page-size-after.md`.
- Required baseline content: line-counts, `PAGE_SIZE_EXCEPTIONS`, classification par page, owner actuel, owner cible, decision attendue et blocker si applicable.
- Expected invariant: aucune exception temporaire non traitee ne reste hors decisions permanent-route-only explicites.
- Allowed differences: decompositions de composants, imports, tests et allowlist diff strictement lies aux pages ciblees.

## 4d. Ownership Routing Rule

- Ownership Routing Rule: not applicable
- Reason: l'archetype principal est `dead-code-removal`; l'ownership necessaire a la decision de suppression est formalise dans `Canonical Ownership`.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Route shell publique ou settings | page route cible | feature/business UI lourde dans route page |
| Profil astrologue UI reutilisable | owner composant/feature existant | page monolithique si section extractable |
| Birth profile UI reutilisable | owner composant/feature existant | page monolithique si section extractable |
| Subscription settings sections | owner settings/subscription existant ou nouveau composant canonique | logique UI lourde dans `SubscriptionSettings.tsx` |
| Admin sample payloads sous-surface | owner admin-prompts existant ou composant admin dedie | exception stale ou page monolithique |

Rules:
- Classer chaque page avant modification: `below-threshold-stale`, `extractable`, `permanent-route-only`, `needs-user-decision`.
- Une page `permanent-route-only` doit avoir une raison stable, un seuil exact et aucune section extractable documentee.
- Une page `extractable` doit sortir de l'allowlist ou abaisser son seuil sans hausse.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `page-architecture-allowlist.ts` | `AstrologerProfilePage.tsx` | page profil au-dessus du seuil | supprimer ou reclasser avec preuve |
| `page-architecture-allowlist.ts` | `BirthProfilePage.tsx` | birth profile au-dessus du seuil | supprimer ou reclasser avec preuve |
| `page-architecture-allowlist.ts` | `SubscriptionSettings.tsx` | settings abonnement au-dessus du seuil | supprimer ou reclasser avec preuve |
| `page-architecture-allowlist.ts` | `AdminSamplePayloadsAdmin.tsx` | stale ou near-threshold | supprimer si stale ou traiter |

Rules:
- No wildcard, no folder-wide exception, no threshold increase.
- Toute exception restante doit porter une decision de permanence et une preuve.
- Si une page requiert arbitrage utilisateur, stopper au lieu de cacher la dette.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les entrees d'allowlist sont auditees individuellement et supprimees/conservees selon classification, sans migration par lots de consommateurs.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | `AstrologerProfilePage.tsx` exception | owner composant/feature | page route | test cible | line-count + allowlist diff | decision produit si permanent |
| B2 | `BirthProfilePage.tsx` exception | owner composant/feature | page route | test cible | line-count + allowlist diff | decision produit si permanent |
| B3 | `SubscriptionSettings.tsx` exception | owner settings/subscription | page route | test cible | line-count + allowlist diff | blocker si copy/contrat change |
| B4 | `AdminSamplePayloadsAdmin.tsx` stale | remove stale entry or owner exact | page route | guard architecture | stale proof | skip if below threshold |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before page-size inventory | `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/page-size-before.md` | Capturer baseline. |
| After page-size inventory | `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/page-size-after.md` | Prouver decisions finales. |
| Final evidence | `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/generated/10-final-evidence.md` | Conserver commandes, resultats, scans et blockers. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: `npm run test -- page-architecture`
  must fail if stale or broad page-size exceptions are reintroduced.
- Required architecture guard against reintroduction: `npm run test -- page-architecture`.
- Forbidden symbols are the deterministic source for stale page-size entries if they are reintroduced.
- Deterministic source: `frontend/src/tests/page-architecture-guards.test.ts` and `frontend/src/tests/page-architecture-allowlist.ts`.
- Required forbidden examples: wildcard exception, folder exception, threshold increase, unclassified permanent exception, hidden duplicate owner.
- Guard evidence: page-size before/after inventory, allowlist diff and page-architecture test.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md#F-002`
- Closure proof required: line-count before/after, per-page classification,
  exact `PAGE_SIZE_EXCEPTIONS` diff, page-architecture green, targeted tests.
- Known residual in-domain work: none
- Deferred non-domain concerns: none
- Full-closure rule: do not accept `PASS with limitation`, broad allowlists,
  wildcard exceptions, unclassified fallback, compatibility, legacy,
  migration-only, shim, alias, TODO, or hidden residual in-domain work.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md#E-004`
  reports the current line-counts for all target pages.
- Evidence 2: `frontend/src/tests/page-architecture-allowlist.ts` - `PAGE_SIZE_EXCEPTIONS` contains exact entries for the four page targets plus AdminPrompts.
- Evidence 3: `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md#E-007` - `npm run test -- page-architecture` passes but only controls growth, not closure.
- Evidence 4: `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-002` - candidate provides a finite page map and stop condition.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - `RG-064` and adjacent frontend invariants consulted before story scope was finalized.

## 6. Target State

- `PAGE_SIZE_EXCEPTIONS` contains no temporary page decomposition debt outside approved permanent-route-only exceptions.
- Every target page is below guard threshold or has an exact permanent-route-only rationale with no extractable section left.
- Extracted UI/feature sections live in canonical owners and are not duplicated in route pages.
- Page architecture guard and targeted page tests pass.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page-size exceptions and page architecture debt must remain exact or absent.
  - `RG-047` - extracted JSX must not introduce static inline styles.
  - `RG-049` - CSS movement must not reintroduce unclassified legacy style surfaces.
  - `RG-066` - this story establishes that non-AdminPrompts page-size debt is finite and must not grow silently.
- Non-applicable invariants:
  - `RG-054` - no admin route redirect or alias path is changed.
  - `RG-053` - no runtime payload compatibility mapper is changed.
- Required regression evidence:
  - `npm run test -- page-architecture`
  - `npm run lint`
  - targeted existing tests for each touched page or explicit skip with risk.
  - before/after line-count and allowlist artifacts.
- Allowed differences:
  - Component extraction, imports and exact allowlist changes tied to the four target pages.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory captures all target pages. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "AstrologerProfilePage" page-size-before.md`. |
| AC2 | Each page is classified before edits. | Evidence profile: `external_usage_blocker`; runtime evidence: AST guard; test: `npm run test -- page-architecture`. |
| AC3 | Extractable pages move to canonical owners. | Evidence profile: `batch_migration_mapping`; command: `rg -n "canonical-owner\|no-shim-proof" page-size-after.md`. |
| AC4 | Stale or closed page-size exceptions are removed. | Evidence profile: `allowlist_register_validated`; test: `npm run test -- page-architecture`. |
| AC5 | No threshold is increased. | Evidence profile: `reintroduction_guard`; test: `npm run test -- page-architecture`; diff: `page-architecture-allowlist.ts`. |
| AC6 | Touched page behavior remains covered. | Evidence profile: `runtime_behavior`; test: `npm run test -- AstrologerProfile BirthProfile SubscriptionSettings`. |
| AC7 | Final artifact states no residual temporary debt. | Evidence profile: `persistent_evidence`; command: `rg -n "Known residual in-domain work" page-size-after.md`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture detailed page-size baseline and classify each target page. (AC: AC1, AC2)
  - [x] Include current line count, allowlist row, route-only responsibilities and extractable candidates.
  - [x] Stop if any page is `needs-user-decision`.
- [x] Task 2 - Process `AstrologerProfilePage.tsx`. (AC: AC3, AC4, AC5, AC6)
  - [x] Extract or permanently classify with proof.
  - [x] Update focused tests if behavior surface is touched.
- [x] Task 3 - Process `BirthProfilePage.tsx`. (AC: AC3, AC4, AC5, AC6)
  - [x] Extract or permanently classify with proof.
  - [x] Avoid copy/paste component ownership.
- [x] Task 4 - Process `SubscriptionSettings.tsx`. (AC: AC3, AC4, AC5, AC6)
  - [x] Extract settings sections without changing subscription behavior or API contracts.
  - [x] Keep date/time formatting changes out of scope unless touched code already imports canonical helper without behavior change.
- [x] Task 5 - Reconcile `AdminSamplePayloadsAdmin.tsx`. (AC: AC1, AC4, AC5, AC7)
  - [x] Remove stale exception if below threshold.
  - [x] If still over threshold, extract a bounded admin-prompts sub-surface or stop with blocker.
- [x] Task 6 - Update guard evidence and after artifact. (AC: AC4, AC5, AC6, AC7)
  - [x] Record final line-counts, allowlist diff, tests and residual status.

## 9. Mandatory Reuse / DRY Constraints

- Reuse existing page-adjacent components and feature directories before creating new owners.
- Reuse existing API clients/hooks; do not move API calls into newly extracted UI components unless that is already the local owner pattern.
- Reuse existing CSS files/classes; no inline style migration or new design-system tokens unless strictly required by moved JSX and already present.
- Do not create a single shared component for unrelated pages unless identical behavior and API shape are proven.
- Shared abstraction allowed only when it removes duplication across target pages without blending product concepts.

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

- wildcard or folder-wide `PAGE_SIZE_EXCEPTIONS`.
- increasing existing `maxLines` values.
- `temporary` exception without exit condition.
- duplicate route page and component owner implementations for the same section.
- backend edits for a page-size-only story.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: page file is an active route owner and must not be deleted; only its stale allowlist entry may be removed after line-count proof.
- `external-active`: page or exception is referenced by public docs, generated links, navigation or external entry points; must not be removed without explicit user decision.
- `historical-facade`: allowlist entry delegates only to a former temporary threshold and has no current line-count need; it must be deleted from the allowlist.
- `dead`: allowlist entry is stale because the file is absent or below threshold with no permanent-route-only decision; it must be deleted from the allowlist.
- `needs-user-decision`: ambiguity remains after scans and must block deletion or permanent classification.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep`, `decompose`, `remove-allowlist-if-below-threshold` | Must not delete the page; may remove only stale governance entry. |
| `external-active` | `keep`, `needs-user-decision` | Must not delete page or external path without explicit user decision. |
| `historical-facade` | `delete-allowlist-entry`, `needs-user-decision` | Must delete stale allowlist entry when no blocker remains. |
| `dead` | `delete-allowlist-entry` | Must delete stale allowlist entry. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/page-size-before.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Route shell per target page | original page route file | extracted feature/UI internals kept in page |
| Reusable profile/settings/admin sections | existing owner under components/features or page-adjacent module | oversized page with temporary exception |
| Page-size governance | `frontend/src/tests/page-architecture-allowlist.ts` and `frontend/src/tests/page-architecture-guards.test.ts` | hidden reviewer memory or broad allowlist |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed from `PAGE_SIZE_EXCEPTIONS`.

Forbidden:

- replacing a stale exact entry with a broader entry;
- increasing `maxLines`;
- preserving a temporary exception through a renamed owner;
- adding a compatibility alias for a page-size exception;
- replacing deletion with soft-disable behavior.
- preserving a wrapper;
- preserving a re-export;

## 15. External Usage Blocker

If a page or exception is classified as `external-active`, it must not be deleted.
The dev agent must stop or record an explicit user decision with deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-002`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- Existing tests covering the touched pages under `frontend/src/tests/**`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/AstrologerProfilePage.tsx` - extract or classify route-only responsibilities.
- `frontend/src/pages/BirthProfilePage.tsx` - extract or classify route-only responsibilities.
- `frontend/src/pages/settings/SubscriptionSettings.tsx` - extract or classify settings sections.
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` - remove stale exception or extract if still over threshold.
- `frontend/src/components/**` - possible canonical owners if existing architecture points there.
- `frontend/src/features/**` - possible canonical owners if existing architecture points there.
- `frontend/src/tests/page-architecture-allowlist.ts` - remove or reclassify page-size exceptions.

Likely tests:

- `frontend/src/tests/page-architecture-guards.test.ts` - guard should pass; update only if exact exception model changes.
- Existing page tests for `AstrologerProfilePage`, `BirthProfilePage`, `SubscriptionSettings`, or `AdminSamplePayloadsAdmin`.
- New focused tests under `frontend/src/tests/**` only for extracted behavior lacking coverage.

Files not expected to change:

- `backend/**` - no backend contract change.
- `frontend/src/api/**` - no API owner change expected.
- `frontend/package.json` - existing scripts are sufficient.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture
npm run test -- AstrologerProfile BirthProfile SubscriptionSettings AdminSamplePayloads
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: extraction changes visible page composition or settings behavior.
  - Guardrail: targeted page tests and no behavior change allowed.
- Risk: one page remains as hidden temporary debt.
  - Guardrail: full-closure AC7 and exact allowlist diff.
- Risk: broad abstraction mixes unrelated page concepts.
  - Guardrail: ownership classification per page and DRY constraints.
- Risk: page-size guard remains green but stale exceptions hide closure.
  - Guardrail: before/after artifacts must classify every exception and stale entries.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated refactors.
- Do not increase thresholds, add wildcard exceptions or hide permanent route-owner decisions.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work for this full-closure story.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-002` - source candidate and finite page map.
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md#F-002` - source finding.
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md` - page-size evidence and guard results.
- `frontend/src/tests/page-architecture-allowlist.ts` - current exception register.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
