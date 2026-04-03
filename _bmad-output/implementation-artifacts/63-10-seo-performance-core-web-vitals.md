# Story 63.10: SEO & Performance (Core Web Vitals)

Status: done

## Story

As a responsable produit et responsable SEO,
I want que la landing page soit optimisée pour les moteurs de recherche et les performances (Core Web Vitals),
so que la page soit indexée correctement, charge rapidement et convertisse mieux.

## Acceptance Criteria

### AC1 — Meta tags SEO

1. La `LandingPage` injecte dans le `<head>` via un composant `Helmet` ou `useEffect` + manipulation DOM :
   - `<title>` : titre optimisé (ex. "Votre Astrologue IA Personnel | [Nom App]")
   - `<meta name="description">` : description de 150–160 caractères, orientée intention
   - `<meta property="og:title">` et `<meta property="og:description">` pour Open Graph
   - `<link rel="canonical">` pointant vers l'URL de production
2. Le H1 et le `<title>` sont cohérents (même thématique, pas en compétition).
3. Les meta tags sont externalisés dans `frontend/src/i18n/landing.ts` sous clé `seo`.

### AC2 — Données structurées JSON-LD

4. Un bloc `<script type="application/ld+json">` est injecté dans le `<head>` avec le type `SoftwareApplication` :
   ```json
   {
     "@context": "https://schema.org",
     "@type": "SoftwareApplication",
     "name": "[Nom App]",
     "applicationCategory": "LifestyleApplication",
     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
     "operatingSystem": "Web"
   }
   ```
5. Un bloc JSON-LD `FAQPage` est injecté avec les questions/réponses de la section FAQ (story 63-08) pour les rich results Google.

### AC3 — Performance images

6. Toutes les images de la landing page (`<img>`) ont :
   - `loading="lazy"` sauf l'image hero principale (above the fold → `loading="eager"`)
   - `width` et `height` attributs pour éviter le CLS (Cumulative Layout Shift)
   - `alt` descriptif
7. L'image hero (ou visuel produit) est au format WebP ou AVIF si possible, sinon PNG optimisé.
8. LCP cible : le visuel hero principal doit être la LCP element et charger en < 2.5s sur connexion 4G simulée.

### AC4 — Performance JS et CSS

9. La `LandingPage` est une route distincte (lazy-loaded) : utiliser `React.lazy` + `Suspense` dans `routes.tsx` pour que le bundle de la landing ne soit pas chargé dans l'app authentifiée.
10. Aucun import de librairie lourde spécifique à la landing qui n'existerait pas déjà dans le bundle principal.
11. Les polices utilisées (si custom) sont préchargées avec `<link rel="preload">`.

### AC5 — Vérification CLS

12. Aucun élément de la landing n'a de CLS > 0.1 : les images ont des dimensions réservées, les polices n'induisent pas de FOUT, les animations CSS ne déplacent pas le contenu existant.
13. **Le conteneur du visuel hero (story 63.1) a des dimensions CSS figées ou un `aspect-ratio` stable** : vérifier que le bloc visuel à droite ne provoque pas de layout shift lors du chargement de l'image (coordonner avec story 63.1 AC9).
14. Si aucun screenshot réel n'est disponible, le visuel hero est un asset statique optimisé avec dimensions connues à l'avance — pas de chargement asynchrone non dimensionné.

### Definition of Done QA

- [ ] Meta title et description non vides (vérifiable en DevTools → Elements → `<head>`)
- [ ] JSON-LD `SoftwareApplication` présent dans le `<head>` (vérifiable via Google Rich Results Test)
- [ ] JSON-LD `FAQPage` contient les mêmes questions que la section 63.8
- [ ] Image hero sans CLS : `width` et `height` ou `aspect-ratio` CSS définis
- [ ] `LandingPage` en `React.lazy` dans `routes.tsx` : bundle landing absent du chunk auth (vérifiable en DevTools → Network → JS)
- [ ] Toutes les images hors hero avec `loading="lazy"`
- [ ] Image hero avec `loading="eager"` et `fetchpriority="high"`

## Tasks / Subtasks

- [ ] T1 — Meta tags SEO (AC: 1, 2, 3)
  - [ ] Vérifier si `react-helmet-async` est déjà installé dans le projet
  - [ ] Implémenter les meta tags dans `LandingPage.tsx`
  - [ ] Clé `seo` dans `landing.ts`
- [ ] T2 — JSON-LD (AC: 4, 5)
  - [ ] Composant `StructuredData.tsx` ou injection inline
  - [ ] SoftwareApplication + FAQPage schemas
- [ ] T3 — Images optimisées (AC: 6, 7, 8)
  - [ ] Attributs `loading`, `width`, `height`, `alt` sur toutes les images
  - [ ] Image hero en `loading="eager"`
- [ ] T4 — Code splitting landing (AC: 9, 10, 11)
  - [ ] `React.lazy(() => import('./pages/landing/LandingPage'))` dans `routes.tsx`
  - [ ] `<Suspense>` wrapper
- [ ] T5 — Vérification CLS (AC: 12)
  - [ ] Audit visuel des animations et images
  - [ ] Dimensions réservées pour les images

## Dev Notes

- **react-helmet-async** : vérifier sa présence dans `package.json`. Sinon, utiliser un `useEffect` pour setter `document.title` et les meta tags via `document.querySelector` — moins élégant mais sans dépendance.
- **Lazy loading route** : `React.lazy` est natif React 19 — pattern à utiliser dans `routes.tsx` avec `<Suspense fallback={<div />}>`.
- **JSON-LD FAQ** : les questions/réponses doivent être les mêmes que celles de `FaqSection` (story 63-08) — partager les données depuis `landing.ts`.
- **LCP** : l'image hero étant above-the-fold, ne pas lui mettre `loading="lazy"`. Lui ajouter `fetchpriority="high"` si c'est une `<img>`.

### Project Structure Notes

```
frontend/src/pages/landing/
├── LandingPage.tsx        # modifier — ajouter meta tags + JSON-LD
frontend/src/app/
└── routes.tsx             # modifier — React.lazy pour LandingPage
```

### References

- routes.tsx : [frontend/src/app/routes.tsx](frontend/src/app/routes.tsx)
- package.json : [frontend/package.json](frontend/package.json) (vérifier react-helmet-async)
- Document funnel — SEO : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#seo-on-page-et-performance)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
