# Story CS-109 fermer-decisions-residuelles-pages-layout: Fermer les decisions residuelles de pages layout

Status: done

## 1. Objective

Fermer completement le finding `F-201` de l'audit `frontend-layouts`.
La story applique et gouverne les decisions utilisateur du 2026-05-08:
router privacy, router les callbacks Stripe confirmes, supprimer l'ancienne
`HomePage`, rattacher `TestimonialsSection`, puis aligner les artefacts CONDAMAD.

## 2. Trigger / Source

- Source type: code-review
- Source reference: review utilisateur du 2026-05-08 sur les changements issus de `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md#SC-201`
- Reason for change: la review signale que le code route/suppression est sain,
  mais que l'audit `1914`, `generated/10-final-evidence.md` de CS-108 et le
  contrat CS-108 restent contradictoires apres application des decisions.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-layouts`
- In scope:
  - Formaliser les decisions utilisateur pour `PrivacyPolicyPage`, `BillingSuccessPage`, `BillingCancelPage`, `HomePage` et `TestimonialsSection`.
  - Verifier ou appliquer le routage `/privacy`, `/billing/success` et `/billing/cancel` sous des owners layout explicites.
  - Verifier ou appliquer la suppression physique de `frontend/src/pages/HomePage.tsx` sans shim, alias, redirect, fallback ou re-export.
  - Verifier ou appliquer le rattachement de `TestimonialsSection` dans `LandingPage`.
  - Mettre a jour `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`, les guards, les tests et les artefacts CS-107/CS-108/1914 pour qu'ils ne racontent plus un etat bloque.
  - Produire une preuve persistante de cloture CS-109.
- Out of scope:
  - Modifier le contenu legal de `PrivacyPolicyPage` au-dela du minimum necessaire au routage.
  - Modifier le contrat backend Stripe, les variables `STRIPE_CHECKOUT_SUCCESS_URL` ou `STRIPE_CHECKOUT_CANCEL_URL`, ou la creation de session checkout.
  - Refaire les layouts `RootLayout`, `LandingLayout`, `AuthLayout` ou `AppLayout`.
  - Refactorer le design system, les tokens CSS, les styles inline ou les pages non citees.
  - Changer les permissions, l'authentification, le pricing ou les endpoints billing.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064`, `RG-066`, `RG-067` ou `RG-068`.
  - Ne pas reintroduire `HomePage` sous forme de route, re-export, wrapper, alias ou fallback.
  - Ne pas creer de route billing de compatibilite autre que les chemins canoniques confirmes.
  - Ne pas laisser `F-201`, `SC-201`, CS-108 final evidence ou l'audit `1914` dans un etat contradictoire avec le code.
  - Ne pas accepter `PASS with limitation`, `TODO`, wildcard, broad allowlist, legacy, shim, alias, fallback, migration-only ou residual work cache comme preuve de fermeture.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime l'ancienne `HomePage` morte et ferme les classifications residuelles en prouvant les owners canoniques restants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: exposer `/privacy`, `/billing/success`, `/billing/cancel`;
    supprimer `HomePage`; composer `TestimonialsSection`; corriger les artefacts.
  - Interdit: changer le contenu metier billing/legal, ajouter des routes de compatibilite, changer les layouts principaux ou elargir le domaine.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une route privacy/billing, la suppression de
  `HomePage`, ou le rattachement de `TestimonialsSection` diverge des decisions
  utilisateur deja donnees dans cette conversation.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le route tree frontend et la config checkout Stripe prouvent les routes actives et callbacks attendus. |
