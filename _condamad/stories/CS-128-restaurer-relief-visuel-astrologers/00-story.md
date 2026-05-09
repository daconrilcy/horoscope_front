# Story CS-128 restaurer-relief-visuel-astrologers: Restaurer le relief visuel de la page /Astrologers

Status: done

## 1. Objective

Retablir les details stylistiques perdus sur la page `/astrologers` apres la refacto de `App.css`.
La mise en page globale est deja revenue; cette story cible uniquement la matiere visuelle de la liste:
ombres, halos, transparences, petite pastille logo, teintes par persona, bordures et chips.
Le changement ne doit pas faire regrossir `App.css` ni ajouter de styles inline.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-09 avec capture avant refacto.
- Analysis reference: `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/reference-visual-analysis.md`
- Reason for change: la refacto de `App.css` a preserve la structure globale de `/Astrologers`.
- Visual gap: les overrides compacts `.people-page .person-card*` ont aplati des details de relief et de matiere.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/features/astrologers` visual surface for route `/astrologers`
- In scope:
  - rendu compact de `frontend/src/pages/AstrologersPage.tsx`
  - `AstrologerGrid.tsx` et `AstrologerCard.tsx` uniquement si une classe ou un attribut manque
  - styles App modules existants qui possedent deja cette surface: `frontend/src/styles/app/tokens.css`, `frontend/src/styles/app/cards.css`, `frontend/src/styles/app/media.css`
  - tests `frontend/src/tests/AstrologersPage.test.tsx`, `frontend/src/tests/design-system-guards.test.ts`, `frontend/src/tests/visual-smoke.test.tsx`
  - artefacts before/after dans ce dossier de story
- Out of scope:
  - backend, API `/v1/astrologers`, cache local et contrats `Astrologer`
  - page profil `/astrologers/:id`
  - picker chat, step consultations, settings default astrologer et modal natal
  - nouvelle navigation, nouveau contenu, nouvelle dependance ou refonte produit
  - extraction large de `App.css` ou creation d'un nouveau module CSS
- Explicit non-goals:
  - ne pas modifier `frontend/src/App.css` hors verification qu'il reste limite aux imports
  - ne pas ajouter de dossier sous `frontend/src/styles/app/`
  - ne pas affaiblir `RG-044` a `RG-050`, `RG-059`, `RG-061`, `RG-075`, `RG-076`, `RG-077`, `RG-078`
  - ne pas recreer d'alias `.astrologer-card`, `.astrologer-grid` ou autre surface legacy retiree par `CS-071`
  - ne pas rendre visibles les badges provider/default sur la liste compacte si cela contredit la capture

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: supported archetypes cover removals, route/API changes, namespace moves, guards and large splits.
- Custom reason: this is a bounded visual restoration on an existing frontend route.
- Excluded operations: no route, API, namespace or removal operation.
- Additional validation rules:
  - ACs must include DOM evidence, CSS guard evidence and before/after visual evidence.
  - The story must prohibit `App.css` growth and new `styles/app` modules.
  - The implementation must prove the route still renders loading, error, empty and populated states.
- Behavior change allowed: constrained
- Behavior change constraints:
  - allowed: visual-only changes on `/astrologers` cards and page shell to restore shadows, transparent material, themed accents, chips, small icon and avatar relief
  - forbidden: route path, API calls, data mapping, card click, rotation, profile navigation, copy and badge visibility changes
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: restoring the reference requires a new CSS module, dependency, behavior change or visible provider/default badges.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The runtime DOM for `/astrologers` is the source for the visible route and card states. |
| Baseline Snapshot | yes | The visual regression is a before/after issue and must be evidenced with screenshots or DOM/CSS snapshots. |
| Ownership Routing | yes | Styles must stay in existing typed App CSS modules and not pollute `App.css`. |
| Allowlist Exception | no | No new exception, wildcard, fallback or allowlist entry is expected. |
| Contract Shape | no | No API, DTO, OpenAPI, generated client or payload shape is affected. |
| Batch Migration | no | This is one bounded visual restoration, not a multi-batch migration. |
| Reintroduction Guard | yes | Guards must prevent `App.css` pollution, legacy selector return and loss of required card material tokens. |
| Persistent Evidence | yes | The story needs persisted visual notes, before/after artifacts and validation evidence. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/design-system-guards.test.ts`, loaded CSS manifest `APP_CSS_MODULE_FILES`, and rendered `/astrologers` DOM from `AstrologersPage`
- Secondary evidence:
  - `frontend/src/tests/AstrologersPage.test.tsx`, `frontend/src/tests/design-system-guards.test.ts`, `frontend/src/tests/visual-smoke.test.tsx`, targeted `rg` scans
