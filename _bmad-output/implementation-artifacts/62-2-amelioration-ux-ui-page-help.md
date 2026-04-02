# Story 62.2 : Amélioration UX/UI de la page `/help`

Status: ready-for-dev

---

## Story

En tant qu'utilisateur authentifié,
je veux que la page `/help` soit restructurée avec une hiérarchie visuelle forte, un hero d'orientation immédiat, des raccourcis vers les fonctionnalités clés, un bloc comparatif des quotas/tokens, une carte abonnement dédiée, un flux support guidé et une liste de tickets plus scannable,
afin de comprendre instantanément l'utilité de la page, trouver rapidement la bonne action, ouvrir un ticket sans friction et suivre facilement les réponses du support.

---

## Résultat de vérification

La story a été relue contre l'implémentation actuelle de la page `/help` et de ses composants.

Corrections apportées dans cette version :

- Scope clarifié : **frontend uniquement**, aucun changement backend attendu pour cette story.
- Références corrigées vers les bons fichiers réels (`frontend/src/api/help.ts`, composants de `frontend/src/pages/support/`).
- Suppression des ambiguïtés héritées de la Story 62.1 (`/support`, navigation ops, `api/support.ts`) qui ne font pas partie de 62.2.
- Critères d'acceptation rendus plus testables et alignés avec les composants existants.
- Dépendances explicites vis-à-vis de la Story 62.1 et du contrat API déjà en place.

---

## Contexte

### Dépendance

La Story 62.2 dépend de la Story 62.1, déjà livrée, qui a introduit :

- la route frontend `/help`
- l'API frontend `frontend/src/api/help.ts`
- les composants `SupportCategorySelect`, `SupportTicketForm`, `SupportTicketList`
- le fichier i18n `frontend/src/i18n/support.ts`
- les endpoints backend `/v1/help/categories` et `/v1/help/tickets`

Cette story est une **amélioration UX/UI** de l'existant. Elle ne doit pas réouvrir le scope backend sauf anomalie bloquante découverte pendant l'implémentation.

### Ce qui existe déjà et doit être réutilisé

**Composants UI**

- `Button` (`frontend/src/components/ui/Button`)
- `Field` et les classes `field__input`, `field__input--textarea`, `field__error`
- `Skeleton` / `SkeletonGroup`
- `EmptyState`
- `ErrorState`
- `PageLayout`

**Patterns visuels à réutiliser**

- [`Settings.css`](/c:/dev/horoscope_front/frontend/src/pages/settings/Settings.css) : `.settings-card`, `.settings-bg-halo`, `.settings-noise`, `.settings-divider`, `.settings-section-title`
- cartes abonnement de type `subscription-plan-card`
- variables de thème déjà présentes dans l'application (`--primary`, `--text-1`, `--text-2`, `--glass`, `--glass-border`, `--glass-strong`, `--success`, `--danger`)

**Fichiers frontend cibles**

- [`HelpPage.tsx`](/c:/dev/horoscope_front/frontend/src/pages/HelpPage.tsx)
- [`HelpPage.css`](/c:/dev/horoscope_front/frontend/src/pages/HelpPage.css)
- [`support.ts`](/c:/dev/horoscope_front/frontend/src/i18n/support.ts)
- [`SupportCategorySelect.tsx`](/c:/dev/horoscope_front/frontend/src/pages/support/SupportCategorySelect.tsx)
- [`SupportTicketForm.tsx`](/c:/dev/horoscope_front/frontend/src/pages/support/SupportTicketForm.tsx)
- [`SupportTicketList.tsx`](/c:/dev/horoscope_front/frontend/src/pages/support/SupportTicketList.tsx)
- [`help.ts`](/c:/dev/horoscope_front/frontend/src/api/help.ts) uniquement si un type frontend manque déjà

### Hors scope

- backend FastAPI
- routes backend `/v1/help/*`
- navigation globale hors liens déjà existants vers `/help`
- panneau ops `/support`
- changement de contrat API hors correction mineure de type frontend

---

## Décisions de design à respecter

