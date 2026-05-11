# Story CS-145 ajouter-garde-complexite-visuelle-landing: Ajouter une garde anti-complexite visuelle landing

Status: done

## 1. Objective

Ajouter une garde executable qui empeche la reintroduction de complexite
visuelle non classee dans le domaine landing: `@keyframes`, declarations
`animation:` toujours actives et usages `filter` / `backdrop-filter`. La garde
doit utiliser une allowlist exacte par selecteur et raison, sans wildcard.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-003`
- Reason for change: les guards actuels prouvent ownership, absence de timers,
  absence de styles inline et absence d'overflow. Ils ne bornent pas la
  croissance CSS motion/filter apres la simplification hero.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Ajouter ou durcir un test Vitest qui inspecte les CSS landing pour `@keyframes`, `animation:`, `filter` et `backdrop-filter`.
  - Classer toute exception conservee par fichier, selecteur, declaration et raison.
  - Garder les owner groups landing existants et les invariants fond/dark mode.
  - Produire une preuve before/after du budget executable.
- Out of scope:
  - Simplifier le hero ou le menu mobile directement; ces changements sont routes vers `CS-143` et `CS-144`.
  - Interdire globalement transitions hover/focus ou animations hors landing.
  - Ajouter une dependance de parsing CSS.
  - Modifier le backend ou les routes.
- Explicit non-goals:
  - Ne pas creer d'allowlist folder-wide, wildcard ou threshold global vague.
  - Ne pas autoriser `PASS with limitation`.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-085`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story ajoute une garde de test deterministe contre une regression architecturale/visuelle frontend.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le budget actuel ne peut pas etre exprime par
  exceptions exactes apres `CS-143` / `CS-144`, ou si une exception doit rester
  permanente sans condition de sortie.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde doit etre executable dans Vitest et verifier les fichiers reels. |
| Baseline Snapshot | yes | L'audit demande une preuve failing/then passing ou before/after du budget. |
| Ownership Routing | yes | Les exceptions doivent nommer le fichier et selecteur owner exacts. |
| Allowlist Exception | yes | Les animations/filtres conserves doivent etre allowlistes au niveau selecteur. |
| Contract Shape | no | Aucun contrat API, route, schema ou type public n'est modifie. |
| Batch Migration | no | Il ne s'agit pas d'une migration par lots. |
| Reintroduction Guard | yes | C'est l'objet principal de la story. |
| Persistent Evidence | yes | Le budget et les exceptions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `frontend/src/tests/design-system-guards.test.ts` ou `frontend/src/tests/landing-visual-complexity.test.ts`.
  - Test Vitest dans `frontend/src/tests/design-system-guards.test.ts` ou `frontend/src/tests/landing-visual-complexity.test.ts`.
  - Fichiers CSS reels sous `frontend/src/pages/landing` et `frontend/src/layouts/LandingLayout.css`.
- Secondary evidence:
  - Scans `rg` pour `@keyframes`, `animation:`, `filter` et `backdrop-filter`.
- Static scans alone are not sufficient because:
  - le guard doit echouer automatiquement sur ajout non classe, pas seulement documenter un etat manuel.
- Runtime validation command:
  - `cd frontend; npm run test -- design-system visual-smoke LandingPage`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/landing-visual-complexity-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/landing-visual-complexity-after.md`
- Required baseline content:
  - inventaire des keyframes, animations, filters et backdrop filters landing;
  - liste des exceptions actuelles et leur raison;
  - resultat test avant garde quand pertinent.
- Expected invariant:
  - toute croissance motion/filter landing doit etre classee par selecteur exact ou echouer.
- Allowed differences:
  - ajout d'un test et d'un registre exact; pas de changement visuel applicatif attendu.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Guard complexite visuelle landing | `frontend/src/tests/design-system-guards.test.ts` ou `frontend/src/tests/landing-visual-complexity.test.ts` | audit manuel seul |
| Exceptions motion/filter | table exacte dans le test ou artefact story | wildcard path, dossier complet |
| CSS hero/menu inspecte | `frontend/src/pages/landing/LandingPage.css`, `LandingNavbar.css` | `App.css` ou global non landing |

Rules:

- Chaque exception doit inclure fichier, selecteur ou bloc, declaration, raison et condition de sortie.
- Le test doit echouer sur un nouveau `@keyframes`, `animation:` ou filtre non declare.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/pages/landing/LandingPage.css` | exact `@keyframes` name | Unique animation hero prouvee par `CS-143`. | Expire when hero becomes static. |
| `frontend/src/pages/landing/LandingPage.css` | `animation:` on exact selector | Declaration documentee apres simplification. | Must include exit condition in after artifact. |
| `frontend/src/pages/landing/sections/LandingNavbar.css` | `filter` on exact selector | Effet non dominant prouve par `CS-144`. | Selector reason and exit condition required. |

