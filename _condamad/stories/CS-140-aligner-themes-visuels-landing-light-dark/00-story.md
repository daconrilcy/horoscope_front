# Story CS-140 aligner-themes-visuels-landing-light-dark: Aligner les themes visuels landing light/dark

Status: done

## 1. Objective

Faire de light et dark mode deux variantes du meme systeme visuel landing:
memes roles de surface, texte, bordure et elevation, avec valeurs themees
coherentes. La story ferme `F-002` sans toucher au montage de route, sans
nouveau fond landing et sans reecrire les sections marketing.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-002`
- Reason for change: l'audit observe que light mode lit comme glass pale sur
  fond pale, tandis que dark mode laisse le starfield dominer et differencie
  moins les surfaces locales.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Demarrer seulement apres livraison de `CS-139` et de son artefact after
    d'ownership CSS.
  - Ajuster les valeurs themees des roles landing confirmes par CS-139.
  - Conserver le starfield dark-only et le fond global canonique.
  - Produire captures desktop/mobile light/dark premier viewport, mid-page et menu mobile.
  - Ajouter ou durcir les tests si le contrat visuel devient plus precis.
- Out of scope:
  - Creer une nouvelle taxonomie CSS au-dela des roles confirmes par CS-139.
  - Modifier le contenu, les routes, l'auth redirect, SEO/head ou analytics.
  - Ajouter une dependance de contraste, d'animation ou de theming.
  - Refaire le layout mobile au-dela des ajustements de lisibilite.
- Explicit non-goals:
  - Ne pas recreer `app-bg--landing`.
  - Ne pas dupliquer le fond global dans `LandingPage.css`.
  - Ne pas corriger le theme via `frontend/src/App.css` ou inline styles.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: l'alignement visuel theme frontend n'a pas d'archetype
  standard; la story active baseline, ownership, runtime tests, reintroduction
  guard et preuves persistantes.
- Additional validation rules:
  - La story doit partir des roles landing confirmes par `CS-139`; sans
    artefact after `CS-139`, l'implementation doit s'arreter.
  - Les contrastes spot doivent etre documentes pour texte principal, texte
    muted, CTA et texte de carte en light et dark.
  - Les differences permises sont visuelles et themees uniquement.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: valeurs CSS light/dark de surfaces, bordures, ombres et textes landing.
  - Interdit: changement de route, contenu, analytics, SEO/head, fond global et structure section.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un contraste cible ne peut pas etre atteint sans
  changer la composition ou le contenu au-dela des roles CSS landing.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests et captures doivent verifier la cascade effective light/dark. |
| Baseline Snapshot | yes | Les screenshots et contrastes before/after sont requis. |
| Ownership Routing | yes | Les corrections doivent rester dans les owners landing ou theme canoniques. |
| Allowlist Exception | no | Aucune exception large de contraste ou de surface n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO ou type public n'est touche. |
| Batch Migration | no | Un seul domaine landing est ajuste. |
| Reintroduction Guard | yes | Le retour de surfaces light non classees ou d'un fond landing dedie doit echouer. |
| Persistent Evidence | yes | Les captures, contrastes et scans doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `frontend/src/tests/design-system-guards.test.ts` pour dark mode, fond canonique et page-level backgrounds.
  - `frontend/src/tests/visual-smoke.test.tsx` pour les attentes landing representatives.
  - DOM et CSS charges par Vite sur `/` pour les captures Playwright.
- Secondary evidence:
  - Scans `rg` des selectors `.dark .landing-layout`, `--landing-*` et `app-bg--landing`.
  - Mesures de contraste spot documentees dans l'artefact after.
- Static scans alone are not sufficient because:
  - la hierarchie visuelle depend du theme actif, du viewport, du menu mobile et du fond global.
- Runtime validation command:
  - `cd frontend; npm run test -- design-system visual-smoke AppBgStyles`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/landing-theme-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/landing-theme-after.md`
- Required baseline content:
  - screenshots desktop/mobile light/dark premier viewport, mid-page et menu mobile;
  - valeurs ou captures de contraste spot pour texte principal, muted, CTA et cartes;
  - resultats tests `design-system`, `visual-smoke`, `AppBgStyles`.
- Expected invariant:
  - light et dark partagent la meme hierarchie de roles, avec seulement les valeurs themees qui changent.
- Allowed differences:
  - contraste, opacite, bordures et ombres landing; aucune difference de route, contenu ou fond global.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Valeurs themees landing | `frontend/src/layouts/LandingLayout.css` | `frontend/src/App.css`, inline styles |
