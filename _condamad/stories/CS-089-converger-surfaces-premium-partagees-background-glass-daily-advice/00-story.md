# Story CS-089 converger-surfaces-premium-partagees-background-glass-daily-advice: Converger les surfaces premium partagees background, glass et daily advice

Status: ready-to-review

## 1. Objective

Attribuer un ownership canonique unique aux valeurs premium partagees dans `backgrounds.css`,
`glass.css`, `DailyHoroscopePage.css` et `DailyAdviceCard.css`, puis migrer les literals repetables
vers les tokens globaux, `premium-theme.css`, `--glass-*` ou les variables semantiques locales
documentees. Aucun legacy ne doit rester et aucune AC ne peut etre acceptee en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-003`
- Reason for change: `F-004` indique que les decisions background/glass/premium daily restent
  reparties entre literals locaux, tokens premium et tokens page/component sans owner canonique unique.

## 3. Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un baseline before/after des quatre fichiers exacts: `backgrounds.css`, `glass.css`, `DailyHoroscopePage.css`, `DailyAdviceCard.css`.
  - Decider pour chaque valeur si l'owner canonique est global, `premium-theme.css`, `--glass-*`, page daily ou composant daily advice.
  - Migrer les rgba, gradients, shadows, radius et overlays repetables vers l'owner canonique.
  - Ajouter des guards exacts anti-retour pour ces quatre fichiers.
  - Garder `DailyHoroscopePage.css` aligne avec les entrees `--glass-*` existantes.
- Out of scope:
  - Modifier la logique React, les donnees daily horoscope, l'API, les stores ou le backend.
  - Migrer `App.css` ou `HelpPage.css`.
  - Refaire l'architecture theme globale hors decisions strictement necessaires aux surfaces premium partagees.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044` a `RG-060`.
  - Ne pas creer de namespace `legacy`, `compatibility`, `migration-only`, alias, shim, fallback ou re-export.
  - Ne pas conserver de dette sous forme de TODO, exception large, limitation acceptee ou `PASS with limitation`.
  - Ne pas creer de second owner concurrent pour `--glass-*` ou `--premium-*`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de quatre fichiers premium vers des owners canoniques avec mapping before/after.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents tokenises ou aux decisions finales documentees.
  - Les composants React, props, imports, routes, payloads et etats utilisateur restent inchanges.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une valeur premium partagee ne peut pas recevoir un owner canonique unique sans creer fallback, compatibilite, legacy, double owner ou AC limitee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest et visual-smoke prouvent que les surfaces premium rendues restent valides. |
