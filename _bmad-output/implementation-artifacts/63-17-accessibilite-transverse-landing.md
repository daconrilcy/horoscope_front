# Story 63.17: Accessibilité transverse — landing page complète

Status: done

## Mise en oeuvre réelle

- Le skip link est présent dans `LandingLayout`.
- Les labels ARIA de navigation, l'accordéon FAQ et les contrôles du menu mobile sont câblés.
- Le hover des cartes pricing respecte `prefers-reduced-motion`.
- L'audit reste une passe continue, mais les correctifs transverses prioritaires de la landing ont été intégrés.

## Story

As a utilisateur avec handicap visuel, moteur ou cognitif visitant la landing page,
I want pouvoir naviguer et utiliser toutes les fonctionnalités de la landing uniquement au clavier ou avec un lecteur d'écran,
so que le produit soit accessible à tous et conforme WCAG 2.1 AA.

## Note

**Cette story doit être implémentée après les stories UI (63.1–63.9), idéalement en dernier avant la mise en ligne.** Elle constitue une passe transverse d'audit et de correction — pas une refonte.

## Acceptance Criteria

### AC1 — Navigation clavier complète

1. Tous les éléments interactifs de la landing sont atteignables et activables au clavier (Tab, Shift+Tab, Enter, Space, Escape) :
   - Navbar : liens, CTA, menu hamburger mobile, sélecteur de langue
   - Hero : CTAs primaire et secondaire
   - CTAs des plans tarifaires
   - Accordéon FAQ (ouverture/fermeture)
   - Liens du footer
2. L'ordre de focus suit l'ordre visuel logique de la page (pas de focus qui saute dans tous les sens).
3. Un **skip link** "Aller au contenu principal" est présent en première position focusable (visible au focus, invisible au repos).

### AC2 — Focus visible

4. Tous les éléments focusables ont un outline de focus visible et suffisamment contrasté (ne pas utiliser `outline: none` sans alternative).
5. L'outline de focus utilise `var(--primary)` ou une couleur accessible sur tous les fonds de la landing.

### AC3 — Structure sémantique

6. La hiérarchie des titres est cohérente et non sautée : H1 (hero) → H2 (sections) → H3 (sous-sections si présentes).
7. Les listes de bullet points utilisent `<ul>/<li>`, pas des `<div>` avec icônes en texte.
8. La navbar utilise `<nav>` avec `aria-label="Navigation principale"`.
9. Les sections principales ont des `aria-label` ou `aria-labelledby` liés à leur H2.
10. Les images décoratives ont `alt=""`, les images informatives ont un `alt` descriptif.

### AC4 — Composants interactifs

11. **Accordéon FAQ** : chaque élément a `aria-expanded`, `aria-controls`, et le contenu a `id` correspondant.
12. **Menu hamburger mobile** : bouton avec `aria-expanded`, `aria-controls`, `aria-label="Ouvrir le menu"`.
13. **Fermeture menu mobile** : Escape ferme le menu et retourne le focus sur le bouton hamburger.

### AC5 — Mouvement réduit

15. Toutes les animations de la landing respectent `@media (prefers-reduced-motion: reduce)` — désactivées ou réduites à des transitions instantanées.
16. Un test visuel est effectué avec le réglage activé dans le navigateur.

### AC6 — Contraste des couleurs

17. Tous les textes sur tous les fonds de la landing respectent un ratio de contraste ≥ 4.5:1 (texte normal) ou ≥ 3:1 (texte large ≥ 18px ou gras ≥ 14px).
18. Les badges, pills et étiquettes colorées ont un contraste suffisant avec leur fond.

### Definition of Done QA

- [ ] Navigation clavier complète sans souris : chaque CTA, lien, menu mobile et accordéon FAQ activable
- [ ] Skip link visible au premier Tab sur la landing
- [ ] Menu hamburger mobile : Escape → fermeture + focus retour sur bouton
- [ ] Accordéon FAQ : `aria-expanded` change à l'ouverture/fermeture
- [ ] `prefers-reduced-motion: reduce` → aucune animation visible
- [ ] Audit automatisé axe-core (ou Lighthouse Accessibility ≥ 90) sans erreur critique
- [ ] Contraste hero H1 sur fond starfield ≥ 4.5:1 (vérifier avec le fond réel)

## Tasks / Subtasks

- [ ] T1 — Skip link (AC: 3)
  - [ ] `<a href="#main-content" class="skip-link">` en premier élément du layout
  - [ ] CSS : visible au focus uniquement
- [ ] T2 — Navigation clavier navbar et menu mobile (AC: 1, 2, 13, 14)
  - [ ] `aria-expanded`, `aria-controls` sur hamburger
  - [ ] Fermeture Escape + retour focus
- [ ] T3 — Structure sémantique (AC: 6–10)
  - [ ] Audit hiérarchie titres
  - [ ] `<nav aria-label>`, sections `aria-labelledby`
  - [ ] `alt` sur toutes les images
- [ ] T4 — Composants interactifs (AC: 11, 12)
  - [ ] FAQ accordéon `aria-expanded`/`aria-controls`
  - [ ] Vérifier les CTAs et liens de pricing, sans supposer l'existence d'un switch de facturation
- [ ] T5 — prefers-reduced-motion (AC: 15, 16)
  - [ ] Audit toutes les CSS animations/transitions de la landing
  - [ ] `@media (prefers-reduced-motion: reduce)` dans chaque fichier CSS section
- [ ] T6 — Audit contraste (AC: 17, 18)
  - [ ] Vérifier contrastes avec Lighthouse ou axe DevTools
  - [ ] Corriger les non-conformités

## Dev Notes

- **Outil recommandé** : axe DevTools (extension Chrome gratuite) pour l'audit manuel + Lighthouse Accessibility pour le score automatique.
- **Ne pas réécrire les composants** : c'est une passe de correction/enrichissement ARIA, pas une refonte.
- **Focus visible** : si `outline: none` existe dans le CSS landing, le remplacer par un outline visible. Ne pas le supprimer sans remplacement.
- **prefers-reduced-motion** : règle CSS globale à ajouter dans `LandingPage.css` ou dans le CSS global landing :
  ```css
  @media (prefers-reduced-motion: reduce) {
    .landing-page *, .landing-page *::before, .landing-page *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

### References

- WCAG 2.1 AA : https://www.w3.org/WAI/WCAG21/quickref/
- axe-core : outil d'audit standard
- Stories UI landing : 63-01 à 63-09 (à auditer)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