| Baseline Snapshot | yes | Les artefacts CS-108/1914 et le registre page ownership doivent avoir un avant/apres auditable. |
| Ownership Routing | yes | Chaque fichier residuel doit avoir owner layout ou decision de suppression exacte. |
| Allowlist Exception | yes | `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` est le registre executable des classifications et exceptions page-adjacent. |
| Contract Shape | yes | Les routes frontend et la forme de classification page doivent etre explicites. |
| Batch Migration | no | Le lot est ferme et contient cinq decisions exactes, pas une migration par vagues. |
| Reintroduction Guard | yes | `HomePage` et les etats bloques ne doivent pas revenir silencieusement. |
| Persistent Evidence | yes | La cloture doit etre conservee dans des artefacts CS-109 et les audits/stories alignes. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/page-architecture-guards.test.ts` over
    exported `routes` from `frontend/src/app/routes.tsx`.
  - AST/registry guard `frontend/src/tests/page-architecture-guards.test.ts` over `frontend/src/tests/page-architecture-allowlist.ts` for page owners.
  - Loaded config source `backend/app/core/config.py` for default checkout URLs.
- Secondary evidence:
  - `frontend/src/pages/landing/LandingPage.tsx` pour le rattachement de `TestimonialsSection`.
  - `rg --files frontend/src/pages -g "*.tsx"` pour prouver l'absence de `HomePage.tsx`.
- Static scans alone are not sufficient because:
  - une route peut etre importee sans etre effective; le guard doit inspecter la route tree exportee.
  - une page supprimee peut revenir par re-export ou import indirect.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md`
- Required baseline content:
  - extrait de `_condamad/audits/frontend-layouts/2026-05-08-1914/00-audit-report.md` montrant `Status: blocked`;
  - extrait de `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md#SC-201`;
  - extrait de `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` montrant les contradictions de review;
  - inventaire route/page des cinq surfaces.
- Expected invariant:
  - zero contradiction active entre code, allowlist, audit 1914, CS-107 et CS-108.
- Allowed differences:
  - passage de `blocked` a `closed` pour `F-201`;
  - suppression de `HomePage.tsx`;
  - routes canoniques et rattachement testimonials conformes aux decisions utilisateur.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Page privacy publique | `LandingLayout` sous `RootLayout`, route `/privacy` | route directe sans owner, app/admin par defaut, ou blocage stale |
| Callback Stripe success | `AppLayout` sous `RootLayout`, route `/billing/success` | route absente alors que `STRIPE_CHECKOUT_SUCCESS_URL` pointe vers ce chemin |
| Callback Stripe cancel | `AppLayout` sous `RootLayout`, route `/billing/cancel` | route absente alors que `STRIPE_CHECKOUT_CANCEL_URL` pointe vers ce chemin |
| Ancienne home | `LandingPage` comme remplacement canonique de `/` | `HomePage.tsx`, route, barrel export, wrapper, alias ou re-export |
| Testimonials landing | `LandingPage` compose `TestimonialsSection` | candidat mort, import opportuniste hors landing, ou suppression non decidee |
| Evidence de cloture | CS-109 et audit 1914 alignes | CS-108/1914 contradictoires ou stale |

Rules:

- Toute entree de `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` doit avoir `file`, `classification`, `owner`, `reason`, `exit`.
- Les routes `routed-page` doivent exister dans `routes.tsx`.
- `HomePage.tsx` ne doit plus etre present dans l'inventaire page.

## 4e. Allowlist / Exception Register

Use `frontend/src/tests/page-architecture-allowlist.ts` as the single executable register.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `pages/PrivacyPolicyPage.tsx` | `/privacy` | Page privacy publique decidee par l'utilisateur. | Permanent tant que la page privacy est requise. |
| `pages/billing/BillingSuccessPage.tsx` | `/billing/success` | URL checkout success Stripe par defaut. | Permanent tant que la config checkout utilise ce chemin. |
| `pages/billing/BillingCancelPage.tsx` | `/billing/cancel` | URL checkout cancel Stripe par defaut. | Permanent tant que la config checkout utilise ce chemin. |
| `pages/landing/sections/TestimonialsSection.tsx` | import par `LandingPage` | Section landing rattachee par decision produit. | Permanent tant que `LandingPage` en est l'owner. |

Rules:

- no wildcard;
- no folder-wide exception;
- no stale `needs-user-decision` or `dead/unmounted-page-candidate` for the five residual decisions;
- no `HomePage` row after deletion.

## 4f. Contract Shape

Contract type:

- frontend route/page ownership decision

Fields:

