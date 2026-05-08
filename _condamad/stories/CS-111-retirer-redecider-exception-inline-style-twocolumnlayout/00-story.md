# Story CS-111 retirer-redecider-exception-inline-style-twocolumnlayout: Retirer ou redecider l'exception inline style de TwoColumnLayout

Status: done

## 1. Objective

Fermer le finding layout sur `TwoColumnLayout` en supprimant l'ecriture inline
de `--sidebar-width` quand les consommateurs actuels peuvent utiliser des
variants CSS finis, ou en produisant une decision explicite avec owner et
condition de sortie si un besoin runtime arbitraire est prouve.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md#SC-302`
- Reason for change: `TwoColumnLayout.tsx` conserve un `style=` allowliste dans
  le domaine layout alors que la regle repository interdit les styles inline.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-layouts`
- In scope:
  - Auditer tous les consommateurs `TwoColumnLayout` et `sidebarWidth`.
  - Remplacer l'inline style par classes ou attributs CSS si les largeurs sont finies.
  - Retirer les entrees allowlist layout quand l'inline style disparait.
  - Produire une decision persistante si la largeur arbitraire reste requise.
- Out of scope:
  - Migrer les autres exceptions inline style hors `frontend/src/layouts/**`.
  - Refondre les pages consommatrices au-dela de l'appel layout.
  - Changer la hierarchie des routes ou les owners pages.
  - Modifier le design-system global hors variables necessaires au layout.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047`, `RG-050` ou `RG-068`.
  - Ne pas ajouter de nouvelle allowlist large.
  - Ne pas conserver une compatibility facade, un legacy alias ou un fallback silencieux.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: l'inline custom property est une surface d'exception qui
  contourne la regle canonique CSS-owned styling.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: remplacer le pilotage de largeur par variants CSS equivalants.
  - Autorise: bloquer et documenter une decision si un besoin arbitraire est prouve.
  - Interdit: changer le layout visuel attendu des consommateurs actuels.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un consommateur actif exige une valeur `sidebarWidth`
  arbitraire non representable par des variants CSS finis.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les consommateurs TSX et les tests inline-style/design-system prouvent l'usage effectif. |
| Baseline Snapshot | yes | L'inventaire avant/apres des consommateurs et allowlists doit etre auditable. |
| Ownership Routing | yes | La responsabilite largeur doit etre routee vers CSS ou decision owner explicite. |
| Allowlist Exception | yes | Les entrees allowlist inline-style doivent etre retirees ou redecidees exactement. |
| Contract Shape | no | Aucun contrat API ou type public externe n'est change. |
| Batch Migration | no | La migration est limitee au layout et a ses consommateurs directs. |
| Reintroduction Guard | yes | Le retour du `style=` layout doit faire echouer les guards. |
| Persistent Evidence | yes | La classification des consommateurs et la decision doivent etre conservees. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard executed by `npm run test -- inline-style design-system`.
  - Consumer inventory from `rg -n "TwoColumnLayout|sidebarWidth|--sidebar-width|style=" frontend/src`.
- Secondary evidence:
  - `frontend/src/layouts/TwoColumnLayout.tsx`
  - `frontend/src/layouts/TwoColumnLayout.css`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Static scans alone are not sufficient because:
  - A scan can list occurrences, but the guard suite proves whether the
    repository policy still permits or rejects the inline style.
- Command:
  - `npm run test -- inline-style design-system`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/twocolumnlayout-inline-style-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/twocolumnlayout-inline-style-after.md`
- Required baseline content:
  - current `TwoColumnLayout` inline style hit;
  - current allowlist rows;
  - current consumers and `sidebarWidth` values.
- Expected invariant:
  - zero hidden layout inline style, or one explicit owner decision with exit condition.
- Allowed differences:
  - CSS-owned variants replacing current width values;
  - removal of layout allowlist entries;
  - decision artifact when arbitrary runtime width is proven.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Default two-column sidebar width | `frontend/src/layouts/TwoColumnLayout.css` | inline `style=` in TSX |
| Finite width variants | CSS class or data attribute in `TwoColumnLayout.css` | arbitrary custom property write |
| Runtime arbitrary width decision | CS-111 decision artifact with owner and exit condition | undocumented allowlist row |
| Inline-style policy | `frontend/src/tests/inline-style-allowlist.ts` guard | wildcard or folder-wide bypass |

Rules:

- Every active `sidebarWidth` consumer must be classified.
- A removable inline style must be deleted, not moved to another wrapper.
- A retained exception must name owner, reason, and exit condition.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `inline-style-allowlist.ts` | `TwoColumnLayout.tsx` `style=` | Current exception under review. | Expires with CS-111 unless arbitrary width is proven. |
| `design-system-allowlist.ts` | `--sidebar-width` inline custom property | Current design-system exception under review. | Expires with CS-111 unless arbitrary width is proven. |

Rules:

- no wildcard;
- no folder-wide exception;
- no new layout inline style entry;
- no retained row without owner and exit condition.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, HTTP response, payload, generated client, DTO, or exported
  frontend contract is changed.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: the scope is a single layout primitive plus exact direct consumers.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline inventory | `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/before.md` | Capturer consommateurs et allowlists. |
| Closure inventory | `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/after.md` | Prouver suppression ou decision. |
| Decision record | `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/decision.md` | Requis si largeur arbitraire reste necessaire. |

## 4i. Reintroduction Guard

The implementation must add or preserve an architecture guard so layout inline
styles cannot be reintroduced silently.

Deterministic guard sources:

- forbidden symbols
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/layouts/TwoColumnLayout.tsx`

Required forbidden examples:

- `style={{ '--sidebar-width': sidebarWidth }}`
- broad allowlist entry for `frontend/src/layouts`
- retained `--sidebar-width` exception without owner and exit condition

Guard evidence:

- `npm run test -- inline-style design-system`
- targeted `rg` scans in the validation plan

## 4j. Source Finding Closure

- Closure status: blocked
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md#F-302`
- Closure proof required: consumer inventory, before/after artifact, guard tests,
  and either zero inline style hit or explicit owner decision artifact.
- Known residual in-domain work: none after either deletion or explicit decision artifact.
- Deferred non-domain concerns: inline-style exceptions outside `frontend/src/layouts/**`.
- Blocker decision: arbitrary runtime sidebar width support must be decided if
  scans show consumers cannot use finite CSS variants.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md` - E-007 records `style={{ '--sidebar-width': sidebarWidth }}`.
- Evidence 2: `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md` - F-302 classifies the surface as layout-owned inline style debt.
- Evidence 3: `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md` - SC-302 requires consumer inspection and removal or renewed decision.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-047`, `RG-050`, and `RG-068` were consulted before scope was finalized.

## 6. Target State

After implementation:

- Every `TwoColumnLayout` consumer has a recorded width classification.
- `TwoColumnLayout.tsx` has no inline `style=` when finite CSS variants cover current needs.
- Inline-style and design-system allowlists no longer contain the layout exception when remediated.
- If arbitrary width remains required, `sidebar-width-decision.md` records owner, reason, evidence, and exit condition.
- No broad layout inline-style bypass exists.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - static inline styles are forbidden and dynamic exceptions must be exact.
  - `RG-050` - design-system exceptions must stay exact and source-backed.
  - `RG-068` - layout hierarchy must not be altered while changing layout primitives.
- Non-applicable invariants:
  - `RG-064` - page architecture registry is not modified.
  - `RG-048` - CSS fallback classification is not the target of this story.
- Required regression evidence:
  - `npm run test -- inline-style design-system`
  - `npm run test -- page-architecture layout`
  - targeted scans for `TwoColumnLayout`, `sidebarWidth`, `--sidebar-width`, and `style=`
- Allowed differences:
  - CSS-owned sidebar width variants or an explicit retained-decision artifact.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `TwoColumnLayout` consumers are inventoried. | Evidence profile: `baseline_before_after_diff`; command `rg -n "TwoColumnLayout|sidebarWidth" frontend/src`. |
| AC2 | Remediable width usage is CSS-owned. | Evidence profile: `ast_architecture_guard`; command `npm run test -- inline-style design-system`; inspect `TwoColumnLayout.css`. |
| AC3 | Layout inline-style allowlists are removed after remediation. | Evidence profile: `allowlist_register_validated`; command `rg -n "TwoColumnLayout" frontend/src/tests`. |
| AC4 | Required arbitrary width has an approved decision record. | Evidence profile: `external_usage_blocker`; command `npm run test -- inline-style design-system`. |
| AC5 | Inline-style guard passes for the layout surface. | Evidence profile: `reintroduction_guard`; command `npm run test -- inline-style design-system`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture the current inline-style baseline. (AC: AC1)
  - [x] Write `twocolumnlayout-inline-style-before.md` with consumer hits and allowlist rows.

- [x] Task 2 - Classify width requirements. (AC: AC1, AC4)
  - [x] Mark each consumer as default, finite variant, or arbitrary runtime.
  - [x] Stop and write `sidebar-width-decision.md` if arbitrary runtime width is required.

- [x] Task 3 - Remove remediable inline style path. (AC: AC2, AC3)
  - [x] Move finite width behavior into `TwoColumnLayout.css`.
  - [x] Remove obsolete allowlist entries after `style=` disappears.

- [x] Task 4 - Harden guards and record after state. (AC: AC3, AC4, AC5)
  - [x] Ensure guards fail on unapproved layout inline styles.
  - [x] Write `twocolumnlayout-inline-style-after.md` with final proof.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/layouts/TwoColumnLayout.css` as the owner of visual layout width.
  - `frontend/src/tests/inline-style-allowlist.ts` as the single inline-style policy registry.
  - `frontend/src/tests/design-system-allowlist.ts` as the single design-system exception registry.
- Do not recreate:
  - another inline-style allowlist;
  - another two-column layout component;
  - a wrapper that only preserves the old inline custom property path.
- Shared abstraction allowed only when:
  - two or more current consumers need the same named CSS variant.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `style={{ '--sidebar-width': sidebarWidth }}`
- broad `frontend/src/layouts` inline-style allowlist
- `--sidebar-width` allowlist row without owner and exit condition
- new `TwoColumnLayout` wrapper preserving the old behavior

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, clients, or audit evidence.
- `historical-facade`: item exists only to preserve an older style surface.
- `dead`: item has zero references in production code, tests, docs, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table in `twocolumnlayout-inline-style-after.md`:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `TwoColumnLayout.tsx style=` | inline style | `historical-facade` | exact consumers | CSS variants | `delete` | scan and tests | visual drift |

Allowed decisions in the audit are `keep`, `delete`, `replace-consumer`, and
`needs-user-decision`; only the row classification determines which one is valid.

Audit output path:

- `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/twocolumnlayout-inline-style-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Sidebar width styling | `frontend/src/layouts/TwoColumnLayout.css` | inline `style=` custom property |
| Inline-style policy | `frontend/src/tests/inline-style-allowlist.ts` | untracked local bypass |
| Design-system style policy | `frontend/src/tests/design-system-allowlist.ts` | untracked custom property bypass |
| Arbitrary runtime width decision | CS-111 decision artifact | implicit retained exception |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated inline style active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If arbitrary runtime width is classified as `external-active` or
`needs-user-decision`, it must not be deleted. The dev agent must stop for a
user decision or write `sidebar-width-decision.md` with exact consumer evidence,
owner, reason, exit condition, and deletion risk.

## 17. Generated Contract Check

- Generated contract check: active for removal validator.
- Reason: no API client is generated, but the public frontend source contract
  must prove absence of the removed inline style surface.
- Required generated-contract evidence:
  - source route manifest impact: none, proven by `npm run test -- page-architecture layout`;
  - generated client/schema impact: none, no generated client files are touched;
  - public frontend contract impact: `rg -n "TwoColumnLayout|--sidebar-width|style=" frontend/src`.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/layouts/TwoColumnLayout.tsx` - remove inline style or keep only after decision artifact.
- `frontend/src/layouts/TwoColumnLayout.css` - add CSS-owned width variants.
- `frontend/src/tests/inline-style-allowlist.ts` - remove or redecide the exact row.
- `frontend/src/tests/design-system-allowlist.ts` - remove or redecide the exact row.
- `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/twocolumnlayout-inline-style-before.md` - baseline.
- `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/twocolumnlayout-inline-style-after.md` - closure proof.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - guard policy coverage.
- `frontend/src/tests/inline-style-allowlist.ts` - policy data consumed by inline-style tests.
- Existing or new `frontend/src/tests/*TwoColumnLayout*.test.tsx` - layout behavior coverage when present or newly added.

Files not expected to change:

- `frontend/src/app/routes.tsx` - no route change.
- `frontend/src/tests/page-architecture-allowlist.ts` - no page owner change.
- `frontend/package.json` - no dependency or script change.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- inline-style design-system
npm run test -- page-architecture layout
Pop-Location
rg -n "TwoColumnLayout|sidebarWidth|--sidebar-width|style=" frontend/src
rg -n "TwoColumnLayout|--sidebar-width" frontend/src/tests/*allowlist.ts
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/00-story.md
```

## 22. Regression Risks

- Risk: consumers lose their intended sidebar width.
  - Guardrail: baseline and after inventories require every consumer to be classified.
- Risk: the inline style is moved to another wrapper.
  - Guardrail: removal sections forbid wrapper, alias, fallback, and soft-disable routes.
- Risk: the allowlist remains but no owner decision exists.
  - Guardrail: AC4 requires owner and exit condition for retained arbitrary runtime width.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md#SC-302` - source story candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md#F-302` - source finding.
- `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md#E-007` - inline-style evidence.
- `_condamad/stories/regression-guardrails.md` - shared guardrail registry.
