# Story CS-084 migrer-cluster-settings-valeurs-visuelles-typographiques: Migrer le cluster Settings de valeurs visuelles et typographiques

Status: ready-to-dev

## 1. Objective

Migrer `frontend/src/pages/settings/Settings.css` vers les tokens, roles typographiques et variables semantiques documentees du design-system.
Le comportement React reste inchange.
Aucun legacy ne doit rester dans le cluster implemente et aucune AC ne peut etre acceptee en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-07-0017/03-story-candidates.md#SC-001`
- Reason for change: `F-002` signale encore 68 fichiers applicatifs frontend avec literals visuels ou typographiques.
  `Settings.css` fait partie des clusters recommandes pour poursuivre la convergence.

## 3. Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un inventaire before/after des literals de `frontend/src/pages/settings/Settings.css`.
  - Classer chaque literal selectionne comme token global, token semantic page-scoped `--settings-*`, role typographique, constante runtime typable ou donnee locale non-style.
  - Migrer les couleurs, gradients, shadows, radius, espacements et valeurs typographiques repetables vers des owners documentes.
  - Mettre a jour les registres design-system et les guards exacts uniquement pour le cluster Settings.
- Out of scope:
  - Migrer les 67 autres fichiers de l'inventaire F-002.
  - Modifier `frontend/src/App.css`, qui doit rester une story separee quand il est concerne.
  - Modifier routes, API, stores, logique abonnement, logique React ou contenu produit.
  - Traiter le warning de chunk-size Vite `F-004`, qui releve de `frontend-performance`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044` a `RG-060`.
  - Ne pas creer de namespace `legacy`, `compatibility`, `migration-only`, alias, shim, fallback ou re-export.
  - Ne pas conserver de dette sous forme de TODO, exception large, limitation acceptee ou `PASS with limitation`.
  - Ne pas reutiliser des tokens page-scoped Settings hors de `Settings.css`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de valeurs CSS vers les owners canoniques du design-system avec mapping before/after.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents tokenises documentes dans l'artefact after.
  - Les composants React, props, imports, routes, payloads et etats utilisateur restent inchanges.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une valeur du cluster ne peut pas recevoir une decision finale sans garder une compatibilite, un fallback, une dette legacy ou une limitation.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system et visual-smoke prouvent que les surfaces rendues par `Settings.css` restent valides. |
| Baseline Snapshot | yes | Les artefacts before/after bornent les valeurs Settings migrees. |
| Ownership Routing | yes | Les decisions visuelles doivent etre routees vers tokens, roles typographiques, `--settings-*` documente ou donnee locale non-style. |
| Allowlist Exception | yes | Les allowlists inline-style, css-fallback et legacy-style doivent rester exactes; aucune exception Settings large n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route, payload ou client genere n'est modifie. |
| Batch Migration | yes | Les valeurs sont migrees par sous-surfaces coherentes de `Settings.css`. |
| Reintroduction Guard | yes | Les literals Settings migres ne doivent pas revenir silencieusement. |
| Persistent Evidence | yes | Les scans, decisions finales et validations doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/inline-style-policy.test.ts`
  - `frontend/src/tests/legacy-style-policy.test.ts`
  - `frontend/src/tests/visual-smoke.test.ts` if present after inspection
- Secondary evidence:
  - scans `rg` cibles sur `frontend/src/pages/settings/Settings.css`.
- Static scans alone are not sufficient because:
  - les surfaces Settings rendues doivent rester couvertes par des tests frontend executables et par les guards de gouvernance.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur du cluster a une decision finale.
  - decisions autorisees: `migrated`, `registered-semantic-owner`, `runtime-custom-property` ou `kept-one-off-final`.
  - aucun TODO, legacy, fallback non classe ou limitation.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleurs et surfaces | tokens globaux ou `--settings-*` documente | literals repetes ou aliases |