- `file`: path relative to `frontend/src`.
- `classification`: `routed-page`, `nested-routed-page`, `page-adjacent-component`, `dead/unmounted-page-candidate`, or `needs-user-decision`.
- `route`: frontend route when applicable.
- `owner`: layout or component owner.
- `reason`: decision/source-backed rationale.
- `exit`: permanence or exit condition.

Required fields:

- `file`, `classification`, `owner`, `reason`, `exit`.

Optional fields:

- `route`, `decisionSource`, `expiresOn`, `removalStory`.

Status codes:

- none; no HTTP API response is changed.

Serialization names:

- TypeScript object fields in `PageLayoutOwnerClassification`.

Frontend type impact:

- No new frontend type expected unless needed to strengthen guard readability.

Generated contract impact:

- No generated API client or OpenAPI contract changes. The frontend route tree is the runtime manifest for this story.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: the story closes a finite set of five decisions plus three stale governance findings in one bounded pass.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Closure baseline | `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-before.md` | Capturer les contradictions et surfaces avant cloture. |
| Closure result | `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md` | Prouver les routes, suppression, rattachement et artefacts alignes. |
| Final evidence | `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/generated/10-final-evidence.md` | Conserver commandes, scans et resultats. |
| Updated audit | `_condamad/audits/frontend-layouts/2026-05-08-1914/*.md` | Remplacer l'etat `blocked` par l'etat ferme ou supersede par CS-109. |
| Updated prior story evidence | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` | Supprimer les contradictions actives. |

## 4i. Reintroduction Guard

The implementation must add or preserve an architecture guard against reintroduction so the removed or closed surfaces cannot be reintroduced.

Deterministic guard sources:

- frontend route table: `frontend/src/app/routes.tsx`
- forbidden symbols or states: `HomePage`, `needs-user-decision`, `dead/unmounted-page-candidate`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/app/routes.tsx`

Required forbidden examples:

- `frontend/src/pages/HomePage.tsx` reappears.
- `HomePage` is exported from `frontend/src/pages/index.ts`.
- `PrivacyPolicyPage`, `BillingSuccessPage`, or `BillingCancelPage` remains `needs-user-decision`.
- `TestimonialsSection` remains `dead/unmounted-page-candidate`.
- Audit `1914` or CS-108 final evidence still claims `F-201` is blocked as the current state.
- Any broad `frontend/src/pages/**` wildcard exception is added.

Guard evidence:

- `npm run test -- page-architecture layout`
- targeted `rg` scans listed in the validation plan.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1914/02-finding-register.md#F-201`
- Closure proof required: before/after closure artifacts, audit 1914 updated,
  CS-108 final evidence updated, page architecture guard, targeted tests, lint,
  and negative scans for stale blockers.
