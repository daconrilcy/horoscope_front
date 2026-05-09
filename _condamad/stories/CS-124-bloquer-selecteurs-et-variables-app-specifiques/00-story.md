# Story CS-124 bloquer-selecteurs-et-variables-app-specifiques: Bloquer les selecteurs et variables App specifiques

Status: done

## 1. Objective

Ajouter la garde finale qui interdit la reintroduction de selecteurs et variables `--app-*` specifiques dans `App.css`.
Cette story ferme l'audit apres CS-121, CS-122 et CS-123.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-004`
- Reason for change: `F-004` montre que les guards actuels protegent les valeurs mais pas la specificite des noms.

## 3. Domain Boundary

- Domain: frontend-app-css-standardization
- In scope:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts` si exceptions exactes
  - `frontend/src/App.css`
  - registres CSS si exceptions temporaires
- Out of scope:
  - nouvelle migration fonctionnelle hors reliquats indispensables a la garde
  - CSS hors `App.css`
  - backend
- Explicit non-goals:
  - pas de wildcard
  - pas de seuil permissif du type "moins de N violations"
  - pas d'exception permanente page-specific sans decision utilisateur

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story durcit les guards anti-drift apres migration.
- Behavior change allowed: no
- Behavior change constraints:
  - aucun rendu ne doit changer
  - les reliquats bloquants doivent etre classes ou transformes par les primitives deja creees
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une exception permanente page-specific est demandee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests design-system doivent etre la source executable. |
| Baseline Snapshot | yes | Capturer les reliquats avant garde stricte. |
| Ownership Routing | yes | Toute exception doit avoir owner et exit condition. |
| Allowlist Exception | yes | La garde depend d'exceptions exactes si reliquats restent. |
| Contract Shape | no | Aucun contrat API. |
| Batch Migration | no | Migration deja couverte par CS-121 a CS-123. |
| Reintroduction Guard | yes | Objectif principal. |
| Persistent Evidence | yes | Evidence finale de fermeture de l'audit. |

## 4b. Runtime Source of Truth

- Primary source of truth: AST guard `frontend/src/tests/design-system-guards.test.ts`.
- Secondary evidence: scans `rg` sur `frontend/src/App.css`.
- Static scans alone are not sufficient because la garde Vitest doit devenir le controle canonique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/app-specificity-guard-before.md`
- Comparison after implementation: `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/app-specificity-guard-after.md`
- Expected invariant: zero violation non allowlistee et aucune allowlist sans expiry.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| App class names | generic primitives from CS-121 | page/feature/service selectors in App.css |
| App custom properties | generic semantic `--app-*` roles | `--app-astrologer-*`, `--app-consultation-*`, etc. |
| Exceptions | exact allowlist with owner and expiry | broad threshold or regex wildcard |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | exact residual names only | temporary blocker | exit condition: exit story or user decision before review |

Rules: no wildcard, no folder-wide exception, no count threshold, no permanent page-specific exception without explicit user decision.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: this is the final guard story; migration batches are owned by CS-121, CS-122 and CS-123.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before | `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/app-specificity-guard-before.md` | residual inventory |
| after | `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/app-specificity-guard-after.md` | guard closure |
| final evidence | `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/generated/10-final-evidence.md` | validation output |

## 4i. Reintroduction Guard

- Guard source: `frontend/src/tests/design-system-guards.test.ts`
- Forbidden examples:
  - class selectors in `App.css` containing audited domain words unless exact allowlist with expiry
  - variables `--app-*` containing audited domain words unless exact allowlist with expiry
  - `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only`
- Guard evidence: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-004`
- Closure proof required: strict guard plus zero unclassified violations.
- Known residual in-domain work: none allowed when this story is done.
- Deferred non-domain concerns: Vite chunk-size warning.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/01-evidence-log.md#E-010` - `OLD` comment and fallback vocabulary hits require classification.
- Evidence 2: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/01-evidence-log.md#E-011` - current guard does not block page-specific names.
- Evidence 3: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/02-finding-register.md#F-004` - missing guard.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes.

## 6. Target State

- A deterministic test fails on any new unclassified App page-specific selector or variable.
- All residual exceptions are exact and expiring.
- No `OLD` or No Legacy vocabulary remains unclassified in active `App.css`.
- The audit closure map has no residual in-domain implementation work.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - namespaces classifies.
  - `RG-045` - valeurs migrees protegees.
  - `RG-046` - typographie canonique.
  - `RG-047` - pas de style inline statique.
  - `RG-048` - pas de fallback CSS non classe.
  - `RG-049` - surfaces legacy classees.
  - `RG-050` - suite anti-drift active.
  - `RG-059`, `RG-061` - App.css garde.
- Non-applicable invariants:
  - `RG-054` - routes admin legacy hors scope.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run lint`
- Allowed differences:
  - none for guard violations; exceptions must be exact and expiring.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline des reliquats page-specific App. | Evidence profile: `baseline_before_after_diff`; `rg -n "(dashboard|astrologer|consultation|settings)" frontend/src/App.css`. |
| AC2 | Guard Vitest bloque les noms App specifiques. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system` checks AST guard. |
| AC3 | Toute exception est expiree. | Evidence profile: `allowlist_register_validated`; `rg -n "APP_CSS|expiry|exit" frontend/src/tests`. |
| AC4 | No Legacy vocabulary non classe absent de `App.css`. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "OLD|legacy|alias|compat|shim" frontend/src/App.css`. |
| AC5 | Suite design-system passe. | Evidence profile: `runtime_source_of_truth`; `npm run test -- design-system visual-smoke` and `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline de specificite App. (AC: AC1)
- [ ] Task 2 - Implementer la garde stricte dans `design-system-guards.test.ts`. (AC: AC2)
- [ ] Task 3 - Classer ou transformer les reliquats No Legacy. (AC: AC3, AC4)
- [ ] Task 4 - Persister l'after et final evidence. (AC: AC1, AC5)
- [ ] Task 5 - Executer validations et fermer la map d'audit. (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse helpers de parsing existants dans `design-system-guards.test.ts`.
- Reuse `design-system-allowlist.ts` only for exact exceptions.
- Do not create a second guard file for the same policy.

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

- wildcard allowlist
- count threshold
- `PASS with limitation`
- unclassified domain words in `App.css`
- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| App specificity policy | `design-system-guards.test.ts` | manual review only |
| Exceptions | `design-system-allowlist.ts` exact entries | wildcard/count thresholds |
| App class system | CS-121 primitives | page-specific selectors in App.css |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/00-audit-report.md`
- `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md`
- `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/00-story.md`
- `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/00-story.md`
- `frontend/src/App.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/design-system-guards.test.ts` - garde stricte.
- `frontend/src/tests/design-system-allowlist.ts` - exceptions exactes avec expiry.
- `frontend/src/App.css` - classement ou transformation des reliquats bloquants.
- `frontend/src/styles/legacy-style-surface-registry.md` - seulement si une exception legacy exacte est decidee.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`

Files not expected to change:

- `frontend/package.json`
- `backend/**`

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only when explicitly listed here with justification.

## 21. Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/00-story.md
```

## 22. Regression Risks

- Risk: guard trop stricte bloque une exception legitime.
  - Guardrail: exception exacte avec owner, source et expiry.
- Risk: guard trop permissive laisse revenir les noms page-specific.
  - Guardrail: pas de threshold global ni wildcard.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback, compatibility, legacy, migration-only, shim or alias.
- Do not leave hidden residual in-domain work when this story is marked `full-closure`.

## 24. References

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md#SC-004` - source.
- `_condamad/stories/regression-guardrails.md` - invariants.
