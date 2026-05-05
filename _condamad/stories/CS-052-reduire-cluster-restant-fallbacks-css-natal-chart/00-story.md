# Story CS-052 reduire-cluster-restant-fallbacks-css-natal-chart: Reduire le cluster restant de fallbacks CSS NatalChart

Status: ready-to-dev

## 1. Objective

Reduire un lot borne de fallbacks CSS `var(--token, literal)` en commencant par `frontend/src/pages/NatalChartPage.css`.
Les suppressions ne sont autorisees que lorsque le token canonique est garanti dans l'application et les registres restent synchronises.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-001`
- Reason for change: `F-002` indique 54 exceptions CSS fallback dans 10 fichiers; `NatalChartPage.css` est le cluster prioritaire restant.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Capturer les compteurs before/after des fallbacks du lot choisi, avec `NatalChartPage.css` en point de depart obligatoire.
  - Supprimer uniquement les fallbacks dont le token canonique est garanti par les sources chargees.
  - Synchroniser `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts`.
  - Traiter les aliases `--premium-*` seulement si leur retrait direct est prouve sans decision produit.
- Out of scope:
  - Migration globale des 10 fichiers fallback.
  - Refonte visuelle NatalChart ou premium theme.
  - Migration des styles inline, hardcoded values hors fallback, ou selectors legacy.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-048` ou `RG-050`.
  - Ne pas remplacer un fallback par un autre fallback literal.
  - Ne pas retirer un alias premium ambigu sans decision utilisateur explicite.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story reduit un lot CSS multi-entrees avec baseline, registre et guard anti-retour.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent lorsque le token canonique possede la valeur attendue.
  - Toute difference admise doit etre documentee comme convergence vers token canonique.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un fallback premium ou theme semble compenser un token non garanti, une valeur produit, ou un alias compatibility encore consomme.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards `css-fallback` et `design-system` prouvent l'etat executable des exceptions. |
| Baseline Snapshot | yes | Les compteurs before/after du lot NatalChart sont obligatoires. |
| Ownership Routing | yes | Les decisions visuelles doivent appartenir aux tokens et registres canoniques. |
| Allowlist Exception | yes | Les exceptions restantes doivent rester exactes dans le markdown et l'allowlist executable. |
| Contract Shape | no | Aucun contrat API, DTO, route, schema ou type public n'est modifie. |
| Batch Migration | yes | Le lot peut couvrir plusieurs fallbacks dans `NatalChartPage.css` et fichiers associes si justifie. |
| Reintroduction Guard | yes | Les fallbacks retires ne doivent pas revenir non classes. |
| Persistent Evidence | yes | Les inventories before/after doivent rester auditables dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
- Secondary evidence:
  - Scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Le scan ne prouve pas que le token canonique est garanti ni que les deux registres restent synchronises.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-after.md`
- Expected invariant:
  - Le nombre de fallbacks du lot diminue; chaque fallback conserve est justifie avec condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token CSS garanti | `design-tokens.css` ou `theme.css` | fallback literal local |
