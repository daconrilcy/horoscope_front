# Story CS-069 migrer-cluster-admin-settings-valeurs-visuelles-hardcodees: Migrer le cluster admin settings de valeurs visuelles hardcodees

Status: done

## Objective

Migrer un cluster coherent de valeurs visuelles hardcodees autour des surfaces admin settings et entitlements.
Le cluster doit avoir 100% de decisions finales dans les artefacts before/after.
Aucune AC ne peut rester en PASS with limitation.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-002`
- Reason for change: des literals CSS concurrencent les tokens semantiques.

## Domain Boundary

- Domain: `frontend/src/pages/admin`
- In scope:
  - Traiter uniquement le cluster admin settings defini dans les fichiers CSS admin listes par cette story.
  - Capturer les valeurs hardcodees before/after avec mapping vers owner canonique.
  - Utiliser les tokens/roles existants; mettre a jour `token-namespace-registry.md` ou `typography-roles.md` seulement si une extension durable et non legacy est necessaire.
- Out of scope:
  - Traiter tous les fichiers de `E-011`.
  - Toucher les routes, API, i18n ou logique React admin.
  - Traiter le vocabulaire admin prompts `legacy`, couvert par `CS-070`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de token pour une valeur unique.
  - Ne pas conserver une valeur migree sous forme de literal parallele.

## Regression Guardrails

- Applicable invariants:
  - `RG-044` - new or reused token namespaces must stay classified.
  - `RG-045` - migrated visual values must not return in the cluster.
  - `RG-046` - typography repetitions must use documented roles.
  - `RG-050` - design-system guards must stay executable.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: the story migrates a bounded batch of repeated admin CSS literals to canonical tokens and documented semantic owners.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Visual output may change only where the canonical token represents the same design role.
  - Admin settings and entitlements interaction behavior, layout intent and React logic must remain unchanged.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a hardcoded value has no reusable owner and cannot be kept with a final classification.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards et tests admin prouvent l'etat executable. |
| Baseline Snapshot | yes | Les artefacts before/after bornent le cluster. |
| Ownership Routing | no | Le routage d'ownership global n'est pas l'archetype primaire; les owners sont documentes dans le plan batch. |
| Allowlist Exception | no | Aucune exception large ou temporaire n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO ou serialization n'est modifie. |
| Batch Migration | yes | Le cluster admin est migre par lots de valeurs vers des owners canoniques. |
| Reintroduction Guard | yes | Les valeurs migrees ne doivent pas revenir non classees. |
| Persistent Evidence | yes | Les artefacts before/after et les resultats doivent rester consultables. |

## Runtime Source of Truth

- Primary source of truth: AST guard and CSS guard tests in `frontend/src/tests/design-system-guards.test.ts` and `frontend/src/tests/theme-tokens.test.ts`.
- Secondary evidence: focused admin component tests for `AdminSettingsPage`, `AdminEntitlementsPage`, `AdminUserDetailPage`, and `PersonasAdmin`.
- Static scans alone are not sufficient: executable evidence is required through
  `npm run test -- design-system theme-tokens visual-smoke AdminSettingsPage`.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-069-migrer-cluster-admin-settings-valeurs-visuelles-hardcodees/hardcoded-values-before.md`.
- Comparison after implementation: `_condamad/stories/CS-069-migrer-cluster-admin-settings-valeurs-visuelles-hardcodees/hardcoded-values-after.md`.
- Expected invariant: every cluster value has a final decision of migrated, registered semantic owner, or explicitly kept-classified with no TODO.

## Ownership Routing Rule

- Ownership Routing Rule: not applicable
- Reason: ownership is captured in the batch migration plan and no routing-boundary refactor is required.

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: the story does not authorize exceptions or allowlists for migrated hardcoded values.

## Contract Shape

- Contract Shape: not applicable
- Reason: no generated API, DTO, HTTP status, serialization name, or frontend data contract is changed.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Settings colors | literals in `AdminSettingsPage.css` | tokens or semantic variables | settings CSS | admin tests | color scans | missing owner |
| Entitlements values | literals in `AdminEntitlementsPage.css` | tokens or semantic variables | entitlements CSS | admin tests | scans | one-off value |
| Typography/shape | repeated font, radius or shadow | typography roles or tokens | admin CSS | visual-smoke tests | zero TODO | one-use token |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before hardcoded-value baseline | `hardcoded-values-before.md` | Bound the admin settings cluster and initial literal decisions. |
| After hardcoded-value evidence | `hardcoded-values-after.md` | Persist final decisions and reintroduction scans. |
| Final validation evidence | `generated/10-final-evidence.md` | Persist commands, results and residual risks. |