- Pas de Tailwind.
- Aucun style inline.
- Réutiliser au maximum les patterns visuels de la page settings au lieu de recréer un sous-système visuel.
- Les navigations primaires se font avec `<Link>` de `react-router-dom`.
- La route abonnement cible est `/settings/subscription`.
- Les traductions passent par `frontend/src/i18n/support.ts` en `fr`, `en`, `es`.
- Le hero doit pointer vers la zone support avec un ancrage `#help-support-section`.
- Les hover cards utilisent `translateY(-2px)` et jamais `scale(...)`.
- Ne pas utiliser `transition: all`.

---

## Acceptance Criteria

### AC1 — Hero d'orientation premium

La page `/help` s'ouvre sur un hero premium en tête de page contenant :

- un titre `help.hero.title`
- un sous-titre `help.hero.subtitle`
- un CTA primaire `help.hero.primaryCta` qui scroll vers `#help-support-section`
- un CTA secondaire `help.hero.secondaryCta` qui pointe vers `/settings/subscription` avec `<Link>`
- trois micro-étapes d'orientation `help.hero.steps[0..2]`

Contraintes :

- halo et texture inspirés de `Settings.css`
- hiérarchie visuelle forte
- CTA empilés en mobile et largeur pleine

### AC2 — Raccourcis vers les fonctionnalités clés

La section "Comment fonctionne l'application" est remplacée par une grille de 4 raccourcis, chacun avec :

- icône
- titre
- bénéfice utilisateur
- libellé d'action
- navigation via `<Link>`

Routes attendues :

- `/today`
- `/chat`
- `/natal-chart`
- `/consultations`

Clés i18n :

- `help.shortcuts.dashboard.*`
- `help.shortcuts.chat.*`
- `help.shortcuts.natal.*`
- `help.shortcuts.consultations.*`

### AC3 — Bloc tokens/quota comparatif

Le tableau mono-colonne actuel est supprimé et remplacé par :

- un court texte d'introduction `help.tokens.intro`
- trois cartes comparatives `free`, `basic`, `premium`
- pour chaque carte : nom, logique de quota, 2 à 4 points clés, tagline

Clés i18n :

- `help.tokens.plans.free.*`
- `help.tokens.plans.basic.*`
- `help.tokens.plans.premium.*`

Contraintes :

- 3 colonnes en desktop
- 1 colonne sur mobile
- réutilisation du pattern de cartes premium

### AC4 — Carte abonnement/facturation dédiée

Le simple CTA abonnement actuel est remplacé par une vraie carte d'assistance contenant :

- une icône
- un titre `help.billing.title`
- quatre points d'aide `help.billing.features[]`
- un CTA `<Link to="/settings/subscription">`

La carte doit réutiliser le style `.settings-card` ou un dérivé cohérent avec ce pattern.

### AC5 — Sélection de catégorie enrichie

Dans `SupportCategorySelect.tsx` :

- chaque carte catégorie affiche icône, label, description courte
- si `cat.description` est `null`, la description utilise le fallback i18n `help.categoryDescriptions[code]`
- la carte sélectionnée expose un état actif visible
- hover et focus sont alignés avec les règles d'accessibilité ci-dessous

Important :

- `HelpCategory.description` existe déjà dans [`help.ts`](/c:/dev/horoscope_front/frontend/src/api/help.ts) ; ne pas recréer un contrat parallèle

### AC6 — Formulaire guidé

Dans `SupportTicketForm.tsx` :

- la catégorie sélectionnée est rappelée dans un chip visuel identifiable
- le bouton "Modifier" reste disponible sans écraser l'information de contexte
- le placeholder description devient guidant via `help.form.description.placeholder`
- un texte d'aide sous le champ description utilise `help.form.description.hint`
- après succès, un message inline visible s'affiche dans `HelpPage.tsx` via `help.form.successMessage`

Le succès ne doit pas être invisible ou uniquement déduit de la disparition du formulaire.

### AC7 — Liste des tickets restructurée

Dans `SupportTicketList.tsx` :

- le badge statut est en `inline-flex`
- l'en-tête ticket est restructuré :
  - ligne 1 : sujet + badge statut
  - ligne 2 : date + catégorie si disponible
