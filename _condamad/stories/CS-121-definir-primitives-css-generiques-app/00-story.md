# Story CS-121 definir-primitives-css-generiques-app: Definir les primitives CSS generiques App

Status: done

## 1. Objective

Definir dans `frontend/src/App.css` une taxonomie finie de classes generiques reutilisables.
Elle couvre pages, sections, stacks, grilles, cartes, panneaux, actions, etats, badges, avatars et modales.
Cette story etablit le contrat de migration; elle ne migre pas tous les consommateurs specifiques.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-001`
- Reason for change: `F-001` montre 442 variables `--app-*`, 439 single-use et 482 classes uniques au lieu de primitives reutilisables.

## 3. Domain Boundary

- Domain: frontend-app-css-standardization
- In scope:
  - `frontend/src/App.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - artefacts before/after sous ce dossier de story
- Out of scope:
  - migration exhaustive des consommateurs TSX
  - refactor des CSS page-scoped hors `App.css`
  - changement de routes, API, stores ou comportement utilisateur
- Explicit non-goals:
  - ne pas affaiblir `RG-044` a `RG-063`
  - ne pas creer d'alias de classe pour conserver les anciens noms
  - ne pas introduire de nouvelle dependance

## 4. Operation Contract

- Operation type: converge
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story cree le catalogue canonique de primitives CSS App et documente leur ownership.
- Behavior change allowed: constrained
- Behavior change constraints:
  - seules des equivalences visuelles arrondies et documentees sont autorisees
  - aucun comportement React ou routage ne change
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une primitive ne peut pas remplacer des styles proches sans difference visuelle majeure.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | La story cree le contrat CSS; les stories suivantes prouvent les migrations runtime. |
| Baseline Snapshot | yes | Capturer le nombre initial de classes/variables specifiques. |
| Ownership Routing | yes | Chaque primitive et namespace doit avoir un owner canonique. |
| Allowlist Exception | yes | Aucune exception large n'est autorisee; toute exception doit etre exacte. |
| Contract Shape | no | Aucun contrat API ou DTO. |
| Batch Migration | yes | Les primitives couvrent plusieurs familles de styles. |
| Reintroduction Guard | yes | Le contrat doit commencer a bloquer les nouveaux noms page-specific. |
| Persistent Evidence | yes | Les decisions de primitives doivent rester consultables. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: cette story etablit les primitives et les guards statiques; les validations runtime visuelles seront obligatoires dans CS-122 et CS-123.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-121-definir-primitives-css-generiques-app/app-css-standardization-before.md`
- Comparison after implementation: `_condamad/stories/CS-121-definir-primitives-css-generiques-app/app-css-primitives-after.md`
- Expected invariant: l'after liste les primitives creees, les anciens groupes couverts, et les exceptions restantes avec owner et condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Primitives de page/section/layout | `frontend/src/App.css` classes `.app-*` generiques | classes nommees par page ou feature |
| Typographie generique | `frontend/src/styles/typography-roles.md` et classes `.type-*` | variables `--app-page-name-*-font-size` single-use |
| Couleur/radius/shadow | tokens globaux ou primitives App documentees | variables `--app-*` mecaniques ou page-specific |
| Exceptions temporaires | `design-system-allowlist.ts` avec expiry | wildcard, dossier entier ou commentaire differe |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | exact entries only | aucune exception large | exit condition: aucune entree CS-121 apres CS-124 sans decision utilisateur |

Rules: no wildcard, no folder-wide exception, no hidden compatibility alias.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Layout primitives | repeated flex/grid/page classes | `.app-page`, `.app-section`, `.app-stack`, `.app-grid` | minimal examples | design-system | no alias | visual mismatch |
| Content primitives | panel/card/header/text states | `.app-panel`, `.app-card`, `.app-header`, `.app-state` | minimal examples | design-system | no wrapper | missing token |
| Action primitives | buttons/links/actions | `.app-action`, `.app-action--danger`, `.app-action-row` | minimal examples | design-system | no duplicate | a11y risk |
| Object primitives | badge/avatar/modal | `.app-badge`, `.app-avatar`, `.app-modal` | none or minimal examples | design-system | no domain prefix | semantic ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before | `_condamad/stories/CS-121-definir-primitives-css-generiques-app/app-css-standardization-before.md` | mesure initiale classes/variables |
| after | `_condamad/stories/CS-121-definir-primitives-css-generiques-app/app-css-primitives-after.md` | catalogue final primitives et decisions |
| final evidence | `_condamad/stories/CS-121-definir-primitives-css-generiques-app/generated/10-final-evidence.md` | validations executees |

## 4i. Reintroduction Guard

- Guard source: `frontend/src/tests/design-system-guards.test.ts`
- Forbidden examples:
  - nouvelle variable `--app-astrologer-*`, `--app-consultation-*`, `--app-dashboard-*`, `--app-settings-*`, `--app-wizard-*`
  - nouvelle classe App page-specific sans allowlist exacte
  - commentaire `OLD`, `legacy`, `compatibility`, `migration-only`
- Guard evidence: `npm run test -- design-system theme-tokens legacy-style`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-001`
- Closure proof required: before/after artifact plus guard update.
- Known residual in-domain work: CS-122, CS-123, CS-124.
- Deferred non-domain concerns: Vite chunk-size warning.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/01-evidence-log.md#E-006` - `App.css` contient 442 variables `--app-*` et 482 classes uniques.
- Evidence 2: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-001` - centralisation sans primitives.
- Evidence 3: `frontend/src/tests/design-system-guards.test.ts` - la garde existante bloque les literals, pas les noms page-specific.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `App.css` expose une base de primitives generiques documentees.
- Les noms de primitives ne contiennent pas de domaine produit ou page.
- Les arrondis acceptes de spacing, radius, elevation et typographie sont documentes.
- Les stories suivantes peuvent migrer les consommateurs sans rediscuter le vocabulaire CSS.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - namespaces CSS classes et variables doivent rester classifies.
  - `RG-045` - valeurs visuelles migrees ne doivent pas revenir hors owner.
  - `RG-046` - typographie via roles semantiques.
  - `RG-048` - aucun fallback CSS non classe.
  - `RG-059` - App.css reste protege par garde anti-retour.
  - `RG-061` - declarations App restent routees et sans noms mecaniques.
- Non-applicable invariants:
  - `RG-054` - aucune route admin legacy.
  - `RG-073` - aucun composant natal.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens legacy-style`
  - `npm run lint`
