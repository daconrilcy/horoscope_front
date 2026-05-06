# Story CS-077 supprimer-redirects-legacy-admin-frontend: Supprimer les redirects legacy admin frontend

Status: ready-to-dev

## Objective

Supprimer les redirects frontend legacy `/admin/pricing`, `/admin/monitoring` et
`/admin/personas`. La decision produit est explicite: aucun legacy ne doit
rester. Ces routes ne doivent pas etre conservees comme redirects, aliases,
facades ou routes compatibles.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-004`
- Reason for change: `F-007` montre trois redirects admin legacy actifs et testes sans politique de compatibilite explicite.

## Domain Boundary

- Domain: `frontend-routing`
- In scope:
  - Supprimer les routes `/admin/pricing`, `/admin/monitoring` et `/admin/personas` de `routes.tsx`.
  - Mettre a jour `AdminPage.test.tsx` pour prouver leur absence ou leur non-resolution.
  - Ajouter des scans no-return pour les anciens chemins et commentaires legacy.
- Out of scope:
  - Compatibilites runtime consultation/prediction, couvertes par `CS-076`.
  - Backend routing.
  - Refonte navigation admin canonique.
- Explicit non-goals:
  - Ne pas affaiblir `RG-049` ou `RG-050`.
  - Ne pas repointer les anciens chemins vers des routes canoniques.
  - Ne pas accepter de `PASS with limitation`.

## Operation Contract

- Operation type: remove
- Primary archetype: frontend-route-removal
- Archetype reason: la story retire des routes frontend historiques et leurs tests de compatibilite.
- Behavior change allowed: yes
- Behavior change constraints:
  - Les anciennes URLs admin ne doivent plus matcher comme routes supportees.
  - Les routes admin canoniques existantes doivent continuer a fonctionner.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une preuve externe active impose la conservation publique d'une ancienne URL; la decision actuelle n'autorise aucun legacy interne.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests de routing admin prouvent le comportement. |
| Baseline Snapshot | yes | L'inventaire before/after des routes prouve la suppression. |
| Ownership Routing | yes | Les routes canoniques admin doivent rester les seuls owners. |
| Allowlist Exception | no | Aucune exception de redirect legacy n'est autorisee. |
| Contract Shape | yes | La shape de route frontend publique change par suppression. |
| Batch Migration | no | La suppression vise trois routes exactes. |
| Reintroduction Guard | yes | Les anciens paths ne doivent pas revenir. |
| Persistent Evidence | yes | L'audit route before/after doit etre conserve. |

## Runtime Source of Truth

- Primary source of truth:
  - frontend route table in `frontend/src/app/routes.tsx`
  - `frontend/src/tests/AdminPage.test.tsx`
- Secondary evidence:
  - scans `rg` sur route table et tests.
- Static scans alone are not sufficient because:
  - le routeur doit prouver que les anciennes URLs ne sont plus supportees.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-077-supprimer-redirects-legacy-admin-frontend/admin-legacy-routes-before.md`.
- Comparison after implementation: `_condamad/stories/CS-077-supprimer-redirects-legacy-admin-frontend/admin-legacy-routes-after.md`.
- Expected invariant: zero route frontend active pour `/admin/pricing`, `/admin/monitoring`, `/admin/personas`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin billing/pricing UI | route admin canonique existante apres inspection | `/admin/pricing` redirect legacy |
| Admin monitoring/logs UI | route admin canonique existante apres inspection | `/admin/monitoring` redirect legacy |
| Admin personas UI | route admin canonique existante apres inspection | `/admin/personas` redirect legacy |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune allowlist d'ancienne route admin n'est autorisee.

## Contract Shape

Contract type:
- Frontend route table.
Fields:
- Route path strings and redirect behavior.
Required fields:
- Canonical admin routes only.
Optional fields:
- No optional field for removed legacy paths.
Status codes:
- Unchanged for HTTP; client route absence is asserted by tests.
Serialization names:
- Unchanged.
Frontend type impact:
- Route definitions and tests may change.
Generated contract impact:
- If a route manifest exists after inspection, prove removed paths are absent.

## Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: trois routes exactes sont supprimees par audit de route.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before route audit | `admin-legacy-routes-before.md` | Capturer routes, tests et consommateurs connus avant suppression. |
| After route audit | `admin-legacy-routes-after.md` | Prouver absence des anciens chemins et tests adaptes. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: les anciens paths admin echouent s'ils sont reintroduced dans routes ou tests de support.
- Deterministic source: frontend route table and forbidden symbols in `routes.tsx`, `AdminPage.test.tsx`, et scans `rg`.
- Required forbidden examples:
  - `/admin/pricing`
  - `/admin/monitoring`
  - `/admin/personas`
  - commentaire `Legacy redirects`
- Guard evidence: `npm run test -- AdminPage`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-007` - redirects admin legacy actifs.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md#E-013` - scan route/test en echec.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - `RG-049` et `RG-050` consultes avant cadrage.

## Target State

