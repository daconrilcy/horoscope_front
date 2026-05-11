# Story CS-143 simplifier-complexite-visuelle-hero-landing: Simplifier la complexite visuelle du hero landing

Status: done

## 1. Objective

Reduire la complexite visuelle et CSS du hero landing apres la fermeture du
timer JS. Le hero doit rester un signal produit lisible, conserver les CTA, les
evenements analytics et le responsive actuel. Les animations et couches
filtrees doivent etre limitees a un contrat explicite.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-001`
- Reason for change: l'audit signale que `LandingPage.css` conserve 995 lignes,
  7 keyframes et 10 descendants hero animes au runtime. Le hero reste donc
  plus couteux a maintenir que necessaire.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Simplifier `frontend/src/pages/landing/sections/HeroSection.tsx` uniquement si la structure du hero doit perdre des couches decoratives.
  - Reduire dans `frontend/src/pages/landing/LandingPage.css` les animations, filtres et panels concurrents du hero.
  - Conserver `hero_cta_click`, `secondary_cta_click`, les libelles accessibles, les liens et le responsive existant.
  - Produire des preuves before/after avec screenshots et counts `@keyframes`, `animation:` et descendants animes.
- Out of scope:
  - Changer les sections non hero, le routing, `LandingLayout`, `LandingHead`, SEO, auth redirect ou API.
  - Refaire tout le contrat light/dark/menu mobile; ce point est route vers `CS-144`.
  - Ajouter canvas, WebGL, dependance d'animation ou remplacement image-only.
- Explicit non-goals:
  - Ne pas recreer de timer JS dans landing.
  - Ne pas ajouter de style inline.
  - Ne pas recreer `app-bg--landing` ou un fond landing dedie.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-085`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: le catalogue ne contient pas d'archetype dedie a une
  simplification visuelle CSS frontend; cette story active runtime source,
  baseline, ownership, reintroduction guard et evidence persistante.
- Additional validation rules:
  - Toute animation hero conservee doit etre nommee, comptee et couverte par `prefers-reduced-motion`.
  - Le nombre de familles `@keyframes` hero doit etre reduit a au plus une famille nommee, ou zero si le rendu statique suffit.
  - Les CTA et analytics doivent etre prouves par test ou scan cible.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: reduction de mouvement, simplification des panels decoratifs redondants, simplification d'ombres/filtres hero.
  - Interdit: changement des routes, contenus marketing, CTA, analytics, SEO/head, fond global ou menu mobile hors impact direct.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le rendu souhaite exige plus d'une famille d'animation permanente, canvas/WebGL, image decorative principale ou dependance externe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le rendu hero et les animations effectives doivent etre verifies par tests, scans et captures. |
| Baseline Snapshot | yes | L'audit demande counts et screenshots before/after pour prouver la simplification. |
| Ownership Routing | yes | Le hero doit rester sous ses owners `HeroSection.tsx` et `LandingPage.css`. |
| Allowlist Exception | no | Aucune exception large d'animation ou filtre n'est autorisee. |
| Contract Shape | no | Aucun contrat API, route, schema ou type public n'est modifie. |
| Batch Migration | no | La story vise une seule surface hero landing. |
| Reintroduction Guard | yes | Les timers, animations non nommees et complexite non classee doivent etre bloques. |
| Persistent Evidence | yes | Les artefacts before/after doivent persister dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard ou test source dans `frontend/src/tests/visual-smoke.test.tsx` / `frontend/src/tests/design-system-guards.test.ts`.
  - DOM rendu par `LandingPage.test.tsx` pour contenu hero, CTA et analytics.
  - `visual-smoke.test.tsx` pour absence d'overflow, reduced motion et assertions representatives.
  - Scans CSS cibles pour `@keyframes`, `animation:` et timers.
- Secondary evidence:
  - Screenshots light/dark `screenshots/*top.png` de l'audit et nouvelles captures after.
- Static scans alone are not sufficient because:
  - une reduction CSS peut casser la lisibilite ou les CTA sans changer les symboles recherches.
