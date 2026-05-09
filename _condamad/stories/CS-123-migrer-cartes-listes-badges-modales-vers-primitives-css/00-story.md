# Story CS-123 migrer-cartes-listes-badges-modales-vers-primitives-css: Migrer cartes, listes, badges et modales vers les primitives App

Status: done

## 1. Objective

Converger les familles visuelles restantes de `App.css` vers les primitives et variantes generiques.
Le scope couvre cartes, panels, listes, badges/pills, avatars/media, modales et overlays.
Supprimer les anciens noms page-specific migres sans alias ni wrapper.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-003`
- Reason for change: `F-003` montre que les familles visuelles transverses restent nommees par domaine (`astrologer`, `consultation`, `dashboard`, `settings`, `wizard`).

## 3. Domain Boundary

- Domain: frontend-app-css-standardization
- In scope:
  - `frontend/src/App.css`
  - TSX consumers des familles visuelles App
  - tests cibles Astrologers, Consultations, Dashboard, Settings selon fichiers touches
- Out of scope:
  - CSS page-scoped hors App
  - refonte UX ou changement de copy
  - garde finale stricte reservee a CS-124
- Explicit non-goals:
  - pas d'alias de classes anciennes
  - pas de coexistence ancien/nouveau nom pour compatibilite
  - pas de nouvelle dependance UI

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: dead-code-removal
- Archetype reason: les anciens selecteurs specifiques deviennent des surfaces mortes apres migration des consumers vers les primitives.
- Behavior change allowed: constrained
- Behavior change constraints:
  - arrondis visuels standardises autorises si documentes
  - aucun changement de donnees, routes ou interactions
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une classe visuelle specifique est un contrat externe documente.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les pages/components touches doivent rendre les memes etats. |
| Baseline Snapshot | yes | Inventaire anciens prefixes et consumers. |
| Ownership Routing | yes | Chaque famille visuelle route vers une primitive ou variante. |
| Allowlist Exception | yes | Exceptions exactes seulement. |
| Contract Shape | no | Aucun contrat API. |
| Batch Migration | yes | Lots cartes/listes/badges/avatars/modales. |
| Reintroduction Guard | yes | Les anciens prefixes migres doivent etre bloques. |
| Persistent Evidence | yes | Mapping et validations persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth: AST guard `frontend/src/tests/design-system-guards.test.ts`, Vitest cibles des pages/composants touches et `visual-smoke`.
- Secondary evidence: scans zero-hit des anciens prefixes.
- Static scans alone are not sufficient because les familles visuelles couvrent hover, focus, empty states et responsive.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/app-visual-families-before.md`
- Comparison after implementation: `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/app-visual-families-after.md`
- Expected invariant: chaque ancien prefixe migre est absent ou classe comme blocked user decision.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Cards/panels | `.app-card`, `.app-card--featured`, `.app-panel` | `*-card-*` par domaine dans App.css |
| Lists/items | `.app-list`, `.app-list-item` | liste nommee par page |
| Badges/pills/tags | `.app-badge`, `.app-pill` variants | `astrologer-card-tag`, `precision-badge` duplicatifs |
| Avatars/media | `.app-avatar`, `.app-media` variants | avatar nomme par feature |
| Modal/overlay | `.app-modal`, `.app-overlay` | modal locale dupliquee |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | exact entries only if unavoidable | blocker temporaire de migration | exit condition: expires by CS-124 |

Rules: no wildcard, no folder-wide exception, no compatibility alias.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Cards | domain card selectors | `.app-card` variants | exact TSX consumers | page/component tests | zero-hit old prefixes | external contract |
| Lists/items | `chat-list`, history lists, compact lists | `.app-list` variants | exact TSX consumers | tests touched | old selectors absent | semantic mismatch |
| Badges/pills | `precision-badge`, tags, pills | `.app-badge`, `.app-pill` | exact TSX consumers | visual-smoke | no alias | variant ambiguity |
| Avatar/media | avatar classes in App.css | `.app-avatar`, `.app-media` | exact TSX consumers | page tests | no old wrapper | image regression |
| Modal/overlay | modal classes in App.css | `.app-modal`, `.app-overlay` | exact TSX consumers | settings/modal tests | old selectors deleted | a11y regression |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before | `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/app-visual-families-before.md` | inventory |
| after | `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/app-visual-families-after.md` | final mapping |
| final evidence | `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/generated/10-final-evidence.md` | validations |

## 4i. Reintroduction Guard

