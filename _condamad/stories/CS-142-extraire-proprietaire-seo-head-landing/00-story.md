# Story CS-142 extraire-proprietaire-seo-head-landing: Extraire le proprietaire SEO/head de la landing

Status: done

## 1. Objective

Faire de `LandingPage.tsx` une route de composition de contenu et deplacer les
mutations `document.*` vers un owner SEO/head landing petit, testable et
deterministe. La story ferme `F-004` en conservant les tags SEO, Open Graph,
canonical et JSON-LD avec nettoyage fiable.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-004`
- Reason for change: `LandingPage.tsx` possede aujourd'hui les mutations
  `document.title`, meta description, Open Graph, canonical et JSON-LD, ce qui
  melange page composition, tracking et side effect head.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/pages/landing`
- In scope:
  - Extraire les mutations head/JSON-LD dans un owner landing canonique.
  - Garder `LandingPage.tsx` comme composition des sections et tracking `landing_view`.
  - Tester ajout, mise a jour et nettoyage des tags head.
  - Supprimer les commentaires runtime de type story-era `AC*`.
- Out of scope:
  - Ajouter une dependance head-management.
  - Modifier routes, layout, CSS landing, contenu marketing, analytics CTA ou auth redirect.
  - Changer les valeurs SEO au-dela de leur ownership et nettoyage.
  - Modifier le backend ou les contrats API.
- Explicit non-goals:
  - Ne pas ajouter de compatibility wrapper ou fallback silencieux.
  - Ne pas garder de mutation brute `document.` dans `LandingPage.tsx`.
  - Ne pas ajouter de style inline.
  - Ne pas affaiblir `RG-068`, `RG-083`, `RG-084`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: move
- Primary archetype: ownership-routing-refactor
- Archetype reason: le deplacement des mutations head hors de `LandingPage.tsx`
  vers un owner canonique est un refactor d'ownership routing.
- Additional validation rules:
  - `LandingPage.tsx` doit avoir zero hit `document.` apres implementation.
  - Le nouvel owner doit nettoyer les tags crees et restaurer les tags existants
    modifiees.
  - Aucune dependance nouvelle n'est autorisee pour gerer le head.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: emplacement du code SEO/head et meilleure correction du nettoyage.
  - Interdit: changement de sections rendues, route, URL cible canonical hors
    logique existante, tracking `landing_view`, textes ou contrats API.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une dependance head-management ou un changement global de SEO provider est necessaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le head DOM doit etre teste en environnement DOM, pas seulement scanne. |
| Baseline Snapshot | yes | Les tags geres avant/apres et le scan `document.` doivent etre documentes. |
| Ownership Routing | yes | La responsabilite SEO/head doit etre routee hors page composition. |
| Allowlist Exception | yes | Le registre zero-exception rend les symboles interdits explicites et durables. |
| Contract Shape | no | Aucun contrat API, DTO ou schema genere n'est modifie. |
| Batch Migration | no | Le deplacement reste dans le domaine landing. |
| Reintroduction Guard | yes | Le retour de `document.` dans `LandingPage.tsx` doit echouer. |
| Persistent Evidence | yes | Les scans et resultats de tests doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Test DOM dans `frontend/src/tests/LandingPage.test.tsx` ou test landing head cible.
  - DOM `document.head` sous Vitest/Testing Library pour les meta, link canonical et scripts JSON-LD.
  - AST guard ou scan cible sur `LandingPage.tsx` pour `document.`.
- Secondary evidence:
  - Source scan `rg -n "document\\.|AC[0-9]"`.
  - Lint TypeScript.
- Static scans alone are not sufficient because:
  - le nettoyage doit etre observe dans `document.head` apres unmount ou changement de traduction.
