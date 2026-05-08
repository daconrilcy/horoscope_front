# Story CS-108 statuer-pages-publiques-candidates-layout: Statuer les pages publiques et candidates layout

Status: done

## 1. Objective

Transformer les cinq classifications residuelles de CS-107 en decisions
explicites et auditees.
La story doit rattacher une page a un layout owner approuve, conserver le
blocage avec owner et expiry, ou retirer la surface si la decision l'autorise.
Elle ne doit jamais router ou supprimer silencieusement une page bloquee.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-1532/03-story-candidates.md#SC-101`
- Reason for change: `F-101` indique que la hierarchie frontend-layouts est
  gardee, mais que cinq fichiers restent bloques par decision produit, legal,
  billing ou retrait.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-layouts`
- In scope:
  - Obtenir et consigner une decision explicite pour les cinq fichiers residuels listes par `SC-101`.
  - Mettre a jour `frontend/src/tests/page-architecture-allowlist.ts` pour remplacer ou documenter chaque classification residuelle avec owner, route, raison et expiry/permanence.
  - Modifier `frontend/src/app/routes.tsx` uniquement si une decision approuve le routage public ou applicatif d'une page.
  - Mettre a jour `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` et creer les preuves CS-108 avant/apres.
  - Adapter `frontend/src/tests/page-architecture-guards.test.ts` uniquement si la logique de garde doit verifier la decision sans l'affaiblir.
- Out of scope:
  - Redefinir `RootLayout`, `LandingLayout`, `AuthLayout`, `AppLayout` ou l'arborescence principale deja fermee par CS-103 a CS-107.
  - Changer le contenu legal de `PrivacyPolicyPage`.
  - Modifier le contrat Stripe/backend ou les URLs externes de checkout hors decision de callback frontend.
  - Supprimer physiquement `HomePage` ou `TestimonialsSection` dans cette story.
  - Refactorer CSS, design-system, styles inline ou tokens.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064`, `RG-066`, `RG-067` ou `RG-068`.
  - Ne pas introduire de route, redirect, alias, fallback, wrapper ou shim de compatibilite.
  - Ne pas creer d'allowlist wildcard ou folder-wide pour `frontend/src/pages/**`.
  - Ne pas considerer `PASS with limitation`, `TODO`, `migration-only`, `legacy`, `shim`, `alias` ou residual work cache comme une fermeture.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: frontend-route-removal
- Archetype reason: la story statue des pages/routes frontend residuelles et peut supprimer uniquement les surfaces explicitement decidees comme retirees.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: rendre accessible une page uniquement si la decision produit/legal/billing nomme la route et le layout owner.
  - Autorise: conserver un blocage explicite avec owner de decision, expiry et preuve.
  - Interdit: changer le contenu metier, les permissions, les flux Stripe, le design system ou la hierarchie layout hors effet direct de la decision.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une des cinq lignes residuelles n'a pas de decision explicite et sourcee avant modification de route, de classification ou de story de retrait.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le routage eventuel doit etre prouve par un `AST guard` sur la route tree et le guard, pas par scan seul. |
| Baseline Snapshot | yes | Les cinq lignes residuelles doivent avoir un avant/apres auditable. |
| Ownership Routing | yes | La story decide ou conserve l'owner layout/classification de chaque fichier. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre exactes, justifiees et expirees ou permanentes. |
| Contract Shape | yes | Les routes/frontend entries exposees ou retirees doivent avoir un shape explicite: chemin, layout owner, statut et absence de contrat genere. |
| Batch Migration | no | Le lot est un ensemble fini de cinq decisions, sans migration multi-batch. |
| Reintroduction Guard | yes | Les routes sans decision et les classifications anonymes ne doivent pas reapparaitre. |
| Persistent Evidence | yes | Les decisions et inventaires doivent etre conserves dans des artefacts markdown. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AST guard` sur la route tree exportee par `frontend/src/app/routes.tsx`;
  - guard executable `frontend/src/tests/page-architecture-guards.test.ts`;
  - registre executable `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`.
- Secondary evidence:
  - scans cibles sur les cinq fichiers residuels et les imports correspondants.
- Static scans alone are not sufficient because:
  - une page peut etre importee sans etre routee, et une classification peut devenir fausse si le route tree change.
- Required runtime proof:
  - `npm run test -- page-architecture layout`
  - `npm run test -- App router BillingSuccessPage`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md`
