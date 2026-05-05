# Story CS-037 reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres: Reduire la dette de valeurs visuelles hardcodees hors lots deja migres

Status: done

## 1. Objective

Reduire un nouveau lot borne de valeurs visuelles et typographiques hardcodees dans `frontend/src`.
Le rendu produit doit rester equivalent hors differences documentees.
La story doit prouver une reduction mesurable et bloquer toute reintroduction des literals migres.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1501/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-002` indique 1899 occurrences color-like et 4172 declarations visuelles ou typographiques encore presentes hors lots deja migres.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Selectionner un lot explicite de fichiers CSS/TSX a plus forte repetition hors lots deja migres.
  - Remplacer les literals repetes par tokens, variables ou roles typographiques deja classes.
  - Capturer les comptes avant/apres sur le lot touche.
  - Mettre a jour les registres uniquement si une extension semantique durable est introduite.
- Out of scope:
  - Migration exhaustive de tout `frontend/src`.
  - Conversion des styles inline statiques de `TurningPointsList.tsx`.
  - Reduction des fallbacks CSS `var(--token, value)`.
  - Refonte visuelle, changement de contenu ou redesign.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de namespace token non classe.
  - Ne pas ajouter de style inline ou de fallback CSS pour compenser une token manquante.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de consommateurs visuels vers les surfaces design-system canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les valeurs remplacees doivent etre equivalentes ou listees comme differences autorisees dans l'artefact apres.
  - Aucun changement de structure DOM, contenu, navigation ou logique React n'est autorise sauf besoin de classe CSS.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: deux valeurs proches ne peuvent pas converger vers un token existant sans decision design explicite.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system sont la source observable des regles statiques. |
| Baseline Snapshot | yes | Les comptes hardcoded avant/apres sont obligatoires pour prouver la reduction. |
| Ownership Routing | no | Aucun deplacement de responsabilite; les owners de tokens existent deja. |
| Allowlist Exception | yes | Les registres existants doivent rester exacts si une valeur est conservee hors migration. |
| Contract Shape | no | Aucun contrat API, DTO, payload, type ou schema n'est modifie. |
| Batch Migration | yes | Le scope est un lot de fichiers explicite. |
| Reintroduction Guard | yes | Les literals migres ne doivent pas revenir dans le lot. |
| Persistent Evidence | yes | Les inventaires avant/apres doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts`.
  - Token namespace guard: `frontend/src/tests/theme-tokens.test.ts`.
- Secondary evidence:
  - Scans `rg` cibles sur les fichiers du lot.
- Static scans alone are not sufficient for this story because:
  - Les guards Vitest raccordent les registres design-system aux fichiers reels.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-037-reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-037-reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres/hardcoded-values-after.md`
- Expected invariant:
  - Les comptes color/spacing/radius/shadow/typography diminuent dans le lot touche et aucune valeur migree ne revient sans classification.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `token-namespace-registry.md` | namespace token eventuel | Classification obligatoire si extension durable. | Permanent if canonical or semantic-extension. |
| `typography-roles.md` | role typographique eventuel | Classification obligatoire si role durable. | Permanent if reused by migrated surfaces. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | Literals du lot | Tokens et roles existants | Liste dans `hardcoded-values-after.md` | `npm run test -- design-system theme-tokens` | Scans cibles | Equivalence incertaine |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `hardcoded-values-before.md` | Capturer le lot, les comptes initiaux et les valeurs candidates. |
| After inventory | `hardcoded-values-after.md` | Prouver la reduction, les remplacements et les differences autorisees. |

## 4i. Reintroduction Guard

- Guard target: valeurs hardcodees migrees dans le lot de fichiers selectionnes.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens` et scans `rg` cibles sur les fichiers migres.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-013` - 1899 occurrences color-like restent hors fichiers token core.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-014` - 4172 declarations visuelles ou typographiques restent visibles dans les CSS.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-015` -
  les literals exacts deja migres par `CS-027` ne sont pas reintroduits dans le lot controle.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un lot explicite contient moins de valeurs hardcodees qu'avant implementation.
- Les valeurs remplacees reutilisent les tokens, variables ou roles existants.
- Les registres frontend restent la source de classification des namespaces et roles.
- Les preuves avant/apres rendent impossible une validation partielle ou subjective.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace de token CSS frontend doit rester classe.
  - `RG-045` - les valeurs exactes migrees ne doivent pas revenir dans les fichiers couverts.
  - `RG-046` - les roles typographiques semantiques sont canoniques pour les surfaces migrees.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline sont traites par `CS-038`.
  - `RG-048` - les fallbacks CSS sont traites par `CS-039`.
  - `RG-049` - aucun selecteur legacy n'est cree ou migre par cette story.
- Required regression evidence:
  - Inventaires avant/apres, `npm run test -- design-system theme-tokens`, `npm run lint`, scans `rg` cibles sur le lot.
- Allowed differences:
  - Remplacement de literals par tokens equivalentes ou differences explicitement listees dans `hardcoded-values-after.md`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le lot migre est liste avant modification. | Evidence profile: `baseline_before_after_diff`; `rg -n "frontend/src" hardcoded-values-before.md`. |
| AC2 | Les comptes cibles diminuent dans chaque categorie touchee. | Evidence profile: `baseline_before_after_diff`; `rg -n "delta" hardcoded-values-after.md`. |
| AC3 | Tout nouveau token ou role eventuel est classe dans le registre existant. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- theme-tokens`. |
| AC4 | Les roles typographiques existants sont reutilises pour les repetitions migrees. | Evidence profile: `ast_architecture_guard`; `npm run test -- design-system`. |
| AC5 | Aucun namespace non classe n'est ajoute au lot. | Evidence profile: `reintroduction_guard`; command: `npm run test -- theme-tokens`. |
| AC6 | Aucun style inline ou fallback literal n'est ajoute au lot. | Evidence profile: `reintroduction_guard`; command: `npm run test -- inline-style css-fallback`. |
| AC7 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; command: `npm run lint`. |

