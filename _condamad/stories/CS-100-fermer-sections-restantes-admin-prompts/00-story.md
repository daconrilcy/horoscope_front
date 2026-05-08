# Story CS-100 fermer-sections-restantes-admin-prompts: Fermer les sections restantes de AdminPromptsPage

Status: done

## 1. Objective

Fermer la dette restante documentee par CS-096 dans `AdminPromptsPage.tsx`.
Les sections catalogue, consommation et release encore implementees dans la page
doivent aller vers des owners canoniques sous `frontend/src/features/admin-prompts`.
La page doit rester un conteneur de route: onglets, queries, navigation et composition.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-001`
- Reason for change: `F-001` indique que CS-096 a extrait une premiere tranche.
  `AdminPromptsPage.tsx` conserve encore les sections JSX catalogue,
  consommation et release classees `remaining-next-slice`.

## 3. Domain Boundary

- Domain: `frontend-react-pages/admin-prompts`
- In scope:
  - Reprendre la carte de fermeture `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md`.
  - Extraire les sections catalogue, consommation et release encore locales dans `AdminPromptsPage.tsx`, une section coherente a la fois.
  - Conserver les hooks, types et contrats existants de `frontend/src/api/adminPrompts.ts`.
  - Mettre a jour les tests AdminPrompts et l'allowlist page-size exacte.
  - Produire les inventaires before/after de fermeture dans ce dossier de story.
- Out of scope:
  - Modifier les contrats backend, endpoints admin LLM ou payloads API.
  - Traiter les autres pages volumineuses hors `AdminPromptsPage.tsx`.
  - Reconcevoir le parcours, le copy produit ou les styles hors mouvements strictement necessaires.
  - Centraliser le formatage date/heure inline, couvert par `CS-102`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064` sur l'architecture des pages React.
  - Ne pas rouvrir les protections design-system `RG-044` a `RG-063`.
  - Ne pas recreer `apiFetch(`, `@ts-nocheck` ou `@ts-ignore` dans les pages/features admin-prompts.
  - Ne pas conserver une copie locale de section extraite dans `AdminPromptsPage.tsx`.
  - Ne pas accepter de wildcard, exception dossier ou `PASS with limitation` pour `PAGE_SIZE_EXCEPTIONS`.

## 4. Operation Contract

- Operation type: split
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story deplace des responsabilites UI/feature hors d'une page route vers leurs owners canoniques.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une section exige un changement de contrat backend/API,
  un changement produit visible, ou une exception permanente non prouvee par la carte.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard Vitest `page-architecture` est la source executable de la politique page-size et des dettes page. |
| Baseline Snapshot | yes | La fermeture doit comparer line-count, section choisie, owner extrait et exception avant/apres. |
| Ownership Routing | yes | Chaque section doit etre routee vers un owner feature canonique. |
| Allowlist Exception | yes | `PAGE_SIZE_EXCEPTIONS` contient une exception exacte pour la page cible. |
| Contract Shape | no | Aucun DTO, payload ou schema API n'est change. |
| Batch Migration | no | La story traite une carte finie dans un seul domaine, pas une migration multi-domaines. |
| Reintroduction Guard | yes | Les sections extraites et dettes page interdites ne doivent pas revenir. |
| Persistent Evidence | yes | Les preuves before/after de fermeture doivent etre conservees. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard runtime artifact: `frontend/src/tests/page-architecture-guards.test.ts`.
  - `frontend/src/tests/page-architecture-guards.test.ts`
  - `frontend/src/tests/page-architecture-allowlist.ts`
- Secondary evidence:
  - `npm run test -- page-architecture`
  - `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow`