- Les trois anciens chemins admin ne sont plus presents dans `routes.tsx`.
- Les tests n'assertent plus un redirect legacy; ils prouvent la politique de suppression.
- Aucun wrapper, alias, redirect ou soft-disable ne preserve les anciennes URLs.
- Les validations passent sans limitation.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - les surfaces legacy frontend doivent etre retirees ou gardees contre retour.
  - `RG-050` - les guards frontend doivent rester executables.
- Non-applicable invariants:
  - `RG-044` - aucun token CSS n'est dans le scope.
  - `RG-047` - aucun style inline n'est dans le scope.
- Required regression evidence:
  - `npm run test -- AdminPage`
  - scans zero-hit des trois anciens paths et du commentaire legacy.
- Allowed differences:
  - les anciennes URLs admin ne sont plus supportees.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline liste les anciennes routes. | Command `npm run test -- frontend/src/tests/AdminPage.test.tsx`; scans in Validation Plan. |
| AC2 | Les trois redirects sont absents de la route table. | Command `npm run test -- frontend/src/tests/AdminPage.test.tsx`; scans in Validation Plan. |
| AC3 | Les tests admin prouvent les routes canoniques. | Evidence profile: `route_absence_runtime`; command `npm run test -- frontend/src/tests/AdminPage.test.tsx`. |
| AC4 | Aucun ancien path admin ne reste. | Command `rg -e "Legacy redirects" -e /admin/pricing src`. |
| AC5 | La reintroduction des anciens paths est gardee. | Evidence profile: `reintroduction_guard`; test ou scan dedie plus `npm run lint`. |

## Implementation Tasks

- [ ] Task 1 - Capturer audit before des anciennes routes admin. (AC: AC1)
- [ ] Task 2 - Supprimer les redirects de `routes.tsx` sans repointage. (AC: AC2, AC4)
- [ ] Task 3 - Mettre a jour `AdminPage.test.tsx` pour la politique de suppression. (AC: AC3)
- [ ] Task 4 - Ajouter ou renforcer un guard no-return sur les anciens paths. (AC: AC4, AC5)
- [ ] Task 5 - Capturer after et executer validations. (AC: AC2, AC3, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse la route table existante et les helpers de test admin existants.
- Do not create a second route registry.
- Shared abstraction allowed only if elle protege les routes canoniques, pas une compatibilite legacy.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `/admin/pricing`
  - `/admin/monitoring`
  - `/admin/personas`
  - `Legacy redirects`

## Removal Classification Rules

- `canonical-active`: route admin actuelle documentee par la route table.
- `external-active`: ancienne URL prouvee par lien public actif; bloque suppression silencieuse.
- `historical-facade`: redirect ancien chemin vers route canonique.
- `dead`: route sans consommateur externe connu.
- `needs-user-decision`: ambiguite externe apres scans.

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete` | Must be deleted under the user decision. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path:
- `_condamad/stories/CS-077-supprimer-redirects-legacy-admin-frontend/admin-legacy-routes-after.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Frontend admin routes | `frontend/src/app/routes.tsx` canonical paths | legacy redirects `/admin/pricing`, `/admin/monitoring`, `/admin/personas` |
| Admin route tests | `frontend/src/tests/AdminPage.test.tsx` | tests asserting legacy redirects |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: redirecting to canonical route, wrapper route, compatibility alias, keeping deprecated route active, soft-disable behavior, or re-export.

## External Usage Blocker

- `external-active` items must not be deleted without a user decision.
- If an item is classified as `external-active`, implementation must stop and
  record exact external evidence and deletion risk. Without such proof, the user
  decision requires deletion.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path may change for this frontend route removal.
- Generated artifact absence: if a generated route manifest, sitemap, static
  route snapshot or generated client navigation artifact exists after inspection,
  prove `/admin/pricing`, `/admin/monitoring` and `/admin/personas` are absent.
- Required evidence: `rg -n '/admin/pricing|/admin/monitoring|/admin/personas' src` and generated artifact scan if such artifact exists.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/AdminPage.test.tsx`

## Expected Files to Modify

Likely files:
- `frontend/src/app/routes.tsx` - supprimer les redirects.
- `frontend/src/tests/AdminPage.test.tsx` - adapter la politique de test.

Likely tests:
- `frontend/src/tests/AdminPage.test.tsx` - absence des anciens redirects et routes canoniques.

Files not expected to change:
- `frontend/src/types/consultation.ts` - compat runtime couverte par `CS-076`.
- `backend/app/main.py` - aucun backend dans le scope.
- `frontend/package.json` - aucune dependance requise.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- AdminPage
npm run lint
rg -n 'Legacy redirects|pricing|monitoring|personas' src/app/routes.tsx src/tests/AdminPage.test.tsx
rg -n '/admin/pricing|/admin/monitoring|/admin/personas' src
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-077-supprimer-redirects-legacy-admin-frontend/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: suppression casse un bookmark admin interne encore utilise.
  - Guardrail: blocker uniquement si preuve externe active, sinon decision produit stricte.
- Risk: route conservee comme redirect renomme.
  - Guardrail: Delete-only rule et scans paths.

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

- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-004`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-007`
- `_condamad/stories/regression-guardrails.md`