| Baseline Snapshot | yes | Les artefacts before/after bornent les quatre fichiers premium. |
| Ownership Routing | yes | Chaque valeur premium doit etre routee vers global, premium, glass, page daily ou composant daily advice. |
| Allowlist Exception | yes | Les allowlists css-fallback, inline-style et legacy-style doivent rester exactes. |
| Contract Shape | no | Aucun contrat API, DTO, route, payload ou client genere n'est modifie. |
| Batch Migration | yes | Les valeurs sont migrees par sous-surfaces premium partagees. |
| Reintroduction Guard | yes | Les literals premium migres ne doivent pas revenir silencieusement. |
| Persistent Evidence | yes | Les scans, decisions et validations doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/inline-style-policy.test.ts`
  - `frontend/src/tests/legacy-style-policy.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx`
- Secondary evidence:
  - scans `rg` cibles sur les quatre fichiers premium exacts.
- Static scans alone are not sufficient because:
  - les surfaces daily/premium rendues doivent rester couvertes par les tests frontend executables.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-089-converger-surfaces-premium-partagees-background-glass-daily-advice/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-089-converger-surfaces-premium-partagees-background-glass-daily-advice/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur premium partagee a un owner canonique unique.
  - decisions autorisees: `global-token`, `premium-token`, `glass-token`, `daily-page-token`, `daily-advice-token`, `runtime-value` ou `kept-one-off-final`.
  - aucun TODO, legacy, fallback non classe, double owner ou limitation.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Tokens globaux reutilisables | `frontend/src/styles/design-tokens.css` | literals dupliques dans fichiers premium |
| Theme premium partage | `frontend/src/styles/premium-theme.css` | page/component token concurrent |
| Effets glass partages | `frontend/src/styles/glass.css` avec namespace `--glass-*` documente | `--glass-*` redefini localement hors owner |
| Backgrounds partages | `frontend/src/styles/backgrounds.css` ou token global/premium documente | gradients locaux repetes |
| Surface Daily page | variables semantiques de `DailyHoroscopePage.css` seulement si page-specific | token global invente pour un cas unique |
| Surface Daily advice | variables semantiques de `DailyAdviceCard.css` seulement si component-specific | double owner avec `premium-theme.css` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | existing exact premium entries | aucune exception premium large autorisee | entrees exactes seulement |
| `frontend/src/styles/css-fallback-allowlist.md` | existing fallback entries | aucun fallback premium non classe attendu | ne pas elargir |
| `frontend/src/styles/legacy-style-surface-registry.md` | existing legacy-style entries | aucune surface legacy premium attendue | ne pas elargir |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan;
- no new exception can be used to accept an AC with limitation.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Shared backgrounds | literals in `backgrounds.css` | global or premium tokens | CSS only | design-system, theme-tokens | after scan | owner conflict |
| Shared glass | literals in `glass.css` | documented `--glass-*` or global tokens | CSS only | design-system, theme-tokens | registry check | duplicate glass owner |
| Daily page premium | literals in `DailyHoroscopePage.css` | premium/glass/page daily tokens | CSS only | visual-smoke, DailyHoroscopePage | after scan | fallback required |
| Daily advice card | literals in `DailyAdviceCard.css` | premium/component semantic tokens | CSS only | visual-smoke, design-system | after scan | double owner |
| Governance | exact guard coverage | `design-system-guards.test.ts` and registries | tests only | design-system, theme-tokens | failing forbidden examples | exception large |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before baseline | `hardcoded-values-before.md` | Borne les valeurs premium initiales. |
| After evidence | `hardcoded-values-after.md` | Persiste owners canoniques, decisions finales et scans anti-retour. |
| Final validation | `generated/10-final-evidence.md` | Persiste commandes, resultats et absence de limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: les literals premium migres echouent s'ils reviennent hors owner canonique documente.
- Deterministic source: forbidden symbols listed in `hardcoded-values-after.md`, `frontend/src/tests/design-system-guards.test.ts`, and targeted scans.
- Required forbidden examples:
  - rgba/hex/hsl migres des quatre fichiers;
  - gradients, overlays, shadows et radius migres;
  - `var(--token, literal)` non allowliste;
  - double definition locale de valeurs `--glass-*` ou `--premium-*` hors owner canonique.
- Guard evidence: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md#F-004`
  - les decisions background/glass/daily premium manquent d'un owner canonique unique.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-003` - le candidat fixe les quatre fichiers d'implementation exacts.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md` - les surfaces premium partagees font partie des six fichiers restants.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-044` a `RG-060` consultes avant cadrage.

## 6. Target State

