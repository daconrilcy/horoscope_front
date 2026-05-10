# Story CS-136 definir-politique-facade-api-publique: Definir la politique de facade publique @api

Status: ready-to-dev

## 1. Objective

Prendre une decision d'architecture documentee sur `frontend/src/api/index.ts` et l'alias `@api`.
La story doit choisir entre entrypoint global, entrypoints par domaine, ou imports directs controles.
Elle classe aussi les modules B2B, Ops et guidance sans consommateur runtime trouve par l'audit.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-006`
- Reason for change: l'audit `frontend-api` signale `F-006`, une ambiguite d'entrypoint public qui bloque la classification finale de plusieurs exports.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/api`
- In scope:
  - Produire une decision d'architecture sur la facade `@api`.
  - Classer `b2bAstrology.ts`, `b2bBilling.ts`, `b2bEditorial.ts`, `b2bUsage.ts`, `guidance.ts` et `opsMonitoring.ts`.
  - Definir les regles d'import public/interne applicables aux prochaines migrations.
- Out of scope:
  - Migrer physiquement les modules avant decision.
  - Changer les contrats backend ou endpoints.
  - Corriger les findings `F-001` a `F-005`, couverts par `CS-131` a `CS-135`.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-053`, `RG-057`, `RG-064` et `RG-069`.
  - Ne pas changer `frontend/src/api/index.ts` sans decision explicite dans l'artefact d'architecture.
  - Ne pas classer un module sans preuve d'import, test ou usage runtime.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story est une decision d'architecture bloquante, pas une migration de code par defaut.
- Additional validation rules:
  - La decision doit etre ecrite avant tout changement de structure.
  - Chaque module ambigu doit recevoir une classification exacte et une preuve.
  - Les changements de code sont interdits tant que la decision n'est pas presente.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: plusieurs politiques restent plausibles apres l'inventaire ou si un export est destine a un consommateur externe non visible dans le depot.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | le guard ou inventaire `api-architecture` devient la source executable de la politique choisie. |
| Baseline Snapshot | yes | l'inventaire des imports/exports doit preceder la decision. |
| Ownership Routing | yes | les entrypoints publics et internes doivent avoir des owners. |
| Allowlist Exception | yes | les exports sans consommateur runtime doivent etre classes exactement. |
| Contract Shape | no | aucun DTO ou payload ne change. |
| Batch Migration | no | les migrations futures seront des stories separees. |
| Reintroduction Guard | no | le guard sera ajoute dans les stories d'implementation selon la politique retenue. |
| Persistent Evidence | yes | la decision et la classification doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - inventaire d'exports `@api` et AST guard `api-architecture` si present.
- Secondary evidence:
  - scans des imports `@api`, B2B, Ops et guidance.
- Static scans alone are not sufficient:
  - la decision doit citer le guard existant ou expliquer le guard a creer dans une story d'application.
  - AST guard evidence: `npm run test -- api-architecture`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-public-surface-inventory.md`
- Comparison after implementation:
  - `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-public-facade-decision.md`
- Expected invariant:
  - chaque export ambigu possede une classification exacte et une action autorisee.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Facade publique globale | decision `api-public-facade-decision.md` | convention implicite |
| Entrypoint par domaine | decision `api-public-facade-decision.md` | chemins inventes par story locale |
| Module sans consommateur runtime | classification exacte | conservation implicite par barrel |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `api-module-classification.md` | B2B/Ops/guidance exports | classification des exports ambigus | permanent until next architecture decision |

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: la story ne change aucun contrat de donnees.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: cette story produit une decision et ouvre des migrations separees quand la decision les exige.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| inventory | `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-public-surface-inventory.md` | lister exports et consommateurs actuels. |
| decision | `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-public-facade-decision.md` | documenter la politique retenue. |
| classification | `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-module-classification.md` | classer modules B2B, Ops et guidance. |

## 4i. Reintroduction Guard

- Reintroduction guard: not applicable
- Reason: la decision cree la politique; les guards executables seront exiges par les stories qui appliquent cette politique.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md` - la closure est bloquee par la politique de facade publique.
- Evidence 2: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md` - `SC-006` liste les modules et le besoin de decision.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `api-public-facade-decision.md` nomme la politique retenue et ses consequences.
- `api-module-classification.md` classe les modules B2B, Ops et guidance ambigus.
- Les stories `CS-131` a `CS-135` disposent d'une decision claire si elles touchent la facade publique.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-053` - aucune compatibilite runtime historique ne doit etre introduite par decision.
  - `RG-057` - aucun vocabulaire legacy ou fallback de compatibilite n'est autorise.
  - `RG-064` - la politique ne doit pas rendre les pages owners implicites d'API.
  - `RG-069` - la politique ne doit pas rendre les composants partages owners implicites d'API.
- Required regression evidence:
  - inventaire d'imports publics et scan des consommateurs.
  - `npm run test -- api-architecture page-architecture component-architecture` si un guard existe deja.
