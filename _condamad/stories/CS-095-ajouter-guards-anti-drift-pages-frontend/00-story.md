# Story CS-095 ajouter-guards-anti-drift-pages-frontend: Ajouter des guards anti-drift d'architecture des pages frontend

Status: ready-to-dev

## 1. Objective

Ajouter une suite deterministe de guards Vitest/scans pour les pages React.
Elle couvre `@ts-nocheck`, `apiFetch`, barrels stale, alias de routes et exceptions de taille.
Les allowlists doivent etre exactes et non legacy.
Aucune AC ne peut etre acceptee avec limitation.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-006`
- Reason for change: `F-006` montre l'absence de guard page-architecture malgre des guards design-system existants.

## 3. Domain Boundary

- Domain: `frontend-react-pages/architecture-guards`
- In scope:
  - Ajouter `frontend/src/tests/page-architecture-guards.test.ts` ou equivalent.
  - Garder `@ts-nocheck`, `apiFetch` direct en pages, barrels stale, route aliases et page-size exceptions.
  - Creer des allowlists exactes avec owner, raison et condition de sortie.
- Out of scope:
  - Refactorer les pages auditees.
  - Supprimer les routes ou barrels; stories dediees CS-090 a CS-094.
  - Changer les scripts npm sauf besoin strictement justifie.
- Explicit non-goals:
  - Ne pas masquer la dette existante par wildcard.
  - Ne pas creer d'allowlist permanente sans owner et sortie.
  - Ne pas accepter de `PASS with limitation`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ajoute des tests/guards anti-drift sur l'architecture frontend pages.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une exception existante ne peut pas etre classee avec owner, preuve et condition de sortie.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest deviennent la source executable de politique page-architecture. |
| Baseline Snapshot | yes | L'inventaire initial des exceptions gardees doit etre capture. |
| Ownership Routing | no | La story ne migre pas les owners, elle les garde. |
| Allowlist Exception | yes | Les exceptions existantes doivent etre exactes et justifiees. |
| Contract Shape | no | Aucun contrat API/route n'est modifie. |
| Batch Migration | no | Aucun lot de migration code app. |
| Reintroduction Guard | yes | Objet principal de la story. |
| Persistent Evidence | yes | Les preuves de guard et allowlist doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/page-architecture-guards.test.ts` or equivalent
  - allowlist exacte associee aux exceptions existantes
- Secondary evidence:
  - `npm run test -- page-architecture`
  - scans `rg` cibles.
