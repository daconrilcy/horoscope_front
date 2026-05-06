# Story CS-078 migrer-cluster-prediction-valeurs-visuelles-hardcodees: Migrer le cluster prediction de valeurs visuelles hardcodees

Status: ready-to-dev

## Objective

Migrer un cluster coherent de valeurs visuelles et typographiques hardcodees
dans les composants prediction de la page horoscope quotidienne vers les tokens,
roles typographiques ou variables semantiques existants. Le lot est
volontairement borne aux fichiers prediction listes, sans migration globale et
sans AC limitee.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-005`
- Reason for change: `F-003` indique que 101 fichiers frontend contiennent encore
  des valeurs visuelles ou typographiques hardcodees; le cluster prediction est
  une option recommandee.

## Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un baseline hardcoded-values pour le cluster prediction borne.
  - Migrer les valeurs repetees des fichiers prediction selectionnes vers tokens/roles/variables semantiques non legacy.
  - Mettre a jour les registres de tokens ou typographie seulement si un owner durable est cree.
  - Ajouter les scans no-return des literals migres.
- Out of scope:
  - Modifier les 101 fichiers de l'inventaire.
  - Modifier les mappers runtime legacy prediction, couverts par `CS-076`.
  - Refonte UX de la page horoscope quotidienne.
- Explicit non-goals:
  - Ne pas affaiblir `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas introduire fallback CSS, alias ou namespace migration-only.
  - Ne pas accepter de `PASS with limitation`.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de valeurs CSS/TSX vers owners canoniques avec mapping before/after.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents de tokens documentes.
  - Les comportements et donnees prediction restent inchanges.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une valeur ne peut etre ni migree ni classee comme one-off final sans dette.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests visual-smoke/design-system prouvent la surface frontend. |
| Baseline Snapshot | yes | Les artefacts before/after bornent le cluster. |
| Ownership Routing | no | Aucun transfert de responsabilite de domaine n'est attendu hors owners de tokens documentes. |
| Allowlist Exception | no | Aucune exception temporaire n'est autorisee. |
| Contract Shape | no | Aucun contrat API, route ou type payload n'est modifie. |
| Batch Migration | yes | Les valeurs sont migrees par lots de fichiers prediction. |
| Reintroduction Guard | yes | Les literals migres ne doivent pas revenir. |
| Persistent Evidence | yes | Les scans et decisions doivent rester consultables. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/visual-smoke.test.ts` if present after inspection.
- Secondary evidence:
  - scans hardcoded-values cibles sur les fichiers du cluster.
- Static scans alone are not sufficient because:
  - les composants prediction doivent rester rendus sans regression visuelle majeure.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-078-migrer-cluster-prediction-valeurs-visuelles-hardcodees/hardcoded-values-before.md`.
- Comparison after implementation: `_condamad/stories/CS-078-migrer-cluster-prediction-valeurs-visuelles-hardcodees/hardcoded-values-after.md`.
- Expected invariant: chaque valeur du cluster a une decision finale `migrated`, `registered-semantic-owner` ou `kept-one-off-final`, sans TODO ni limitation.

## Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected beyond token owner documentation.

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: no exception is allowed by this story.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Prediction colors | color literals | design tokens or local semantic vars | prediction CSS files | design-system | after color scan | no equivalent owner |
| Prediction typography | hardcoded font values | typography roles or tokens | prediction CSS files | design-system | after type scan | durable role missing |
| Prediction spacing/elevation | spacing, radius, shadow | tokens or one-off final | prediction CSS files | visual-smoke | after literal scan | cannot classify |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before hardcoded-value baseline | `hardcoded-values-before.md` | Borne les fichiers et valeurs initiales du cluster. |
| After hardcoded-value evidence | `hardcoded-values-after.md` | Persiste decisions finales et scans anti-retour. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: les literals migres echouent s'ils sont reintroduced non classes dans le cluster.
- Deterministic source: forbidden symbols in `hardcoded-values-after.md`, tests design-system et scans `rg`.
- Required forbidden examples:
  - hex/rgb/hsl migres
  - `font-size`, `font-weight`, `line-height`, `letter-spacing` migres
  - `box-shadow`, `border-radius` ou spacing migres quand remplaces par token
- Guard evidence: `npm run test -- design-system theme-tokens visual-smoke`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-003` - 101 fichiers contiennent des valeurs hardcodees.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1031/00-audit-report.md`
  - inventaire exhaustif des fichiers candidats pour `F-003`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - `RG-045`, `RG-046` et `RG-050` consultes avant cadrage.

## Target State

- Le cluster prediction selectionne utilise des tokens/roles/variables semantiques non legacy pour les valeurs repetees.
- Les valeurs restantes, s'il y en a, sont finalisees comme one-off et documentees dans l'after.
- Aucun fallback, alias, compatibility ou migration-only n'est ajoute.
- Les validations passent sans limitation.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir.
  - `RG-046` - les repetitions typographiques passent par roles semantiques.
  - `RG-050` - la suite design-system anti-drift doit rester executable.