- Les valeurs premium partagees ont un owner unique entre tokens globaux, `premium-theme.css`, `--glass-*`, page daily ou composant daily advice.
- Les quatre fichiers exacts ne contiennent plus de literals repetables sans decision finale.
- `DailyHoroscopePage.css` reste aligne avec le registre `--glass-*`.
- Les guards design-system, theme-tokens, fallback, inline-style, legacy-style, visual-smoke, lint et build passent sans limitation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace premium, glass ou daily nouveau/modifie doit etre classe.
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir non classees.
  - `RG-046` - les repetitions typographiques eventuelles passent par roles semantiques ou decision finale documentee.
  - `RG-047` - aucun style inline statique ne doit etre introduit.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-049` - aucune surface legacy CSS ne doit etre creee.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
  - `RG-052` - aucun namespace migration-only ne doit revenir.
  - `RG-055` - le cluster prediction premium protege doit rester ferme.
  - `RG-060` - aucun vocabulaire No Legacy non classe dans les commentaires CSS actifs.
- Non-applicable invariants:
  - `RG-051` - la story ne consomme pas de token page-scoped tiers hors owner.
  - `RG-053`, `RG-057` - aucune compatibilite runtime frontend n'est dans ce scope.
  - `RG-054` - aucune route admin legacy n'est modifiee.
  - `RG-056`, `RG-058`, `RG-059` - les clusters UI partagee, chat et App sont hors scope.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage`
  - `npm run lint`
  - `npm run build`
  - scans exacts des literals premium migres dans `hardcoded-values-after.md`.
- Allowed differences:
  - differences visuelles uniquement si documentees comme equivalent tokenise ou decision finale non legacy.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Scope borne aux quatre fichiers premium exacts. | Evidence profile: `baseline_before_after_diff`; `hardcoded-values-before.md`; `rg` premium. |
| AC2 | Chaque valeur premium a un owner final. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|TODO" hardcoded-values-after.md`. |
| AC3 | Les valeurs repetables utilisent un owner documente. | Evidence profile: `batch_migration_mapping`; `npm run test -- theme-tokens design-system`. |
| AC4 | Aucun double owner premium n'est ajoute. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback legacy-style`; token `rg`. |
| AC5 | `DailyHoroscopePage.css` reste aligne avec `--glass-*`. | Evidence profile: `reintroduction_guard`; `npm run test -- DailyHoroscopePage visual-smoke theme-tokens`. |
| AC6 | Les guards empechent le retour des literals migres. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`; AST guard. |
| AC7 | No Legacy est respecte sans AC limitee. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "PASS with limitation|TODO" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline des quatre fichiers premium exacts. (AC: AC1, AC2)
- [ ] Task 2 - Classer chaque valeur avec un owner canonique unique sans legacy. (AC: AC2, AC4, AC7)
- [ ] Task 3 - Migrer les valeurs repetables vers tokens globaux, premium, glass, daily page ou daily advice documentes. (AC: AC3, AC5)
- [ ] Task 4 - Mettre a jour les registres design-system pour tout owner premium/glass/daily durable cree ou modifie. (AC: AC3, AC4, AC5)
- [ ] Task 5 - Ajouter les guards anti-retour exacts pour les quatre fichiers. (AC: AC6, AC7)
- [ ] Task 6 - Persister l'after, les scans et l'evidence finale sans limitation. (AC: AC2, AC4, AC6, AC7)
- [ ] Task 7 - Executer les validations frontend et la validation de story. (AC: AC5, AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`,
  `frontend/src/styles/premium-theme.css`, `frontend/src/styles/token-namespace-registry.md`
  et `frontend/src/styles/typography-roles.md`.
- Reuse les owners `--glass-*` existants au lieu de redefinir des effets glass locaux.
- Reuse les tokens `--premium-*`, `--color-*`, `--surface-*`, `--radius-*`, `--shadow-*` et `--space-*` quand ils portent deja la decision voulue.
- Do not recreate local variables for a visual role already covered by an owner global, premium ou glass.
- Shared abstraction allowed only if elle retire une duplication reelle entre les quatre fichiers et reste documentee.

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

