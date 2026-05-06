# Story CS-075 converger-namespaces-css-migration-only-restants: Converger les namespaces CSS migration-only restants

Status: ready-to-dev

## Objective

Retirer les statuts migration-only restants du registre de tokens frontend:
supprimer la ligne stale `--default_dropshadow`, puis converger `--settings-*`,
`--profile-*` et `--astro-*` vers des owners canoniques ou extensions
semantiques non legacy. Aucun namespace compatibility, migration-only, alias ou
fallback ne doit rester apres implementation.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-002`
- Reason for change: `F-005` indique que des namespaces migration-only restent actifs ou inscrits malgre la fin attendue des surfaces legacy.

## Domain Boundary

- Domain: `frontend/src/styles`
- In scope:
  - Supprimer `--default_dropshadow` du registre si les scans confirment zero usage actif.
  - Reclasser ou renommer `--settings-*`, `--profile-*` et `--astro-*` sans statut migration-only.
  - Migrer les consommateurs owners listes par l'audit vers tokens canoniques ou extensions semantiques finales.
  - Ajouter des scans no-return exacts pour les noms retires.
- Out of scope:
  - Corriger la dependance HelpPage a `--settings-*`, couverte par `CS-074`.
  - Migrer toutes les valeurs hardcodees de l'application.
  - Refonte visuelle des pages Settings, Profile ou Astro.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-049` ou `RG-050`.
  - Ne pas conserver de statut migration-only apres implementation.
  - Ne pas accepter de `PASS with limitation`.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime les facades de tokens migration-only et route les consommateurs vers des owners canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux remplacements par tokens canoniques documentes.
  - Les pages Settings, Profile et Astro gardent leurs intentions visuelles.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un namespace est prouve `external-active`; sinon la decision utilisateur fournie impose la suppression du legacy restant.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards theme-tokens/design-system prouvent l'etat actif des namespaces. |
| Baseline Snapshot | yes | Les inventaires before/after prouvent la convergence exacte. |
| Ownership Routing | yes | Chaque namespace retire doit etre route vers un owner final. |
| Allowlist Exception | no | Aucune exception migration-only n'est autorisee. |
| Contract Shape | no | Aucun contrat API ou type public n'est modifie. |
| Batch Migration | no | La suppression se pilote par classification de namespaces. |
| Reintroduction Guard | yes | Les noms retires ne doivent pas revenir. |
| Persistent Evidence | yes | Les decisions et scans doivent etre persistants. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/legacy-style-policy.test.ts`
- Secondary evidence:
  - scans `rg` sur `frontend/src` pour les declarations et consommateurs.
- Static scans alone are not sufficient because:
  - le registre doit rester synchronise avec les guards executables.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-075-converger-namespaces-css-migration-only-restants/token-migration-only-before.md`.
- Comparison after implementation: `_condamad/stories/CS-075-converger-namespaces-css-migration-only-restants/token-migration-only-after.md`.
- Expected invariant: zero namespace `migration-only` ou stale alias dans le registre apres implementation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token global | `frontend/src/styles/design-tokens.css` | registre migration-only |
| Token page semantique | CSS owner de la page et row registry `semantic-extension` | namespace compatibility ou migration-only |
| Token stale sans usage | suppression complete | conservation documentaire active |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune allowlist de namespace migration-only n'est autorisee.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la classification removal par namespace est le contrat actif.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before namespace baseline | `token-migration-only-before.md` | Inventorier rows et usages `--settings-*`, `--profile-*`, `--astro-*`, `--default_dropshadow`. |
| After namespace evidence | `token-migration-only-after.md` | Prouver zero legacy restant et owners finaux. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: les namespaces retires ou statuts migration-only echouent s'ils sont reintroduced.
- Deterministic source: forbidden symbols in `token-namespace-registry.md`, CSS owners et tests design-system.
- Required forbidden examples:
  - `--default_dropshadow`
  - row `migration-only` pour `--settings-*`, `--profile-*` ou `--astro-*`
  - nouvel usage `compatibility`, `legacy`, `alias`, `shim`
- Guard evidence: `npm run test -- design-system theme-tokens legacy-style`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-005` - namespaces migration-only restants.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md#E-011`
  - scan en echec sur namespaces et registre.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - `RG-044`, `RG-045`, `RG-049` et `RG-050` consultes avant cadrage.

## Target State

- Le registre ne contient plus `--default_dropshadow`.
- Aucun namespace `--settings-*`, `--profile-*` ou `--astro-*` n'est classe migration-only ou compatibility.
- Les consommateurs actifs pointent vers owners canoniques ou extensions semantiques finales.
- Les guards et scans passent sans limitation.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace de token doit etre classe et source.
  - `RG-045` - les valeurs migrees ne doivent pas revenir en hardcoded concurrents.
  - `RG-049` - aucune surface CSS legacy ne doit rester.
  - `RG-050` - les exceptions design-system doivent rester exactes.