- Static scans alone are not sufficient for this story because:
  - a selector can exist while cascade order, scoped overrides or hidden badges still flatten the visible page.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-before.md`
  - before screenshot artifact in the same folder, or a blocker note explaining why the screenshot could not be captured
- Comparison after implementation:
  - `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-after.md`
  - after screenshot artifact in the same folder, or a blocker note explaining why the screenshot could not be captured
- Expected invariant:
  - same route, copy, data-driven cards, navigation and compact grid; only visual details listed in `reference-visual-analysis.md` may change.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| App CSS import entrypoint | `frontend/src/App.css` imports only | active `.people-page`, `.person-card` or token declarations |
| Person/people visual tokens | `frontend/src/styles/app/tokens.css` prefixes `--app-person-*`, `--app-people-*` | new prefix or page token in `App.css` |
| Card layout/material declarations | `frontend/src/styles/app/cards.css` | duplicate page CSS file, inline style, legacy selector alias |
| Avatar/icon/media relief | `frontend/src/styles/app/media.css` | component inline style or unrelated feature CSS |
| Route composition | `frontend/src/pages/AstrologersPage.tsx` | API/data logic change |
| Astrologer card markup | `frontend/src/features/astrologers/components/AstrologerCard.tsx` | duplicated card implementation |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable.
- Reason: no new fallback, inline-style exception, legacy-style exception, page-size exception or wildcard allowlist is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable.
- Reason: no API, route manifest, DTO, OpenAPI schema, generated client, persisted payload or serialization contract is modified.

## 4g. Batch Migration Plan

- Batch migration: not applicable.
- Reason: the story is a single visual restoration on one route surface; there is no old-to-new multi-surface migration.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| reference analysis | `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/reference-visual-analysis.md` | captures the stylistic target from the user image |
| before snapshot | `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-before.md` | records current flattened state before code changes |
| after snapshot | `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-after.md` | records restored details and allowed differences |
| validation log | `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/validation-evidence.md` | records exact commands, results and skipped checks if any |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if these forbidden or required surfaces drift:

- forbidden examples:
  - active selectors or token declarations added to `frontend/src/App.css`
  - `.astrologer-card`, `.astrologer-grid`, `.astrologer-card-avatar` aliases in active CSS
  - new file under `frontend/src/styles/app/`
  - `style=` in `AstrologersPage.tsx`, `AstrologerCard.tsx` or `AstrologerGrid.tsx`
- required examples:
  - `.people-page .person-card` keeps a token-backed shadow and translucent background
  - `.people-page .person-card--featured` keeps a distinct token-backed border/shadow/background
  - `.people-page .person-card-icon` remains displayed as the small themed logo
  - `.people-page .person-card-tag` keeps token-backed themed chip material

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- design-system visual-smoke AstrologersPage` checks the required and forbidden symbols.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase and user source indicate:

- Evidence 1: `frontend/src/pages/AstrologersPage.tsx` - `/astrologers` renders `PageLayout`,
  `app-panel people-page`, a compact header and `AstrologerGrid`.
- Evidence 2: `frontend/src/features/astrologers/components/AstrologerCard.tsx` - each card exposes
  `data-theme`, `person-card-icon`, orbit layers, avatar, display name, style, divider, specialties and bio.
- Evidence 3: `frontend/src/styles/app/tokens.css` - existing `--app-person-card-*` tokens contain
  gradients, shadows, avatar glow, icon colors and themed chip values.
- Evidence 4: `frontend/src/styles/app/cards.css` - `.people-page .person-card*` compact overrides
  currently replace richer card material with generic glass/card tokens.
