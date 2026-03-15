# Epic 58 — Global App Shell : Top Bar Fixe, Sidebar Navigable à 3 États et Menu Utilisateur

## Objectif

Refondre entièrement la coque applicative (app shell) pour offrir une expérience de navigation moderne, cohérente et accessible :

- Un **top bar fixe** contenant : bouton hamburger (gauche), logo + nom de l'app (centre), toggle dark/light + avatar cliquable (droite).
- Un **menu latéral gauche à 3 états** : caché → overlay étendu (avec backdrop) → icônes seules (après sélection d'un item).
- Un **menu utilisateur flottant** (overlay au clic sur l'avatar) avec informations du profil, liens vers le compte et déconnexion.
- Le nom de l'application `"Astrorizon"` centralisé en constante pour permettre un changement global instantané.

## Contexte technique

**Stack actuel :**
- `frontend/src/layouts/AppLayout.tsx` — orchestre Header, Sidebar, BottomNav et content
- `frontend/src/components/layout/Header.tsx` — header basique sans logo ni hamburger
- `frontend/src/components/layout/Sidebar.tsx` — sidebar statique (toujours visible sur desktop, absente sur mobile)
- `frontend/src/components/layout/BottomNav.tsx` — barre de navigation mobile (à conserver)
- `frontend/src/state/ThemeProvider.tsx` — `useTheme()` / `toggleTheme()`
- `frontend/src/api/authMe.ts` — retourne `{ id, role, email, created_at }`
- `frontend/src/ui/nav.ts` — `NavItem[]` avec `icon: LucideIcon`, `key`, `path`, `label`, `roles`
- `frontend/src/utils/constants.ts` — constantes utilitaires existantes
- Pas de Tailwind ; CSS custom vars (`--color-*`, `--space-*`, `--radius-*`)
- Path aliases : `@ui`, `@components`, `@layouts`, `@utils`, `@state`, `@api`
- `verbatimModuleSyntax: true` → types-only en `import type`

**Pas d'API backend pour l'avatar** — l'avatar est soit une image uploadée (prop future), soit un cercle mauve avec l'initiale de l'email.

## Comportement Sidebar attendu (machine d'état à 3 états)

```
hidden  ──hamburger──►  expanded (overlay + backdrop)
expanded ──nav click──► icon-only  (mini-strip icons seulement)
icon-only ──hamburger──► hidden
hidden  ──hamburger──►  expanded   (cycle)
```

- **hidden** : aucun élément de sidebar visible
- **expanded** : sidebar en superposition, backdrop semi-transparent qui assombrit le reste de la page ; chaque item = icône + label ; fermeture possible via click backdrop ou item
- **icon-only** : bande étroite (≈48px) sur le côté gauche montrant uniquement les icônes, pas de backdrop

## Stories de l'Epic 58

### Story 58.1 — Constante APP_NAME et configuration centrale de l'application
- Fichier : `_bmad-output/implementation-artifacts/58-1-app-name-constante-et-config-centrale.md`
- Scope :
  - Ajouter `APP_NAME = "Astrorizon"` dans `frontend/src/utils/constants.ts`
  - Exposer le logo `docs/interfaces/logo_horoscope02.png` via un import centralisé (`@utils/appConfig` ou barrel)
  - Mettre à jour les références existantes au titre de l'app dans `Header.tsx` et `i18n/common.ts` pour pointer vers cette constante

### Story 58.2 — Refonte Header : hamburger, logo, nom d'app et actions droite
- Fichier : `_bmad-output/implementation-artifacts/58-2-header-hamburger-logo-nom-actions.md`
- Scope :
  - Nouveau layout du Header (fixe, `position: sticky top: 0`, `z-index` approprié) :
    - **Zone gauche** : bouton hamburger (icône `Menu` / `X` de lucide-react) qui dispatch l'état sidebar
    - **Zone centre** : `<img>` logo + `<span>` APP_NAME
    - **Zone droite** : toggle dark/light (icône `Sun`/`Moon`) + composant `UserAvatar` cliquable
  - Supprimer l'affichage du rôle-badge et du bouton logout standalone
  - Relier le bouton hamburger au `SidebarContext` (story 58.3)
  - CSS `Header.css` refondu avec tokens design
  - i18n : aria-labels pour hamburger, avatar, toggle

### Story 58.3 — SidebarContext et Sidebar overlay à 3 états
- Fichier : `_bmad-output/implementation-artifacts/58-3-sidebar-context-et-overlay-3-etats.md`
- Scope :
  - Créer `frontend/src/state/SidebarContext.tsx` exposant :
    - `sidebarState: "hidden" | "expanded" | "icon-only"`
    - `openSidebar()`, `closeSidebar()`, `collapseSidebar()`
    - Transitions : `hidden → expanded`, `expanded → icon-only` (sur nav click), `icon-only → hidden` (sur hamburger)
  - Refondre `Sidebar.tsx` :
    - **État hidden** : `display: none`
    - **État expanded** : `position: fixed`, backdrop semi-transparent, chaque item = icône + label, fermeture sur clic backdrop
    - **État icon-only** : bande fixe 48px, icônes seules, tooltips sur hover
  - CSS `Sidebar.css` complet avec transitions (`transform`, `opacity`)
  - Appel à `collapseSidebar()` dans chaque NavLink onClick
  - Ajouter `SidebarProvider` dans `AppLayout.tsx`

### Story 58.4 — Composant UserAvatar (initiales ou image)
- Fichier : `_bmad-output/implementation-artifacts/58-4-composant-user-avatar.md`
- Scope :
  - Créer `frontend/src/components/ui/UserAvatar/UserAvatar.tsx` :
    - Props : `email: string`, `displayName?: string`, `avatarUrl?: string`, `size?: "sm" | "md" | "lg"`
    - Si `avatarUrl` fourni : `<img>` avec fallback sur initiales
    - Sinon : cercle mauve (`var(--color-primary)`) avec la 1re lettre de l'email en uppercase
    - Accessible (`role="img"`, `aria-label`)
  - Créer `UserAvatar.css` avec tokens design
  - Exporter via `@ui` barrel

### Story 58.5 — Menu utilisateur flottant (overlay au clic sur l'avatar)
- Fichier : `_bmad-output/implementation-artifacts/58-5-menu-utilisateur-flottant.md`
- Scope :
  - Créer `frontend/src/components/ui/UserMenu/UserMenu.tsx` :
    - Déclenché par clic sur `UserAvatar` dans le Header
    - Apparaît en overlay flottant (dropdown), fermeture sur clic extérieur ou `Escape`
    - **En-tête du menu** : `UserAvatar` (taille lg) + email et rôle de l'utilisateur
    - **Item 1** : "Modifier mon compte" → navigate `/settings`
    - **Item 2** : "Déconnexion" → `clearAccessToken()` + navigate `/login`
    - **Item 3** : "Paramètres" → navigate `/settings` (ou page dédiée future)
  - Créer `UserMenu.css`
  - i18n FR/EN/ES pour les labels
  - Accessible : `role="menu"`, `aria-expanded`, navigation clavier

### Story 58.6 — Intégration AppLayout, suppression BottomNav desktop et QA
- Fichier : `_bmad-output/implementation-artifacts/58-6-integration-applayout-et-qa.md`
- Scope :
  - Intégrer `SidebarProvider` dans `AppLayout.tsx`
  - `BottomNav` conservé pour mobile (≤ 768px), masqué sur desktop
  - Vérifier que le `main` content area s'adapte à l'état icon-only de la sidebar (margin-left ≈ 48px) et à hidden (margin-left: 0)
  - Tests Vitest/RTL :
    - Hamburger open/close/collapse cycle
    - UserMenu open/close, déconnexion, navigation
    - UserAvatar initiales vs image
    - Dark mode toggle
  - Vérification accessibilité (aria-labels, focus trap dans UserMenu, touche Escape)
  - Responsive (mobile / tablet / desktop)

## Fichiers impactés (aperçu global)

| Fichier | Action |
|---------|--------|
| `frontend/src/utils/constants.ts` | Ajout `APP_NAME` |
| `frontend/src/components/layout/Header.tsx` | Refonte complète |
| `frontend/src/components/layout/Header.css` | Nouveau (remplace styles App.css) |
| `frontend/src/components/layout/Sidebar.tsx` | Refonte complète |
| `frontend/src/components/layout/Sidebar.css` | Nouveau |
| `frontend/src/state/SidebarContext.tsx` | Nouveau |
| `frontend/src/components/ui/UserAvatar/UserAvatar.tsx` | Nouveau |
| `frontend/src/components/ui/UserAvatar/UserAvatar.css` | Nouveau |
| `frontend/src/components/ui/UserMenu/UserMenu.tsx` | Nouveau |
| `frontend/src/components/ui/UserMenu/UserMenu.css` | Nouveau |
| `frontend/src/layouts/AppLayout.tsx` | Intégration SidebarProvider |
| `frontend/src/App.css` | Nettoyage styles header/sidebar obsolètes |
| `frontend/src/i18n/common.ts` | Ajout labels menu utilisateur |

## Critères de Done (Epic)

- [ ] Le nom "Astrorizon" est une constante centrale et apparaît dans le Header
- [ ] Le logo est affiché dans le Header
- [ ] La sidebar fonctionne selon la machine à 3 états (hidden → expanded → icon-only → hidden)
- [ ] Le backdrop s'affiche et assombrit le contenu lors de l'état expanded
- [ ] L'avatar affiche les initiales (email) ou une image uploadée
- [ ] Le menu utilisateur flotte, est accessible au clavier et se ferme sur Escape/clic extérieur
- [ ] Le toggle dark/light est accessible depuis le Header
- [ ] La BottomNav mobile est conservée et fonctionnelle
- [ ] Tous les tests Vitest passent (≥ 1052 tests existants + nouveaux)
- [ ] Aucune régression TypeScript (`tsc --noEmit` clean)
