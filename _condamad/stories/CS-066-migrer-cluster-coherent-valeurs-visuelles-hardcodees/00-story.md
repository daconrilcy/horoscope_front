# Story CS-066 migrer-cluster-coherent-valeurs-visuelles-hardcodees: Migrer un cluster coherent de valeurs visuelles hardcodees

Status: ready-to-dev

## Objective

Reduire la dette de valeurs visuelles hardcodees en migrant un seul cluster produit coherent.
La migration utilise tokens, roles typographiques et utilitaires existants, avec preuves before/after.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-003`
- Reason for change: diminuer progressivement les valeurs visuelles hardcodees tout en gardant une migration bornée et testable.

## Domain Boundary

- Domain: `frontend/src/styles`
In scope:
- Choisir un seul cluster: admin prompts, admin shell, prediction cards, UI primitives, chat shell, landing, natal ou app legacy shell.
- Utiliser les tokens, roles typographiques et utilitaires existants avant toute creation de token.
- Capturer les compteurs before/after des valeurs hardcodees dans les fichiers touches.
- Mettre a jour `token-namespace-registry.md` ou `typography-roles.md` uniquement si une decision durable est introduite.

Out of scope:
- Migration globale des 113 fichiers de la liste.
- Refonte UX ou changement de layout non necessaire a la tokenisation.
- Migration des styles inline, fallbacks CSS ou selectors legacy sauf si le cluster choisi les exige explicitement et que la story est bloquee pour decision.

Explicit non-goals:
  - Ne pas changer `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer un token semantique opportuniste pour une valeur unique.
  - Ne pas modifier plusieurs clusters dans la meme implementation.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la migration doit selectionner un lot borne et mapper chaque ancienne valeur vers une surface canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu de la surface choisie doit rester equivalent hors differences autorisees par la tokenisation.
  - Les seules differences autorisees sont la substitution de valeurs hardcodees par tokens, roles ou utilitaires.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: plusieurs valeurs proches doivent converger vers un nouveau token semantique sans equivalence existante.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | l'AST guard Vitest est la source runtime-equivalente des valeurs visuelles migrees |
| Baseline Snapshot | yes | les compteurs before/after sont obligatoires |
| Ownership Routing | no | aucun ownership applicatif cross-layer n'est deplace |
| Allowlist Exception | yes | les exceptions design-system eventuelles doivent rester exactes et non implicites |
| Contract Shape | no | aucun contrat type/API n'est modifie |
| Batch Migration | yes | un cluster coherent est migre par batch |
| Reintroduction Guard | yes | les guards design-system doivent empecher le retour non classe des valeurs migrees |
| Persistent Evidence | yes | les inventaires hardcoded before/after doivent etre persistés |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/design-system-guards.test.ts` execute par Vitest.
  - AST guard `frontend/src/tests/theme-tokens.test.ts` execute par Vitest.
- Secondary evidence:
  - inventaire before/after des valeurs hardcodees du cluster choisi.
- Static scans alone are not sufficient for this story because:
  - les valeurs detectees doivent etre reliees aux registres de tokens et roles.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - seul le cluster choisi peut changer; les compteurs des fichiers touches doivent baisser ou etre explicitement classes.

## Ownership Routing Rule

- Ownership routing: not applicable
- Reason: the story keeps design-token ownership in existing style registries and does not move module ownership.

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | selected cluster exception if any | exception exacte | sortie: valeur migree ou classee |
| `frontend/src/styles/token-namespace-registry.md` | token namespace introduced if any | ownership durable des tokens | permanent seulement si un token semantique est cree |
| `frontend/src/styles/typography-roles.md` | typography role introduced if any | ownership durable des roles typo | permanent seulement si un role semantique est cree |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| selected cluster | hardcoded values | tokens, roles or utilities | chosen files | `npm run test -- design-system` | after inventory | no token fits |

## Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| hardcoded baseline | `_condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-before.md` | lister cluster choisi et compteurs initiaux |
| hardcoded result | `_condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-after.md` | prouver la baisse ou classification |
| cluster decision | `_condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/cluster-selection.md` | documenter le cluster unique choisi et les non-goals |

## Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- valeurs exactes migrees dans le cluster choisi.
- nouveau token namespace non classe dans `frontend/src/styles/token-namespace-registry.md`.
- role typographique durable non liste dans `frontend/src/styles/typography-roles.md`.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens visual-smoke` checks migrated visual debt and registries.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-003` - signale une liste large et exige un cluster coherent.
- Evidence 2: `frontend/src/styles/token-namespace-registry.md` - registre des namespaces de tokens.
- Evidence 3: `frontend/src/styles/typography-roles.md` - registre des roles typographiques et exceptions.
- Evidence 4: `frontend/src/tests/visual-smoke.test.tsx` et `frontend/src/tests/design-system-guards.test.ts` - guards frontend design-system.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants `RG-044`, `RG-045`, `RG-046` et `RG-050` consultes avant cadrage.

## Target State

- Un seul cluster est migre et documente.
- Les valeurs hardcodees touchees sont remplacees par tokens, roles ou utilitaires existants, ou bloquees par decision explicite.
- Les registres design-system changent uniquement si la migration cree un invariant durable.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace token nouveau ou touche doit rester classe.
  - `RG-045` - les valeurs migrees ne doivent pas revenir non classees.
  - `RG-046` - les roles typographiques restent la voie canonique pour les repetitions migrees.
  - `RG-050` - les guards design-system restent executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline ne sont pas dans le scope.
  - `RG-048` - les fallbacks CSS ne sont pas dans le scope.
  - `RG-049` - les selectors legacy ne sont pas dans le scope.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens visual-smoke`
  - targeted component/page tests for selected cluster.