- `legacy`, `Legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` dans les fichiers touches.
- `var(--token, literal)` ou tout fallback CSS literal non allowliste dans les quatre fichiers.
- double owner concurrent pour une valeur `--glass-*` ou `--premium-*`.
- modification de comportement dans les composants React daily horoscope, clients API, routes ou stores.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Shared premium values | `frontend/src/styles/premium-theme.css` or global design tokens | repeated local literals |
| Shared glass effects | `frontend/src/styles/glass.css` and documented `--glass-*` | page-level glass duplicates |
| Shared backgrounds | `frontend/src/styles/backgrounds.css` or documented global/premium tokens | repeated gradients in page/component CSS |
| Daily page-specific values | documented Daily page semantic vars | global token invented for one-off |
| DailyAdviceCard component-specific values | documented component semantic vars | duplicate premium/glass owner |
| Anti-return guard | `frontend/src/tests/design-system-guards.test.ts` | manual-only review |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md`
- `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/backgrounds.css` - converger les backgrounds premium partages.
- `frontend/src/styles/glass.css` - converger les effets glass partages et owners `--glass-*`.
- `frontend/src/pages/DailyHoroscopePage.css` - migrer overlays/valeurs premium daily page.
- `frontend/src/components/prediction/DailyAdviceCard.css` - migrer overlays/valeurs premium du composant.
- `frontend/src/styles/design-tokens.css` - seulement si une valeur globale durable est creee.
- `frontend/src/styles/premium-theme.css` - seulement si l'owner canonique est premium.
- `frontend/src/styles/token-namespace-registry.md` - documenter tout owner premium/glass/daily durable nouveau ou modifie.
- `frontend/src/styles/typography-roles.md` - documenter tout role typographique durable manquant.
- `frontend/src/tests/design-system-guards.test.ts` - ajouter les guards anti-retour exacts.
- `frontend/src/tests/theme-tokens.test.ts` - ajuster si le registre de tokens impose une nouvelle verification.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture anti-retour premium.
- `frontend/src/tests/theme-tokens.test.ts` - validation des namespaces premium/glass/daily.
- `frontend/src/tests/css-fallback-policy.test.ts` - preservation des fallbacks exacts.
- `frontend/src/tests/inline-style-policy.test.ts` - preservation absence de styles inline statiques.
- `frontend/src/tests/legacy-style-policy.test.ts` - preservation absence de surface legacy.
- `frontend/src/tests/visual-smoke.test.tsx` - preservation rendu DailyHoroscope.

Files not expected to change:

- `frontend/package.json` - aucune dependance ou script nouveau.
- `frontend/src/pages/DailyHoroscopePage.tsx` - comportement React hors scope, sauf retrait mecanique d'une classe morte apres preuve.
- `frontend/src/components/prediction/DailyAdviceCard.tsx` - comportement React hors scope, sauf retrait mecanique d'une classe morte apres preuve.
- `frontend/src/App.css` - story dediee CS-087.
- `frontend/src/pages/HelpPage.css` - story dediee CS-088.
- `backend/app/main.py` - aucun backend dans ce scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage
npm run lint
npm run build
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/styles/backgrounds.css src/styles/glass.css src/pages/DailyHoroscopePage.css src/components/prediction/DailyAdviceCard.css
$premiumFiles = @(
  "src/styles/backgrounds.css",
  "src/styles/glass.css",
  "src/pages/DailyHoroscopePage.css",
  "src/components/prediction/DailyAdviceCard.css"
)
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" $premiumFiles
rg -n "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," $premiumFiles
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" $premiumFiles
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-089-converger-surfaces-premium-partagees-background-glass-daily-advice/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: les owners premium/glass deviennent concurrents.
  - Guardrail: AC2, AC4 et registre `token-namespace-registry.md`.
- Risk: la migration modifie involontairement le rendu DailyHoroscope premium.
  - Guardrail: visual-smoke, tests DailyHoroscopePage et artefact after.
- Risk: des gradients/overlays sont remplaces par fallbacks locaux.
  - Guardrail: `RG-048`, scans No Legacy et tests css-fallback.
- Risk: une AC partiellement satisfaite est acceptee.
  - Guardrail: AC7 interdit `PASS with limitation` et impose evidence finale sans limitation.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers, migration-only namespaces or re-exports.
- No legacy may remain in the implemented cluster.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-003` - source de la story.
- `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md#F-004` - constat principal.
- `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md` - contexte d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
