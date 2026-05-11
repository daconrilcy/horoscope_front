# Story CS-147 optimiser-conversion-mobile-landing: Optimiser la conversion mobile de la landing

Status: ready-to-review

## 1. Objective

Mettre en oeuvre le plan d'evolution landing issu de l'audit utilisateur:
compacter le premier ecran mobile, exposer plus tot un signal produit et une
preuve forte, reduire la dette `backdrop-filter` sous `RG-088`, puis clarifier
le chemin de conversion pricing/FAQ sans changer le catalogue tarifaire ni le
fond global. La sortie attendue est une landing mobile plus efficace et
mesurable, avec preuves before/after et tests cibles.

## 2. Trigger / Source

- Source type: audit
- Source reference: audit utilisateur colle dans la demande du 2026-05-11 sur
  l'evolution de la landing page.
- Reason for change: le hero mobile mesure environ `1426px` sur un viewport
  `390x844`; le mock produit et les preuves fortes arrivent trop tard, tandis
  que les filtres landing actifs restent sous contrainte `RG-088`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Compactifier le hero mobile pour faire apparaitre le mock produit ou son
    debut dans le premier viewport `390x844`.
  - Ajouter pres du CTA hero une preuve compacte issue des contenus landing
    existants: Swiss Ephemeris, RGPD ou sans carte bancaire.
  - Reduire ou classifier exactement les `backdrop-filter` landing conserves
    dans navbar, social proof et testimonials.
  - Clarifier la conversion pricing/FAQ en gardant `getActivePlans()` comme
    source unique, les liens `/register?plan=PLAN_CODE` et l'evenement
    `pricing_plan_select`.
  - Ajouter ou adapter les tests et artefacts landing pertinents.
- Out of scope:
  - Modifier le backend, Stripe, l'authentification, les routes API, OpenAPI ou
    les donnees tarifaires source.
  - Modifier `RootLayout`, le fond global, `App.css`, le starfield ou une
    variante `app-bg--landing`.
  - Refaire le copywriting marketing global, le SEO/head ou le systeme de
    traduction hors cles landing deja consommees.
  - Ajouter une librairie d'animation, de tracking, de layout ou de parsing CSS.
- Explicit non-goals:
  - Ne pas dupliquer `SocialProofSection` dans le hero; seules des preuves
    compactes reutilisant les traductions ou donnees existantes sont admises.
  - Ne pas changer le plan recommande, les prix, les quotas ou l'ordre source
    de `pricingConfig`.
  - Ne pas ajouter de style inline.
  - Ne pas ajouter de nouveaux `@keyframes`, `animation:`, `filter` ou
    `backdrop-filter` sans exception exacte.
  - Ne pas affaiblir `RG-058`, `RG-059`, `RG-060`, `RG-061`, `RG-068`,
    `RG-078`, `RG-082`, `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087` ou
    `RG-088`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: le catalogue ne contient pas d'archetype dedie a une
  evolution UX/conversion page-scoped; cette story active runtime, baseline,
  ownership, allowlist exacte, reintroduction guard et preuves persistantes.
- Additional validation rules:
  - La preuve mobile `390x844` doit mesurer le haut du mock produit et le debut
    de `#social-proof` avant/apres.
  - Le CTA primaire hero doit rester visible dans le premier viewport mobile.
  - Les preuves hero compactes doivent venir d'une source landing existante ou
    d'une cle de traduction landing clairement owned.
  - Les filtres conserves doivent avoir un fichier, selecteur, declaration,
    raison et condition de sortie.
  - Le pricing doit conserver `getActivePlans()` comme source unique et les
    liens `/register?plan=PLAN_CODE`.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: densite mobile hero, ordre/format de preuves compactes dans le
    hero, surfaces tokenisees a la place de filtres, presentation mobile des
    cards pricing/FAQ, tests et artefacts.
  - Interdit: changement de route, fond global, plan tarifaire, prix, quotas,
    SEO/head, analytics event names existants, backend ou API.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'objectif impose de supprimer le mock produit,
  changer le plan recommande, modifier les prix/quotas, changer la promesse
  marketing principale ou conserver un `backdrop-filter` sans condition de
  sortie exacte.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les objectifs se prouvent par DOM runtime: positions mobile, CTA visible, liens pricing, analytics et CSS chargee. |