- Runtime validation command:
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/hero-complexity-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/hero-complexity-after.md`
- Required baseline content:
  - counts `@keyframes`, `animation:` et descendants hero animes;
  - scan timers landing;
  - screenshots light/dark top desktop et mobile;
  - tests cibles avant changement.
- Expected invariant:
  - le hero reste lisible et actionnable, sans timer JS ni empilement decoratif non classe.
- Allowed differences:
  - moins de mouvement, moins de panels, ombres/filtres plus sobres.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Markup et CTA hero | `frontend/src/pages/landing/sections/HeroSection.tsx` | composant partage speculative |
| Styles, panels et motion hero | `frontend/src/pages/landing/LandingPage.css` | `App.css`, inline styles, JS loop |
| Guard complexite hero | `frontend/src/tests/visual-smoke.test.tsx` ou guard landing cible | commentaire manuel |
| Roles theme landing consommes par hero | `frontend/src/layouts/LandingLayout.css` et owners confirmes par CS-139 | nouveaux roles vagues |

Rules:

- Toute reduction de couche doit rester locale au hero.
- Toute animation conservee doit etre rattachee a un selecteur exact et a une raison produit.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: cette story ne permet pas d'exception large; les animations conservees doivent etre decrites dans l'artefact after et dans un guard exact.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO ou type public n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la simplification est mono-surface hero, sans migration par lots.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline complexite hero | `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/hero-complexity-before.md` | Counts, scans, captures et tests avant. |
| Preuve after complexite hero | `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/hero-complexity-after.md` | Counts reduits, captures, scans et tests apres. |

## 4i. Reintroduction Guard

- Guard target:
  - timers JS sous `frontend/src/pages/landing`;
  - plus d'une famille `@keyframes` hero permanente;
  - `animation:` hero non nommee ou non couverte par reduced motion;
  - couches `filter` / `backdrop-filter` hero non justifiees.
- Forbidden examples:
  - `setInterval(`, `setTimeout(` ou `requestAnimationFrame(` dans landing;
  - nouvelle animation infinie non listee dans `hero-complexity-after.md`;
  - `style=` dans `HeroSection.tsx`;
  - `canvas`, `WebGL` ou `three` pour une decoration hero.
- Guard command/test:
  - AST architecture guard dans `frontend/src/tests/visual-smoke.test.tsx` ou `frontend/src/tests/design-system-guards.test.ts`.
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`
  - `rg -n "window\\.setInterval|setInterval\\(|requestAnimationFrame|setTimeout\\(" src/pages/landing`
  - `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing/LandingPage.css src/pages/landing/sections/LandingNavbar.css`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-001`
- Closure proof required: before/after screenshots, counts animation/keyframes, runtime animated descendant metric, timer scan, tests and lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md` - `F-001` reports 995 CSS lines, 7 keyframes and 10 animated hero descendants.
- Evidence 2: `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-001` -
  candidate requires reducing always-running hero motion to at most one named
  CSS animation family.
- Evidence 3: `frontend/src/pages/landing/sections/HeroSection.tsx` - active hero owner, must remain free of timers and inline styles.
- Evidence 4: `frontend/src/pages/landing/LandingPage.css` - active hero CSS owner and source of residual animation/filter complexity.
- Evidence 5: `_condamad/stories/CS-141-simplifier-hero-preview-landing/00-story.md` - prior timer closure is done; this story must not reopen that runtime loop.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage; `RG-083`, `RG-084`, `RG-085`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- Le hero contient un modele de preview plus simple, statique ou avec une seule famille d'animation nommee.
- Les couches decoratives non necessaires et variables actives inutilisees sont reduites ou prouvees conservees.
- `HeroSection.tsx` reste sans timer et sans style inline.
- Les CTA, analytics, libelles accessibles et responsive restent inchanges.
- Les preuves after montrent la baisse de complexite sans nouveau fond landing.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - le hero touche les surfaces dark auditees et ne doit pas redevenir illisible.
  - `RG-084` - aucune couche hero ne doit devenir un fond page-level concurrent.
  - `RG-085` - le fond dark astral reste global et dark-only.
  - `RG-086` - la landing ne doit pas recreer `app-bg--landing`.
  - `RG-087` - le fond global fixed viewport ne doit pas dependre du hero.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - domaines non hero landing.
- Required regression evidence:
  - tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles`, `page-architecture`;
  - scans timers, `style=`, `app-bg--landing`, `@keyframes` et `animation:`;
  - screenshots light/dark top desktop et mobile.
- Allowed differences:
  - reduction visuelle du mouvement et des panels; aucune difference de route, CTA, analytics ou fond global.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Budget hero: une famille d'animation CSS nommee au maximum. | Before/after artifacts; `rg -n "@keyframes\|animation:" src/pages/landing/LandingPage.css`. |
| AC2 | Aucun timer JS landing n'est reintroduit. | `rg -n "setInterval\|setTimeout\|requestAnimationFrame" src/pages/landing` zero-hit. |
| AC3 | Les analytics CTA hero restent inchanges. | `npm run test -- LandingPage`; scan `hero_cta_click\|secondary_cta_click\|aria-label`. |
| AC4 | Le hero reste lisible sans scroll horizontal. | Screenshots after; Playwright `scrollWidth === clientWidth`; `npm run test -- visual-smoke`. |
| AC5 | Les interdits hero restent absents. | `npm run test -- design-system AppBgStyles page-architecture`; scan interdits. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline de complexite hero (AC: AC1, AC2, AC4)
  - [ ] Subtask 1.1 - Lire `HeroSection.tsx`, `LandingPage.css`, `visual-smoke.test.tsx` et l'audit `2026-05-11-1841`.
  - [ ] Subtask 1.2 - Creer `hero-complexity-before.md` avec counts, scans, screenshots et tests.

- [ ] Task 2 - Simplifier le rendu et CSS hero (AC: AC1, AC3, AC4, AC5)
  - [ ] Subtask 2.1 - Supprimer les panels, variables et effets decoratifs non necessaires.
  - [ ] Subtask 2.2 - Garder au plus une famille d'animation nommee et compatible `prefers-reduced-motion`.
  - [ ] Subtask 2.3 - Verifier que les CTA, liens, textes et analytics ne changent pas.

- [ ] Task 3 - Ajouter ou ajuster les guards hero (AC: AC1, AC2, AC5)
  - [ ] Subtask 3.1 - Adapter `visual-smoke.test.tsx` ou un test landing cible pour borner le budget hero.
  - [ ] Subtask 3.2 - Ne pas ajouter d'allowlist wildcard ou folder-wide.

- [ ] Task 4 - Capturer l'etat after (AC: AC1, AC2, AC3, AC4, AC5)
  - [ ] Subtask 4.1 - Creer `hero-complexity-after.md` avec differences autorisees.
  - [ ] Subtask 4.2 - Executer tests, lint, scans et captures.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HeroSection.tsx` pour markup, CTA et analytics.
  - `LandingPage.css` pour les styles hero.
  - `visual-smoke.test.tsx`, `LandingPage.test.tsx` et `design-system-guards.test.ts` pour les guards existants.
- Do not recreate:
  - une boucle runtime decorative;
  - une taxonomie CSS hero parallele;
  - un fond landing dedie;
  - un composant shared speculative.
- Shared abstraction allowed only if:
  - aucune nouvelle abstraction partagee n'est attendue; tout besoin doit d'abord reuser les roles landing existants.

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

- `setInterval(`, `setTimeout(`, `requestAnimationFrame(`
- `style=` sous `frontend/src/pages/landing`
- `app-bg--landing`
- `canvas`, `WebGL`, `three`
- `PASS with limitation`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Hero structure and CTA analytics | `frontend/src/pages/landing/sections/HeroSection.tsx` | shared decorative component |
| Hero CSS and motion | `frontend/src/pages/landing/LandingPage.css` | `App.css`, inline styles, JS timer |
| Landing runtime visual guards | `frontend/src/tests/visual-smoke.test.tsx` | screenshots without executable guard |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/landing/sections/HeroSection.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/tests/LandingPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/landing/sections/HeroSection.tsx` - reduire la structure
  quand la baseline prouve des couches decoratives redondantes.
- `frontend/src/pages/landing/LandingPage.css` - simplifier motion, panels, filtres et variables hero.
- `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/hero-complexity-before.md` - baseline.
- `_condamad/stories/CS-143-simplifier-complexite-visuelle-hero-landing/hero-complexity-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/LandingPage.test.tsx` - CTA, contenu et analytics si DOM change.
- `frontend/src/tests/visual-smoke.test.tsx` - budget hero et reduced motion.
- `frontend/src/tests/design-system-guards.test.ts` - guard anti-retour si le budget est centralise.

Files not expected to change:

- `frontend/src/App.css` - owner global interdit.
- `frontend/src/app/routes.tsx` - route hors scope.
- `frontend/src/pages/landing/LandingHead.tsx` - SEO/head hors scope.
- `backend/pyproject.toml` - aucune dependance backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture
npm run lint
rg -n "window\.setInterval|setInterval\(|requestAnimationFrame|setTimeout\(" src/pages/landing
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing/LandingPage.css src/pages/landing/sections/LandingNavbar.css
rg -n "hero_cta_click|secondary_cta_click|aria-label" src/pages/landing/sections/HeroSection.tsx
rg -n "app-bg--landing|style=|canvas|WebGL|three" src/pages/landing src/layouts package.json
```

Manual/runtime checks required:

- Capture desktop 1440px et mobile 390px en light/dark top.
- Mesurer `scrollWidth === clientWidth` a 390px et 1440px.
- Documenter dans `hero-complexity-after.md` les animations conservees et les differences autorisees.

## 22. Regression Risks

- Risk: la simplification altere les CTA ou leur tracking.
  - Guardrail: AC3 et tests `LandingPage`.
- Risk: une animation est simplement renommee sans baisser la complexite.
  - Guardrail: AC1, counts before/after et guard exact.
- Risk: le hero compense la reduction de panels par un fond local concurrent.
  - Guardrail: `RG-084`, `RG-086`, AC5.

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

- `_condamad/audits/frontend-landing-page/2026-05-11-1841/00-audit-report.md` - audit source et contexte de fermeture.
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-001` - finding hero complexity.
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-001` - candidat source.
- `_condamad/stories/CS-141-simplifier-hero-preview-landing/00-story.md` - precedent timer hero clos.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