- Non-applicable invariants:
  - `RG-047` - styles inline hors scope sauf si un fichier TSX du cluster est explicitement inclus dans le baseline.
  - `RG-049` - aucun selector legacy n'est attendu; tout hit bloque.
- Required regression evidence:
  - `npm run test -- design-system visual-smoke`
  - tests focalises prediction existants si trouves apres inspection.
  - scans exacts des literals migres.
- Allowed differences:
  - differences visuelles uniquement si documentees dans `hardcoded-values-after.md`.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster est borne aux fichiers prediction selectionnes. | Command `rg -e "font-size:" -e "rgba(" src/components/prediction`. |
| AC2 | Chaque valeur du cluster a une decision finale. | Evidence profile: `persistent_evidence`; command `rg -e TODO -e "PASS with limitation" hardcoded-values-after.md`. |
| AC3 | Les valeurs repetees migrent vers owners canoniques non legacy. | Evidence profile: `batch_migration_mapping`; `npm run test -- theme-tokens design-system`. |
| AC4 | Aucun fallback CSS n'est introduit. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- css-fallback legacy-style`. |
| AC5 | Les composants prediction restent couverts. | Evidence profile: `runtime_guard`; `npm run test -- visual-smoke DailyHoroscopePage`. |
| AC6 | Les literals migres ne peuvent pas revenir silencieusement. | Evidence profile: `reintroduction_guard`; scans exacts dans `hardcoded-values-after.md` et `npm run lint`. |

## Implementation Tasks

- [ ] Task 1 - Choisir et documenter le cluster prediction exact depuis l'inventaire. (AC: AC1)
- [ ] Task 2 - Capturer les valeurs hardcodees before pour ce cluster uniquement. (AC: AC1, AC2)
- [ ] Task 3 - Migrer valeurs repetees vers tokens, roles ou variables semantiques existants. (AC: AC3)
- [ ] Task 4 - Mettre a jour registres uniquement si un owner durable non legacy est cree. (AC: AC3, AC4)
- [ ] Task 5 - Capturer after, scans no-return, tests et lint. (AC: AC2, AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`, `frontend/src/styles/token-namespace-registry.md` et `frontend/src/styles/typography-roles.md`.
- Do not create duplicated local variables for the same prediction visual role.
- Shared abstraction allowed only if elle retire une duplication reelle et reste documentee.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `legacy`, `Legacy`, `alias`, `compat`, `shim`, `fallback`, `migration-only` dans les fichiers touches.
  - `var(--token, literal)` fallback dans les fichiers touches.

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Prediction visual values | design tokens, typography roles, or documented semantic vars | repeated hardcoded literals |
| Cluster evidence | story before/after artifacts | undocumented local decisions |

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1031/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/pages/DailyHoroscopePage.css` - migrate selected hardcoded values if included in baseline.
- `frontend/src/components/prediction/DailyAdviceCard.css` - migrate selected hardcoded values if included.
- `frontend/src/components/prediction/DailyPageHeader.css` - migrate selected hardcoded values if included.
- `frontend/src/components/prediction/DayAgenda.css` - migrate selected hardcoded values if included.
- `frontend/src/components/prediction/DayPredictionCard.css` - migrate selected hardcoded values if included.
- `frontend/src/components/prediction/DayStateBadge.css` - migrate selected hardcoded values if included.
- `frontend/src/components/prediction/DayTimeline.css` - migrate selected hardcoded values if included.
- `frontend/src/components/prediction/TurningPointsList.css` - migrate selected hardcoded values if included.
- `frontend/src/styles/token-namespace-registry.md` - only if a durable semantic owner is added.
- `frontend/src/styles/typography-roles.md` - only if a durable typography role is added.

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts` - anti-return or hardcoded policy.
- `frontend/src/tests/theme-tokens.test.ts` - token registry if changed.
- `frontend/src/tests/visual-smoke.test.ts` - visual smoke if present.

Files not expected to change:
- `frontend/src/types/consultation.ts` - runtime compatibility covered by `CS-076`.
- `frontend/src/app/routes.tsx` - routing covered by `CS-077`.
- `backend/app/main.py` - no backend scope.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke DailyHoroscopePage
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/DailyHoroscopePage.css src/components/prediction -g "*.css"
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/DailyHoroscopePage.css src/components/prediction -g "*.css"
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/DailyHoroscopePage.css src/components/prediction -g "*.css"
rg -n "legacy|Legacy|alias|compat|shim|fallback|migration-only" src/pages/DailyHoroscopePage.css src/components/prediction -g "*.css" -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-078-migrer-cluster-prediction-valeurs-visuelles-hardcodees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: le cluster s'elargit a une migration repository-wide.
  - Guardrail: AC1 et baseline bornent les fichiers.
- Risk: remplacement token provoque une derive visuelle.
  - Guardrail: visual-smoke et after artifact.
- Risk: hardcoded values remplacees par variables legacy locales.
  - Guardrail: No Legacy scans et token registry.

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

- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-005`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-003`
- `_condamad/stories/regression-guardrails.md`
