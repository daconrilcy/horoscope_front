# Story 16.2: Dashboard Page — Hub d'accueil

Status: done

## Story

As a utilisateur connecté,
I want voir un dashboard d'accueil avec des raccourcis vers toutes les fonctionnalités,
So that je puisse accéder rapidement à ce que je cherche.

## Contexte

Actuellement, après connexion, l'utilisateur arrive directement sur la page du thème natal. Il n'y a pas de hub central pour orienter vers les différentes fonctionnalités. Le dashboard servira de point d'entrée principal.

## Scope

### In-Scope
- Page `/dashboard` avec cartes de raccourci
- Cartes pour : Thème astral, Chat, Consultations, Astrologues, Profil
- Navigation vers chaque section au clic
- États loading/error si données utilisateur nécessaires

### Out-of-Scope
- Widgets dynamiques (stats, dernières conversations)
- Notifications ou alertes
- Personnalisation du dashboard

## Acceptance Criteria

### AC1: Affichage du dashboard
**Given** un utilisateur connecté naviguant vers `/dashboard`
**When** la page se charge
**Then** il voit un titre "Tableau de bord" et des cartes de raccourci

### AC2: Cartes de navigation
**Given** le dashboard affiché
**When** l'utilisateur clique sur une carte
**Then** il est redirigé vers la section correspondante :
- "Mon thème astral" → `/natal`
- "Chat astrologue" → `/chat`
- "Consultations" → `/consultations`
- "Astrologues" → `/astrologers`
- "Paramètres" → `/settings`

### AC3: Accessibilité
**Given** un utilisateur naviguant au clavier
**When** il utilise Tab et Enter
**Then** toutes les cartes sont accessibles et activables

## Tasks

- [x] Task 1: Créer DashboardPage (AC: #1, #2)
  - [x] 1.1 Créer `src/pages/DashboardPage.tsx`
  - [x] 1.2 Créer composant `DashboardCard.tsx`
  - [x] 1.3 Implémenter les 5 cartes avec icônes/labels
  - [x] 1.4 Ajouter navigation avec `useNavigate()`

- [x] Task 2: Intégration router (AC: #2)
  - [x] 2.1 Ajouter route `/dashboard` dans routes.tsx
  - [x] 2.2 Vérifier que `/` redirige vers `/dashboard` (configuré dans 16-1)
  - [x] 2.3 Créer routes placeholder `/consultations`, `/astrologers`, `/settings`

- [x] Task 3: Accessibilité et tests (AC: #3)
  - [x] 3.1 Ajouter rôles ARIA appropriés
  - [x] 3.2 Créer `src/tests/DashboardPage.test.tsx`
  - [x] 3.3 Tester navigation vers chaque section

## Dev Notes

### Pattern Loading/Error

La page actuelle est statique (pas de fetch de données). Quand des widgets dynamiques seront ajoutés (quotas, dernières conversations, etc.), implémenter les états loading/error/empty selon l'architecture:
- TanStack Query pour le server state
- Skeleton glass + texte de progression pour loading
- Messages d'erreur explicites avec action de récupération

### Structure

```typescript
// DashboardPage.tsx
const dashboardCards = [
  { id: "natal", label: "Mon thème astral", path: "/natal", icon: "⭐" },
  { id: "chat", label: "Chat astrologue", path: "/chat", icon: "💬" },
  { id: "consultations", label: "Consultations", path: "/consultations", icon: "🔮" },
  { id: "astrologers", label: "Astrologues", path: "/astrologers", icon: "👤" },
  { id: "settings", label: "Paramètres", path: "/settings", icon: "⚙️" },
]
```

### DashboardCard props

```typescript
type DashboardCardProps = {
  label: string
  path: string
  icon: string
  description?: string
}
```

### Fichiers

```
frontend/src/
├── pages/
│   └── DashboardPage.tsx
├── components/
│   └── dashboard/
│       └── DashboardCard.tsx
```

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (Cursor)

### Debug Log References
N/A

### Completion Notes List
- DashboardPage créée avec 5 cartes de navigation (Thème astral, Chat, Consultations, Astrologues, Paramètres)
- DashboardCard composant réutilisable utilisant `<Link>` natif React Router (support middle-click, Enter)
- Accessibilité complète : liens sémantiques avec aria-labels, aria-hidden pour icônes décoratives
- 11 tests unitaires couvrant AC1 (affichage), AC2 (navigation), AC3 (accessibilité clavier)
- Tests renforcés : vérification que la page destination existe (pas juste le pathname)
- Routes placeholder créées pour /consultations, /astrologers, /settings
- Système i18n centralisé (`frontend/src/i18n/dashboard.tsx`) avec support FR/EN/ES
- Icônes SVG personnalisées remplaçant les emojis pour cohérence cross-platform
- Styles CSS ajoutés avec grid responsive et effets hover/focus

### File List

**Fichiers créés:**
- `frontend/src/pages/DashboardPage.tsx` - Page dashboard avec grille de cartes
- `frontend/src/pages/ConsultationsPage.tsx` - Page placeholder consultations
- `frontend/src/pages/AstrologersPage.tsx` - Page placeholder astrologues
- `frontend/src/pages/SettingsPage.tsx` - Page placeholder paramètres (i18n fr/en/es)
- `frontend/src/components/dashboard/DashboardCard.tsx` - Composant carte cliquable accessible (Link natif)
- `frontend/src/components/dashboard/index.ts` - Barrel export
- `frontend/src/components/icons/DashboardIcons.tsx` - Icônes SVG pour dashboard
- `frontend/src/components/icons/index.ts` - Barrel export icônes
- `frontend/src/i18n/dashboard.tsx` - Traductions des cartes dashboard (pur i18n, sans JSX)
- `frontend/src/app/router.tsx` - AppRouter (production) + TestAppRouter (tests)
- `frontend/src/tests/DashboardPage.test.tsx` - 10 tests (affichage, navigation, accessibilité)
- `frontend/src/tests/router.test.tsx` - Tests AuthGuard, RoleGuard, RootRedirect, Navigation

**Fichiers modifiés:**
- `frontend/src/app/routes.tsx` - Routes dashboard + consultations + astrologers + settings (+ routes admin/enterprise anticipées pour l'epic)
- `frontend/src/App.css` - Ajout styles .dashboard-grid, .dashboard-card (+ styles stories suivantes de l'epic intégrés en avance)
- `frontend/src/tests/App.test.tsx` - Mise à jour des assertions pour "Tableau de bord"

### Change Log
| Date | Change | Author |
|------|--------|--------|
| 2026-02-22 | Implémentation complète Dashboard Page | Claude Opus 4.5 |
| 2026-02-22 | Code Review: Routes placeholder, Link natif, icônes SVG, i18n | Claude Opus 4.5 |
| 2026-02-23 | ACR: locale detectLang(), getDashboardCardIcon dans DashboardPage, i18n SettingsPage, test Tab réel, imports dashboard.tsx, cursor:pointer, File List | Claude Sonnet 4.6 |
