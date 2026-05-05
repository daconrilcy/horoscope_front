# Story CS-036 stabiliser-isolation-suite-vitest-help-page: Stabiliser l'isolation de la suite Vitest HelpPage

Status: ready-to-dev

## 1. Objective

Rendre la suite Vitest frontend assez deterministe pour que `npm run test` reste un signal fiable.
La defaillance full-suite-only de `HelpPage.test.tsx` ne doit plus masquer les guards design-system.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-004`
- Reason for change: le finding `F-005` indique un echec full-suite dans `HelpPage.test.tsx`.
  L'execution isolee `npm run test -- HelpPage` a passe immediatement apres.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/tests`
- In scope:
  - Reproduire ou encadrer la defaillance full-suite-only de `HelpPage.test.tsx`.
  - Auditer mocks, caches, timers, router state et nettoyage DOM affectant `HelpPage`.
  - Corriger la source d'isolation avec le plus petit delta.
  - Ajouter une validation repetable.
- Out of scope:
  - Refonte de `HelpPage`.
  - Migration design-system CSS.
  - Changement de runner de test ou ajout de dependance.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-050`.
  - Ne pas masquer le test par `skip`, assertions plus faibles ou timeout arbitraire.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story durcit l'isolation et la fiabilite d'une suite de tests sans changer le runtime applicatif.
- Behavior change allowed: no
- Behavior change constraints:
  - Aucun comportement produit ne doit changer.
  - Les tests doivent verifier le meme contenu fonctionnel ou une intention plus explicite.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la reproduction identifie une vraie divergence produit plutot qu'une fuite d'etat de test.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le signal de verite est l'execution Vitest reelle. |
| Baseline Snapshot | yes | La reproduction et la correction doivent etre documentees. |
| Ownership Routing | no | Aucun deplacement de responsabilite applicative n'est prevu. |
| Allowlist Exception | yes | Les interdictions de skip, timeout arbitraire et assertion affaiblie doivent etre explicites. |
| Contract Shape | no | Aucun contrat API ou type public n'est touche. |
| Batch Migration | no | Ce n'est pas une migration multi-surface. |
| Reintroduction Guard | yes | La commande full-suite doit rester un signal fiable. |
| Persistent Evidence | yes | Les resultats de reproduction et validation doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard / execution Vitest: `npm run test -- HelpPage` et `npm run test`.
- Secondary evidence:
  - Inspection de `frontend/src/tests/HelpPage.test.tsx`, setup Vitest et mocks partages.
- Static scans alone are not sufficient for this story because:
  - Le probleme observe depend de l'ordre ou de l'isolation de suite, pas seulement d'un symbole statique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/help-page-test-isolation-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/help-page-test-isolation-after.md`
- Expected invariant:
  - `HelpPage.test.tsx` passe en execution cible et ne fait plus echouer la suite complete par fuite d'etat.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/HelpPage.test.tsx` | `it.skip`, `describe.skip`, `test.skip` | Skips masqueraient le signal full-suite. | Forbidden permanently. |
| `frontend/src/tests/HelpPage.test.tsx` | timeout arbitraire | Un timeout masquerait une fuite d'isolation. | Forbidden permanently. |
| `frontend/src/tests/HelpPage.test.tsx` | assertion trop generale | Une assertion faible masquerait la regression observee. | Forbidden permanently. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before reproduction | `help-page-test-isolation-before.md` | Documenter tentative, ordre de suite et hypothese. |
| After validation | `_condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/help-page-test-isolation-after.md` | Prouver les commandes passees apres correction. |

## 4i. Reintroduction Guard