| Typographie Settings | `frontend/src/styles/typography-roles.md` et tokens `--type-*` existants | tailles, poids, line-height ou letter-spacing repetes sans role |
| Radius, spacing, elevation | tokens shape/space/shadow ou role Settings | fallback literal ou copie locale |
| Progression runtime | `--usage-progress` dynamique allowliste | fallback non documente ou style inline statique |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | `--usage-progress` | progression runtime CSS | permanent tant que runtime |
| `frontend/src/tests/design-system-allowlist.ts` | existing policy entries | source exacte; aucune exception folder-wide Settings | entrees classees seulement |
| `frontend/src/tests/inline-style-allowlist.ts` | dynamic inline-style entries | source exacte | entrees classees seulement |

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
| Palette | color, gradient, shadow literals | tokens or `--settings-*` | `Settings.css` | design-system | after scan | unregistered namespace |
| Cards/controls | radius, spacing, border literals | shape/space/shadow tokens | `Settings.css` | visual-smoke | decision table | no final classification |
| Typography | type literals | type tokens or roles | `Settings.css` | design-system | type scan | durable role missing |
| Runtime progress | `--usage-progress` | exact dynamic allowlist | `Settings.css` | css-fallback | allowlist test | new fallback required |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before baseline | `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/hardcoded-values-before.md` | Borne fichiers et valeurs initiales. |
| After evidence | `hardcoded-values-after.md` | Persiste decisions finales et scans anti-retour. |
| Final validation | `generated/10-final-evidence.md` | Persiste commandes, resultats et absence de limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: les literals migres du cluster Settings echouent s'ils reviennent sans classification finale.
- Deterministic source: forbidden symbols listed in `hardcoded-values-after.md`, tests design-system et scans `rg`.
- Required forbidden examples:
  - hex/rgb/hsl/rgba migres du cluster Settings.
  - `font-size`, `font-weight`, `line-height`, `letter-spacing` migres.
  - `box-shadow`, `border-radius`, gradients ou `var(--token, literal)` non allowlistes.
  - vocabulaire `legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` hors registre ou evidence historique.
- Guard evidence: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-07-0017/02-finding-register.md#F-002`
  - 68 fichiers applicatifs frontend conservent des literals visuels ou typographiques.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-07-0017/03-story-candidates.md#SC-001`
  - recommande une migration de cluster borne et liste `frontend/src/pages/settings/Settings.css` comme candidat prioritaire.
- Evidence 3: `frontend/src/pages/settings/Settings.css`
  - contient des variables `--settings-*`, des gradients, couleurs `rgba`, shadows, radius et valeurs typographiques locales a classifier.
- Evidence 4: `frontend/src/styles/token-namespace-registry.md`
  - `--settings-*` est deja classe `semantic-extension` avec owner `frontend/src/pages/settings/Settings.css`.
- Evidence 5: `frontend/src/styles/css-fallback-allowlist.md`
  - `--usage-progress` dans `Settings.css` est la seule exception dynamique Settings actuellement classee.
- Evidence 6: `_condamad/stories/regression-guardrails.md`
  - `RG-044` a `RG-060` consultes avant cadrage.

## 6. Target State

- `frontend/src/pages/settings/Settings.css` consomme des tokens existants, roles typographiques ou variables semantiques `--settings-*` documentees.
- Chaque literal restant est rare, justifie comme `kept-one-off-final` ou `runtime-custom-property` dans l'after, et ne masque aucune dette legacy.
- Aucun fallback CSS non allowliste, alias, compatibility namespace, migration-only namespace, style inline statique, wrapper ou vocabulaire legacy actif n'est ajoute.
- Les guards design-system, token, fallback, inline-style, legacy-style, visual-smoke, lint et build passent sans limitation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - tout namespace nouveau ou modifie doit rester classe.
  - `RG-045` - les valeurs visuelles migrees ne doivent pas revenir non classees.
  - `RG-046` - les repetitions typographiques passent par roles semantiques.
  - `RG-047` - aucun style inline statique ne doit etre introduit.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-049` - aucune surface legacy CSS ne doit etre creee pour contourner la migration.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
  - `RG-051` - `--settings-*` reste page-scoped et ne doit pas etre consomme hors owner.
  - `RG-052` - aucun namespace migration-only ne doit revenir.
  - `RG-053`, `RG-057` - aucune compatibilite runtime frontend ne doit etre recreee en marge du style.
  - `RG-054` - aucune route admin legacy ne doit revenir.
  - `RG-055`, `RG-056`, `RG-058`, `RG-059` - les clusters prediction, UI partagee, chat et App restent proteges.
  - `RG-060` - les commentaires CSS actifs ne doivent pas conserver de vocabulaire No Legacy non classe.
- Non-applicable invariants:
  - Aucun invariant `RG-044` a `RG-060` n'est ignore; ceux qui ne touchent pas `Settings.css` restent des non-goals de preservation.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run test`
  - `npm run lint`
  - `npm run build`
  - scans exacts des literals migres dans `hardcoded-values-after.md`.
