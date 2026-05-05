# Story CS-042 reduire-fallbacks-css-allowlistes-surfaces-partagees: Reduire les fallbacks CSS allowlistes dans les surfaces partagees

Status: done

## 1. Objective

Reduire le nombre de fallbacks `var(--token, value)` encore allowlistes dans les surfaces frontend partagees.
Les literals de secours doivent devenir des tokens canoniques requis ou des exceptions documentees.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-004` indique que 165 fallbacks CSS restent dans 30 fichiers, ce qui maintient des valeurs alternatives de compatibilite ou migration-only.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Capturer un baseline des 165 fallbacks et selectionner un lot prioritaire partage UI/layout.
  - Remplacer les fallbacks migration-only par `var(--token)` quand le token canonique est requis.
  - Conserver uniquement les fallbacks dynamiques, compatibility ou semantic-extension exactement documentes.
  - Mettre a jour le registre et l'allowlist executable apres reduction.
  - Tester les surfaces partagees touchees.
- Out of scope:
  - Correction de parite markdown/executable deja couverte par `CS-040`, sauf synchronisation necessaire apres reduction.
  - Conversion des styles inline TSX.
  - Migration generale des hardcoded values non fallback.
  - Ajout de nouveaux tokens semantiques sans decision documentee dans le registre de namespaces.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-048` ou `RG-050`.
  - Ne pas ajouter un fallback literal pour rendre un test isole vert.
  - Ne pas creer d'exception par dossier ou wildcard.
  - Ne pas traiter tous les fichiers page-level si cela depasse le lot borne.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot de fallbacks allowlistes vers tokens canoniques et exceptions exactes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent lorsque les tokens requis existent.
  - Les fallbacks permanents restent seulement s'ils ont statut, raison et sortie.
  - Les composants touches ne changent pas d'API React publique.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une surface doit fonctionner sans import global de tokens et qu'aucune politique d'isolation n'existe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest CSS fallback valident les exceptions actives. |
| Baseline Snapshot | yes | Le compte et la liste des fallbacks du lot doivent diminuer avant/apres. |
| Ownership Routing | yes | Les tokens canoniques et exceptions fallback ont des owners distincts. |
| Allowlist Exception | yes | Chaque fallback restant est une exception exacte. |
| Contract Shape | no | Aucun contrat API, DTO, payload ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un lot multi-fichiers priorise. |
| Reintroduction Guard | yes | Les fallbacks retires ou non classes ne doivent pas revenir. |
| Persistent Evidence | yes | Les inventaires before/after prouvent la reduction. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/css-fallback-policy.test.ts`.
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`.
- Secondary evidence:
  - `frontend/src/styles/css-fallback-allowlist.md`.
  - `frontend/src/tests/design-system-allowlist.ts`.
  - Scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Les scans comptent les fallbacks mais ne prouvent pas leur classification exacte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/css-fallbacks-after.md`
- Expected invariant:
  - Le nombre de fallbacks du lot diminue et aucun fallback non classe n'est ajoute ailleurs.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token global requis | `frontend/src/styles/design-tokens.css` ou registre token canonique | fallback literal local |
| Exception fallback | `frontend/src/styles/css-fallback-allowlist.md` + `CSS_FALLBACK_EXCEPTIONS` | CSS implicite |
| Classification namespace | `frontend/src/styles/token-namespace-registry.md` | token local non documente |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | fallbacks restants du lot | Exception documentee. | Exit condition required. |
| `frontend/src/tests/design-system-allowlist.ts` | `CSS_FALLBACK_EXCEPTIONS` | Exception executable exacte. | Must shrink or match documented retained exceptions. |

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
| Shared batch | selected fallbacks | `var(--token)` or exception | CSS lot | `npm run test -- css-fallback` | scan + diff | missing owner |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/css-fallbacks-before.md` | Capturer le lot selectionne et le compte initial. |
| After inventory | `css-fallbacks-after.md` | Prouver la reduction, les exceptions finales et les deltas. |
| Fallback registry | `frontend/src/styles/css-fallback-allowlist.md` | Documenter les exceptions restantes. |
| Executable allowlist | `frontend/src/tests/design-system-allowlist.ts` | Garder la preuve executable exacte. |

## 4i. Reintroduction Guard