- Allowed differences:
  - documentation de decision uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'inventaire public `@api` liste les exports. | Evidence profile: `baseline_before_after_diff`; AST guard via `npm run test -- api-architecture`. |
| AC2 | Une politique unique est choisie pour `frontend/src/api/index.ts`. | Evidence profile: `allowlist_register_validated`; AST guard via `npm run test -- api-architecture`. |
| AC3 | Chaque module B2B/Ops/guidance ambigu est classe. | Evidence profile: `allowlist_register_validated`; `npm run test -- api-architecture` et artefact classification. |
| AC4 | Les stories dependantes savent si elles peuvent modifier l'entrypoint. | Evidence profile: `batch_migration_mapping`; `npm run test -- api-architecture`. |
| AC5 | Aucun changement runtime n'est effectue sans story separee. | Evidence profile: `targeted_forbidden_symbol_scan`; AST guard via `npm run test -- api-architecture`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier la surface publique (AC: AC1)
  - [ ] Lister les exports de `index.ts`.
  - [ ] Lister les consommateurs runtime, tests et barrel-only.
- [ ] Task 2 - Rediger la decision d'architecture (AC: AC2, AC4)
  - [ ] Choisir une politique unique.
  - [ ] Documenter les consequences pour `CS-131` a `CS-135`.
- [ ] Task 3 - Classer les modules ambigus (AC: AC3)
  - [ ] Classer B2B, Ops et guidance.
  - [ ] Identifier les blockers utilisateur.
- [ ] Task 4 - Verifier l'absence de changement runtime non autorise (AC: AC5)
  - [ ] Inspecter le diff.
  - [ ] Executer les scans d'import.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - inventaires de l'audit `frontend-api`.
  - alias `@api` et configuration existante comme evidence.
- Do not recreate:
  - seconde politique d'import.
  - classification implicite.
  - facade parallele.
- Shared abstraction allowed only if:
  - elle est decrite dans la decision et implementee par une story separee.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- legacy imports
- fallback public entrypoint
- duplicate active policies
- silent fallback behavior

Specific forbidden symbols / paths:

- nouvel entrypoint public sans decision
- conservation implicite d'un export barrel-only non classe
- changement de `frontend/src/api/index.ts` sans artefact de decision

## 11. Removal Classification Rules

- Removal classification: not applicable
- Reason: cette story ne ferme aucun fichier; elle classe les surfaces pour de futures stories.

## 12. Removal Audit Format

- Removal audit: not applicable
- Reason: aucune fermeture de surface n'est executee dans cette story.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Politique facade API | `api-public-facade-decision.md` | decisions implicites par fichier |
| Classification modules ambigus | `api-module-classification.md` | exports barrel-only non classes |
| Migrations d'application | stories futures referencees | changement opportuniste dans cette story |

## 14. Delete-Only Rule

- Delete-only rule: not applicable
- Reason: aucune fermeture de fichier ou export n'est autorisee sans story d'application.

## 15. External Usage Blocker

- If an export may be consumed outside the repository, classify it as `external-unknown` in `api-module-classification.md` and require user decision.
- Do not change such export in this story.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucun contrat genere n'est produit ou modifie.

## 17. Files to Inspect First

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md`
- `frontend/src/api/index.ts`
- `frontend/tsconfig.json`
- `frontend/package.json`

## 18. Expected Files to Modify

Likely files:

- `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-public-surface-inventory.md` - inventaire.
- `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-public-facade-decision.md` - decision.
- `_condamad/stories/CS-136-definir-politique-facade-api-publique/api-module-classification.md` - classification.

Likely tests:

- `frontend/src/tests/api-architecture-guards.test.ts` only if an existing guard needs documentation alignment.

Files not expected to change:

- `frontend/src/api/index.ts` - pas avant decision d'application separee.
- `backend/app/**` - aucun backend.
- `frontend/src/pages/**` - aucun consommateur modifie.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
rg -n "from ['\"]@api|from ['\"]../api|from ['\"]../../api" src -g "*.ts" -g "*.tsx"
rg -n "b2bAstrology|b2bBilling|b2bEditorial|b2bUsage|guidance|opsMonitoring" src -g "*.ts" -g "*.tsx"
npm run test -- api-architecture page-architecture component-architecture
npm run lint
git diff --stat
```

## 21. Regression Risks

- Risk: decision insuffisamment precise pour debloquer les autres stories.
  - Guardrail: AC2 et AC4 exigent politique unique et consequences explicites.
- Risk: module ambigu classe sans preuve.
  - Guardrail: inventaire `api-public-surface-inventory.md`.
- Risk: changement runtime accidentel.
  - Guardrail: `git diff --stat` et scope limite aux artefacts.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not change runtime code before the decision artifact exists.
- Keep all Python commands behind `.\\.venv\\Scripts\\Activate.ps1`.

## 23. References

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md#F-006`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-006`
- `_condamad/stories/regression-guardrails.md`
