# Story CS-039 reduire-fallbacks-css-composants-ui-partages: Reduire les fallbacks var(--token, value) des composants UI partages

Status: done

## 1. Objective

Reduire un lot de fallbacks CSS `var(--token, value)` dans les composants UI partages.
Les literals de secours doivent disparaitre quand ils masquent des tokens requis.
La story doit synchroniser le registre documentaire et l'allowlist executable.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1501/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-004` indique 262 fallbacks CSS restants.
  Ils sont notamment presents dans `Select`, `Modal`, `Card`, `Field`, `Button`,
  `UserAvatar`, `LockedSection`, `EmptyState` et `Skeleton`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components/ui`
- In scope:
  - Selectionner un lot explicite de fallbacks CSS dans les composants UI partages.
  - Remplacer les fallbacks migration-only par `var(--token)` quand le token requis est canonique.
  - Conserver uniquement les exceptions dynamiques, compatibility ou semantic-extension exactes avec condition de sortie.
  - Mettre a jour `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts`.
  - Valider les guards CSS fallback et les tests des primitives touchees quand ils existent.
- Out of scope:
  - Reduction des fallbacks page-level dans `HelpPage.css` ou `App.css`.
  - Conversion des styles inline.
  - Migration generale des valeurs hardcodees.
  - Changement d'API React des composants UI.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-044`, `RG-048` ou `RG-050`.
  - Ne pas ajouter de fallback literal local pour rendre un test isole vert.
  - Ne pas creer une allowlist parallele ou une exception par dossier.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne d'exceptions fallback vers les tokens canoniques et registres existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les composants touches doivent continuer a fonctionner avec les imports CSS existants.
  - Les fallbacks permanents ne restent que s'ils sont dynamiques ou explicitement classes.
  - Aucune API de composant, prop publique ou structure DOM significative ne doit changer.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un composant doit etre supporte sans import global de tokens et qu'aucune politique d'isolation n'est documentee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest CSS fallback sont la source observable des regles statiques. |
| Baseline Snapshot | yes | Le nombre de fallbacks du lot doit etre compare avant/apres. |
| Ownership Routing | no | L'ownership des tokens et fallbacks reste dans les registres frontend existants. |
| Allowlist Exception | yes | Les fallbacks restants sont des exceptions exactes. |
| Contract Shape | no | Aucun contrat API, DTO, payload, type ou schema n'est modifie. |
| Batch Migration | yes | Le scope est un lot de fallbacks dans composants UI partages. |
| Reintroduction Guard | yes | Les fallbacks non classes ou retires ne doivent pas revenir. |
| Persistent Evidence | yes | Les inventaires et registres mis a jour prouvent le resultat. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/css-fallback-policy.test.ts`.
  - Executable design-system guard: `frontend/src/tests/design-system-guards.test.ts`.
- Secondary evidence:
  - `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src/components/ui -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Les guards Vitest verifient que chaque fallback restant est present dans l'allowlist exacte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/css-fallbacks-after.md`
- Expected invariant:
  - Le nombre de fallbacks du lot diminue et les exceptions restantes ont statut, raison et condition de sortie exacts.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `css-fallback-allowlist.md` | fallbacks UI restants | Exception exacte. | Exit condition required. |
| `frontend/src/tests/design-system-allowlist.ts` | `CSS_FALLBACK_EXCEPTIONS` | Miroir executable des exceptions exactes. | Must shrink or match documented retained exceptions. |

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
| UI shared fallback batch | selected fallback | `var(--token)` or exception | selected UI CSS | targeted Vitest | `rg` and allowlist diff | token isolation missing |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/css-fallbacks-before.md` | Capturer le lot UI et les fallbacks initiaux. |
| After inventory | `_condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/css-fallbacks-after.md` | Prouver les retraits, les exceptions finales et les deltas. |
| Fallback registry | `frontend/src/styles/css-fallback-allowlist.md` | Source documentaire des fallbacks restants. |
| Executable allowlist | `frontend/src/tests/design-system-allowlist.ts` | Source testee des exceptions exactes. |

## 4i. Reintroduction Guard

- Guard target: fallback `var(--token, value)` absent de l'allowlist ou retire par cette story.
- Architecture guard required: `frontend/src/tests/css-fallback-policy.test.ts` must fail when a CSS fallback is not registered exactly.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system` and targeted UI CSS `rg`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-011` - 262 fallbacks CSS restent dans `frontend/src/**/*.css`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-012` -
  des fallbacks restent dans plusieurs composants UI partages cites par l'audit.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - le registre documente les exceptions autorisees et leurs conditions de sortie.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - `CSS_FALLBACK_EXCEPTIONS` est l'allowlist executable verifiee par Vitest.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les composants UI touches contiennent moins de fallbacks literaux.
