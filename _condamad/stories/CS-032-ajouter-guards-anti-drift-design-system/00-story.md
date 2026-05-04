# Story CS-032 ajouter-guards-anti-drift-design-system: Ajouter les guards anti-drift du design system frontend

Status: ready-to-dev

## 1. Objective

Ajouter une suite de tests statiques anti-regression.
Elle rend detectable en CI la derive des tokens, valeurs hardcodees, styles inline, fallbacks CSS, typographie et selecteurs anciens.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-007`
- Reason for change: le finding `F-007` montre que les tests existants valident des valeurs de tokens mais pas la discipline de consommation du design-system.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/tests`
- In scope:
  - Creer ou consolider les guards statiques design-system.
  - Valider les registres issus de `CS-026` a `CS-031`.
  - Ajouter un snapshot des exceptions autorisees.
  - Documenter la commande de test cible.
- Out of scope:
  - Migrer des styles applicatifs.
  - Ajouter une dependance de lint externe.
  - Remplacer les tests visuels existants.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas faire passer des exceptions non classees par un snapshot global.
  - Ne pas ajouter de garde qui requiert le rendu navigateur pour un scan statique.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story ajoute des tests anti-regression et des allowlists exactes sans changer le runtime.
- Behavior change allowed: no
- Behavior change constraints:
  - Aucun comportement applicatif ne doit changer.
  - Les guards doivent consommer les registres existants plutot que les redefinir.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une garde exige une allowlist initiale qui n'existe pas encore dans `CS-026` a `CS-031`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests doivent inspecter les fichiers reels du frontend. |
| Baseline Snapshot | yes | Le snapshot initial d'exceptions doit etre capture pour comparer la garde. |
| Ownership Routing | no | Les owners sont portes par les registres des stories precedentes. |
| Allowlist Exception | yes | Les exceptions doivent etre exactes et testees. |
| Contract Shape | no | Aucun API, DTO ou type frontend public n'est change. |
| Batch Migration | no | La story installe des guards, pas une migration. |
| Reintroduction Guard | yes | Le but principal est de bloquer la derive future. |
| Persistent Evidence | yes | Les tests et snapshots d'exceptions sont les artefacts executables persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard CSS/TSX et inventaire disque des fichiers frontend.
  - Commande cible: `npm run test -- design-system`.
- Secondary evidence:
  - Les registres `token-namespace`, `css-fallback`, `legacy-style` et inline-style allowlist.
- Static scans alone are not sufficient for this story because:
  - Les scans doivent etre executes sous Vitest avec assertions et exceptions exactes.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-032-ajouter-guards-anti-drift-design-system/design-system-exceptions-before.md`
- Comparison after implementation: `_condamad/stories/CS-032-ajouter-guards-anti-drift-design-system/design-system-exceptions-after.md`
- Expected invariant: chaque exception initiale est exacte, sourcee et verifiee par une assertion.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: les registres d'ownership sont definis par `CS-026`, `CS-031` et les stories de migration.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | hardcoded value exception | Valeur classee par migration precedente. | Until corresponding migration story resolves it. |
| `frontend/src/tests/design-system-allowlist.ts` | inline style exception | Cas dynamique classe par `CS-029`. | Permanent while runtime data controls value. |
| `frontend/src/tests/design-system-allowlist.ts` | CSS fallback exception | Cas classe par `CS-030`. | Until fallback registry marks canonical. |
| `frontend/src/tests/design-system-allowlist.ts` | legacy selector exception | Cas classe par `CS-031`. | Until component migration story resolves it. |

Rules:

- no folder wildcard;
- no regex that matches an entire category;
- every exception must include file, symbol and source story;
- every exception must be asserted by a test.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: cette story ne migre pas de consommateurs; elle valide des politiques existantes.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Design-system allowlist | `frontend/src/tests/design-system-allowlist.ts` | Centraliser les exceptions exactes. |
| Guard test | `frontend/src/tests/design-system-guards.test.ts` | Executer les guards anti-drift. |
| Before snapshot | `design-system-exceptions-before.md` | Capturer les exceptions initiales. |
| After snapshot | `design-system-exceptions-after.md` | Prouver les exceptions finales. |

## 4i. Reintroduction Guard

- Guard target: hardcoded colors, spacing, radius, typography literals, CSS var fallbacks, inline styles and token namespaces outside exact allowlists.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-011` - `theme-tokens.test.ts` ne garde pas la discipline de consommation.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/00-audit-report.md` - les scans identifient les principales derives frontend.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-007` - les guards doivent suivre `SC-001` a `SC-005`.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Une commande cible `npm run test -- design-system` execute les guards design-system.
- Les exceptions sont exactes, sourcees et rattachees aux stories precedentes.
- Les nouvelles derives echouent en CI locale.
- Les tests existants `theme-tokens` restent compatibles ou sont inclus dans la suite.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - namespaces de tokens frontend classes.
  - `RG-045` - valeurs hardcodees migrees bloquees.
  - `RG-046` - typographie par roles semantiques.
  - `RG-047` - styles inline statiques interdits.
  - `RG-048` - fallbacks CSS non classes interdits.
  - `RG-049` - surfaces CSS legacy classees.
  - `RG-050` - suite design-system anti-drift executable.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - hors surface frontend design-system.