- Runtime validation command:
  - `cd frontend; npm run test -- LandingPage`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing/landing-head-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing/landing-head-after.md`
- Required baseline content:
  - scan `document.` et `AC[0-9]` dans `LandingPage.tsx`;
  - inventaire des tags geres: title, description, og:title, og:description, og:type, og:url, canonical, JSON-LD app, JSON-LD FAQ;
  - tests actuels `LandingPage`.
- Expected invariant:
  - meme surface SEO exposee, mais owner head extrait et nettoyage deterministe.
- Allowed differences:
  - nettoyage plus strict des tags crees par la landing.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Composition des sections landing | `frontend/src/pages/landing/LandingPage.tsx` | helper SEO/head |
| Tracking `landing_view` | `frontend/src/pages/landing/LandingPage.tsx` ou hook landing local existant | owner head |
| Meta title/description/Open Graph/canonical | new owner under `frontend/src/pages/landing/` | `LandingPage.tsx` raw `document.` |
| JSON-LD app/FAQ | same landing head owner | duplicate helper global speculative |
| Tests head DOM | `frontend/src/tests/LandingPage.test.tsx` or focused landing head test | manual-only evidence |

Rules:

- Le nouvel owner doit rester page-local tant qu'aucun autre consommateur ne justifie une abstraction globale.
- Les mutations head doivent etre idempotentes et nettoyer les tags crees.

## 4e. Allowlist / Exception Register

No runtime exception is permitted; this register is a zero-allowance guard.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/pages/landing/LandingPage.tsx` | `document.` | Raw head mutation belongs to the landing head owner. | Permanent prohibition; no exception allowed. |
| `frontend/package.json` | `react-helmet`, `@helmet`, `head-manager` | New head dependency is outside dependency policy. | Permanent prohibition; user decision required. |

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun DTO, API, schema genere, export public ou type partage n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: un seul owner page-local est extrait.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline head landing | `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing/landing-head-before.md` | Inventaire des mutations actuelles et tests avant. |
| Preuve after head landing | `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing/landing-head-after.md` | Owner final, nettoyage, scans et tests apres. |

## 4i. Reintroduction Guard

- Guard target:
  - zero `document.` dans `LandingPage.tsx`;
  - zero commentaire story-era `AC[0-9]` dans le runtime landing;
  - owner head unique pour tags SEO landing;
  - nettoyage deterministe des tags ajoutes.
- Forbidden examples:
  - `document.title` dans `LandingPage.tsx`;
  - `document.querySelector` dans `LandingPage.tsx`;
  - commentaires `AC1`, `AC2` dans `frontend/src/pages/landing/**/*.tsx`;
  - dependency head-management ajoutee a `package.json`.
- Guard command/test:
  - `cd frontend; npm run test -- LandingPage`
  - `rg -n "document\\.|AC[0-9]" src/pages/landing/LandingPage.tsx src/pages/landing -g "*.tsx"`
  - `rg -n "react-helmet|@helmet|head-manager" package.json src`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md#F-004`