- Les fallbacks restants sont exacts, justifies, synchronises entre registre et allowlist executable.
- Les tokens canoniques requis sont consommes sans valeur de secours locale.
- Les tests prouvent qu'aucun fallback non classe n'a ete ajoute.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-045` - les hardcoded values non fallback sont traitees par `CS-037`.
  - `RG-046` - la typographie n'est pas le domaine principal.
  - `RG-047` - les inline styles sont traites par `CS-038`.
  - `RG-049` - aucun selecteur legacy n'est cree par cette story.
- Required regression evidence:
  - `npm run test -- css-fallback design-system`, scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src/components/ui -g "*.css"`, `npm run lint`.
- Allowed differences:
  - Retrait de fallbacks pour tokens disponibles; conservation uniquement des exceptions classees dans les registres.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le lot UI est inventorie avant modification. | Evidence profile: `baseline_before_after_diff`; `rg -n "components/ui" css-fallbacks-before.md`. |
| AC2 | Les fallbacks requis deviennent `var(--token)` ou bloquent sur decision. | Evidence profile: `targeted_forbidden_symbol_scan`; targeted UI `rg`. |
| AC3 | `css-fallback-allowlist.md` est reduit ou clarifie pour chaque fallback touche. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback`. |
| AC4 | `CSS_FALLBACK_EXCEPTIONS` reste synchronise avec le registre. | Evidence profile: `allowlist_register_validated`; `npm run test -- design-system css-fallback`. |
| AC5 | Les primitives UI touchees ont une preuve testee. | Evidence profile: `frontend_typecheck_no_orphan`; command: `npm run test -- Button Select UserAvatar`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; command: `npm run lint`. |

## 8. Implementation Tasks

- [x] Task 1 - Inventorier les fallbacks UI du lot et leurs statuts (AC: AC1)
- [x] Task 2 - Retirer les fallbacks de tokens canoniques requis ou bloquer sur decision documentee (AC: AC2)
- [x] Task 3 - Synchroniser `css-fallback-allowlist.md` et `CSS_FALLBACK_EXCEPTIONS` (AC: AC3, AC4)
- [x] Task 4 - Executer ou documenter les tests composants touches (AC: AC5)
- [x] Task 5 - Capturer l'inventaire apres et les scans cibles (AC: AC2, AC3, AC4)
- [x] Task 6 - Executer lint et guards frontend (AC: AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/token-namespace-registry.md` pour decider si un token est requis.
  - `frontend/src/styles/css-fallback-allowlist.md` pour les exceptions documentaires.
  - `frontend/src/tests/design-system-allowlist.ts` pour les exceptions executables.
  - `frontend/src/tests/css-fallback-policy.test.ts` et `frontend/src/tests/design-system-guards.test.ts`.
- Do not recreate:
  - Une deuxieme allowlist de fallbacks.
  - Des tokens locaux pour remplacer des fallbacks retires.
  - Un import CSS opportuniste qui masque une absence de decision.
- Shared abstraction allowed only if:
  - Elle reste dans les tests design-system existants ou dans un composant UI deja proprietaire du style.

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
- exception par dossier entier `frontend/src/components/ui`
- nouveau fallback dans un fichier UI touche sans statut et exit condition

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Fallbacks CSS autorises | `frontend/src/styles/css-fallback-allowlist.md` | fallback literal implicite dans CSS |
| Exceptions executables | `frontend/src/tests/design-system-allowlist.ts` | exception non testee |
| Classification tokens | `frontend/src/styles/token-namespace-registry.md` | token suppose requis sans registre |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/css-fallback-allowlist.md` - reduction ou clarification du lot.
- `frontend/src/tests/design-system-allowlist.ts` - synchronisation des exceptions.
- `frontend/src/components/ui/Button/Button.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/Card/Card.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/Field/Field.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/Modal/Modal.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/Select/Select.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/UserAvatar/UserAvatar.css` - candidat prioritaire si selectionne.
- `frontend/src/components/ui/Skeleton/Skeleton.css` - candidat prioritaire si selectionne.
- `_condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/css-fallbacks-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - garde principale.
- `frontend/src/tests/design-system-guards.test.ts` - synchronisation allowlist.
- Tests composants touches quand disponibles, par exemple `Button.test.tsx`, `Select.test.tsx`, `UserAvatar.test.tsx` ou equivalents existants.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/**/*.tsx` - hors scope sauf tests composants.
- `frontend/src/App.css` - page-level hors lot.
- `frontend/src/pages/HelpPage.css` - page-level hors lot.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- css-fallback design-system
npm run test -- Button Card Field Modal Select UserAvatar Skeleton
rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src/components/ui -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-039-reduire-fallbacks-css-composants-ui-partages/00-story.md
```

## 22. Regression Risks

- Risk: un composant isole perd un fallback encore necessaire.
  - Guardrail: blocker utilisateur si la politique d'import global manque.
- Risk: le registre documentaire et l'allowlist executable divergent.
  - Guardrail: `npm run test -- css-fallback design-system`.
- Risk: un fallback retire revient dans un autre composant UI du meme lot.
  - Guardrail: scan cible `frontend/src/components/ui` et `RG-048`.

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

- `_condamad/audits/frontend-design-system/2026-05-05-1501/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1501/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
