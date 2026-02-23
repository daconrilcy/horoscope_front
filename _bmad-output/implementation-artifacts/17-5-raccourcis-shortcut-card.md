# Story 17.5: Section Raccourcis — ShortcutCard

Status: review

## Story

As a utilisateur de l'application horoscope,
I want voir une section "Raccourcis" avec deux accès rapides (Chat astrologue et Tirage du jour) sur la page "Aujourd'hui",
So that je puisse lancer une action courante en un tap sans parcourir les menus.

## Contexte

La spec §7.3 définit la section "Raccourcis" : un titre de section + 2 cards en grille 2 colonnes. Chaque ShortcutCard affiche un badge d'icône coloré à gauche et un titre + sous-titre à droite. Les badges ont des couleurs spécifiques (vert pour Chat, orange pour Tirage).

**Prérequis** : Stories 17.1 (tokens CSS, icônes Lucide) et 17.2 (fond visible pour le glass).

## Scope

### In-Scope
- Création de `frontend/src/components/ShortcutCard.tsx`
- Création de `frontend/src/components/ShortcutsSection.tsx`
- Titre de section "Raccourcis" (18px, weight 650, margin-top 18px)
- Grille 2 colonnes, gap 12px
- Card Chat astrologue : badge `var(--badge-chat)`, icône `MessageCircle`, sous-titre "En ligne"
- Card Tirage du jour : badge `var(--badge-tirage)`, icône `Layers`, sous-titre "3 cartes"
- Background card : `--glass-2`, border `--glass-border`, radius 18px, padding 14px

### Out-of-Scope
- Statut "En ligne" dynamique depuis l'API
- Plus de 2 raccourcis ou personnalisation
- Animation au tap

## Acceptance Criteria

### AC1: Titre de section rendu correctement
**Given** la section Raccourcis est montée
**When** on inspecte le titre
**Then** "Raccourcis" est affiché en 18px, weight 650, couleur `--text-1`
**And** il a une marge supérieure de 18px

### AC2: Grille 2 colonnes correcte
**Given** les 2 ShortcutCards sont montées
**When** on observe le layout
**Then** les 2 cards sont côte à côte en 2 colonnes égales avec gap 12px

### AC3: Card "Chat astrologue" correcte
**Given** la card Chat est rendue
**When** on l'observe
**Then** un badge 40×40px radius 14px avec `var(--badge-chat)` est visible
**And** l'icône `MessageCircle` (size 20, strokeWidth 1.75) est dans le badge
**And** le titre "Chat astrologue" est en 15px weight 650
**And** le sous-titre "En ligne" est en 13px `--text-2`

### AC4: Card "Tirage du jour" correcte
**Given** la card Tirage est rendue
**When** on l'observe
**Then** un badge avec `var(--badge-tirage)` est visible
**And** l'icône `Layers` (size 20, strokeWidth 1.75) est dans le badge
**And** le titre "Tirage du jour" est en 15px weight 650
**And** le sous-titre "3 cartes" est en 13px `--text-2`

### AC5: Glassmorphism des cards
**Given** les cards sont montées
**When** on inspecte le style
**Then** leur background est `var(--glass-2)`, border `1px solid var(--glass-border)`
**And** radius 18px, padding 14px, `backdrop-filter: blur(14px)`

### AC6: Clic sur une card appelle le callback
**Given** une ShortcutCard avec `onClick` défini
**When** l'utilisateur clique
**Then** le callback `onClick` est appelé

### AC7: Thème dark/light correct
**Given** le thème dark est actif
**When** on observe les badges
**Then** les variables `--badge-chat` et `--badge-tirage` prennent leurs valeurs dark

## Tasks