- Expected invariant:
  - Les cinq fichiers sources restent exhaustivement couverts; chaque difference after correspond a une decision sourcee.
- Allowed differences:
  - ajout de route sous owner explicite approuve;
  - conservation d'un blocage avec owner et expiry;
  - creation d'une reference vers une story de retrait dediee;
  - aucune suppression physique dans cette story.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Page privacy publique | `LandingLayout` sous `RootLayout` ou autre owner public explicitement approuve | route directe sans owner ou application/admin par defaut |
| Callback billing success/cancel | owner billing frontend explicitement approuve sous `RootLayout` | route publique implicite, redirect alias ou callback non documente |
| Ancienne home non routee | story de retrait dediee ou classification conservee avec owner/expiry | suppression silencieuse ou barrel export comme preuve d'activite |
| Section testimonials non montee | `LandingPage` si rattachement approuve, sinon story de retrait dediee ou classification conservee | import opportuniste sans decision produit |
| Registre page ownership | `frontend/src/tests/page-architecture-allowlist.ts` | memoire d'audit non executable |

Rules:
- Chaque decision doit nommer `file`, `classification`, `owner`, `reason`, `exit` et, si routee, `route`.
- Une entree `needs-user-decision` ne peut rester que si la decision explicite est de garder le blocage, avec owner de decision et expiry.

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/pages/PrivacyPolicyPage.tsx` | `PrivacyPolicyPage` | Page publique potentielle. | Expire par route, retrait ou blocage date. |
| `frontend/src/pages/billing/BillingSuccessPage.tsx` | `BillingSuccessPage` | Callback billing potentiel. | Expire par route, retrait ou blocage date. |
| `frontend/src/pages/billing/BillingCancelPage.tsx` | `BillingCancelPage` | Callback billing potentiel. | Expire par route, retrait ou blocage date. |
| `frontend/src/pages/HomePage.tsx` | `HomePage` | Candidat mort non route. | Expire par retrait ou conservation sourcee. |
| `frontend/src/pages/landing/sections/TestimonialsSection.tsx` | `TestimonialsSection` | Section landing non montee. | Expire par rattachement, retrait ou conservation. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

Contract type:

- frontend route/page ownership decision

Fields:

- `file`: chemin relatif sous `frontend/src/pages`.
- `classification`: `routed-page`, `page-adjacent-component`, `dead/unmounted-page-candidate` ou `needs-user-decision`.
- `route`: chemin frontend si la page est routee.
- `owner`: layout owner ou owner de decision.
- `reason`: justification sourcee.
- `exit`: condition de sortie, story de retrait ou permanence.

Required fields:

- `file`, `classification`, `owner`, `reason`, `exit`.

Optional fields:

- `route`, uniquement si une route est approuvee.

Status codes:

- none; no HTTP API response is changed.

Serialization names:

- TypeScript object fields in `PageLayoutOwnerClassification`.

Frontend type impact:

- aucun nouveau type attendu; `PageLayoutOwnerClassification` reste la forme canonique.

Generated contract impact:

- none; no generated API, route manifest, schema or generated client is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Draft de cadrage | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/story-draft.md` | Detaille le candidat SC-101 avant contractualisation. |
| Baseline decisions | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-before.md` | Capturer les classifications avant edition. |
| After decisions | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md` | Prouver decision, owner et expiry. |
| Trace d'acceptance | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/03-acceptance-traceability.md` | Relier AC, decisions, tests et scans. |
| Evidence finale | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` | Conserver commandes, resultats et risques residuels. |
| Inventaire CS-107 mis a jour | `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` | Garder le registre historique aligne avec la decision. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- frontend route table
- forbidden symbols or states

Required forbidden examples:

- route d'une entree `needs-user-decision` sans decision sourcee;
- wildcard `frontend/src/pages/**`;
- classification residuelle sans `owner`, `reason` ou `exit`;
- `PASS with limitation` dans les artefacts after/final evidence.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture layout` checks page ownership and blocked routing.
- Evidence profile: `targeted_forbidden_symbol_scan`; targeted scans check `PASS with limitation`, wildcard exceptions and stale residual labels.

## 4j. Source Finding Closure

- Closure status: blocked
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1532/02-finding-register.md#F-101`
- Closure proof required: before/after decision artifact, updated registry,
  updated CS-107 after inventory, page guard, targeted tests and scans.
- Known residual in-domain work: the five residual files remain blocked until
  explicit decisions are supplied. After implementation, residual work must be
  `none` or an owner/expiry-retained blocker.
- Deferred non-domain concerns: legal policy content, Stripe/provider callback contract, billing backend configuration, CSS/design-system debt.
- Exact decisions required before implementation:
  - `PrivacyPolicyPage`: route under `LandingLayout`, route under another explicit public owner, keep blocked with owner/expiry, or create dedicated removal story.
  - `BillingSuccessPage`: route under explicit billing/public owner, keep blocked with owner/expiry, or create dedicated removal story.
  - `BillingCancelPage`: route under explicit billing/public owner, keep blocked with owner/expiry, or create dedicated removal story.
  - `HomePage`: keep classified with owner/expiry or create dedicated removal story.
  - `TestimonialsSection`: reattach to `LandingPage`, keep classified with owner/expiry, or create dedicated removal story.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-layouts/2026-05-08-1532/00-audit-report.md` -
  implementation CS-103 a CS-107 fermee; domaine encore `blocked`.
- Evidence 2: `_condamad/audits/frontend-layouts/2026-05-08-1532/03-story-candidates.md#SC-101` - candidat unique actif, demande de statuer sans compatibilite ni wildcard.
- Evidence 3: `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` -
  les cinq fichiers cites par `SC-101` sont les residus exacts.
- Evidence 4: `frontend/src/tests/page-architecture-allowlist.ts` - `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` contient les cinq classifications residuelles executables.
- Evidence 5: `frontend/src/tests/page-architecture-guards.test.ts` - le guard bloque deja le routage des entrees `needs-user-decision` et verifie les routes classees.
- Evidence 6: `frontend/src/app/routes.tsx` - aucune des trois pages `needs-user-decision` n'est actuellement routee.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - `RG-064` a `RG-068` consultes avant cadrage.

## 6. Target State

After implementation:

- Les cinq fichiers residuels ont une decision explicite, sourcee, persistante et testable.
- `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` reflete chaque decision sans wildcard ni owner anonyme.
- Si une page est routee, elle l'est sous `RootLayout` puis un layout owner explicite, avec test de route.
- Si une page reste bloquee, son `exit` nomme l'owner de decision et une date/condition d'expiry.
- Si une page doit etre retiree, cette story cree ou reference une story de retrait dediee et ne supprime pas physiquement le fichier.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - les guards page-architecture restent la preuve executable des exceptions pages.
  - `RG-066` - aucune exception page-size ne doit etre elargie pendant cette decision.
  - `RG-067` - aucun formatage date/heure page ne doit etre modifie par cette story.
  - `RG-068` - la hierarchie `RootLayout` plus owners landing/auth/app/admin et la classification exacte des pages restent l'invariant central.
- Non-applicable invariants:
  - `RG-044` - aucun namespace de tokens CSS n'est touche.
  - `RG-054` - aucun redirect legacy admin n'est touche.
  - `RG-063` - aucune surface premium CSS n'est touchee.
- Required regression evidence:
  - `npm run test -- page-architecture layout`
  - `npm run test -- App router BillingSuccessPage`
  - `npm run lint`
  - before/after decision artifacts.
- Allowed differences:
  - uniquement les classifications, routes et preuves correspondant aux decisions explicites.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline liste les cinq residus. | Evidence profile: `baseline_before_after_diff`; command `rg -n "PrivacyPolicyPage|BillingSuccessPage" page-decisions-before.md`. |
| AC2 | Chaque residu a une decision sourcee. | Evidence profile: `external_usage_blocker`; runtime evidence `AST guard`; commands `rg -n "HomePage" page-decisions-after.md`. |
| AC3 | Aucune page `needs-user-decision` n'est routee sans decision. | Evidence profile: `reintroduction_guard`; command `npm run test -- page-architecture layout`. |
| AC4 | Toute route ajoutee a un owner explicite. | Evidence profile: `reintroduction_guard`; runtime evidence `AST guard`; command `npm run test -- page-architecture`. |
| AC5 | Le registre executable reste aligne avec CS-107. | Evidence profile: `allowlist_register_validated`; command `rg -n "HomePage" page-layout-owner-after.md`. |
| AC6 | Tout retrait execute est decide `delete`. | Evidence profile: `frontend_route_removed`; runtime evidence `AST guard`; command `npm run test -- page-architecture layout`. |
| AC7 | Les validations frontend restent vertes. | Evidence profile: `reintroduction_guard`; commands `npm run lint`; `npm run test -- App router BillingSuccessPage`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline des cinq residus avant modification. (AC: AC1)
  - [ ] Lire `page-layout-owner-after.md`, `page-architecture-allowlist.ts`, `routes.tsx` et les cinq fichiers residuels.
  - [ ] Ecrire `page-decisions-before.md` avec classification, owner, reason, exit et preuve de route/import.

- [ ] Task 2 - Obtenir et consigner les decisions explicites. (AC: AC2, AC6)
  - [ ] Pour privacy, documenter owner legal/produit et choix route/maintien/retrait.
  - [ ] Pour billing success/cancel, documenter owner billing/Stripe et choix route/maintien/retrait.
  - [ ] Pour `HomePage` et `TestimonialsSection`, documenter choix maintien, rattachement ou story de retrait dediee.

- [ ] Task 3 - Appliquer uniquement les decisions autorisees. (AC: AC3, AC4, AC5)
  - [ ] Mettre a jour `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`.
  - [ ] Modifier `routes.tsx` seulement si une decision nomme route et layout owner.
  - [ ] Mettre a jour `page-layout-owner-after.md` pour reflet exact du registre executable.

- [ ] Task 4 - Durcir ou conserver les guards contre les interpretations faibles. (AC: AC3, AC5, AC7)
  - [ ] Verifier que le guard bloque toujours les entrees `needs-user-decision` routees sans decision.
  - [ ] Ajouter une verification ciblee si une decision de maintien bloque necessite owner/expiry.

- [ ] Task 5 - Capturer l'after et la trace d'acceptance. (AC: AC2, AC5, AC7)
  - [ ] Ecrire `page-decisions-after.md`.
  - [ ] Ecrire `generated/03-acceptance-traceability.md` et `generated/10-final-evidence.md`.
  - [ ] Executer et reporter les validations.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/tests/page-architecture-allowlist.ts` comme registre executable unique des classifications pages.
  - `frontend/src/tests/page-architecture-guards.test.ts` comme garde principale de hierarchie et inventaire.
  - `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` comme historique d'ownership deja livre.
- Do not recreate:
  - un second registre de page ownership divergent;
  - un layout public dedie si `LandingLayout` ou un owner existant approuve suffit;
  - des tests dupliques qui contournent `page-architecture`.
- Shared abstraction allowed only if:
  - aucune abstraction applicative nouvelle n'est attendue; si un besoin apparait, il est hors scope et doit bloquer.

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

- wildcard `frontend/src/pages/**`;
- route directe de `PrivacyPolicyPage`, `BillingSuccessPage` ou `BillingCancelPage` sans decision sourcee;
- redirect ou alias de compatibilite pour simuler un callback billing;
- suppression physique de `frontend/src/pages/HomePage.tsx` dans cette story;
- suppression physique de `frontend/src/pages/landing/sections/TestimonialsSection.tsx` dans cette story;
- `PASS with limitation`, `TODO`, `legacy`, `shim`, `alias`, `fallback`, `migration-only` dans les preuves finales comme justification de fermeture.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner defined in `Canonical Ownership`.
- `external-active`: item is referenced by email templates, public docs,
  generated links, provider callback configuration, analytics events,
  generated contracts, or explicit audit/user evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an older UI route, import path, or compatibility surface.
- `dead`: item has zero references in production code, tests requiring retention, docs, generated contracts, route tree, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion or routing until the user/product/legal/billing decision is recorded.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted if the user confirms the retirement decision for this story. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table in `page-decisions-after.md`:

| Item | Type | Current classification | Decision | Owner | Expiry / next artifact | Proof | Risk |
|---|---|---|---|---|---|---|---|

Removal contract audit table:

Allowed decisions in the audit: `keep`, `replace-consumer`, `delete`,
`needs-user-decision`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `PrivacyPolicyPage.tsx` | UI page | `needs-user-decision` | route/legal | public owner or none | recorded decision | scan plus decision | legal exposure |
| `BillingSuccessPage.tsx` | UI page | `needs-user-decision` | route/billing | billing owner or none | recorded decision | scan plus decision | callback risk |
| `BillingCancelPage.tsx` | UI page | `needs-user-decision` | route/billing | billing owner or none | recorded decision | scan plus decision | callback risk |
| `HomePage.tsx` | UI page | `dead` if scans confirm | route/barrel/docs | none | recorded decision | scan plus decision | hidden link |
| `TestimonialsSection.tsx` | UI component | `dead` or `canonical-active` | Landing imports | `LandingPage` if reattached | recorded decision | scan plus decision | content risk |

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Route landing/public legal | `LandingLayout` sous `RootLayout` ou owner public approuve | page publique directe sans layout |
| Route callback billing frontend | owner billing/public explicitement approuve sous `RootLayout` | callback non route mais suppose actif |
| Page ownership registry | `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` | artefact markdown non executable seul |
| Retrait de pages candidates mortes | story de retrait dediee | suppression opportuniste dans story de decision |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to a replacement route;
- preserving a wrapper;
- adding a compatibility alias;
- keeping a deprecated route active;
- preserving the old path through re-export;
- replacing deletion with soft-disable behavior.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted without
explicit user decision.
Privacy and billing callback pages are potential external/public entrypoints.
The dev agent must stop if no explicit product/legal/billing user decision is
available.
A test-only import of `BillingSuccessPage` is not proof that callback URLs are
externally inactive.

## 17. Generated Contract Check

Generated contract evidence:

- `frontend/src/app/routes.tsx` route tree is the canonical frontend route manifest for this repository scope.
- `npm run test -- page-architecture layout` must prove removed or retained routes are reflected in the route tree.
- `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection"`
  on `frontend/src/app/routes.tsx` and `page-architecture-allowlist.ts` must
  prove route ownership matches `page-decisions-after.md`.
- No generated API client, OpenAPI schema or backend contract is changed by this frontend route decision.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-layouts/2026-05-08-1532/00-audit-report.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/03-story-candidates.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-before.md` - baseline des cinq residus.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md` - decisions finales et preuves.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/03-acceptance-traceability.md` - trace AC.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` - validations finales.
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` - alignement historique.
- `frontend/src/tests/page-architecture-allowlist.ts` - classifications finales.
- `frontend/src/tests/page-architecture-guards.test.ts` - seulement si une nouvelle condition de decision doit etre gardee.
- `frontend/src/app/routes.tsx` - seulement si une decision approuve une route.

Likely tests:

- `frontend/src/tests/page-architecture-guards.test.ts` - garde layout, classification et blocage decisionnel.
- `frontend/src/tests/BillingSuccessPage.test.tsx` - regression cible si le callback billing success devient route.
- `frontend/src/tests/App.test.tsx` - seulement si route publique/app ajoutee et test router necessaire.

Files not expected to change:

- `backend/**` - la decision frontend ne modifie pas le contrat backend.
- `frontend/package.json` - aucune dependance ni script.
- `frontend/src/styles/**` - aucun travail design-system.
- `frontend/src/pages/**/*.css` - aucun changement CSS attendu.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture layout
npm run test -- App router BillingSuccessPage
rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" `
  src/tests/page-architecture-allowlist.ts `
  ../_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md
rg -n "PASS with limitation|TODO|wildcard|compatibility wrapper|shim|alias|fallback|migration-only" `
  ../_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout `
  ../_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: une page publique privacy ou billing devient accessible sans validation produit/legal/billing.
  - Guardrail: AC2, AC3, AC4 et `RG-068`.
- Risk: un candidat mort est supprime sans audit removal complet.
  - Guardrail: deletion interdite dans cette story; AC6 exige story dediee.
- Risk: l'allowlist devient un passe-droit permanent.
  - Guardrail: AC5 exige owner, reason et expiry/permanence exacts.
- Risk: la fermeture masque un residu par `PASS with limitation`.
  - Guardrail: AC7 et scans des artefacts.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not delete any page file in this story unless `page-decisions-after.md` classifies it as removable, records explicit user decision, and the delete-only rule is satisfied.
- Do not route privacy or billing pages without explicit decision evidence.
- Do not add redirects, aliases, compatibility wrappers, fallbacks, re-exports or wildcard exceptions.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when closing this source finding.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1532/03-story-candidates.md#SC-101` - source candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1532/02-finding-register.md#F-101` - source finding.
- `_condamad/audits/frontend-layouts/2026-05-08-1532/01-evidence-log.md` - preuves runtime, tests et scans.
- `_condamad/stories/CS-107-classer-pages-layout-owner/00-story.md` - story precedente qui a cree le registre executable.
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` - etat actuel des cinq residus.
- `frontend/src/tests/page-architecture-allowlist.ts` - source executable des classifications.
- `frontend/src/tests/page-architecture-guards.test.ts` - guard de hierarchie et ownership.
- `_condamad/stories/regression-guardrails.md` - invariants applicables, notamment `RG-068`.
