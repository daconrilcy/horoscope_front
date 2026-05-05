# Story CS-047 realigner-guard-visual-smoke-typographie-tokenisee: Realigner le guard visual-smoke sur la typographie tokenisee

Status: ready-to-dev

## 1. Objective

Corriger a 100% le drift du guard `visual-smoke`.
La suite Vitest complete doit valider le contrat typographique tokenise actuel,
sans reintroduire les anciennes valeurs hardcodees dans le CSS applicatif.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-001`
- Reason for change: `F-002` indique que `npm run test` et `npm run test -- visual-smoke` echouent.
  Le test attend encore `18px`, `12px` et `500` alors que `App.css` utilise les tokens typographiques.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/tests`
- In scope:
  - Mettre a jour `frontend/src/tests/visual-smoke.test.tsx` pour verifier le contrat typographique canonique tokenise.
  - Remplacer les assertions obsoletees `font-size: 18px`, `font-size: 12px` et `font-weight: 500` par une verification liee aux tokens ou a leur resolution deterministe.
  - Conserver les checks d'opacite existants.
- Out of scope:
  - Modifier `frontend/src/App.css` pour satisfaire l'ancien test.
  - Refaire le design, la hierarchie typographique ou les tokens.
  - Reduire les fallbacks CSS, styles inline ou valeurs hardcodees hors test.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-046` ou `RG-050`.
  - Ne pas reintroduire `font-size: 18px`, `font-size: 12px` ou `font-weight: 500` comme contrat nominal.
  - Ne pas supprimer les assertions d'opacite.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story realigne un guard de test sur le contrat runtime/design-system canonique.
- Behavior change allowed: no
- Behavior change constraints:
  - Aucun comportement produit, route, composant ou style applicatif ne doit changer.
  - Seul le test doit evoluer pour verifier le bon contrat.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le contrat canonique ne peut pas etre resolu depuis les tokens existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le test doit verifier le contrat effectif des tokens typographiques rendus. |
| Baseline Snapshot | yes | Le drift doit etre capture avant/apres pour prouver que seules les assertions obsoletees changent. |
| Ownership Routing | no | Aucun proprietaire de code n'est deplace. |
| Allowlist Exception | yes | Les assertions legacy doivent etre retirees sans creer d'exception de test. |
| Contract Shape | no | Aucun API, DTO, schema ou type public n'est modifie. |
| Batch Migration | no | Le scope est un fichier de test unique. |
| Reintroduction Guard | yes | Le test doit echouer si le contrat retombe sur les literals obsoletes. |
| Persistent Evidence | yes | Le resultat des assertions before/after doit rester auditables dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/visual-smoke.test.tsx`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/App.css`
  - rendu DOM exerce par `frontend/src/tests/visual-smoke.test.tsx`
- Secondary evidence:
  - `frontend/src/styles/typography-roles.md`
  - `npm run test -- visual-smoke`
- Static scans alone are not sufficient for this story because:
  - Le test doit prouver la valeur rendue ou le token attendu, pas seulement l'absence d'un literal dans le fichier.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-047-realigner-guard-visual-smoke-typographie-tokenisee/visual-smoke-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-047-realigner-guard-visual-smoke-typographie-tokenisee/visual-smoke-after.md`
- Expected invariant:
  - Seules les assertions typographiques obsoletees changent; les checks d'opacite restent presents.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: aucun owner applicatif ne change; le guard consomme seulement les owners design-system existants.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/visual-smoke.test.tsx` | anciennes assertions typo | Contrat obsolete signale par F-002. | A retirer; aucune exception durable. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: one test file is updated; no multi-surface migration is performed.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before snapshot | `visual-smoke-before.md` | Capturer les assertions obsoletees et l'echec `visual-smoke`. |
| After snapshot | `visual-smoke-after.md` | Prouver le passage des tests et le maintien des checks d'opacite. |

## 4i. Reintroduction Guard

- Guard target: `frontend/src/tests/visual-smoke.test.tsx` typography assertions.
- Architecture guard against reintroduction required: the visual smoke test must assert tokenized or deterministically resolved token values.
- Guard evidence: Evidence profile: `test_guard`; `npm run test -- visual-smoke`, `npm run test`, and a scan proving obsolete typography assertions are gone.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-002` - full Vitest and isolated visual-smoke fail on obsolete typography expectations.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-001` - candidate requires token-aware assertions and preserved opacity checks.
- Evidence 3: `frontend/src/tests/visual-smoke.test.tsx` - file identified as the exhaustive file to modify.
- Evidence 4: `frontend/src/styles/design-tokens.css` - token source to inspect before choosing assertion strategy.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- `visual-smoke.test.tsx` validates the tokenized typography contract instead of obsolete hardcoded values.
- Existing opacity assertions remain present and meaningful.
- `npm run test -- visual-smoke` and `npm run test` pass without changing production CSS.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespaces remain canonical.
  - `RG-046` - semantic typography tokens/roles are canonical for migrated typography.
  - `RG-050` - anti-drift tests must stay executable.