- Allowed differences:
  - differences visuelles uniquement si documentees dans `hardcoded-values-after.md` comme equivalent tokenise ou decision finale non legacy.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster est borne a `Settings.css`. | Evidence profile: `baseline_before_after_diff`; AST guard; `npm run test -- design-system`; `rg` baseline. |
| AC2 | Chaque literal Settings a une decision finale. | Evidence profile: `persistent_evidence`; AST guard; `npm run test -- design-system`; `rg` limitation. |
| AC3 | Les valeurs repetables utilisent un owner documente. | Evidence profile: `batch_migration_mapping`; AST guard; command `npm run test -- theme-tokens design-system`. |
| AC4 | Les exceptions restent exactes. | Evidence profile: `allowlist_register_validated`; AST guard; `npm run test -- css-fallback inline-style legacy-style`; `rg` cible. |
| AC5 | Les rendus Settings restent couverts. | Evidence profile: `reintroduction_guard`; AST guard; command `npm run test -- visual-smoke design-system`. |
| AC6 | Les literals migres ne reviennent pas. | Evidence profile: `reintroduction_guard`; AST guard; `npm run test -- design-system theme-tokens`; scans exacts. |
| AC7 | La contrainte No Legacy est respectee. | Evidence profile: `targeted_forbidden_symbol_scan`; AST guard; `npm run test -- legacy-style`; `rg` sans hit. |
| AC8 | Aucune AC n'est `PASS with limitation`. | Evidence profile: `persistent_evidence`; AST guard; `npm run test -- design-system`; `rg` final sans hit. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline de `Settings.css` uniquement. (AC: AC1, AC2)
- [ ] Task 2 - Classer chaque valeur avec une decision finale sans legacy. (AC: AC2, AC7, AC8)
- [ ] Task 3 - Migrer les valeurs repetables vers tokens, roles ou variables semantiques documentees. (AC: AC3)
- [ ] Task 4 - Mettre a jour les registres design-system seulement si un owner durable ou une exception exacte change. (AC: AC3, AC4)
- [ ] Task 5 - Ajouter ou ajuster la garde anti-retour exacte du cluster Settings. (AC: AC4, AC6, AC7)
- [ ] Task 6 - Persister l'after, les scans zero-hit et l'evidence finale AC par AC sans limitation. (AC: AC2, AC6, AC7, AC8)
- [ ] Task 7 - Executer les validations frontend, lint, build et validation story. (AC: AC5, AC8)

## 9. Mandatory Reuse / DRY Constraints

- Reuse les fichiers design-system canoniques: `design-tokens.css`, `theme.css`, `premium-theme.css`, `token-namespace-registry.md` et `typography-roles.md`.
- Reuse le namespace `--settings-*` deja classe pour les roles visuels Settings page-scoped.
- Reuse `--usage-progress` uniquement comme custom property runtime dynamique deja allowlistee.
- Do not recreate local variables for a visual role already covered by `--color-*`, `--surface-*`, `--radius-*`, `--shadow-*`, `--space-*`, `--premium-*` or `--type-*`.
- Shared abstraction allowed only if elle retire une duplication reelle dans `Settings.css` et reste documentee dans le registre applicable.

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

