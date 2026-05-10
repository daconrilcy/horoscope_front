# Story CS-133 structurer-modules-api-volumineux: Structurer les modules API volumineux par domaine

Status: ready-to-dev

## 1. Objective

Scinder `frontend/src/api/adminPrompts.ts` et `frontend/src/api/natalChart.ts` en sous-modules de domaine, sans changer les imports publics observes.
La sortie attendue est une separation lisible des types, requetes, hooks et effets navigateur avec un entrypoint public explicite.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-003`
- Reason for change: l'audit `frontend-api` signale `F-003`, deux fichiers API volumineux qui portent trop de responsabilites.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/api`
- In scope:
  - Extraire `adminPrompts.ts` vers une structure de domaine admin prompts.
  - Extraire `natalChart.ts` vers une structure de domaine natal chart.
  - Maintenir `frontend/src/api/index.ts` comme facade publique actuelle tant que `CS-136` n'a pas tranche.
- Out of scope:
  - Changer la politique globale `@api`, couverte par `CS-136`.
  - Centraliser les erreurs, couvert par `CS-132`.
  - Migrer le transport, couvert par `CS-131`.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-053`, `RG-057`, `RG-064`, `RG-065`, `RG-071` et `RG-073`.
  - Ne pas creer d'entrypoint transitoire parallele au-dela de l'entrypoint public choisi.
  - Ne pas deplacer de logique UI dans `frontend/src/api`.

## 4. Operation Contract

- Operation type: split
- Primary archetype: namespace-convergence
- Archetype reason: deux modules plats doivent converger vers des namespaces de domaine explicites.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la politique `@api` requise par `CS-136` impose des chemins finaux incompatibles avec la facade actuelle.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | le guard `api-architecture` devient la source executable de la structure API frontend. |
| Baseline Snapshot | yes | les exports et imports publics doivent etre captures avant/apres. |
| Ownership Routing | yes | types, requetes, hooks et effets doivent recevoir un owner clair. |
| Allowlist Exception | no | aucune exception ou allowlist n'est attendue. |
| Contract Shape | no | les types publics doivent rester compatibles. |
| Batch Migration | yes | les deux modules sont des lots separes. |
| Reintroduction Guard | yes | la croissance monolithique doit etre bloquee par guard ou inventaire. |
| Persistent Evidence | yes | les inventaires d'exports et ownership doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `api-architecture` sous `frontend/src/tests`.
- Secondary evidence:
  - tests cibles `AdminPromptsPage`, `adminPromptsApi`, `natalChartApi`, `NatalChartPage` et `natalInterpretation`.
- Static scans alone are not sufficient:
  - le guard d'architecture doit verifier les entrypoints et owners au-dela d'un simple `rg`.
  - AST guard evidence: `npm run test -- api-architecture`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-exports-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-exports-after.md`
- Expected invariant:
  - les exports publics existants restent disponibles depuis le point public retenu.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Types admin prompts | domaine admin prompts API | fichier monolithique racine |
| Requetes admin prompts | domaine admin prompts API | hooks natal ou client core |
| Types natal chart | domaine natal chart API | fichier monolithique racine |
| Effets navigateur natal | sous-module natal explicite | helper partage sans owner |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucun fichier ne doit etre conserve par exception.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: les payloads et types publics restent compatibles.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| admin-prompts | `frontend/src/api/adminPrompts.ts` | `frontend/src/api/admin-prompts/**` | imports internes | admin prompts tests | export inventory | `CS-136` incompatible |
| natal-chart | `frontend/src/api/natalChart.ts` | `frontend/src/api/natal-chart/**` | imports internes | natal tests | export inventory | `CS-136` incompatible |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| export baseline | `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-exports-before.md` | capturer exports et consommateurs publics. |
| export result | `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-exports-after.md` | prouver la compatibilite finale. |
| ownership map | `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-module-ownership.md` | classer les sous-modules crees. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard against reintroduced monolithic ownership.

Deterministic source: forbidden symbols in `frontend/src/api/adminPrompts.ts` and `frontend/src/api/natalChart.ts`.

Required guard evidence:

```powershell
cd frontend
npm run test -- api-architecture AdminPromptsPage adminPromptsApi natalChartApi NatalChartPage natalInterpretation
```

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md` - `F-003` classe les fichiers API volumineux.
- Evidence 2: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md` - `SC-003` cible `adminPrompts.ts` et `natalChart.ts`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les responsabilites admin prompts et natal chart sont separees en fichiers de domaine.
- Les imports publics existants via `@api` restent fonctionnels jusqu'a decision `CS-136`.
- Les tests cibles prouvent l'absence de regression fonctionnelle.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - les pages gardent leur architecture route/container.
  - `RG-065` - AdminPrompts reste sous owners feature pour les sections page.
  - `RG-071` et `RG-073` - l'orchestration natal interpretation reste sous owner feature.
- Required regression evidence:
  - `npm run test -- page-architecture AdminPromptsPage natalInterpretation NatalChartPage`