- Known residual in-domain work: none.
- Deferred non-domain concerns: legal copy content of `PrivacyPolicyPage`; external Stripe dashboard configuration outside repository if it overrides backend defaults.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-layouts/2026-05-08-1914/00-audit-report.md` - current audit artifact still reports `Status: blocked` and lists the five residual decisions.
- Evidence 2: `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md` - `SC-201` still says decisions are required before implementation.
- Evidence 3: `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md`
  - earlier sections claim no route and no deletion, while a later amendment says
  routes and deletion were applied.
- Evidence 4: `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md`
  - original CS-108 forbids physical deletion of `HomePage`, so CS-109 governs
  the closure.
- Evidence 5: `backend/app/core/config.py`
  - default checkout URLs point to `/billing/success` and `/billing/cancel`.
- Evidence 6: `frontend/src/app/routes.tsx`, `frontend/src/tests/page-architecture-allowlist.ts`,
  and `frontend/src/pages/landing/LandingPage.tsx`
  - current worktree may already contain the intended implementation; CS-109
  must verify, complete, and govern it.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants `RG-064`, `RG-066`, `RG-067`, and `RG-068` consulted before scope was finalized.

## 6. Target State

After implementation:

- `PrivacyPolicyPage` is a canonical routed page at `/privacy` under `LandingLayout` and `RootLayout`.
- `BillingSuccessPage` is a canonical routed page at `/billing/success` under `AppLayout` and `RootLayout`.
- `BillingCancelPage` is a canonical routed page at `/billing/cancel` under `AppLayout` and `RootLayout`.
- `HomePage.tsx` is physically absent, not exported, not routed, and not preserved through a wrapper.
- `TestimonialsSection` is owned by `LandingPage` and no longer classified as dead.
- `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`, CS-107 after inventory, CS-108 evidence, and audit `2026-05-08-1914` all describe the same closed state.
- `F-201` has no residual in-domain implementation or governance work.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture guards must remain exact while routes and page classifications change.
  - `RG-066` - page-size exceptions must not be broadened while touching page architecture files.
  - `RG-067` - date/time formatting must continue to use `formatDate`; no inline formatting migration is part of this story.
  - `RG-068` - RootLayout and explicit layout owners remain the central invariant for every page file.
- Non-applicable invariants:
  - `RG-044` - no token namespace migration.
  - `RG-054` - no legacy admin redirect is touched.
  - `RG-063` - premium/glass CSS surfaces are not part of this story.
- Required regression evidence:
  - `npm run test -- page-architecture layout`
  - `npm run test -- App router BillingSuccessPage BillingCancelPage`
  - `npm run test -- LandingPage visual-smoke`
  - `npm run lint`
  - targeted negative scans for `HomePage` and stale blocked wording.
- Allowed differences:
  - only the route/classification/governance changes required by the five user decisions and review findings.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Privacy/billing routes have layout owners. | Evidence profile: `runtime_source_of_truth`; AST guard; command `npm run test -- page-architecture layout`. |
| AC2 | No `HomePage.tsx` route/export/shim/alias/wrapper exists. | Evidence profile: `targeted_forbidden_symbol_scan`; AST guard; command `rg -n "HomePage" frontend/src`. |
| AC3 | `TestimonialsSection` uses `LandingPage` ownership classification. | Evidence profile: `ownership_routing`; command `npm run test -- LandingPage visual-smoke`. |
| AC4 | CS-107/CS-108/audit `1914` match runtime state. | Evidence profile: `persistent_evidence`; AST guard; loaded config; command `rg -n "blocked" _condamad`. |
| AC5 | CS-109 durable proof exists in `story-status.md`. | Evidence profile: `persistent_evidence`; command `rg -n "CS-109" _condamad/stories`. |
| AC6 | Frontend route regression tests pass. | Evidence profile: `reintroduction_guard`; runtime evidence: AST guard; command `npm run lint`; tests in section 22. |

## 8. Implementation Tasks

- [x] Task 1 - Capture closure baseline. (AC: AC4, AC5)
  - [x] Create `closure-before.md` with current audit/story contradictions and route/page inventory.
  - [x] Include exact references to review findings 1, 2 and 3.

- [x] Task 2 - Apply or verify user decisions in runtime code. (AC: AC1, AC2, AC3)
  - [x] Ensure `/privacy` routes `PrivacyPolicyPage` under `LandingLayout`.
  - [x] Ensure `/billing/success` and `/billing/cancel` route billing pages under `AppLayout`.
  - [x] Ensure `HomePage.tsx` is deleted and not re-exported.
  - [x] Ensure `TestimonialsSection` is imported and rendered by `LandingPage`.

- [x] Task 3 - Align executable page ownership and guards. (AC: AC1, AC2, AC3, AC6)
  - [x] Update `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` for the three routed pages and testimonials.
  - [x] Remove the `HomePage` classification row.
  - [x] Keep or strengthen guards so zero blocked/dead entries is allowed, but reintroduction still fails.

- [x] Task 4 - Close stale governance artifacts. (AC: AC4, AC5)
  - [x] Update audit `2026-05-08-1914` so `F-201` is closed or superseded by CS-109, not active blocked work.
  - [x] Rewrite CS-108 final evidence sections that currently contradict the new state, or move old statements into historical baseline notes.
  - [x] Update CS-107 after inventory and CS-108 decision artifact to match runtime and allowlist.

- [x] Task 5 - Add or update tests and final evidence. (AC: AC1, AC2, AC3, AC5, AC6)
  - [x] Add route/render coverage for `/privacy`.
  - [x] Add billing cancel coverage if absent.
  - [x] Write `closure-after.md` and `generated/10-final-evidence.md`.
  - [x] Run all validation commands and record outcomes.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/app/routes.tsx` as the single route tree.
  - `frontend/src/tests/page-architecture-allowlist.ts` as the single page ownership registry.
  - `frontend/src/tests/page-architecture-guards.test.ts` as the architecture guard owner.
  - `backend/app/core/config.py` as evidence for default Stripe checkout callback URLs.