| Baseline Snapshot | yes | L'audit donne une mesure mobile; la story doit comparer before/after pour le hero, les preuves et le pricing. |
| Ownership Routing | yes | Les changements doivent rester dans les owners landing React/CSS existants. |
| Allowlist Exception | yes | `RG-088` exige des exceptions exactes pour tout filtre/motion landing conserve. |
| Contract Shape | no | Aucun contrat API, schema, payload, DTO, client genere ou type public partage n'est modifie. |
| Batch Migration | no | La story reste mono-domaine landing; les sous-sections sont traitees comme surfaces d'une meme page. |
| Reintroduction Guard | yes | Le retour d'un hero mobile trop haut, d'une preuve tardive ou d'un filtre non classe doit etre detecte. |
| Persistent Evidence | yes | Captures, mesures et inventaire des filtres doivent etre conserves dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - rendu local de `/` via `LandingLayout`, `LandingPage`, `HeroSection`,
    `SocialProofSection`, `PricingSection` et `FaqSection`;
  - AST guard dans `frontend/src/tests/design-system-guards.test.ts` pour les
    interdits CSS landing, ownership de fond et exceptions motion/filter;
  - tests Vitest/Testing Library de `LandingPage` pour DOM, liens, presence des
    preuves et analytics;
  - visual smoke ou Playwright local pour mesures `390x844`, `768x1024` et
    `1440x1000`;
  - guard CSS dans `frontend/src/tests/design-system-guards.test.ts` ou test
    landing dedie pour l'inventaire `@keyframes|animation:|filter|backdrop-filter`.
- Secondary evidence:
  - scans `rg` cibles dans `frontend/src/pages/landing` et
    `frontend/src/layouts/LandingLayout.css`;
  - captures markdown before/after dans le dossier story.
- Static scans alone are not sufficient because:
  - la hauteur hero, l'apparition du mock produit et la clarte du pricing
    dependent du viewport, du rendu DOM et de la cascade CSS runtime.
- Runtime validation command:
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/landing-conversion-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/landing-conversion-after.md`
- Required baseline content:
  - captures ou mesures `390x844`, `768x1024`, `1440x1000`;
  - `getBoundingClientRect()` de `.hero-section`, `.hero-visual`,
    `.hero-device`, `.hero-ctas`, `#social-proof`, `#pricing` et `#faq`;
  - inventaire des preuves visibles dans le premier viewport mobile;
  - inventaire `@keyframes|animation:|filter|backdrop-filter`;
  - ordre mobile des plans pricing et liens CTA resultants.
- Expected invariant:
  - le premier viewport mobile montre la promesse, le CTA primaire, une preuve
    forte compacte et le debut du mock produit ou du moins son shell; aucune
    regression de fond global, pricing source, routes ou analytics.
- Allowed differences:
  - densite/espacement mobile hero, ajout d'une preuve compacte hero, retrait
    ou classification exacte de filtres, presentation pricing/FAQ mobile.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Structure hero et preuves compactes | `frontend/src/pages/landing/sections/HeroSection.tsx` | composant duplique, `LandingPage.tsx` gonfle, style inline |
| Styles hero et densite mobile | `frontend/src/pages/landing/LandingPage.css` | `frontend/src/App.css`, layouts globaux, CSS de section voisine |
| Preuves fortes completes | `frontend/src/pages/landing/sections/SocialProofSection.tsx` / `.css` | duplication complete dans hero |
| Navigation landing et filtres navbar | `frontend/src/pages/landing/sections/LandingNavbar.css` | `App.css`, exception wildcard |
| Testimonials landing et filtres | `frontend/src/pages/landing/sections/TestimonialsSection.css` | styles globaux ou suppression non prouvee de contenu |
| Pricing mobile et CTA plan | `frontend/src/pages/landing/sections/PricingSection.tsx` / `.css` | copie locale de `pricingConfig`, ordre source duplique |
| FAQ et CTA final | `frontend/src/pages/landing/sections/FaqSection.tsx` / `.css` | nouvelle section finale concurrente |
| Tests landing | `frontend/src/tests/LandingPage.test.tsx`, `visual-smoke.test.tsx`, `design-system-guards.test.ts` | test manuel seul |