- le bloc de réponse support utilise un fond plus lisible (`var(--glass-strong)` ou équivalent cohérent)
- l'état vide propose un CTA renvoyant vers `#help-support-section`
- le texte vide utilise `help.tickets.emptyDescription`

### AC8 — Accessibilité et cohérence d'interaction

Les règles suivantes sont appliquées :

- `.category-card:hover` utilise `translateY(-2px)` et pas `scale(...)`
- aucune règle `transition: all`
- les focus visibles existent pour les cartes interactives
- les liens CTA principaux utilisent `<Link>` au lieu de `navigate(...)`
- `.ticket-badge` est en `display: inline-flex`
- les textes i18n utilisent `…` au lieu de `...` lorsque pertinent

### AC9 — Responsive mobile

En mobile :

- hero sur une colonne
- CTA hero pleine largeur
- grille tokens en une colonne
- grille raccourcis sur 1 ou 2 colonnes maximum selon largeur disponible
- cartes catégories avec surface tactile suffisante (`min-height` cohérente)

### AC10 — i18n complète

Le fichier [`support.ts`](/c:/dev/horoscope_front/frontend/src/i18n/support.ts) contient toutes les nouvelles clés en `fr`, `en`, `es` :

- `help.hero.*`
- `help.shortcuts.*`
- `help.tokens.plans.*`
- `help.billing.*`
- `help.form.description.hint`
- `help.form.successMessage`
- `help.categoryDescriptions.*`
- `help.tickets.emptyDescription`

---

## Tasks / Subtasks

- [x] **T1 — Étendre l'i18n support** (AC10)
  - [x] Ajouter les clés hero
  - [x] Ajouter les clés shortcuts
  - [x] Ajouter les clés tokens comparatives
  - [x] Ajouter les clés billing
  - [x] Ajouter les fallbacks `help.categoryDescriptions.*`
  - [x] Ajouter `help.form.description.hint`
  - [x] Ajouter `help.form.successMessage`
  - [x] Ajouter `help.tickets.emptyDescription`
  - [x] Remplacer les ellipses ASCII par `…` lorsque pertinent

- [x] **T2 — Refonte CSS dans `HelpPage.css`** (AC1, AC2, AC3, AC4, AC7, AC8, AC9)
  - [x] Ajouter le hero premium
  - [x] Ajouter la grille de raccourcis
  - [x] Ajouter la variante des cartes plans
  - [x] Corriger `category-card` hover et transitions
  - [x] Corriger `.ticket-badge`
  - [x] Corriger `.ticket-response`
  - [x] Ajouter styles de focus visibles
  - [x] Ajouter styles responsive

- [x] **T3 — Restructurer `HelpPage.tsx`** (AC1, AC2, AC3, AC4, AC6)
  - [x] Ajouter le hero
  - [x] Ajouter la section raccourcis
  - [x] Remplacer le bloc tokens
  - [x] Remplacer le bloc abonnement actuel par une carte dédiée
  - [x] Ajouter `id="help-support-section"`
  - [x] Afficher un message de succès inline après soumission
  - [x] Remplacer les navigations primaires ad hoc par des `<Link>`

- [x] **T4 — Améliorer `SupportCategorySelect.tsx`** (AC5, AC8)
  - [x] Afficher les descriptions
  - [x] Ajouter un état actif visuel
  - [x] Réutiliser `cat.description` avec fallback i18n

- [x] **T5 — Améliorer `SupportTicketForm.tsx`** (AC6)
  - [x] Ajouter le chip catégorie
  - [x] Ajouter le texte d'aide description
  - [x] Vérifier le message succès remonté au parent

- [x] **T6 — Améliorer `SupportTicketList.tsx`** (AC7)
  - [x] Restructurer le header ticket
  - [x] Ajouter le CTA de l'état vide
  - [x] Rendre la réponse support plus lisible

- [x] **T7 — Mettre à jour les tests frontend** (AC1 à AC10)
  - [x] Mettre à jour `HelpPage.test.tsx`
  - [x] Ajouter ou ajuster les assertions sur hero, CTA, succès inline, descriptions catégories, état vide tickets

---

## Dev Notes

### Points de vigilance

