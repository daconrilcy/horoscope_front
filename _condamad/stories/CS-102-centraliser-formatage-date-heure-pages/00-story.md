# Story CS-102 centraliser-formatage-date-heure-pages: Centraliser le formatage date/heure inline des pages

Status: done

## 1. Objective

Fermer la duplication de formatage date/heure dans les pages React.
Les affichages UI partages doivent passer par `frontend/src/utils/formatDate.ts`.
Les appels numeriques `toLocaleString()` doivent etre exclus apres classification.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-003`
- Reason for change: `F-003` indique que les helpers nommes ont ete centralises par CS-098.
  Des appels inline `new Date(value).toLocaleString()`, `toLocaleDateString()`
  et `Intl.DateTimeFormat(options)` restent dupliques dans les pages.

## 3. Domain Boundary

- Domain: `frontend-react-pages/page-helpers`
- In scope:
  - Construire l'inventaire before depuis la selection exacte date/time indiquee dans le plan de validation.
  - Classer chaque hit en `date-time-ui`, `numeric-only`, `canonical-consumer`, `page-specific-retained` ou `out-of-scope`.
  - Remplacer les hits `date-time-ui` partages par `formatDate`, `formatDateTime` ou `formatDateWithOptions`.
  - Etendre `frontend/src/utils/formatDate.ts` uniquement si l'output actuel ne peut pas etre preserve par les helpers existants.
  - Mettre a jour `frontend/src/tests/formatDate.test.ts` si le helper change.
- Out of scope:
  - Modifier les formats de montant, quotas ou nombres purs.
  - Decomposer les pages volumineuses, couvert par `CS-101`.
  - Modifier les contrats API ou les schemas.
  - Revoir le copy produit ou le design.
- Explicit non-goals:
  - Ne pas transformer des appels numeriques `toLocaleString()` en format date.
  - Ne pas creer de wrapper page-local autour du helper canonique.
  - Ne pas changer un format visible si le helper canonique ne le preserve pas; stopper avec blocker.
  - Ne pas affaiblir `RG-064` sur l'architecture des pages.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: les responsabilites de formatage date/heure quittent les pages vers l'owner utilitaire canonique.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: un format visible page-specific doit rester different et ne peut pas etre exprime par le helper canonique sans modifier le comportement.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Aucun runtime API/route n'est modifie; les tests frontend et scans sont suffisants. |
| Baseline Snapshot | yes | Chaque hit inline doit etre inventorie avant/apres. |
| Ownership Routing | yes | Le formatage date/heure partage doit appartenir a `formatDate.ts`. |
| Allowlist Exception | yes | Les hits retenus doivent etre classes exactement; aucune exception large. |
| Contract Shape | no | Aucun DTO, payload, schema ou contrat HTTP n'est change. |
| Batch Migration | yes | Plusieurs pages sont migrees par lots independants depuis un scan fini. |
| Reintroduction Guard | yes | Les appels date/time inline partages ne doivent pas revenir sans classification. |
| Persistent Evidence | yes | L'inventaire before/after doit etre persiste. |

## 4b. Runtime Source of Truth

- Runtime Source of Truth: not applicable
- Reason: le changement concerne du formatage frontend local; aucune route runtime, OpenAPI, config chargee ou schema genere n'est touche.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/date-time-format-before.md`.
- Comparison after implementation: `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/date-time-format-after.md`.
- Required baseline content: resultat complet du scan, classification de chaque hit, output attendu, helper cible ou raison de retention.
- Expected invariant: aucun formatage date/heure UI partage ne reste implemente inline dans les pages.
- Allowed differences: remplacement par imports canoniques et tests associes; output visible equivalent requis.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Date UI simple | `frontend/src/utils/formatDate.ts` / `formatDate` | `new Date(value).toLocaleDateString()` inline en page |
| Date/heure UI standard | `frontend/src/utils/formatDate.ts` / `formatDateTime` | `new Date(value).toLocaleString()` inline en page |
| Date avec options explicites | `frontend/src/utils/formatDate.ts` / `formatDateWithOptions` ou variante testee | `Intl.DateTimeFormat(options)` inline en page |
| Nombre/monnaie/quota | owner numerique existant ou classification `numeric-only` | migration vers helper date |

Rules:
- Classer avant modification; ne pas editer les hits `numeric-only` sauf pour les marquer dans l'artefact.
- Etendre `formatDate.ts` seulement avec docstring/commentaire francais et tests si les helpers existants ne preservent pas l'output.
- Les imports doivent venir du helper canonique, pas d'un alias local.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `date-time-format-after.md` | `page-specific-retained` date/time hits | format propre a une page | expire si le meme format apparait ailleurs |
| `date-time-format-after.md` | `numeric-only` hits | appels `toLocaleString()` numeriques hors domaine date/time | permanent tant que la selection rule les capture |