- Non-applicable invariants:
  - `RG-047` - inline styles are not modified.
  - `RG-048` - CSS fallback registries are not modified.
  - `RG-049` - legacy selectors are not modified.
- Required regression evidence:
  - `npm run test -- visual-smoke`, `npm run test`, `npm run test -- design-system theme-tokens`.
- Allowed differences:
  - Test assertions may move from raw literals to token names or deterministic resolved token values.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le test ne conserve plus les anciennes assertions typo litterales. | Evidence profile: `negative_scan`; `rg -n "18px|12px|500" src/tests/visual-smoke.test.tsx`. |
| AC2 | Les nouvelles assertions typo utilisent le contrat tokenise. | Evidence profile: `runtime_guard`; `npm run test -- visual-smoke`. |
| AC3 | Les assertions d'opacite existantes restent couvertes. | Evidence profile: `test_guard`; scan `opacity` plus `npm run test -- visual-smoke`. |
| AC4 | Full frontend Vitest no longer fails because of the visual-smoke drift. | Evidence profile: `frontend_test`; `npm run test` passes. |
| AC5 | Design-system guards still pass after the test realignment. | Evidence profile: `architecture_guard`; `npm run test -- design-system theme-tokens`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inspecter le test, les tokens et `App.css` avant edition (AC: AC1, AC2)
- [ ] Task 2 - Capturer `visual-smoke-before.md` avec les assertions actuelles et l'echec cible (AC: AC1, AC4)
- [ ] Task 3 - Remplacer uniquement les assertions typographiques obsoletees par un contrat token-aware (AC: AC1, AC2)
- [ ] Task 4 - Verifier que les assertions d'opacite sont intactes (AC: AC3)
- [ ] Task 5 - Capturer `visual-smoke-after.md`, executer les tests et scans requis (AC: AC1, AC2, AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` for typography token names/values.
  - Existing helper style in `visual-smoke.test.tsx` if present.
- Do not recreate:
  - Un parseur de tokens ad hoc si le test peut lire les styles calcules.
  - Un second fichier de visual-smoke pour contourner le test existant.
- Shared abstraction allowed only if:
  - Elle remplace une duplication reelle dans les tests et reste locale au harnais de test.

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

- Reintroduire `font-size: 18px`, `font-size: 12px` ou `font-weight: 500` comme expected nominal.
- Modifier `frontend/src/App.css` pour revenir aux literals.
- Supprimer les checks d'opacite pour faire passer le test.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens typographiques globaux | `frontend/src/styles/design-tokens.css` | literals dans tests |
| Verification visual-smoke | `frontend/src/tests/visual-smoke.test.tsx` | assertions obsoletees non tokenisees |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/App.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/typography-roles.md`
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/visual-smoke.test.tsx` - realignement des assertions typographiques.
- `_condamad/stories/CS-047-realigner-guard-visual-smoke-typographie-tokenisee/visual-smoke-before.md` - baseline du drift.
- `_condamad/stories/CS-047-realigner-guard-visual-smoke-typographie-tokenisee/visual-smoke-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/visual-smoke.test.tsx` - test cible.
- `frontend/src/tests/design-system-guards.test.ts` - guard design-system existant a executer sans modification attendue.
- `frontend/src/tests/theme-tokens.test.ts` - guard tokens existant a executer sans modification attendue.

Files not expected to change:

- `frontend/src/App.css` - le CSS tokenise est le contrat a verifier, pas a revert.
- `frontend/src/styles/design-tokens.css` - aucune creation de token.
- `backend/` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- visual-smoke
npm run test -- design-system theme-tokens
npm run test
rg -n "18px|12px|font-weight.*500" src/tests/visual-smoke.test.tsx
rg -n "opacity" src/tests/visual-smoke.test.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-047-realigner-guard-visual-smoke-typographie-tokenisee/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-047-realigner-guard-visual-smoke-typographie-tokenisee/00-story.md
```

## 22. Regression Risks

- Risk: le test passe en supprimant des assertions utiles.
  - Guardrail: AC3 exige la presence et l'execution des checks d'opacite.
- Risk: le test encode un nouveau literal non canonique.
  - Guardrail: AC2 exige un lien aux tokens ou a leur resolution deterministe.
- Risk: la correction masque la regression globale.
  - Guardrail: AC4 exige `npm run test` complet.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-002` - current failing behavior.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