## Reintroduction Guard

- Architecture guard: migrated admin CSS literals must fail if reintroduced without classification.
- Deterministic source: forbidden symbols include migrated hardcoded values recorded in `hardcoded-values-after.md`.
- Evidence profile: `reintroduction_guard`; command `npm run test -- design-system theme-tokens`.
- Additional executable evidence: targeted `rg` scans for color, typography, shadow and radius literals in the Validation Plan.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-002` - audit source for the admin settings hardcoded-value cluster.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - shared design-system guardrails for tokens, typography and guards.

## Target State

- Le cluster admin settings/entitlements utilise des tokens existants ou des variables locales semantiques.
- Chaque literal restant est classifie dans l'artefact after.
- Les guards design-system et tests admin restent executables et verts.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The cluster is bounded. | Evidence profile: `baseline_snapshot`; baseline artifact plus `npm run test -- design-system`. |
| AC2 | 100% of values have a final decision. | Evidence profile: `persistent_evidence`; `rg -n "TODO" hardcoded-values-after.md` returns zero hits. |
| AC3 | Clear mappings use canonical owners. | Evidence profile: `batch_migration`; run typography `rg` scan in the Validation Plan. |
| AC4 | Durable new owners are registered. | Evidence profile: `registry_guard`; `npm run test -- theme-tokens design-system`. |
| AC5 | Focused frontend quality remains green. | Evidence profile: `runtime_guard`; `npm run test -- AdminSettingsPage` and `npm run lint`. |
| AC6 | Migrated literals cannot silently return. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens` plus exact migrated-value scans. |

## Implementation Tasks

- [ ] Task 1 - Capture before artifact for the selected admin settings cluster. (AC: AC1, AC2)
- [ ] Task 2 - Classify every literal as `migrate`, `keep-classified`, or `needs-user-decision`. (AC: AC2)
- [ ] Task 3 - Replace clear duplicates with existing tokens, roles, or documented local variables. (AC: AC3)
- [ ] Task 4 - Update token/typography registries only for durable reusable owners. (AC: AC4)
- [ ] Task 5 - Capture after artifact and add exact reintroduction evidence. (AC: AC2, AC6)
- [ ] Task 6 - Run focused tests, design guards and lint. (AC: AC4, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse existing design tokens and typography roles.
- Do not create a global token for a one-off value.
- Do not duplicate migrated literals as parallel CSS values.

## No Legacy / Forbidden Paths

- Forbidden: new compatibility or migration-only token namespace.
- Forbidden: legacy wrapper, fallback token, or migrated literal kept in parallel without classification.
- Forbidden: unregistered semantic owner when a value becomes reusable.

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin visual values | existing design tokens, typography roles, or registered local semantic variables | raw literals without final classification |
| Cluster evidence | `hardcoded-values-before.md` and `hardcoded-values-after.md` | undocumented ad hoc comments |

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-0806/01-evidence-log.md`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `frontend/src/pages/admin/PersonasAdmin.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/styles/token-namespace-registry.md`

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

Files not expected to change:
- `backend/app/main.py`
- `frontend/package.json`

## Dependency Policy

- New dependencies: none.
- Justification: no dependency change is required.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens visual-smoke AdminSettingsPage AdminEntitlementsPage AdminUserDetailPage PersonasAdmin
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}" src/pages/admin/AdminSettingsPage.css src/pages/admin/AdminEntitlementsPage.css
rg -n "font-size:|font-weight:|line-height:" src/pages/admin/AdminSettingsPage.css
rg -n "box-shadow:|border-radius:" src/pages/admin/AdminSettingsPage.css
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-069-migrer-cluster-admin-settings-valeurs-visuelles-hardcodees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not preserve duplicate literals for convenience.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Cluster trop large et incomplet.
- Visual drift from near-equivalent values.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-002`
- `_condamad/stories/regression-guardrails.md`
