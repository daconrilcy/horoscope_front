# Story 17.7: Bottom Navigation — Glass Pill

Status: todo

## Story

As a utilisateur de l'application horoscope,
I want une barre de navigation en bas de l'écran avec un effet "glass pill" premium (flou, translucide, arrondi),
So que la navigation entre les sections soit élégante, accessible et conforme au design "Dark Cosmic / Light Pastel" des maquettes.

## Contexte

La spec §8 décrit précisément la bottom nav : positionnée en `fixed` à `bottom: 16px`, s'étendant de `left: 16px` à `right: 16px`, avec un effet glassmorphism (`backdrop-filter: blur(14px)`), `border-radius: 24px`, 5 items avec icônes Lucide et labels, et un état actif subtil.

Le `BottomNav.tsx` existant (`frontend/src/components/layout/BottomNav.tsx`) doit être **remplacé** par cette version premium — il utilise actuellement des styles hardcodés non conformes à la spec.

**Prérequis** : Stories 17.1 (tokens CSS, `navItems` de `ui/nav.ts`), 17.2 (thème).

## Scope

### In-Scope
- Refactorisation complète de `frontend/src/components/layout/BottomNav.tsx`
- `position: fixed`, `bottom: 16px`, `left: 16px`, `right: 16px`
- `border-radius: 24px`, `padding: 10px`
- `backdrop-filter: blur(14px)`, `background: var(--nav-glass)`, `border: 1px solid var(--nav-border)`
- `box-shadow: var(--shadow-nav)`
- 5 items depuis `navItems` (ui/nav.ts) : Aujourd'hui, Chat, Thème, Tirages, Profil
- Icônes Lucide : 24px, strokeWidth 1.75
- Labels : 12px, weight 500, `--text-2`
- État actif : background `rgba(134,108,208,0.18)` (light) / `rgba(150,110,255,0.18)` (dark), icône + label plus contrastés
- Utilisation de `useLocation()` pour détecter l'item actif

### Out-of-Scope
- Badge de notification sur les items
- Animation de transition entre onglets
- Safe-area iOS (PWA)

## Acceptance Criteria

### AC1: Positionnement fixed glass pill
**Given** la page est chargée
**When** on observe la bottom nav
**Then** elle est en `position: fixed`, `bottom: 16px`, `left: 16px`, `right: 16px`
**And** son `border-radius` est 24px, son `padding` est 10px
**And** `backdrop-filter: blur(14px)` est appliqué
**And** son background est `var(--nav-glass)`, border `1px solid var(--nav-border)`
**And** son ombre est `var(--shadow-nav)`

### AC2: 5 items de navigation présents
**Given** la bottom nav est rendue
**When** on liste les items
**Then** 5 items sont présents : Aujourd'hui, Chat, Thème, Tirages, Profil
**And** chaque item a une icône Lucide (24px, strokeWidth 1.75) et un label (12px)

### AC3: Icônes correctes par item
**Given** la bottom nav est rendue
**When** on observe chaque item
**Then** Aujourd'hui → `CalendarDays`, Chat → `MessageCircle`, Thème → `Star`, Tirages → `Layers`, Profil → `User`

### AC4: État actif correct
**Given** l'utilisateur est sur la route `/dashboard`
**When** on observe l'item "Aujourd'hui"
**Then** il a un fond subtil (`rgba(134,108,208,0.18)` en light, `rgba(150,110,255,0.18)` en dark)
**And** son icône et son label sont plus contrastés (`--text-1`)

**Given** l'utilisateur est sur une autre route
**When** on observe l'item "Aujourd'hui"
**Then** il n'a pas de fond de sélection et son label est `--text-2`

### AC5: Navigation fonctionnelle
**Given** l'utilisateur clique sur un item de la bottom nav
**When** le clic est effectué
**Then** il est redirigé vers la route correspondante
**And** l'item cliqué devient actif

### AC6: Thème dark/light correct
**Given** le thème dark est actif
**When** on observe la bottom nav
**Then** `--nav-glass` et `--nav-border` prennent leurs valeurs dark
**And** l'état actif utilise `rgba(150,110,255,0.18)`