- Evidence 5: `frontend/src/styles/app/media.css` - avatar glow and orbit pseudo-elements already exist; compact overrides must not neutralize them.
- Evidence 6: `frontend/src/tests/design-system-guards.test.ts` - App CSS surface is guarded for module filenames, duplicate selectors, `App.css` size and App-specific prefixes.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consulted before scope was finalized, especially `RG-044` to `RG-050`, `RG-061`, `RG-075` to `RG-078`.
- Evidence 8: `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/reference-visual-analysis.md` - user image details converted into testable visual requirements.

## 6. Target State

After implementation:

- `/astrologers` keeps the current compact centered layout and first-card-full-width grid.
- The page shell and cards recover the previous material: translucent glass, soft shadows, subtle radial highlights, themed borders and visible depth.
- The small themed icon/pastille remains visible on every card and uses the persona theme.
- Avatar photos keep round crop, liseret, glow and depth without layout shift.
- Specialty chips are small, translucent, themed and token-backed.
- `frontend/src/App.css` remains import-only; any CSS edits stay in existing typed modules.
- Tests and evidence prove no route/data behavior changed.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespaces must remain classified; this story uses `--app-person-*`, `--app-people-*` and `--astro-*`.
  - `RG-045` - visual literals must not return outside token owners when values are migrated.
  - `RG-047` - no inline static styles may be added to the route or card components.
  - `RG-048` - no unclassified CSS fallback `var(--token, value)` may be introduced.
  - `RG-049` - legacy CSS aliases such as removed astrologer-card surfaces must not return.
  - `RG-050` - design-system static guards must stay executable.
  - `RG-061` - active App CSS declarations must stay token-backed and not reintroduce raw visual declarations in `App.css`.
  - `RG-075` - `App.css` must not reintroduce domain-specific `astrologer` selectors or variables.
  - `RG-076` - no new unclassified `--app-*` prefix is allowed.
  - `RG-078` - `App.css` must remain bounded, import-only, and routed through existing typed modules.
  - `RG-079` - `/astrologers` visual material must retain token-backed relief without polluting `App.css`.
- Non-applicable invariants:
  - backend API invariants `RG-001` to `RG-043` do not apply because no backend route, DB, prompt, billing or script surface is modified.
  - layout ownership `RG-068` applies only as a passive route hierarchy guard; this story does not change route ownership.
- Required regression evidence:
  - `npm run test -- AstrologersPage design-system visual-smoke`
  - `npm run lint`
  - targeted scans listed in the validation plan
  - before/after artifacts in this story folder
- Allowed differences:
  - visual-only differences limited to shadows, backgrounds, borders, radius, icon/chip/avatar material and themed accent intensity on `/astrologers`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before artifact has owner mapping. | Evidence profile: `baseline_before_after_diff`; `rg -n "Owner mapping" _condamad/stories/CS-128*/astrologers-visual-before.md`. |
| AC2 | Compact cards keep token-backed material. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system visual-smoke`. |
| AC3 | Featured card remains full-width. | Evidence profile: `baseline_before_after_diff`; `npm run test -- AstrologersPage design-system`. |
| AC4 | Small persona icon remains visible. | Evidence profile: `reintroduction_guard`; `npm run test -- AstrologersPage visual-smoke`. |
| AC5 | Avatars keep visual relief. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage visual-smoke`. |
| AC6 | Specialty chips keep themed material. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- design-system theme-tokens css-fallback`. |
| AC7 | Provider default featured badges stay hidden. | Evidence profile: `baseline_before_after_diff`; `npm run test -- AstrologersPage design-system`. |
| AC8 | `App.css` keeps zero active page style. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`; zero-hit `rg -n "people-page" src/App.css`. |
| AC9 | No legacy astrologer selector returns. | Evidence profile: `no_legacy_contract`; zero-hit `rg -n "astrologer-" src/styles/app src/features/astrologers`. |
| AC10 | Existing route states still pass. | Evidence profile: `frontend_typecheck_no_orphan`; `frontend/src/tests/AstrologersPage.test.tsx`; `npm run test -- AstrologersPage`. |
| AC11 | After evidence records commands. | Evidence profile: `baseline_before_after_diff`; `rg -n "Commands run" _condamad/stories/CS-128*/astrologers-visual-after.md`. |

## 7a. Acceptance Evidence Details

