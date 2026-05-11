# Story CS-144 converger-contrat-visuel-landing-menu-mobile: Clarifier le contrat visuel landing light/dark et menu mobile

Status: done

## 1. Objective

Faire converger les surfaces landing light/dark et le menu mobile vers un petit
contrat visuel partage: surface primaire, surface secondaire, bordure, texte,
texte muted et CTA. Le rendu doit perdre le grand glow mobile dominant sans
changer le fond global, le starfield dark-only, les routes ou le contenu.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-002`
- Reason for change: l'audit constate que light et dark sont gardes mais lisent
  encore comme deux traitements differents. Le menu mobile ajoute aussi une
  lueur floutee qui affaiblit la hierarchie.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Clarifier les roles CSS landing pour cartes et menu mobile.
  - Ajuster `LandingLayout.css`, `LandingPage.css` et `LandingNavbar.css` pour consommer ces roles.
  - Modifier les CSS de sections uniquement si elles consomment un role renomme ou resserre.
  - Capturer desktop/mobile light/dark top, mid et menu mobile before/after.
- Out of scope:
  - Modifier `RootLayout`, `App.css`, route `/`, SEO/head, auth redirect, analytics ou backend.
  - Simplifier le hero au-dela des roles consommes; ce travail est route vers `CS-143`.
  - Ajouter une nouvelle taxonomie globale de design tokens.
- Explicit non-goals:
  - Ne pas recreer `app-bg--landing`.
  - Ne pas rendre le starfield actif en light mode.
  - Ne pas ajouter de style inline.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-085`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: custom
- Archetype reason: le catalogue ne contient pas d'archetype specifique pour
  convergence visuelle CSS light/dark page-scoped; cette story active baseline,
  ownership, runtime, reintroduction guard et preuves persistantes.
- Additional validation rules:
  - Les roles landing retenus doivent etre finis, nommes semantiquement et consommes par au moins une surface auditee.
  - Les corrections dark/light doivent rester dans les owners landing, jamais dans `App.css` ou inline.
  - Le menu mobile doit etre valide avec screenshots light/dark et mesure sans scroll horizontal.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: ajustements de couleurs, surfaces, bordures, opacites, ombres et glow landing/menu.
  - Interdit: changement de structure route, contenu, CTA, analytics, SEO/head, fond global et starfield dark-only.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le contrat visuel exige une modification de contenu marketing, de structure mobile majeure ou du fond global canonique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les effets light/dark et menu mobile doivent etre verifies au runtime avec CSS effectif. |
| Baseline Snapshot | yes | Les captures et contrastes before/after sont requis par l'audit. |
| Ownership Routing | yes | Chaque role visuel doit rester sous son owner landing exact. |
| Allowlist Exception | no | Aucune exception wildcard de role, glow ou surface n'est autorisee. |
| Contract Shape | no | Aucun contrat API, route, schema ou type public n'est modifie. |
| Batch Migration | no | La convergence reste dans un domaine landing unique. |
| Reintroduction Guard | yes | Le retour du fond dedie, inline styles ou roles non classes doit echouer. |
| Persistent Evidence | yes | Les captures, contrastes, scans et decisions de roles doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `frontend/src/tests/design-system-guards.test.ts` pour les roles, fonds et interdits CSS.
  - CSS effectif de `/` via `LandingLayout`, `LandingPage` et `LandingNavbar`.
  - `visual-smoke.test.tsx`, `design-system-guards.test.ts` et `AppBgStyles.test.ts`.
  - Captures Playwright desktop/mobile en light/dark, menu ferme et ouvert.
- Secondary evidence:
  - Scans des roles `--landing-*`, absence de `app-bg--landing`, absence de `style=`.
- Static scans alone are not sufficient because:
  - le probleme est visuel et depend de la cascade, du theme et de l'etat menu mobile.
