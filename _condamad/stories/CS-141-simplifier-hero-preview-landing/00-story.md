# Story CS-141 simplifier-hero-preview-landing: Simplifier le hero preview de la landing

Status: done

## 1. Objective

Remplacer la boucle React decorative du hero preview landing par un rendu
statique ou CSS-only. Le hero doit rester visuellement utile, conserver les
analytics CTA et ne plus executer de timer runtime dans le domaine landing.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-003`
- Reason for change: `HeroSection.tsx` utilise `window.setInterval` toutes les
  80ms pour animer des elements decoratifs, ce qui melange rendu marketing et
  boucle runtime alors qu'une animation CSS ou un etat statique suffit.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/pages/landing`
- In scope:
  - Modifier `HeroSection.tsx` pour supprimer la boucle d'intervalle.
  - Si une animation est conservee, la porter en CSS tokenise dans `LandingPage.css`.
  - Ajouter un test ou guard prouvant l'absence de timer dans le domaine landing.
  - Conserver les CTA, liens, textes et analytics existants.
- Out of scope:
  - Modifier les sections autres que le hero.
  - Changer le design system global, le fond global, SEO/head, route ou auth redirect.
  - Ajouter canvas, WebGL, librairie d'animation ou nouvelle dependance.
  - Recomposer toute la landing pour un objectif de performance general.
- Explicit non-goals:
  - Ne pas recreer la boucle via `setTimeout`, `requestAnimationFrame` ou un hook global.
  - Ne pas ajouter de style inline.
  - Ne pas changer les noms d'evenements analytics des CTA.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la simplification runtime d'un composant frontend decoratif
  n'a pas d'archetype standard; la story active runtime source, baseline,
  ownership, reintroduction guard et preuves persistantes.
- Additional validation rules:
  - La preuve doit inclure un scan zero-hit de `setInterval`, `setTimeout` et
    `requestAnimationFrame` dans `frontend/src/pages/landing`.
  - Si une animation CSS remplace le state loop, elle doit respecter le media
    query `prefers-reduced-motion` deja present pour la landing.
  - Les CTA doivent garder leurs handlers `track`.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: animation decorative moins dynamique ou CSS-only dans le hero preview.
  - Interdit: changement des liens CTA, textes, analytics, route, sections ou API.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le rendu exige une animation JS continue, canvas/WebGL ou une dependance externe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le composant rendu et l'absence de timer doivent etre verifies par test ou scan cible. |
| Baseline Snapshot | yes | Le comportement avant/apres du hero preview et le scan intervalle doivent etre documentes. |
| Ownership Routing | yes | La logique decorative doit rester dans le hero ou son CSS adjacent. |
| Allowlist Exception | no | Aucune exception de timer landing n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route ou type public n'est modifie. |
| Batch Migration | no | Un seul composant landing est vise. |
| Reintroduction Guard | yes | Le retour de timers decoratifs doit echouer. |
| Persistent Evidence | yes | Les scans, screenshots et tests before/after doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard ou test source dans `frontend/src/tests/visual-smoke.test.tsx` ou test hero cible.
  - DOM rendu de `HeroSection` via Testing Library pour CTA et contenu visible.
  - Scan cible `rg` sur `window.setInterval`, `setTimeout` et `requestAnimationFrame`.
- Secondary evidence:
  - Screenshots premier viewport light/dark.
  - Lint TypeScript.
- Static scans alone are not sufficient because:
  - le rendu doit garder les CTA, textes et etats visibles, pas seulement masquer un symbole.
