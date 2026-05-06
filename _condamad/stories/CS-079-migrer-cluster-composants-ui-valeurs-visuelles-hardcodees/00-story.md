# Story CS-079 migrer-cluster-composants-ui-valeurs-visuelles-hardcodees: Migrer le cluster composants UI de valeurs visuelles hardcodees

Status: done

## Objective

Migrer un cluster borne de composants UI partages vers les tokens, roles
typographiques et variables semantiques existants, sans refactor global. La
story doit reduire l'inventaire `F-002` sur un lot coherent, produire des
artefacts before/after, ne laisser aucun legacy et ne permettre aucune AC en
`PASS with limitation`.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md#SC-001`
- Reason for change: `F-002` indique que 101 fichiers applicatifs frontend
  gardent des valeurs visuelles ou typographiques hardcodees; le cluster des
  primitives UI partagees est un lot coherent et reutilisable.

## Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un baseline hardcoded-values pour les composants UI partages selectionnes.
  - Migrer les valeurs repetees vers tokens, roles typographiques ou variables semantiques non legacy.
  - Mettre a jour les registres design-system uniquement si un owner durable est cree.
  - Ajouter une preuve anti-retour des literals migres.
- Out of scope:
  - Modifier les 101 fichiers de l'inventaire.
  - Modifier les pages produit, admin, prediction, natal ou profile hors consommation directe des composants UI.
  - Refonte UX des composants ou changement de comportement React.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046`, `RG-048` ou `RG-050`.
  - Ne pas changer `RG-053`, `RG-054` ou les decisions runtime legacy.
  - Ne pas creer de namespace `legacy`, `compatibility`, `migration-only`, alias ou fallback.
  - Ne pas accepter de `PASS with limitation`.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de valeurs CSS/TSX vers des owners canoniques avec mapping before/after.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents de tokens documentes.
  - Les API React, props, comportements de loading/error/empty states et exports publics restent inchanges.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une valeur repetee ne peut etre ni migree ni classee comme one-off final sans dette legacy.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system et smoke prouvent que les primitives restent rendues. |
| Baseline Snapshot | yes | Les artefacts before/after bornent le cluster et les valeurs migrees. |
| Ownership Routing | yes | Les valeurs partagees doivent etre routees vers owners design-system canoniques. |
| Allowlist Exception | no | Aucune exception temporaire ou large n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route ou payload n'est modifie. |
| Batch Migration | yes | Les valeurs sont migrees par categories de composants UI. |
| Reintroduction Guard | yes | Les literals migres ne doivent pas revenir dans le cluster. |
| Persistent Evidence | yes | Les scans et decisions doivent rester consultables. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/visual-smoke.test.ts` if present after inspection
- Secondary evidence:
  - scans `rg` cibles sur `frontend/src/components/ui/**`.
- Static scans alone are not sufficient because:
  - les primitives UI doivent rester rendues avec leurs etats accessibles et reutilisables.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur du cluster a une decision finale `migrated`, `registered-semantic-owner` ou `kept-one-off-final`, sans TODO, sans legacy et sans limitation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleurs UI partagees | `frontend/src/styles/design-tokens.css` ou extension semantique documentee | variables locales dupliquees par composant |
| Typographie UI partagee | `frontend/src/styles/typography-roles.md` et tokens existants | tailles/poids/line-height repetes sans owner |
| Radius, spacing, elevation | tokens existants ou one-off final documente | alias, fallback ou namespace migration-only |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: no exception is allowed by this story.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| UI colors | hex/rgb/hsl literals | tokens or documented semantic vars | selected `components/ui` CSS | design-system/theme | after color scan | no equivalent owner |
| UI typography | font-size, weight, line-height literals | typography roles or tokens | selected `components/ui` CSS/TSX | design-system | after type scan | durable role missing |
| UI shape/elevation | radius, shadow, spacing | tokens or final one-off | selected UI CSS | css-fallback/smoke | after scan | cannot classify |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before hardcoded-value baseline | `hardcoded-values-before.md` | Borne les fichiers UI et valeurs initiales. |
| After hardcoded-value evidence | `hardcoded-values-after.md` | Persiste decisions finales et scans anti-retour. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: les literals migres du cluster UI echouent s'ils reviennent sans classification finale.
- Deterministic source: values listed in `hardcoded-values-after.md`, tests design-system et scans `rg`.
- Required forbidden examples:
  - hex/rgb/hsl migres des composants UI.
  - `font-size`, `font-weight`, `line-height`, `letter-spacing` migres.
  - `box-shadow`, `border-radius` ou `var(--token, literal)` migres.
- Guard evidence: `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1618/00-audit-report.md`
  - `F-002` liste 101 fichiers candidats et inclut les composants UI partages.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1618/01-evidence-log.md#E-010`
  - le scan hardcoded-values non-test reste en echec sur 101 fichiers.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md#SC-001`
  - recommande de choisir un cluster coherent et de ne pas modifier tous les fichiers.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-044`, `RG-045`, `RG-046`, `RG-048`, `RG-050` et `RG-055` consultes avant cadrage.

## Target State

- Les primitives UI selectionnees utilisent des tokens, roles typographiques ou variables semantiques non legacy.
- Les valeurs restantes sont documentees comme one-off finales dans l'after, pas comme dette reportee.
- Aucun fallback CSS, alias, compatibility namespace ou migration-only namespace n'est ajoute.
- Les validations frontend passent sans limitation.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace nouveau ou modifie doit rester classe.
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir non classees.
  - `RG-046` - les repetitions typographiques passent par roles semantiques.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
- Non-applicable invariants:
  - `RG-053` - aucune compatibilite runtime n'est dans ce scope.
  - `RG-054` - aucune route admin legacy n'est dans ce scope.
  - `RG-055` - le cluster prediction premium n'est pas modifie.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke`
  - scans exacts des literals migres dans `hardcoded-values-after.md`.
