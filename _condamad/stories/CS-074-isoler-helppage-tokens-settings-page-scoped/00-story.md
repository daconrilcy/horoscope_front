# Story CS-074 isoler-helppage-tokens-settings-page-scoped: Isoler HelpPage des tokens page-scoped Settings

Status: ready-to-dev

## Objective

Faire disparaitre la dependance de `HelpPage.css` aux variables `--settings-*`
en la remplacant par des tokens canoniques globaux ou des variables semantiques
propres a HelpPage. La correction doit ajouter une garde executable contre la
consommation de tokens page-scoped hors owner, sans alias, fallback ou
compatibilite transitoire.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-001`
- Reason for change: `F-004` montre que `HelpPage.css` consomme `--settings-card-border` et `--settings-card-shadow-soft`, pourtant owners par `Settings.css`.

## Domain Boundary

- Domain: `frontend/src/pages/HelpPage.css`
- In scope:
  - Remplacer les usages `--settings-card-border` et `--settings-card-shadow-soft` dans `HelpPage.css`.
  - Declarer les nouveaux owners dans `token-namespace-registry.md` uniquement si une variable Help locale ou semantique durable est creee.
  - Ajouter ou etendre une garde qui echoue si un namespace page-scoped est consomme hors fichier owner.
  - Produire des scans before/after `--settings-` pour `HelpPage.css`.
- Out of scope:
  - Converger tous les namespaces `--settings-*`, `--profile-*` ou `--astro-*` restants, couvert par `CS-075`.
  - Migrer les valeurs hardcodees non liees a cette dependance.
  - Refonte visuelle de HelpPage.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-049` ou `RG-050`.
  - Ne pas creer de namespace `compatibility`, `legacy`, `migration-only`, alias, shim ou fallback.
  - Ne pas accepter de `PASS with limitation`: chaque AC doit finir en PASS complet ou bloquer.

## Operation Contract

- Operation type: converge
- Primary archetype: namespace-convergence
- Archetype reason: la story corrige une violation d'ownership de namespace CSS sans changer le comportement produit.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu HelpPage doit rester equivalent hors remplacement par tokens canoniques documentes.
  - Aucun chemin legacy ou alias CSS ne peut etre conserve pour absorber la migration.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: aucun token canonique ou owner Help non legacy ne peut remplacer la valeur sans derive visuelle documentee.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system prouvent l'ownership executable des tokens. |
| Baseline Snapshot | yes | Les scans before/after prouvent la disparition des consommations `--settings-` dans HelpPage. |
| Ownership Routing | yes | La dependance cross-page doit etre routee vers un owner canonique. |
| Allowlist Exception | no | Aucune exception page-scoped hors owner n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route ou type public n'est modifie. |
| Batch Migration | yes | Le scope migre deux usages cross-page vers un owner canonique documente. |
| Reintroduction Guard | yes | La consommation hors owner doit echouer si elle revient. |
| Persistent Evidence | yes | Les scans et decisions doivent rester dans le dossier de story. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
- Secondary evidence:
  - scans `rg` cibles sur `frontend/src/pages/HelpPage.css` et `frontend/src/styles/token-namespace-registry.md`.
- Static scans alone are not sufficient because:
  - le contrat d'ownership doit etre executable par la suite design-system.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-074-isoler-helppage-tokens-settings-page-scoped/settings-token-usage-before.md`.
- Comparison after implementation: `_condamad/stories/CS-074-isoler-helppage-tokens-settings-page-scoped/settings-token-usage-after.md`.
- Expected invariant: `HelpPage.css` contient zero usage `--settings-` apres implementation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Tokens de carte HelpPage | `HelpPage.css` via variables locales semantiques ou tokens globaux `design-tokens.css` | namespace `--settings-*` |
| Ownership page-scoped | fichier page owner declare dans `token-namespace-registry.md` | consommation cross-page non declaree |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception de consommation cross-page n'est autorisee.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Help border | `--settings-card-border` | Help var or global token | `HelpPage.css` | design-system | AC1 scan | no owner |
| Help shadow | `--settings-card-shadow-soft` | Help var or global token | `HelpPage.css` | theme-tokens | AC1 scan | no owner |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before token usage | `settings-token-usage-before.md` | Inventorier les usages `--settings-` dans HelpPage avant modification. |
| After token usage | `settings-token-usage-after.md` | Prouver zero usage `--settings-` dans HelpPage et documenter le remplacement. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: aucun namespace page-scoped ne peut etre reintroduced hors owner declare.
- Deterministic source: forbidden symbols from `token-namespace-registry.md`, `HelpPage.css`, `Settings.css`, et `design-system-guards.test.ts`.
- Required forbidden examples:
  - `var(--settings-card-border)` dans `frontend/src/pages/HelpPage.css`
  - `var(--settings-card-shadow-soft)` dans `frontend/src/pages/HelpPage.css`
