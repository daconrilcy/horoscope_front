# Story 17.8: TodayPage — Assemblage, Route et Tests

Status: todo

## Story

As a utilisateur authentifié de l'application horoscope,
I want accéder à la page "Aujourd'hui / Horoscope" comme page principale de l'application,
So que je voie immédiatement mon horoscope du jour, mes raccourcis et mes insights dans un design premium, dès ma connexion.

## Contexte

Cette story est la story d'intégration finale de l'Epic 17. Elle assemble les 5 composants créés dans les stories 17.3 à 17.7 en une `TodayPage` cohérente, câble la route, et s'assure que tout fonctionne ensemble par des tests d'intégration.

La spec §10.3 décrit l'ordre exact de composition :
1. `<TodayHeader />`
2. `<HeroHoroscopeCard />`
3. `<ShortcutsSection />`
4. `<AmourSection />`
5. `<BottomNav />` (fixé, via AppShell)

Actuellement, `/dashboard` pointe vers `DashboardPage.tsx`. Selon la stratégie décidée à la story 17.1 (via `nav.ts`), l'item "Aujourd'hui" pointe vers `/dashboard`. La `TodayPage` **remplace** `DashboardPage` comme contenu de la route `/dashboard`.

**Prérequis** : Stories 17.1 à 17.7 complétées.

## Scope

### In-Scope
- Création de `frontend/src/pages/TodayPage.tsx` assemblant les 5 composants
- Mise à jour de la route `/dashboard` dans `frontend/src/app/routes.tsx` → `<TodayPage />`
- Passage du `userName` de l'utilisateur connecté au `<TodayHeader />`
- Callbacks de navigation depuis `HeroHoroscopeCard` (vers `/natal`) et `ShortcutsSection` (vers `/chat`, `/consultations`)
- Page scrollable avec `padding: 22px 18px 110px` (spec §5.1 + espace bottom nav)
- Tests d'intégration : rendu complet de la page + navigation

### Out-of-Scope
- Données horoscope dynamiques (API) — statiques pour ce sprint
- Sign dynamique basé sur la date de naissance de l'utilisateur — "Verseau" statique pour ce sprint
- Page `/today` séparée — `/dashboard` est réutilisé
- Animations page transition

## Acceptance Criteria

### AC1: TodayPage assemblée dans le bon ordre
**Given** l'utilisateur est authentifié et navigue vers `/dashboard`
**When** la page est chargée
**Then** les blocs apparaissent dans cet ordre exact :
1. Header ("Aujourd'hui" + "Horoscope" + avatar)
2. HeroHoroscopeCard (chip Verseau, headline, CTA, "Version détaillée")
3. Section Raccourcis (titre + 2 cards)
4. Section Amour (en-tête + 3 mini cards)

### AC2: Données statiques conformes à la spec
**Given** la page est rendue
**When** on inspecte le contenu
**Then** le chip affiche "♒ Verseau • 23 fév."
**And** le headline est "Ta journée s'éclaircit après 14h."
**And** les raccourcis sont "Chat astrologue / En ligne" et "Tirage du jour / 3 cartes"
**And** les mini cards affichent "Amour / Balance dans ta relation", "Travail / Nouvelle opportunité à saisir", "Énergie / Énergie haute, humeur positive"

### AC3: Navigation depuis HeroHoroscopeCard fonctionnelle
**Given** l'utilisateur est sur `/dashboard`
**When** il clique sur "Lire en 2 min"
**Then** il est redirigé vers `/natal`

**Given** l'utilisateur est sur `/dashboard`
**When** il clique sur "Version détaillée"
**Then** il est redirigé vers `/natal`

### AC4: Navigation depuis ShortcutsSection fonctionnelle
**Given** l'utilisateur est sur `/dashboard`
**When** il clique sur "Chat astrologue"
**Then** il est redirigé vers `/chat`

**Given** l'utilisateur est sur `/dashboard`
**When** il clique sur "Tirage du jour"
**Then** il est redirigé vers `/consultations`

### AC5: Avatar avec nom utilisateur
**Given** l'utilisateur connecté a un `username` dans le contexte d'auth
**When** la page est chargée
**Then** l'avatar du `TodayHeader` affiche les initiales du nom de l'utilisateur

### AC6: Page scrollable sur mobile
**Given** la page est affichée sur un écran mobile (390px)
**When** le contenu dépasse la hauteur de l'écran
**Then** la page est scrollable verticalement
**And** le bottom nav reste en `position: fixed` en bas et n'est pas scrollé

### AC7: DashboardPage.tsx conservée (ne pas supprimer)
**Given** la refactorisation est en cours
**When** la route `/dashboard` est mise à jour vers `TodayPage`
**Then** `DashboardPage.tsx` est conservé dans le projet (ne pas supprimer, peut servir ultérieurement)
**And** les tests existants de `DashboardPage.test.tsx` ne doivent pas régresser

### AC8: Tests passent
**Given** la TodayPage est créée
**When** on exécute `npm test` dans `frontend/`
**Then** tous les tests passent (hors échecs préexistants connus)

## Tasks