- Do not recreate:
  - another page ownership registry;
  - a compatibility `HomePage` wrapper;
  - alternate billing callback routes;
  - a second landing testimonials owner.
- Shared abstraction allowed only if:
  - an existing guard becomes unreadable; otherwise keep changes local to the existing guard/test files.

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

- `frontend/src/pages/HomePage.tsx`
- `export * from "./HomePage"`
- route path for legacy home other than `/` landing.
- `/billing` as a compatibility retry destination for checkout cancel.
- `PrivacyPolicyPage`, `BillingSuccessPage`, or `BillingCancelPage` classified as `needs-user-decision`.
- `TestimonialsSection` classified as `dead/unmounted-page-candidate`.
- stale active text in audit `1914` claiming `F-201` remains blocked.
- wildcard `frontend/src/pages/**`.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table in `closure-after.md`:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `frontend/src/pages/HomePage.tsx` | UI page | `dead` | none | landing page | `delete` | scans | external link risk accepted |
| `frontend/src/pages/PrivacyPolicyPage.tsx` | UI page | `canonical-active` | `/privacy` | `LandingLayout` | `keep` | route test | legal maintenance |
| `BillingSuccessPage.tsx` | UI page | `canonical-active` | success URL | `AppLayout` | `keep` | config/test | Stripe dashboard override |
| `BillingCancelPage.tsx` | UI page | `canonical-active` | cancel URL | `AppLayout` | `keep` | config/test | Stripe dashboard override |
| stale CS-108 contradiction | governance text | `historical-facade` | review | CS-109 evidence | `replace-consumer` | scan | future confusion |
| external Stripe dashboard override | external config | `needs-user-decision` | outside repo | backend defaults | `needs-user-decision` | recorded | cannot prove from repo |

Audit output path:

- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public home route `/` | `LandingPage` under `LandingLayout` and `RootLayout` | deleted `HomePage.tsx`, any `HomePage` wrapper/export |
| Privacy route `/privacy` | `PrivacyPolicyPage` under `LandingLayout` and `RootLayout` | blocked privacy classification |
| Stripe success callback | `BillingSuccessPage` under `AppLayout` and `RootLayout` | blocked billing success classification or alternate callback route |
| Stripe cancel callback | `BillingCancelPage` under `AppLayout` and `RootLayout` | blocked billing cancel classification or `/billing` retry route |
| Testimonials section | `LandingPage` owns `TestimonialsSection` | dead/unmounted candidate classification |
| Closure evidence | CS-109 artifacts and updated audit 1914 | stale CS-108/1914 contradictory current-state text |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

Applies to:

- `frontend/src/pages/HomePage.tsx`

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.

For `HomePage.tsx`, deletion is allowed only after scans show:

- no route in `frontend/src/app/routes.tsx`;
- no export in `frontend/src/pages/index.ts`;
- no production import under `frontend/src`;
- user decision states the landing replaces the old home.

