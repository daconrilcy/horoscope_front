# Story CS-050 migrer-lot-prioritaire-valeurs-visuelles-hardcodees: Migrer un lot prioritaire de valeurs visuelles hardcodees

Status: ready-to-dev

## 1. Objective

Migrer a 100% un cluster produit borne de valeurs visuelles et typographiques hardcodees issues de `F-005`.
La story exige compteurs before/after, reutilisation prioritaire des tokens/roles existants,
et documentation de toute nouvelle ownership semantique.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-004`
- Reason for change: 107 fichiers applicatifs contiennent encore des signaux visuels hardcodes qui concurrencent les tokens semantiques.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Choisir un cluster coherent unique parmi prediction components, shared UI primitives, ou admin pages.
  - Traiter 100% des valeurs hardcodees du cluster choisi pour couleurs, spacing, radius, shadow et typographie.
  - Reutiliser tokens, variables et roles existants avant toute creation.
  - Documenter compteurs before/after et toute extension dans `token-namespace-registry.md` ou `typography-roles.md`.
- Out of scope:
  - Traiter les 107 fichiers.
  - Refondre les composants ou changer l'UX.
  - Reduire les fallbacks CSS ou styles inline sauf si directement inclus comme valeur du cluster.
- Explicit non-goals:
  - Ne pas affaiblir `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de token pour une valeur unique.
  - Ne pas corriger du style hors cluster.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot multi-fichiers de literals vers owners canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent ou converger explicitement vers un token/role documente.
  - Aucune logique React, API, route ou contenu produit ne change.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: un literal a plusieurs mappings plausibles ou encode une decision produit non documentee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards theme/design-system valident les tokens et roles. |
| Baseline Snapshot | yes | Les compteurs du cluster sont indispensables. |
| Ownership Routing | yes | Les decisions visuelles doivent appartenir aux tokens/roles/registres. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre explicites. |
| Contract Shape | no | Aucun contrat API ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un cluster multi-fichiers. |
| Reintroduction Guard | yes | Les literals migres ne doivent pas revenir non classes. |
| Persistent Evidence | yes | Les decisions before/after doivent rester auditables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
- Secondary evidence:
  - Scans cibles du cluster pour couleurs, dimensions, shadows, radius et typographie.
- Static scans alone are not sufficient for this story because:
  - Ils ne prouvent pas que le literal a ete route vers le bon owner canonique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - Le cluster choisi diminue ses literals hardcodes; chaque literal conserve a une classification et une condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleur reusable | `design-tokens.css` + `token-namespace-registry.md` | literal local repete |
| Typographie reusable | `typography-roles.md` | declaration CSS repetee |
| Spacing/radius/shadow recurrent | variables/tokens existants | valeur magique locale |
| Exception unique | `hardcoded-values-after.md` | exception implicite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `hardcoded-values-after.md` | literals conserves du cluster | Valeur unique, blocker ou decision produit. | Must include sortie or permanence decision. |
| `frontend/src/styles/token-namespace-registry.md` | nouveau token | Ownership semantique durable. | Permanent only if reusable. |
| `frontend/src/styles/typography-roles.md` | nouveau role | Role typographique durable. | Permanent only if reusable. |

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
| Chosen F-005 cluster | hardcoded visual values | tokens, roles, or semantic extension | cluster files | theme/design guards | counts | ambiguous mapping |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before count | `hardcoded-values-before.md` | Capturer cluster, compteurs, literals et mapping propose. |
| After count | `hardcoded-values-after.md` | Prouver reduction, mappings effectifs et exceptions finales. |

## 4i. Reintroduction Guard

- Guard target: literals migres du cluster et namespaces/roles non classes.
- Architecture guard against reintroduction required: `npm run test -- design-system theme-tokens` and targeted scans must fail or flag drift.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus before/after artifacts.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-005` - 107 application files still contain hardcoded visual or typography signals.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-004` - recommends one bounded product-surface batch.
- Evidence 3: `frontend/src/styles/token-namespace-registry.md` - token ownership registry.
- Evidence 4: `frontend/src/styles/typography-roles.md` - typography role registry.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- Un cluster prioritaire nomme est migre jusqu'a decision finale de 100% de ses literals.
- Les mappings clairs utilisent les owners existants.
- Les exceptions et extensions semantiques sont documentees, testees et auditables.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespaces remain classified.
  - `RG-045` - migrated hardcoded values must not return unclassified.
  - `RG-046` - typography roles are canonical for repeated typography.
  - `RG-050` - anti-drift tests must remain executable.
