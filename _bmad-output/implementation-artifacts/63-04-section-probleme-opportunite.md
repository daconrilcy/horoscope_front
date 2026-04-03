# Story 63.4: Section Problème → Opportunité

Status: ready-for-dev

## Story

As a visiteur non authentifié sur la landing page,
I want lire une section qui articule clairement les douleurs que je ressens et comment le produit les résout,
so que je me reconnaisse dans la problématique et que ma motivation à essayer le produit augmente.

## Acceptance Criteria

### AC1 — Contenu et structure narrative

1. La section est identifiée par `id="problem"` et apparaît après la section Social Proof.
2. Elle contient deux sous-parties visuellement distinguées :
   - **Bloc "Aujourd'hui"** (problème/douleurs) : liste de 3–4 symptômes courants de l'utilisateur cible (ex : "Vous cherchez des réponses mais les horoscopes génériques ne vous correspondent pas").
   - **Bloc "Avec [Nom produit]"** (opportunité/solution) : contraste positif, transition vers "Nous rendons cela simple".
3. Les symptômes sont présentés avec une icône de douleur (ex : ⚡ ou ✗ rouge) et l'opportunité avec une icône positive (ex : ✓ vert ou ★).
4. Un titre de section H2 clair au-dessus ("Vous vous reconnaissez ?", "Le problème que nous résolvons").

### AC2 — Impact visuel

5. Le design crée une tension visuelle entre le bloc problème (couleurs froides/neutres, légèrement sombres) et le bloc opportunité (couleurs chaudes/premium, lumineux).
6. La transition entre les deux blocs est visuellement marquée (séparateur, gradient, icône de flèche ou transformation).
7. Animation au scroll (fade-in des items en cascade avec `IntersectionObserver`).
8. Layout : 2 colonnes côte à côte sur desktop, empilé verticalement sur mobile.

### AC3 — Style

9. Aucun style inline : CSS dans `ProblemSection.css`.
10. Variables CSS du projet utilisées :
    - Texte : `var(--premium-text-strong)`, `var(--premium-text-main)`, `var(--premium-text-meta)`
    - Douleurs (bloc "Avant") : `var(--color-danger)` ou `var(--color-text-muted)` pour la teinte atténuée
    - Opportunité (bloc "Après") : `var(--premium-accent-purple)` ou `var(--color-primary)` pour la teinte positive
    - Alias `var(--danger)`, `var(--text-1)`, `var(--text-2)` acceptés (définis dans `theme.css`)

### AC4 — i18n

11. Tous les textes (titre, symptômes, opportunités) dans `frontend/src/i18n/landing.ts` sous clé `problem`.

## Tasks / Subtasks

- [ ] T1 — Créer `ProblemSection.tsx` (AC: 1, 2, 3, 4)
  - [ ] Structure HTML sémantique avec `id="problem"`
  - [ ] Bloc douleurs (3–4 items) + bloc opportunités
  - [ ] Icônes différenciées
- [ ] T2 — CSS et animation (AC: 5, 6, 7, 8, 9, 10)
  - [ ] Créer `ProblemSection.css`
  - [ ] Différenciation visuelle douleur/opportunité
  - [ ] Animation IntersectionObserver en cascade
- [ ] T3 — i18n (AC: 11)
  - [ ] Clé `problem` dans `landing.ts`

## Dev Notes

- **i18n** : `useTranslation('landing')` — voir `frontend/src/i18n/index.ts` pour enregistrer le namespace.
- Contenu adapté au contexte astrologie : douleurs typiques = "horoscopes génériques impersonnels", "pas d'accès à un astrologue quand j'en ai besoin", "comprendre son thème natal seul est complexe".
- `var(--danger)` est défini dans `theme.css` comme alias de `--color-error` (`#ff6b81`) ✓
- `var(--success)` est défini dans `theme.css` comme alias de `--color-success` ✓ (ne pas le re-créer)
- **Tokens premium** : `frontend/src/styles/premium-theme.css`.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── ProblemSection.tsx    # nouveau
└── ProblemSection.css    # nouveau
```

### References

- Variables CSS : [frontend/src/index.css](frontend/src/index.css)
- Document funnel — section Problème→Opportunité : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)
- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