Rules:
- No wildcard, no folder-wide exception, no unclassified remaining hit.
- A retained date/time hit must include file, line, reason and blocker/owner.
- Numeric hits must not be counted as closure residue.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | Admin date/time hits | `formatDate.ts` helpers | admin pages | `formatDate.test.ts` if helper changes | zero unowned date/time | blocker if format cannot be preserved |
| B2 | Settings date/time hits | `formatDate.ts` helpers | settings pages | `formatDate.test.ts` if helper changes | zero unowned date/time | blocker if copy needs decision |
| B3 | Numeric-only scan hits | no date helper migration | numeric consumers classified only | no helper test | after artifact marks `numeric-only` | none |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before date/time inventory | `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/date-time-format-before.md` | Capturer scan complet et classification initiale. |
| After date/time inventory | `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/date-time-format-after.md` | Prouver canonicalisation ou classification exacte. |
| Final evidence | `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/generated/10-final-evidence.md` | Conserver commandes, resultats, scans et blockers. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: final scan must classify every remaining hit; any unclassified `date-time-ui` hit fails the story.
- Deterministic source: exact `rg` selection rule over `frontend/src/pages/**/*.tsx` plus helper tests.
- Required forbidden examples:
  - direct `new Date(value).toLocaleString()` for shared UI;
  - direct `new Date(value).toLocaleDateString()` for shared UI;
  - inline `Intl.DateTimeFormat` when `formatDateWithOptions` covers it;
  - page-local wrapper aliases.
- Guard evidence: after inventory, `npm run test -- formatDate page-architecture`, and final scan.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md#F-003`
- Closure proof required: before/after scan, classification of every hit, helper tests if `formatDate.ts` changes, final targeted scan with no unowned `date-time-ui`.
- Known residual in-domain work: none
- Deferred non-domain concerns: none
- Full-closure rule: do not accept `PASS with limitation`, broad allowlists,
  wildcard exceptions, unclassified fallback, compatibility, legacy,
  migration-only, shim, alias, TODO, or hidden residual in-domain work.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md#E-009` - direct UI date/time formatting remains in admin and settings pages.
- Evidence 2: `frontend/src/utils/formatDate.ts` - canonical helpers `formatDate`, `formatDateTime`, and `formatDateWithOptions` already exist.
- Evidence 3: `frontend/src/tests/formatDate.test.ts` - canonical date helper tests already exist.
- Evidence 4: `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-003` - candidate gives exact scan rule and high-confidence files.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - `RG-064` and adjacent frontend invariants consulted before story scope was finalized.

## 6. Target State

- Every date/time UI formatting hit in `frontend/src/pages/**/*.tsx` is canonical, classified page-specific, numeric-only, or outside the selection rule.
- Shared date/time formatting is implemented in `frontend/src/utils/formatDate.ts` and covered by tests.
- No page-local wrapper or alias preserves old inline formatting for convenience.
- Final inventory records all remaining hits with exact reason.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture must not regain duplicate helper ownership or TS/API bypasses.
  - `RG-067` - this story establishes canonical date/time UI formatting through `frontend/src/utils/formatDate.ts`.
- Non-applicable invariants:
  - `RG-047` - no style surface should be touched by this helper-only story.
  - `RG-054` - no route aliases or redirects are touched.
  - `RG-053` - no runtime payload compatibility mapper is touched.
- Required regression evidence:
  - `npm run test -- formatDate page-architecture`
  - `npm run lint`
  - final targeted scan and classification inventory.
- Allowed differences:
  - Imports and helper calls replacing equivalent inline date/time formatting only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory classifies every scan hit. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "date-time-ui\|numeric-only" date-time-format-before.md`. |
| AC2 | Shared date/time UI hits use canonical helpers. | Evidence profile: `ownership_routing`; command: `rg -n "canonical-owner" date-time-format-after.md`. |
| AC3 | Helper behavior is tested whenever `formatDate.ts` changes. | Evidence profile: `runtime_behavior`; test: `npm run test -- formatDate`; after artifact names new tests. |
| AC4 | Remaining scan hits are fully classified. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "unowned" date-time-format-after.md` returns zero. |
| AC5 | Frontend lint remains green. | Evidence profile: `reintroduction_guard`; test: `npm run lint`. |
| AC6 | Visible date/time output is preserved or blocked. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "Allowed differences" date-time-format-after.md`. |
| AC7 | Page architecture remains green. | Evidence profile: `reintroduction_guard`; test: `npm run test -- page-architecture`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture and classify the before scan. (AC: AC1)
  - [x] Run the exact selection rule.
  - [x] Mark every hit as `date-time-ui`, `numeric-only`, `canonical-consumer`, `page-specific-retained`, or `out-of-scope`.
- [x] Task 2 - Replace admin page shared date/time hits with canonical helpers. (AC: AC2, AC3, AC4, AC6)
  - [x] Prioritize audit high-confidence files:
    `AdminAiGenerationsPage.tsx`, `AdminLogsPage.tsx`,
    `AdminPromptsPage.tsx`, `AdminSupportPage.tsx`,
    `AdminUserDetailPage.tsx`, `AdminUsersPage.tsx`.
  - [x] Do not modify numeric-only hits in `AdminDashboardPage.tsx`.
- [x] Task 3 - Replace settings page shared date/time hits with canonical helpers. (AC: AC2, AC3, AC4, AC6)
  - [x] Inspect `SubscriptionSettings.tsx` and `UsageSettings.tsx`.
  - [x] Keep numeric formatting helper behavior out of scope.
- [x] Task 4 - Extend `formatDate.ts` only if required for behavior preservation. (AC: AC2, AC3, AC6)
  - [x] Add French docstrings/comments for non-trivial public helper changes.
  - [x] Update `formatDate.test.ts`.
- [x] Task 5 - Produce after inventory and run validation. (AC: AC4, AC5, AC6)
  - [x] Record every remaining scan hit and classification.
  - [x] Persist commands and outcomes in final evidence.

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/utils/formatDate.ts` for shared date/time formatting.
- Reuse existing helpers before adding a new one.
- Do not create per-page wrappers such as local `formatTimestamp` if they only call a canonical helper.
- Do not fold numeric formatting into date helpers.
- Shared abstraction allowed only when it preserves current output for at least two consumers or provides an exact option-based canonical helper.

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