- Allowed differences:
  - les compteurs hardcoded du cluster choisi peuvent baisser; les autres clusters ne doivent pas changer.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster choisi est borne. | Evidence profile: `baseline_before_after_diff`; `npm run test -- design-system` + `cluster-selection.md` |
| AC2 | Le baseline liste les valeurs hardcodees du cluster. | Evidence profile: `baseline_before_after_diff`; `npm run test -- design-system` + `hardcoded-values-before.md` |
| AC3 | Les valeurs migrables utilisent les tokens existants. | Evidence profile: `batch_migration_mapping`; diff + `npm run test -- design-system theme-tokens` |
| AC4 | Tout token ou role durable est enregistre dans son registre. | Evidence profile: `allowlist_register_validated`; `npm run test -- theme-tokens design-system` |
| AC5 | Les valeurs migrees ne reviennent pas non classees. | Evidence profile: `reintroduction_guard`; `hardcoded-values-after.md` + `npm run test -- visual-smoke design-system` |

## Implementation Tasks

- [ ] Task 1 - Selectionner un seul cluster et documenter les fichiers inclus/exclus. (AC: AC1)
- [ ] Task 2 - Capturer le baseline hardcoded before pour ce cluster. (AC: AC2)
- [ ] Task 3 - Migrer les valeurs vers tokens, roles ou utilitaires existants avec le plus petit delta. (AC: AC3)
- [ ] Task 4 - Mettre a jour les registres seulement si un token ou role durable est cree ou reclassifie. (AC: AC4)
- [ ] Task 5 - Capturer l'after, comparer les compteurs et executer les validations. (AC: AC5)

## Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` pour les tokens globaux.
  - `frontend/src/styles/utilities.css` et `frontend/src/styles/glass.css` quand les utilitaires existants couvrent le besoin.
  - `frontend/src/styles/token-namespace-registry.md` et `frontend/src/styles/typography-roles.md` pour les decisions durables.
- Do not recreate:
  - un token local pour une valeur deja couverte.
  - une classe utilitaire propre au cluster si une utilite existante suffit.
- Shared abstraction allowed only if:
  - au moins deux fichiers du cluster partagent exactement la meme responsabilite visuelle et aucun token existant ne convient.

## No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- nouveau namespace de token absent de `frontend/src/styles/token-namespace-registry.md`.
- nouveau role typographique durable absent de `frontend/src/styles/typography-roles.md`.
- migration simultanee de plusieurs clusters.
- nouvelle surface legacy, compatibility ou fallback pour contourner les tokens canoniques.

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

- Canonical ownership: not applicable

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/utilities.css`
- `frontend/src/styles/glass.css`
- `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

## Expected Files to Modify

Likely files:

- `frontend/src/App.css` - only if app legacy shell is selected.
- `frontend/src/pages/admin/AdminDashboardPage.css` - only if admin shell is selected.
- `frontend/src/layouts/AdminLayout.css` - only if admin shell is selected.
- `frontend/src/pages/admin/AdminPromptsPage.css` - only if admin prompts is selected and legacy selector migration is not required.
- `frontend/src/components/prediction/DayPredictionCard.css` - only if prediction cards is selected.
- `frontend/src/features/chat/components/ChatWindow.css` - only if chat shell is selected.
- `frontend/src/pages/landing/LandingPage.css` - only if landing is selected.
- `frontend/src/pages/NatalChartPage.css` - only if natal is selected.
- `frontend/src/styles/token-namespace-registry.md` - only if new token ownership is introduced.
- `frontend/src/styles/typography-roles.md` - only if typography roles or exceptions change.
- `frontend/src/tests/design-system-allowlist.ts` - only if guard exceptions change.

Likely tests:

- `frontend/src/tests/visual-smoke.test.tsx` - smoke coverage for selected visual surface.
- `frontend/src/tests/theme-tokens.test.ts` - token coverage.
- `frontend/src/tests/design-system-guards.test.ts` - registry/allowlist guard.
- targeted page/component test for the selected cluster, for example `frontend/src/tests/AdminPage.test.tsx` or `frontend/src/tests/chat/ChatComponents.test.tsx`.

Files not expected to change:

- `backend/` - aucun contrat backend n'est touche.
- files outside the chosen cluster - scope guard.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens visual-smoke
npm run lint
# Run the targeted page/component test for the selected cluster, for example:
# npm run test -- AdminPage
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-066-migrer-cluster-coherent-valeurs-visuelles-hardcodees/00-story.md
```

## Regression Risks

- Risk: migration trop large qui touche plusieurs clusters et rend la validation floue.
  - Guardrail: `cluster-selection.md` et AC1 bornent les fichiers.
- Risk: nouveau token semantique cree sans ownership.
  - Guardrail: `RG-044`, `RG-046` et tests `theme-tokens design-system`.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-003` - source du candidat.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-044`, `RG-045`, `RG-046`, `RG-050`.
- `frontend/src/styles/token-namespace-registry.md` - ownership tokens.
- `frontend/src/styles/typography-roles.md` - roles typographiques.