- Runtime validation command:
  - `cd frontend; npm run test -- LandingPage visual-smoke`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-141-simplifier-hero-preview-landing/hero-preview-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-141-simplifier-hero-preview-landing/hero-preview-after.md`
- Required baseline content:
  - source scan des timers actuels dans `HeroSection.tsx`;
  - screenshots premier viewport light/dark;
  - tests actuels `LandingPage` et `visual-smoke`.
- Expected invariant:
  - les CTA et le contenu hero restent disponibles; aucun timer landing ne reste actif.
- Allowed differences:
  - animation decorative simplifiee, statique ou CSS-only, sans timer JS.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Markup hero | `frontend/src/pages/landing/sections/HeroSection.tsx` | helper global ou composant partage non necessaire |
| Animation decorative hero | `frontend/src/pages/landing/LandingPage.css` | intervalle React permanent, inline styles |
| Analytics CTA | `frontend/src/pages/landing/sections/HeroSection.tsx` avec `useAnalytics` | helper non teste ou perte de tracking |
| Guard anti-timer | `frontend/src/tests/visual-smoke.test.tsx` ou test hero cible | commentaire manuel |

Rules:

- Preferer un rendu statique ou CSS-only.
- Aucun etat React periodique n'est autorise; un etat local reste possible
  seulement s'il est declenche par interaction utilisateur.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucun timer n'est autorise dans landing.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO ou type public n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: une seule surface composant hero est modifiee.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline hero preview | `_condamad/stories/CS-141-simplifier-hero-preview-landing/hero-preview-before.md` | Timers actuels, screenshots et tests avant. |
| Preuve after hero preview | `_condamad/stories/CS-141-simplifier-hero-preview-landing/hero-preview-after.md` | Absence de timer, screenshots et tests apres. |

## 4i. Reintroduction Guard

- Guard target:
  - `window.setInterval`, `setInterval`, `setTimeout` ou `requestAnimationFrame` dans landing;
  - perte accidentelle des handlers `track` des CTA;
  - animation qui ignore `prefers-reduced-motion`.
- Forbidden examples:
  - `window.setInterval(updateLiveState, 80)`;
  - `requestAnimationFrame` dans `HeroSection.tsx`;
  - `style=` dans le hero;
  - disparition de `track("hero_cta_click"` ou `track("secondary_cta_click"`.
- Guard command/test:
  - `cd frontend; npm run test -- LandingPage visual-smoke`
  - `rg -n "window\\.setInterval|setInterval\\(|requestAnimationFrame|setTimeout\\(" src/pages/landing`
  - `rg -n "hero_cta_click|secondary_cta_click|prefers-reduced-motion" src/pages/landing src/tests`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md#F-003`
- Closure proof required: negative timer scan, focused tests, first-viewport screenshots and lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/pages/landing/sections/HeroSection.tsx` - `useEffect` lance `window.setInterval(updateLiveState, 80)` pour animer tool, trend et typing.
- Evidence 2: `frontend/src/pages/landing/LandingPage.css` - contient deja animations CSS hero et media query `prefers-reduced-motion` via le scope landing.
- Evidence 3: `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - `E-007` signale l'intervalle hero comme responsabilite runtime decorative.
- Evidence 4: `frontend/src/tests/visual-smoke.test.tsx` - smoke landing disponible pour assertions CSS et rendu.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage; `RG-083`, `RG-084`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- `HeroSection.tsx` ne contient plus de boucle intervalle decorative.
- Le preview hero affiche une composition utile en light/dark.
- Les CTA gardent leurs liens et events analytics.
- `prefers-reduced-motion` coupe ou neutralise toute animation decorative conservee.
- Les tests echouent si un timer revient dans le domaine landing.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - le rendu hero dark ne doit pas redevenir illisible.
  - `RG-084` - aucune animation hero ne doit porter un fond global concurrent.
  - `RG-086` - pas de variante de fond landing pendant le changement hero.
  - `RG-087` - le fond global fixed viewport reste hors scope.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - domaines non hero landing.
- Required regression evidence:
  - `npm run test -- LandingPage visual-smoke`;
  - scan zero-hit des timers landing;
  - screenshots premier viewport light/dark.
- Allowed differences:
  - animation hero moins dynamique ou statique; aucune difference de CTA, route ou analytics.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Aucun timer JS dans landing. | `rg "setInterval|requestAnimationFrame|setTimeout" src/pages/landing`; `npm run test -- LandingPage`. |
| AC2 | Hero preview coherent light/dark. | before/after screenshots; `npm run test -- visual-smoke`. |
| AC3 | Analytics CTA conserves. | `npm run test -- LandingPage`; `rg "hero_cta_click|secondary_cta_click" src/pages/landing`. |
| AC4 | Reduced motion neutralise le mouvement. | `npm run test -- visual-smoke`; `rg "prefers-reduced-motion|hero-live" src/pages/landing`. |
| AC5 | Aucune dependance nouvelle. | `npm run lint`; `rg "style=|canvas|WebGL|three" src/pages/landing package.json`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer baseline hero et timers (AC: AC1, AC2)
  - [ ] Subtask 1.1 - Lire `HeroSection.tsx`, `LandingPage.css` et les tests landing.
  - [ ] Subtask 1.2 - Rediger `hero-preview-before.md` avec scan timer et screenshots.

- [ ] Task 2 - Remplacer la boucle decorative (AC: AC1, AC2, AC4)
  - [ ] Subtask 2.1 - Remplacer l'intervalle si un etat statique suffit.
  - [ ] Subtask 2.2 - Porter l'effet necessaire en CSS tokenise, respecte par `prefers-reduced-motion`.
  - [ ] Subtask 2.3 - Eviter toute nouvelle dependance ou API canvas/WebGL.

- [ ] Task 3 - Preserver CTA et analytics (AC: AC3)
  - [ ] Subtask 3.1 - Garder `Link` `/register`, ancre `#how-it-works` et appels `track`.
  - [ ] Subtask 3.2 - Ajouter un test si la couverture existante ne prouve pas les handlers.

- [ ] Task 4 - Ajouter guards et preuve after (AC: AC1, AC4, AC5)
  - [ ] Subtask 4.1 - Ajouter un guard zero timer landing.
  - [ ] Subtask 4.2 - Rediger `hero-preview-after.md` et executer validations.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HeroSection.tsx` pour la composition hero et analytics CTA.
  - `LandingPage.css` pour animation CSS et reduced motion.
  - `visual-smoke.test.tsx` ou test landing cible pour guard anti-retour.
- Do not recreate:
  - un hook animation global;
  - une boucle `setInterval`, `setTimeout` ou `requestAnimationFrame`;
  - un canvas/WebGL;
  - compatibility wrappers, legacy aliases ou fallback silencieux.
- Shared abstraction allowed only if:
  - aucun nouveau shared abstraction n'est cree; le changement reste local au hero.

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

- `window.setInterval`
- `requestAnimationFrame`
- `setTimeout`
- `style=`
- `canvas`
- `WebGL`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Hero markup and CTA analytics | `frontend/src/pages/landing/sections/HeroSection.tsx` | shared hook animation |
| Hero styling and motion | `frontend/src/pages/landing/LandingPage.css` | inline styles, JS loop |
| Guard anti timer | `frontend/src/tests/visual-smoke.test.tsx` or focused landing test | manual review only |

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
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/FaqSection.test.tsx`
- `frontend/src/tests/setup.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/landing/sections/HeroSection.tsx` - supprimer la boucle intervalle.
- `frontend/src/pages/landing/LandingPage.css` - porter l'effet hero en CSS si conserve.
- `_condamad/stories/CS-141-simplifier-hero-preview-landing/hero-preview-before.md` - baseline.
- `_condamad/stories/CS-141-simplifier-hero-preview-landing/hero-preview-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/visual-smoke.test.tsx` - guard anti timer et motion si approprie.
- `frontend/src/tests/LandingPage.test.tsx` - focused test si existant ou a creer pour CTA/hero.

Files not expected to change:

- `frontend/src/layouts/LandingLayout.css` - CSS theme general hors scope sauf impact direct.
- `frontend/src/app/routes.tsx` - route hors scope.
- `frontend/src/App.css` - owner global interdit.
- `backend/pyproject.toml` - aucune dependance backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- LandingPage visual-smoke
npm run lint
rg -n "window\.setInterval|setInterval\(|requestAnimationFrame|setTimeout\(" src/pages/landing
rg -n "hero_cta_click|secondary_cta_click|prefers-reduced-motion" src/pages/landing src/tests
rg -n "style=|canvas|WebGL|three" src/pages/landing package.json
```

Manual/runtime checks required:

- Premier viewport light/dark: verifier que le hero preview reste comprehensible.
- Reduced motion: verifier que l'effet conserve est coupe ou fige.

## 22. Regression Risks

- Risk: l'animation est deplacee vers une autre API de boucle.
  - Guardrail: AC1, AC5 et scan timers.
- Risk: le hero devient statique au point de perdre l'information preview.
  - Guardrail: AC2 screenshots.
- Risk: les analytics CTA sont retires pendant la simplification.
  - Guardrail: AC3 scan et test.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass guardrails through a different timer, compatibility wrapper, alias, fallback, inline style, canvas or WebGL.
- Respecter les instructions projet: commentaires globaux en francais pour tout fichier applicatif nouveau ou significativement modifie.

## 24. References

- `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md` - finding `F-003`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - preuve `E-007`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-003` - candidat source.
- `frontend/src/pages/landing/sections/HeroSection.tsx` - owner actuel du hero.
- `frontend/src/pages/landing/LandingPage.css` - owner CSS hero et reduced motion.