### AC7: Aucune régression sur les pages existantes
**Given** la BottomNav est refactorisée
**When** on navigue dans l'application (dashboard, chat, natal, settings)
**Then** la navigation fonctionne sans régression

## Tasks

- [ ] Task 1: Refactoriser `frontend/src/components/layout/BottomNav.tsx` (AC: #1–#6)
  - [ ] 1.1 Remplacer les styles hardcodés par les tokens CSS
  - [ ] 1.2 Utiliser `navItems` depuis `../../ui/nav` (ou `ui/nav.ts`)
  - [ ] 1.3 Utiliser `useLocation()` de react-router-dom pour détecter l'item actif
  - [ ] 1.4 Utiliser `<Link>` de react-router-dom pour la navigation
  - [ ] 1.5 Appliquer les classes actif/inactif conditionnellement
  - [ ] 1.6 Icônes : `size={24}`, `strokeWidth={1.75}`
  - [ ] 1.7 Supprimer tout `backgroundColor` hardcodé

- [ ] Task 2: Mettre à jour les styles CSS (AC: #1, #4, #6)
  - [ ] 2.1 Dans `App.css`, section `/* === BottomNav === */`, appliquer spec §8
  - [ ] 2.2 Classe `.bottom-nav` : positionnement fixed + glassmorphism
  - [ ] 2.3 Classe `.bottom-nav__item` : flex 1, column, align center
  - [ ] 2.4 Classe `.bottom-nav__item--active` : background actif light + dark via `.dark`
  - [ ] 2.5 Classe `.bottom-nav__label` : 12px, weight 500, couleur via state actif

- [ ] Task 3: Mettre à jour les tests (AC: #2, #3, #4, #5, #7)
  - [ ] 3.1 Mettre à jour `frontend/src/tests/router.test.tsx` si nécessaire
  - [ ] 3.2 Créer `frontend/src/tests/BottomNavPremium.test.tsx`
  - [ ] 3.3 Test : 5 items présents avec labels corrects
  - [ ] 3.4 Test : item actif détecté via la route courante
  - [ ] 3.5 Test : clic sur un item déclenche la navigation
  - [ ] 3.6 Vérifier que les tests existants sur BottomNav passent toujours

## Dev Notes

### Structure JSX refactorisée

```tsx
import { Link, useLocation } from 'react-router-dom'
import { navItems } from '../../ui/nav'

export function BottomNav() {
  const { pathname } = useLocation()

  return (
    <nav className="bottom-nav" aria-label="Navigation principale">
      {navItems.map(({ key, label, icon: Icon, path }) => {
        const isActive = pathname === path || pathname.startsWith(path + '/')
        return (
          <Link
            key={key}
            to={path}
            className={`bottom-nav__item ${isActive ? 'bottom-nav__item--active' : ''}`}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon size={24} strokeWidth={1.75} />
            <span className="bottom-nav__label">{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
```

### CSS cible (spec §8)

```css
/* === BottomNav === */
.bottom-nav {
  position: fixed;
  bottom: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  border-radius: 24px;
  padding: 10px;
  background: var(--nav-glass);
  border: 1px solid var(--nav-border);
  box-shadow: var(--shadow-nav);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  z-index: 100;
}

.bottom-nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 6px 4px;
  border-radius: 14px;
  text-decoration: none;
  color: var(--text-2);
  transition: background 0.15s ease;
}

.bottom-nav__item--active {
  background: rgba(134, 108, 208, 0.18);
  color: var(--text-1);
}

.dark .bottom-nav__item--active {
  background: rgba(150, 110, 255, 0.18);
}

.bottom-nav__label {
  font-size: 12px;
  font-weight: 500;
}
```

### Note sur la détection de route active

Pour `/dashboard` (Aujourd'hui) : `pathname === '/dashboard'`
Pour `/chat` : `pathname === '/chat' || pathname.startsWith('/chat/')`
Pour `/natal` : `pathname === '/natal'`
Pour `/consultations` : `pathname === '/consultations' || pathname.startsWith('/consultations/')`
Pour `/settings/account` : `pathname.startsWith('/settings')`

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §8, §9.1]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light), docs/interfaces/ChatGPT Image 23 févr. 2026, 15_12_17.png (dark)]
