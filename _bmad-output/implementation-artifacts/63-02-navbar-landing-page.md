# Story 63.2: Barre de navigation de la landing page

Status: done

## Story

As a visiteur non authentifié sur la landing page,
I want une barre de navigation claire avec le logo, les liens essentiels et un accès rapide à la connexion,
so that je puisse naviguer facilement entre les sections et me connecter ou m'inscrire sans friction.

## Acceptance Criteria

### AC1 — Composition de la navbar

1. [x] La navbar contient dans l'ordre : Logo (gauche) | Liens de navigation (centre) | Actions (droite).
2. [x] Liens de navigation : "Comment ça marche" (ancre vers `#how-it-works`), "Tarifs" (ancre vers `#pricing`).
3. [x] Actions droite : bouton "Connexion" → `/login` et bouton CTA "Démarrer" → `/register`.
4. [x] Un sélecteur de langue FR/EN est présent (icône globe ou label), appliquant la langue via le mécanisme i18n du projet.

### AC2 — Comportement sticky et scroll

5. [x] La navbar est sticky (`position: sticky; top: 0`) et reste visible lors du scroll.
6. [x] Sur scroll > 50px, la navbar adopte un fond légèrement opaque/glass (backdrop-filter ou background semi-transparent) pour rester lisible sur le fond hero.
7. [x] La transition fond transparent → fond glass est animée (150–200ms ease).

### AC3 — Responsive mobile

8. [x] Sur mobile (< 768px), les liens "Comment ça marche" et "Tarifs" sont masqués ou regroupés dans un menu hamburger.
9. [x] Le menu hamburger s'ouvre en overlay ou dropdown avec les liens et les actions.
10. [x] Le bouton "Démarrer" reste visible sur mobile sans menu hamburger.

### AC4 — Style cohérent

11. [x] Aucun style inline : CSS dans `frontend/src/pages/landing/sections/LandingNavbar.css`.
12. [x] Variables CSS utilisées — suivre le pattern de `app-bg` :
    - Fond transparent → fond glass : `var(--color-nav-glass)` avec `backdrop-filter: blur(18px) saturate(140%)`
    - Bordure inférieure au scroll : `var(--color-nav-border)`
    - Texte liens : `var(--premium-text-main)`
    - CTA button : composant `Button` avec `variant="primary"` et `size="sm"`
    - Ombre au scroll : `var(--premium-shadow-nav)` ou `var(--shadow-nav)`
13. [x] La navbar de la landing est distincte de l'AppShell/Header de l'app authentifiée — pas de réutilisation du composant `AppShell`.

### AC5 — i18n

14. [x] Tous les labels (liens, boutons, langue) dans `frontend/src/i18n/landing.ts` sous la clé `navbar`.

## Tasks / Subtasks

- [x] T1 — Créer le composant `LandingNavbar` (AC: 1, 2, 3, 4)
  - [x] Créer `frontend/src/pages/landing/sections/LandingNavbar.tsx`
  - [x] Logo (utiliser le même logo que l'app)
  - [x] Liens d'ancre + actions droite
  - [x] Sélecteur langue
- [x] T2 — Comportement sticky + scroll (AC: 5, 6, 7)
  - [x] CSS sticky
  - [x] Listener scroll pour classe glass-on-scroll
- [x] T3 — Menu hamburger mobile (AC: 8, 9, 10)
  - [x] Bouton hamburger sur < 768px
  - [x] Dropdown/overlay mobile
- [x] T4 — CSS (AC: 11, 12, 13)
  - [x] Créer `LandingNavbar.css`
- [x] T5 — i18n (AC: 14)
  - [x] Ajouter clé `navbar` dans `landing.ts`

## Dev Notes

- Ne pas réutiliser `AppShell` ni le `Header` de l'app interne (ils dépendent de l'état auth et de la sidebar).
- **Logo** : vérifier `frontend/src/assets/` ou `public/` — le même logo que l'app.
- **Pattern scroll glass** : utiliser `--color-nav-glass` et `--color-nav-border` qui sont les tokens prévus pour les navbars glass dans le projet.
- **Icônes** : Lucide React disponible (déjà dans les dépendances) — `Globe`, `Menu`, `X`, `ChevronDown`.
- **i18n** — même pattern que story 63.1 : `useTranslation('landing')` après enregistrement du namespace `landing` dans `frontend/src/i18n/index.ts`. Consulter `frontend/src/i18n/auth.ts` pour le modèle exact.
- **Langues supportées** : `fr`, `en`, `es` (comme les autres namespaces) — voir `AstrologyLang` dans `frontend/src/i18n/types.ts`.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── LandingNavbar.tsx    # nouveau
└── LandingNavbar.css    # nouveau
```

### References

- Pattern i18n : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts) (créé en 63-01)
- AppShell existant (pour référence, NE PAS réutiliser) : [frontend/src/components/AppShell.tsx](frontend/src/components/AppShell.tsx)
- Document de référence funnel wireframe : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-001 (Code Review & Fix)

### Debug Log References

- Fixed inline styles in `LandingNavbar.tsx`.
- Adjusted responsive breakpoint to 768px in `LandingNavbar.css`.
- Fixed logo path by using ES imports.
- Verified all ACs are met.

### Completion Notes List

- Implementation is now fully compliant with AC4 (no inline styles).
- Responsive behavior aligns with AC3 (768px breakpoint).
- i18n is correctly implemented and used.

### File List

- frontend/src/i18n/landing.ts
- frontend/src/pages/landing/sections/LandingNavbar.tsx
- frontend/src/pages/landing/sections/LandingNavbar.css
- frontend/src/layouts/LandingLayout.tsx