- Non-applicable invariants:
  - `RG-047` - inline style reduction is covered by `CS-049`.
  - `RG-048` - CSS fallback reduction is covered by `CS-048`.
  - `RG-049` - legacy selector extinction is covered by `CS-051`.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens`, `npm run lint`, targeted cluster scans, before/after artifacts.
- Allowed differences:
  - Documented convergence toward semantic token/role values.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster choisi est explicite. | Evidence profile: `scope_guard`; `rg -n "Cluster|Files" hardcoded-values-before.md`. |
| AC2 | 100% des literals du cluster ont une decision finale. | Evidence profile: `baseline_snapshot`; `rg -n "TODO|TBD|unclassified" hardcoded-values-after.md`. |
| AC3 | Les values avec mapping clair migrent vers tokens/roles existants. | Evidence profile: `architecture_guard`; `npm run test -- design-system theme-tokens`. |
| AC4 | Toute extension semantique durable est documentee. | Evidence profile: `registry_guard`; `npm run test -- theme-tokens design-system`. |
| AC5 | Les compteurs du cluster diminuent. | Evidence profile: `before_after`; `rg -n "Total|before|after" hardcoded-values-*.md`. |
| AC6 | Le frontend reste valide. | Evidence profile: `frontend_quality`; `npm run lint` and targeted component/page tests when existing. |

## 8. Implementation Tasks

- [ ] Task 1 - Selectionner un seul cluster prioritaire et capturer le baseline exhaustif (AC: AC1, AC2)
- [ ] Task 2 - Mapper chaque literal vers owner canonique, exception ou blocker (AC: AC2, AC3)
- [ ] Task 3 - Migrer les mappings clairs vers tokens/roles existants (AC: AC3)
- [ ] Task 4 - Documenter extensions et exceptions finales (AC: AC4, AC5)
- [ ] Task 5 - Executer les guards, lint et tests cibles (AC: AC3, AC4, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - Variables locales deja presentes dans le cluster.
- Do not recreate:
  - Token pour valeur unique.
  - Role typographique duplicatif.
  - Utility globale speculative.
- Shared abstraction allowed only if:
  - Elle supprime une repetition mesurable dans le cluster et son owner est documente.

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

- Nouveau namespace token absent du registre.
- Nouveau role absent de `typography-roles.md`.
- Literal migre qui reste ou revient sans justification.

## 11. Removal Classification Rules

Classification must be deterministic:

- `migrate`: clear canonical token/role exists.
- `keep-classified`: unique or externally constrained literal with documented reason.
- `needs-user-decision`: ambiguous product/design decision.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `migrate` | `replace` | Must use canonical owner. |
| `keep-classified` | `keep` | Must be documented in after artifact. |
| `needs-user-decision` | `needs-user-decision` | Must block that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- `_condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/hardcoded-values-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens frontend | `design-tokens.css` + `token-namespace-registry.md` | repeated literals |
| Typography roles | `typography-roles.md` | repeated font declarations |
| Remaining exceptions | `hardcoded-values-after.md` | implicit local values |

## 14. Delete-Only Rule

Items classified as `migrate` must be replaced by canonical owner, not kept as parallel literal.

Forbidden:

- keeping the literal and adding a token beside it
- near-equivalent token without documented mapping
- compatibility alias to preserve a hardcoded value

## 15. External Usage Blocker

If a literal is tied to external branding, third-party visual contract, or product decision, classify it `needs-user-decision` or `keep-classified` with proof before changing it.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- Representative cluster candidate: `frontend/src/components/prediction/DayPredictionCard.css`
- Representative cluster candidate: `frontend/src/components/ui/Button/Button.css`
- Representative cluster candidate: `frontend/src/pages/admin/AdminDashboardPage.css`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `unknown until repo inspection` plus assumption risk: the exact CSS/TSX files depend on the selected single cluster.
- `frontend/src/styles/token-namespace-registry.md` - only if a reusable token namespace extension is introduced.
- `frontend/src/styles/typography-roles.md` - only if a reusable typography role is introduced.
- `_condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/hardcoded-values-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- Existing component/page tests for the chosen cluster when present.

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- Fichiers hors cluster choisi - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|font-size:|font-weight:|box-shadow:" selected-cluster-files
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-050-migrer-lot-prioritaire-valeurs-visuelles-hardcodees/00-story.md
```

## 22. Regression Risks

- Risk: cluster trop large et inacheve.
  - Guardrail: AC1 limite a un cluster unique et AC2 exige 100% des decisions.
- Risk: token near-equivalent modifie le rendu.
  - Guardrail: user decision required on ambiguity.
- Risk: nouvelle dette de tokens.
  - Guardrail: AC4 et RG-044 imposent registre canonique.

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

- `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-005` - current broad file list.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