- Guard target: fallback CSS retire ou fallback non present dans l'allowlist exacte.
- Architecture guard required: `frontend/src/tests/css-fallback-policy.test.ts` doit echouer pour tout fallback non classe.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-004` - 165 fallbacks CSS restent dans 30 fichiers.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md#F-004---Remaining-CSS-Fallback-Files` - liste exhaustive des fichiers candidats.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - registre des exceptions a reduire/synchroniser.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist executable des exceptions.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le lot partage contient moins de fallbacks CSS literaux.
- Les fallbacks restants sont classes et synchronises dans le registre et l'allowlist executable.
- Les tokens canoniques requis sont consommes sans valeur de secours locale.
- Les tests design-system et scans prouvent qu'aucune exception implicite n'a ete ajoutee.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-045` - les hardcoded values hors fallback ne sont pas le domaine principal.
  - `RG-046` - la typographie n'est pas le domaine principal.
  - `RG-047` - les styles inline ne sont pas touches.
  - `RG-049` - aucun selecteur legacy n'est cree.
- Required regression evidence:
  - `npm run test -- css-fallback design-system`, scan fallback cible, `npm run lint`.
- Allowed differences:
  - Suppression de fallbacks pour tokens disponibles; conservation d'exceptions exactes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Un lot explicite est capture avant edition avec compte initial. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "Batch|count" css-fallbacks-before.md`. |
| AC2 | Les fallbacks migration-only du lot deviennent `var(--token)` ou bloquent. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "var\\(" src -g "*.css"`. |
| AC3 | Les fallbacks restants du lot ont une condition de sortie. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- css-fallback`. |
| AC4 | Le contrat fallback reste synchronise. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- design-system css-fallback`. |
| AC5 | Les surfaces touchees ont une preuve de non-regression. | Evidence profile: `component_behavior_test`; command: `npm run test -- css-fallback Button Modal Select`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et choisir un lot partage borne (AC: AC1)
- [ ] Task 2 - Classer chaque fallback du lot et identifier le token canonique ou l'exception restante (AC: AC2, AC3)
- [ ] Task 3 - Remplacer les fallbacks migration-only par le token requis (AC: AC2)
- [ ] Task 4 - Synchroniser registre markdown et allowlist executable apres reduction (AC: AC3, AC4)
- [ ] Task 5 - Executer tests cibles des surfaces partagees touchees (AC: AC5)
- [ ] Task 6 - Capturer l'inventaire after, scans, guards et lint (AC: AC1, AC4, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/token-namespace-registry.md`.
  - `frontend/src/styles/css-fallback-allowlist.md`.
  - `frontend/src/tests/design-system-allowlist.ts`.
  - `frontend/src/tests/css-fallback-policy.test.ts`.
- Do not recreate:
  - Des tokens locaux pour eviter une decision de namespace.
  - Une deuxieme allowlist de fallbacks.
  - Des fallback literals dans des CSS touches sans classification.
- Shared abstraction allowed only if:
  - Elle correspond a un token semantique durable documente dans le registre de namespaces.

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

- `var(--token, value)` pour un token canonique requis dans un fichier touche.
- Entree `CSS_FALLBACK_EXCEPTIONS` sans ligne documentaire equivalente.
- Fallback conserve sans condition de sortie.
- Exception wildcard ou par dossier.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Token requis | `frontend/src/styles/design-tokens.css` et registre token | fallback local |
| Exception fallback | `css-fallback-allowlist.md` + `CSS_FALLBACK_EXCEPTIONS` | CSS implicite |

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
- `frontend/src/App.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/styles/utilities.css`
- `frontend/src/styles/glass.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/css-fallback-allowlist.md` - reduction/synchronisation des exceptions.
- `frontend/src/tests/design-system-allowlist.ts` - reduction/synchronisation executable.
- CSS du lot selectionne depuis `Files to Inspect First` - suppression de fallbacks.
- `_condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/css-fallbacks-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - garde principale.
- `frontend/src/tests/design-system-guards.test.ts` - garde design-system.
- Tests existants des composants/pages touches si disponibles.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/**/*.tsx` - hors scope sauf test cible necessaire.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- css-fallback design-system Button Badge EmptyState ErrorState LockedSection Modal Select UpgradeCTA
rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-042-reduire-fallbacks-css-allowlistes-surfaces-partagees/00-story.md
```

## 22. Regression Risks

- Risk: un composant isole perd un fallback encore necessaire.
  - Guardrail: blocker si la politique d'import global ou de token ownership est ambiguë.
- Risk: l'allowlist et le registre divergent apres reduction.
  - Guardrail: tests `css-fallback design-system`.
- Risk: un fallback retire revient dans un fichier voisin.
  - Guardrail: scan cible du lot et `RG-048`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Ne pas ajouter de fallback literal pour compenser une decision de token manquante.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md` - liste des fichiers candidats.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
