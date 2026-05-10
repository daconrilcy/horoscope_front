# Story CS-134 interdire-imports-api-barrel-internes: Interdire les imports @api depuis le domaine API

Status: ready-to-dev

## 1. Objective

Remplacer l'import interne `@api` dans `frontend/src/api/useDailyPrediction.ts` par un import canonique local.
Ajouter une garde qui interdit les imports barrel `@api` depuis `frontend/src/api`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-004`
- Reason for change: l'audit `frontend-api` signale `F-004`, un import du barrel public depuis l'interieur de son propre domaine.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/api`
- In scope:
  - Corriger l'import `ApiError` dans `useDailyPrediction.ts`.
  - Ajouter ou etendre un test d'architecture frontend qui scanne `frontend/src/api`.
  - Preserver les imports `@api` des consommateurs externes au domaine.
- Out of scope:
  - Changer la politique publique globale `@api`, couverte par `CS-136`.
  - Reorganiser les modules API.
  - Modifier les payloads ou requetes.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-053`, `RG-057`, `RG-064` et `RG-069`.
  - Ne pas ajouter d'allowlist wildcard.
  - Ne pas forcer les pages a abandonner `@api` dans cette story.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ferme une regle de direction d'import par un guard executable.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un autre import `@api` interne est decouvert et ne peut pas etre remplace par un owner local clair.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | le test d'architecture devient la source de verite de la regle d'import. |
| Baseline Snapshot | yes | l'import interdit initial et le resultat final doivent etre captures. |
| Ownership Routing | no | une seule direction d'import est durcie. |
| Allowlist Exception | yes | la story interdit les allowlists larges et documente zero exception retenue. |
| Contract Shape | no | aucun contrat API ou type public ne change. |
| Batch Migration | no | un seul import source est cible. |
| Reintroduction Guard | yes | le guard doit echouer si `@api` revient sous `src/api`. |
| Persistent Evidence | yes | les scans before/after doivent persister pour prouver la fermeture. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - test `api-architecture` sous `frontend/src/tests`.
- Secondary evidence:
  - scan `rg -n 'from [''\""]@api' src/api`.
- Static scans alone are not sufficient:
  - le test `api-architecture` doit agir comme AST guard ou guard de fichiers.
  - AST guard evidence: `npm run test -- api-architecture`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-134-interdire-imports-api-barrel-internes/api-internal-barrel-imports-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-134-interdire-imports-api-barrel-internes/api-internal-barrel-imports-after.md`
- Expected invariant:
  - aucun import `@api` ne reste sous `frontend/src/api`.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: la story ne deplace pas de responsabilites, elle corrige une direction d'import.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/api-architecture-guards.test.ts` | no retained `@api` import in `src/api` | zero exception policy for internal barrel imports | permanent no-exception rule |

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: aucun schema, champ ou status code n'est modifie.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: un fichier source exact est cible par `SC-004`.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before scan | `_condamad/stories/CS-134-interdire-imports-api-barrel-internes/api-internal-barrel-imports-before.md` | capturer le hit initial. |
| after scan | `_condamad/stories/CS-134-interdire-imports-api-barrel-internes/api-internal-barrel-imports-after.md` | prouver le zero-hit final. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails on any import `@api` inside `frontend/src/api`.

Required guard evidence:

```powershell
cd frontend
npm run test -- api-architecture
rg -n 'from [''\""]@api' src/api -g "*.ts" -g "*.tsx"
```

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md` - `F-004` signale l'import API interne.
- Evidence 2: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md` - `SC-004` cible `useDailyPrediction.ts`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `useDailyPrediction.ts` importe `ApiError` depuis `./client` ou l'owner local choisi.
- `rg -n 'from [''\""]@api' src/api` retourne zero hit.
- Le test `api-architecture` bloque toute reintroduction.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - les pages gardent leurs imports publics existants.
  - `RG-069` - les composants partages ne deviennent pas owners d'API.
