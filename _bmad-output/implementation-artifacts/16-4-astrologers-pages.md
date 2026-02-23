# Story 16.4: Catalogue et Profil Astrologues

Status: done

## Story

As a utilisateur,
I want parcourir un catalogue d'astrologues et voir leur profil détaillé,
So that je puisse choisir l'astrologue qui me correspond pour démarrer une conversation.

## Contexte

Actuellement, il n'y a pas de page dédiée aux astrologues. L'utilisateur ne peut pas parcourir, comparer ou choisir son astrologue. Cette story ajoute :
- Une page catalogue `/astrologers` avec grille de vignettes
- Une page profil `/astrologers/:id` avec détails et CTAs

**Note:** Si l'API astrologues n'existe pas encore côté backend, utiliser des données mock en attendant.

## Scope

### In-Scope
- Page `/astrologers` avec grille de vignettes
- Page `/astrologers/:id` avec profil détaillé
- Composants : AstrologerCard, AstrologerProfileHeader
- CTA : "Démarrer conversation"
- Mock data si API non disponible (données en français uniquement)
- Navigation vers chat avec astrologue sélectionné

### Out-of-Scope
- API backend astrologues (existante ou à créer séparément)
- Filtres avancés (par spécialité, langue, etc.)
- Système de favoris
- Disponibilité temps réel
- CTA "Consultation thématique" (future story)

## Acceptance Criteria

### AC1: Catalogue astrologues
**Given** un utilisateur sur `/astrologers`
**When** la page se charge
**Then** il voit une grille de vignettes d'astrologues
**And** chaque vignette affiche : avatar, nom, spécialités, style

### AC2: Navigation vers profil
**Given** le catalogue affiché
**When** l'utilisateur clique sur une vignette
**Then** il est redirigé vers `/astrologers/:id`

### AC3: Profil astrologue
**Given** un utilisateur sur `/astrologers/1`
**When** la page se charge
**Then** il voit le profil complet : avatar, bio, spécialités, langues, style

### AC4: Démarrer conversation
**Given** un profil astrologue affiché
**When** l'utilisateur clique "Démarrer une conversation"
**Then** il est redirigé vers `/chat` avec cet astrologue pré-sélectionné

### AC5: Empty state
**Given** aucun astrologue disponible
**When** la page catalogue se charge
**Then** un message "Aucun astrologue disponible" est affiché

## Tasks

