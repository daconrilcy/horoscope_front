# Story 63.1: Hero Section — au-dessus de la ligne de flottaison

Status: done

## Mise en oeuvre réelle

- Le hero final conserve la route canonique `/`, mais a été réorienté vers une composition "message + preuve produit" plus forte.
- Le CTA secondaire implémenté est `Découvrir comment ça marche` et scrolle vers `#how-it-works`.
- Le visuel n'est pas un screenshot brut mais une composition produit crédible : carte horoscope du jour, conversation IA et encart "moment clé".
- Le hero est compacté sur mobile pour éviter qu'un titre trop long monopolise le premier écran.

## Story

As a visiteur non authentifié arrivant sur la landing page,
I want voir immédiatement la promesse de valeur, une preuve produit et un appel à l'action clair,
so that je comprenne en moins de 5 secondes ce que l'application offre et je sois incité à m'inscrire.

## Acceptance Criteria

### AC1 — Route canonique `/` pour la LandingPage (bloquant)

1. **`/` est la route canonique publique** de la landing page — il n'existe pas de route `/landing` distincte (pour éviter toute ambiguïté SEO et canonical).
2. La résolution de `/` est faite **directement dans `routes.tsx`**, sous `RootLayout` : si l'utilisateur est authentifié → redirect vers `/dashboard` ; si non-authentifié → rendu de la `LandingPage` sur `/` (pas de redirect intermédiaire, pas de `RootRedirect` sur cette route).
3. La `LandingPage` est accessible sans token JWT (aucun `AuthGuard` n'entoure cette route).
4. La page est encapsulée dans un `LandingLayout` sans sidebar, sans AppShell, sans bottom nav.
5. `/landing` ne doit pas exister comme route — si une ancienne URL l'utilise, configurer un redirect 301 vers `/`.

### AC2 — Hero Section complète au-dessus de la ligne de flottaison

5. La section hero est le premier élément visible sans scroll sur desktop (≥ 1024px) et mobile (≤ 768px).
6. Elle contient dans l'ordre :
   - **H1** : proposition de valeur avec le résultat concret + le public cible (ex : "Votre guide astrologique personnel — disponible 24h/24")
   - **Sous-titre** : mécanisme + bénéfice + délai (1–2 lignes, sans jargon)
   - **3 bullet points** bénéfices avec icône ✓ ou étoile
   - **CTA primaire** : bouton "Démarrer gratuitement" → redirige vers `/register`
   - **CTA secondaire** : lien/bouton "Voir un exemple" → scroll vers la section Solution (#how-it-works)
   - **Micro-réassurance** : 3 items inline : "Sans carte bancaire", "Annulation en 1 clic", "Données protégées RGPD"
7. Côté visuel (droite sur desktop, en bas sur mobile) : un screenshot ou mockup validé de l'interface app avec 2–3 mini-légendes. **Si aucun screenshot réel n'est disponible, utiliser un asset statique illustratif validé par le design — jamais un placeholder générique `placeholder.png`**.
8. Le layout desktop utilise 2 colonnes (60% texte / 40% visuel), le layout mobile est une colonne unique (texte puis visuel).
9. **Le conteneur du visuel hero réserve un espace fixe à tous les breakpoints** (dimensions explicites en CSS ou `aspect-ratio`) : aucun chargement du visuel ne doit décaler le texte ou les CTAs (CLS = 0 sur cet élément).

### AC3 — Style premium cohérent avec le design system existant

9. Aucun style inline : tout le CSS est dans `frontend/src/pages/landing/LandingPage.css` ou un fichier section dédié.
10. Les variables CSS utilisées sont les **tokens premium canoniques** (et non les alias génériques insuffisants) :
    - Typographie : `var(--premium-text-strong)`, `var(--premium-text-main)`, `var(--premium-text-meta)`
    - Surfaces glass : `var(--premium-glass-surface-1)` avec `backdrop-filter: blur(18px) saturate(140%)`
    - Bordures : `var(--premium-glass-border)`
    - Rayons : `var(--premium-radius-hero)` (28px), `var(--premium-radius-card)` (24px)
    - Ombres : `var(--premium-shadow-hero)`, `var(--premium-shadow-card)`
    - Accent : `var(--premium-accent-purple)`, `var(--color-primary)`
    - Alias de compatibilité (`var(--primary)`, `var(--glass)`, `var(--text-1)`) acceptés pour les overrides ponctuels uniquement
11. **L'arrière-plan du hero N'EST PAS à réimplémenter** : `RootLayout` inclut déjà `StarfieldBackground` (dark mode) et le gradient `app-bg`. La `LandingPage` hérite de ce fond sans rien ajouter. Si un halo de couleur supplémentaire est souhaité au-dessus du fond, utiliser un `::before` avec `position: fixed; z-index: -1` comme les autres pages.
12. Le max-width de la landing est de **1200px** (plus large que les pages app à 912px, pour une landing pleine largeur) — défini en variable locale CSS dans `.landing-page`.
13. Le bouton CTA primaire réutilise le composant `Button` de `frontend/src/components/ui/Button/Button.tsx` avec `variant="primary"` et `size="lg"`.

### AC4 — i18n

13. Tous les textes (H1, sous-titre, bullets, CTA, micro-réassurance) sont externalisés dans `frontend/src/i18n/landing.ts`.
14. Le fichier i18n expose les clés pour `fr`, `en` et `es`, conformément au système de langues déjà supporté par l'application.
15. Le hook `useTranslation` (ou équivalent existant dans le projet) est utilisé pour récupérer les traductions.

### AC5 — Responsive et accessibilité

16. La page est mobile-first : le hero est lisible et fonctionnel sur 375px de largeur.
17. Le H1 est bien un `<h1>` unique sur la page.
18. Les CTAs ont des `aria-label` explicites et sont utilisables au clavier (focus visible).
19. Le contraste texte/fond respecte WCAG 2.1 AA.
20. Les animations (si présentes dans le hero) respectent `@media (prefers-reduced-motion: reduce)`.

### Definition of Done QA

- [ ] `/` affiche la LandingPage sans être authentifié — pas de redirect vers `/login`
- [ ] `/` avec token auth valide → redirect vers `/dashboard`
- [ ] Le conteneur visuel hero a des dimensions CSS fixes — pas de CLS au chargement
- [ ] Sur 375px : H1, CTA primaire et micro-réassurance visibles sans scroll horizontal
- [ ] CTA "Démarrer gratuitement" focus-visible au clavier
- [ ] H1 unique sur la page (pas de second `h1` dans le layout)
- [ ] Clic "Voir un exemple" → scroll vers `#how-it-works` sans rechargement de page

## Tasks / Subtasks

- [ ] T1 — Route canonique `/` pour LandingPage (AC: 1, 2, 3, 4, 5)
  - [ ] Lire `routes.tsx` en entier : aujourd'hui `/` pointe vers `RootRedirect`
  - [ ] Remplacer ce montage par une route `/` sous `RootLayout` qui rend `LandingLayout` + `LandingPage` pour les non-authentifiés et redirige les authentifiés vers `/dashboard`
  - [ ] Retirer l'usage de `RootRedirect` pour `/`
  - [ ] Supprimer toute route `/landing` si elle existe
  - [ ] Créer `LandingLayout` = wrapper sans `AppShell`, sans sidebar, sans `BottomNav` — **à placer à l'intérieur de `RootLayout`** (pour hériter du fond app-bg et du StarfieldBackground)
- [ ] T2 — Créer le composant `LandingPage` (AC: 5, 6, 7, 8)
  - [ ] Créer `frontend/src/pages/landing/LandingPage.tsx`
  - [ ] Implémenter la structure HTML sémantique du hero (h1, p, ul, buttons)
  - [ ] Intégrer le visuel produit (screenshot réel ou asset statique illustratif validé)
  - [ ] Intégrer les mini-légendes
- [ ] T3 — Styles CSS hero (AC: 9, 10, 11, 12)
  - [ ] Créer `frontend/src/pages/landing/LandingPage.css`
  - [ ] Implémenter layout 2 colonnes desktop / 1 colonne mobile
  - [ ] Réutiliser le fond existant hérité de `RootLayout` sans le recréer
  - [ ] Styles CTA primaire/secondaire, micro-réassurance
- [ ] T4 — i18n (AC: 13, 14, 15)
  - [ ] Créer `frontend/src/i18n/landing.ts` avec clés `fr`, `en`, `es`
  - [ ] Brancher les textes du hero sur les clés i18n
- [ ] T5 — Accessibilité et responsive (AC: 16, 17, 18, 19)
  - [ ] Vérifier H1 unique
  - [ ] Ajouter aria-labels sur les boutons
  - [ ] Tester sur 375px

## Dev Notes

- **Routing actuel** : `frontend/src/app/routes.tsx` déclare aujourd'hui `path: "/"` vers `RootRedirect`, qui renvoie ensuite vers `/login` ou `/dashboard`. Cette story doit supprimer cette redirection intermédiaire pour `/`.
- **StarfieldBackground** : NE PAS l'importer dans LandingPage. Il est déjà rendu dans `RootLayout` (`frontend/src/layouts/RootLayout.tsx`). La landing hérite du fond via `RootLayout` → `LandingLayout` → `LandingPage`.
- **Architecture layout** : `RootLayout` > `LandingLayout` > `LandingPage`. `LandingLayout` est juste un wrapper CSS sans AppShell — il ne recrée pas de fond.
- **Tokens CSS** : utiliser les tokens premium (`--premium-*`) définis dans `frontend/src/styles/premium-theme.css`. Les alias `theme.css` (`--glass`, `--text-1`, etc.) sont acceptables pour la compatibilité mais les tokens premium sont plus expressifs pour une landing.
- **Pattern glassmorphism** pour toutes les cards/sections : `background: var(--premium-glass-surface-1); backdrop-filter: blur(18px) saturate(140%); border: 1px solid var(--premium-glass-border); border-radius: var(--premium-radius-card);`
- **Button** : `<Button variant="primary" size="lg">Démarrer gratuitement</Button>` — `frontend/src/components/ui/Button/Button.tsx`
- **i18n** — pattern exact du projet :
  1. Créer `frontend/src/i18n/landing.ts` suivant le modèle exact de `frontend/src/i18n/auth.ts` (interface + record `fr`/`en` + fonction export)
  2. Ajouter dans `frontend/src/i18n/index.ts` : le namespace `landing` dans `TranslationMap` et `translationFunctions`
  3. Dans le composant : `const t = useTranslation('landing')`

### Project Structure Notes

```
frontend/src/
├── pages/
│   └── landing/
│       ├── LandingPage.tsx        # nouveau
│       ├── LandingPage.css        # nouveau
│       └── sections/
│           └── HeroSection.tsx    # nouveau
├── layouts/
│   └── LandingLayout.tsx          # nouveau
├── i18n/
│   └── landing.ts                 # nouveau
└── app/
    └── routes.tsx                 # modifier — rendre "/" directement
```

### References

- Structure CSS variables : [frontend/src/index.css](frontend/src/index.css)
- StarfieldBackground : [frontend/src/components/StarfieldBackground.tsx](frontend/src/components/StarfieldBackground.tsx)
- Button UI : [frontend/src/components/ui/Button/Button.tsx](frontend/src/components/ui/Button/Button.tsx)
- Pattern i18n : [frontend/src/i18n/auth.ts](frontend/src/i18n/auth.ts)
- Routes : [frontend/src/app/routes.tsx](frontend/src/app/routes.tsx)
- Document de référence funnel : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#structure-détaillée-de-la-landing-page)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
