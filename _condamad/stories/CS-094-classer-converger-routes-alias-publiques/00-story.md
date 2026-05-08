# Story CS-094 classer-converger-routes-alias-publiques: Classer et converger les routes alias publiques

Status: ready-to-dev

## 1. Objective

Classer puis converger les routes publiques `/today`, `/natal-chart` et `/birth-profile`.
La decision utilisateur impose qu'aucun legacy ne reste.
Les alias ou redirects historiques doivent etre supprimes sauf preuve externe active bloquante.
Aucune AC ne peut etre acceptee en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-005`
- Reason for change: `F-005` identifie des alias/redirects publics actifs a cote des routes canoniques.

## 3. Domain Boundary

- Domain: `frontend-react-pages/routes`
- In scope:
  - Classer `/today`, `/natal-chart`, `/birth-profile` dans un audit de routes.
  - Supprimer les alias/redirects classes legacy, sans repointage.
  - Mettre a jour les tests router/pages/navigation.
- Out of scope:
  - Refonte des pages `DashboardPage`, `DailyHoroscopePage`, `NatalChartPage` ou `BirthProfilePage`.
  - Backend routing.
  - SEO/sitemap sauf artefact genere existant decouvert.
- Explicit non-goals:
  - Ne pas conserver un redirect pour compatibilite.
  - Ne pas transformer un legacy en alias supporte sans preuve produit explicite.
  - Ne pas accepter de `PASS with limitation`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: route-architecture-convergence
- Archetype reason: la story converge la route table publique vers des routes canoniques explicites et supprime les alias legacy.
- Behavior change allowed: yes
- Behavior change constraints:
  - Les routes canoniques restent fonctionnelles.
  - Les anciennes routes classees legacy ne matchent plus comme surfaces supportees.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une route est prouvee `external-active` par lien public, doc, sitemap ou contrat externe; sinon la decision no-legacy impose suppression.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La route table et les tests router sont la source runtime frontend. |
| Baseline Snapshot | yes | Le before/after des routes prouve les suppressions. |
| Ownership Routing | yes | Chaque page publique doit avoir une route canonique unique. |
| Allowlist Exception | yes | Les blockers externes doivent etre exacts ou absents. |
| Contract Shape | no | Aucun contrat API/DTO n'est modifie. |
| Batch Migration | no | Trois routes exactes sont traitees. |
| Reintroduction Guard | yes | Les alias ne doivent pas revenir. |
| Persistent Evidence | yes | L'audit de routes doit rester persistant. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - frontend route table in `frontend/src/app/routes.tsx`
  - `frontend/src/tests/router.test.tsx`
- Secondary evidence:
  - tests pages et scans des anciens paths.
- Static scans alone are not sufficient because:
  - le routeur doit prouver le comportement de resolution.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/public-route-aliases-before.md`.
- Comparison after implementation: `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/public-route-aliases-after.md`.
- Expected invariant: zero route legacy active pour les alias classes supprimables.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Horoscope du jour | route canonique existante apres inspection | `/today` redirect legacy |
| Theme natal | route canonique existante apres inspection | `/natal-chart` alias legacy |
| Profil naissance | route canonique existante apres inspection | `/birth-profile` redirect legacy |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| route audit | `/today`, `/natal-chart`, `/birth-profile` | blocker uniquement si preuve externe active | sinon suppression obligatoire |

Rules:
- no wildcard;
- no undocumented public alias;
- no redirect compatibility;
- no exception can justify `PASS with limitation`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, DTO, OpenAPI contract, generated client, or backend schema is affected.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: trois routes exactes sont classees et convergent dans un seul lot.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before route audit | `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/public-route-aliases-before.md` | Capturer routes, tests, liens et consommateurs. |
| After route audit | `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/public-route-aliases-after.md` | Prouver suppression ou blocker explicite. |
| Final validation | `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/generated/10-final-evidence.md` | Persister commandes sans limitation. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: test route ou scan qui echoue si un alias supprime revient.
- Deterministic source: `frontend/src/app/routes.tsx`, `frontend/src/tests/router.test.tsx`, page tests.
- Required forbidden examples: `/today`, `/natal-chart`, `/birth-profile` si classes legacy.
- Guard evidence: `npm run test -- router DashboardPage DailyHoroscopePage NatalChartPage BirthProfilePage`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-005` - alias publics actifs beside routes canoniques.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md#E-005` - `/today`, `/natal-chart`, `/birth-profile` dans `routes.tsx`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants frontend consultes avant cadrage.