| Roles hero deja locaux | `frontend/src/pages/landing/LandingPage.css` si CS-139 le confirme | sections non hero |
| Menu mobile landing | `frontend/src/pages/landing/sections/LandingNavbar.css` | overrides globaux |
| Guard dark/fond canonique | `frontend/src/tests/design-system-guards.test.ts` | commentaire non executable |
| Smoke visual landing | `frontend/src/tests/visual-smoke.test.tsx` | screenshots sans test associe |

Rules:

- Les corrections dark doivent rester sous `.dark .landing-layout` ou un owner
  CSS landing exact.
- Les roles light et dark doivent garder le meme nom semantique.
- Toute correction locale doit citer le role consomme et le contraste vise.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception durable n'est autorisee pour surfaces light non
  classees, liens bleu navigateur, inline styles ou fond landing dedie.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat de donnees, API, route, schema genere ou type public n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les ajustements restent dans le domaine landing et ne migrent pas de consommateurs multi-domaines.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline theme landing | `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/landing-theme-before.md` | Captures, contrastes et tests avant. |
| Preuve after theme landing | `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/landing-theme-after.md` | Captures, contrastes, scans et tests apres. |

## 4i. Reintroduction Guard

- Guard target:
  - `.dark .landing-layout` comme owner theme landing;
  - absence de `app-bg--landing`;
  - absence de corrections dans `App.css` ou inline styles;
  - surfaces landing light/dark consommees par roles semantiques.
- Forbidden examples:
  - `style=` sous `frontend/src/pages/landing`;
  - `#0000ee`, `color: blue`, grandes surfaces white en `.dark`;
  - `app-bg--landing`;
  - nouveaux selectors dark landing dans `frontend/src/App.css`.
- Guard command/test:
  - `cd frontend; npm run test -- design-system visual-smoke AppBgStyles`
  - `rg -n "app-bg--landing|style=|#0000ee|color:\\s*blue" src/pages/landing src/layouts src/App.css`
  - `rg -n "\\.dark\\s+\\.landing-layout|--landing-surface|--landing-text" src/layouts/LandingLayout.css src/pages/landing -g "*.css"`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md#F-002`
- Closure proof required: screenshots before/after, contrast spots, guard tests, scan no inline/fond dedie and lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md` - `F-002` reports divergent light and dark visual systems.
- Evidence 2: `frontend/src/layouts/LandingLayout.css` - `.dark .landing-layout` overrides many surface roles but keeps the same broad owner.
- Evidence 3: `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - `E-009` documents washed-out light surfaces and dark low separation.
- Evidence 4: `frontend/src/tests/design-system-guards.test.ts` - `RG-083` and canonical background guards are already executable.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage; `RG-083`, `RG-084`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- Light et dark mode utilisent les memes roles `--landing-*` pour surfaces,
  bordures, elevation, texte fort, texte principal et texte muted.
- Les cartes et panels se detachent du fond dans les deux themes.
- Le starfield reste dark-only et decoratif, sans devenir le principal moyen de hierarchie.
- Le menu mobile conserve lisibilite et separation dans les deux themes.
- Les tests et l'artefact after documentent les contrastes spot.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - la story touche directement le dark mode des surfaces landing.
  - `RG-084` - les ajustements ne doivent pas creer de fond concurrent.
  - `RG-086` - la landing ne doit pas recuperer une variante de fond dediee.
  - `RG-087` - le fond global fixed viewport doit rester stable.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - surfaces non landing et backend non touchees.
- Required regression evidence:
  - tests `design-system`, `visual-smoke`, `AppBgStyles`;
  - screenshots light/dark desktop/mobile et menu mobile;
  - contrastes spot documentes.
- Allowed differences:
  - valeurs light/dark landing pour lisibilite; aucune difference de route, contenu, fond global ou auth.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Artefact after `CS-139` disponible. | `rg "Allowed Owner Map" landing-css-ownership-after.md`; after artifact. |
| AC2 | Roles landing paires light/dark coherents. | `npm run test -- design-system visual-smoke`; after artifact. |
| AC3 | Hierarchie equivalente en captures light/dark. | before/after screenshots; `npm run test -- visual-smoke`. |
| AC4 | Contrastes spot documentes. | `rg "Contrast spot" landing-theme-after.md`; `npm run test -- design-system`. |
| AC5 | Fond landing dedie absent. | `npm run test -- AppBgStyles design-system`; `rg "app-bg--landing" src`. |
| AC6 | Menu mobile lisible sans overflow. | menu screenshots; `npm run test -- visual-smoke`; overflow metric. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer baseline theme et contrastes (AC: AC1, AC2, AC3, AC4)
  - [ ] Subtask 1.1 - Lire les roles landing dans l'artefact after `CS-139`.
  - [ ] Subtask 1.2 - Rediger `landing-theme-before.md` avec screenshots et contrastes spot.

