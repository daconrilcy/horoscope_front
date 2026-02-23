# Story 17.6: Section "Amour" — MiniInsightCard (3 cartes)

Status: review

## Story

As a utilisateur de l'application horoscope,
I want voir une section "Amour" sur la page "Aujourd'hui" avec 3 mini cartes thématiques (Amour, Travail, Énergie),
So que j'aie un aperçu rapide des 3 domaines clés de ma journée, chacun avec une icône colorée et un court message.

## Contexte

La spec §7.4 définit la section "Amour" : un en-tête de section avec un `ChevronRight` à droite, suivi de 3 mini cards en grille 3 colonnes. Chaque MiniInsightCard affiche une icône avec badge coloré en haut, un titre et une description sur 2 lignes max. Les badges ont des couleurs distinctes par domaine.

**Prérequis** : Stories 17.1 (tokens CSS, icônes Lucide) et 17.2 (fond).

## Scope

### In-Scope
- Création de `frontend/src/components/MiniInsightCard.tsx`
- Création de `frontend/src/components/AmourSection.tsx`
- En-tête de section : "Amour" à gauche + `ChevronRight` à droite, margin-top 18px
- Grille 3 colonnes égales, gap 12px
- Card Amour : badge `--badge-amour`, icône `Heart`, titre "Amour", desc "Balance dans ta relation"
- Card Travail : badge `--badge-travail`, icône `Briefcase`, titre "Travail", desc "Nouvelle opportunité à saisir"
- Card Énergie : badge `--badge-energie`, icône `Zap`, titre "Énergie", desc "Énergie haute, humeur positive"
- Background card : `--glass-2`, border `--glass-border`, radius 18px, padding 14px

### Out-of-Scope
- Connexion aux vraies données
- Navigation vers une page "Amour" détaillée (le ChevronRight est visuel uniquement pour ce MVP)
- Autres domaines (Finances, Santé...)

## Acceptance Criteria

### AC1: En-tête de section correct
**Given** la section Amour est montée
**When** on inspecte l'en-tête
**Then** "Amour" est affiché à gauche en 18px weight 650 `--text-1`
**And** une icône `ChevronRight` (size 18, strokeWidth 1.75, `--text-2`) est à droite
**And** l'en-tête a un margin-top de 18px

### AC2: Grille 3 colonnes correcte
**Given** les 3 MiniInsightCards sont montées
**When** on observe le layout
**Then** les 3 cards sont en 3 colonnes égales avec gap 12px

### AC3: Card "Amour" correcte
**Given** la card Amour est rendue
**When** on l'observe
**Then** un badge 36×36px radius 14px avec `var(--badge-amour)` est visible
**And** l'icône `Heart` (size 18, strokeWidth 1.75) est dans le badge
**And** le titre "Amour" est en 14px weight 650
**And** la description "Balance dans ta relation" est en 13px `--text-2`, max 2 lignes

### AC4: Card "Travail" correcte
**Given** la card Travail est rendue
**When** on l'observe
**Then** un badge avec `var(--badge-travail)` est visible, icône `Briefcase`
**And** titre "Travail", description "Nouvelle opportunité à saisir"

### AC5: Card "Énergie" correcte
**Given** la card Énergie est rendue
**When** on l'observe
**Then** un badge avec `var(--badge-energie)` est visible, icône `Zap`
**And** titre "Énergie", description "Énergie haute, humeur positive"

### AC6: Glassmorphism des cards
**Given** les cards sont montées
**When** on inspecte le style
**Then** `var(--glass-2)` background, `1px solid var(--glass-border)` border, radius 18px, padding 14px
**And** `backdrop-filter: blur(14px)` appliqué

### AC7: Thème dark/light correct
**Given** le thème dark est actif
**When** on observe les badges
**Then** `--badge-amour`, `--badge-travail`, `--badge-energie` prennent leurs valeurs dark

## Tasks