## 6. Target State

- Les routes canoniques sont documentees dans l'audit after.
- Les alias legacy sont supprimes ou bloquent explicitement si preuve externe active.
- Aucun redirect, alias, wrapper ou fallback ne preserve les anciens chemins.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - les surfaces legacy frontend doivent etre retirees.
  - `RG-050` - les guards frontend restent executables.
  - `RG-054` - les redirects legacy admin ne doivent pas revenir pendant les changements routes.
- Non-applicable invariants:
  - `RG-044` - pas de tokens CSS.
  - `RG-053` - pas de compatibilite runtime payload.
- Required regression evidence:
  - `npm run test -- router DashboardPage DailyHoroscopePage NatalChartPage BirthProfilePage`
  - `npm run lint`
  - scans des paths classes legacy.
- Allowed differences:
  - anciennes URLs legacy non supportees apres suppression.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Chaque alias recoit une classification. | Evidence profile: `removal_audit`; artifact `public-route-aliases-before.md`; command `rg -n "/today" src`. |
| AC2 | Les alias supprimables sont absents. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -n "/today|/natal-chart|/birth-profile" src/app`. |
| AC3 | Les routes canoniques restent testees. | Evidence profile: `runtime_behavior`; runtime evidence `npm run test -- frontend/src/tests/router.test.tsx`. |
| AC4 | `external-active` bloque. | Evidence profile: `allowlist_register_validated`; artifact `public-route-aliases-after.md`; command `rg -n "external-active" route-after.md`. |
| AC5 | Aucun legacy ne reste. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|legacy|fallback" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'audit before des trois alias publics. (AC: AC1)
- [ ] Task 2 - Supprimer les aliases classes supprimables dans `routes.tsx`. (AC: AC2)
- [ ] Task 3 - Mettre a jour tests router/pages pour routes canoniques et absence legacy. (AC: AC3)
- [ ] Task 4 - Ajouter guard anti-retour des paths supprimes. (AC: AC2, AC5)
- [ ] Task 5 - Capturer after, blockers externes eventuels et evidence finale. (AC: AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/app/routes.tsx` comme seule route table.
- Reuse `frontend/src/tests/router.test.tsx` et tests pages existants.
- Do not create a route manifest concurrent.

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
- `/today` si classe legacy.
- `/natal-chart` si classe legacy.
- `/birth-profile` si classe legacy.
- redirect compatibility pour ces paths.
- `PASS with limitation`.

## 11. Removal Classification Rules

- `canonical-active`: route publique deliberement supportee par decision produit explicite.
- `external-active`: route prouvee par docs publiques, sitemap, email, analytics ou lien externe actif.
- `historical-facade`: alias/redirect vers route canonique.
- `dead`: route sans consommateur connu.
- `needs-user-decision`: ambiguite apres scans.

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete` | Must be deleted under the no-legacy decision. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:
- `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/public-route-aliases-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Frontend public routes | `frontend/src/app/routes.tsx` canonical paths | `/today`, `/natal-chart`, `/birth-profile` if classified legacy |
| Route tests | `frontend/src/tests/router.test.tsx` | tests asserting legacy redirects |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: redirecting, wrapper route, compatibility alias, deprecated route active, soft-disable behavior, re-export.

## 15. External Usage Blocker

If an item is classified as `external-active`, implementation must stop and record exact evidence and deletion risk.
Without such proof, the no-legacy decision requires deletion of legacy aliases.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API schema is affected; if a route manifest or sitemap exists after inspection, prove removed aliases are absent.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/app/routes.tsx` - supprimer alias/redirects classes legacy.
- `frontend/src/tests/router.test.tsx` - tester routes canoniques et absence legacy.

Likely tests:
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`

Files not expected to change:
- `frontend/package.json` - aucune dependance.
- `backend/app/main.py` - aucun backend.
- `frontend/src/styles/design-tokens.css` - aucun style.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- router DashboardPage DailyHoroscopePage NatalChartPage BirthProfilePage
npm run lint
rg -n "/today|/natal-chart|/birth-profile" src/app src/tests
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-094-classer-converger-routes-alias-publiques/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: lien externe actif casse.
  - Guardrail: External Usage Blocker.
- Risk: alias conserve comme redirect.
  - Guardrail: Delete-only rule et scans paths.
- Risk: test continue d'encoder le legacy.
  - Guardrail: AC3 et AC5.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- No legacy may remain in the implemented cluster.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-005`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-005`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`
