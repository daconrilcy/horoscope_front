# Story CS-073 migrer-cluster-help-page-valeurs-visuelles-hardcodees: Migrer le cluster HelpPage de valeurs visuelles hardcodees

Status: done

## Objective

Migrer un cluster coherent de valeurs visuelles et typographiques hardcodees
dans `HelpPage.css` vers les tokens, roles typographiques ou variables
semantiques existants. Le lot doit etre borne, documente par artefacts
before/after, sans refactor global, sans legacy restant et sans AC en
`PASS with limitation`.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-003`
- Reason for change: l'audit `F-004` indique que 106 fichiers frontend gardent
  des valeurs visuelles hardcodees; `HelpPage.css` est une option recommandee
  pour un prochain cluster borne.

## Domain Boundary

- Domain: `frontend/src/pages/HelpPage.css`
- In scope:
  - Capturer les valeurs hardcodees du cluster `HelpPage.css` avant implementation.
  - Remplacer les valeurs repetees ou semantiques par des tokens/roles existants ou variables locales non legacy.
  - Mettre a jour les registres design-system uniquement si une extension semantique durable est necessaire.
  - Capturer un after avec 100% de decisions finales.
- Out of scope:
  - Migrer les 105 autres fichiers de l'inventaire `F-004`.
  - Refonte visuelle de la page aide.
  - Modifier les routes, contenus i18n, API ou logique React de la page.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046`, `RG-048` ou `RG-050`.
  - Ne pas creer de token global pour une valeur one-off.
  - Ne pas conserver de literal migre sous forme de doublon parallele.
  - Ne pas introduire de namespace `legacy`, `compatibility`, `migration-only`, alias ou fallback.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace de token nouveau ou modifie doit rester classe.
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir non classees.
  - `RG-046` - les repetitions typographiques doivent passer par les roles documentes.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
- Non-applicable invariants:
  - `RG-047` - aucun style inline TSX n'est dans le scope attendu.
  - `RG-049` - aucun selecteur legacy ou alias n'est attendu dans ce cluster; tout hit doit bloquer.
- Required regression evidence:
  - `npm run test -- design-system visual-smoke`
  - focused HelpPage test si existant, sinon justification dans `generated/10-final-evidence.md`
  - scans exacts des literals migres documentes dans `hardcoded-values-after.md`.
- Allowed differences:
  - Differences visuelles uniquement si elles correspondent a un token canonique documente dans l'after.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de valeurs CSS vers des owners canoniques avec mapping before/after.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le layout et les interactions de la page aide doivent rester inchanges.
  - Les differences de rendu autorisees sont limitees aux equivalents de tokens documentes.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une valeur hardcodee ne peut etre ni migree, ni justifiee comme one-off final sans creer de dette legacy.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system et visual-smoke prouvent l'etat executable. |
| Baseline Snapshot | yes | Les artefacts before/after bornent le cluster. |
| Ownership Routing | no | Les owners sont documentes dans le plan batch et les registres, sans refactor de frontiere. |
| Allowlist Exception | no | Aucune exception temporaire ou large n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route ou type public n'est modifie. |
| Batch Migration | yes | Les valeurs du cluster sont mappees par categories vers owners canoniques. |
| Reintroduction Guard | yes | Les valeurs migrees ne doivent pas revenir non classees. |
| Persistent Evidence | yes | Les artefacts before/after et resultats doivent rester consultables. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/visual-smoke.test.ts` if present after inspection
- Secondary evidence:
  - scans `rg` cibles sur `frontend/src/pages/HelpPage.css`.
- Static scans alone are not sufficient for this story because:
  - une migration de valeurs visuelles doit conserver les invariants de rendu et de gouvernance executables.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-073-migrer-cluster-help-page-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-073-migrer-cluster-help-page-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur du cluster a une decision finale `migrated`, `registered-semantic-owner` ou `kept-one-off-final`, sans TODO ni limitation.

## Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: no exception is allowed by this story.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Help colors | color literals | tokens or local semantic vars | `HelpPage.css` | design-system and smoke | after color scan | no equivalent token |
| Help spacing/radius | spacing/radius literals | tokens or final one-off | `HelpPage.css` | design-system | decision table | cannot route repeated value |
| Help typography | type literals | typography roles or tokens | `HelpPage.css`, registry for durable role | theme/design tests | after type scan | durable role missing |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before hardcoded-value baseline | `hardcoded-values-before.md` | Borne le cluster HelpPage et les valeurs initiales. |
| After hardcoded-value evidence | `hardcoded-values-after.md` | Persiste les decisions finales et scans anti-retour. |
| Final validation evidence | `generated/10-final-evidence.md` | Persist commands, results and residual risks. |

## Reintroduction Guard

- Architecture guard: migrated HelpPage literals must fail if they return without final classification.
- Deterministic source: values listed in `hardcoded-values-after.md` and CSS guard tests.
- Required forbidden examples:
  - migrated hex/rgb/hsl color literals from `HelpPage.css`
  - migrated repeated `font-size`, `font-weight`, `line-height`, `border-radius`, `box-shadow`
  - any new `var(--token, literal)` fallback
- Guard evidence:
  - Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens css-fallback`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0932/00-audit-report.md`
  - `frontend/src/pages/HelpPage.css` is in the hardcoded-value inventory.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-003` - recommends choosing one bounded cluster, including `HelpPage.css`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - `RG-044`, `RG-045`, `RG-046`, `RG-048` and `RG-050` consulted before story scope was finalized.