If any external/public reference is found, stop and record a blocker instead of deleting.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, OpenAPI schema, generated client, or backend contract is changed.
  The frontend route tree is validated directly by `routes.tsx` and page architecture tests.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-layouts/2026-05-08-1914/00-audit-report.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1914/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/pages/landing/LandingPage.tsx`
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `backend/app/core/config.py`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/app/routes.tsx` - add or verify canonical routes.
- `frontend/src/pages/HomePage.tsx` - delete if still present.
- `frontend/src/pages/landing/LandingPage.tsx` - attach `TestimonialsSection`.
- `frontend/src/pages/PrivacyPolicyPage.tsx` - only minimal cleanup required by routing/lint.
- `frontend/src/pages/billing/BillingCancelPage.tsx` - ensure retry action targets canonical subscription settings.
- `frontend/src/pages/billing/BillingSuccessPage.tsx` - only required comment/lint-level changes.
- `frontend/src/tests/page-architecture-allowlist.ts` - update classifications.
- `frontend/src/tests/page-architecture-guards.test.ts` - keep guards valid when no blocked/dead entries remain.
- `frontend/src/tests/App.test.tsx` - route/render coverage for `/privacy`.
- `frontend/src/tests/router.test.tsx` - route inventory assertions.
- `frontend/src/tests/BillingCancelPage.test.tsx` - cancel callback coverage if absent.
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` - align inventory.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md` - align decisions.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` - remove or clearly historicalize contradictions.
- `_condamad/audits/frontend-layouts/2026-05-08-1914/*.md` - close or supersede `F-201` and `SC-201`.
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-before.md` - baseline.
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md` - closure result.
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/generated/10-final-evidence.md` - final evidence.

Likely tests:

- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/BillingSuccessPage.test.tsx`
- `frontend/src/tests/BillingCancelPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`

Files not expected to change:

- `backend/app/core/config.py` - evidence only, no config change.
- `backend/**` other than read-only evidence - no backend implementation change.
- `frontend/package.json` - no dependency or script change.
- `frontend/src/styles/**` - no design-system/token work.
- `frontend/src/layouts/**` - no layout component refactor.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture layout
npm run test -- App router BillingSuccessPage BillingCancelPage
npm run test -- LandingPage visual-smoke
rg --files src/pages -g "*.tsx" | rg "HomePage"
rg -n "HomePage" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts
rg -n "privacy|billing/success|billing/cancel" src/app/routes.tsx src/tests/page-architecture-allowlist.ts
rg -n "TestimonialsSection" src/pages/landing/LandingPage.tsx src/tests/page-architecture-allowlist.ts
Pop-Location
rg -n "Status: `blocked`|Closure intent: `blocked`|remains `needs-user-decision`|dead/unmounted-page-candidate.*TestimonialsSection|HomePage.*pending" `
  _condamad/audits/frontend-layouts/2026-05-08-1914 `
  _condamad/stories/CS-107-classer-pages-layout-owner `
  _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout `
  _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Expected scan outcomes:

- `rg --files src/pages -g "*.tsx" | rg "HomePage"` returns no hit.
- `rg -n "HomePage" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts` returns no hit.
- The stale-blocked scan may hit `closure-before.md` only as historical baseline; active after/final/audit files must not contain stale current-state blockers.

## 22. Regression Risks

- Risk: CS-109 repeats the CS-108 contradiction by appending amendments instead of rewriting stale current-state evidence.
  - Guardrail: AC4 requires active artifacts to stop claiming blocked/no-route/no-delete current state.
- Risk: `HomePage` is preserved through a re-export or wrapper.
  - Guardrail: AC2 and Delete-Only Rule require file removal and negative scans.
- Risk: billing callbacks are routed but not aligned with Stripe config.
  - Guardrail: AC1 references `backend/app/core/config.py` defaults and route tests.
- Risk: page architecture guard becomes weaker when no blocked/dead entries remain.
  - Guardrail: AC6 keeps `page-architecture layout` tests mandatory and requires forbidden-symbol scans.
- Risk: testimonials becomes visible unexpectedly.
  - Guardrail: existing `VITE_SHOW_TESTIMONIALS` feature flag remains the display control; story does not alter CSS or copy.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not update backend Stripe config values; use them only as evidence.
- Do not leave audit `1914`, CS-108 evidence, or CS-107 inventory contradictory with runtime code.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md#SC-201` - source closure candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1914/02-finding-register.md#F-201` - source finding.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` - prior decision story whose scope must not be silently rewritten.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` - review finding source for contradictory evidence.
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` - page ownership inventory.
- `frontend/src/app/routes.tsx` - runtime frontend route source.
- `frontend/src/tests/page-architecture-allowlist.ts` - executable page ownership registry.
- `frontend/src/tests/page-architecture-guards.test.ts` - architecture guard owner.
- `backend/app/core/config.py` - Stripe checkout callback URL defaults.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