- unclassified `new Date(value).toLocaleString()` for date/time UI in `frontend/src/pages/**/*.tsx`.
- unclassified `new Date(value).toLocaleDateString()` for date/time UI in `frontend/src/pages/**/*.tsx`.
- unclassified `Intl.DateTimeFormat(options)` for page UI when canonical helper can express the format.
- page-local wrapper aliases around `formatDate.ts`.
- edits that change numeric-only formatting in this story.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Shared date UI formatting | `frontend/src/utils/formatDate.ts` / `formatDate` | page-local `new Date(value).toLocaleDateString()` |
| Shared date/time UI formatting | `frontend/src/utils/formatDate.ts` / `formatDateTime` | page-local `new Date(value).toLocaleString()` |
| Date/time UI formatting with options | `frontend/src/utils/formatDate.ts` / `formatDateWithOptions` or exact tested extension | page-local `Intl.DateTimeFormat(options)` |
| Numeric formatting | existing numeric owner or page-specific classification | date helper migration |

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
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-003`
- `frontend/src/utils/formatDate.ts`
- `frontend/src/tests/formatDate.test.ts`
- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/AdminLogsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- `frontend/src/pages/admin/AdminUserDetailPage.tsx`
- `frontend/src/pages/admin/AdminUsersPage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/settings/UsageSettings.tsx`
- Any additional `frontend/src/pages/**/*.tsx` hit from the exact scan rule.

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx` - replace timestamp formatting with canonical helper.
- `frontend/src/pages/admin/AdminLogsPage.tsx` - replace log/event timestamp formatting with canonical helper.
- `frontend/src/pages/admin/AdminPromptsPage.tsx` - replace consumption/release timestamp formatting with canonical helper only; no page decomposition here.
- `frontend/src/pages/admin/AdminSupportPage.tsx` - replace support date/time formatting with canonical helper.
- `frontend/src/pages/admin/AdminUserDetailPage.tsx` - replace user/ticket/event date/time formatting with canonical helper.
- `frontend/src/pages/admin/AdminUsersPage.tsx` - replace user date formatting with canonical helper.
- `frontend/src/pages/settings/SubscriptionSettings.tsx` - replace date/time formatting only if scan classifies hits as date/time UI.
- `frontend/src/pages/settings/UsageSettings.tsx` - replace or classify `Intl.DateTimeFormat` date/time helper.
- `frontend/src/utils/formatDate.ts` - extend only when current helpers cannot preserve output.

Likely tests:

- `frontend/src/tests/formatDate.test.ts` - update if `formatDate.ts` changes.
- Existing focused tests for touched pages only if replacing formatting exposes behavior not covered by helper tests.
- `frontend/src/tests/page-architecture-guards.test.ts` - should pass; no change expected.

Files not expected to change:

- `backend/**` - no backend contract change.
- `frontend/src/tests/page-architecture-allowlist.ts` - no page-size/API/TS bypass exception change expected.
- `frontend/package.json` - existing scripts are sufficient.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- formatDate page-architecture
rg -n "new Date\\([^\\n]+\\)\\.toLocale(DateString|String)|Intl\\.DateTimeFormat|\\.toLocaleString\\(" src/pages -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: helper replacement changes locale/dateStyle/timeStyle output.
  - Guardrail: behavior change not allowed; helper tests and after artifact must prove allowed differences `none`.
- Risk: numeric `toLocaleString()` hits are accidentally migrated as dates.
  - Guardrail: AC1 requires numeric-only classification before edits.
- Risk: local wrappers hide duplicate formatting ownership.
  - Guardrail: No Legacy section forbids page-local wrapper aliases.
- Risk: scan still shows hits but they are not classified.
  - Guardrail: AC4 fails any unclassified remaining hit.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated refactors.
- Do not edit numeric-only formatting except to classify it in artifacts.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work for this full-closure story.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md#SC-003` - source candidate and exact scan rule.
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md#F-003` - source finding.
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md#E-009` - current date/time duplication evidence.
- `frontend/src/utils/formatDate.ts` - canonical helper owner.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