- AC1 before artifact must include a table with columns `Missing detail`, `Current selector/token`,
  `Target owner`, `Evidence` and `Decision`.
- AC2 CSS guard must assert `.people-page .person-card` uses token-backed background,
  border and shadow values rather than generic flat card tokens.
- AC3 CSS or DOM guard must assert `.people-page .person-card--featured` still spans two
  columns on desktop and uses a distinct token-backed material.
- AC4 DOM or CSS guard must assert `.people-page .person-card-icon` is not hidden and uses
  the existing `data-theme` variable path.
- AC5 evidence must preserve image source, alt text and click target while checking avatar
  border/glow selectors.
- AC6 evidence must show chips use existing `--app-person-card-tag-*` or `--astro-chip-*`
  ownership.
- AC7 evidence must keep provider/default/featured text badges hidden in compact list scope.
- AC8 zero-hit scan means no output is the expected result; any hit in `src/App.css` is a
  blocker unless it is the import-only file comment.
- AC9 zero-hit scan means no active `.astrologer-*` selector, alias or duplicate card surface.
- AC11 after artifact must include `Allowed differences`, `Commands run`, `Skipped checks`
  and `Screenshots` sections.

## 8. Implementation Tasks

- [x] Task 1 - Capture current visual baseline and ownership map. (AC: AC1, AC11)
  - [x] Create `astrologers-visual-before.md` with current selectors, token owners and visible gaps against `reference-visual-analysis.md`.
  - [x] Start the frontend and capture a before screenshot, or record the exact blocker in the artifact.

- [x] Task 2 - Restore card material through existing CSS owners. (AC: AC2, AC3, AC6, AC8)
  - [x] Adjust only `tokens.css`, `cards.css` and/or `media.css`.
  - [x] Reuse existing `--app-person-*`, `--app-people-*`, `--astro-*`, global color, radius, shadow and typography tokens before adding any token.
  - [x] If a new `--app-*` token is unavoidable, update `token-namespace-registry.md` or stop for user decision.
  - [x] Keep `.people-page` compact dimensions and two-column/full-width-featured grid.

- [x] Task 3 - Preserve and guard the small icon, avatar depth and chip treatment. (AC: AC4, AC5, AC6)
  - [x] Ensure `.people-page .person-card-icon` remains visible and themed.
  - [x] Ensure compact avatar overrides do not remove liseret/glow/pseudo-element depth.
  - [x] Ensure chips keep compact sizing with themed translucent border/background.

- [x] Task 4 - Keep compact-list badge and behavior decisions unchanged. (AC: AC7, AC10)
  - [x] Do not change provider/default/featured badge visibility without user decision.
  - [x] Do not change `AstrologersPage` data loading, rotation or navigation behavior.

- [x] Task 5 - Add or update deterministic guards. (AC: AC2, AC4, AC7, AC8, AC9)
  - [x] Extend `design-system-guards.test.ts` with static assertions for `/astrologers` compact material.
  - [x] Extend `visual-smoke.test.tsx` only when static CSS assertions cannot prove the rendered DOM state.
  - [x] Ensure guards fail if `App.css` receives active `/Astrologers` selectors or if a new `styles/app` module appears.

- [x] Task 6 - Validate and persist after evidence. (AC: AC8, AC9, AC10, AC11)
  - [x] Create `astrologers-visual-after.md` and `validation-evidence.md`.
  - [x] Run the validation plan and record command results.

### Review Findings

- [x] [Review][Patch] Synchroniser le statut source avec la cloture.
  `00-story.md` indiquait encore `ready-to-dev` alors que le registre et
  l'evidence finale etaient `done`; corrige le 2026-05-10.
- [x] [Review][Patch] Synchroniser les taches de la story avec les preuves.
  Les taches Task 1 a Task 6 restaient decochees malgre les artefacts et
  validations; corrige le 2026-05-10.
- [x] [Review][Patch] Nettoyer l'evidence finale obsolete.
  `generated/10-final-evidence.md` gardait une note capsule `In progress`;
  corrige le 2026-05-10.
- [x] [Review][Patch] Renforcer le relief visuel apres capture utilisateur.
  La premiere passe restait trop plate sur la capture fournie: couleurs,
  ombrages, pastilles et chips etaient trop faibles. Correction appliquee le
  2026-05-10 via tokens compacts dans `tokens.css`, usage strict dans
  `cards.css`, et garde-fous mis a jour.
