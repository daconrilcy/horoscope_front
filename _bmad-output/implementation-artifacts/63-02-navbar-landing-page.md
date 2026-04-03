# Story 63.2: Barre de navigation de la landing page

Status: ready-for-dev

## Story

As a visiteur non authentifié sur la landing page,
I want une barre de navigation claire avec le logo, les liens essentiels et un accès rapide à la connexion,
so that je puisse naviguer facilement entre les sections et me connecter ou m'inscrire sans friction.

## Acceptance Criteria

### AC1 — Composition de la navbar

1. La navbar contient dans l'ordre : Logo (gauche) | Liens de navigation (centre) | Actions (droite).
2. Liens de navigation : "Comment ça marche" (ancre vers `#how-it-works`), "Tarifs" (ancre vers `#pricing`).
3. Actions droite : bouton "Connexion" → `/login` et bouton CTA "Démarrer" → `/register`.
4. Un sélecteur de langue FR/EN est présent (icône globe ou label), appliquant la langue via le mécanisme i18n du projet.

### AC2 — Comportement sticky et scroll

5. La navbar est sticky (`position: sticky; top: 0`) et reste visible lors du scroll.
6. Sur scroll > 50px, la navbar adopte un fond légèrement opaque/glass (backdrop-filter ou background semi-transparent) pour rester lisible sur le fond hero.
7. La transition fond transparent → fond glass est animée (150–200ms ease).

### AC3 — Responsive mobile

8. Sur mobile (< 768px), les liens "Comment ça marche" et "Tarifs" sont masqués ou regroupés dans un menu hamburger.
9. Le menu hamburger s'ouvre en overlay ou dropdown avec les liens et les actions.
10. Le bouton "Démarrer" reste visible sur mobile sans menu hamburger.

### AC4 — Style cohérent

11. Aucun style inline : CSS dans `frontend/src/pages/landing/sections/LandingNavbar.css`.
12. Variables CSS utilisées — suivre le pattern de `app-bg` :
    - Fond transparent → fond glass : `var(--color-nav-glass)` avec `backdrop-filter: blur(18px) saturate(140%)`
    - Bordure inférieure au scroll : `var(--color-nav-border)`
    - Texte liens : `var(--premium-text-main)`
    - CTA button : composant `Button` avec `variant="primary"` et `size="sm"`
    - Ombre au scroll : `var(--premium-shadow-nav)` ou `var(--shadow-nav)`
13. La navbar de la landing est distincte de l'AppShell/Header de l'app authentifiée — pas de réutilisation du composant `AppShell`.

### AC5 — i18n

14. Tous les labels (liens, boutons, langue) dans `frontend/src/i18n/landing.ts` sous la clé `navbar`.

## Tasks / Subtasks

- [ ] T1 — Créer le composant `LandingNavbar` (AC: 1, 2, 3, 4)
  - [ ] Créer `frontend/src/pages/landing/sections/LandingNavbar.tsx`
  - [ ] Logo (utiliser le même logo que l'app)
  - [ ] Liens d'ancre + actions droite
  - [ ] Sélecteur langue
- [ ] T2 — Comportement sticky + scroll (AC: 5, 6, 7)
  - [ ] CSS sticky
  - [ ] Listener scroll pour classe glass-on-scroll
- [ ] T3 — Menu hamburger mobile (AC: 8, 9, 10)
  - [ ] Bouton hamburger sur < 768px
  - [ ] Dropdown/overlay mobile
- [ ] T4 — CSS (AC: 11, 12, 13)
  - [ ] Créer `LandingNavbar.css`
- [ ] T5 — i18n (AC: 14)
  - [ ] Ajouter clé `navbar` dans `landing.ts`

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

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
