# Story CS-122 migrer-layouts-etats-actions-vers-primitives-css: Migrer layouts, etats et actions vers les primitives App

Status: done

## 1. Objective

Migrer les surfaces structurelles de `frontend/src/App.css` vers les primitives CS-121.
Le scope couvre containers, stacks, grilles, headers, states, action rows, boutons et liens d'action.
Les anciens noms ne doivent pas rester comme wrappers ou alias.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-002`
- Reason for change: `F-002` montre des repetitions massives de layout et etats malgre la centralisation.

## 3. Domain Boundary

- Domain: frontend-app-css-standardization
- In scope:
  - `frontend/src/App.css`
  - TSX consumers de classes structurelles definies dans App.css
  - tests de pages/composants touches
- Out of scope:
  - migration des cartes visuelles complexes reservee a CS-123
  - CSS hors `App.css` sauf si un TSX consumer change de classe
  - changement fonctionnel ou API
- Explicit non-goals:
  - ne pas creer d'ancien nom en alias
  - ne pas modifier les routes
  - ne pas reduire la couverture des guards CS-087/CS-121

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: dead-code-removal
- Archetype reason: les anciens selecteurs structurels deviennent morts apres migration des consumers vers les primitives CS-121.
- Behavior change allowed: constrained
- Behavior change constraints:
  - equivalence visuelle ou arrondi standardise documente
  - aucun changement de contenu, ordre, navigation ou etat
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un ancien nom de classe est identifie comme contrat externe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les pages rendues doivent rester valides apres migration className. |
| Baseline Snapshot | yes | Capturer les classes structurelles avant/apres. |
| Ownership Routing | yes | Chaque ancien selecteur doit router vers primitive ou suppression. |
| Allowlist Exception | yes | Les exceptions temporaires doivent etre exactes. |
| Contract Shape | no | Aucun contrat API. |
| Batch Migration | yes | Lots layout, etats, actions. |
| Reintroduction Guard | yes | Les anciens prefixes migres ne doivent pas revenir. |
| Persistent Evidence | yes | Inventaires before/after requis. |

## 4b. Runtime Source of Truth

- Primary source of truth: AST guard `frontend/src/tests/design-system-guards.test.ts`, tests Vitest des pages/composants touches et `visual-smoke`.
- Secondary evidence: scans zero-hit des anciens selecteurs migres.
- Static scans alone are not sufficient because les `className` React doivent continuer a rendre les etats attendus.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/app-structure-before.md`
- Comparison after implementation: `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/app-structure-after.md`
- Expected invariant: chaque ancien selecteur structurel migre est absent ou justifie par une exception exacte avec exit condition.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Page/container/header | primitives `.app-page`, `.app-section`, `.app-header` | `.astrologers-page-header`, `.consultations-page-header` equivalents conserves |
| Stack/grid/action row | primitives `.app-stack`, `.app-grid`, `.app-actions` | duplications locales flex/grid dans App.css |
| Loading/empty/error/success | primitive `.app-state` + variants | etats nommes par page |
| Buttons/actions | primitive `.app-action` + variants | bouton page-specific ou shadow divergent |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | none expected | aucune exception large | exit condition: aucune exception CS-122 ne peut rester apres implementation |

Rules: no wildcard, no folder-wide exception, no alias class.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Layout | page shells and headers | `.app-page`, `.app-section`, `.app-header` | exact TSX consumers | page tests | zero-hit old selectors | external class contract |
| Structure | repeated grids/stacks/lists | `.app-grid`, `.app-stack`, `.app-list` | exact TSX consumers | visual-smoke | no duplicate selector bodies | CSS dependency unknown |
| States | loading/empty/error/success classes | `.app-state` variants | exact TSX consumers | page tests | old state selectors removed | semantic mismatch |
| Actions | action rows, buttons, back links | `.app-actions`, `.app-action` variants | exact TSX consumers | accessibility smoke/tests | no old alias | focus regression |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before | `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/app-structure-before.md` | inventaire selectors/consumers |
| after | `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/app-structure-after.md` | mapping final |
| final evidence | `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/generated/10-final-evidence.md` | validations |

## 4i. Reintroduction Guard

