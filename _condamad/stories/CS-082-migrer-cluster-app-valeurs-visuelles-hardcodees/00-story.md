# Story CS-082 migrer-cluster-app-valeurs-visuelles-hardcodees: Migrer le cluster App de valeurs visuelles hardcodees

Status: done

## 1. Objective

Migrer `frontend/src/App.css` vers les tokens, roles typographiques et variables semantiques documentees.
Le comportement React reste inchange.
Aucun legacy ne doit rester et aucune AC ne peut etre acceptee en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md#SC-001`
- Reason for change: `F-002` signale encore 66 fichiers applicatifs frontend avec literals visuels ou typographiques.
  `App.css` est le cluster coherent recommande avec la densite la plus forte.

## 3. Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Capturer un inventaire before/after des literals de `frontend/src/App.css`.
  - Migrer les couleurs, gradients, shadows, radius et valeurs typographiques repetables vers tokens existants, roles typographiques ou variables semantiques documentees.
  - Mettre a jour les registres design-system si un namespace semantic durable est cree ou modifie.
  - Ajouter ou etendre une garde anti-retour exacte pour les literals App migres.
- Out of scope:
  - Migrer les 65 autres fichiers de l'inventaire F-002.
  - Modifier les composants React, routes, hooks, stores, appels API ou comportements applicatifs.
  - Modifier les clusters deja proteges par `CS-073`, `CS-078`, `CS-079` ou `CS-081`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-055`, `RG-056`, `RG-058` ou `RG-059`.
  - Ne pas creer de namespace `legacy`, `compatibility`, `migration-only`, alias, shim, fallback ou re-export.
  - Ne pas conserver de dette sous forme de TODO, exception large, limitation acceptee ou `PASS with limitation`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de valeurs visuelles dans un fichier applicatif dense vers les owners canoniques du design-system.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les differences visuelles sont limitees aux equivalents tokenises documentes dans l'artefact after.
  - Les composants React, props, imports, routes, payloads et etats utilisateur restent inchanges.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une valeur du cluster ne peut pas recevoir une decision finale sans garder une compatibilite, un fallback ou une limitation.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest et smoke frontend prouvent que les surfaces rendues par `App.css` restent valides apres migration. |
| Baseline Snapshot | yes | Les artefacts before/after bornent les valeurs App migrees. |
| Ownership Routing | yes | Les decisions visuelles doivent etre routees vers tokens, roles typographiques ou namespace semantic documente. |
| Allowlist Exception | yes | Les allowlists inline-style, css-fallback et legacy-style doivent rester exactes et ne pas etre elargies pour ce cluster. |
| Contract Shape | no | Aucun contrat API, DTO, route, payload ou client genere n'est modifie. |
| Batch Migration | yes | Les valeurs sont migrees par sous-surfaces coherentes de `App.css`. |
| Reintroduction Guard | yes | Les literals App migres ne doivent pas revenir silencieusement. |
| Persistent Evidence | yes | Les scans, decisions finales et validations doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard executable in `frontend/src/tests/design-system-guards.test.ts`.
  - `frontend/src/tests/theme-tokens.test.ts`.
  - `frontend/src/tests/css-fallback-policy.test.ts`.
  - `frontend/src/tests/inline-style-policy.test.ts`.
  - `frontend/src/tests/visual-smoke.test.ts` if present after inspection.
- Secondary evidence:
  - scans `rg` cibles sur `frontend/src/App.css`.
- Static scans alone are not sufficient because:
  - les surfaces applicatives rendues via `App.css` doivent rester couvertes par des tests frontend executables.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - chaque valeur du cluster a une decision finale.
  - decisions autorisees: `migrated`, `registered-semantic-owner` ou `kept-one-off-final`.
  - aucun TODO, legacy, fallback non classe ou limitation.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleurs et surfaces App | tokens globaux existants, `--premium-*`, `--astro-*` ou namespace semantic documente | literals locaux repetes ou aliases non registres |
| Typographie App | `frontend/src/styles/typography-roles.md` et tokens `--type-*` existants | tailles, poids, line-height ou letter-spacing repetes sans role |
| Radius, spacing, elevation | tokens shape/space/shadow ou variable semantique documentee | fallback literal, namespace migration-only ou copie locale |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | existing policy entries | Exact source; no broad App exception. | Classified entries only. |
| `frontend/src/tests/inline-style-allowlist.ts` | dynamic inline-style entries | Exact source; no App inline exception. | Permanent for classified entries only. |

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
| App shell | hardcoded layout literals | tokens or semantic vars | `App.css` | design-system | after scan | fallback required |
| Astro/profile | `--astro-*` or semantic vars | registry owner | `App.css` | theme-tokens | registry check | undocumented namespace |
| Typography | sizes/weights/colors | type roles and tokens | `App.css` | visual-smoke | after scan | unbounded visual drift |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before baseline | `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/hardcoded-values-before.md` | Borne fichiers et valeurs initiales. |
| After evidence | `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/hardcoded-values-after.md` | Persiste decisions finales et scans. |
| Final validation | `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/generated/10-final-evidence.md` | Persiste commandes et resultats. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.
- Architecture guard against reintroduction: les literals migres du cluster App echouent s'ils reviennent sans classification finale.
- Deterministic source: forbidden symbols listed in `hardcoded-values-after.md`, tests design-system et scans `rg`.
- Required forbidden examples:
  - hex/rgb/hsl/rgba migres du cluster App.
  - `font-size`, `font-weight`, `line-height`, `letter-spacing` migres.
  - `box-shadow`, `border-radius`, gradients ou `var(--token, literal)` migres.
- Guard evidence: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-2320/02-finding-register.md#F-002`
  - 66 fichiers applicatifs frontend conservent des literals visuels ou typographiques.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md#E-015` - `App.css` est le plus gros cluster detecte avec 515 hits.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md#SC-001`
  - recommande un cluster coherent, avec `App.css` comme premier candidat par densite.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-044` a `RG-059` consultes avant cadrage.
- Evidence 5: scan local du 2026-05-06 - `rg` sur `frontend/src/App.css` montre des rgba, gradients, radius, shadows et valeurs typographiques hardcodees.

## 6. Target State

- `frontend/src/App.css` consomme des tokens existants, roles typographiques ou variables semantiques documentees.
- Les literals restants, s'il y en a, sont rares, justifies comme one-off final dans l'after, et ne masquent aucune dette legacy.
- Aucun fallback CSS, alias, compatibility namespace, migration-only namespace, style inline statique ou wrapper n'est ajoute.
- Les validations frontend passent sans limitation et les preuves sont persistantes.

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
  - `RG-059` - le cluster App migre ne doit pas reintroduire ses literals hors owners documentes.
- Non-applicable invariants:
  - `RG-051` - la story ne touche pas la consommation cross-page `--settings-*`.
  - `RG-052` - la story ne traite pas un namespace migration-only actif.
  - `RG-053`, `RG-057` - aucune compatibilite runtime frontend n'est dans ce scope.
  - `RG-054` - aucune route admin legacy n'est dans ce scope.
  - `RG-055`, `RG-056`, `RG-058` - les clusters prediction, UI partagee et chat ne sont pas modifies.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - scans exacts des literals migres dans `hardcoded-values-after.md`.
  - `npm run lint` et `npm run build`.
- Allowed differences:
  - differences visuelles uniquement si documentees dans `hardcoded-values-after.md` comme equivalent tokenise.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster est borne a `App.css`. | Evidence profile: `baseline_before_after_diff`; before artifact avec commande `rg`. |
| AC2 | Chaque literal App a une decision finale. | Evidence profile: `persistent_evidence`; command `rg -n "PASS with limitation|legacy|fallback" hardcoded-values-after.md`. |
| AC3 | Les valeurs repetables utilisent un owner documente. | Evidence profile: `batch_migration_mapping`; `npm run test -- theme-tokens design-system`. |
| AC4 | Les guards de style interdit restent verts. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback inline-style legacy-style`. |
| AC5 | Les surfaces rendues restent couvertes. | Evidence profile: `runtime_guard`; `npm run test -- visual-smoke design-system`. |
| AC6 | Les literals App migres ne peuvent pas revenir. | Evidence profile: `reintroduction_guard`; garde exacte dans `design-system-guards.test.ts`. |
| AC7 | Aucun livrable n'a d'AC partielle. | Evidence profile: `persistent_evidence`; command `rg -n "PASS with limitation|PARTIAL|TODO" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline de `App.css` uniquement. (AC: AC1, AC2)
- [ ] Task 2 - Classer chaque valeur avec une decision finale sans legacy. (AC: AC2, AC7)
- [ ] Task 3 - Migrer les valeurs repetables vers tokens, roles ou variables semantiques documentees. (AC: AC3)
- [ ] Task 4 - Mettre a jour `token-namespace-registry.md` ou `typography-roles.md` uniquement si un owner durable est cree ou modifie. (AC: AC3, AC4)
- [ ] Task 5 - Ajouter ou ajuster la garde anti-retour exacte du cluster App. (AC: AC4, AC6)
- [ ] Task 6 - Executer les validations frontend et persister l'evidence finale sans limitation. (AC: AC5, AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css` et `frontend/src/styles/premium-theme.css`.
- Reuse `frontend/src/styles/token-namespace-registry.md` et `frontend/src/styles/typography-roles.md`.
- Reuse les tokens `--astro-*` deja declares pour les roles astrologer card dans `App.css`.
- Do not recreate local variables for a visual role already covered by `--color-*`, `--surface-*`, `--radius-*`, `--shadow-*`, `--space-*`, `--premium-*` or `--type-*`.
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
- `var(--token, literal)` ou tout fallback CSS literal dans les fichiers touches.
- nouveau namespace non documente dans `frontend/src/styles/token-namespace-registry.md`.
- modification de comportement dans `frontend/src/App.tsx`, clients API, routes ou stores.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| App visual values | design tokens, premium tokens, typography roles, or documented semantic vars | repeated hardcoded literals in `App.css` |
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