Rules:

- Les nouvelles variables CSS doivent reutiliser les tokens/roles `--landing-*`
  existants avant d'en creer de nouvelles.
- Toute nouvelle variable `--landing-*` doit avoir un owner local et une raison
  dans l'artefact after.
- Les changements TSX restent presentational; aucune logique metier tarifaire
  ne doit migrer dans les composants UI.

## 4e. Allowlist / Exception Register

Path prefix for CSS rows:
`frontend/src/pages/landing/sections/`

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `LandingNavbar.css` | `.landing-navbar__shell`: `backdrop-filter: blur(14px)` | Navbar sticky lisible. | Delete or keep with after proof plus exact guard row. |
| `LandingNavbar.css` | `.landing-navbar__lang`: `backdrop-filter: blur(18px) saturate(135%)` | Control language chrome. | Delete in this story. |
| `LandingNavbar.css` | `.landing-navbar__lang-dropdown`: `backdrop-filter: blur(22px) saturate(145%)` | Short overlay. | Delete or keep with exact guard row. |
| `LandingNavbar.css` | `.landing-navbar__mobile-menu`: `backdrop-filter: blur(6px)` | Mobile modal separation. | Keep only with menu screenshot plus exact guard row. |
| `SocialProofSection.css` | `.social-proof__container`: `backdrop-filter: blur(18px)` | Late surface visual debt. | Delete in this story. |
| `TestimonialsSection.css` | `.testimonial-card`: `backdrop-filter: blur(18px) saturate(140%)` | Late card visual debt. | Delete in this story. |
| `TestimonialsSection.css` | `.testimonial-card`: `-webkit-backdrop-filter: blur(18px) saturate(140%)` | Prefixed pair. | Delete with the standard declaration. |
| `TestimonialsSection.css` | reduced motion: `animation: none !important` | Accessibility protection. | Permanent accessibility exception. |

Rules:

- No wildcard exceptions.
- No folder-wide exception.
- No new `backdrop-filter`, `filter`, `animation:` or `@keyframes` outside this
  table without updating the guard and l'artefact after.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO, client genere ou type
  public partage n'est modifie; les URL CTA existantes restent sous
  `/register` et `/register?plan=PLAN_CODE`.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la story applique une evolution coherente a une seule page landing,
  sans migration multi-domaines ou lots de consommateurs.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline conversion landing | `landing-conversion-before.md` | Mesures hero, preuves, pricing mobile et inventaire filtres. |
| Preuve after conversion landing | `landing-conversion-after.md` | Captures, mesures, scans, exceptions et differences autorisees. |

## 4i. Reintroduction Guard

- Guard target:
  - `.hero-device` commence a `y >= 844px` sur viewport mobile `390x844`;
  - CTA primaire hero absent du premier viewport mobile `390x844`;
  - preuve forte compacte absente du premier viewport mobile `390x844`;
  - nouveaux filtres/motion landing non classes;
  - pricing mobile qui casse les liens `/register?plan=PLAN_CODE` ou la
    source unique `getActivePlans()`;
  - correction via `App.css`, fond global ou style inline.
- Forbidden examples:
  - `app-bg--landing`;
  - `style=` dans `frontend/src/pages/landing` ou `frontend/src/layouts`;
  - copie locale d'un tableau de plans dans `PricingSection.tsx`;
  - nouvel `analytics` event remplaçant `pricing_plan_select`;
  - nouvelle declaration `backdrop-filter` non presente dans l'exception
    register;
  - hero mobile valide seulement par texte visible sans debut de mock produit.