- [x] Task 1: Créer API client astrologers (AC: #1, #3)
  - [x] 1.1 Créer `src/api/astrologers.ts`
  - [x] 1.2 Définir types `Astrologer`, `AstrologerProfile`
  - [x] 1.3 Créer hooks `useAstrologers()`, `useAstrologer(id)`
  - [x] 1.4 Implémenter mock data fallback

- [x] Task 2: Créer composants (AC: #1, #3)
  - [x] 2.1 Créer `src/features/astrologers/components/AstrologerCard.tsx`
  - [x] 2.2 Créer `src/features/astrologers/components/AstrologerProfileHeader.tsx`
  - [x] 2.3 Créer `src/features/astrologers/components/AstrologerGrid.tsx`

- [x] Task 3: Créer pages (AC: #1, #2, #3, #4)
  - [x] 3.1 Créer `src/pages/AstrologersPage.tsx`
  - [x] 3.2 Créer `src/pages/AstrologerProfilePage.tsx`
  - [x] 3.3 Ajouter routes dans routes.tsx
  - [x] 3.4 Implémenter navigation vers chat

- [x] Task 4: Tests (AC: #1, #2, #5)
  - [x] 4.1 Test rendu grille astrologues
  - [x] 4.2 Test navigation vers profil
  - [x] 4.3 Test CTA démarrer conversation
  - [x] 4.4 Test empty state

## Dev Notes

### Types

```typescript
// types/astrologer.ts
export type Astrologer = {
  id: string
  name: string
  avatar_url: string
  specialties: string[]
  style: string
  bio_short: string
}

export type AstrologerProfile = Astrologer & {
  bio_full: string
  languages: string[]
  experience_years: number
}
```

### Mock data

```typescript
// api/astrologers.ts
const MOCK_ASTROLOGERS: Astrologer[] = [
  {
    id: "1",
    name: "Luna Céleste",
    avatar_url: "/avatars/luna.jpg",
    specialties: ["Thème natal", "Transits", "Relations"],
    style: "Bienveillant et direct",
    bio_short: "Astrologue depuis 15 ans, spécialisée en astrologie relationnelle."
  },
  {
    id: "2", 
    name: "Orion Mystique",
    avatar_url: "/avatars/orion.jpg",
    specialties: ["Carrière", "Événements", "Tarot"],
    style: "Analytique et précis",
    bio_short: "Expert en astrologie prévisionnelle et choix de carrière."
  },
  // ... autres astrologues
]
```

### Structure fichiers

```
frontend/src/
├── api/
│   └── astrologers.ts
├── features/
│   └── astrologers/
│       ├── components/
│       │   ├── AstrologerCard.tsx
│       │   ├── AstrologerGrid.tsx
│       │   └── AstrologerProfileHeader.tsx
│       └── index.ts
├── pages/
│   ├── AstrologersPage.tsx
│   └── AstrologerProfilePage.tsx
└── types/
    └── astrologer.ts
```

### Navigation vers chat avec astrologue

```typescript
// AstrologerProfilePage.tsx
const navigate = useNavigate()

const handleStartConversation = () => {
  // Query param avec encodage sécurisé
  navigate(`/chat?astrologerId=${encodeURIComponent(astrologer.id)}`)
}
```

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
N/A

### Completion Notes List
- Implémentation complète du catalogue d'astrologues avec grille de vignettes
- Page profil astrologue avec tous les détails (bio, spécialités, langues, expérience)
- Mock data fallback si l'API backend n'existe pas encore
- CTA "Démarrer une conversation" avec navigation vers /chat?astrologerId=X
- Empty state affiché quand aucun astrologue disponible
- 19 tests couvrant tous les ACs: 15 tests UI (AstrologersPage.test.tsx) + 4 tests validation ID (astrologers-validation.test.ts)
- Tous les tests frontend passent sans régression

### File List
- frontend/src/api/astrologers.ts (nouveau)
- frontend/src/types/astrologer.ts (nouveau)
- frontend/src/i18n/astrologers.ts (nouveau)
- frontend/src/features/astrologers/components/AstrologerCard.tsx (nouveau)
- frontend/src/features/astrologers/components/AstrologerProfileHeader.tsx (nouveau)
- frontend/src/features/astrologers/components/AstrologerGrid.tsx (nouveau)
- frontend/src/features/astrologers/index.ts (nouveau)
- frontend/src/features/chat/components/AstrologerDetailPanel.tsx (modifié - intégration astrologue sélectionné)
- frontend/src/pages/AstrologersPage.tsx (nouveau)
- frontend/src/pages/AstrologerProfilePage.tsx (nouveau)
- frontend/src/pages/ChatPage.tsx (modifié - gestion astrologerId)
- frontend/src/app/routes.tsx (modifié)
- frontend/src/App.css (modifié - styles astrologues + avatar img)
- frontend/src/tests/AstrologersPage.test.tsx (nouveau)
- frontend/src/tests/astrologers-validation.test.ts (nouveau - tests unitaires isValidAstrologerId)
- frontend/src/tests/ChatPage.test.tsx (modifié - mock useAstrologer)
- frontend/src/tests/DashboardPage.test.tsx (modifié - correction test i18n)
- frontend/src/tests/chat/ChatComponents.test.tsx (modifié - ajout beforeEach i18n)
- frontend/src/tests/router.test.tsx (modifié - matchers i18n pour empty state chat)

### Change Log
- 2026-02-22: Implémentation initiale + 16 passes de code review adversarial
  - **Architecture**: Types centralisés (src/types/astrologer.ts), cache React Query
  - **Sécurité**: Validation ID (isValidAstrologerId avec JSDoc), encodeURIComponent
  - **i18n**: Textes internationalisés (fr/en/es) via src/i18n/astrologers.ts
  - **Accessibilité**: aria-labels, aria-hidden, alt textes
  - **Tests**: 19 tests (15 UI + 4 validation ID), mock via vi.importActual
  - **Intégration**: ChatPage + AstrologerDetailPanel connectés via query param
- 2026-02-23: Code review fixes (round 2):
  - Fix: H1 — `USE_MOCK_FALLBACK = true` hardcodé → `import.meta.env.DEV` (actif seulement en dev, pas en production)
  - Fix: H1 — Dead code supprimé dans les blocs catch de `getAstrologers()` et `getAstrologer()` (branche `AstrologersApiError.status === 404` inaccessible)
  - Fix: M1 — `lang = "fr"` default retiré de `AstrologerCard`, `AstrologerGrid`, `AstrologerProfileHeader` → `detectLang()` appelé en interne (cohérence avec le reste de l'app)
  - Fix: M2 — `<h3>` remplacé par `<span className="astrologer-card-name">` dans `AstrologerCard` (HTML5 content model valide)
  - Fix: M3 — `role="img"` contradictoire retiré des spans emoji avec `aria-hidden="true"` dans `AstrologerCard`, `AstrologerProfileHeader`, `AstrologerDetailPanel`
  - Fix: M4 — `handleStartConversation` dans `AstrologerProfilePage` utilise `profile.id` (ID canonique validé) au lieu de `id ?? ""` (URL param)
  - Fix: L1 — Assertion `getByAltText("Avatar de Luna Céleste")` ajoutée dans le test "displays avatar, name, specialties, and style" (AC1 complet)
