# Story CS-035 reduire-fallbacks-css-allowlistes: Reduire les fallbacks CSS allowlistes

Status: ready-to-dev

## 1. Objective

Reduire un lot de fallbacks CSS `var(--token, value)` encore allowlistes en remplacant les fallbacks migration-only par des tokens canoniques requis ou par des imports documentes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-004` indique que 329 fallbacks CSS restent actifs malgre une garde contre la croissance non classee.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Selectionner un lot explicite de fallbacks CSS allowlistes.
  - Retirer les fallbacks qui masquent des tokens requis disponibles.
  - Mettre a jour `css-fallback-allowlist.md` et `design-system-allowlist.ts`.
  - Valider les composants CSS touches.
- Out of scope:
  - Redefinir la source globale des tokens.
  - Convertir les inline styles.
  - Migrer toutes les valeurs hardcodees CSS.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-048` ou `RG-050`.
  - Ne pas garder un fallback literal local pour un token canonique requis.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne d'exceptions fallback vers les tokens canoniques et registres existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les composants touches doivent continuer a fonctionner avec les imports CSS existants.
  - Les fallbacks dynamiques permanents restent seulement s'ils sont classes.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un composant doit fonctionner sans import global de tokens et qu'aucune politique d'isolation n'est documentee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Aucun runtime route/config n'est modifie. |
| Baseline Snapshot | yes | Le nombre de fallbacks doit etre compare avant/apres. |
| Ownership Routing | no | L'ownership des tokens est deja dans le registre frontend. |
| Allowlist Exception | yes | Les fallbacks restants sont des exceptions exactes. |
| Contract Shape | no | Aucun contrat API ou type public n'est touche. |
| Batch Migration | yes | Le scope est un lot de fallbacks allowlistes. |
| Reintroduction Guard | yes | Les fallbacks non classes ou retires ne doivent pas revenir. |
| Persistent Evidence | yes | Les inventaires et registres mis a jour prouvent le resultat. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: no runtime route, config, generated contract, persistence, or architecture rule is affected.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-after.md`
- Expected invariant:
  - Le nombre de fallbacks du lot diminue et les exceptions restantes ont statut, raison et condition de sortie.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | fallbacks dynamiques ou compatibility | Pont runtime ou isolation documentee. | Expiry explicit. |
| `frontend/src/tests/design-system-allowlist.ts` | `CSS_FALLBACK_EXCEPTIONS` | Miroir executable des exceptions exactes. | Must shrink for migrated fallbacks. |

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
| 1 | Fallbacks du lot | `var(--token)` ou exception | Liste after | Tests CSS fallback | Scan cible | Isolation non tranchee |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-before.md` | Capturer le lot et les fallbacks initiaux. |
| After inventory | `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-after.md` | Prouver les retraits et exceptions finales. |
| Fallback registry | `frontend/src/styles/css-fallback-allowlist.md` | Source documentaire des fallbacks restants. |
| Executable allowlist | `frontend/src/tests/design-system-allowlist.ts` | Source testee des exceptions exactes. |

## 4i. Reintroduction Guard

- Guard target: fallback `var(--token, value)` absent de l'allowlist ou retire par cette story.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-012` - 329 usages de fallbacks CSS restent dans `frontend/src/**/*.css`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1411/02-finding-register.md#F-004` - les fallbacks agissent encore comme dette migration-only ou compatibility.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - le registre documente les exceptions autorisees.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le lot touche contient moins de fallbacks literaux.
- Les fallbacks restants sont explicitement justifies et synchronises entre registre et allowlist executable.
- Les tokens canoniques requis sont consommes sans valeur de secours locale.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - la classification des namespaces determine les tokens requis.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - les inline styles sont traites par `CS-034`.
  - `RG-046` - la typographie n'est pas le domaine principal.
- Required regression evidence:
  - `npm run test -- css-fallback design-system`, scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*,"` sur fichiers migres, `npm run lint`.
- Allowed differences:
  - Retrait de fallbacks pour tokens disponibles; conservation uniquement des exceptions classees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le lot de fallbacks migres est inventorie avant modification. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "var\\(" css-fallbacks-before.md`. |
| AC2 | Les fallbacks de tokens requis du lot sont remplaces. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "var\\(\\s*--" src -g "*.css"`. |
| AC3 | `css-fallback-allowlist.md` est reduit ou clarifie pour le lot. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback`. |
| AC4 | `CSS_FALLBACK_EXCEPTIONS` reste synchronise avec le registre. | Evidence profile: `allowlist_register_validated`; `npm run test -- design-system css-fallback`. |
| AC5 | Aucun fallback non classe n'est introduit. | Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier les fallbacks du lot et leurs statuts (AC: AC1)
- [ ] Task 2 - Retirer les fallbacks de tokens canoniques requis (AC: AC2)
- [ ] Task 3 - Synchroniser registre documentaire et allowlist executable (AC: AC3, AC4)
- [ ] Task 4 - Valider les composants/pages CSS touches (AC: AC5)
- [ ] Task 5 - Executer lint, tests et scans cibles (AC: AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/token-namespace-registry.md`.
  - `frontend/src/styles/css-fallback-allowlist.md`.
  - `frontend/src/tests/css-fallback-policy.test.ts`.
- Do not recreate:
  - Une deuxieme allowlist de fallbacks hors `design-system-allowlist.ts`.
  - Des tokens locaux pour remplacer des fallbacks retires.
- Shared abstraction allowed only if:
  - Elle reste dans les tests design-system existants.

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

- fallback literal pour token canonique requis
- entree `CSS_FALLBACK_EXCEPTIONS` sans ligne correspondante dans `css-fallback-allowlist.md`
- exception par fichier entier

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Fallbacks CSS autorises | `frontend/src/styles/css-fallback-allowlist.md` | fallback literal implicite dans CSS |
| Exceptions executables | `frontend/src/tests/design-system-allowlist.ts` | exception non testee |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/App.css`
- `frontend/src/pages/HelpPage.css`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/css-fallback-allowlist.md` - reduction ou clarification du lot.
- `frontend/src/tests/design-system-allowlist.ts` - synchronisation des exceptions.
- `frontend/src/components/ui/Select/Select.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/UserMenu/UserMenu.css` - candidat prioritaire si selectionne.
- `frontend/src/pages/NatalChartPage.css` - candidat prioritaire si selectionne.
- `frontend/src/App.css` - candidat prioritaire si selectionne.
- `frontend/src/pages/HelpPage.css` - candidat prioritaire si selectionne.
- `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - garde principale.
- `frontend/src/tests/design-system-guards.test.ts` - synchronisation allowlist.
- Tests composants touches quand disponibles, par exemple `Select.test.tsx` ou `UserMenu.test.tsx`.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/**/*.tsx` - hors scope sauf test composant.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- css-fallback design-system
rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/00-story.md
```

## 22. Regression Risks

- Risk: un composant isole perd un fallback necessaire en test ou storybook local.
  - Guardrail: blocker utilisateur si la politique d'import global manque.
- Risk: le registre documentaire et l'allowlist executable divergent.
  - Guardrail: `npm run test -- css-fallback design-system`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Do not add fallback literals to solve missing token imports silently.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