- [x] Task 1: Créer `frontend/src/components/MiniInsightCard.tsx` (AC: #3, #4, #5, #6)
  - [x] 1.1 Interface : `{ title: string; description: string; icon: LucideIcon; badgeColor: string }`
  - [x] 1.2 Layout vertical : badge en haut, titre, description
  - [x] 1.3 Badge 36×36px, radius 14px, background via prop
  - [x] 1.4 Icône dans le badge : size 18, strokeWidth 1.75, centrée
  - [x] 1.5 Titre : 14px, weight 650, `--text-1`
  - [x] 1.6 Description : 13px, `--text-2`, `overflow: hidden`, clamp 2 lignes (`-webkit-line-clamp: 2`)

- [x] Task 2: Créer `frontend/src/components/AmourSection.tsx` (AC: #1, #2)
  - [x] 2.1 En-tête flex : "Amour" à gauche + `ChevronRight` à droite, margin-top 18px
  - [x] 2.2 Grid 3 colonnes, gap 12px, margin-top 12px
  - [x] 2.3 Trois `<MiniInsightCard>` avec données statiques (spec §13)
  - [x] 2.4 Prop optionnelle `onSectionClick?: () => void` pour le ChevronRight

- [x] Task 3: Styles CSS (AC: #1–#7)
  - [x] 3.1 Ajouter dans `App.css` sous `/* === MiniInsightCard === */`
  - [x] 3.2 Classes : `.mini-card`, `.mini-card__badge`, `.mini-card__title`, `.mini-card__desc`
  - [x] 3.3 `.section-header` : flex, justify-content space-between, align-items center
  - [x] 3.4 `.mini-cards-grid` : grid 3 colonnes, gap 12px

- [x] Task 4: Tests unitaires (AC: #1–#6)
  - [x] 4.1 Créer `frontend/src/tests/MiniInsightCard.test.tsx`
  - [x] 4.2 Test rendu titre + description
  - [x] 4.3 Test que le badge est rendu avec la couleur correcte
  - [x] 4.4 Test rendu de la section avec 3 cards et l'en-tête

## Dev Notes

### Données statiques (spec §13)

```typescript
const AMOUR_INSIGHTS = [
  {
    key: 'amour',
    title: 'Amour',
    description: 'Balance dans ta relation',
    icon: Heart,
    badgeColor: 'var(--badge-amour)',
  },
  {
    key: 'travail',
    title: 'Travail',
    description: 'Nouvelle opportunité à saisir',
    icon: Briefcase,
    badgeColor: 'var(--badge-travail)',
  },
  {
    key: 'energie',
    title: 'Énergie',
    description: 'Énergie haute, humeur positive',
    icon: Zap,
    badgeColor: 'var(--badge-energie)',
  },
]
```

### Structure JSX indicative

```tsx
export function MiniInsightCard({ title, description, icon: Icon, badgeColor }) {
  return (
    <div className="mini-card">
      <div className="mini-card__badge" style={{ background: badgeColor }}>
        <Icon size={18} strokeWidth={1.75} />
      </div>
      <p className="mini-card__title">{title}</p>
      <p className="mini-card__desc">{description}</p>
    </div>
  )
}
```

### CSS cible

```css
/* === MiniInsightCard === */
.mini-card {
  padding: 14px;
  border-radius: 18px;
  background: var(--glass-2);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.mini-card__badge {
  width: 36px;
  height: 36px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.mini-card__title {
  font-size: 14px;
  font-weight: 650;
  color: var(--text-1);
  margin: 0 0 4px;
}

.mini-card__desc {
  font-size: 13px;
  color: var(--text-2);
  margin: 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.mini-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
}

.section-header__title {
  font-size: 18px;
  font-weight: 650;
  color: var(--text-1);
  margin: 0;
}
```

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §7.4, §13]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light), docs/interfaces/ChatGPT Image 23 févr. 2026, 15_12_17.png (dark)]

## Dev Agent Record

### Implementation Plan

- Task 1: Création de `MiniInsightCard.tsx` — composant générique avec interface `{ title, description, icon: LucideIcon, badgeColor }`, structure div/badge/titre/desc
- Task 2: Création de `AmourSection.tsx` — section avec en-tête flex (titre + ChevronRight) et grille 3 colonnes avec données AMOUR_INSIGHTS statiques
- Task 3: Ajout CSS dans `App.css` — section `/* === MiniInsightCard === */` avec classes `.mini-card`, `.mini-card__badge`, `.mini-card__title`, `.mini-card__desc`, `.mini-cards-grid`, `.section-header`, `.section-header__title`
- Task 4: Tests dans `MiniInsightCard.test.tsx` — 22 tests couvrant MiniInsightCard (AC3-6) et AmourSection (AC1-5)

### Completion Notes

✅ Tous les critères d'acceptation AC1 à AC7 sont couverts :
- AC1: En-tête flex avec `.section-header`, titre `.section-header__title` (18px, weight 650), `ChevronRight` (size 18, strokeWidth 1.75, color var(--text-2)), margin-top 18px via CSS
- AC2: Grid `.mini-cards-grid` en `repeat(3, 1fr)`, gap 12px
- AC3: Card Amour — badge `var(--badge-amour)`, icône `Heart`, titre/desc conformes
- AC4: Card Travail — badge `var(--badge-travail)`, icône `Briefcase`, titre/desc conformes
- AC5: Card Énergie — badge `var(--badge-energie)`, icône `Zap`, titre/desc conformes
- AC6: `.mini-card` avec `background: var(--glass-2)`, `border: 1px solid var(--glass-border)`, `border-radius: 18px`, `padding: 14px`, `backdrop-filter: blur(14px)`
- AC7: Tokens `--badge-amour/travail/energie` définis en light ET dark dans `theme.css` (existant depuis story 17.1)

Tests: 22/22 passent. Aucune régression (les 3 échecs `SettingsPage.test.tsx` étaient pré-existants).

## File List

- `frontend/src/components/MiniInsightCard.tsx` (nouveau)
- `frontend/src/components/AmourSection.tsx` (nouveau)
- `frontend/src/App.css` (modifié — ajout section `/* === MiniInsightCard === */`)
- `frontend/src/tests/MiniInsightCard.test.tsx` (nouveau)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié — statut 17-6: review)

## Change Log

- 2026-02-23: Implémentation story 17.6 — création MiniInsightCard, AmourSection, styles CSS, 22 tests unitaires
