# Story 63.5: Section Solution — Comment ça marche

Status: done

## Mise en oeuvre réelle

- Le CTA secondaire du hero cible cette section avec le libellé `Découvrir comment ça marche`.
- La section finale ne repose plus sur 3 cartes génériques avec connecteurs décoratifs lourds.
- Chaque étape embarque une micro-preuve d'usage visible : données demandées, question type, synthèse actionnable.

## Story

As a visiteur non authentifié sur la landing page,
I want voir en 3 étapes simples comment le produit fonctionne concrètement,
so that je comprenne le mécanisme et la valeur ajoutée avant de m'inscrire.

## Acceptance Criteria

### AC1 — Structure en 3 étapes

1. La section est identifiée par `id="how-it-works"` (cible du CTA secondaire "Voir un exemple" du Hero).
2. Elle contient un H2 de section ("Comment ça marche", "En 3 étapes simples").
3. 3 étapes sont présentées, chacune avec :
   - Numéro d'étape (01, 02, 03) stylisé
   - Icône ou illustration (capture écran ou SVG illustratif)
   - Titre de l'étape
   - Description courte (2–3 lignes max)
   - Bénéfice mis en avant (badge ou texte souligné)
4. Les 3 étapes du flux Horoscope IA :
   - Étape 1 : "Partagez votre date, heure et lieu de naissance" → votre thème natal est calculé
   - Étape 2 : "Choisissez votre astrologue IA" → conversation guidée et personnalisée
   - Étape 3 : "Recevez vos insights au quotidien" → guidance actionnable et prédictions

### AC2 — Layout et visuel

5. Layout desktop : 3 colonnes côte à côte avec une flèche/connecteur entre elles.
6. Layout mobile : cards empilées verticalement, numéro d'étape bien visible.
7. Illustration ou screenshot de chaque étape : utiliser des captures écran réelles de l'application si disponibles, sinon un asset illustratif statique validé par le design.
8. Animation au scroll : les 3 cartes apparaissent en cascade (delay 0ms, 150ms, 300ms).

### AC3 — Style

9. Aucun style inline : CSS dans `SolutionSection.css`.
10. Cards d'étapes : pattern glassmorphism premium du projet :
    ```css
    background: var(--premium-glass-surface-1);
    backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--premium-glass-border);
    border-radius: var(--premium-radius-card); /* 24px */
    box-shadow: var(--premium-shadow-card);
    padding: var(--space-6); /* 1.5rem */
    ```
11. Numérotation des étapes : `color: var(--premium-accent-purple)` ou `var(--color-primary)`, font-size large, font-weight 700.

### AC4 — i18n

12. Tous les textes dans `frontend/src/i18n/landing.ts` sous clé `solution`.

## Tasks / Subtasks

- [x] T1 — Créer `SolutionSection.tsx` (AC: 1, 2, 3, 4)
  - [x] `id="how-it-works"` sur la section
  - [x] 3 cards d'étapes avec numéro, icône, titre, description, bénéfice
- [x] T2 — Layout et animation (AC: 5, 6, 7, 8)
  - [x] CSS 3 colonnes desktop / 1 colonne mobile
  - [x] Connecteurs/flèches entre étapes (desktop)
  - [x] Animation cascade IntersectionObserver
- [x] T3 — CSS (AC: 9, 10, 11)
  - [x] Créer `SolutionSection.css`
  - [x] Cards glass, numérotation premium
- [x] T4 — i18n (AC: 12)
  - [x] Clé `solution` dans `landing.ts`

## Dev Notes

- **i18n** : `useTranslation('landing')` — namespace à enregistrer dans `frontend/src/i18n/index.ts`.
- Screenshots de l'app : `frontend/public/landing/step1.webp` etc. (format WebP recommandé). Images avec dimensions fixes pour éviter le CLS.
- Lucide React disponible : `ArrowRight`, `Sparkles`, `Star`, `MessageCircle`.
- Pattern card glass : s'inspirer de `frontend/src/components/ui/Card/Card.tsx` et de `frontend/src/styles/glass.css`. Ne pas réinventer — utiliser `var(--premium-glass-surface-1)` + `backdrop-filter: blur(18px) saturate(140%)`.
- **Tokens premium** : `frontend/src/styles/premium-theme.css` — contient `--premium-radius-card` (24px), `--premium-shadow-card`, `--premium-glass-surface-1`.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── SolutionSection.tsx    # nouveau
└── SolutionSection.css    # nouveau
frontend/public/landing/
├── step1-screenshot.png   # à créer/fournir
├── step2-screenshot.png   # à créer/fournir
└── step3-screenshot.png   # à créer/fournir
```

### References

- Card UI : [frontend/src/components/ui/Card/Card.tsx](frontend/src/components/ui/Card/Card.tsx)
- Document funnel — Solution : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)
- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
- frontend/src/i18n/landing.ts
- frontend/src/pages/landing/sections/SolutionSection.tsx
- frontend/src/pages/landing/sections/SolutionSection.css
- frontend/src/pages/landing/LandingPage.tsx