- Static scans alone are not sufficient because:
  - les guards doivent echouer de maniere deterministe pendant Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/page-architecture-before.md`.
- Comparison after implementation: `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/page-architecture-after.md`.
- Expected invariant: les exceptions gardees sont exactes, sourcees et testees par guard.

## 4d. Ownership Routing Rule

- Ownership Routing Rule: not applicable
- Reason: les stories CS-090 a CS-094 traitent les migrations d'ownership; ici seules les regles anti-drift sont ajoutees.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| page architecture allowlist | existing `@ts-nocheck` pages | dette existante uniquement si owner + story de sortie | expire par story referencee |
| page architecture allowlist | existing direct `apiFetch` pages | dette existante uniquement si owner + story de sortie | expire par story referencee |
| page architecture allowlist | existing route aliases | blocker exact ou story CS-094 | expire par classification |
| page architecture allowlist | page-size exceptions | owner + seuil + sortie | expire par story referencee |

Rules:
- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must have owner, evidence and exit condition;
- no exception can justify `PASS with limitation`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or route behavior is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: aucune migration applicative n'est faite dans cette story.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before guard inventory | `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/page-architecture-before.md` | Capturer dette initiale. |
| After guard inventory | `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/page-architecture-after.md` | Prouver garde et allowlist finale. |
| Final validation | `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/generated/10-final-evidence.md` | Persister commandes sans limitation. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: ajouter un guard Vitest qui echoue sur nouvelle dette page-architecture non allowlistee.
- Deterministic source: AST/text scan dans `frontend/src/tests/page-architecture-guards.test.ts`.
- Required forbidden examples: nouveau `@ts-nocheck` en pages, nouveau `apiFetch(` direct en pages, duplicate/stale barrel, alias route non classe, page-size exception sans owner.
- Guard evidence: `npm run test -- page-architecture` ou filtre equivalent.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-006` - aucun guard page-architecture ne bloque la derive.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md#E-011` - tests existants utiles mais pas de guard page ownership.
- Evidence 3: `frontend/package.json` - `npm run test`, `npm run lint` et `npm run build` existent.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants frontend consultes avant cadrage.

## 6. Target State

- Une suite page-architecture executable couvre les cinq risques audites.
- Les exceptions existantes sont exactes, sourcees, avec owner et sortie.
- Les nouvelles derives echouent sans attendre un audit manuel.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - styles inline statiques restent gardes et la nouvelle suite ne l'affaiblit pas.
  - `RG-049` - surfaces legacy frontend restent gardees.
  - `RG-050` - la suite anti-drift frontend reste executable.
  - `RG-054` - redirects admin legacy ne reviennent pas.
- Non-applicable invariants:
  - `RG-044` - aucun namespace token.
  - `RG-053` - aucune compatibilite runtime payload.
- Required regression evidence:
  - `npm run test -- page-architecture`
  - `npm run test -- design-system legacy-style`
  - `npm run lint`
- Allowed differences:
  - nouveaux tests/allowlists exactes uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le guard echoue pour nouveau `@ts-nocheck` page non allowliste. | Evidence profile: `reintroduction_guard`; test `npm run test -- page-architecture`. |
| AC2 | Le guard echoue pour nouvel `apiFetch(` direct. | Evidence profile: `reintroduction_guard`; test `npm run test -- page-architecture`. |
| AC3 | Le guard couvre les alias routes. | Evidence profile: `reintroduction_guard`; runtime evidence `npm run test -- src/tests/page-architecture-guards.test.ts`. |
| AC4 | Les exceptions taille ont un owner. | Evidence profile: `allowlist_register_validated`; artifact `page-architecture-after.md`; command `rg -n "owner" page-after.md`. |
| AC5 | Aucun wildcard n'est utilise. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "PASS with limitation|wildcard|legacy" final.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier les surfaces existantes a allowlister exactement. (AC: AC4)
- [ ] Task 2 - Ajouter le test guard page-architecture. (AC: AC1, AC2, AC3)
- [ ] Task 3 - Creer ou completer l'allowlist exacte avec owners et sorties. (AC: AC4, AC5)
- [ ] Task 4 - Prouver que les guards existants design-system restent verts. (AC: AC5)
- [ ] Task 5 - Capturer evidence finale sans limitation. (AC: AC1, AC2, AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse les patterns de `frontend/src/tests/design-system-guards.test.ts` et allowlists existantes.
- Do not duplicate scanner logic if un helper test local existe deja.
- Shared abstraction allowed only if elle sert plusieurs guards testables.

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
- wildcard allowlist.
- exception folder-wide `frontend/src/pages/**`.
- `PASS with limitation`.
- `legacy` ou `compatibility` comme justification d'exception.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Page architecture guards | `frontend/src/tests/page-architecture-guards.test.ts` | audit manuel uniquement |
| Guard allowlist | exact allowlist module or data file under `frontend/src/tests` | wildcard comments |
| Design-system guards | existing design-system tests | duplicated policy divergent |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `frontend/package.json`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/admin/index.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/tests/page-architecture-guards.test.ts` - nouvelle suite guard.
- `frontend/src/tests/page-architecture-allowlist.ts` - allowlist exacte des exceptions existantes.
- `frontend/src/tests/design-system-guards.test.ts` - uniquement si un helper commun local est reutilise sans affaiblir l'existant.

Likely tests:
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`

Files not expected to change:
- `frontend/package.json` - les filtres Vitest existants suffisent sauf preuve contraire.
- `frontend/src/pages/**/*.tsx` - aucune refactor applicative dans cette story.
- `backend/app/main.py` - aucun backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- page-architecture
npm run test -- design-system legacy-style
npm run lint
rg -n "PASS with limitation|wildcard|compatibility|fallback" src/tests/page-architecture*
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: guard trop large bloque toute evolution utile.
  - Guardrail: allowlist exacte avec owner et sortie.
- Risk: guard trop permissif masque la dette.
  - Guardrail: AC5 interdit wildcard et limitation.
- Risk: duplication des policies design-system.
  - Guardrail: reuse des patterns existants.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- No legacy may remain in the implemented guard policy.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-006`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-006`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`
