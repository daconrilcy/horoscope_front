# Story CS-125 fermer-taxonomie-variables-app-restantes: Fermer la taxonomie des variables App restantes

Status: done

## 1. Objective

Fermer `F-001` en transformant l'inventaire `--app-*` restant de `frontend/src/App.css` en taxonomie deterministe.
Sorties admises: primitives App generiques conservees, owners semantiques documentes, extractions vers owners existants, ou suppressions avec migrations.
La story doit produire une preuve de fermeture complete, sans `PASS with limitation` ni residual in-domain cache.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md#SC-001`
- Reason for change: `F-001` prouve que `App.css` conserve encore 442 variables `--app-*`.
  Les prefixes non generiques `person`, `people`, `activity`, `premium`, `flow`, `summary`, `precision`, `evidence`, `chat` et `usage` ne sont pas fermes par CS-121 a CS-124.

## 3. Domain Boundary

- Domain: frontend-app-css-standardization
- In scope:
  - `frontend/src/App.css`
  - consommateurs TSX exacts des classes App retournes par le scan des primitives App, `precision-badge`, `evidence-pill` et `evidence-tags`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md` seulement si des roles typographiques sont modifies
- Out of scope:
  - backend, API, auth, billing, DB
  - refactor de CSS page-scoped hors extraction directe depuis `App.css`
  - decomposition React non necessaire a la migration de classes App
- Explicit non-goals:
  - ne pas changer le rendu fonctionnel ou les parcours utilisateur
  - ne pas introduire de dossier backend
  - ne pas affaiblir `RG-044` a `RG-050`, `RG-059`, `RG-061`, `RG-075`
  - ne pas conserver un prefix `--app-*` non classe
  - ne pas creer d'alias, shim, wrapper, fallback silencieux ou exception wildcard

## 4. Operation Contract

- Operation type: converge
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story ferme un catalogue de namespaces CSS en routant chaque prefix `--app-*` vers une decision persistante et testable.
- Behavior change allowed: no
- Behavior change constraints:
  - le rendu doit rester equivalent hors changements de nommage/ownership CSS
  - les differences autorisees se limitent aux noms de variables/classes et aux emplacements owner
  - la migration vers des primitives existantes est autorisee; conserver l'ancienne surface comme remplacement ne l'est pas
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un prefix non generique doit rester contrat public permanent dans `App.css` sans owner source-backed.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard Vitest/AST design-system devient la source executable de la taxonomie acceptee. |
| Baseline Snapshot | yes | Le nombre et les prefixes `--app-*` doivent etre compares avant/apres. |
| Ownership Routing | yes | Chaque prefix restant doit avoir un owner canonique ou une extraction. |
| Allowlist Exception | yes | Les prefixes conserves doivent etre exacts, source-backed et sans wildcard. |
| Contract Shape | no | Aucun contrat API, DTO, route, schema ou client genere n'est touche. |
| Batch Migration | yes | Les familles de prefixes doivent etre traitees par lots independants avec preuve no-shim. |
| Reintroduction Guard | yes | Une garde positive doit bloquer les futurs prefixes App non autorises. |
| Persistent Evidence | yes | Les inventaires et decisions doivent etre persistes dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts` validant la liste positive des prefixes App acceptes dans `App.css`.
- Secondary evidence:
  - scans `rg` sur `frontend/src/App.css`, `frontend/src/**/*.tsx`, `frontend/src/styles/token-namespace-registry.md` et `frontend/src/tests/design-system-allowlist.ts`.
- Static scans alone are not sufficient for this story because:
  - la politique durable doit echouer en test Vitest si un prefix non classe revient, pas seulement etre constatee manuellement.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-after.md`
- Expected invariant:
  - zero prefix `--app-*` non classe; baisse ou justification source-backed de chaque prefix non generique observe dans E-013.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Primitives App generiques | `frontend/src/App.css` avec prefix documente | fichier page/feature si la classe est reutilisable globalement |
| Style page/feature extrait de `App.css` | stylesheet existant du owner page/feature | nouveau dossier backend ou alias conserve dans `App.css` |
| Exception de prefix conserve | `frontend/src/styles/token-namespace-registry.md` + allowlist exacte | wildcard, seuil global, regex permissive |
| Guard de taxonomie App | `frontend/src/tests/design-system-guards.test.ts` | commentaire manuel ou audit non executable |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | prefixes App conserves un par un | owner App generique ou extension source-backed | permanence documentee ou expiry datee |
| `frontend/src/styles/token-namespace-registry.md` | owners App restants | registre canonique des namespaces CSS | aucune entree temporaire sans condition de sortie |

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
| prefix decision table | all App prefixes | after artifact and registry | none unless renamed | design-system tests | one decision per prefix | unknown prefix |
| page/feature extraction | page/feature prefixes | owner stylesheet or App primitive | exact TSX consumers | targeted tests | zero-hit or exact keep | ambiguous owner |
| residual visuals | `precision`, `evidence` | prefix owner here; class policy in CS-126 | exact consumers | targeted tests | no alias | public API decision |

Closure map:

- Total affected surface: all `--app-*` variables in `frontend/src/App.css`, with E-013 prefixes as mandatory minimum.
- Batches included in this story: complete prefix classification and every migration needed to close `F-001`.
- Batches intentionally deferred: none for `F-001`; `precision/evidence` prefix ownership must be classified here.
- Related follow-up scope: CS-126 closes `F-002` for the exact `precision/evidence` class and guard policy.
- Stop condition for the source finding: no unclassified `--app-*` prefix remains in `App.css`.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before prefix inventory | `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-before.md` | reproduire E-013 |
| after prefix inventory | `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-after.md` | prouver la decision finale pour chaque prefix |
| final evidence | `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/generated/10-final-evidence.md` | conserver les commandes, resultats et scans de fermeture |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- unclassified App prefixes for `person`, `people`, `activity`, `premium`, `flow`, `summary`, `precision`, `evidence`, `chat`, or `usage` in `frontend/src/App.css`
- any new `--app-*` prefix absent from the positive registry
- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only` in `frontend/src/App.css`