- [ ] Task 2 - Ajuster les valeurs themees landing (AC: AC2, AC4, AC5)
  - [ ] Subtask 2.1 - Harmoniser surfaces, bordures et elevations light/dark.
  - [ ] Subtask 2.2 - Harmoniser texte principal, muted, CTA et carte.
  - [ ] Subtask 2.3 - Garder le starfield dark-only et decoratif.

- [ ] Task 3 - Verifier responsive et menu mobile (AC: AC3, AC6)
  - [ ] Subtask 3.1 - Capturer mobile viewport et mobile menu light/dark.
  - [ ] Subtask 3.2 - Documenter absence de scroll horizontal.

- [ ] Task 4 - Durcir tests et preuve after (AC: AC2, AC4, AC5, AC6)
  - [ ] Subtask 4.1 - Mettre a jour les tests si le contrat visuel est rendu plus strict.
  - [ ] Subtask 4.2 - Rediger `landing-theme-after.md` avec commandes et differences autorisees.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - roles `--landing-*` confirmes par CS-139;
  - tokens existants `--premium-*`, `--glass-*`, `--color-*` quand leur sens correspond;
  - guards `design-system`, `visual-smoke` et `AppBgStyles`.
- Do not recreate:
  - un fond landing dedie;
  - un theme provider;
  - des couleurs inline ou corrections dans `App.css`;
  - compatibility wrappers, legacy aliases ou fallback silencieux.
- Shared abstraction allowed only if:
  - elle factorise un role light/dark consomme par au moins deux surfaces landing et reste dans les CSS landing.

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
- `#0000ee`
- `color: blue`
- `PASS with limitation`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Theme landing | `frontend/src/layouts/LandingLayout.css` | `App.css`, inline styles |
| Hero local roles | `frontend/src/pages/landing/LandingPage.css` | nav/footer CSS |
| Menu mobile | `frontend/src/pages/landing/sections/LandingNavbar.css` | layout global |
| Background global | `frontend/src/styles/backgrounds.css` and `frontend/src/styles/premium-theme.css` | landing page CSS |

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
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/ProblemSection.css`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/SolutionSection.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/AppBgStyles.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/layouts/LandingLayout.css` - aligner valeurs light/dark des roles landing.
- `frontend/src/tests/visual-smoke.test.tsx` - renforcer le contrat visuel quand les roles acceptes changent.
- `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/landing-theme-before.md` - baseline.
- `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/landing-theme-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - guards dark/background existants.
- `frontend/src/tests/visual-smoke.test.tsx` - smoke landing.
- `frontend/src/tests/AppBgStyles.test.ts` - fond canonique.

Files not expected to change:

- `frontend/src/app/routes.tsx` - route hors scope.
- `frontend/src/pages/landing/LandingPage.tsx` - composition et SEO hors scope.
- `frontend/src/App.css` - corrections theme interdites.
- `backend/pyproject.toml` - aucune dependance backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
rg "Allowed Owner Map" _condamad\stories\CS-139-refactoriser-ownership-css-landing\landing-css-ownership-after.md
cd frontend
npm run test -- design-system visual-smoke AppBgStyles
npm run lint
rg -n "app-bg--landing|style=|#0000ee|color:\s*blue" src/pages/landing src/layouts src/App.css
rg -n "\.dark\s+\.landing-layout|--landing-surface|--landing-text" src/layouts/LandingLayout.css src/pages/landing -g "*.css"
```

Manual/runtime checks required:

- Desktop 1440px light/dark premier viewport et mid-page.
- Mobile 390px light/dark premier viewport et menu ouvert.
- Documenter dans `landing-theme-after.md` les contrastes spot et l'absence de scroll horizontal.

## 22. Regression Risks

- Risk: dark mode corrige localement en dupliquant le fond ou des surfaces non classees.
  - Guardrail: `RG-083`, `RG-084`, AC5.
- Risk: light mode gagne en contraste mais diverge encore en hierarchie.
  - Guardrail: AC2, AC3, contrastes spot.
- Risk: menu mobile devient une troisieme grammaire de surface.
  - Guardrail: AC6 et captures mobile menu.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass guardrails through inline style, App.css override, compatibility wrapper, alias, fallback or hidden residual theme role.
- Respecter les instructions projet: commentaires globaux en francais pour tout fichier applicatif nouveau ou significativement modifie.

## 24. References

- `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md` - finding `F-002`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - preuves `E-008`, `E-009`, `E-010`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-002` - candidat source.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-083`, `RG-084`, `RG-086`, `RG-087`.
- `frontend/src/layouts/LandingLayout.css` - owner theme landing.