- Closure proof required: DOM head tests, negative `document.` scan in `LandingPage.tsx`, AC comment scan, lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/pages/landing/LandingPage.tsx` - `useEffect` modifie directement `document.title`, meta description, OG tags, canonical and JSON-LD.
- Evidence 2: `frontend/src/pages/landing/LandingPage.tsx` - contient des commentaires runtime `AC1`, `AC1.1.4`, `AC2`.
- Evidence 3: `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - `E-007` signale `document.` dans landing runtime.
- Evidence 4: `frontend/src/tests/visual-smoke.test.tsx` - les tests landing existants couvrent le rendu mais pas le nettoyage head.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage; `RG-068`, `RG-083`, `RG-084`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- `LandingPage.tsx` importe ou rend un owner SEO/head landing et ne contient plus de mutation brute `document.`.
- Le nouvel owner gere title, meta description, OG tags, canonical, JSON-LD app et JSON-LD FAQ.
- Les tags crees sont supprimes au nettoyage, les tags preexistants sont restaures.
- Les commentaires story-era `AC*` disparaissent du runtime landing.
- Un test prouve set/update/nettoyage du head.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-068` - `LandingPage` doit rester page sous `LandingLayout` sans nouvelle route ou layout.
  - `RG-083` - aucun correctif dark inline ou App.css ne doit accompagner l'extraction head.
  - `RG-084` - aucun fond page-level ne doit etre cree.
  - `RG-086` - pas de variante `app-bg--landing`.
  - `RG-087` - le fond global fixed reste hors scope.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - domaines backend, API, prediction et CSS non landing head.
- Required regression evidence:
  - test `LandingPage` pour head DOM et nettoyage;
  - scans `document.`, `AC[0-9]`, dependency head-management;
  - lint.
- Allowed differences:
  - owner code et nettoyage plus strict; aucune difference de contenu visible ou route.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `LandingPage.tsx` n'a plus de mutation head brute. | `rg "document\\." src/pages/landing/LandingPage.tsx`; `npm run test -- LandingPage`. |
| AC2 | Owner head landing unique. | `npm run test -- LandingPage`; `frontend/src/tests/LandingPage.test.tsx`. |
| AC3 | Le nettoyage restaure ou supprime les tags. | `npm run test -- LandingPage`; DOM assertions after unmount. |
| AC4 | Les commentaires story-era `AC*` disparaissent. | `rg "AC[0-9]" src/pages/landing`; `npm run test -- LandingPage`; `npm run lint`. |
| AC5 | Pas de dependance head ni fallback. | `rg "react-helmet|head-manager|fallback" package.json src/pages/landing`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer baseline head landing (AC: AC1, AC2, AC4)
  - [ ] Subtask 1.1 - Lire `LandingPage.tsx`, traductions `landing` et tests existants.
  - [ ] Subtask 1.2 - Rediger `landing-head-before.md` avec inventaire tags et scans.

- [ ] Task 2 - Extraire l'owner SEO/head (AC: AC1, AC2, AC3)
  - [ ] Subtask 2.1 - Creer un owner page-local sous `frontend/src/pages/landing/` si cela reduit la complexite.
  - [ ] Subtask 2.2 - Deplacer title, meta description, OG, canonical and JSON-LD dans cet owner.
  - [ ] Subtask 2.3 - Garantir idempotence, restauration et suppression au nettoyage.

- [ ] Task 3 - Nettoyer la page de composition (AC: AC1, AC4, AC5)
  - [ ] Subtask 3.1 - Retirer les commentaires `AC*` du runtime.
  - [ ] Subtask 3.2 - Garder `track("landing_view", getUtmParams())` dans le bon owner.

- [ ] Task 4 - Ajouter tests et preuve after (AC: AC2, AC3, AC4, AC5)
  - [ ] Subtask 4.1 - Ajouter tests DOM head set/update/nettoyage.
  - [ ] Subtask 4.2 - Rediger `landing-head-after.md` et executer validations.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `useTranslation("landing")` pour les valeurs SEO et FAQ.
  - `useAnalytics` and `getUtmParams` dans la page de composition pour `landing_view`.
  - helpers DOM standards existants; pas de dependance head externe.
- Do not recreate:
  - un provider SEO global speculatif;
  - une dependance `react-helmet` ou equivalente;
  - un fallback silencieux qui masque un tag absent;
  - compatibility wrappers, legacy aliases ou duplicate active implementation.
- Shared abstraction allowed only if:
  - elle reste page-local landing et remplace directement les mutations existantes.

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

- `document.` dans `frontend/src/pages/landing/LandingPage.tsx`
- `AC[0-9]` dans `frontend/src/pages/landing/**/*.tsx`
- `react-helmet`
- `head-manager`
- `fallback`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Composition landing sections | `frontend/src/pages/landing/LandingPage.tsx` | owner SEO/head |
| Landing view analytics | `frontend/src/pages/landing/LandingPage.tsx` | owner head |
| SEO/head landing | page-local owner sous `frontend/src/pages/landing/` | raw `document.` dans `LandingPage.tsx` |
| Head tests | `frontend/src/tests/LandingPage.test.tsx` or focused test | manual-only proof |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/landing/LandingPage.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/FaqSection.tsx`
- `frontend/src/i18n`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/setup.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/landing/LandingPage.tsx` - retirer les mutations head et commentaires `AC*`.
- `frontend/src/pages/landing/LandingHead.tsx` - nouvel owner page-local possible pour le side effect head.
- `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing/landing-head-before.md` - baseline.
- `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing/landing-head-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/LandingPage.test.tsx` - head set/update/nettoyage, page composition and analytics existing behavior.
- `frontend/src/tests/visual-smoke.test.tsx` - smoke landing quand les assertions existantes doivent suivre l'owner.

Files not expected to change:

- `frontend/src/app/routes.tsx` - route hors scope.
- `frontend/src/layouts/LandingLayout.tsx` - layout hors scope.
- `frontend/src/App.css` - hors scope.
- `backend/pyproject.toml` - aucune dependance backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- LandingPage
npm run lint
rg -n "document\." src/pages/landing/LandingPage.tsx
rg -n "AC[0-9]" src/pages/landing -g "*.tsx"
rg -n "react-helmet|@helmet|head-manager|compat|fallback" package.json src/pages/landing
```

Manual/runtime checks required:

- Monter puis demonter la landing dans le test DOM: verifier title, meta description, OG, canonical et JSON-LD.
- Verifier que la page rend encore les sept sections landing.

## 22. Regression Risks

- Risk: le nettoyage supprime un tag preexistant appartenant a une autre page.
  - Guardrail: AC3 DOM assertions.
- Risk: `LandingPage.tsx` redevient owner brut du document head.
  - Guardrail: AC1 scan `document.`.
- Risk: une dependance globale de head-management cree un nouveau domaine.
  - Guardrail: AC5 et Dependency Policy.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass guardrails through compatibility wrapper, alias, fallback, duplicate head owner or global provider.
- Respecter les instructions projet: commentaires globaux en francais pour tout fichier applicatif nouveau ou significativement modifie.

## 24. References

- `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md` - finding `F-004`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - preuve `E-007`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-004` - candidat source.
- `frontend/src/pages/landing/LandingPage.tsx` - owner actuel a reduire.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