- Runtime validation command:
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/landing-visual-contract-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/landing-visual-contract-after.md`
- Required baseline content:
  - screenshots desktop light/dark top et mid;
  - screenshots mobile light/dark top et menu ouvert;
  - spot contrast hero titre/body, menu links, CTA et copy de cartes;
  - scan des roles landing et fonds dedies.
- Expected invariant:
  - light et dark partagent la meme hierarchie; le menu mobile n'a plus de glow dominant non classe.
- Allowed differences:
  - valeurs themees, opacites, ombres et intensite du menu mobile.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Roles transverses landing | `frontend/src/layouts/LandingLayout.css` | `frontend/src/App.css`, inline styles |
| Consommation hero/cards | `frontend/src/pages/landing/LandingPage.css` | variables non classees ou section voisine |
| Navigation et menu mobile | `frontend/src/pages/landing/sections/LandingNavbar.css` | overrides globaux |
| Sections marketing | CSS adjacent sous `frontend/src/pages/landing/sections` | roles vagues sans consommateur |
| Guard role/fond | `frontend/src/tests/design-system-guards.test.ts` | documentation seule |

Rules:

- Les roles doivent etre semantiques: primary surface, secondary surface, border, text, muted text, CTA.
- Tout nouveau role `--landing-*` doit etre ajoute a la carte owner finie ou refuse.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception large n'est permise; tout role conserve doit etre exact, nomme et garde.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO ou type public n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les consommateurs sont dans le meme domaine landing et ne forment pas un lot multi-domaine.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline contrat visuel landing | `landing-visual-contract-before.md` | Captures, contrastes, roles et scans avant. |
| Preuve after contrat visuel landing | `landing-visual-contract-after.md` | Roles finaux, captures, contrastes, scans et tests apres. |

## 4i. Reintroduction Guard

- Guard target:
  - `app-bg--landing` absent;
  - corrections landing absentes de `App.css` et des styles inline;
  - roles `--landing-*` finis et non wildcard;
  - glow mobile non dominant et classe par selecteur exact.
- Forbidden examples:
  - `app-bg--landing`;
  - `style=` sous `src/pages/landing` ou `src/layouts`;
  - `#0000ee`, `color: blue`;
  - `--landing-misc-*`, `--landing-common-*`, `--landing-temp-*`, `--landing-global-*`;
  - grand `filter`/`backdrop-filter` mobile sans entree exacte dans l'artefact after.
- Guard command/test:
  - AST architecture guard dans `frontend/src/tests/design-system-guards.test.ts`.
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`
  - `rg -n "app-bg--landing|style=|#0000ee|color:\\s*blue" src/pages/landing src/layouts src/App.css`
  - `rg -n "--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-002`
- Closure proof required: screenshots before/after, spot contrasts, runtime metrics, owner scans, guard tests and lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md` - `F-002` reports light/dark visual divergence and menu mobile glow.
- Evidence 2: `_condamad/audits/frontend-landing-page/2026-05-11-1841/00-audit-report.md` - visual notes identify mobile menu light/dark screenshots as clearest before artifacts.
- Evidence 3: `frontend/src/layouts/LandingLayout.css` - owner des roles transverses landing actuels.
- Evidence 4: `frontend/src/pages/landing/sections/LandingNavbar.css` - owner actif du menu mobile concerne par le glow.
- Evidence 5: `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/00-story.md` - premier alignement theme deja livre; cette story traite le residuel plus etroit.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage; `RG-083`, `RG-084`, `RG-085`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- Les roles de surfaces landing et menu mobile sont petits, finis et documentes.
- Light et dark utilisent la meme hierarchie de roles avec valeurs themees.
- Le menu mobile n'est plus domine par une grande lueur floutee.
- Le starfield reste dark-only et le fond global reste canonique.
- Les captures after et tests prouvent absence d'overflow, lisibilite et non-regression des guardrails.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - la story touche directement le dark mode des surfaces landing.
  - `RG-084` - elle ne doit pas creer de fond page-level concurrent.
  - `RG-085` - elle doit conserver le fond astral dark comme unique fond dark global.
  - `RG-086` - elle doit garder `app-bg--landing` absent.
  - `RG-087` - elle ne doit pas rendre le fond dependant de la hauteur landing.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - domaines non landing visual.
- Required regression evidence:
  - tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles`, `page-architecture`;
  - screenshots desktop/mobile light/dark, menu ouvert;
  - scans des roles, inline styles, fond dedie et liens bleus.
- Allowed differences:
  - valeurs visuelles des roles landing et menu; aucune difference de route, texte, analytics, SEO ou fond global.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le contrat declare des roles visuels landing finis. | After artifact; `npm run test -- design-system`; scan roles `--landing-*`. |
| AC2 | La hierarchie themee landing reste equivalente. | Screenshots before/after; spot contrasts; `npm run test -- visual-smoke`. |
| AC3 | Le menu mobile n'a plus de glow dominant non classe. | Screenshots; `rg -n "filter\|backdrop-filter\|blur" src/pages/landing/sections/LandingNavbar.css`; after artifact. |
| AC4 | Les interdits visuels globaux restent absents. | `npm run test -- AppBgStyles design-system page-architecture`; scan interdits. |
| AC5 | Le responsive landing reste sans scroll horizontal. | Profile: `baseline_before_after_diff`; Playwright `scrollWidth === clientWidth`; `npm run test -- visual-smoke`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer baseline contrat visuel (AC: AC1, AC2, AC3, AC5)
  - [ ] Subtask 1.1 - Lire `LandingLayout.css`, `LandingPage.css`, `LandingNavbar.css`, CSS de sections et tests.
  - [ ] Subtask 1.2 - Creer `landing-visual-contract-before.md` avec screenshots, contrasts, scans et tests.

