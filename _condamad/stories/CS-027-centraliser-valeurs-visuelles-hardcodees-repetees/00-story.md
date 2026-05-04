# Story CS-027 centraliser-valeurs-visuelles-hardcodees-repetees: Centraliser les valeurs visuelles hardcodees repetees

Status: ready-to-dev

## 1. Objective

Convertir les valeurs visuelles repetees les plus risquees en tokens semantiques, puis migrer un premier lot de fichiers CSS partages ou volumineux sans changer le rendu attendu.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-002` montre que les couleurs, surfaces glass, bordures, espacements, rayons et ombres repetes dupliquent les responsabilites des tokens.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Inventorier les valeurs repetees exactes issues de l'audit.
  - Ajouter des tokens semantiques pour surfaces, borders, elevation, status, spacing et radius.
  - Migrer un premier lot limite a `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css` et `AstrologerProfilePage.css`.
  - Capturer les comptes avant/apres des valeurs migrees.
- Out of scope:
  - Refondre toute la palette visuelle.
  - Migrer toute la typographie, traitee par `CS-028`.
  - Changer les composants React hors ajustement de classes existantes.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas fusionner des valeurs proches mais non identiques sans decision explicite.
  - Ne pas introduire de style inline.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un premier lot de valeurs CSS repetees vers des tokens semantiques avec preuve avant/apres.
- Behavior change allowed: no
- Behavior change constraints:
  - Les valeurs remplacees doivent etre exactes ou explicitement approuvees.
  - Le rendu des pages migrees doit rester equivalent.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une valeur candidate est seulement approximative et implique une normalisation de design.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | La preuve primaire est statique et CSS. |
| Baseline Snapshot | yes | Les comptes de valeurs hardcodees doivent etre compares avant/apres. |
| Ownership Routing | no | `CS-026` etablit l'ownership des namespaces de tokens. |
| Allowlist Exception | no | Les exceptions appartiennent au registre de migration du lot. |
| Contract Shape | no | Aucun contrat API ou type frontend n'est change. |
| Batch Migration | yes | La migration est limitee a un lot de fichiers priorises. |
| Reintroduction Guard | yes | Une garde doit bloquer la croissance des valeurs migrees. |
| Persistent Evidence | yes | Le registre de migration et les comptes avant/apres doivent persister. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: aucun inventaire runtime n'est requis pour remplacer des declarations CSS statiques.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-027-centraliser-valeurs-visuelles-hardcodees-repetees/hardcoded-values-before.md`
- Comparison after implementation: `_condamad/stories/CS-027-centraliser-valeurs-visuelles-hardcodees-repetees/hardcoded-values-after.md`
- Expected invariant: les valeurs exactes migrees diminuent dans les fichiers du lot et n'augmentent pas ailleurs.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: l'ownership des tokens est porte par `CS-026`; cette story consomme ce contrat sans le redefinir.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: les exceptions sont documentees dans le plan de lot avec une cible exacte et une condition de sortie.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | repeated glass rgba values | semantic surface tokens | CSS declarations in batch files | design-system static test | exact count decreases | approximate alpha decision |
| 2 | pill radius and gaps | radius and spacing tokens | batch CSS | design-system test | literals absent | local layout conflict |
| 3 | repeated status and focus colors | semantic status tokens | CSS declarations in batch files | visual smoke test | no local duplicate token | inaccessible contrast result |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Migration inventory | `hardcoded-value-migration.md` | Lister les valeurs migrees et les valeurs bloquees. |
| Before counts | `hardcoded-values-before.md` | Capturer les occurrences initiales. |
| After counts | `hardcoded-values-after.md` | Capturer les occurrences finales. |

## 4i. Reintroduction Guard

- Guard target: valeurs hardcodees migrees dans le lot CSS.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-003` - 1696 occurrences de couleurs hors fichiers tokens.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-004` - 2823 declarations non tokenisees de spacing, margin, padding, border et radius.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-008` - repetitions exactes comme `border-radius: 999px`, `gap: 12px` et `gap: 8px`.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les valeurs repetees exactes du premier lot sont remplacees par des tokens semantiques.
- Les valeurs approximatives restent documentees avec decision requise.
- Le nombre d'occurrences des valeurs migrees diminue dans l'artefact apres.
- Une garde statique detecte la reintroduction des literals migres.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - la classification des tokens frontend doit etre consultee avant ajout de tokens.
  - `RG-045` - les valeurs hardcodees migrees ne doivent pas revenir.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - surfaces backend et documentation hors scope.
- Required regression evidence:
  - Comptes avant/apres, test statique design-system, `npm run lint`.
- Allowed differences:
  - Remplacement exact des valeurs du lot par tokens semantiques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Un inventaire des valeurs repetees exactes du lot existe. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- design-system`. |
| AC2 | Les tokens semantiques ajoutes correspondent a des usages nommes. | `frontend/src/styles/design-tokens.css`; command: `npm run test -- design-system`. |
| AC3 | Les fichiers du lot consomment les tokens au lieu des literals migres. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `npm run test -- design-system`. |
| AC4 | Les valeurs approximatives restent hors migration sans decision. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- design-system`. |
| AC5 | La reintroduction des literals migres est gardee. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline des valeurs repetees du premier lot (AC: AC1)
- [ ] Task 2 - Ajouter les tokens semantiques strictement necessaires (AC: AC2)
- [ ] Task 3 - Migrer les declarations exactes dans les fichiers du lot (AC: AC3)
- [ ] Task 4 - Documenter les valeurs approximatives bloquees (AC: AC4)
- [ ] Task 5 - Ajouter ou etendre la garde statique et capturer l'etat final (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` et le registre de `CS-026`.
  - Les tests Vitest existants sous `frontend/src/tests`.
- Do not recreate:
  - Des tokens synonymes pour une meme intention.
  - Des variables locales pour remplacer des tokens globaux existants.
- Shared abstraction allowed only if:
  - Elle valide les literals CSS sans devenir un outil de build runtime.

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

- nouveau token semantique sans intention nommee
- valeur migree conservee dans un fichier du lot
- fallback CSS ajoute pour simuler un token manquant

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens semantiques de valeurs repetees | `frontend/src/styles/design-tokens.css` | variables locales de page |
| Preuve de migration | dossier `CS-027` | compte ad hoc non persiste |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/App.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/design-tokens.css` - tokens semantiques.
- `frontend/src/App.css` - migration du lot.
- `frontend/src/pages/admin/AdminPromptsPage.css` - migration du lot.
- `frontend/src/pages/HelpPage.css` - migration du lot.
- `frontend/src/pages/settings/Settings.css` - migration du lot.
- `frontend/src/pages/AstrologerProfilePage.css` - migration du lot.
- `frontend/src/tests/theme-tokens.test.ts` - garde statique.

Likely tests:

- `frontend/src/tests/theme-tokens.test.ts` - garde design-system.
- `frontend/src/tests/visual-smoke.test.tsx` - smoke visuel cible.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- theme-tokens
npm run test -- visual-smoke
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-027-centraliser-valeurs-visuelles-hardcodees-repetees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-027-centraliser-valeurs-visuelles-hardcodees-repetees/00-story.md
```

## 22. Regression Risks

- Risk: un token semantique devient un doublon d'un token existant.
  - Guardrail: registre de tokens et revue des noms avant ajout.
- Risk: une normalisation approximative change le rendu.
  - Guardrail: valeurs exactes uniquement sans decision utilisateur.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Keep all styling in CSS files and reuse existing variables before adding tokens.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