- Allowed differences:
  - chemins internes de fichiers API, pas de changement de comportement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les exports publics before/after sont documentes. | Evidence profile: `baseline_before_after_diff`; `npm run test -- api-architecture` et artefacts before/after. |
| AC2 | `adminPrompts` est scinde par responsabilite. | Evidence profile: `namespace_converged`; `npm run test -- AdminPromptsPage adminPromptsApi api-architecture`. |
| AC3 | `natalChart` est scinde par responsabilite. | Evidence profile: `namespace_converged`; `npm run test -- natalChartApi NatalChartPage natalInterpretation`. |
| AC4 | Aucun re-export transitoire parallele n'est ajoute. | Evidence profile: `targeted_forbidden_symbol_scan`; scan imports/exports et `npm run test -- api-architecture`. |
| AC5 | Les invariants page restent preserves. | Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture component-architecture`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer les exports et consommateurs (AC: AC1)
  - [ ] Ecrire l'inventaire before.
  - [ ] Identifier les imports publics a preserver.
- [ ] Task 2 - Scinder admin prompts (AC: AC2, AC4)
  - [ ] Extraire types, requetes et hooks.
  - [ ] Garder une facade publique unique.
- [ ] Task 3 - Scinder natal chart (AC: AC3, AC4)
  - [ ] Extraire types, requetes, hooks et effets navigateur.
  - [ ] Verifier les consommateurs feature.
- [ ] Task 4 - Valider et documenter after (AC: AC1, AC5)
  - [ ] Ecrire `api-exports-after.md` et `api-module-ownership.md`.
  - [ ] Executer tests et scans.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - exports publics existants de `frontend/src/api/index.ts`.
  - tests existants admin prompts et natal chart.
- Do not recreate:
  - facade parallele.
  - types dupliques entre ancien et nouveau module.
  - logique API dans les pages ou composants.
- Shared abstraction allowed only if:
  - elle est neutre entre les deux domaines et remplace une duplication prouvee.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- legacy imports
- fallback re-export behavior
- duplicate active implementations
- silent fallback behavior

Specific forbidden symbols / paths:

- ancien module racine conservant la logique apres extraction
- re-export profond non documente hors entrypoint public choisi
- nouveau `index.ts` de compatibilite sans owner

## 11. Removal Classification Rules

- Removal classification: not applicable
- Reason: les fichiers racine peuvent rester entrypoints publics tant que `CS-136` n'a pas tranche.

## 12. Removal Audit Format

- Removal audit: not applicable
- Reason: aucun export public n'est supprime par cette story.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| API admin prompts | sous-module admin prompts | fichier racine monolithique |
| API natal chart | sous-module natal chart | fichier racine monolithique |
| Facade publique API | `frontend/src/api/index.ts` jusqu'a `CS-136` | facades paralleles |

## 14. Delete-Only Rule

- Delete-only rule: not applicable
- Reason: aucune surface publique n'est classee removable dans ce lot.

## 15. External Usage Blocker

- External usage blocker: not applicable
- Reason: l'inventaire porte sur consommateurs frontend internes.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucun schema genere n'est change.

## 17. Files to Inspect First

- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/api/index.ts`
- `frontend/package.json`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/api/adminPrompts.ts` - facade ou decomposition.
- `frontend/src/api/natalChart.ts` - facade ou decomposition.
- `frontend/src/api/index.ts` - exports publics preserves.
- `frontend/src/api/admin-prompts/**` - nouveaux sous-modules si convention retenue.
- `frontend/src/api/natal-chart/**` - nouveaux sous-modules si convention retenue.
- `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-exports-before.md` - baseline.
- `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-exports-after.md` - preuve finale.
- `_condamad/stories/CS-133-structurer-modules-api-volumineux/api-module-ownership.md` - ownership.

Likely tests:

- `frontend/src/tests/api-architecture-guards.test.ts` - guard de structure API.
- tests existants couvrant `AdminPromptsPage`, `adminPromptsApi`, `natalChartApi`, `NatalChartPage`, `natalInterpretation`.

Files not expected to change:

- `backend/app/**` - aucun backend.
- `frontend/src/components/ui/**` - aucun composant UI primitif.
- `frontend/src/pages/**` - pas de refonte page.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- AdminPromptsPage adminPromptsApi natalChartApi NatalChartPage natalInterpretation
npm run test -- api-architecture page-architecture component-architecture
npm run lint
npm run typecheck
rg -n "from ['\"]@api|from ['\"]\\./adminPrompts|from ['\"]\\./natalChart" src -g "*.ts" -g "*.tsx"
```

## 21. Regression Risks

- Risk: export public perdu.
  - Guardrail: inventaire before/after.
- Risk: facade de compatibilite parallele.
  - Guardrail: scan imports/exports et ownership map.
- Risk: page admin ou natal cassee.
  - Guardrail: tests cibles.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Preserve public imports until `CS-136` decides otherwise.
- Keep all Python commands behind `.\\.venv\\Scripts\\Activate.ps1`.

## 23. References

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md#F-003`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-003`
- `_condamad/stories/regression-guardrails.md`