- Required regression evidence:
  - `npm run test -- design-system`, `npm run lint`, validation des allowlists.
- Allowed differences:
  - Ajout de tests, allowlists exactes et snapshots d'exceptions.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Une suite design-system execute les guards statiques principaux. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`. |
| AC2 | Les exceptions hardcoded values ont une entree exacte. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- design-system`. |
| AC3 | La garde namespaces tokens est incluse. | Evidence profile: `ast_architecture_guard`; command: `npm run test -- design-system`. |
| AC4 | La garde inline styles est incluse. | Evidence profile: `ast_architecture_guard`; command: `npm run test -- design-system`. |
| AC5 | La garde fallbacks CSS est incluse. | Evidence profile: `ast_architecture_guard`; command: `npm run test -- design-system`. |
| AC6 | La garde typographie est incluse. | Evidence profile: `ast_architecture_guard`; command: `npm run test -- design-system`. |
| AC7 | Le lint frontend reste passant avec les nouveaux tests. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inspecter les registres et tests crees par `CS-026` a `CS-031` (AC: AC1)
- [ ] Task 2 - Creer la suite design-system et l'allowlist exacte (AC: AC1, AC2)
- [ ] Task 3 - Ajouter la garde namespaces tokens (AC: AC3)
- [ ] Task 4 - Ajouter les gardes inline, fallback et typographie (AC: AC4, AC5, AC6)
- [ ] Task 5 - Executer lint et tests cibles (AC: AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/tests/theme-tokens.test.ts`.
  - Les registres produits par `CS-026` a `CS-031`.
- Do not recreate:
  - Une allowlist concurrente par test.
  - Un parser different pour chaque categorie quand un helper commun suffit.
- Shared abstraction allowed only if:
  - Elle est limitee aux tests et partage la lecture de fichiers CSS/TSX.

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

- exception sans fichier exact
- snapshot global qui accepte toutes les derives courantes
- dependance externe pour parser ce que TypeScript ou regex ciblee couvre deja

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Suite anti-drift design-system | `frontend/src/tests/design-system-guards.test.ts` | tests disperses non lies aux registres |
| Exceptions design-system | `frontend/src/tests/design-system-allowlist.ts` | snapshot implicite non source |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/design-system-guards.test.ts` - suite anti-drift.
- `frontend/src/tests/design-system-allowlist.ts` - exceptions exactes.
- `frontend/src/tests/theme-tokens.test.ts` - raccordement ou reutilisation.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture principale.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/pages` - aucune migration applicative dans cette story.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- design-system
npm run test -- theme-tokens
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-032-ajouter-guards-anti-drift-design-system/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-032-ajouter-guards-anti-drift-design-system/00-story.md
```

## 22. Regression Risks

- Risk: la suite accepte trop d'exceptions initiales.
  - Guardrail: chaque exception doit citer fichier, symbole et story source.
- Risk: les guards dupliquent la logique des stories precedentes.
  - Guardrail: reutilisation des registres et helpers de test.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Do not use this story to migrate application CSS.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-007` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-007` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
