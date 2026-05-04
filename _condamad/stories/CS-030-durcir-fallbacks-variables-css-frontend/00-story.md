# Story CS-030 durcir-fallbacks-variables-css-frontend: Durcir les fallbacks de variables CSS frontend

Status: ready-to-dev

## 1. Objective

Classer les usages `var(--token, value)` et reduire les fallbacks CSS qui agissent comme tokens alternatifs caches, en conservant uniquement les exceptions documentees et testees.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-005`
- Reason for change: le finding `F-005` montre 329 fallbacks CSS capables de masquer une absence ou une divergence de token canonique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Inventorier les fallbacks CSS existants.
  - Retirer les fallbacks des tokens canoniques obligatoires.
  - Documenter les exceptions pour tokens externes, migration-only ou compatibility.
  - Ajouter une garde contre les nouveaux fallbacks non classes.
- Out of scope:
  - Redefinir la source canonique des tokens, traitee par `CS-026`.
  - Migrer toutes les valeurs hardcodees, traite par `CS-027`.
  - Changer le rendu produit premium.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas utiliser un fallback pour compenser un token manquant.
  - Ne pas creer une allowlist large par fichier complet.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story durcit une regle d'architecture CSS avec allowlist exacte et garde anti-reintroduction.
- Behavior change allowed: no
- Behavior change constraints:
  - Les fallbacks retires doivent cibler des tokens requis existants.
  - Les exceptions conservees doivent etre documentees avant conservation.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un fallback protege une vraie absence de token dont le statut n'a pas ete tranche par `CS-026`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde doit inspecter les fichiers CSS reels. |
| Baseline Snapshot | yes | Le nombre de fallbacks doit etre compare avant/apres. |
| Ownership Routing | no | L'ownership des tokens vient de `CS-026`. |
| Allowlist Exception | yes | Les fallbacks autorises sont des exceptions exactes. |
| Contract Shape | no | Aucun contrat API ou type frontend n'est touche. |
| Batch Migration | no | Le scope est une classification et une garde, pas un lot multi-surface. |
| Reintroduction Guard | yes | La garde bloque les nouveaux fallbacks non classes. |
| Persistent Evidence | yes | Le registre de fallbacks est une preuve durable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard CSS qui detecte `var(--token, value)` sous `frontend/src`.
  - Commande cible: `npm run test -- css-fallback`.
- Secondary evidence:
  - `rg -n "var\\(--[^,]+," src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Le test doit valider chaque fallback contre un registre exact.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-030-durcir-fallbacks-variables-css-frontend/css-fallbacks-before.md`
- Comparison after implementation: `_condamad/stories/CS-030-durcir-fallbacks-variables-css-frontend/css-fallbacks-after.md`
- Expected invariant: les fallbacks non classes disparaissent et les exceptions restent exactes.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: cette story applique la classification de tokens existante sans changer les owners.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/theme.css` | external token fallback | Surface fournie par navigateur ou integration externe. | Permanent avec justification exacte. |
| `frontend/src/pages/settings/Settings.css` | migration-only token fallback | Dette classee par `CS-026`. | Until migration registry marks canonical target complete. |
| `frontend/src/styles/premium-theme.css` | compatibility alias fallback | Alias documente dans le registre tokens. | Until alias target is migrated. |

Rules:

- no wildcard fallback family without token name;
- no fallback literal for a required canonical token;
- every exception must include file, token and literal;
- every exception must be validated by test.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: aucun lot multi-consommateur n'est requis; chaque fallback est classe ou remplace.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Fallback registry | `frontend/src/styles/css-fallback-allowlist.md` | Classer les fallbacks autorises et leur condition de sortie. |
| Before inventory | `css-fallbacks-before.md` | Capturer les fallbacks initiaux. |
| After inventory | `css-fallbacks-after.md` | Prouver la classification finale. |

## 4i. Reintroduction Guard

- Guard target: nouveau fallback `var(--token, value)` absent de `css-fallback-allowlist.md`.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-007` - 329 usages de fallbacks CSS.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-005` - les fallbacks couvrent plusieurs familles de tokens.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-005` - cette story depend de la classification `SC-001`.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les tokens canoniques requis ne portent plus de fallback literal local.
- Les fallbacks conserves sont exacts, justifies et testes.
- Un nouveau fallback non classe echoue en Vitest.
- Le registre `css-fallback-allowlist.md` indique la condition de sortie des exceptions migration-only.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - la classification des tokens frontend determine les tokens requis.
  - `RG-048` - les fallbacks CSS non classes ne doivent pas revenir.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - hors surface frontend CSS.
- Required regression evidence:
  - Test css-fallback, inventaire avant/apres, `npm run lint`.
- Allowed differences:
  - Retrait des fallbacks pour tokens canoniques existants.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'inventaire initial des fallbacks CSS est persiste. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- css-fallback`. |
| AC2 | Les fallbacks de tokens requis utilisent `var(--token)`. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `npm run test -- css-fallback`. |
| AC3 | Les fallbacks conserves ont une entree exacte. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- css-fallback`. |
| AC4 | Un nouveau fallback non classe fait echouer la garde. | Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback`. |
| AC5 | L'inventaire final prouve uniquement des exceptions classees. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- css-fallback`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire initial des fallbacks (AC: AC1)
- [ ] Task 2 - Creer le registre exact des exceptions (AC: AC3)
- [ ] Task 3 - Remplacer les fallbacks de tokens requis (AC: AC2)
- [ ] Task 4 - Ajouter la garde css-fallback (AC: AC3, AC4)
- [ ] Task 5 - Capturer l'inventaire final et executer lint (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Le registre de namespaces de `CS-026`.
  - `frontend/src/tests/theme-tokens.test.ts` ou un test design-system voisin.
- Do not recreate:
  - Un second registre de tokens.
  - Des fallbacks de substitution pour contourner une valeur absente.
- Shared abstraction allowed only if:
  - Elle parse CSS pour plusieurs gardes design-system.

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

- fallback literal sur token canonique requis
- exception par fichier entier
- token migration-only conserve sans condition de sortie

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Fallbacks CSS autorises | `frontend/src/styles/css-fallback-allowlist.md` | fallback implicite dans CSS |
| Garde fallback | test `css-fallback` | scan manuel d'audit |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/App.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/css-fallback-allowlist.md` - registre exact.
- `frontend/src/tests/css-fallback-policy.test.ts` - garde fallback.
- `frontend/src/**/*.css` - retrait de fallbacks classifies comme non autorises.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - couverture principale.
- `frontend/src/tests/theme-tokens.test.ts` - integration token si la garde y est rattachee.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- css-fallback
rg -n "var\\(--[^,]+," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-030-durcir-fallbacks-variables-css-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-030-durcir-fallbacks-variables-css-frontend/00-story.md
```

## 22. Regression Risks

- Risk: un fallback retiré cache un token absent dans un theme.
  - Guardrail: dependance explicite a la classification `CS-026`.
- Risk: l'allowlist devient trop large.
  - Guardrail: entree exacte par fichier, token et literal.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Confirm `CS-026` token classification before changing required-token fallbacks.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-005` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