- Guard evidence: `npm run test -- design-system theme-tokens`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-004` - `HelpPage.css` depend de tokens Settings.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md#E-011` - scan `--settings-` en echec.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - `RG-044`, `RG-045`, `RG-049` et `RG-050` consultes avant cadrage.

## Target State

- `HelpPage.css` ne consomme plus aucun token `--settings-*`.
- Les remplacements sont canoniques, semantiques et documentes dans l'after.
- Une garde executable bloque toute nouvelle consommation page-scoped hors owner.
- Les validations passent sans limitation.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens doivent rester classes.
  - `RG-045` - les valeurs remplacees ne doivent pas revenir en literals concurrents.
  - `RG-049` - aucun alias legacy CSS ne doit etre cree.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - aucun style inline TSX n'est dans le scope.
  - `RG-048` - aucun fallback CSS ne doit etre touche; tout ajout bloque.
- Required regression evidence:
  - `npm run test -- HelpPage design-system theme-tokens visual-smoke`
  - scan zero-hit `rg -n -- "--settings-" src/pages/HelpPage.css`
- Allowed differences:
  - none

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `HelpPage.css` ne contient plus aucun usage `--settings-*`. | Command `npm run test -- frontend/src/tests/HelpPage.test.tsx`; scan in Validation Plan. |
| AC2 | Les remplacements utilisent un owner canonique. | Evidence profile: `namespace_converged`; command `npm run test -- theme-tokens design-system`. |
| AC3 | La garde cross-page echoue pour un namespace page-scoped consomme hors owner. | Evidence profile: `architecture_guard`; `npm run test -- design-system theme-tokens`. |
| AC4 | Aucun alias CSS n'est ajoute. | Evidence profile: `targeted_forbidden_symbol_scan`; `npm run test -- legacy-style css-fallback`. |
| AC5 | Le rendu HelpPage reste couvert sans limitation. | Evidence profile: `runtime_guard`; `npm run test -- HelpPage visual-smoke` et `npm run lint`. |

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline des usages `--settings-` HelpPage. (AC: AC1)
- [ ] Task 2 - Remplacer les deux usages par tokens canoniques ou variables Help semantiques. (AC: AC1, AC2)
- [ ] Task 3 - Mettre a jour le registre de namespaces seulement si un owner durable est cree. (AC: AC2, AC4)
- [ ] Task 4 - Ajouter ou etendre la garde de consommation page-scoped hors owner. (AC: AC3)
- [ ] Task 5 - Capturer l'after et executer validations, lint et scans. (AC: AC1, AC3, AC4, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`, `frontend/src/styles/token-namespace-registry.md` et les guards design-system existants.
- Do not recreate un token Settings sous un autre nom sans ownership documente.
- Shared abstraction allowed only if elle sert au moins deux surfaces et est documentee comme non legacy.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `--settings-card-border` dans `frontend/src/pages/HelpPage.css`
  - `--settings-card-shadow-soft` dans `frontend/src/pages/HelpPage.css`
  - tout nouveau `legacy`, `alias`, `compat`, `shim`, `fallback`, `migration-only`

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| HelpPage card border and shadow | HelpPage semantic variable or global design token | `--settings-*` consumed by HelpPage |
| Page-scoped token policy | `token-namespace-registry.md` plus design-system guards | ad hoc cross-page CSS consumption |

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-policy.ts`
- `frontend/src/tests/theme-tokens.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/pages/HelpPage.css` - remplacer les usages `--settings-*`.
- `frontend/src/styles/token-namespace-registry.md` - documenter tout owner durable ajoute ou promu.

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts` - garde cross-page page-scoped.
- `frontend/src/tests/design-system-policy.ts` - helper central si la politique y existe.

Files not expected to change:
- `backend/app/main.py` - aucun backend dans le scope.
- `frontend/package.json` - aucune dependance ou script requis.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- HelpPage design-system theme-tokens visual-smoke
npm run test -- legacy-style css-fallback
npm run lint
rg -n -- "--settings-" src/pages/HelpPage.css
rg -n "legacy|Legacy|alias|compat|shim|fallback|migration-only" src/pages/HelpPage.css src/tests/design-system-guards.test.ts
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-074-isoler-helppage-tokens-settings-page-scoped/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: remplacement par un token proche mais non equivalent.
  - Guardrail: visual-smoke et evidence after.
- Risk: la garde laisse passer une autre consommation page-scoped.
  - Guardrail: test design-system negatif et scan cible.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-001`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-004`
- `_condamad/stories/regression-guardrails.md`