- Ne pas modifier `frontend/src/api/support.ts` : ce fichier concerne les usages support/ops, pas le help center utilisateur.
- Ne pas rouvrir `frontend/src/app/routes.tsx` sauf si une anomalie bloque réellement la page `/help`. La route existe déjà depuis 62.1.
- Ne pas introduire de nouveaux composants génériques si les primitives actuelles couvrent le besoin.
- Avant de créer de nouvelles variables CSS, vérifier `frontend/src/index.css`, `frontend/src/styles/theme.css` et `Settings.css`.

### Structure cible de la page

```tsx
<PageLayout>
  <div className="help-page">
    <div className="help-bg-halo" />
    <div className="help-noise" />

    <section className="help-hero">...</section>
    <section className="help-section help-shortcuts">...</section>
    <section className="help-section help-tokens">...</section>
    <section className="help-section settings-card help-billing">...</section>

    <section id="help-support-section" className="help-section">
      {!selectedCategory ? <SupportCategorySelect /> : <SupportTicketForm />}
      {ticketSuccess && <div className="help-ticket-success">...</div>}
    </section>

    <section className="help-section">
      <SupportTicketList />
    </section>
  </div>
</PageLayout>
```

### Références utiles

- [`HelpPage.tsx`](/c:/dev/horoscope_front/frontend/src/pages/HelpPage.tsx)
- [`HelpPage.css`](/c:/dev/horoscope_front/frontend/src/pages/HelpPage.css)
- [`support.ts`](/c:/dev/horoscope_front/frontend/src/i18n/support.ts)
- [`SupportCategorySelect.tsx`](/c:/dev/horoscope_front/frontend/src/pages/support/SupportCategorySelect.tsx)
- [`SupportTicketForm.tsx`](/c:/dev/horoscope_front/frontend/src/pages/support/SupportTicketForm.tsx)
- [`SupportTicketList.tsx`](/c:/dev/horoscope_front/frontend/src/pages/support/SupportTicketList.tsx)
- [`help.ts`](/c:/dev/horoscope_front/frontend/src/api/help.ts)
- [`Settings.css`](/c:/dev/horoscope_front/frontend/src/pages/settings/Settings.css)
- [`62-1-page-support-et-help-center-utilisateur.md`](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/62-1-page-support-et-help-center-utilisateur.md)

---

## Dev Agent Record

### Agent Model Used

gpt-5

### Implementation Notes

L'amélioration UX/UI de la page `/help` a été réalisée conformément aux spécifications.
- **Hero Premium** : Intégration d'un hero avec halo et texture, CTA vers le support et l'abonnement, et micro-étapes d'orientation.
- **Raccourcis** : Grille de 4 raccourcis vers les fonctionnalités clés (`/today`, `/chat`, `/natal-chart`, `/consultations`) avec icônes et bénéfices.
- **Comparaison de Tokens** : Remplacement du tableau par une grille comparative de 3 plans (Free, Basic, Premium) avec caractéristiques détaillées.
- **Carte Facturation** : Ajout d'une carte dédiée au style `Settings.css` pour la gestion de l'abonnement.
- **Support UI** :
  - Sélection de catégorie enrichie avec descriptions et état actif.
  - Formulaire avec chip de rappel de catégorie et texte d'aide.
  - Message de succès inline visible.
  - Liste de tickets restructurée (header sur deux lignes) et état vide avec CTA.
- **Tests** : Mise à jour exhaustive de `HelpPage.test.tsx` pour couvrir toutes les nouvelles AC.

### File List

- `frontend/src/pages/HelpPage.tsx`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/i18n/support.ts`
- `frontend/src/pages/support/SupportCategorySelect.tsx`
- `frontend/src/pages/support/SupportTicketForm.tsx`
- `frontend/src/pages/support/SupportTicketList.tsx`
- `frontend/src/tests/HelpPage.test.tsx`
- `frontend/src/components/ui/Button/Button.tsx`

### Review Notes

- Story relue et réalignée sur l'implémentation réelle de `/help`.
- Références de scope et de fichiers corrigées.
- ACs clarifiés pour éviter les contradictions pendant le dev.

---

## Status

Status: done

