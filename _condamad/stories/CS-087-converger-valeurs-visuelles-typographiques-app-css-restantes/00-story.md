# Story CS-087 converger-valeurs-visuelles-typographiques-app-css-restantes: Converger les valeurs visuelles et typographiques restantes de App.css

Status: ready-to-review

## 1. Objective

Fermer la dette restante de `frontend/src/App.css` en classant puis migrant les valeurs visuelles
et typographiques vers les tokens globaux, les roles typographiques ou les variables semantiques
`--app-*` documentees. Le comportement React reste inchange. Aucun legacy ne doit rester et aucune
AC ne peut etre acceptee en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-001`
- Reason for change: `F-002` indique que `App.css` conserve 561 hits visuels ou typographiques hors garde exhaustive apres `CS-082`.

## 3. Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un baseline before/after de `frontend/src/App.css`.
  - Classer chaque literal App restant comme token global, `--app-*`, role typographique, valeur runtime/animation ou one-off final.
  - Migrer uniquement les valeurs repetables de `App.css` vers des owners documentes.
  - Etendre la garde `CS-082` pour couvrir le fichier App plus largement, pas seulement les variables deja selectionnees.
- Out of scope:
  - Modifier `frontend/src/App.tsx`, les routes, les stores, les clients API ou les comportements applicatifs.
  - Migrer `HelpPage.css`, les surfaces premium partagees, ou tout autre CSS hors `App.css`.
  - Traiter le warning de bundle-size Vite, qui releve de `frontend-performance`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044` a `RG-060`.
  - Ne pas creer de namespace `legacy`, `compatibility`, `migration-only`, alias, shim, fallback ou re-export.
  - Ne pas conserver de dette sous forme de TODO, exception large, limitation acceptee ou `PASS with limitation`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de valeurs CSS restantes dans `App.css` avec mapping before/after et garde anti-retour.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents tokenises ou aux decisions finales documentees.
  - Les composants React, props, imports, routes, payloads et etats utilisateur restent inchanges.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une valeur ne peut pas recevoir une decision finale sans garder une compatibilite, un fallback, une dette legacy ou une AC limitee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest et visual-smoke prouvent que les surfaces App rendues restent valides. |
| Baseline Snapshot | yes | Les artefacts before/after bornent les valeurs App restantes. |
| Ownership Routing | yes | Chaque valeur doit etre routee vers token global, `--app-*`, role typographique, runtime/animation ou one-off final. |
| Allowlist Exception | yes | Les allowlists css-fallback, inline-style et legacy-style doivent rester exactes et non elargies. |
| Contract Shape | no | Aucun contrat API, DTO, route, payload ou client genere n'est modifie. |
| Batch Migration | yes | Les valeurs App sont traitees par sous-surfaces coherentes. |
| Reintroduction Guard | yes | Les literals App migres ne doivent pas revenir silencieusement. |
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
  - scans `rg` cibles sur `frontend/src/App.css`.
- Static scans alone are not sufficient because:
  - le shell App rendu doit rester couvert par des tests frontend executables.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur App restante a une decision finale.
  - decisions autorisees: `migrated`, `registered-semantic-owner`, `typography-role`, `runtime-animation-value` ou `kept-one-off-final`.
  - aucun TODO, legacy, fallback non classe, shim, alias ou limitation.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleurs, gradients et surfaces App | tokens globaux, `premium-theme.css` si deja canonique, ou `--app-*` documente | literals repetes dans `App.css` |
