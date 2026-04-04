# Story 63.3: Section Preuves rapides (Social Proof)

Status: done

## Mise en oeuvre réelle

- La variante MVP réellement exposée est une section de confiance qualitative en 3 colonnes desktop / 1 colonne mobile.
- Chaque item affiche désormais : icône + intitulé + preuve courte explicite.
- La variante chiffrée reste techniquement possible côté contenu, mais le funnel principal n'affiche aucune métrique client fictive.

## Story

As a visiteur non authentifié explorant la landing page,
I want voir des signaux de confiance concrets juste sous le hero (métriques, logos, badges),
so that ma perception de légitimité du produit augmente et je continue à lire.

## Acceptance Criteria

### AC1 — Conformité des données affichées (bloquant prod)

1. **Aucune métrique chiffrée fictive ne peut être affichée en production** : toute statistique ("X utilisateurs", "4.8/5", "200+ avis") doit être soit réelle et vérifiable, soit absente.
2. En l'absence de métriques réelles validées, la section affiche uniquement des **éléments qualitatifs non quantifiés** : badges de confiance, labels de fonctionnalité, certifications — jamais de chiffres inventés.
3. Un **variant de contenu** est défini dans `landing.ts` : `socialProof.variant = 'metrics'` (avec chiffres réels) ou `'badges'` (qualitatif seul). Le composant rend l'un ou l'autre selon la config. Par défaut : `'badges'` jusqu'à ce que des métriques réelles soient validées par le PO.
4. Un feature flag `VITE_SOCIAL_PROOF_VARIANT` (`metrics` | `badges`) contrôle le variant actif.

### AC2 — Contenu de la section

5. La section apparaît immédiatement sous le hero (entre le hero et la section Problème).
6. **Variant `badges`** (par défaut) : 3 badges qualitatifs non chiffrés :
   - "Calculs Swiss Ephemeris" (réel — cf. epic 20)
   - "Données protégées RGPD"
   - "Disponible 24h/24"
7. **Variant `metrics`** (activé uniquement si métriques réelles disponibles) : remplace les badges par des métriques chiffrées validées par le PO.
8. Section avec `id="social-proof"` pour les ancres.

### AC3 — Style et layout

9. Layout horizontal sur desktop (flex row, centré), vertical ou grille 2 colonnes sur mobile.
10. Fond de section : `background: var(--premium-glass-surface-2)` avec `backdrop-filter: blur(14px)` — légèrement différencié du hero.
11. Chaque item badge/métrique a : icône + texte — pas de chiffres si variant `badges`.
12. Animation d'entrée non bloquante respectant `prefers-reduced-motion`.
13. Aucun style inline : CSS dans `SocialProofSection.css`.

### AC4 — i18n

14. Labels, badges et métriques dans `frontend/src/i18n/landing.ts` sous clé `socialProof`.
15. Les deux variants (`badges` et `metrics`) ont leurs textes définis dans i18n.

### Definition of Done QA

- [ ] Avec `VITE_SOCIAL_PROOF_VARIANT=badges` : aucun chiffre visible
- [ ] Avec `VITE_SOCIAL_PROOF_VARIANT=metrics` : chiffres visibles uniquement si définis dans i18n (pas de valeur vide affichée)
- [ ] Aucune métrique "4.8/5" ou "200+ avis" fictive visible en prod
- [ ] Section lisible sur 375px (pas d'overflow horizontal)

## Tasks / Subtasks

- [ ] T1 — Créer `SocialProofSection.tsx` (AC: 1, 2, 3, 4)
  - [ ] 3+ items de preuve sociale avec données statiques
  - [ ] `id="social-proof"` sur la section
- [ ] T2 — CSS et animation (AC: 5, 6, 7, 8, 9)
  - [ ] Créer `SocialProofSection.css`
  - [ ] IntersectionObserver pour fade-in
- [ ] T3 — i18n (AC: 10)
  - [ ] Clé `socialProof` dans `landing.ts`

## Dev Notes

- **i18n** : même pattern que toutes les sections — `useTranslation('landing')` après enregistrement dans `frontend/src/i18n/index.ts`. Les namespaces `TranslationMap` et `translationFunctions` sont dans ce fichier.
- Les données métriques sont fictives/marketing à ce stade — utiliser le variant `badges` par défaut.
- Pour l'animation : CSS transition + IntersectionObserver natif. Vérifier si un hook `useIntersectionObserver` existe dans `frontend/src/hooks/` avant d'en créer un.
- **Tokens premium** : `frontend/src/styles/premium-theme.css` — les tokens `--premium-glass-*`, `--premium-text-*`, `--premium-shadow-*` sont définis là.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── SocialProofSection.tsx    # nouveau
└── SocialProofSection.css    # nouveau
```

### References

- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)
- Variables CSS : [frontend/src/index.css](frontend/src/index.css)
- Document funnel : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