- Guard command/test:
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`
  - `cd frontend; npm run lint`
  - `rg -n "app-bg--landing|style=" frontend/src/pages/landing frontend/src/layouts`
  - `rg -n "@keyframes|animation:|backdrop-filter|filter:" frontend/src/pages/landing frontend/src/layouts/LandingLayout.css`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: audit utilisateur du 2026-05-11, section "Plan de mise en
  oeuvre" pour l'evolution landing mobile/conversion.
- Closure proof required: artefacts before/after, tests LandingPage,
  visual-smoke, design-system, scans filtres/styles inline, capture mobile
  pricing et verification liens CTA.
- Known residual in-domain work: none
- Deferred non-domain concerns: mesures business reelles apres livraison
  (`hero_cta_click`, scroll pricing, `pricing_plan_select`) hors implementation
  technique.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/pages/landing/sections/HeroSection.tsx` - le hero
  affiche deja micro-reassurances et mock produit, mais les preuves fortes
  Swiss Ephemeris/RGPD/disponibilite vivent plus bas.
- Evidence 2: `frontend/src/pages/landing/sections/SocialProofSection.tsx` -
  les contenus `t.socialProof.badges.*` et `t.socialProof.proofs.*` sont la
  source existante des preuves fortes.
- Evidence 3: `frontend/src/pages/landing/LandingPage.css` - le hero mobile est
  deja compactifie par `CS-146`, mais l'audit demande encore que le mock ou son
  debut arrive dans le premier viewport `390x844`.
- Evidence 4: `frontend/src/pages/landing/sections/PricingSection.tsx` -
  `getActivePlans()` est la source unique des plans, les CTA pointent vers
  `/register?plan=${plan.planCode}` et `pricing_plan_select` est emis au clic.
- Evidence 5: `frontend/src/pages/landing/sections/PricingSection.css` - le
  plan recommande passe en premier sur mobile via `order: -1`.
- Evidence 6: scan `rg -n "@keyframes|animation:|backdrop-filter|filter:" frontend/src/pages/landing frontend/src/layouts/LandingLayout.css` -
  des `backdrop-filter` actifs restent dans `LandingNavbar.css`,
  `SocialProofSection.css` et `TestimonialsSection.css`.
- Evidence 7: `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/00-story.md` -
  `RG-088` encadre toute croissance motion/filter landing par exceptions
  exactes.
- Evidence 8: `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/00-story.md` -
  le responsive/a11y critique landing est deja corrige; cette story ne doit pas
  regressser ces contrats.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-058` a `RG-061`, `RG-068`, `RG-078`, `RG-082` a
  `RG-088` s'appliquent.

## 6. Target State

After implementation:

- Le hero mobile `390x844` montre la promesse, le CTA primaire, une preuve
  forte compacte et le debut du mock produit ou de son shell.
- Les preuves Swiss Ephemeris/RGPD/sans CB ou disponibilite sont visibles plus
  tot sans dupliquer toute la section social proof.
- Les `backdrop-filter` landing non essentiels sont retires; ceux conserves
  sont exacts, justifies, gardes et documentes.
- Le pricing mobile reste clair: le plan recommande peut rester en premier,
  mais l'entree gratuite reste evidente et les CTA `/register?plan=PLAN_CODE`
  restent corrects.
- Le CTA final/FAQ reste coherente avec l'entree gratuite et sans style inline.
- Les artefacts before/after et tests cibles prouvent la correction.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-058` - les surfaces landing ne doivent pas reintroduire des literals
    visuels/typographiques hors tokens ou roles documentes.
  - `RG-059` - les corrections ne doivent pas polluer `App.css`.
  - `RG-060` - aucun vocabulaire legacy/compatibility/fallback non classe ne
    doit revenir dans les commentaires CSS actifs.
  - `RG-061` - les valeurs visuelles actives doivent rester tokenisees et hors
    declarations brutes non classees.
  - `RG-068` - `LandingLayout` reste l'owner public landing sous `RootLayout`.
  - `RG-078` - `App.css` reste size-bounded et ne devient pas owner de fixes
    landing.
  - `RG-082` - aucune police decorative directe ne doit revenir.
  - `RG-083` - les surfaces landing doivent rester lisibles en dark mode sans
    correction inline ou `App.css`.
  - `RG-084` - aucun fond page-level landing concurrent ne doit etre cree.
  - `RG-085` - le fond dark astral global reste canonique.
  - `RG-086` - `app-bg--landing` ne doit pas revenir.
  - `RG-087` - la landing longue ne doit pas modifier le fond viewport-fixed.
  - `RG-088` - motion/filter landing doit rester sans croissance non classee.