- Guard target: defaillance full-suite-only de `HelpPage.test.tsx` liee a fuite de mocks, timers, routeur, cache ou DOM.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- HelpPage` puis `npm run test`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-013` -
  full run echoue une fois dans `HelpPage.test.tsx` sur `Bug / dysfonctionnement`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-013` - execution isolee `npm run test -- HelpPage` passe 4/4 immediatement apres.
- Evidence 3: `frontend/src/tests/HelpPage.test.tsx` - test cible a inspecter avant toute correction.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- La cause d'isolation est corrigee ou documentee avec une preuve de non-reproduction robuste.
- `HelpPage.test.tsx` reste significatif et ne devient pas plus permissif.
- `npm run test` redevient un signal utilisable pour les stories design-system.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - les guards design-system doivent rester executables et leur signal ne doit pas etre masque par la suite frontend.
- Non-applicable invariants:
  - `RG-044` a `RG-049` - cette story ne modifie pas les registres ou styles design-system.
  - `RG-001` a `RG-043` - hors backend.
- Required regression evidence:
  - `npm run test -- HelpPage`, `npm run test`, repetition de la suite complete si la premiere investigation confirme une flakiness.
- Allowed differences:
  - Correction de setup/mocks/tests; aucun changement runtime produit.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La defaillance est reproduite ou une tentative est documentee. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "npm run test" before.md`. |
| AC2 | L'audit couvre les fuites d'etat de test HelpPage. | Evidence profile: `runtime_behavior`; AST guard plus `npm run test -- HelpPage`. |
| AC3 | Le correctif ne masque pas le test par skip ou assertion faible. | Evidence profile: `targeted_forbidden_symbol_scan`; scan `rg -n "skip|timeout" HelpPage.test.tsx`. |
| AC4 | `HelpPage.test.tsx` passe en execution cible. | Evidence profile: `component_behavior_test`; `npm run test -- HelpPage`. |
| AC5 | La suite frontend complete passe apres correction. | Evidence profile: `reintroduction_guard`; `npm run test`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la reproduction ou tentative de reproduction full-suite (AC: AC1)
- [ ] Task 2 - Auditer les fuites possibles autour de `HelpPage.test.tsx` et du setup Vitest (AC: AC2)
- [ ] Task 3 - Corriger l'isolation avec un delta cible (AC: AC3)
- [ ] Task 4 - Executer `HelpPage` cible puis suite complete (AC: AC4, AC5)
- [ ] Task 5 - Executer lint et persister la validation finale (AC: AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Setup Vitest existant.
  - Helpers de rendu React Testing Library existants s'ils sont deja presents.
  - Patterns de nettoyage deja utilises dans `frontend/src/tests`.
- Do not recreate:
  - Un second harnais de rendu uniquement pour `HelpPage`.
  - Un mock global concurrent si un mock partage existe.
- Shared abstraction allowed only if:
  - Elle corrige une fuite de test commune identifiee par preuve.

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

- `it.skip`, `describe.skip` ou `test.skip` sur `HelpPage`
- assertion remplacee par une presence trop generale
- timeout arbitraire qui cache l'ordre de suite

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/HelpPage.test.tsx`
- `frontend/src/pages/HelpPage.tsx`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/tests/setup.ts`
- `frontend/vitest.config.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/HelpPage.test.tsx` - isolation, requetes ou nettoyage cible.
- `frontend/src/tests/setup.ts` - seulement si une fuite globale est prouvee.
- `_condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/help-page-test-isolation-before.md` - baseline.
- `_condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/help-page-test-isolation-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/HelpPage.test.tsx` - test cible.
- Suite frontend complete via `npm run test`.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/pages/HelpPage.tsx` - a modifier seulement si la preuve montre un bug produit reel.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- HelpPage
npm run test
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-036-stabiliser-isolation-suite-vitest-help-page/00-story.md
```

## 22. Regression Risks

- Risk: le test devient moins strict et laisse passer une regression HelpPage.
  - Guardrail: interdiction d'affaiblir l'assertion sans intention explicite.
- Risk: la correction locale ne couvre pas la fuite globale.
  - Guardrail: `npm run test` complet et repetition si la flakiness est confirmee.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Do not skip or weaken `HelpPage` assertions to make the suite pass.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