- Guard source: `frontend/src/tests/design-system-guards.test.ts`
- Architecture guard against reintroduction: the test must fail when migrated forbidden symbols are reintroduced.
- Forbidden examples: anciens selecteurs structurels migres, nouveaux `--app-page-name-header-*`, duplications de boutons hors `.app-action`.
- Guard evidence: `npm run test -- design-system visual-smoke`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-002`
- Closure proof required: before/after structure plus tests runtime cibles.
- Known residual in-domain work: CS-123, CS-124.
- Deferred non-domain concerns: none.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/01-evidence-log.md#E-008` - declarations structurelles repetees.
- Evidence 2: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-002` - DRY violation.
- Evidence 3: `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md` - primitives a reutiliser.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes.

## 6. Target State

- Les surfaces structurelles App utilisent les primitives CS-121.
- Les vieux noms structurels supprimes ne restent ni en CSS ni en TSX.
- Les etats loading/empty/error/success ont un rendu commun.
- Les boutons/actions partagent shadow, focus, radius et typographie.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-045` - ne pas recreer les valeurs visuelles migrees.
  - `RG-046` - typographie standardisee.
  - `RG-047` - pas de style inline statique.
  - `RG-048` - pas de fallback CSS non classe.
  - `RG-059` et `RG-061` - App.css reste garde.
- Non-applicable invariants:
  - `RG-054` - routes admin legacy hors scope.
- Required regression evidence:
  - `npm run test -- design-system visual-smoke App router`
  - tests cibles des pages touchees
  - `npm run lint`
- Allowed differences:
  - arrondis documentes de spacing/radius/typographie.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Inventaire before structurel. | Evidence profile: `baseline_before_after_diff`; `rg -n "className=.*(page|header|loading)" frontend/src -g "*.tsx"`. |
| AC2 | Layouts migrent vers CS-121. | Evidence profile: `batch_migration_mapping`; `rg -n "\\.app-(page|section|header|state)" frontend/src/App.css`. |
| AC3 | Aucun ancien nom migre ne reste comme alias. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "OLD|legacy|alias|compat|shim" frontend/src/App.css`. |
| AC4 | Les tests runtime cibles passent. | Evidence profile: `runtime_source_of_truth`; `npm run test -- visual-smoke App router` runs `visual-smoke.test.tsx`. |
| AC5 | Les guards design-system restent verts. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier les classes structurelles et consumers. (AC: AC1)
- [ ] Task 2 - Migrer le lot layout/page/header. (AC: AC2, AC3)
- [ ] Task 3 - Migrer le lot grids/stacks/lists. (AC: AC2, AC3)
- [ ] Task 4 - Migrer le lot states et actions. (AC: AC2, AC4)
- [ ] Task 5 - Mettre a jour la garde anti-retour et preuves. (AC: AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse primitives creees par CS-121.
- Reuse classes `.type-*` pour la typographie.
- Do not recreate page-specific classes for near-identical spacing/radius/shadow.

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

- ancien selecteur migre conserve avec le meme body
- className compose avec ancien nom + nouveau nom pour compatibilite
- commentaire `OLD`

## 11. Removal Classification Rules

Classification must be deterministic:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Primitive structurelle CS-121 active. |
| `external-active` | `keep`, `needs-user-decision` | Contrat externe documente ou consumer hors repo prouve. |
| `historical-facade` | `delete`, `needs-user-decision` | Ancien selecteur conserve uniquement comme facade CSS. |
| `dead` | `delete` | Ancien selecteur sans consumer apres migration. |
| `needs-user-decision` | `needs-user-decision` | Externalite ambigue ou exception permanente demandee. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| Structure selector | CSS/className | required during implementation | TSX inventory | CS-121 primitive | replace-consumer, delete, keep, needs-user-decision | scans | drift |

Audit output path when applicable:

- `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/app-structure-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Structure App | primitives CS-121 in `App.css` | page-specific structure selectors |
| State UI | `.app-state` variants | page-specific loading/error/empty selectors |
| Actions | `.app-action` variants | bespoke button shadows/radius |

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
- `frontend/src/App.css`
- `frontend/src/App.tsx`
- `frontend/src/layouts/**/*.tsx`
- `frontend/src/pages/**/*.tsx`
- `frontend/src/features/**/*.tsx`
- `frontend/src/components/**/*.tsx`
- `frontend/src/tests/design-system-guards.test.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - remplacer blocs structurels.
- TSX consumers exacts - remplacer className.
- `frontend/src/tests/design-system-guards.test.ts` - anti-retour.

Likely tests:

- tests des pages/composants dont className change.
- `frontend/src/tests/visual-smoke.test.tsx`.

Files not expected to change:

- `frontend/package.json` - aucune dependance.
- `backend/**` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system visual-smoke App router
npm run lint
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/00-story.md
```

## 22. Regression Risks

- Risk: className migration casse un test de page.
  - Guardrail: tests cibles et visual-smoke.
- Risk: ancien selecteur conserve comme compatibilite.
  - Guardrail: scans zero-hit et delete-only rule.

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

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-002` - source.
- `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md` - primitive dependency.