Rules:

- No wildcard exceptions.
- No broad folder allowlist.
- No permanent exception without reason and exit condition.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO ou type public n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la story ajoute un guard, pas une migration par lots.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline complexite visuelle landing | `landing-visual-complexity-before.md` | Inventaire avant et etat des guards actuels. |
| Preuve after complexite visuelle landing | `landing-visual-complexity-after.md` | Budget final, exceptions exactes, tests et scans apres. |

## 4i. Reintroduction Guard

- Guard target:
  - nouveau `@keyframes` landing non classe;
  - nouvelle declaration `animation:` non classee;
  - nouveau `filter` ou `backdrop-filter` permanent non classe;
  - allowlist wildcard ou path-level.
- Forbidden examples:
  - `allowedAnimations: ["*"]`;
  - exception sur `frontend/src/pages/landing/**/*.css`;
  - nouvelle animation infinite sans selecteur exact;
  - filtre menu/hero ajoute sans raison ni condition de sortie.
- Guard command/test:
  - AST architecture guard dans `frontend/src/tests/design-system-guards.test.ts` ou `frontend/src/tests/landing-visual-complexity.test.ts`.
  - `cd frontend; npm run test -- design-system visual-smoke LandingPage`
  - `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-003`
- Closure proof required: deterministic guard, exact exception register, before/after inventory, negative wildcard scan, tests and lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md` - `F-003` states current tests do not bound CSS motion/filter growth.
- Evidence 2: `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-003` -
  candidate requires exact checks for `@keyframes`, `animation:` and always-on
  `backdrop-filter`.
- Evidence 3: `frontend/src/tests/design-system-guards.test.ts` - existing design-system guard owner for CSS architecture.
- Evidence 4: `frontend/src/tests/visual-smoke.test.tsx` - existing visual smoke guard for landing behavior.
- Evidence 5: `CS-143` and `CS-144` stories - expected upstream
  simplifications whose final retained exceptions should be guarded by this
  story.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage; `RG-083`, `RG-084`, `RG-085`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- Un test executable borne la complexite motion/filter landing.
- Toute exception conservee est exacte, justifiee et associee a une condition de sortie.
- Les guards existants de fond, dark mode, ownership et absence de timers continuent de passer.
- Une nouvelle animation ou filtre landing non classe fait echouer la suite.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - les filtres/surfaces dark landing doivent rester classes.
  - `RG-084` - les effets landing ne doivent pas recreer des halos/fonds page-level concurrents.
  - `RG-085` - le dark astral global ne doit pas etre concurrence par une animation landing.
  - `RG-086` - la landing ne doit pas recreer `app-bg--landing`.
  - `RG-087` - les effets landing ne doivent pas modifier le fond viewport-fixed.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - domaines non landing visual.
- Required regression evidence:
  - test guard deterministe;
  - inventory before/after;
  - scans `@keyframes`, `animation:`, `filter`, `backdrop-filter`, wildcard allowlists.
- Allowed differences:
  - ajout de tests et artefacts; aucune difference visuelle applicative attendue.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Une garde detecte tout `@keyframes` landing non classe. | `npm run test -- design-system` ou `npm run test -- landing-visual-complexity`; inventory after. |
| AC2 | Une garde detecte toute declaration `animation:` non classee. | Mutation documentee ou fixture; scan `rg -n "animation:" src/pages/landing src/layouts/LandingLayout.css`. |
| AC3 | Une garde detecte tout filtre landing non classe. | Registre exact; scan `rg -n "backdrop-filter\|filter:" src/pages/landing src/layouts/LandingLayout.css`. |
| AC4 | Aucune allowlist wildcard n'est admise. | `npm run test -- design-system`; after artifact; scan anti-wildcard dans les tests. |
| AC5 | Les guards landing existants continuent de passer. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system visual-smoke LandingPage`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier l'etat actuel motion/filter (AC: AC1, AC2, AC3)
  - [ ] Subtask 1.1 - Lire `design-system-guards.test.ts`, `visual-smoke.test.tsx` et CSS landing.
  - [ ] Subtask 1.2 - Creer `landing-visual-complexity-before.md` avec inventaire et tests actuels.

