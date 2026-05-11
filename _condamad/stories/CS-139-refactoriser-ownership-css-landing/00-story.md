# Story CS-139 refactoriser-ownership-css-landing: Refactoriser l'ownership CSS landing

Status: done

## 1. Objective

Transformer le bloc dense de variables landing en modele fini d'owners visuels
par responsabilite, sans changer la route `/`, le montage `LandingLayout` ni le
fond global. La livraison doit fermer `F-001` avec une carte d'ownership
persistante, des guards deterministes et aucune categorie residuelle large.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-001`
- Reason for change: l'audit `frontend-landing-page` constate que `LandingLayout.css`
  declare 256 variables `--landing-*` dans un seul owner, ce qui melange les
  decisions de surfaces, typographie, navigation, hero, mobile et sections.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Couvrir `frontend/src/layouts/LandingLayout.css` et
    `frontend/src/pages/landing/**` comme surfaces du meme domaine audite.
  - Classer les variables et styles landing par owners finis: base page,
    surfaces, type, navigation, hero, mobile, sections et footer.
  - Conserver les fichiers landing existants comme owners locaux quand ils
    consomment deja les roles `--landing-*`.
  - Ajouter une preuve persistante avant/apres du nombre de declarations et de
    l'usage des groupes `--landing-*`.
  - Adapter les guards `design-system` ou `visual-smoke` seulement pour rendre
    la nouvelle carte d'ownership executable.
- Out of scope:
  - Modifier `RootLayout`, `LandingLayout.tsx`, `LandingRedirect` ou la table de routes.
  - Harmoniser finement light/dark au-dela des consequences directes du split
    d'owners; ce travail est route vers `SC-002`.
  - Changer les textes marketing, les CTA, l'analytics, le SEO/head ou le hero
    preview.
  - Modifier `frontend/src/App.css` ou le backend.
- Explicit non-goals:
  - Ne pas recreer `app-bg--landing`.
  - Ne pas ajouter de fond page-level concurrent au fond global canonique.
  - Ne pas ajouter de styles inline.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-086` ou `RG-087`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: custom
- Archetype reason: le catalogue CONDAMAD ne contient pas d'archetype dedie a
  une convergence de tokens CSS frontend page-scoped; la story active les
  contrats necessaires pour baseline, ownership, anti-retour et preuves
  persistantes.
- Additional validation rules:
  - La carte d'ownership doit nommer chaque groupe `--landing-*` retenu, son
    owner canonique exact et au moins un consommateur audite.
  - Tout groupe `--landing-*` hors carte exacte ou sans consommateur doit
    bloquer la story.
  - Les tests doivent prouver que le fond landing dedie ne revient pas.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: renommage ou regroupement de variables landing avec migration de
    tous les consommateurs dans le domaine landing.
  - Interdit: changement de route, fond global, contenu marketing, analytics,
    SEO/head et comportement responsive attendu.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une variable landing parait inutilisee mais que la
  suppression ne peut pas etre prouvee par scan et screenshots before/after.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards frontend doivent rendre les fichiers CSS et composants landing effectifs, pas seulement scanner du texte. |
| Baseline Snapshot | yes | Le nombre de declarations et la carte d'owners doivent etre compares avant/apres. |
| Ownership Routing | yes | Chaque responsabilite visuelle landing doit avoir un owner canonique. |
| Allowlist Exception | no | Aucune exception large ou categorie residuelle n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, payload ou schema genere n'est modifie. |
| Batch Migration | no | La migration reste mono-domaine landing; elle n'est pas un lot multi-package. |
| Reintroduction Guard | yes | Le retour d'un owner `--landing-*` fourre-tout doit etre bloque. |
| Persistent Evidence | yes | La carte d'ownership et les scans before/after doivent persister avec la story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `frontend/src/tests/design-system-guards.test.ts` pour les guards CSS actifs.
  - `frontend/src/tests/visual-smoke.test.tsx` pour les assertions landing representatives.
  - DOM rendu de `LandingPage` via les tests existants.
- Secondary evidence:
  - Scans `rg` des declarations et usages `--landing-*`.
  - Screenshots desktop/mobile light/dark avant/apres.
- Static scans alone are not sufficient because:
  - une variable peut etre syntaxiquement presente sans produire un rendu coherent ou sans etre consommee par la section attendue.
- Runtime validation command:
  - `cd frontend; npm run test -- design-system visual-smoke AppBgStyles page-architecture`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-after.md`
- Required baseline content:
  - count des declarations `--landing-*` par fichier;
  - inventaire des groupes et consommateurs;
  - screenshots desktop/mobile light/dark premier viewport et mid-page;
  - resultat des tests cibles.
- Expected invariant:
  - `/` reste sous `LandingLayout`, le fond global reste canonique et aucun style inline n'est introduit.
- Allowed differences:
  - noms et emplacement des variables landing, si tous les consommateurs sont migres et documentes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Roles globaux landing | `frontend/src/layouts/LandingLayout.css` | `frontend/src/App.css`, styles inline |
| Hero visual roles | `frontend/src/pages/landing/LandingPage.css` | section CSS non hero, App.css |
| Navigation et mobile menu | `frontend/src/pages/landing/sections/LandingNavbar.css` | `LandingLayout.css` fourre-tout |
| Footer | `frontend/src/pages/landing/sections/LandingFooter.css` | page CSS globale |
| Sections marketing | CSS adjacent de chaque section sous `frontend/src/pages/landing/sections` | variables non classees dans un owner unique |
| Guard de carte d'ownership | `frontend/src/tests/design-system-guards.test.ts` | documentation seule non executable |

Rules:

- Toute variable retenue doit etre nommee par role, pas par apparence brute
  reutilisee dans plusieurs sections.
- Les sections doivent consommer les roles existants avant de creer un nouveau
  role local.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception durable n'est autorisee pour un groupe
  `--landing-*` non classe, un wildcard ou une categorie residuelle.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, route, schema, DTO, export public ou type frontend n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: un seul domaine frontend landing est touche; les groupes sont des responsabilites internes du meme owner.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline ownership CSS | `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-before.md` | Etat actuel des variables, usages, tests et captures. |
| Preuve after ownership CSS | `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-after.md` | Carte exacte des owners, counts, guards et captures. |

## 4i. Reintroduction Guard

- Guard target:
  - groupes `--landing-*` absents de la carte exacte;
  - retour de `app-bg--landing`;
  - literals visuels hors owner landing deja migres par CS-085;
  - styles inline dans les sources landing.
- Forbidden examples:
  - `--landing-misc-*`, `--landing-common-*`, `--landing-temp-*`;
  - `--landing-shared-*`, `--landing-base-*`, `--landing-general-*`, `--landing-global-*`;
  - `app-bg--landing`;
  - `style=` sous `frontend/src/pages/landing`;
  - nouveau literal `rgba(` ou `#` dans les section CSS hors owner autorise.
- Guard command/test:
  - `cd frontend; npm run test -- design-system visual-smoke AppBgStyles page-architecture`
  - `rg -n "app-bg--landing|style=|--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts`
  - `rg -n "^\\s*--landing-" src/layouts/LandingLayout.css src/pages/landing -g "*.css"`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md#F-001`
- Closure proof required: before/after ownership artifact, guard design-system, screenshots, count scan and lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - `E-005` reports 256 declarations `--landing-*` in `LandingLayout.css`.
- Evidence 2: `frontend/src/layouts/LandingLayout.css` - the `.landing-layout` block owns surface, navigation, hero, mobile and type variables in one namespace.
- Evidence 3: `frontend/src/tests/design-system-guards.test.ts` - guards already block migrated landing literals outside the owner block.
- Evidence 4: `frontend/src/tests/visual-smoke.test.tsx` - smoke assertions cover representative landing CSS roles.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage; `RG-083`, `RG-084`, `RG-086` and `RG-087` apply.

## 6. Target State

After implementation:

- Le namespace landing est decrit par une carte exacte de groupes, owners,
  consumers et commande de guard dans l'artefact after.
- `LandingLayout.css` ne porte que les primitives transverses landing et les
  overrides theme necessaires.
- Les sections adjacentes consomment les roles de leur responsabilite sans
  dupliquer des valeurs brutes.
- Les guards echouent si un groupe non classe ou une variante de fond dediee revient.
- Les ecarts visuels autorises se limitent aux consequences du routing de variables.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - la story touche les surfaces landing et ne doit pas recreer de grandes surfaces dark non classees.
  - `RG-084` - les variables landing ne doivent pas redefinir un fond global concurrent.
  - `RG-086` - la landing ne doit pas recreer `app-bg--landing`.
  - `RG-087` - le fond global fixed viewport doit rester protege pendant le refactor CSS.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - domaines backend, API, prediction, composants et layouts non landing.
- Required regression evidence:
  - `npm run test -- design-system visual-smoke AppBgStyles page-architecture`;
  - scan `app-bg--landing`, `style=` et groupes `--landing-*` hors carte exacte;
  - screenshots before/after.
- Allowed differences:
  - regroupement et renommmage de variables landing documentes; aucune difference de route ou fond global.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Carte owner exacte pour chaque groupe `--landing-*`. | `rg "^\\s*--landing-" src/layouts src/pages/landing`; after artifact. |
| AC2 | Chaque groupe retenu cite un consommateur audite. | `npm run test -- design-system`; after artifact. |
| AC3 | Les invariants shell landing tiennent. | `npm run test -- AppBgStyles page-architecture`; `frontend/src/tests/AppBgStyles.test.ts`. |
| AC4 | Pas de style inline landing nouveau. | `npm run test -- design-system visual-smoke`; `rg "style=" src/pages/landing`. |
| AC5 | Captures light/dark desktop/mobile conservees. | before/after screenshots; `npm run test -- visual-smoke`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et la carte actuelle (AC: AC1, AC2, AC5)
  - [ ] Subtask 1.1 - Lire `LandingLayout.css`, `LandingPage.css`, les CSS de sections et les guards existants.
  - [ ] Subtask 1.2 - Rediger `landing-css-ownership-before.md` avec counts, groupes actuels, consommateurs et screenshots.

- [ ] Task 2 - Router les variables vers des owners finis (AC: AC1, AC2, AC4)
  - [ ] Subtask 2.1 - Nommer les groupes transverses conserves dans `LandingLayout.css` avec owner et consommateur.
  - [ ] Subtask 2.2 - Deplacer ou renommer les roles locaux seulement quand le consommateur canonique est prouve.
  - [ ] Subtask 2.3 - Supprimer les groupes sans consommation prouvee ou bloquer sur decision utilisateur.

- [ ] Task 3 - Renforcer les guards anti-retour (AC: AC2, AC3, AC4)
  - [ ] Subtask 3.1 - Adapter `design-system-guards.test.ts` pour rejeter tout groupe hors carte exacte.
  - [ ] Subtask 3.2 - Conserver les guards `app-bg--landing`, fond canonique et literals landing.

- [ ] Task 4 - Capturer l'etat after (AC: AC1, AC3, AC5)
  - [ ] Subtask 4.1 - Rediger `landing-css-ownership-after.md`.
  - [ ] Subtask 4.2 - Executer les tests, lint et screenshots cibles.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/layouts/LandingLayout.css` pour les primitives transverses landing.
  - CSS adjacent des sections sous `frontend/src/pages/landing/sections` pour les roles locaux deja possedes.
  - `frontend/src/tests/design-system-guards.test.ts` pour les guards CSS executables.
- Do not recreate:
  - une deuxieme taxonomie de tokens landing;
  - un fond landing dedie;
  - un helper CSS global dans `App.css`;
  - des wrappers de compatibility, legacy aliases ou fallback silencieux.
- Shared abstraction allowed only if:
  - elle remplace une duplication prouvee par deux consommateurs landing actifs et reste dans le domaine landing.

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
- `style=` sous `frontend/src/pages/landing`
- `--landing-misc-*`, `--landing-common-*`, `--landing-temp-*`
- `--landing-shared-*`, `--landing-base-*`, `--landing-general-*`, `--landing-global-*`
- `PASS with limitation`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Primitives landing transverses | `frontend/src/layouts/LandingLayout.css` | `App.css`, page CSS non landing |
| Hero | `frontend/src/pages/landing/LandingPage.css` | variables hero dans footer/nav |
| Navigation | `frontend/src/pages/landing/sections/LandingNavbar.css` | layout CSS fourre-tout |
| Sections marketing | CSS adjacent de section | variables non classees |

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
- `frontend/src/pages/landing/sections/LandingFooter.css`
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

- `frontend/src/layouts/LandingLayout.css` - reduire et classer les primitives transverses landing.
- `frontend/src/pages/landing/LandingPage.css` - aligner les roles hero quand la carte prouve un mauvais owner.
- `frontend/src/pages/landing/sections/LandingNavbar.css` - porter les roles nav/mobile quand la carte prouve un mauvais owner.
- `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-before.md` - baseline.
- `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - guard carte d'ownership landing.
- `frontend/src/tests/visual-smoke.test.tsx` - assertions representatives landing.

Files not expected to change:

- `frontend/src/app/routes.tsx` - la route `/` reste stable.
- `frontend/src/app/guards/LandingRedirect.tsx` - redirection auth hors scope.
- `frontend/src/App.css` - owner global interdit pour ce changement.
- `backend/pyproject.toml` - aucune dependance backend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- design-system visual-smoke AppBgStyles page-architecture
npm run lint
rg -n "app-bg--landing|style=|--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts
rg -n "^\\s*--landing-" src/layouts/LandingLayout.css src/pages/landing -g "*.css"
```

Manual/runtime checks required:

- Desktop light/dark premier viewport et mid-page: verifier hierarchie conservee.
- Mobile light/dark premier viewport: verifier absence de scroll horizontal et de regression de menu.

## 22. Regression Risks

- Risk: un groupe landing residuel remplace le probleme actuel par un nom plus vague.
  - Guardrail: AC1, AC2, `landing-css-ownership-after.md`.
- Risk: le refactor CSS reintroduit un fond landing dedie.
  - Guardrail: `RG-084`, `RG-086`, AC3.
- Risk: une section perd ses roles visuels pendant le renommage.
  - Guardrail: AC5, screenshots et `visual-smoke`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass guardrails through compatibility wrapper, alias, fallback, hidden residual category or route/background change.
- Respecter les instructions projet: commentaires globaux en francais pour tout fichier applicatif nouveau ou significativement modifie.

## 24. References

- `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md` - finding `F-001`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md` - preuves `E-004`, `E-005`, `E-006`, `E-010`.
- `_condamad/audits/frontend-landing-page/2026-05-11-1706/03-story-candidates.md#SC-001` - candidat source.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-083`, `RG-084`, `RG-086`, `RG-087`.
- `frontend/src/layouts/LandingLayout.css` - owner actuel du namespace landing.