| Typographie App | `frontend/src/styles/typography-roles.md` et tokens `--type-*` | tailles, poids, line-height ou letter-spacing repetes non classes |
| Radius, spacing, elevation | tokens shape/space/shadow ou `--app-*` documente | fallback literal ou namespace non documente |
| Animation et runtime CSS | valeur locale classee `runtime-animation-value` | token semantique invente sans reutilisation reelle |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | existing exact entries | aucune exception App large autorisee | entrees exactes seulement |
| `frontend/src/styles/css-fallback-allowlist.md` | existing fallback entries | aucun fallback App non classe attendu | ne pas elargir |
| `frontend/src/styles/legacy-style-surface-registry.md` | existing legacy-style entries | aucune surface legacy App attendue | ne pas elargir |

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
| App shell | remaining shell literals in `App.css` | global tokens or `--app-*` | CSS only | design-system, visual-smoke | after scan | fallback required |
| Catalogue/dashboard App | repeated visual values | global tokens or documented `--app-*` | CSS only | design-system | guard diff | owner unclear |
| Typography App | repeated type literals | typography roles or `--type-*` | CSS only | design-system, visual-smoke | after scan | role absent and cannot be documented |
| Governance | App guard coverage | `design-system-guards.test.ts` exact guard | tests only | design-system | failing forbidden examples | exception large |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before baseline | `_condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/hardcoded-values-before.md` | Borne les valeurs App initiales. |
| After evidence | `hardcoded-values-after.md` | Persiste decisions finales et scans anti-retour. |
| Final validation | `generated/10-final-evidence.md` | Persiste commandes, resultats et absence de limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: les literals App migres ou classes comme interdits echouent s'ils reviennent hors owner documente.
- Deterministic source: forbidden symbols listed in `hardcoded-values-after.md`, `frontend/src/tests/design-system-guards.test.ts`, and targeted scans.
- Required forbidden examples:
  - hex/rgb/hsl/rgba migres de `App.css`;
  - `font-size`, `font-weight`, `line-height`, `letter-spacing` migres;
  - `box-shadow`, `border-radius`, gradients ou `var(--token, literal)` non allowlistes;
  - vocabulaire `legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` dans les fichiers touches hors evidence historique.
- Guard evidence: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md#F-002` - `App.css` conserve 561 hits visuels/type hors garde exhaustive.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-001` - le candidat borne l'implementation a `frontend/src/App.css`.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md` - les fichiers restants sont concentres et `App.css` est une surface prioritaire.
- Evidence 4: `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md` - une premiere garde App existe mais doit etre etendue.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - `RG-044` a `RG-060` consultes avant cadrage.

## 6. Target State

- `frontend/src/App.css` ne contient plus de valeurs visuelles ou typographiques repetables non routees.
- Les valeurs restantes ont une decision finale explicite dans l'after et ne masquent aucun legacy.
- Les registres `token-namespace-registry.md` et `typography-roles.md` documentent tout owner durable nouveau ou modifie.
- Les guards design-system, token, fallback, inline-style, legacy-style, visual-smoke, lint et build passent sans limitation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace App nouveau ou modifie doit etre classe.
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir non classees.
  - `RG-046` - les repetitions typographiques passent par roles semantiques ou decision finale documentee.
  - `RG-047` - aucun style inline statique ne doit etre introduit.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-049` - aucune surface legacy CSS ne doit etre creee.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
  - `RG-052` - aucun namespace migration-only ne doit revenir.
  - `RG-053`, `RG-057` - aucune compatibilite runtime frontend ne doit etre recreee.
  - `RG-059` - le cluster App doit rester protege par une garde anti-retour.
  - `RG-060` - aucun vocabulaire No Legacy non classe dans les commentaires CSS actifs.
- Non-applicable invariants:
  - `RG-051` - la story ne consomme pas de token page-scoped tiers hors App.
  - `RG-054` - aucune route admin legacy n'est modifiee.
  - `RG-055`, `RG-056`, `RG-058` - les clusters prediction, UI partagee et chat sont hors scope.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run lint`
  - `npm run build`
  - scans exacts des literals App migres dans `hardcoded-values-after.md`.
- Allowed differences:
  - differences visuelles uniquement si documentees comme equivalent tokenise ou decision finale non legacy.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Scope borne a `frontend/src/App.css`. | Evidence profile: `baseline_before_after_diff`; `hardcoded-values-before.md`; `rg` App. |