- Allowed differences:
  - differences visuelles uniquement si documentees dans `hardcoded-values-after.md` comme equivalent tokenise.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster est borne uniquement aux composants UI selectionnes. | Evidence profile: `baseline_before_after_diff`; before artifact avec liste exacte et commande `rg`. |
| AC2 | Toutes les valeurs ont une decision finale. | Evidence profile: `persistent_evidence`; command `rg -n "TODO|PASS with limitation|legacy" hardcoded-values-after.md`. |
| AC3 | Les valeurs repetees migrent vers owners canoniques non legacy. | Evidence profile: `batch_migration_mapping`; `npm run test -- theme-tokens design-system`. |
| AC4 | Aucun fallback CSS ou namespace non canonique n'est introduit. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- css-fallback legacy-style`. |
| AC5 | Les primitives UI restent couvertes par les guards frontend. | Evidence profile: `runtime_guard`; `npm run test -- design-system visual-smoke`. |
| AC6 | Les literals migres ne peuvent pas revenir silencieusement. | Evidence profile: `reintroduction_guard`; after scans exacts et `npm run lint`. |

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline des fichiers UI selectionnes uniquement. (AC: AC1, AC2)
- [ ] Task 2 - Classer chaque valeur du cluster avec une decision finale. (AC: AC2)
- [ ] Task 3 - Migrer les valeurs repetees vers tokens, roles ou variables semantiques existants. (AC: AC3)
- [ ] Task 4 - Mettre a jour les registres uniquement si un owner durable non legacy est cree. (AC: AC3, AC4)
- [ ] Task 5 - Ajouter ou ajuster les guards anti-retour exacts si le projet en dispose deja. (AC: AC5, AC6)
- [ ] Task 6 - Capturer l'after, les scans zero-hit, les tests et le lint. (AC: AC2, AC4, AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`, `frontend/src/styles/token-namespace-registry.md` et `frontend/src/styles/typography-roles.md`.
- Reuse les composants UI existants; ne pas creer de doublon de primitive pour eviter une migration CSS.
- Do not create duplicated local variables for the same shared visual role.
- Shared abstraction allowed only if elle retire une duplication reelle entre composants UI et reste documentee.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `legacy`, `Legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` dans les fichiers touches.
  - `var(--token, literal)` fallback dans les fichiers touches.
  - nouveau namespace global non documente dans `frontend/src/styles/token-namespace-registry.md`.

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Shared UI visual values | design tokens, typography roles, or documented semantic vars | repeated hardcoded literals in `components/ui` |
| Cluster evidence | story before/after artifacts | undocumented local decisions |

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1618/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/components/ui/Badge/Badge.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/Button/Button.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/Card/Card.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/EmptyState/EmptyState.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/ErrorState/ErrorState.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/Field/Field.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/LockedSection/LockedSection.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/Modal/Modal.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/Select/Select.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/Skeleton/Skeleton.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/UserAvatar/UserAvatar.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/components/ui/UserMenu/UserMenu.css` - migrate selected hardcoded values if present after baseline.
- `frontend/src/styles/token-namespace-registry.md` - only if a durable semantic namespace is added or reclassified.
- `frontend/src/styles/typography-roles.md` - only if a durable typography role is added.

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts` - anti-return or hardcoded policy updates required by migrated values.
- `frontend/src/tests/theme-tokens.test.ts` - token registry validation if registry changes.
- `frontend/src/tests/css-fallback-policy.test.ts` - fallback guard preservation.
- `frontend/src/tests/visual-smoke.test.ts` - smoke coverage if present.

Files not expected to change:
- `frontend/src/pages/DailyHoroscopePage.css` - prediction cluster covered by `CS-078`.
- `frontend/src/pages/HelpPage.css` - HelpPage cluster already covered by `CS-073` and `CS-074`.
- `frontend/src/pages/admin/AdminSettingsPage.css` - admin settings cluster already covered by `CS-069`.
- `frontend/package.json` - no dependency or script change is required.
- `backend/app/main.py` - no backend behavior is in scope.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/components/ui -g "*.css" -g "*.tsx"
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/components/ui -g "*.css" -g "*.tsx"
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/components/ui -g "*.css" -g "*.tsx"
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/components/ui -g "*.css" -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: la migration de primitives UI provoque une derive visuelle transverse.
  - Guardrail: visual-smoke, design-system guards et after artifact.
- Risk: le cluster s'elargit a une migration globale.
  - Guardrail: AC1 borne les fichiers exacts.
- Risk: des literals sont remplaces par variables locales legacy.
  - Guardrail: scans No Legacy et registre de tokens.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers, migration-only namespaces or re-exports.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md#SC-001`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/02-finding-register.md#F-002`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/01-evidence-log.md#E-010`
- `_condamad/stories/regression-guardrails.md`