- `legacy`, `Legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` dans les fichiers applicatifs touches.
- `var(--token, literal)` ou tout fallback CSS literal non allowliste dans les fichiers touches.
- nouveau namespace non documente dans `frontend/src/styles/token-namespace-registry.md`.
- consommation de `--settings-*` hors `frontend/src/pages/settings/Settings.css`.
- modification de comportement dans composants React, clients API, routes ou stores.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Settings visual values | design tokens, typography roles, or documented `--settings-*` semantic vars | repeated hardcoded literals in `Settings.css` |
| Dynamic usage progress | exact `--usage-progress` allowlist | fallback literal or static inline style |
| Cluster evidence | story before/after artifacts | undocumented local decisions |
| Anti-return guard | `frontend/src/tests/design-system-guards.test.ts` or equivalent guard test | manual-only review |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-07-0017/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-07-0017/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-07-0017/02-finding-register.md`
- `_condamad/audits/frontend-design-system/2026-05-07-0017/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/settings/Settings.css` - migrer valeurs visuelles/typographiques du cluster Settings.
- `frontend/src/styles/token-namespace-registry.md` - seulement si un namespace semantic durable est cree ou modifie.
- `frontend/src/styles/typography-roles.md` - seulement si un role durable manquant est cree.
- `frontend/src/styles/css-fallback-allowlist.md` - seulement si l'evidence `--usage-progress` change, sans elargir l'exception.
- `frontend/src/tests/design-system-guards.test.ts` - ajouter la garde anti-retour exacte des literals Settings migres.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture anti-retour du cluster Settings.
- `frontend/src/tests/theme-tokens.test.ts` - validation registre si namespace ajoute.
- `frontend/src/tests/css-fallback-policy.test.ts` - preservation des fallbacks exacts.
- `frontend/src/tests/inline-style-policy.test.ts` - preservation absence de styles inline statiques.
- `frontend/src/tests/legacy-style-policy.test.ts` - preservation absence de surface legacy.

Files not expected to change:

- `frontend/package.json` - aucune dependance ou script nouveau.
- `frontend/src/pages/settings/Settings.tsx` - comportement React hors scope, sauf retrait mecanique d'une classe devenue morte apres preuve.
- `frontend/src/App.css` - cluster explicitement separe.
- `frontend/src/pages/HelpPage.css` - cluster deja couvert par une story dediee.
- `backend/app/main.py` - aucun backend dans ce scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run test
npm run lint
npm run build
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/settings/Settings.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/settings/Settings.css
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/settings/Settings.css
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/settings/Settings.css
rg -n -- "--settings-" src --glob "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: la migration Settings modifie involontairement les etats abonnement ou usage.
  - Guardrail: visual-smoke, tests Settings cibles si existants et comportement React hors scope.
- Risk: le cluster s'elargit vers autres pages ou App.
  - Guardrail: AC1 borne les fichiers exacts et fichiers hors scope.
- Risk: des literals sont remplaces par variables locales non documentees ou fallbacks.
  - Guardrail: `RG-044`, `RG-048`, scans No Legacy et registre de tokens.
- Risk: une AC partiellement satisfaite est acceptee.
  - Guardrail: AC8 interdit `PASS with limitation` et impose evidence finale sans limitation.

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

- `_condamad/audits/frontend-design-system/2026-05-07-0017/03-story-candidates.md#SC-001` - source de la story.
- `_condamad/audits/frontend-design-system/2026-05-07-0017/02-finding-register.md#F-002` - constat principal.
- `_condamad/audits/frontend-design-system/2026-05-07-0017/00-audit-report.md` - contexte, guardrails applicables et liste exhaustive F-002.
- `frontend/src/pages/settings/Settings.css` - cluster choisi.
- `frontend/src/styles/token-namespace-registry.md` - owner `--settings-*`.
- `frontend/src/styles/css-fallback-allowlist.md` - exception dynamique `--usage-progress`.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