- Guard source: `frontend/src/tests/design-system-guards.test.ts`
- Architecture guard against reintroduction: the test must fail when migrated forbidden symbols are reintroduced.
- Forbidden examples: prefixes migres `astrologer-card`, `consultation-card`, `dashboard-summary`, `settings-tab`, `precision-badge`, `modal-*` si remplaces par primitives.
- Guard evidence: `npm run test -- design-system visual-smoke`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-003`
- Closure proof required: artifact after plus scans zero-hit.
- Known residual in-domain work: CS-124 final guard.
- Deferred non-domain concerns: none.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/01-evidence-log.md#E-007` - prefixes visuels page-specific dominants.
- Evidence 2: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-003` - familles visuelles non reutilisables.
- Evidence 3: `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md` - primitives a reutiliser.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes.

## 6. Target State

- Les familles cartes/listes/badges/avatars/modales utilisent des primitives generiques.
- Les anciens prefixes migres sont absents de `App.css` et des consumers TSX.
- Les variantes restantes sont nommees par effet ou role, pas par page/service.
- Les tests cibles et visual-smoke passent.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - namespaces classifies.
  - `RG-045` - pas de retour des literals migres.
  - `RG-046` - roles typographiques.
  - `RG-047` - pas de style inline statique.
  - `RG-049` - aucune surface legacy CSS.
  - `RG-059`, `RG-061` - App.css garde.
- Non-applicable invariants:
  - `RG-054` - aucune route admin legacy.
- Required regression evidence:
  - `npm run test -- design-system visual-smoke AstrologersPage ConsultationsPage SettingsPage DashboardPage`
  - `npm run lint`
- Allowed differences:
  - arrondis documentes dans l'artefact after.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Inventaire before des familles visuelles. | Evidence profile: `baseline_before_after_diff`; `rg -n "(astrologer-card|consultation-card|modal-)" frontend/src`. |
| AC2 | Chaque famille migree utilise une primitive. | Evidence profile: `ownership_routing`; AST guard plus `rg -n "\\.app-(card|list|badge|modal)" frontend/src/App.css`. |
| AC3 | Les anciens prefixes migres sont supprimes. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "alias|compat|shim|migration-only" frontend/src/App.css`. |
| AC4 | Pages/composants touches passent leurs tests. | Evidence profile: `runtime_source_of_truth`; `npm run test -- AstrologersPage ConsultationsPage SettingsPage`. |
| AC5 | Visual-smoke passe. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system visual-smoke`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier prefixes et consumers. (AC: AC1)
- [ ] Task 2 - Migrer cards/panels. (AC: AC2, AC3)
- [ ] Task 3 - Migrer lists/items. (AC: AC2, AC3)
- [ ] Task 4 - Migrer badges/pills/avatars/media. (AC: AC2, AC4)
- [ ] Task 5 - Migrer modal/overlay et mettre a jour guards. (AC: AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse primitives CS-121 and migrations CS-122.
- Reuse global tokens and typography classes.
- A variant is allowed only when its visual difference is reusable by at least two consumers or documented as a durable semantic role.

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

- old class kept only to avoid TSX migration
- `.old-*`, `OLD`, `legacy`, `compatibility`, `alias`
- page-specific `--app-*` variables for migrated families

## 11. Removal Classification Rules

Classification must be deterministic:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Primitive/variant generique active. |
| `external-active` | `keep`, `needs-user-decision` | Contrat externe documente ou consumer hors repo prouve. |
| `historical-facade` | `delete`, `needs-user-decision` | Ancien selecteur conserve uniquement comme facade CSS. |
| `dead` | `delete` | Ancien selecteur sans consumer apres migration. |
| `needs-user-decision` | `needs-user-decision` | Externalite ambigue ou exception permanente demandee. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| Visual selector | CSS/className | required during implementation | TSX inventory | CS-121 primitive | replace-consumer, delete, keep, needs-user-decision | after scans | drift |

Audit output path when applicable:

- `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/app-visual-families-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Cards/panels | App primitives | domain card prefixes in App.css |
| Badges/pills | App primitives | domain badge/tag prefixes |
| Modals/overlays | App primitives | duplicate modal local selectors |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md`
- `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/00-story.md`
- `frontend/src/App.css`
- `frontend/src/features/astrologers/**/*.tsx`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/pages/ConsultationsPage.tsx`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/tests/design-system-guards.test.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - remplacer familles visuelles.
- TSX consumers exacts - remplacer className.
- `frontend/src/tests/design-system-guards.test.ts` - anti-retour.

Likely tests:

- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/ConsultationsPage.test.tsx`
- `frontend/src/tests/SettingsPage.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`

Files not expected to change:

- `frontend/package.json`
- `backend/**`

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system visual-smoke AstrologersPage ConsultationsPage SettingsPage DashboardPage
npm run lint
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/00-story.md
```

## 22. Regression Risks

- Risk: perte de style distinctif utile.
  - Guardrail: variants semantiques documentees, pas par page.
- Risk: migration TSX incomplete.
  - Guardrail: scans zero-hit et tests cibles.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback, compatibility, legacy, migration-only, shim or alias.
- Do not leave hidden residual in-domain work when this story is marked `full-closure`.

## 24. References

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-003` - source.
- `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md` - primitive dependency.