| AC2 | Chaque literal App a une decision finale. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|TODO" hardcoded-values-after.md`. |
| AC3 | Les valeurs repetables utilisent un owner documente. | Evidence profile: `batch_migration_mapping`; `npm run test -- theme-tokens design-system`. |
| AC4 | Aucune exception large ou fallback non classe n'est ajoute. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback inline-style legacy-style`. |
| AC5 | La garde App couvre les valeurs App restantes migrees. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`; guard `design-system-guards.test.ts`. |
| AC6 | Les rendus critiques restent couverts sans changement fonctionnel. | Evidence profile: `reintroduction_guard`; `npm run test -- visual-smoke`; `npm run build`. |
| AC7 | No Legacy est respecte sans AC limitee. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "PASS with limitation|TODO" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline de `App.css` uniquement. (AC: AC1, AC2)
- [x] Task 2 - Classer chaque valeur App restante avec une decision finale sans legacy. (AC: AC2, AC7)
- [x] Task 3 - Migrer les valeurs repetables vers tokens, roles ou `--app-*` documentes. (AC: AC3)
- [x] Task 4 - Mettre a jour les registres design-system uniquement pour les owners durables crees ou modifies. (AC: AC3, AC4)
- [x] Task 5 - Etendre la garde anti-retour App issue de `CS-082`. (AC: AC5, AC7)
- [x] Task 6 - Persister l'after, les scans et l'evidence finale sans limitation. (AC: AC2, AC5, AC6, AC7)
- [x] Task 7 - Executer les validations frontend et la validation de story. (AC: AC4, AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`,
  `frontend/src/styles/premium-theme.css`, `frontend/src/styles/token-namespace-registry.md`
  et `frontend/src/styles/typography-roles.md`.
- Reuse les tokens `--color-*`, `--surface-*`, `--radius-*`, `--shadow-*`, `--space-*`, `--premium-*`, `--type-*` et les `--app-*` deja documentes si leur role correspond.
- Do not recreate local variables for a role already covered by a token or role typographique.
- Shared abstraction allowed only if elle retire une duplication reelle dans `App.css` et reste documentee dans le registre applicable.

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
  - `var(--token, literal)` ou tout fallback CSS literal non allowliste dans `App.css`.
- nouveau namespace non documente dans `frontend/src/styles/token-namespace-registry.md`.
- modification de comportement dans `frontend/src/App.tsx`, clients API, routes ou stores.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| App visual values | design tokens, premium tokens, typography roles, or documented `--app-*` vars | repeated hardcoded literals in `App.css` |
| App typography | `frontend/src/styles/typography-roles.md` and `--type-*` tokens | untracked repeated type literals |
| App evidence | story before/after artifacts | undocumented local decisions |
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
- `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md`
- `frontend/src/App.css`
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

- `frontend/src/App.css` - migrer les valeurs visuelles et typographiques restantes.
- `frontend/src/styles/token-namespace-registry.md` - documenter tout `--app-*` durable nouveau ou modifie.
- `frontend/src/styles/typography-roles.md` - documenter tout role typographique durable manquant.
- `frontend/src/tests/design-system-guards.test.ts` - etendre la garde App exacte.
- `frontend/src/tests/design-system-allowlist.ts` - uniquement si une exception exacte existante doit etre ajustee, sans wildcard.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture anti-retour App.
- `frontend/src/tests/theme-tokens.test.ts` - validation du registre de tokens.
- `frontend/src/tests/css-fallback-policy.test.ts` - preservation des fallbacks exacts.
- `frontend/src/tests/inline-style-policy.test.ts` - preservation absence de styles inline statiques.
- `frontend/src/tests/legacy-style-policy.test.ts` - preservation absence de surface legacy.
- `frontend/src/tests/visual-smoke.test.tsx` - preservation rendu critique.

Files not expected to change:

- `frontend/package.json` - aucune dependance ou script nouveau.
- `frontend/src/App.tsx` - comportement React hors scope, sauf retrait mecanique d'une classe morte apres preuve.
- `frontend/src/pages/HelpPage.css` - story dediee CS-088.
- `frontend/src/styles/backgrounds.css` - story dediee CS-089.
- `frontend/src/styles/glass.css` - story dediee CS-089.
- `backend/app/main.py` - aucun backend dans ce scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/App.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/App.css
rg -n "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/App.css
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: la migration App modifie involontairement le rendu global.
  - Guardrail: visual-smoke, design-system guards et artefact after.
- Risk: le scope s'elargit vers Help ou premium shared surfaces.
  - Guardrail: AC1 borne les fichiers exacts et fichiers hors scope.
- Risk: une valeur est remplacee par une variable locale non documentee ou un fallback.
  - Guardrail: `RG-044`, `RG-048`, scans No Legacy et registre de tokens.
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

- `_condamad/audits/frontend-design-system/2026-05-07-2236/03-story-candidates.md#SC-001` - source de la story.
- `_condamad/audits/frontend-design-system/2026-05-07-2236/02-finding-register.md#F-002` - constat principal.
- `_condamad/audits/frontend-design-system/2026-05-07-2236/00-audit-report.md` - contexte d'audit.
- `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md` - garde App existante a etendre.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