Guard evidence:

- Evidence profile: `reintroduction_guard`.
  `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` checks the positive prefix registry and No Legacy vocabulary.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md#F-001`
- Closure proof required: before/after prefix inventory, positive guard, zero unclassified prefix scan, lint and build.
- Known residual in-domain work: none
- Deferred non-domain concerns: page-scoped CSS outside direct extraction from `App.css`.

## 5. Current State Evidence

- Evidence 1: audit E-013 - App prefix counts include `person=124`, `activity=59`, `summary=26`, `flow=17`, `premium=15`, `precision=14`, `evidence=13`.
- Evidence 2: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/00-audit-report.md` - closure map requires classifying every remaining `--app-*` prefix.
- Evidence 3: CS-121 to CS-124 story files - prior App CSS convergence stories are done but partial for this residual.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.
- Evidence 5: `frontend/src/tests/design-system-guards.test.ts` - current App specificity guard exists but the audit says it is narrow.

## 6. Target State

- Every `--app-*` first semantic prefix in `App.css` appears in a persisted decision table.
- `App.css` keeps only generic App primitives or documented semantic extensions.
- `precision/evidence` prefixes have a source-backed owner decision even when detailed class migration is executed by CS-126.
- Page/feature-owned names are extracted to existing owner stylesheets or replaced by primitives without aliases.
- `design-system-guards.test.ts` fails on new non-classified App prefixes.
- `token-namespace-registry.md` mirrors only owners intentionally retained.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - namespace CSS frontend must remain classified.
  - `RG-045` - migrated visual literals must not return outside tokens.
  - `RG-046` - typography roles remain canonical when typography is touched.
  - `RG-047` - TSX consumers must not receive static inline styles during migration.
  - `RG-048` - CSS fallbacks remain classified.
  - `RG-049` - no unclassified legacy style surface may be retained.
  - `RG-050` - design-system guards remain executable and exact.
  - `RG-059` and `RG-061` - active `App.css` declarations stay tokenized and guarded.
  - `RG-075` - App-specific audited words remain forbidden.
  - `RG-076` - this story establishes a positive allowlist for App prefixes.
- Non-applicable invariants:
  - `RG-064` - page architecture is not changed except class consumers.
  - `RG-069` - shared component API ownership is not changed.
- Required regression evidence:
  - before/after taxonomy artifacts, positive guard test, targeted scans, `npm run lint`, `npm run build`.
- Allowed differences:
  - CSS selector/variable names and owner stylesheet location only when backed by the decision table.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline reproduces current App prefix inventory. | Baseline profile; `app-prefix-taxonomy-before.md`; `rg -- "--app-" src/App.css` from `frontend`. |
| AC2 | Every App prefix has an explicit final decision. | Allowlist evidence; `app-prefix-taxonomy-after.md`; `npm run test -- design-system`. |
| AC3 | `precision/evidence` prefix ownership is classified. | Allowlist evidence; `app-prefix-taxonomy-after.md`; `npm run test -- design-system`. |
| AC4 | Non-generic prefixes have a source-backed decision. | Batch mapping; `npm run test -- design-system`; No Legacy scan from `frontend`. |
| AC5 | App guard uses a positive accepted-prefix registry. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens`. |
| AC6 | Retained-owner governance is synchronized. | Evidence profile: `allowlist_register_validated`; `npm run test -- theme-tokens`; registry scan. |
| AC7 | Frontend validates after migration. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`, `npm run build`, targeted tests from affected TSX consumers. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture the baseline prefix inventory and consumer inventory. (AC: AC1)
  - [ ] Write `app-prefix-taxonomy-before.md` with counts, commands, and E-013 mandatory prefixes.
  - [ ] Record exact TSX consumers for any class selector moved or renamed.

- [ ] Task 2 - Build the prefix decision table. (AC: AC2, AC3, AC6)
  - [ ] Classify every first semantic prefix under `--app-*`.
  - [ ] Update `token-namespace-registry.md` only for retained owners.
  - [ ] Add exact allowlist entries only when backed by owner and permanence/expiry.

- [ ] Task 3 - Migrate or remove non-generic owners. (AC: AC4, AC7)
  - [ ] Move page/feature-owned CSS to existing owner stylesheets or replace with App primitives.
  - [ ] Update only exact TSX class consumers needed by moved selectors.
  - [ ] Do not keep old class names, variable aliases, or compatibility selectors.

- [ ] Task 4 - Harden the guard. (AC: AC5, AC6)
  - [ ] Update `design-system-guards.test.ts` to validate the positive accepted-prefix registry.
  - [ ] Ensure exceptions are exact and fail on unknown prefixes.

- [ ] Task 5 - Persist after evidence and run validation. (AC: AC1, AC5, AC7)
  - [ ] Write `app-prefix-taxonomy-after.md` and `generated/10-final-evidence.md`.
  - [ ] Run lint, build, tests, and negative scans.

## 9. Mandatory Reuse / DRY Constraints

- Reuse existing App primitives before creating a new style family:
  `.app-page`, `.app-section`, `.app-stack`, `.app-grid`, `.app-card`, `.app-panel`, `.app-state`, `.app-badge`, `.app-avatar`, `.app-modal`, `.app-actions`, `.app-list`.
- Reuse existing parsing/helpers in `frontend/src/tests/design-system-guards.test.ts`.
- Reuse `frontend/src/tests/design-system-allowlist.ts` for exact exceptions only.
- Do not recreate a second namespace registry outside `frontend/src/styles/token-namespace-registry.md`.
- Shared abstraction allowed only if at least two active consumers move to it in this story and it has a documented owner.

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

- wildcard allowlist entries for `--app-*`
- broad folder exceptions
- `PASS with limitation`
- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only`
- unclassified `--app-*` prefixes
- new `backend/**` paths

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: prefix or selector is referenced by first-party production code and is the canonical owner.
- `external-active`: prefix or selector is referenced by public docs, generated links, analytics, or explicit audit evidence.
- `historical-facade`: prefix or selector exists only to preserve an older CSS surface.
- `dead`: prefix or selector has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