- [ ] Task 2 - Ajouter le guard executable (AC: AC1, AC2, AC3, AC4)
  - [ ] Subtask 2.1 - Choisir `design-system-guards.test.ts` ou un nouveau `landing-visual-complexity.test.ts`.
  - [ ] Subtask 2.2 - Implementer l'inspection des CSS sans nouvelle dependance.
  - [ ] Subtask 2.3 - Definir les exceptions exactes par selecteur/declaration/raison.

- [ ] Task 3 - Prouver anti-wildcard et integration tests (AC: AC4, AC5)
  - [ ] Subtask 3.1 - Ajouter assertions qui refusent wildcard, dossier complet et exceptions sans raison.
  - [ ] Subtask 3.2 - Executer tests cibles et lint.

- [ ] Task 4 - Capturer la preuve after (AC: AC1, AC2, AC3, AC4, AC5)
  - [ ] Subtask 4.1 - Creer `landing-visual-complexity-after.md`.
  - [ ] Subtask 4.2 - Documenter comment le guard echoue sur croissance non classee.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - helpers de lecture/scan deja presents dans les tests frontend si existants.
  - `design-system-guards.test.ts` quand il reste l'owner naturel du guard CSS.
  - `visual-smoke.test.tsx` pour validation runtime complementaire, pas pour remplacer le guard statique.
- Do not recreate:
  - un parser CSS externe;
  - une deuxieme allowlist vague de design-system;
  - un audit manuel non executable;
  - un seuil global non rattache a des selecteurs.
- Shared abstraction allowed only if:
  - elle factorise une logique de scan deja dupliquee dans les tests et reste test-only.

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

- wildcard `*`, `**` ou folder-wide dans l'allowlist motion/filter.
- `PASS with limitation`
- `app-bg--landing`
- nouvelle dependance CSS parser dans `package.json`
- exception sans raison ou condition de sortie

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Guard CSS landing motion/filter | `frontend/src/tests/design-system-guards.test.ts` ou `frontend/src/tests/landing-visual-complexity.test.ts` | audit manuel seul |
| Exceptions exactes | test guard ou artefact story after | wildcard, dossier complet, commentaire libre |
| CSS inspecte | `frontend/src/pages/landing/**.css`, `frontend/src/layouts/LandingLayout.css` | `App.css` corrections ou global non landing |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/LandingPage.test.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/layouts/LandingLayout.css`
- `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/00-story.md`
- `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/design-system-guards.test.ts` - ajouter le guard si l'owner CSS central reste approprie.
- `frontend/src/tests/landing-visual-complexity.test.ts` - optionnel, si un test cible rend le contrat plus lisible.
- `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/landing-visual-complexity-before.md` - baseline.
- `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/landing-visual-complexity-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - guard exact ou integration dans suite existante.
- `frontend/src/tests/visual-smoke.test.tsx` - verification complementaire du rendu landing.

Files not expected to change:

- `frontend/src/pages/landing/LandingPage.css` - pas requis sauf si `CS-143` / `CS-144` n'a pas encore reduit la surface et qu'une exception doit etre retiree avant guard.
- `frontend/src/App.css` - hors scope.
- `frontend/src/app/routes.tsx` - hors scope.
- `backend/pyproject.toml` - aucune dependance backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- design-system visual-smoke LandingPage
npm run lint
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css
rg -n "\\*|\\.\\*|\\*\\*" src/tests/design-system-guards.test.ts src/tests/landing-visual-complexity.test.ts
```

Manual/runtime checks required:

- Documenter dans `landing-visual-complexity-after.md` une preuve que le guard echoue sur un ajout non classe, via mutation locale revertie ou description de fixture/test.

## 22. Regression Risks

- Risk: un guard trop large bloque des transitions hover/focus legitimes.
  - Guardrail: AC2 limite les declarations inspectees et classe les exceptions exactes.
- Risk: une allowlist vague rend le guard inutile.
  - Guardrail: AC4 anti-wildcard.
- Risk: la story est executee avant `CS-143`/`CS-144` et encode le bruit actuel comme permanent.
  - Guardrail: AC4 exige raison et condition de sortie pour chaque exception.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work.
- Respecter les instructions projet: aucun style inline et commentaires/docstrings en francais pour tout fichier applicatif nouveau ou significativement modifie.

## 24. References

- `_condamad/audits/frontend-landing-page/2026-05-11-1841/00-audit-report.md` - audit source et closure status.
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-003` - finding guard missing.
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-003` - candidat source.
- `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/00-story.md` - simplification hero attendue.
- `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/00-story.md` - convergence theme/menu attendue.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
