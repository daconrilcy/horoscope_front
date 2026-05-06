# Story CS-064 retirer-dernier-fallback-css-migration-only: Retirer le dernier fallback CSS migration-only

Status: ready-to-dev

## Objective

Retirer le fallback CSS migration-only `var(--glass-heavy, #1a1a1a)` de `AdminEntitlementsPage.css` apres preuve de token canonique.
Les deux fallbacks dynamiques `--usage-progress` restent classes comme ponts runtime tant que la progression est injectee par propriete CSS.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-001`
- Reason for change: supprimer la derniere exception fallback migration-only sans affaiblir les guards design-system.

## Domain Boundary

- Domain: `frontend/src/styles`
In scope:
- Inspecter `--glass-heavy` et son owner canonique pour la surface admin entitlement.
- Retirer le fallback literal local de `frontend/src/pages/admin/AdminEntitlementsPage.css` si le token est garanti.
- Synchroniser `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts`.
- Conserver les entrees `--usage-progress` comme exceptions dynamiques si le pont runtime reste requis.

Out of scope:
- Refonte visuelle de la page admin entitlement.
- Retrait global de `--glass-heavy` comme token si des consommateurs restent actifs.
- Migration des styles inline, selectors legacy ou valeurs hardcodees hors fallback cible.

Explicit non-goals:
  - Ne pas changer `RG-048` ni `RG-050`.
  - Ne pas supprimer les fallbacks `--usage-progress` sans changement du pont runtime.
  - Ne pas ajouter de fallback `var(--token, literal)` local.

## Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: le fallback local migration-only est une surface supprimable apres preuve que le token canonique couvre le comportement.
- Behavior change allowed: constrained
- Behavior change constraints:
  - La couleur effective de la surface admin entitlement doit rester stable si `--glass-heavy` est canonique.
  - Les seules differences autorisees sont la disparition du fallback literal et la baisse des compteurs d'allowlist.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: `--glass-heavy` n'est pas declare dans une source canonique ou si le token doit etre retire entierement.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les guards Vitest et le registre executable sont la source verifiee des fallbacks actifs |
| Baseline Snapshot | yes | le compteur before/after des fallbacks CSS doit prouver une baisse ciblee |
| Ownership Routing | yes | `--glass-heavy` doit avoir un owner de token avant suppression du fallback local |
| Allowlist Exception | yes | les allowlists markdown et TypeScript doivent rester exactes |
| Contract Shape | no | aucun type, API, DTO ou contrat public n'est modifie |
| Batch Migration | no | un seul fallback migration-only est cible |
| Reintroduction Guard | yes | le guard `css-fallback` doit echouer si le fallback revient non classe |
| Persistent Evidence | yes | le dossier de story doit conserver le baseline before/after des fallbacks |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/css-fallback-policy.test.ts` execute par Vitest.
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/styles/css-fallback-allowlist.md`
- Secondary evidence:
  - `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - les exceptions restantes doivent etre comparees au registre executable, pas seulement detectees.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/css-fallbacks-after.md`
- Expected invariant:
  - seul `--glass-heavy` peut sortir des allowlists; les deux entrees `--usage-progress` restent presentes sauf changement runtime documente.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token global de surface glass | `frontend/src/styles/design-tokens.css` ou registre canonique declare | fallback local dans `AdminEntitlementsPage.css` |
| Exception fallback CSS | `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts` | exception implicite dans un test local |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | `--usage-progress` | pont runtime dynamique | permanent tant que la progression est injectee au runtime |
| `frontend/src/tests/design-system-allowlist.ts` | `--usage-progress` | miroir executable exact | permanent tant que la progression est injectee au runtime |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

- Batch migration: not applicable
- Reason: one exact fallback is removed, not a multi-batch consumer migration.

## Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| fallback baseline | `_condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/css-fallbacks-before.md` | prouver l'etat initial des fallbacks |
| fallback result | `_condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/css-fallbacks-after.md` | prouver que seul le fallback migration-only a ete retire |

## Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `var(--glass-heavy, #1a1a1a)`
- nouvelle entree fallback non classee dans `frontend/src/styles/css-fallback-allowlist.md`
- deterministic source: forbidden symbols

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system theme-tokens` checks fallback classification.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-001` - le candidat cible `--glass-heavy` et conserve `--usage-progress`.
- Evidence 2: `frontend/src/pages/admin/AdminEntitlementsPage.css` - contient `background: var(--glass-heavy, #1a1a1a);`.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - classe `--glass-heavy` comme `migration-only` et `--usage-progress` comme `dynamic`.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - contient les trois exceptions fallback executables.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants `RG-048` et `RG-050` consultes avant cadrage.

## Target State

- `AdminEntitlementsPage.css` consomme `--glass-heavy` ou son remplacement canonique sans fallback literal local.
- Les allowlists markdown et TypeScript ne listent plus `--glass-heavy` si le token est garanti.
- Les deux exceptions `--usage-progress` restent documentees et executablement verifiees.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-048` - la story supprime un fallback CSS et doit garder les exceptions restantes exactes.
  - `RG-050` - les allowlists design-system doivent rester executees par Vitest.
- Non-applicable invariants:
  - `RG-047` - aucun style inline TSX n'est modifie.
  - `RG-049` - aucun selector ou alias legacy n'est modifie.
- Required regression evidence:
  - `npm run test -- css-fallback design-system theme-tokens`
  - scan cible des fallbacks CSS restants.
- Allowed differences:
  - l'entree `--glass-heavy` peut disparaitre des allowlists; `--usage-progress` doit rester sauf preuve runtime contraire.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline cible `--glass-heavy`. | Evidence profile: `baseline_before_after_diff`; `rg -n "var\\(" src -g "*.css"` + before artifact |
| AC2 | `var(--glass-heavy, #1a1a1a)` disparait. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "glass-heavy" src/pages/admin/AdminEntitlementsPage.css` + test |
| AC3 | Les allowlists restent synchronisees. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback design-system` |
| AC4 | `--usage-progress` reste un pont runtime classe. | Evidence profile: `allowlist_register_validated`; AST guard `npm run test -- css-fallback` + after artifact |
| AC5 | Aucun nouveau fallback CSS non classe n'est introduit. | Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback` + `rg -n "var\\(" src` |

## Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire before des fallbacks CSS et le stocker dans `css-fallbacks-before.md`. (AC: AC1)
- [ ] Task 2 - Verifier l'ownership de `--glass-heavy` ou du token de remplacement avant d'editer `AdminEntitlementsPage.css`. (AC: AC2)
- [ ] Task 3 - Retirer uniquement le fallback literal `#1a1a1a` du fichier cible. (AC: AC2, AC5)
- [ ] Task 4 - Synchroniser `css-fallback-allowlist.md` et `design-system-allowlist.ts` sans toucher aux exceptions `--usage-progress`. (AC: AC3, AC4)
- [ ] Task 5 - Capturer l'inventaire after et executer les validations frontend. (AC: AC1, AC3, AC4, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/css-fallback-allowlist.md` pour la classification markdown.
  - `frontend/src/tests/design-system-allowlist.ts` pour l'allowlist executable.
  - `frontend/src/tests/css-fallback-policy.test.ts` pour le guard principal.
- Do not recreate:
  - un second registre de fallbacks.
  - une constante locale du fallback `#1a1a1a`.
- Shared abstraction allowed only if:
  - non applicable; aucun nouveau helper n'est attendu.

## No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `var(--glass-heavy, #1a1a1a)`
- nouveau `var(--token, literal)` non liste dans `frontend/src/styles/css-fallback-allowlist.md`

## Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: token ou pont runtime declare comme source active.
- `external-active`: fallback documente comme requis par surface externe ou produit.
- `historical-facade`: fallback local conservant une ancienne surface de migration.
- `dead`: fallback sans consommateur ni necessite runtime apres verification du token.
- `needs-user-decision`: ownership du token ou retrait complet ambigu.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/fallback-removal-audit.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Glass heavy background token | `frontend/src/styles/design-tokens.css` or registry-confirmed token owner | local fallback `#1a1a1a` |
| Dynamic usage progress fallback | runtime CSS custom property bridge | none while classified dynamic |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- wrapper
- replacing `#1a1a1a` with another literal fallback
- adding a compatibility alias to preserve fallback behavior
- moving the fallback to a shared CSS file
- re-export

## External Usage Blocker

If `--glass-heavy` is classified `external-active`, it must not be deleted.
If it is not canonical or must be retired entirely, the dev agent must stop and record a user decision.

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`

## Expected Files to Modify

Likely files:

- `frontend/src/pages/admin/AdminEntitlementsPage.css` - retirer le fallback literal si le token est garanti.
- `frontend/src/styles/css-fallback-allowlist.md` - retirer l'entree `--glass-heavy` si elle n'est plus necessaire.
- `frontend/src/tests/design-system-allowlist.ts` - synchroniser l'allowlist executable.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - ajuster seulement si le contrat exact change.

Files not expected to change:

- `backend/` - aucun contrat backend n'est touche.
- `frontend/src/components/**` - aucune migration inline ou composant n'est dans le scope.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- css-fallback design-system theme-tokens
npm run lint
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-064-retirer-dernier-fallback-css-migration-only/00-story.md
```

## Regression Risks

- Risk: suppression d'un fallback encore necessaire si `--glass-heavy` n'est pas declare dans le theme actif.
  - Guardrail: `npm run test -- theme-tokens` et audit d'ownership avant suppression.
- Risk: derive des exceptions `--usage-progress`.
  - Guardrail: `npm run test -- css-fallback design-system` et comparaison before/after.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-001` - source du candidat.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-048` et `RG-050`.
- `frontend/src/styles/css-fallback-allowlist.md` - registre de fallbacks CSS.
- `frontend/src/tests/design-system-allowlist.ts` - allowlist executable.