## Target State

- `HelpPage.css` uses existing tokens, typography roles, or documented local semantic variables for repeated visual decisions.
- Any remaining one-off literal is explicitly final in `hardcoded-values-after.md`, not a deferred limitation.
- No new fallback, compatibility namespace, migration-only namespace, legacy selector or alias is introduced.
- Design-system, token, fallback and visual smoke validations pass.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The cluster is exactly bounded to `HelpPage.css`. | Evidence profile: `baseline_before_after_diff`; capture the AC1 `rg` command in `hardcoded-values-before.md`. |
| AC2 | 100% of HelpPage values have final decisions. | Evidence profile: `persistent_evidence`; AC2 after-artifact `rg` scan returns zero. |
| AC3 | Repeated values migrate to canonical owners. | Evidence profile: `batch_migration_mapping`; `npm run test -- theme-tokens design-system`. |
| AC4 | No forbidden namespace is introduced. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- css-fallback theme-tokens legacy-style`. |
| AC5 | HelpPage visual smoke remains green. | Evidence profile: `runtime_guard`; `npm run test -- design-system visual-smoke` and focused HelpPage test if one exists. |
| AC6 | Migrated literals cannot silently return. | Evidence profile: `reintroduction_guard`; exact migrated-value scans in `hardcoded-values-after.md` and `npm run lint`. |

## Implementation Tasks

- [x] Task 1 - Capture before artifact for `HelpPage.css` values only. (AC: AC1, AC2)
- [x] Task 2 - Classify every value as `migrate`, `registered-semantic-owner`, or `kept-one-off-final`. (AC: AC2)
- [x] Task 3 - Replace repeated values with existing tokens, roles, or documented local semantic variables. (AC: AC3)
- [x] Task 4 - Update token or typography registries only when a durable non-legacy owner is created. (AC: AC3, AC4)
- [x] Task 5 - Capture after artifact, exact anti-return scans and final validation evidence. (AC: AC2, AC4, AC6)
- [x] Task 6 - Run focused frontend tests, lint and story validation. (AC: AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`, `frontend/src/styles/token-namespace-registry.md` and `frontend/src/styles/typography-roles.md`.
- Do not create a global token for a one-off HelpPage-only literal.
- Do not duplicate migrated literals in parallel CSS declarations.
- Shared semantic extensions are allowed only if documented, reusable and non-legacy.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, fallback CSS, duplicate active values, migration-only namespaces, legacy namespaces.
- Forbidden: `var(--token, literal)` fallback in `HelpPage.css`.
- Forbidden: any selector or custom property name containing `legacy`, `alias`, `compat`, `shim` or `fallback`.

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| HelpPage visual values | existing design tokens, typography roles, or documented local semantic variables | raw repeated literals and ad hoc variables |
| Cluster evidence | story before/after artifacts | console-only validation or undocumented reviewer memory |

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-0932/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/pages/HelpPage.css` - migrate cluster values.
- `frontend/src/styles/token-namespace-registry.md` - only if a durable token namespace decision changes.
- `frontend/src/styles/typography-roles.md` - only if a durable typography role is added or updated.

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- focused HelpPage test if one exists after inspection.

Files not expected to change:
- `backend/app/main.py` - no backend behavior is in scope.
- `frontend/package.json` - no dependency or script change is required.
- Other files from the 106-file inventory - out of scope for this story.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke
npm run test -- HelpPage
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/HelpPage.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/HelpPage.css
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/HelpPage.css
rg -n "legacy|Legacy|alias|compat|shim|fallback|migration-only" src/pages/HelpPage.css
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-073-migrer-cluster-help-page-valeurs-visuelles-hardcodees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: the cluster grows into a broad 106-file cleanup.
  - Guardrail: AC1 and before artifact must list only `HelpPage.css`.
- Risk: near-equivalent tokens create visible drift.
  - Guardrail: visual-smoke and after artifact allowed differences.
- Risk: hardcoded values are replaced by local compatibility variables.
  - Guardrail: token namespace and fallback scans.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not create compatibility shims, aliases, fallbacks, wrappers, migration-only namespaces or re-exports.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0932/03-story-candidates.md#SC-003`
- `_condamad/audits/frontend-design-system/2026-05-06-0932/02-finding-register.md#F-004`
- `_condamad/stories/regression-guardrails.md`
