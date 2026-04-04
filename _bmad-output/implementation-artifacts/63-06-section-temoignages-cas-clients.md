# Story 63.6: Section Preuves — Témoignages et Cas clients

Status: implemented-behind-flag

## Mise en oeuvre réelle

- Le composant `TestimonialsSection` existe toujours avec feature flag `VITE_SHOW_TESTIMONIALS`.
- Dans la landing refondue actuelle, la section n'est plus rendue dans le parcours principal MVP.
- La stratégie retenue est : confiance qualitative + FAQ dans le funnel principal, témoignages réactivables plus tard une fois des retours clients validés disponibles.

## Story

As a visiteur non authentifié envisageant de s'inscrire,
I want lire des témoignages réels et voir un mini cas client avant/après,
so que ma confiance dans le produit augmente et que je comprenne concrètement ce que le produit apporte.

## Acceptance Criteria

### AC1 — Conformité marketing obligatoire (bloquant prod)

1. **Aucun témoignage fictif ne peut être publié en production** : les témoignages affichés sont soit des témoignages réels collectés et validés par le PO, soit des cas illustratifs explicitement labelisés comme tels ("Témoignage illustratif" ou "Cas inspiré d'utilisateurs réels").
2. Les témoignages **ne contiennent aucune métrique chiffrée inventée** (ex. "-27% en 3 semaines", "3x plus rapide") sauf si elles correspondent à des données vérifiables.
3. Un mécanisme de feature flag (`SHOW_TESTIMONIALS=true/false` via variable d'environnement ou config frontend) permet de masquer la section si aucun témoignage validé n'est disponible au lancement.
4. En l'absence de témoignages validés, la section est soit masquée, soit remplacée par un message neutre non trompeur ("Rejoignez nos premiers utilisateurs").

### AC2 — Témoignages

5. La section est identifiée par `id="testimonials"`.
6. Quand des témoignages validés sont disponibles, chaque témoignage affiche :
   - Citation entre guillemets (centrée sur un résultat ou une expérience vécue)
   - Prénom + initiale du nom (ou pseudonyme consenti)
   - Contexte bref (ex. "Utilisatrice, Verseau")
   - Avatar : initiales dans un cercle coloré ou icône zodiac — **pas de photo réelle sans consentement explicite**
   - Note étoiles (uniquement si réelle)
7. Les données des témoignages proviennent exclusivement de `frontend/src/i18n/landing.ts` sous clé `testimonials.items` — **pas de hardcode dans le composant**.

### AC3 — Mini étude de cas avant/après

8. Un bloc "Avant / Après" illustratif est présent, explicitement labelisé comme "Cas illustratif" ou équivalent si basé sur un composite.
9. Structure : contexte initial | action prise | résultat observé — sans métriques chiffrées inventées.
10. Layout 2 colonnes contrastées (avant : teinte neutre ; après : `var(--primary)` ou `var(--success)`).

### AC4 — Badges de réassurance statiques (remplace la FAQ inline supprimée)

11. Trois badges de réassurance statiques remplacent toute FAQ inline dans cette section :
    - "🔒 Données chiffrées et protégées"
    - "⭐ Calculs basés sur Swiss Ephemeris"
    - "↩ Annulation sans conditions"
12. Ces badges sont **statiques**, pas interactifs, pas d'accordéon ici — toute FAQ structurée est dans la story 63.8.
13. CSS dans `TestimonialsSection.css` : badges en flex row desktop, wrapping mobile.

### AC5 — Style

14. Aucun style inline : CSS dans `TestimonialsSection.css`.
15. Cards témoignages : pattern glassmorphism premium cohérent avec les autres pages :
    ```css
    background: var(--premium-glass-surface-1);
    backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--premium-glass-border);
    border-radius: var(--premium-radius-card); /* 24px */
    box-shadow: var(--premium-shadow-card);
    ```
16. Layout témoignages : grille CSS 3 colonnes desktop, 1 colonne mobile (scroll snap optionnel sur mobile).
17. Animation au scroll : `prefers-reduced-motion` doit être respecté — si `@media (prefers-reduced-motion: reduce)`, aucune animation.

### AC6 — i18n

18. Tous les textes (témoignages, avant/après, badges) dans `frontend/src/i18n/landing.ts` sous clé `testimonials`.

### Definition of Done QA

- [ ] Aucun témoignage avec chiffre inventé n'est visible en prod
- [ ] Si `SHOW_TESTIMONIALS=false`, la section est absente du DOM (pas seulement masquée CSS)
- [ ] Les badges de réassurance s'affichent sans accordéon
- [ ] Sur 375px, les cards témoignages sont lisibles (pas de overflow horizontal)
- [ ] Animation désactivée si `prefers-reduced-motion: reduce`
- [ ] Aucun `href="#"` dans la section

## Tasks / Subtasks

- [ ] T1 — Créer `TestimonialsSection.tsx` (AC: 1–7)
  - [ ] Feature flag `SHOW_TESTIMONIALS` (env var ou config)
  - [ ] 2–3 cards témoignages depuis i18n (contenu validé ou section masquée)
  - [ ] Label "Cas illustratif" sur le avant/après
- [ ] T2 — Bloc avant/après (AC: 8, 9, 10)
  - [ ] Layout 2 colonnes contrastées
  - [ ] Absence de métriques inventées
- [ ] T3 — Badges de réassurance (AC: 11, 12, 13)
  - [ ] 3 badges statiques (pas d'accordéon)
- [ ] T4 — CSS + a11y (AC: 14–17)
  - [ ] Créer `TestimonialsSection.css`
  - [ ] `@media (prefers-reduced-motion: reduce)` : animations coupées
- [ ] T5 — i18n (AC: 18)

## Dev Notes

- **Différence par rapport à la FAQ** : cette section ne contient AUCUNE FAQ. Toutes les objections FAQ sont dans la story 63.8. Ce découpage est intentionnel pour éviter la duplication et le désalignement du JSON-LD FAQ côté SEO.
- **i18n** : `useTranslation('landing')` — namespace à enregistrer dans `frontend/src/i18n/index.ts` selon le pattern de `auth.ts`.
- **Tokens premium** : `frontend/src/styles/premium-theme.css`. Ne pas utiliser `var(--glass)` seul sans `backdrop-filter`.
- **Feature flag** : implémenter via une constante dans `frontend/src/config/featureFlags.ts` (ou équivalent existant) contrôlée par env var `VITE_SHOW_TESTIMONIALS=true`.
- **prefers-reduced-motion** : règle CSS à ajouter dans `TestimonialsSection.css` :
  ```css
  @media (prefers-reduced-motion: reduce) {
    .testimonials-section * {
      animation: none !important;
      transition: none !important;
    }
  }
  ```
- Swiss Ephemeris mentionné dans le badge est réel (cf. epic 20) — citation légitime.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── TestimonialsSection.tsx    # nouveau
└── TestimonialsSection.css    # nouveau
```

### References

- Epic 20 Swiss Ephemeris : `_bmad-output/implementation-artifacts/20-1-installation-configuration-swiss-ephemeris.md`
- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)
- Document funnel — Preuves : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