## 8. Implementation Tasks

- [x] Task 1 - Choisir et documenter le lot CSS/TSX a migrer (AC: AC1)
- [x] Task 2 - Capturer les scans avant sur ce lot (AC: AC1, AC2)
- [x] Task 3 - Remplacer les repetitions par tokens, variables ou roles existants (AC: AC2, AC4)
- [x] Task 4 - Mettre a jour les registres seulement si une extension durable est requise (AC: AC3, AC5)
- [x] Task 5 - Capturer les scans apres, les deltas et les differences autorisees (AC: AC2, AC5, AC6)
- [x] Task 6 - Executer lint et guards frontend (AC: AC3, AC4, AC5, AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` pour les tokens globaux.
  - `frontend/src/styles/token-namespace-registry.md` pour la classification des namespaces.
  - `frontend/src/styles/typography-roles.md` pour les roles texte.
  - `frontend/src/tests/design-system-guards.test.ts` et `frontend/src/tests/theme-tokens.test.ts` pour les guards.
- Do not recreate:
  - Variables locales qui dupliquent une token globale.
  - Registre de tokens parallele.
  - Style inline ou fallback CSS pour contourner une token manquante.
- Shared abstraction allowed only if:
  - Elle sert au moins deux declarations du lot et reste dans la feuille de style appropriee.

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

- nouveau namespace CSS absent de `frontend/src/styles/token-namespace-registry.md`
- `style=` ajoute dans les fichiers touches
- nouveau fallback `var(--token, value)` dans les fichiers touches
- conservation d'un literal migre sans justification dans `hardcoded-values-after.md`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens globaux frontend | `frontend/src/styles/design-tokens.css` | token local non classe |
| Classification namespace | `frontend/src/styles/token-namespace-registry.md` | namespace implicite dans CSS |
| Roles typographiques | `frontend/src/styles/typography-roles.md` | valeur typographique repetee |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/**/*.css` - uniquement le lot selectionne et documente.
- `frontend/src/styles/token-namespace-registry.md` - seulement si une extension semantique durable est ajoutee.
- `frontend/src/styles/typography-roles.md` - seulement si un role existant doit etre clarifie.
- `_condamad/stories/CS-037-reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-037-reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres/hardcoded-values-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - garde design-system principale.
- `frontend/src/tests/theme-tokens.test.ts` - classification tokens.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/components/prediction/TurningPointsList.tsx` - couvert par `CS-038`, sauf si le lot choisi exclut les inline styles et ne touche que CSS adjacent.
- `frontend/src/styles/css-fallback-allowlist.md` - couvert par `CS-039`.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- design-system theme-tokens
npm run test -- inline-style css-fallback
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-037-reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict `
  _condamad/stories/CS-037-reduire-dette-valeurs-visuelles-hardcodees-hors-lots-migres/00-story.md
```

## 22. Regression Risks

- Risk: une valeur proche mais non equivalente est convergee trop vite.
  - Guardrail: decision utilisateur requise si l'equivalence design n'est pas evidente.
- Risk: une variable locale duplique un token global.
  - Guardrail: `RG-044` et `npm run test -- theme-tokens`.
- Risk: la reduction hardcoded derive vers inline style ou fallback CSS.
  - Guardrail: `RG-047`, `RG-048` et validations `inline-style css-fallback`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Respect the project style rule: no inline style for static styling.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1501/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1501/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
