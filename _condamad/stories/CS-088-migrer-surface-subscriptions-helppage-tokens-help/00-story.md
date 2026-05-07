# Story CS-088 migrer-surface-subscriptions-helppage-tokens-help: Migrer la surface subscriptions de HelpPage.css vers les tokens Help

Status: ready-to-review

## 1. Objective

Migrer la sous-surface subscriptions de `frontend/src/pages/HelpPage.css` vers les tokens globaux,
les roles typographiques et les variables semantiques `--help-*` documentees. Le rendu Help reste
fonctionnellement identique. Aucun legacy ne doit rester et aucune AC ne peut etre acceptee en
`PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-002`
- Reason for change: `F-003` indique que la section subscriptions de `HelpPage.css` reste hors fenetre de garde Help et conserve des valeurs locales hardcodees.

## 3. Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un baseline before/after de la sous-surface subscriptions dans `frontend/src/pages/HelpPage.css`.
  - Preserver le modele owner page-scoped `--help-*`.
  - Migrer les valeurs visuelles et typographiques repetables de la section subscriptions vers `--help-*`, tokens globaux ou roles typographiques.
  - Etendre la garde Help existante ou ajouter une garde exacte CS-088 couvrant subscriptions.
- Out of scope:
  - Extraire une page subscriptions dediee ou modifier la structure React.
  - Migrer les autres sections Help deja couvertes, sauf ajustement minimal d'un token `--help-*` partage dans le meme fichier.
  - Modifier App, surfaces premium partagees, routes, API, stores ou backend.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044` a `RG-060`.
  - Ne pas consommer de tokens page-scoped non Help dans `HelpPage.css`.
  - Ne pas creer de namespace `legacy`, `compatibility`, `migration-only`, alias, shim, fallback ou re-export.
  - Ne pas conserver de dette sous forme de TODO, exception large, limitation acceptee ou `PASS with limitation`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre une sous-surface CSS bornee vers son owner Help canonique avec baseline, mapping et garde anti-retour.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents tokenises ou aux decisions finales documentees.
  - Les composants React, props, imports, routes, payloads et etats utilisateur restent inchanges.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la sous-surface subscriptions ne peut pas etre fermee sans extraction produit, fallback, compatibilite, legacy ou AC limitee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest et visual-smoke prouvent que la route Help rendue reste valide. |
| Baseline Snapshot | yes | Les artefacts before/after bornent subscriptions dans `HelpPage.css`. |
| Ownership Routing | yes | Chaque valeur doit rester sous token global, role typographique ou owner `--help-*`. |
| Allowlist Exception | yes | Les allowlists css-fallback, inline-style et legacy-style doivent rester exactes. |
| Contract Shape | no | Aucun contrat API, DTO, route, payload ou client genere n'est modifie. |
| Batch Migration | yes | Les valeurs subscriptions sont migrees par sous-blocs coherents. |
| Reintroduction Guard | yes | Les literals subscriptions migres ne doivent pas revenir silencieusement. |
| Persistent Evidence | yes | Les scans, decisions et validations doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/inline-style-policy.test.ts`
  - `frontend/src/tests/legacy-style-policy.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx`
- Secondary evidence:
  - scans `rg` cibles sur la section subscriptions de `frontend/src/pages/HelpPage.css`.
- Static scans alone are not sufficient because:
  - la route Help rendue doit rester couverte par les smoke tests frontend.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur subscriptions a une decision finale.
  - decisions autorisees: `migrated`, `registered-help-owner`, `typography-role`, `runtime-value` ou `kept-one-off-final`.
  - aucun TODO, legacy, fallback non classe, shim, alias ou limitation.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Surfaces subscriptions Help | `--help-*` documente ou tokens globaux | literals repetes dans subscriptions |