- [ ] Task 1: Créer `frontend/src/pages/TodayPage.tsx` (AC: #1, #2, #5, #6)
  - [ ] 1.1 Importer et composer : `TodayHeader`, `HeroHoroscopeCard`, `ShortcutsSection`, `AmourSection`
  - [ ] 1.2 Récupérer `userName` depuis le hook d'auth existant (ex. `useAuthUser()` ou équivalent)
  - [ ] 1.3 Données statiques inline : `VERSEAU_DATA` (sign, date, headline) conformes spec §13
  - [ ] 1.4 Container page : `padding: 22px 18px 110px` (spec §5.1), `min-height: 100dvh`
  - [ ] 1.5 Callbacks de navigation avec `useNavigate()` (react-router-dom)

- [ ] Task 2: Mettre à jour la route `/dashboard` (AC: #1, #7)
  - [ ] 2.1 Dans `frontend/src/app/routes.tsx`, importer `TodayPage`
  - [ ] 2.2 Remplacer `<DashboardPage />` par `<TodayPage />` pour la route `{ path: '/dashboard', element: <TodayPage /> }`
  - [ ] 2.3 Conserver `DashboardPage` importé si nécessaire pour d'autres usages, sinon laisser le fichier intact

- [ ] Task 3: Tests d'intégration de TodayPage (AC: #1, #2, #3, #4, #5, #8)
  - [ ] 3.1 Créer `frontend/src/tests/TodayPage.test.tsx`
  - [ ] 3.2 Tester le rendu du header ("Aujourd'hui", "Horoscope")
  - [ ] 3.3 Tester le rendu du chip "♒ Verseau"
  - [ ] 3.4 Tester le rendu du headline
  - [ ] 3.5 Tester le rendu de la section Raccourcis (2 cards)
  - [ ] 3.6 Tester le rendu de la section Amour (3 mini cards)
  - [ ] 3.7 Tester clic "Lire en 2 min" → navigate vers `/natal`
  - [ ] 3.8 Tester clic "Chat astrologue" → navigate vers `/chat`

- [ ] Task 4: Vérifier non-régression globale (AC: #7, #8)
  - [ ] 4.1 Lancer `npm test` dans `frontend/` — vérifier que les tests `DashboardPage.test.tsx`, `router.test.tsx` et autres passent toujours
  - [ ] 4.2 Vérification visuelle en dev : scrollabilité, bottom nav fixe, thème light/dark

## Dev Notes

### Données statiques (spec §13)

```typescript
// TodayPage.tsx
const HERO_DATA = {
  sign: '♒',
  signName: 'Verseau',
  date: '23 fév.',
  headline: "Ta journée s'éclaircit après 14h.",
} as const
```

### Récupération du userName

Le projet utilise un hook d'auth existant. Vérifier le contexte d'auth actuel :
- Chercher dans `frontend/src/api/authMe.ts` ou le store d'auth
- Fallback : `userName="Utilisateur"` si non disponible

```typescript
// Exemple selon le pattern existant du projet
const { user } = useAuth() // ou équivalent
const userName = user?.username ?? 'U'
```

### Structure TodayPage

```tsx
export function TodayPage() {
  const navigate = useNavigate()
  const { user } = useAuth() // adapter selon le hook existant
  const userName = user?.username ?? 'Utilisateur'

  return (
    <div className="today-page">
      <TodayHeader userName={userName} />
      <HeroHoroscopeCard
        {...HERO_DATA}
        onReadFull={() => navigate('/natal')}
        onReadDetailed={() => navigate('/natal')}
      />
      <ShortcutsSection
        onChatClick={() => navigate('/chat')}
        onTirageClick={() => navigate('/consultations')}
      />
      <AmourSection />
    </div>
  )
}
```

### CSS page

```css
/* === TodayPage === */
.today-page {
  padding: 22px 18px 110px;
  min-height: 100dvh;
}
```

### Arborescence finale de l'Epic 17

```
frontend/src/
├── components/
│   ├── AmourSection.tsx          ← 17.6
│   ├── ConstellationSVG.tsx      ← 17.4
│   ├── HeroHoroscopeCard.tsx     ← 17.4
│   ├── MiniInsightCard.tsx       ← 17.6
│   ├── ShortcutCard.tsx          ← 17.5
│   ├── ShortcutsSection.tsx      ← 17.5
│   ├── StarfieldBackground.tsx   ← 17.2
│   ├── TodayHeader.tsx           ← 17.3
│   └── layout/
│       └── BottomNav.tsx         ← 17.7 (refactorisé)
├── pages/
│   └── TodayPage.tsx             ← 17.8
├── state/
│   └── ThemeProvider.tsx         ← 17.2
├── styles/
│   └── theme.css                 ← 17.1
├── tests/
│   ├── TodayPage.test.tsx        ← 17.8
│   ├── TodayHeader.test.tsx      ← 17.3
│   ├── HeroHoroscopeCard.test.tsx← 17.4
│   ├── ShortcutCard.test.tsx     ← 17.5
│   ├── MiniInsightCard.test.tsx  ← 17.6
│   └── BottomNavPremium.test.tsx ← 17.7
└── ui/
    ├── icons.tsx                 ← 17.1
    ├── nav.ts                    ← 17.1
    └── index.ts                  ← 17.1
```

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §10.3, §13]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light), docs/interfaces/ChatGPT Image 23 févr. 2026, 15_12_17.png (dark)]