- [ ] Task 2 - Definir et consommer les roles landing finis (AC: AC1, AC2, AC4)
  - [ ] Subtask 2.1 - Resserer les roles transverses dans `LandingLayout.css`.
  - [ ] Subtask 2.2 - Migrer les consommateurs landing vers ces roles sans doublon.
  - [ ] Subtask 2.3 - Supprimer les roles ou effets non consommes; bloquer si un role ne peut pas etre classe.

- [ ] Task 3 - Simplifier le menu mobile (AC: AC2, AC3, AC5)
  - [ ] Subtask 3.1 - Reduire ou retirer le glow/flou dominant dans `LandingNavbar.css`.
  - [ ] Subtask 3.2 - Verifier menu ouvert en light et dark a 390px.

- [ ] Task 4 - Renforcer preuves et guards (AC: AC1, AC3, AC4, AC5)
  - [ ] Subtask 4.1 - Adapter `design-system-guards.test.ts` ou `visual-smoke.test.tsx` si de nouveaux roles deviennent contractuels.
  - [ ] Subtask 4.2 - Creer `landing-visual-contract-after.md`, executer tests, lint, scans et captures.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - roles `--landing-*` deja classifies par `CS-139`.
  - guards `design-system`, `visual-smoke`, `AppBgStyles` et `page-architecture`.
  - CSS adjacent de sections pour consommation locale uniquement.
- Do not recreate:
  - un theme provider;
  - des variables `--landing-*` vagues ou mecaniques;
  - des corrections dans `App.css`;
  - un fond ou halo page-level concurrent.
- Shared abstraction allowed only if:
  - elle remplace une duplication prouvee entre au moins deux surfaces landing et reste dans les CSS landing existants.

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

- `app-bg--landing`
- `frontend/src/App.css`
- `style=`
- `#0000ee`, `color: blue`
- `--landing-misc-*`, `--landing-common-*`, `--landing-temp-*`, `--landing-shared-*`, `--landing-base-*`, `--landing-general-*`, `--landing-global-*`
- `PASS with limitation`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Roles transverses landing | `frontend/src/layouts/LandingLayout.css` | `App.css`, inline styles |
| Hero/card consumption | `frontend/src/pages/landing/LandingPage.css` | nav/footer CSS |
| Mobile menu | `frontend/src/pages/landing/sections/LandingNavbar.css` | layout global, App.css |
| Section cards | CSS adjacent de section | variables transverses non classees |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/ProblemSection.css`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/SolutionSection.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/layouts/LandingLayout.css` - clarifier roles transverses light/dark.
- `frontend/src/pages/landing/LandingPage.css` - consommer les roles resserres pour hero/cards.
- `frontend/src/pages/landing/sections/LandingNavbar.css` - reduire glow/flou menu mobile et aligner roles.
- CSS de sections sous `frontend/src/pages/landing/sections/*.css` - uniquement si un role consomme est renomme ou retire.
- `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/landing-visual-contract-before.md` - baseline.
- `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/landing-visual-contract-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - owner map et interdits.
- `frontend/src/tests/visual-smoke.test.tsx` - smoke light/dark/menu/responsive.
- `frontend/src/tests/AppBgStyles.test.ts` - fond canonique.

Files not expected to change:

- `frontend/src/App.css` - corrections theme interdites.
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
rg -n "app-bg--landing|style=|#0000ee|color:\s*blue" src/pages/landing src/layouts src/App.css
rg -n "--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts
rg -n "filter|backdrop-filter|blur" src/pages/landing/sections/LandingNavbar.css src/pages/landing/LandingPage.css
```

Manual/runtime checks required:

- Capturer desktop light/dark top et mid.
- Capturer mobile light/dark top et menu ouvert.
- Documenter spot contrasts et metric `scrollWidth === clientWidth` dans `landing-visual-contract-after.md`.

## 22. Regression Risks

- Risk: les roles deviennent une nouvelle taxonomie vague.
  - Guardrail: AC1, owner map finie et scan des noms interdits.
- Risk: le menu mobile perd son glow mais perd aussi sa separation.
  - Guardrail: AC2, AC3 et captures menu light/dark.
- Risk: une correction visuelle contourne le fond global.
  - Guardrail: `RG-084`, `RG-086`, AC4.

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

- `_condamad/audits/frontend-landing-page/2026-05-11-1841/00-audit-report.md` - audit source et notes visuelles.
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-002` - finding theme/menu.
- `_condamad/audits/frontend-landing-page/2026-05-11-1841/03-story-candidates.md#SC-002` - candidat source.
- `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/00-story.md` - precedent theme landing clos.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