- Required regression evidence:
  - `npm run test -- api-architecture page-architecture component-architecture`
- Allowed differences:
  - import interne de `useDailyPrediction.ts` uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `useDailyPrediction.ts` n'importe plus depuis `@api`. | Evidence profile: `targeted_forbidden_symbol_scan`; AST guard et `rg -n 'from [''\""]@api' src/api`. |
| AC2 | Un guard executable couvre tout `frontend/src/api`. | Evidence profile: `reintroduction_guard`; AST guard via `npm run test -- api-architecture`. |
| AC3 | Aucune allowlist large n'est introduite. | Evidence profile: `allowlist_register_validated`; revue du test et `npm run test -- api-architecture`. |
| AC4 | Les consommateurs externes conservent leur comportement. | Evidence profile: `ast_architecture_guard`; `npm run test -- DailyHoroscopePage page-architecture`. |

## 8. Implementation Tasks

- [ ] Task 1 - Corriger l'import interne (AC: AC1)
  - [ ] Remplacer `@api` par l'import local canonique.
- [ ] Task 2 - Ajouter la garde d'architecture (AC: AC2, AC3)
  - [ ] Creer ou etendre `api-architecture-guards.test.ts`.
  - [ ] Verifier l'absence de wildcard.
- [ ] Task 3 - Valider les consommateurs (AC: AC4)
  - [ ] Executer les tests cibles.
  - [ ] Executer le scan zero-hit.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - conventions de guards existantes sous `frontend/src/tests`.
  - `ApiError` depuis son owner canonique.
- Do not recreate:
  - nouveau barrel interne.
  - allowlist dossier.
  - wrapper `ApiError` local.
- Shared abstraction allowed only if:
  - elle est deja owner canonique ou requise par un guard existant.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- legacy imports
- fallback import paths
- duplicate active imports
- silent fallback behavior

Specific forbidden symbols / paths:

- `from "@api"` dans `frontend/src/api`
- `from '@api'` dans `frontend/src/api`
- wildcard allowlist pour `src/api`

## 11. Removal Classification Rules

- Removal classification: not applicable
- Reason: aucun module public n'est supprime.

## 12. Removal Audit Format

- Removal audit: not applicable
- Reason: la story corrige un import et ajoute une garde.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Import interne `ApiError` | `frontend/src/api/client.ts` ou helper core canonique | barrel public `@api` |
| Regle d'import interne | `api-architecture` guard | revue manuelle seule |

## 14. Delete-Only Rule

- Delete-only rule: not applicable
- Reason: aucun item removable n'est classe.

## 15. External Usage Blocker

- External usage blocker: not applicable
- Reason: les imports externes `@api` restent explicitement hors scope.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucun contrat genere n'est affecte.

## 17. Files to Inspect First

- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/api/client.ts`
- `frontend/src/tests`
- `frontend/package.json`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/api/useDailyPrediction.ts` - import corrige.
- `frontend/src/tests/api-architecture-guards.test.ts` - guard d'import.

Likely tests:

- `frontend/src/tests/api-architecture-guards.test.ts` - scan AST ou fichier.
- tests existants `DailyHoroscopePage` si import affecte.

Files not expected to change:

- `backend/app/**` - aucun backend.
- `frontend/src/pages/**` - imports publics non changes.
- `frontend/src/components/**` - aucun composant.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- api-architecture DailyHoroscopePage page-architecture component-architecture
npm run lint
npm run typecheck
rg -n 'from [''\""]@api' src/api -g "*.ts" -g "*.tsx"
```

## 21. Regression Risks

- Risk: le guard bloque des imports publics hors domaine.
  - Guardrail: scope strict `src/api`.
- Risk: `ApiError` pointe vers un mauvais owner.
  - Guardrail: test `DailyHoroscopePage` et lint.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not change external `@api` imports.
- Keep all Python commands behind `.\\.venv\\Scripts\\Activate.ps1`.

## 23. References

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md#F-004`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-004`
- `_condamad/stories/regression-guardrails.md`