- Non-applicable invariants:
  - `RG-001` a `RG-057`, `RG-062` a `RG-067` et `RG-069` a `RG-077` - domaines
    backend, API, pages hors landing ou composants hors surface touchee par
    cette story.
- Required regression evidence:
  - tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles`,
    `page-architecture`;
  - captures/mesures before/after mobile, tablette et desktop;
  - scans `style=`, `app-bg--landing`, fonts decoratives et
    `@keyframes|animation:|backdrop-filter|filter:`;
  - verification des liens `/register?plan=PLAN_CODE` et de `pricing_plan_select`.
- Allowed differences:
  - densite hero mobile, preuve compacte hero, surfaces tokenisees remplaçant
    certains filtres, presentation mobile pricing/FAQ; aucune difference de
    route, fond global, SEO/head, backend, plans ou event names existants.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `.hero-device` commence avant `y=844px` sur `390x844`. | Evidence profile: `baseline_before_after_diff`; `npm run test -- visual-smoke LandingPage`. |
| AC2 | Le CTA primaire hero est visible sur `390x844`. | Evidence profile: `baseline_before_after_diff`; `npm run test -- visual-smoke LandingPage`. |
| AC3 | Une preuve forte compacte est visible sur `390x844`. | Evidence profile: `baseline_before_after_diff`; `npm run test -- LandingPage`. |
| AC4 | La preuve hero utilise une source landing owned. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- LandingPage`. |
| AC5 | Les filtres landing restants ont une decision exacte. | Evidence profile: `allowlist_register_validated`; `npm run test -- design-system`. |
| AC6 | Le plan Free reste visible dans le pricing mobile. | Evidence profile: `reintroduction_guard`; `npm run test -- LandingPage`. |
| AC7 | Les liens plan gardent les codes `free` `basic` `premium`. | Evidence profile: `reintroduction_guard`; `npm run test -- LandingPage`. |
| AC8 | Le tracking pricing garde `pricing_plan_select`. | Evidence profile: `reintroduction_guard`; `npm run test -- LandingPage`. |
| AC9 | Le CTA final FAQ garde la cible `/register`. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- LandingPage`. |
| AC10 | Aucun guard landing/fond/design-system ne regresse. | `npm run lint`; `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline conversion landing (AC: AC1, AC2, AC3, AC6, AC7)
  - [x] Subtask 1.1 - Lire les fichiers listes en section 18 et les stories
    `CS-145` / `CS-146`.
  - [x] Subtask 1.2 - Creer `landing-conversion-before.md` avec mesures
    viewport, preuves visibles, inventaire filtres et ordre pricing mobile.

- [x] Task 2 - Compactifier le hero mobile et avancer le signal produit (AC: AC1, AC2, AC3, AC4)
  - [x] Subtask 2.1 - Ajuster uniquement `HeroSection.tsx` et
    `LandingPage.css` pour reduire gaps/hauteurs mobile sans supprimer le mock.
  - [x] Subtask 2.2 - Ajouter une preuve compacte pres des CTA en reutilisant
    les traductions existantes ou une cle landing owned.
  - [x] Subtask 2.3 - Tester la presence DOM de la preuve et capturer la mesure
    `390x844` after.

- [x] Task 3 - Reduire ou classifier les filtres landing (AC: AC5, AC10)
  - [x] Subtask 3.1 - Remplacer les filtres non essentiels par surfaces
    tokenisees dans `LandingNavbar.css`, `SocialProofSection.css` et
    `TestimonialsSection.css`.
  - [x] Subtask 3.2 - Pour chaque filtre conserve, documenter fichier,
    selecteur, declaration, raison et condition de sortie dans l'artefact
    after et le guard.
  - [x] Subtask 3.3 - Verifier que le guard `RG-088` reste exact et sans
    wildcard.

- [x] Task 4 - Clarifier pricing et FAQ mobile (AC: AC6, AC7, AC8, AC9)
  - [x] Subtask 4.1 - Garder `getActivePlans()` comme source unique et prouver
    que le plan Free reste visible sur mobile.
  - [x] Subtask 4.2 - Limiter les effets hover pricing aux contextes desktop
    pour les cards modifiees.
  - [x] Subtask 4.3 - Verifier les liens `/register?plan=free`,
    `/register?plan=basic`, `/register?plan=premium` et l'event
    `pricing_plan_select`.
  - [x] Subtask 4.4 - Verifier que le CTA final FAQ pointe toujours vers
    `/register`.