- Static scans alone are not sufficient because:
  - la politique de taille page et les dettes interdites doivent echouer dans Vitest, pas seulement dans une recherche texte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-before.md`.
- Comparison after implementation: `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md`.
- Required baseline content: line-count de `AdminPromptsPage.tsx`,
  entree `PAGE_SIZE_EXCEPTIONS`, sections ciblees, fonctions/state/JSX associes,
  et owner cible.
- Expected invariant: chaque section extraite a un seul owner actif et n'est plus implementee localement dans la page.
- Allowed differences: deplacement de code, imports, tests et CSS associes aux sections extraites uniquement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Shell de route AdminPrompts | `frontend/src/pages/admin/AdminPromptsPage.tsx` | logique UI interne catalogue/consommation/release |
| Section catalogue prompts | `frontend/src/features/admin-prompts/**` | JSX/table/detail catalogue dans la page route |
| Surface consommation | `frontend/src/features/admin-prompts/**` | state/rendering consommation dans la page route |
| Surface release | `frontend/src/features/admin-prompts/**` | rendu release ou historique release dans la page route |
| Contrats API admin prompts | `frontend/src/api/adminPrompts.ts` | construction endpoint ou `apiFetch(` en page |

Rules:
- Classer chaque section avant extraction: `route-only`, `feature-owner`, `needs-user-decision`.
- Les props de composants extraits doivent rester explicites et typees; ne pas passer un objet "bag" global de page si seules quelques valeurs sont requises.
- Les owners extraits ne doivent pas re-exporter une facade depuis `AdminPromptsPage.tsx`.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `page-architecture-allowlist.ts` | `PAGE_SIZE_EXCEPTIONS` / AdminPrompts | exception temporaire CS-096 | supprimer ou reclasser permanent-route-only |

Rules:
- Aucun wildcard, dossier entier ou hausse de seuil n'est autorise.
- Une exception restante doit citer exactement la section route-only restante et son stop condition.
- Si une section est `needs-user-decision`, l'implementation doit s'arreter avant de masquer la dette.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les trois sections appartiennent au meme domaine et la carte de fermeture est finite dans `admin-prompts-after.md`.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-before.md` | Capturer taille, exception, carte CS-096 et sections ciblees. |
| After inventory | `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md` | Prouver owners finaux, absence dans la page et etat de fermeture. |
| Final evidence | `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/generated/10-final-evidence.md` | Conserver commandes, resultats, scans et limites. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: `npm run test -- page-architecture`
  must fail if page debt, broad exception, TS bypass, direct API call or stale size entry returns.
- Deterministic source: `frontend/src/tests/page-architecture-guards.test.ts` and `frontend/src/tests/page-architecture-allowlist.ts`.
- Required forbidden examples: local duplicate section after extraction, `apiFetch(` in page, `@ts-ignore`, wildcard page-size exception, threshold increase without removal proof.
- Guard evidence: targeted AdminPrompts tests, page-architecture guard, final negative scans.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md#F-001`
- Closure proof required: before/after artifacts, line-count diff,
  section ownership table, absence proof in `AdminPromptsPage.tsx`,
  `PAGE_SIZE_EXCEPTIONS` diff, and targeted AdminPrompts/page-architecture tests.
- Known residual in-domain work: none
- Deferred non-domain concerns: none
- Full-closure rule: do not accept `PASS with limitation`, broad allowlists,
  wildcard exceptions, unclassified fallback, compatibility, legacy,
  migration-only, shim, alias, TODO, or hidden residual in-domain work.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1142/00-audit-report.md` - page at 2586 lines with three sections still local.
- Evidence 2: `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md` - `catalog`, `consumption`, `release` are `remaining-next-slice`.
- Evidence 3: `frontend/src/tests/page-architecture-allowlist.ts` - `PAGE_SIZE_EXCEPTIONS` still lists `pages/admin/AdminPromptsPage.tsx`.
- Evidence 4: `frontend/src/api/adminPrompts.ts` - audit candidate requires preserving existing query hooks/API contracts from this owner.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - `RG-064` and adjacent frontend guardrails consulted before story scope was finalized.

## 6. Target State

- `AdminPromptsPage.tsx` imports canonical feature owners for catalogue, consommation and release surfaces.
- The page owns only route shell responsibilities: tab selection, route-level query orchestration, navigation and composition.
- `PAGE_SIZE_EXCEPTIONS` has no temporary debt for `AdminPromptsPage.tsx`.
- Any remaining entry is permanent-route-only and proves no `remaining-next-slice`.
- AdminPrompts tests and page architecture guard pass without broad exceptions.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture exceptions, direct API page calls and TS bypasses must remain exact or absent.
  - `RG-047` - extracted JSX/CSS must not introduce static inline styles.
  - `RG-049` - extracted CSS must not recreate unclassified legacy style surfaces.
  - `RG-065` - this story establishes that AdminPrompts remaining sections are owned by feature owners, not the route page.
- Non-applicable invariants:
  - `RG-054` - no admin redirect or legacy route alias is changed.
  - `RG-053` - no runtime payload compatibility mapper is changed.
- Required regression evidence:
  - `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture`
  - `npm run lint`
  - scans for `@ts-nocheck`, `@ts-ignore`, `apiFetch(` and retained local section markers.
- Allowed differences:
  - File ownership, imports, tests and CSS class ownership strictly tied to extracted sections.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory identifies residual sections. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "catalog\|consumption\|release" admin-prompts-before.md`. |
| AC2 | Each extracted section has one canonical owner. | Evidence profile: `batch_migration_mapping`; command: `rg -n "extracted-owner-path" admin-prompts-after.md`. |
| AC3 | Page no longer implements extracted sections locally. | Evidence profile: `repo_wide_negative_scan`; command: `rg -n "duplicate-active: none" admin-prompts-after.md`. |
| AC4 | API access remains routed through API owner. | Evidence profile: `targeted_forbidden_symbol_scan`; runtime evidence: AST guard; test: `npm run test -- page-architecture`. |
| AC5 | Page-size governance is closed for AdminPrompts. | Evidence profile: `allowlist_register_validated`; test: `npm run test -- page-architecture`. |
| AC6 | AdminPrompts visible behavior is preserved. | Evidence profile: `runtime_behavior`; test: `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow`. |
| AC7 | No page architecture bypass is introduced. | Evidence profile: `reintroduction_guard`; test: `npm run test -- page-architecture`; scan forbids TS bypass and `apiFetch(`. |

## 8. Implementation Tasks

- [x] Task 1 - Produce the detailed before inventory from CS-096 and current repo state. (AC: AC1)
  - [x] Record current line count, allowlist entry, and exact residual section boundaries.
  - [x] Mark each section as `feature-owner`, `route-only`, or `needs-user-decision`; stop on `needs-user-decision`.
- [x] Task 2 - Extract the catalog section to a canonical feature owner. (AC: AC2, AC3, AC4, AC6)
  - [x] Move JSX/helpers/state only for catalog responsibilities.
  - [x] Preserve imports from `frontend/src/api/adminPrompts.ts`.
- [x] Task 3 - Extract the consumption section to a canonical feature owner. (AC: AC2, AC3, AC4, AC6)
  - [x] Preserve current filtering, labels and row interactions.
  - [x] Avoid page-local duplicate helper copies.
- [x] Task 4 - Extract the release section to a canonical feature owner. (AC: AC2, AC3, AC4, AC6)
  - [x] Preserve release history and action behavior.
  - [x] Keep route-only orchestration in the page.
- [x] Task 5 - Tighten page architecture governance. (AC: AC5, AC7)
  - [x] Remove or permanently reclassify the AdminPrompts page-size exception.
  - [x] Run the page architecture guard and forbidden scans.
- [x] Task 6 - Write after inventory and final evidence. (AC: AC1, AC2, AC3, AC5, AC6, AC7)
  - [x] Record owner paths, page absence proof, allowlist diff, test output and residual status `none`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/api/adminPrompts.ts` for all admin prompts API contracts and hooks.
- Reuse existing `frontend/src/features/admin-prompts/**` patterns before adding new files.
- Reuse `AdminPromptsPage.css` class conventions or move classes to an appropriate feature CSS owner only when ownership moves with JSX.
- Do not create a generic catch-all `AdminPromptsSections` dumping ground unless it has named exports with clear section ownership.
- Shared abstraction allowed only if it removes a concrete duplicate across the extracted sections.

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

- `apiFetch(` in `frontend/src/pages/admin/AdminPromptsPage.tsx` or `frontend/src/features/admin-prompts/**`.
- `@ts-nocheck` and `@ts-ignore` in the touched AdminPrompts files.
- wildcard or folder-wide `PAGE_SIZE_EXCEPTIONS`.
- new compatibility re-export from `AdminPromptsPage.tsx`.
- copied catalog, consumption or release JSX remaining in the page after extraction.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin prompts route shell | `frontend/src/pages/admin/AdminPromptsPage.tsx` | feature section internals in page |
| Catalog UI and detail/table surface | `frontend/src/features/admin-prompts/**` | catalog JSX/state/helper blocks in page |
| Consumption UI surface | `frontend/src/features/admin-prompts/**` | consumption JSX/state/helper blocks in page |
| Release UI surface | `frontend/src/features/admin-prompts/**` | release JSX/state/helper blocks in page |
| Admin prompts API contracts | `frontend/src/api/adminPrompts.ts` | page-local API calls |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-001`
- `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/features/admin-prompts/**`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/admin/AdminPromptsPage.tsx` - remove catalog, consumption and release implementation details; keep route composition.
- `frontend/src/features/admin-prompts/**` - add or extend canonical feature owners for the extracted sections.
- `frontend/src/pages/admin/AdminPromptsPage.css` - only if CSS ownership must follow moved JSX.
- `frontend/src/tests/page-architecture-allowlist.ts` - remove or reclassify AdminPrompts page-size exception.

Likely tests:

- `frontend/src/tests/AdminPromptsPage.test.tsx` - route/page behavior after section extraction.
- `frontend/src/tests/AdminPromptsRouting.test.tsx` - route continuity.
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx` - catalog continuity.
- `frontend/src/tests/page-architecture-guards.test.ts` - guard remains green.

Files not expected to change:

- `backend/**` - no backend contract change.
- `frontend/src/api/adminPrompts.ts` - no API contract change expected; only inspect/reuse.
- `frontend/package.json` - existing scripts are sufficient.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture
rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" src/pages/admin/AdminPromptsPage.tsx src/features/admin-prompts -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: section extraction changes tab state, filters or selected row behavior.
  - Guardrail: targeted AdminPrompts tests and no behavior change allowed.
- Risk: code is moved but page keeps a duplicate local implementation.
  - Guardrail: after inventory owner mapping plus targeted page absence scans.
- Risk: the size exception is retained as temporary hidden debt.
  - Guardrail: AC5 requires removal or permanent route-only reclassification with no residual work.
- Risk: CSS movement introduces inline style or legacy style drift.
  - Guardrail: `RG-047`, `RG-049`, lint and page tests.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated refactors.
- Do not bypass extraction through wrapper, alias, fallback, re-export or page-local copy.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work for this full-closure story.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-001` - source candidate and draft.
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md#F-001` - source finding.
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md` - line counts, guards and scans.
- `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md` - finite closure map.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