## 12. Removal Audit Format

Required audit table in `app-prefix-taxonomy-after.md`:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Generic App primitives | `frontend/src/App.css` | page/feature semantic prefixes in `App.css` |
| Namespace registry | `frontend/src/styles/token-namespace-registry.md` | audit-only notes or comments |
| App CSS guard | `frontend/src/tests/design-system-guards.test.ts` | manual grep without executable guard |
| Exact exceptions | `frontend/src/tests/design-system-allowlist.ts` | wildcard or folder-wide exception |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving an old CSS variable as alias
- preserving an old class selector as wrapper
- replacing deletion with a compatibility selector
- keeping a stale namespace only to satisfy tests

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/00-audit-report.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/01-evidence-log.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md`
- `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md`
- `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/00-story.md`
- `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/00-story.md`
- `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/App.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - migrate, delete, or retain classified `--app-*` prefixes and related selectors.
- `frontend/src/tests/design-system-guards.test.ts` - enforce accepted App prefix registry.
- `frontend/src/tests/design-system-allowlist.ts` - exact accepted prefixes/exceptions.
- `frontend/src/styles/token-namespace-registry.md` - source-backed retained owners.
- `frontend/src/styles/typography-roles.md` - only if typographic variables move to roles.
- exact TSX consumers returned by the required `rg` command - only when class names change.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- targeted Vitest files matching affected consumers found by `rg`

Files not expected to change:

- `backend/**` - outside domain.
- `frontend/package.json` - no dependency change.
- `frontend/src/pages/**/*.css` unless it is the existing owner for CSS extracted from `App.css`.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css
rg -n -- "--app-(person|people|activity|premium|flow|summary|precision|evidence|chat|usage)-" src/App.css
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md
```

The second `rg` command may return only entries explicitly documented as retained.
Any undocumented hit fails the story.

## 22. Regression Risks

- Risk: extraction breaks styling for active TSX consumers.
  - Guardrail: consumer inventory before edits plus targeted component/page tests.
- Risk: positive allowlist becomes too broad.
  - Guardrail: exact prefix list, no wildcard, no count threshold.
- Risk: typography values move without role documentation.
  - Guardrail: update `typography-roles.md` only when typographic roles change and run `theme-tokens`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback, compatibility, legacy, shim, alias, TODO, or hidden residual work.

## 24. References

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md#SC-001` - source candidate.
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md#F-001` - source finding.
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/01-evidence-log.md#E-013` - prefix evidence.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