- Non-applicable invariants:
  - `RG-047` - aucun style inline TSX attendu.
  - `RG-048` - aucun fallback CSS ne doit etre ajoute; tout ajout bloque.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens legacy-style visual-smoke`
  - scans zero-hit des noms retires et du statut `migration-only`.
- Allowed differences:
  - differences visuelles uniquement si documentees dans `token-migration-only-after.md`.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe chaque namespace vise. | Evidence profile: `baseline_before_after_diff`; command `rg -e "--settings-" -e "--profile-" -e "--astro-" src styles`. |
| AC2 | `--default_dropshadow` reste zero-hit. | Evidence profile: `removal`; command `rg -n -- "--default_dropshadow" src`. |
| AC3 | Aucun row `migration-only` ou `compatibility` ne reste pour les namespaces vises. | Evidence profile: `registry_guard`; `npm run test -- theme-tokens design-system`. |
| AC4 | Les consommateurs utilisent des owners canoniques non legacy. | Evidence profile: `ownership_routing`; after artifact plus `npm run test -- legacy-style visual-smoke`. |
| AC5 | Les noms retires sont gardes contre retour. | Evidence profile: `reintroduction_guard`; command `npm run test -- design-system theme-tokens legacy-style`. |

## Implementation Tasks

- [ ] Task 1 - Capturer baseline des namespaces et consommateurs. (AC: AC1)
- [ ] Task 2 - Supprimer `--default_dropshadow` si zero usage actif est confirme. (AC: AC2)
- [ ] Task 3 - Migrer ou reclasser `--settings-*`, `--profile-*`, `--astro-*` vers owners finaux. (AC: AC3, AC4)
- [ ] Task 4 - Mettre a jour registre et guards anti-retour. (AC: AC3, AC5)
- [ ] Task 5 - Capturer after et executer tests, lint et scans. (AC: AC2, AC4, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse `design-tokens.css`, `theme.css`, `token-namespace-registry.md`, `legacy-style-surface-registry.md` et les helpers de policy existants.
- Do not create a second registry or a duplicate namespace for the same visual responsibility.
- Shared abstraction allowed only if elle remplace plusieurs consommateurs et reste non legacy.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `--default_dropshadow`
  - `migration-only` pour les namespaces vises
  - tout nouvel alias `legacy`, `compat`, `shim`, `fallback`

## Removal Classification Rules

- `canonical-active`: namespace owner final documente et consomme par production.
- `external-active`: namespace reference par doc publique ou contrat externe; bloque deletion sauf decision explicite.
- `historical-facade`: namespace migration-only ou compatibility deleguant a un owner canonique.
- `dead`: row ou declaration sans usage actif.
- `needs-user-decision`: ambiguite restante apres scans; ne doit pas etre utilisee pour contourner la decision utilisateur "Aucun legacy ne doit rester".

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `replace-consumer` | Must be deleted or consumers migrated. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path:
- `_condamad/stories/CS-075-converger-namespaces-css-migration-only-restants/token-migration-only-after.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Token namespace governance | `frontend/src/styles/token-namespace-registry.md` | migration-only rows without exit |
| Global design tokens | `frontend/src/styles/design-tokens.css` | stale aliases and unowned variables |
| Page semantic tokens | owning page CSS plus registry classification | cross-page compatibility namespace |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: wrapper CSS, compatibility alias, fallback variable, deprecated active namespace, soft-disable behavior, or re-export.

## External Usage Blocker

- `external-active` items must not be deleted without a user decision.
- If an item is classified as `external-active`, implementation must stop and
  record exact evidence. The current user decision removes internal legacy, but
  does not authorize breaking proven external public contracts silently.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path may change for this frontend token story.
- Generated artifact absence: if a generated route manifest, token snapshot,
  client or schema exists after inspection, prove `--default_dropshadow` and
  migration-only rows are absent.
- Required evidence: `rg -n -- "--default_dropshadow|migration-only" src styles` plus generated artifact scan if such artifact exists.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/App.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/styles/token-namespace-registry.md` - retirer ou reclasser les rows.
- `frontend/src/App.css` - migrer consommateurs si presents.
- `frontend/src/pages/settings/Settings.css` - converger namespace Settings.
- `frontend/src/pages/AstrologerProfilePage.css` - converger namespaces Profile/Astro.

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts` - anti-retour namespaces.
- `frontend/src/tests/theme-tokens.test.ts` - registre synchronise.

Files not expected to change:
- `backend/app/main.py` - aucun backend dans le scope.
- `frontend/package.json` - aucune dependance ou script requis.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens legacy-style visual-smoke
npm run test -- css-fallback
npm run lint
rg -n -- "--default_dropshadow" src
rg -n "migration-only|compatibility|legacy|alias|shim" src/styles/token-namespace-registry.md
rg -n -- "--settings-|--profile-|--astro-" src/App.css src/pages/settings/Settings.css src/pages/AstrologerProfilePage.css src/styles/token-namespace-registry.md
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-075-converger-namespaces-css-migration-only-restants/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: un namespace utile est supprime sans owner final.
  - Guardrail: audit classification et visual-smoke.
- Risk: un statut migration-only reste comme documentation active.
  - Guardrail: scan registre et tests theme-tokens.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-002`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-005`
- `_condamad/stories/regression-guardrails.md`
