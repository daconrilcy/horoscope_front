# Story CS-033 reduire-valeurs-visuelles-typographiques-hardcodees: Reduire les valeurs visuelles et typographiques hardcodees restantes

Status: ready-to-dev

## 1. Objective

Reduire un nouveau lot borne de valeurs CSS hardcodees dans les clusters frontend les plus rentables.
Aucun namespace de tokens non classe ni changement produit attendu n'est autorise.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-002` indique une dette CSS encore large:
  1890 occurrences color-like, 2627 declarations spacing/radius/shadow et
  1533 declarations typographiques hors du premier lot migre.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Selectionner un lot explicite de fichiers CSS frontend a migrer.
  - Remplacer les repetitions par tokens ou roles typographiques deja classes.
  - Capturer les comptes avant/apres uniquement sur les fichiers touches.
  - Mettre a jour les registres existants seulement si un token semantique permanent est necessaire.
- Out of scope:
  - Migration exhaustive de tout `frontend/src`.
  - Refonte visuelle de pages ou composants.
  - Creation d'un nouveau systeme de tokens concurrent.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas migrer les inline styles ou fallbacks CSS; ils ont leurs stories dediees.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de consommateurs CSS vers les surfaces canoniques existantes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les valeurs remplacees doivent etre equivalentes ou documentees comme difference autorisee.
  - Aucune refonte de layout ou de contenu n'est incluse.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: deux valeurs proches ne peuvent pas converger vers un token existant sans decision design explicite.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Aucun runtime, route ou config n'est modifie. |
| Baseline Snapshot | yes | Les comptes hardcoded avant/apres sont obligatoires. |
| Ownership Routing | no | Les owners de tokens existent deja dans les registres frontend. |
| Allowlist Exception | no | Cette story doit reduire la dette sans ajouter d'exception large. |
| Contract Shape | no | Aucun contrat API, DTO ou type frontend n'est modifie. |
| Batch Migration | yes | Le scope est un lot de fichiers CSS explicite. |
| Reintroduction Guard | yes | Les valeurs migrees ne doivent pas revenir dans le lot. |
| Persistent Evidence | yes | Les inventaires avant/apres doivent etre persistants. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: no runtime route, config, generated contract, persistence, or architecture rule is affected.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - Les comptes color/spacing/radius/shadow/typography diminuent dans le lot touche et aucune valeur migree ne revient sans classification.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | Repetitions CSS | Tokens existants | Liste after | Tests design-system | Scan cible | Valeurs non equivalentes |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/hardcoded-values-before.md` | Capturer le lot et les comptes initiaux. |
| After inventory | `_condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/hardcoded-values-after.md` | Prouver la reduction et les differences autorisees. |

## 4i. Reintroduction Guard

- Guard target: valeurs hardcodees migrees dans le lot de fichiers selectionnes.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens` et scans `rg` cibles sur les fichiers migres.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-008` - 1890 occurrences color-like restent hors fichiers token core.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-009` - 2627 declarations spacing/radius/shadow non tokenisees restent visibles.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-010` - 1533 declarations typographiques non tokenisees restent visibles.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un lot CSS explicite a moins de valeurs hardcodees qu'avant implementation.
- Les remplacements reutilisent les tokens et roles existants.
- Toute nouvelle entree de registre est justifiee comme extension semantique durable, pas comme raccourci local.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-045` - les valeurs migrees ne doivent pas revenir dans les fichiers couverts.
  - `RG-046` - la typographie migree passe par les roles semantiques.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - les inline styles sont traites par `CS-034`.
  - `RG-048` - les fallbacks CSS sont traites par `CS-035`.
- Required regression evidence:
  - Inventaires avant/apres, `npm run test -- design-system theme-tokens`, `npm run lint`.
- Allowed differences:
  - Remplacement de literals par tokens equivalentes ou differences explicitement listees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le lot de fichiers migres est liste avant modification. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "frontend/src" hardcoded-values-before.md`. |
| AC2 | Les comptes cibles diminuent dans chaque categorie touchee. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "After|Apres" hardcoded-values-after.md`. |
| AC3 | Les nouveaux tokens eventuels sont classes dans le registre existant. | Evidence profile: `allowlist_register_validated`; `npm run test -- theme-tokens`. |
| AC4 | Les roles typographiques existants sont reutilises pour les valeurs typographiques migrees. | Evidence profile: `ast_architecture_guard`; `npm run test -- design-system`. |
| AC5 | Aucun nouveau namespace non classe n'est introduit. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Choisir et documenter le lot CSS a migrer (AC: AC1)
- [ ] Task 2 - Capturer les scans avant sur ce lot (AC: AC1)
- [ ] Task 3 - Remplacer les repetitions par tokens ou roles existants (AC: AC2, AC4)
- [ ] Task 4 - Mettre a jour les registres uniquement si une extension durable est requise (AC: AC3)
- [ ] Task 5 - Capturer les scans apres et executer les guards frontend (AC: AC2, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` pour les tokens globaux.
  - `frontend/src/styles/token-namespace-registry.md` pour la classification.
  - `frontend/src/styles/typography-roles.md` pour les roles texte.
- Do not recreate:
  - Des variables locales qui dupliquent une token globale.
  - Un registre de tokens parallele.
- Shared abstraction allowed only if:
  - Elle sert au moins deux fichiers du lot et reste dans les feuilles de style appropriees.

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

- nouveau namespace CSS absent de `token-namespace-registry.md`
- `style=` dans les composants touches
- fallback `var(--token, value)` ajoute pour compenser une token manquante

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens globaux frontend | `frontend/src/styles/design-tokens.css` | token local non classe |
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
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/**/*.css` - uniquement le lot selectionne et documente.
- `frontend/src/styles/token-namespace-registry.md` - seulement si une extension semantique durable est ajoutee.
- `frontend/src/styles/typography-roles.md` - seulement si un role existant doit etre clarifie.
- `_condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/hardcoded-values-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - garde hardcoded values.
- `frontend/src/tests/theme-tokens.test.ts` - classification tokens.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/**/*.tsx` - hors scope sauf test composant existant indispensable.

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
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-033-reduire-valeurs-visuelles-typographiques-hardcodees/00-story.md
```

## 22. Regression Risks

- Risk: une valeur proche mais non equivalente est convergee trop vite.
  - Guardrail: decision utilisateur requise si l'equivalence design n'est pas evidente.
- Risk: une variable locale duplique un token global.
  - Guardrail: `RG-044` et `npm run test -- theme-tokens`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Do not use inline styles; all static styling must stay in CSS files.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