| Typographie Help subscriptions | roles typographiques ou `--help-*` documente | repetitions typographiques non classees |
| Radius, spacing, elevation | tokens shape/space/shadow ou `--help-*` documente | fallback literal ou token page-scoped tiers |
| Exceptions dynamiques | allowlist exacte existante si applicable | wildcard ou folder-wide exception |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | existing exact Help entries | aucune exception subscriptions large autorisee | entrees exactes seulement |
| `frontend/src/styles/css-fallback-allowlist.md` | existing fallback entries | aucun fallback Help non classe attendu | ne pas elargir |
| `frontend/src/styles/legacy-style-surface-registry.md` | existing legacy-style entries | aucune surface legacy Help attendue | ne pas elargir |

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
| Subscriptions layout | layout literals in subscriptions section | tokens or `--help-*` | CSS only | design-system, visual-smoke | after scan | owner unclear |
| Subscriptions cards | colors, borders, shadows, radius | tokens or `--help-*` | CSS only | design-system | exact guard | fallback required |
| Subscriptions typography | type literals | typography roles or `--help-*` | CSS only | visual-smoke | after scan | role absent and cannot be documented |
| Governance | Help guard coverage | `design-system-guards.test.ts` exact guard | tests only | design-system | failing forbidden examples | exception large |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before baseline | `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/hardcoded-values-before.md` | Borne les valeurs subscriptions initiales. |
| After evidence | `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/hardcoded-values-after.md` | Persiste decisions finales et scans anti-retour. |
| Final validation | `generated/10-final-evidence.md` | Persiste commandes, resultats et absence de limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: les literals subscriptions migres echouent s'ils reviennent hors owner Help documente.
- Deterministic source: forbidden symbols listed in `hardcoded-values-after.md`, `frontend/src/tests/design-system-guards.test.ts`, and targeted scans.
- Required forbidden examples:
  - hex/rgb/hsl/rgba migres de la section subscriptions;
  - `font-size`, `font-weight`, `line-height`, `letter-spacing` migres;
  - `box-shadow`, `border-radius`, gradients ou `var(--token, literal)` non allowlistes;
  - consommation de namespaces page-scoped non Help.
- Guard evidence: `npm run test -- design-system css-fallback inline-style legacy-style visual-smoke HelpPage`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md#F-003` - la sous-surface subscriptions Help reste localement hardcodee.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-002` - le candidat borne l'implementation a `frontend/src/pages/HelpPage.css`.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md` - `HelpPage.css` fait partie des six fichiers restants.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-044` a `RG-060` consultes avant cadrage.

## 6. Target State