- `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-2320/02-finding-register.md`
- `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/App.css`
- `frontend/src/App.tsx`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - migrer valeurs visuelles/typographiques du cluster App.
- `frontend/src/styles/token-namespace-registry.md` - seulement si un namespace semantic durable est cree ou modifie.
- `frontend/src/styles/typography-roles.md` - seulement si un role durable manquant est cree.
- `frontend/src/tests/design-system-guards.test.ts` - ajouter la garde anti-retour exacte des literals App migres.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture anti-retour du cluster App.
- `frontend/src/tests/theme-tokens.test.ts` - validation registre si namespace ajoute.
- `frontend/src/tests/css-fallback-policy.test.ts` - preservation des fallbacks exacts.
- `frontend/src/tests/inline-style-policy.test.ts` - preservation absence de styles inline statiques.

Files not expected to change:

- `frontend/package.json` - aucune dependance ou script nouveau.
- `frontend/src/App.tsx` - comportement React hors scope, sauf retrait mecanique d'une classe devenue morte apres preuve.
- `frontend/src/pages/ChatPage.css` - cluster deja couvert par `CS-081`.
- `frontend/src/pages/HelpPage.css` - cluster deja couvert par `CS-073`.
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
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/App.css
rg -n "PASS with limitation" ../_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: la migration App modifie involontairement le rendu global.
  - Guardrail: visual-smoke, design-system guards et artefact after.
- Risk: le cluster s'elargit vers composants React, routes ou autres pages.
  - Guardrail: AC1 borne les fichiers exacts et fichiers hors scope.
- Risk: des literals sont remplaces par variables locales non documentees ou fallbacks.
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

- `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md#SC-001` - source de la story.
- `_condamad/audits/frontend-design-system/2026-05-06-2320/02-finding-register.md#F-002` - constat principal.
- `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md#E-014` - scan large restant.
- `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md#E-015` - densite du cluster `App.css`.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