- [x] [Review][Patch] Corriger la resolution runtime des tokens compacts.
  Les tokens compacts initialement portes par `#root` referenceaient
  `--astro-*`, uniquement defini sur `.person-card`; en navigateur les valeurs
  devenaient invalides et les cartes retombaient a `background/border/shadow`
  transparents. Correction appliquee le 2026-05-10 en resolvant ces tokens sur
  `.person-card` et en replaçant la pastille absolue par rapport a la carte.
- [x] [Review][Patch] Ajuster les derniers details de profondeur.
  La pastille `person-card-icon` passe devant l'avatar au hover, son anneau est
  degrade et adouci, l'espacement avec la photo est augmente, le divider
  d'Etienne redevient visible et `person-card-style` utilise un anthracite
  compact token-backed.
- [x] [Review][Patch] Restaurer l'effet glass du top menu au scroll.
  Le header sticky etait trop transparent pendant le defilement vertical; il
  donne maintenant l'impression que le contenu passe dessous grace a un fond
  translucent plus present, un blur sature et un voile `::before`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AstrologerCard` existing `data-theme`, `person-card-icon`, orbit layers, avatar and tag markup.
  - `frontend/src/styles/app/tokens.css` existing `--app-person-card-*`, `--app-person-card-avatar-*`, `--app-person-card-tag-*`, `--app-people-page-*`.
  - `frontend/src/styles/app/cards.css` existing `.people-page` scoped overrides and `data-theme` theme variables.
  - `frontend/src/styles/app/media.css` existing avatar glow/orbit pseudo-elements.
  - global tokens in `design-tokens.css`, `theme.css`, `premium-theme.css`, `glass.css` and `backgrounds.css` before creating new values.
- Do not recreate:
  - a second astrologer card component
  - a page-specific CSS module for this one restoration
  - legacy `.astrologer-*` selectors retired by earlier stories
  - raw hardcoded visual literals in active component CSS when an existing token covers the intent
- Shared abstraction allowed only if:
  - it is an existing typed App CSS owner and is needed by at least the current person/people surface without broadening the story.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- broad allowlists or wildcard exceptions
- new dependencies
- new file under `frontend/src/styles/app/`
- active CSS additions in `frontend/src/App.css`
- inline `style=` additions in route/card/grid components

Specific forbidden symbols / paths:

- `.astrologer-card`
- `.astrologer-grid`
- `.astrologer-card-avatar`
- `.astrologer-card-specialties`
- `frontend/src/App.css` active `/Astrologers` styles
- `frontend/src/styles/app/astrologers.css`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| `/astrologers` route composition | `frontend/src/pages/AstrologersPage.tsx` | data/API changes in this story |
| Astrologer list/card markup | `frontend/src/features/astrologers/components/*.tsx` | duplicate cards under `pages` or `components/ui` |
| Person card tokens | `frontend/src/styles/app/tokens.css` | unclassified `App.css` variables |
| Person card layout/material | `frontend/src/styles/app/cards.css` | new page CSS module or legacy `.astrologer-*` aliases |
| Person avatar/media effects | `frontend/src/styles/app/media.css` | inline styles |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_condamad/stories/CS-071-retirer-alias-css-astrologer-card/00-story.md`
- `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/app/tokens.css` - adjust values under existing `--app-person-*` or `--app-people-*` owners.
- `frontend/src/styles/app/cards.css` - restore compact `.people-page .person-card*` background, shadow, border, icon and chip treatment while preserving layout.
- `frontend/src/styles/app/media.css` - preserve avatar/orbit relief for compact cards if current overrides flatten the media effects.
- `frontend/src/tests/design-system-guards.test.ts` - add deterministic CSS ownership/material guards.
- `frontend/src/tests/visual-smoke.test.tsx` - add representative route/card visual smoke assertions only for rendered DOM proof.
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-before.md` - before evidence.
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-after.md` - after evidence.
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/validation-evidence.md` - command evidence.

Likely tests:

- `frontend/src/tests/AstrologersPage.test.tsx` - maintain route state coverage and add compact DOM assertions only when required.
- `frontend/src/tests/design-system-guards.test.ts` - guard CSS owner and forbidden regressions.
- `frontend/src/tests/visual-smoke.test.tsx` - smoke render for icon/avatar/chip material if static CSS assertions are insufficient.

Files not expected to change:

- `frontend/src/App.css` - must remain import-only.
- `frontend/src/api/astrologers.ts` - API/data contract is out of scope.
- `backend/**` - backend is out of scope.
- `frontend/src/app/routes.tsx` - route registration is out of scope.
- `frontend/src/pages/AstrologerProfilePage.tsx` and `frontend/src/pages/AstrologerProfilePage.css` - profile page is out of scope.
- `frontend/src/styles/app/*.css` other than `tokens.css`, `cards.css`, `media.css` - no broad CSS cleanup.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

No dependency change is allowed for this story.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- AstrologersPage design-system visual-smoke
npm run test -- theme-tokens css-fallback inline-style legacy-style
npm run lint
npm run build
rg -n "person-card|people-page|astrologer" src/App.css
rg -n "astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim" src/styles/app src/pages src/features/astrologers
rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers/components/AstrologerCard.tsx src/features/astrologers/components/AstrologerGrid.tsx
rg --files src/styles/app
Pop-Location
```

Expected scan results:

- `rg -n "person-card|people-page|astrologer" src/App.css` must return zero hit.
- The bounded `astrologer-card|astrologer-grid|compat|legacy|alias|shim` scan must return zero active hit.
- The bounded `style=` scan must return zero hit.
- `rg --files src/styles/app` must list only the approved type modules from `APP_CSS_MODULE_FILES`.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md
```

Manual visual check when the dev server can run:

- Open `/astrologers` on desktop and mobile.
- Verify the first card spans two columns on desktop.
- Verify the small themed icon is visible on every card.
- Verify cards show soft shadow, translucent surface, themed border/chips and avatar glow.
- Verify provider/default badges are not visible on the compact list.
- Verify no text overlaps at mobile width.

## 22. Regression Risks

- Risk: restoring visual richness by adding page-specific styles back into `App.css`.
  - Guardrail: `RG-078`, `RG-079`, `npm run test -- design-system`, scan `rg -n "person-card|people-page|astrologer" src/App.css`.
- Risk: reintroducing legacy `.astrologer-*` selectors after `CS-071`.
  - Guardrail: `RG-049`, scan for `.astrologer-card`, `.astrologer-grid`, `.astrologer-card-avatar`.
- Risk: hiding the small icon or flattening avatar pseudo-elements via compact overrides.
  - Guardrail: `visual-smoke`/design-system assertions for `.people-page .person-card-icon` and avatar selectors.
- Risk: raw hardcoded colors/shadows proliferate in CSS.
  - Guardrail: `RG-044`, `RG-045`, `RG-061`, `theme-tokens`, `css-fallback`, `design-system`.
- Risk: behavior changes are bundled into a visual story.
  - Guardrail: `AstrologersPage.test.tsx` loading/error/empty/populated/navigation coverage.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback,
  compatibility, legacy, migration-only, shim, alias, TODO, or hidden residual in-domain work.
- Start by reading `reference-visual-analysis.md` and the current CSS owner files.
- Keep `frontend/src/App.css` import-only.
- Prefer adjusting existing `.people-page` scoped overrides over changing shared person-card defaults used by chat, consultations, natal or profile surfaces.
- If a visual change would affect surfaces outside `/astrologers`, document the affected selector and either narrow the selector or stop for user decision.

## 24. References

- User-provided screenshot in conversation - visual target for relief, transparency, shadows, icon and persona colors.
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/reference-visual-analysis.md` - extracted visual details and non-goals.
- `frontend/src/pages/AstrologersPage.tsx` - route composition.
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - existing reusable card markup and persona theme hooks.
- `frontend/src/styles/app/tokens.css` - token owner for card material values.
- `frontend/src/styles/app/cards.css` - card and compact people-page CSS owner.
- `frontend/src/styles/app/media.css` - avatar/orbit visual owner.
- `frontend/src/tests/design-system-guards.test.ts` - static design-system guard owner.
- `_condamad/stories/regression-guardrails.md` - shared regression invariants.