- La section subscriptions de `HelpPage.css` consomme uniquement des tokens globaux, roles typographiques ou `--help-*` documentes pour les valeurs repetables.
- Les literals restants ont une decision finale explicite dans l'after et ne masquent aucun legacy.
- La garde Help couvre subscriptions ou une garde CS-088 equivalente echoue en cas de retour des literals migres.
- Les validations frontend passent sans limitation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace Help nouveau ou modifie doit etre classe.
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir non classees.
  - `RG-046` - les repetitions typographiques passent par roles semantiques ou decision finale documentee.
  - `RG-047` - aucun style inline statique ne doit etre introduit.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-049` - aucune surface legacy CSS ne doit etre creee.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
  - `RG-051` - aucun namespace page-scoped non Help ne doit etre consomme par `HelpPage.css`.
  - `RG-052` - aucun namespace migration-only ne doit revenir.
  - `RG-060` - aucun vocabulaire No Legacy non classe dans les commentaires CSS actifs.
- Non-applicable invariants:
  - `RG-053`, `RG-057` - aucune compatibilite runtime frontend n'est dans ce scope.
  - `RG-054` - aucune route admin legacy n'est modifiee.
  - `RG-055`, `RG-056`, `RG-058`, `RG-059` - les clusters prediction, UI partagee, chat et App sont hors scope.
- Required regression evidence:
  - `npm run test -- design-system css-fallback inline-style legacy-style visual-smoke HelpPage`
  - `npm run lint`
  - scans exacts des literals subscriptions migres dans `hardcoded-values-after.md`.
- Allowed differences:
  - differences visuelles uniquement si documentees comme equivalent tokenise ou decision finale non legacy.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Scope borne a subscriptions dans `HelpPage.css`. | Evidence profile: `baseline_before_after_diff`; `hardcoded-values-before.md`; `rg` Help. |
| AC2 | Chaque literal subscriptions a une decision finale. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|TODO" hardcoded-values-after.md`. |
| AC3 | Les valeurs repetables utilisent un owner Help documente. | Evidence profile: `batch_migration_mapping`; `npm run test -- design-system`. |
| AC4 | Aucun token tiers ni fallback non classe n'est introduit. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback legacy-style`; namespace `rg`. |
| AC5 | La garde Help couvre la section subscriptions. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`; guard `design-system-guards.test.ts`. |
| AC6 | Le rendu Help reste couvert. | Evidence profile: `reintroduction_guard`; `npm run test -- visual-smoke HelpPage`; lint frontend. |
| AC7 | No Legacy est respecte sans AC limitee. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "PASS with limitation|TODO" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline de subscriptions dans `HelpPage.css`. (AC: AC1, AC2)
- [ ] Task 2 - Classer chaque valeur subscriptions avec une decision finale sans legacy. (AC: AC2, AC7)
- [ ] Task 3 - Migrer les valeurs repetables vers tokens globaux, roles ou `--help-*` documentes. (AC: AC3)
- [ ] Task 4 - Mettre a jour les registres design-system uniquement pour les owners Help durables crees ou modifies. (AC: AC3, AC4)
- [ ] Task 5 - Etendre ou ajouter la garde anti-retour Help subscriptions. (AC: AC5, AC7)
- [ ] Task 6 - Persister l'after, les scans et l'evidence finale sans limitation. (AC: AC2, AC5, AC6, AC7)
- [ ] Task 7 - Executer les validations frontend et la validation de story. (AC: AC4, AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`, `frontend/src/styles/token-namespace-registry.md` et `frontend/src/styles/typography-roles.md`.
- Reuse le namespace `--help-*` existant pour les decisions page-scoped Help.
- Do not recreate local variables for a role already covered by token global, role typographique ou `--help-*` existant.
- Shared abstraction allowed only if elle retire une duplication reelle dans `HelpPage.css` et reste documentee.

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
- `var(--token, literal)` ou tout fallback CSS literal non allowliste dans `HelpPage.css`.
- consommation de `--settings-*`, `--app-*`, `--chat-*`, `--landing-*`, `--admin-*` ou autre namespace page-scoped non Help.
- extraction React ou nouvelle route subscriptions sans decision produit explicite.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Help subscriptions visual values | design tokens, typography roles, or documented `--help-*` vars | repeated hardcoded literals in subscriptions |
| Help typography | `frontend/src/styles/typography-roles.md`, `--type-*`, or documented `--help-*` | untracked repeated type literals |
| Help evidence | story before/after artifacts | undocumented local decisions |
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
- `frontend/src/pages/HelpPage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/HelpPage.css` - migrer la sous-surface subscriptions.
- `frontend/src/styles/token-namespace-registry.md` - documenter tout `--help-*` durable nouveau ou modifie.
- `frontend/src/styles/typography-roles.md` - documenter tout role typographique durable manquant.
- `frontend/src/tests/design-system-guards.test.ts` - etendre la garde Help subscriptions.
- `frontend/src/tests/visual-smoke.test.tsx` - uniquement si la couverture route Help doit etre ajustee.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture anti-retour Help subscriptions.
- `frontend/src/tests/css-fallback-policy.test.ts` - preservation des fallbacks exacts.
- `frontend/src/tests/inline-style-policy.test.ts` - preservation absence de styles inline statiques.
- `frontend/src/tests/legacy-style-policy.test.ts` - preservation absence de surface legacy.
- `frontend/src/tests/visual-smoke.test.tsx` - preservation rendu Help.

Files not expected to change:

- `frontend/package.json` - aucune dependance ou script nouveau.
- `frontend/src/pages/HelpPage.tsx` - comportement React hors scope, sauf retrait mecanique d'une classe morte apres preuve.
- `frontend/src/App.css` - story dediee CS-087.
- `frontend/src/styles/backgrounds.css` - story dediee CS-089.
- `backend/app/main.py` - aucun backend dans ce scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system css-fallback inline-style legacy-style visual-smoke HelpPage
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/HelpPage.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/HelpPage.css
rg -n "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/HelpPage.css
rg -n -- "--settings-|--app-|--chat-|--landing-|--admin-" src/pages/HelpPage.css
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/HelpPage.css
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: la migration subscriptions modifie involontairement le rendu Help.
  - Guardrail: visual-smoke Help et artefact after.
- Risk: `HelpPage.css` consomme un namespace page-scoped tiers.
  - Guardrail: `RG-051` et scan des namespaces interdits.
- Risk: une exception large masque la dette restante.
  - Guardrail: AC4 et allowlist exactes.
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

- `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-002` - source de la story.
- `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md#F-003` - constat principal.
- `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md` - contexte d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