- Allowed differences:
  - nouvelles classes generiques et documentation de primitives.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline des variables App specifiques. | Evidence profile: `baseline_before_after_diff`; `rg -n -- "--app-[a-z0-9-]+" frontend/src/App.css`. |
| AC2 | `App.css` contient les primitives generiques. | Evidence profile: `ownership_routing`; `rg -n "\\.app-(page|section|stack|grid|card|panel)" frontend/src/App.css`. |
| AC3 | Les primitives evitent les noms de domaine interdits. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- design-system`. |
| AC4 | Les registres tokens/typographie documentent les owners modifies. | Evidence profile: `registry_catalog`; `npm run test -- theme-tokens design-system`. |
| AC5 | Aucune exception large ou alias n'est cree. | Evidence profile: `allowlist_register_validated`; `rg -n "OLD|legacy|alias|compat|shim" frontend/src/App.css`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline App.css. (AC: AC1)
- [ ] Task 2 - Definir les primitives generiques minimales dans `App.css`. (AC: AC2, AC3)
- [ ] Task 3 - Documenter les owners dans les registres applicables. (AC: AC4)
- [ ] Task 4 - Ajouter une premiere garde de nomenclature sans bloquer les migrations suivantes. (AC: AC3, AC5)
- [ ] Task 5 - Persister l'after et les validations. (AC: AC1, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `design-tokens.css`, `utilities.css`, `typography-roles.md`, `token-namespace-registry.md`.
- Do not recreate a primitive already covered by `.panel`, `.grid`, `.card`, `.state-line`, `.action-row` unless it is normalized into the new App taxonomy.
- Shared abstraction allowed only when at least two existing App selectors can consume it.

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

- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only`
- new page-specific `--app-*` variable names
- `.app-astrologer-*`, `.app-consultation-*`, `.app-dashboard-*`, `.app-settings-*`, `.app-wizard-*`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| App primitives | `frontend/src/App.css` | page-specific class names in App.css |
| App typography roles | `frontend/src/styles/typography-roles.md` | single-use App font variables |
| CSS namespace registry | `frontend/src/styles/token-namespace-registry.md` | undocumented `--app-*` namespaces |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/00-audit-report.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md`
- `frontend/src/App.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - ajouter primitives generiques.
- `frontend/src/tests/design-system-guards.test.ts` - ajouter garde de nomenclature.
- `frontend/src/styles/token-namespace-registry.md` - clarifier owner `--app-*`.
- `frontend/src/styles/typography-roles.md` - clarifier les roles App generiques manquants.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

Files not expected to change:

- `frontend/package.json` - aucune dependance.
- `backend/**` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only when explicitly listed here with justification.

## 21. Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens legacy-style
npm run lint
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md
```

## 22. Regression Risks

- Risk: primitives trop nombreuses et non reutilisables.
  - Guardrail: chaque primitive doit mapper au moins deux surfaces ou etre justifiee comme base.
- Risk: ancien nom conserve comme alias.
  - Guardrail: scan No Legacy et interdiction d'alias.

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

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-001` - source.
- `_condamad/stories/regression-guardrails.md` - invariants.