- [x] Task 5 - Finaliser les preuves et validations (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [x] Subtask 5.1 - Creer `landing-conversion-after.md` avec captures,
    mesures, scans, tests executes et differences autorisees.
  - [x] Subtask 5.2 - Executer lint, tests cibles et scans interdits.
  - [x] Subtask 5.3 - Documenter toute commande non executee avec raison et
    risque.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `HeroSection.tsx` comme owner unique du premier ecran hero.
  - `SocialProofSection.tsx` comme source de preuve forte complete; le hero ne
    peut qu'en reprendre un signal compact.
  - `getActivePlans()` et `formatPrice()` dans `PricingSection.tsx`.
  - tokens/roles `--landing-*`, `--premium-*`, `--font-*` existants dans les CSS
    landing.
  - tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles` et
    `page-architecture`.
- Do not recreate:
  - tableau local de plans pricing;
  - deuxieme section social proof dans le hero;
  - fond ou layout landing concurrent;
  - parser CSS externe;
  - analytics event remplaçant les events existants.
- Shared abstraction allowed only if:
  - elle remplace une duplication prouvee entre surfaces landing, reste dans
    `frontend/src/pages/landing`, et dispose d'un test cible.

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
- `style=` dans `frontend/src/pages/landing` ou `frontend/src/layouts`
- modifications opportunistes dans `frontend/src/App.css`
- copie de `getActivePlans()` ou de `pricingConfig`
- nouvel `@keyframes`, `animation:`, `filter` ou `backdrop-filter` non classe
- wildcard `*`, `**` ou folder-wide dans une allowlist motion/filter
- `PASS with limitation`, `TODO`, `fallback`, `compatibility`, `legacy` comme
  justification d'un residuel actif

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Hero et preuves premier ecran | `HeroSection.tsx`, `LandingPage.css` | `App.css`, section dupliquee, inline styles |
| Preuves fortes completes | `frontend/src/pages/landing/sections/SocialProofSection.tsx` / `.css` | duplication complete dans hero |
| Pricing plans et CTA | `PricingSection.tsx`, `pricingConfig.ts` en lecture seule | copie locale des plans, backend, traduction hors landing non owned |
| FAQ et CTA final | `frontend/src/pages/landing/sections/FaqSection.tsx` / `.css` | nouvelle route ou CTA concurrent |
| Complexite filtre/motion landing | CSS landing owners + `frontend/src/tests/design-system-guards.test.ts` | allowlist wildcard, audit manuel seul |
| Preuves de livraison | `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/**` | sortie console non persistante |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or
  generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/landing/LandingPage.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/HeroSection.tsx`
- `frontend/src/pages/landing/sections/SocialProofSection.tsx`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/pages/landing/sections/PricingSection.tsx`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/FaqSection.tsx`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/config/pricingConfig.ts`
- `frontend/src/tests/LandingPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/AppBgStyles.test.ts`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/00-story.md`
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/00-story.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/landing/sections/HeroSection.tsx` - ajouter preuve
  compacte et ajuster eventuel ordre du contenu hero.
- `frontend/src/pages/landing/LandingPage.css` - densite mobile hero et
  contraintes visuelles du mock.
- `frontend/src/pages/landing/sections/SocialProofSection.css` - remplacer ou
  classifier le filtre de la surface preuve.
- `frontend/src/pages/landing/sections/LandingNavbar.css` - reduire ou
  classifier les filtres navbar/langue/menu.
- `frontend/src/pages/landing/sections/TestimonialsSection.css` - reduire ou
  classifier les filtres testimonials.
- `frontend/src/pages/landing/sections/PricingSection.tsx` - preuve ou rendu
  owned du plan Free sans changer la source des plans.
- `frontend/src/pages/landing/sections/PricingSection.css` - presentation
  mobile et hover desktop quand l'artefact before prouve un conflit mobile.
- `frontend/src/pages/landing/sections/FaqSection.tsx` - verification ou rendu
  owned du CTA final.
- `frontend/src/pages/landing/sections/FaqSection.css` - ajustements mobiles
  tokenises quand la capture before prouve une ambiguite CTA.
- `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/landing-conversion-before.md` - baseline.
- `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/landing-conversion-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/LandingPage.test.tsx` - assertions preuves hero, liens
  pricing et analytics.
- `frontend/src/tests/visual-smoke.test.tsx` - mesures responsive du premier
  viewport landing.
- `frontend/src/tests/design-system-guards.test.ts` - exceptions exactes
  motion/filter landing.

Files not expected to change:

- `frontend/src/App.css` - forbidden destination.
- `frontend/src/layouts/RootLayout.tsx` - fond global hors scope.
- `frontend/src/pages/landing/LandingHead.tsx` - SEO/head hors scope.
- `frontend/src/config/pricingConfig.ts` - source lue mais non modifiee sauf
  decision utilisateur explicite.
- `backend/**` - aucun changement backend attendu.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- New runtime dependencies: forbidden.
- New dev dependencies: forbidden.
- Python commands: if a story validation script is run, activate `.venv` first:
  `.\.venv\Scripts\Activate.ps1`.
- Frontend commands: run from `frontend/` with npm scripts already present.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run lint
npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture
rg -n "app-bg--landing|style=" src/pages/landing src/layouts
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css
rg -n "Cormorant|Petit Formal|Brush Script|font-family:\s*\"" src -g "*.css" -g "*.scss"
```

Required runtime/manual evidence:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Then capture or script checks for:

- viewport `390x844`: CTA primary visible, preuve compacte visible, debut mock
  produit ou shell visible;
- viewport `768x1024` and `1440x1000`: no overflow horizontal and no regression
  hero/pricing;
- pricing mobile: Free visible, Basic recommended visible, plan CTA hrefs
  `/register?plan=free`, `/register?plan=basic`, `/register?plan=premium`;
- CSS inventory: every remaining `backdrop-filter`, `filter` or `animation:`
  has exact documented exception.

Story contract validation after drafting or editing this story:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-147-optimiser-conversion-mobile-landing/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-147-optimiser-conversion-mobile-landing/00-story.md
```

## 22. Regression Risks

- Risk: compacter le hero masque la promesse ou degrade la lisibilite mobile.
  - Guardrail: AC1 combine CTA, preuve forte et debut mock avec capture
    `390x844`.
- Risk: preuve forte dupliquee et incoherente avec `SocialProofSection`.
  - Guardrail: AC2 impose reuse de contenus landing existants ou cle owned.
- Risk: reduction des filtres affadit la hierarchie visuelle.
  - Guardrail: before/after desktop/mobile et exception exacte possible avec
    condition de sortie.
- Risk: Free devient moins visible en mettant Basic recommande en premier.
  - Guardrail: AC4 impose evidence Free et liens plan.
- Risk: correction opportuniste via `App.css`, fond global ou style inline.
  - Guardrail: scans et invariants `RG-059`, `RG-078`, `RG-084` a `RG-087`.

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
- Commencer par produire l'artefact before avec les mesures runtime.
- Modifier par petits deltas: hero/preuve, filtres, pricing/FAQ, tests, preuves
  after.
- Ne pas changer les plans, prix, quotas, event names, routes, SEO/head ou fond
  global.
- Respecter les instructions projet: aucun style inline; commentaires globaux
  et docstrings en francais pour tout fichier applicatif nouveau ou
  significativement modifie.

## 24. References

- Audit utilisateur du 2026-05-11 - diagnostic et plan d'action landing.
- `frontend/src/pages/landing/sections/HeroSection.tsx` - owner hero.
- `frontend/src/pages/landing/LandingPage.css` - owner CSS hero.
- `frontend/src/pages/landing/sections/SocialProofSection.tsx` - preuves
  fortes existantes.
- `frontend/src/pages/landing/sections/PricingSection.tsx` - source unique
  `getActivePlans()` et analytics pricing.
- `frontend/src/pages/landing/sections/FaqSection.tsx` - CTA final.
- `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/00-story.md` - guard motion/filter landing.
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/00-story.md` - baseline responsive/a11y recent.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