- [x] Task 1: Créer `frontend/src/components/ShortcutCard.tsx` (AC: #3, #4, #5, #6)
  - [x] 1.1 Interface : `{ title: string; subtitle: string; icon: LucideIcon; badgeColor: string; onClick?: () => void }`
  - [x] 1.2 Layout card : flex, align-items center, gap 12px, glassmorphism
  - [x] 1.3 Badge 40×40px, radius 14px, background via prop `badgeColor`
  - [x] 1.4 Icône dans le badge : size 20, strokeWidth 1.75, centrée
  - [x] 1.5 Texte : titre 15px weight 650 + sous-titre 13px `--text-2`

- [x] Task 2: Créer `frontend/src/components/ShortcutsSection.tsx` (AC: #1, #2)
  - [x] 2.1 Titre "Raccourcis" : 18px, weight 650, margin-top 18px
  - [x] 2.2 Grid 2 colonnes, gap 12px, margin-top 12px
  - [x] 2.3 Deux `<ShortcutCard>` avec données statiques (spec §13)
  - [x] 2.4 Props : `onChatClick?: () => void; onTirageClick?: () => void`

- [x] Task 3: Styles CSS (AC: #1–#7)
  - [x] 3.1 Ajouter dans `App.css` sous `/* === ShortcutCard === */`
  - [x] 3.2 Classes : `.shortcut-card`, `.shortcut-card__badge`, `.shortcut-card__title`, `.shortcut-card__subtitle`
  - [x] 3.3 Classe `.shortcuts-section__title` et `.shortcuts-grid`

- [x] Task 4: Tests unitaires (AC: #1–#6)
  - [x] 4.1 Créer `frontend/src/tests/ShortcutCard.test.tsx`
  - [x] 4.2 Test rendu titre + sous-titre
  - [x] 4.3 Test clic → callback appelé
  - [x] 4.4 Test rendu de la section avec 2 cards

## Dev Notes

### Données statiques (spec §13)

```typescript
const SHORTCUTS = [
  {
    key: 'chat',
    title: 'Chat astrologue',
    subtitle: 'En ligne',
    icon: MessageCircle,
    badgeColor: 'var(--badge-chat)',
    path: '/chat',
  },
  {
    key: 'tirage',
    title: 'Tirage du jour',
    subtitle: '3 cartes',
    icon: Layers,
    badgeColor: 'var(--badge-tirage)',
    path: '/consultations',
  },
]
```

### CSS cible

```css
/* === ShortcutCard === */
.shortcut-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  background: var(--glass-2);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.shortcut-card__badge {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.shortcuts-section__title {
  font-size: 18px;
  font-weight: 650;
  color: var(--text-1);
  margin-top: 18px;
  margin-bottom: 0;
}
```

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §7.3, §13]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light)]

## Dev Agent Record

### Implementation Plan

1. Écriture des tests RED en premier (TDD) : 20 tests couvrant ShortcutCard et ShortcutsSection
2. Création de `ShortcutCard.tsx` : composant `<button>` avec badge coloré (via prop `badgeColor`) + texte
3. Création de `ShortcutsSection.tsx` : données statiques SHORTCUTS, grille 2 colonnes, callbacks optionnels
4. Ajout des styles CSS dans `App.css` : classes BEM conformes à la spec (glassmorphism, grid, typographie)

### Completion Notes

- Tous les ACs couverts par 20 tests unitaires (vitest + @testing-library/react)
- AC7 (thème dark/light) couvert par les tokens CSS déjà définis dans `theme.css`
- `ShortcutCard` utilise un `<button>` natif pour l'accessibilité clavier
- Pas de régression introduite : 813 tests passent, 3 échecs pré-existants dans `SettingsPage.test.tsx` (non liés à cette story)

## File List

- `frontend/src/components/ShortcutCard.tsx` (créé)
- `frontend/src/components/ShortcutsSection.tsx` (créé)
- `frontend/src/tests/ShortcutCard.test.tsx` (créé)
- `frontend/src/App.css` (modifié — section `/* === ShortcutCard === */` ajoutée)

## Change Log

- 2026-02-23: Story 17.5 implémentée — ShortcutCard + ShortcutsSection + CSS + 20 tests unitaires