| Exception fallback conservee | `css-fallback-allowlist.md` et `design-system-allowlist.ts` | exception implicite dans CSS |
| Alias premium ambigu | decision produit ou registre token | suppression silencieuse |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | fallbacks restants du lot | Exceptions CSS exactes. | Doit diminuer ou rester justifie avec sortie. |
| `frontend/src/tests/design-system-allowlist.ts` | inventaire executable correspondant | Guard Vitest. | Doit correspondre au markdown. |

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
| NatalChart batch | fallbacks in `NatalChartPage.css` | guaranteed tokens | selected CSS | allowlist guards | scans | token/alias not guaranteed |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-before.md` | Capturer hits, compteurs et classification initiale. |
| After inventory | `css-fallbacks-after.md` | Prouver suppressions, exceptions restantes et synchronisation. |

## 4i. Reintroduction Guard

- Guard target: fallbacks supprimes du lot NatalChart et synchronisation des registres.
- Architecture guard against reintroduction required: `npm run test -- css-fallback design-system theme-tokens`.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scan cible des fallbacks CSS.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-002` - 54 exceptions exactes et `NatalChartPage.css` comme cluster dominant.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-001` - demande compteurs before/after et mise a jour des deux registres.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - registre markdown des fallbacks.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist executable design-system.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le lot NatalChart a un inventaire before/after persistant.
- Les fallbacks garantis sont supprimes du CSS et des registres.
- Les fallbacks restants sont classes, exacts, et couverts par les guards.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens restent classes.
  - `RG-048` - les fallbacks CSS restent exacts et classes.
  - `RG-050` - les guards design-system restent executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline sont hors scope.
  - `RG-049` - les selectors legacy sont hors scope sauf si un alias premium impose un blocker documente.
- Required regression evidence:
  - `npm run test -- css-fallback design-system theme-tokens`, scan fallback, artefacts before/after.
- Allowed differences:
  - Diminution des entrees allowlistees et suppression des fallbacks garantis.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline couvre 100% des fallbacks du lot choisi. | Evidence profile: `baseline_snapshot`; `rg -n "var\\(" src/pages/NatalChartPage.css`. |
| AC2 | Chaque fallback supprime a une preuve de token canonique garanti. | Evidence profile: `architecture_guard`; `npm run test -- css-fallback design-system theme-tokens`. |
| AC3 | La synchronisation des registres fallback passe le guard. | Evidence profile: `allowlist_guard`; `npm run test -- css-fallback design-system`. |
| AC4 | Les fallbacks premium ambigus sont bloques ou justifies. | Evidence profile: `blocker_guard`; `rg -n "needs-user-decision\|premium" css-fallbacks-*.md`. |
| AC5 | Aucun nouveau fallback non classe n'est introduit. | Evidence profile: `negative_scan`; scan final `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"`. |
| AC6 | Le frontend reste valide sur le scope touche. | Evidence profile: `frontend_quality`; `npm run test -- css-fallback design-system theme-tokens` et tests cibles existants. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline du lot NatalChart et les compteurs initiaux (AC: AC1)
- [ ] Task 2 - Classer chaque fallback comme `delete`, `keep`, ou `needs-user-decision` (AC: AC2, AC4)
- [ ] Task 3 - Supprimer uniquement les fallbacks classes `delete` (AC: AC2, AC5)
- [ ] Task 4 - Synchroniser `css-fallback-allowlist.md` et `design-system-allowlist.ts` apres les modifications CSS (AC: AC3)
- [ ] Task 5 - Capturer l'after et executer les validations (AC: AC1, AC3, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
- Do not recreate:
  - Registre parallele de fallbacks.
  - Alias premium ou fallback literal de remplacement.
  - Token nouveau sans classification dans le registre.
- Shared abstraction allowed only if:
  - Elle supprime une duplication prouvee du lot et reste documentee dans les registres existants.

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

- Nouveau `var(--token, literal)` non classe.
- Entree markdown sans entree executable correspondante.
- Entree executable sans justification markdown.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: fallback still required because the token is not guaranteed.
- `dead`: fallback removable because the token is guaranteed.
- `needs-user-decision`: product, premium theme, or compatibility ambiguity remains.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must remain registered. |
| `dead` | `delete` | Must be deleted from CSS and registries. |
| `needs-user-decision` | `needs-user-decision` | Must block deletion for that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-before.md`
- `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens disponibles | `design-tokens.css` et `theme.css` | fallback literal dans CSS |
| Exceptions fallback | `css-fallback-allowlist.md` et `design-system-allowlist.ts` | exception implicite |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- replacing one fallback literal with another
- preserving an unregistered compatibility alias
- keeping a removed fallback in any allowlist

## 15. External Usage Blocker

If an item is classified as `needs-user-decision`, it must not be deleted. The dev agent must stop for that item or record explicit user decision with evidence and risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/NatalChartPage.css` - supprimer les fallbacks garantis du cluster prioritaire.
- `frontend/src/styles/css-fallback-allowlist.md` - synchroniser les exceptions restantes.
- `frontend/src/tests/design-system-allowlist.ts` - synchroniser l'allowlist executable.
- `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/css-fallbacks-after.md` - evidence finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/tests/inline-style-allowlist.ts` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- css-fallback design-system theme-tokens
npm run lint
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md
```

## 22. Regression Risks

- Risk: suppression d'un fallback premium encore utile.
  - Guardrail: classification `needs-user-decision` bloque la suppression.
- Risk: registres desynchronises.
  - Guardrail: AC3 exige les guards `css-fallback` et `design-system`.
- Risk: scope trop large.
  - Guardrail: AC1 impose un lot nomme avec `NatalChartPage.css`.

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

- `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-002` - current count and file list.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
