# Story 63.9: Footer de la landing page

Status: done

## Mise en oeuvre réelle

- Le footer final a été allégé : pas de colonne sociale rendue tant que les URLs ne sont pas activées.
- Le contact et la confidentialité ont été remontés dans une colonne de confiance plus utile que des colonnes semi-vides.
- Le footer reste strict sur l'absence de liens morts.

## Story

As a visiteur parcourant la landing page,
I want un footer complet avec les liens légaux, les réseaux sociaux et les informations de contact,
so que je puisse accéder aux informations légales et avoir confiance dans la légitimité du produit.

## Acceptance Criteria

### AC1 — Principe strict : aucun lien mort

1. **Règle absolue** : un lien du footer n'est rendu que si sa destination existe réellement. Aucun `href="#"`, aucun lien vers une page inexistante.
2. Le composant lit un objet de configuration `footerLinks` depuis `landing.ts` où chaque lien a un champ `enabled: boolean`. Si `enabled: false`, le lien n'est pas rendu du tout (ni masqué CSS, absent du DOM).

### AC2 — Contenu conditionnel du footer

3. Liens **Produit** (rendus si `enabled: true`) :
   - "Comment ça marche" → ancre `#how-it-works` (toujours activé)
   - "Tarifs" → ancre `#pricing` (toujours activé)
   - "Se connecter" → `/login` (toujours activé)
4. Liens **Légal** (rendus uniquement si la page de destination existe dans `routes.tsx`) :
   - "Politique de confidentialité" → `/privacy` (déjà dans routes.tsx — activé)
   - "Mentions légales" → `/legal` (activé uniquement si cette route est créée avant le lancement)
   - "CGV/CGU" → activé uniquement si route disponible
   - "Politique de cookies" → activé uniquement si implémentée
5. Liens **Contact/Support** : rendus uniquement si une URL ou mailto réelle est définie dans la config. Pas de placeholder.
6. Icônes **réseaux sociaux** : rendues uniquement si l'URL du réseau est définie dans la config (pas de `href="#"`). Si non définies, la colonne réseaux sociaux est absente.
7. Copyright : `© {new Date().getFullYear()} [Nom App]` — dynamique.

### AC3 — Style

8. Aucun style inline : CSS dans `LandingFooter.css`.
9. Fond footer : `var(--color-bg-base)` (`#070a14` en dark, fond sombre distinctif) avec `border-top: 1px solid var(--color-line)`.
10. Layout desktop : colonnes en flex/grid (nombre selon liens activés), layout mobile : 1–2 colonnes empilées.
11. Séparateur `<hr>` ou border-top au-dessus du copyright avec `var(--color-line)`.
12. Liens footer : couleur `var(--premium-text-meta)` au repos, hover `var(--premium-text-main)`, `transition: color var(--duration-fast)`, focus-visible au clavier.

### AC4 — i18n

13. Labels, URLs configurables et flags `enabled` dans `frontend/src/i18n/landing.ts` sous clé `footer`.

### Definition of Done QA

- [ ] Aucun `href="#"` dans le DOM du footer
- [ ] Lien "Mentions légales" absent si la route `/legal` n'existe pas dans `routes.tsx`
- [ ] Lien "Réseaux sociaux" absent si URL non définie dans config
- [ ] Tous les liens footer utilisables au clavier (focus-visible)
- [ ] Copyright affiche l'année courante dynamiquement

## Tasks / Subtasks

- [ ] T1 — Créer `LandingFooter.tsx` (AC: 1–7)
  - [ ] Objet `footerLinks` dans i18n avec champ `enabled`
  - [ ] Rendu conditionnel strict (pas de `href="#"`)
  - [ ] Copyright dynamique
- [ ] T2 — CSS (AC: 8–12)
  - [ ] Créer `LandingFooter.css`
  - [ ] Colonnes dynamiques selon liens actifs
- [ ] T3 — i18n (AC: 13)
  - [ ] Clé `footer` dans `landing.ts` avec `enabled` par lien

## Dev Notes

- **i18n** : `useTranslation('landing')` — voir `frontend/src/i18n/index.ts`.
- **Tokens** : `--color-bg-base` (#070a14), `--color-line` (couleur de séparateur), `--premium-text-meta` (liens au repos), `--premium-text-main` (liens hover), `--duration-fast` (150ms) — tous dans `design-tokens.css` et `theme.css`.
- **Vérifier `routes.tsx`** : `/privacy` existe déjà. Toutes les autres pages légales à `enabled: false` jusqu'à création de leurs routes.
- **Réseaux sociaux** : `enabled: false` par défaut. Ne jamais mettre `href="#"`.
- Ce footer est distinct de tout footer potentiel de l'app authentifiée.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── LandingFooter.tsx    # nouveau
└── LandingFooter.css    # nouveau
```

### References

- Routes existantes : [frontend/src/app/routes.tsx](frontend/src/app/routes.tsx) (pour vérifier `/privacy` etc.)
- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)
- Document funnel — Footer : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
