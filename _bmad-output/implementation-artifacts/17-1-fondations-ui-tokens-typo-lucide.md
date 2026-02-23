# Story 17.1: Fondations UI — Tokens CSS, Typographie et lucide-react

Status: done

## Story

As a développeur front-end implémentant la page "Aujourd'hui",
I want disposer d'un système de tokens de design complet (couleurs, typographie, ombres) et de la librairie d'icônes Lucide,
So that toutes les stories suivantes de l'Epic 17 puissent référencer des variables CSS cohérentes et des icônes unifiées sans duplications.

## Contexte

La page d'accueil "Aujourd'hui / Horoscope" (maquettes Light Pastel Premium + Dark Cosmic) nécessite un socle de design rigoureux avant toute implémentation de composants. La spec `docs/interfaces/horoscope-ui-spec.md` définit deux palettes complètes (§2), des tokens CSS (§3), une échelle typographique précise (§4) et un mapping d'icônes (§9).

Actuellement :
- `frontend/src/styles/` n'existe pas ; les variables CSS sont dispersées dans `App.css` (39 KB)
- `lucide-react` n'est pas installé (les icônes actuelles sont des emojis/SVG custom)
- Aucun fichier centralisé ne définit les tokens "premium" (glass, chip, CTA, nav)

Cette story pose les fondations sur lesquelles toutes les stories 17.2 à 17.8 s'appuieront.

## Scope

### In-Scope
- Création de `frontend/src/styles/theme.css` avec les variables CSS `:root` (light) et `.dark` (dark)
- Application de la police system `-apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, system-ui`
- Installation de `lucide-react` via npm
- Création de `frontend/src/ui/icons.tsx` — barrel export des icônes utilisées dans l'Epic 17
- Création de `frontend/src/ui/nav.ts` — configuration des items de la bottom nav (label, icône, path)
- Import de `theme.css` dans `frontend/src/main.tsx` (avant `index.css`)

### Out-of-Scope
- Implémentation des composants (stories 17.3–17.8)
- Suppression des variables CSS existantes dans `App.css` (refactoring progressif)
- Thème dark mode automatique (détection OS) — géré en story 17.2

## Acceptance Criteria

### AC1: Tokens CSS disponibles et isolés
**Given** le fichier `frontend/src/styles/theme.css` existe
**When** un composant utilise `var(--glass)` ou `var(--cta-l)`
**Then** la valeur provient du fichier `theme.css` (palette light)
**And** en ajoutant la classe `dark` sur `<html>`, les variables basculent automatiquement vers la palette dark cosmic

### AC2: Tokens couvrent la spec complète
**Given** le fichier `theme.css` est ouvert
**When** on vérifie les variables définies
**Then** toutes les variables suivantes existent dans `:root` ET dans `.dark` :
- `--text-1`, `--text-2`, `--text-3`
- `--bg-top`, `--bg-mid`, `--bg-bot`
- `--glass`, `--glass-2`, `--glass-border`
- `--cta-l`, `--cta-r`
- `--chip`
- `--nav-glass`, `--nav-border`
- `--shadow-card`, `--shadow-nav`

### AC3: Police system appliquée
**Given** l'application est chargée dans un navigateur
**When** on inspecte la propriété `font-family` de `<html>` ou `<body>`
**Then** la police est `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, system-ui, sans-serif`

### AC4: lucide-react installé et fonctionnel
**Given** `lucide-react` est listé dans `frontend/package.json`
**When** on importe `{ ChevronRight } from 'lucide-react'`
**Then** le composant se rend sans erreur dans l'application

### AC5: Barrel icons.tsx et nav.ts créés
**Given** le fichier `frontend/src/ui/icons.tsx` existe
**When** on l'importe
**Then** il exporte au minimum : `ChevronRight`, `CalendarDays`, `MessageCircle`, `Star`, `Layers`, `User`, `Heart`, `Briefcase`, `Zap`, `Settings`, `Bell`, `Loader2`

**Given** le fichier `frontend/src/ui/nav.ts` existe
**When** on consulte le tableau `navItems`
**Then** il contient 5 entrées : Aujourd'hui (`/dashboard`), Chat (`/chat`), Thème (`/natal`), Tirages (`/consultations`), Profil (`/settings/account`) — chacune avec `key`, `label`, `icon`, `path`

### AC6: Aucune régression sur les tests existants
**Given** les tokens et la police sont ajoutés
**When** on exécute `npm test` dans `frontend/`
**Then** tous les tests existants (≥ 0 avant cette story) continuent de passer

## Tasks

- [x] Task 1: Installer lucide-react (AC: #4)
  - [x] 1.1 Exécuter `npm install lucide-react` dans `frontend/`
  - [x] 1.2 Vérifier l'entrée dans `frontend/package.json` et `package-lock.json`

- [x] Task 2: Créer `frontend/src/styles/theme.css` (AC: #1, #2)
  - [x] 2.1 Créer le répertoire `frontend/src/styles/`
  - [x] 2.2 Implémenter `:root { ... }` avec les 21 variables de la palette Light (16 base + 5 badges, valeurs exactes issues de la spec §2.1 + §3)
  - [x] 2.3 Implémenter `.dark { ... }` avec les 21 variables de la palette Dark Cosmic (§2.2 + §3)
  - [x] 2.4 Ajouter la règle `html, body { font-family: ... }` (§4.2)

- [x] Task 3: Intégrer `theme.css` dans l'application (AC: #1, #3)
  - [x] 3.1 Importer `./styles/theme.css` dans `frontend/src/main.tsx` (premier import CSS, avant `index.css`)

- [x] Task 4: Créer `frontend/src/ui/icons.tsx` (AC: #5)
  - [x] 4.1 Re-exporter depuis `lucide-react` les icônes du mapping §9 : navigation, hero, raccourcis, mini cards, système
  - [x] 4.2 Documenter via commentaire le groupement (Navigation / Hero / Shortcuts / System)

- [x] Task 5: Créer `frontend/src/ui/nav.ts` (AC: #5)
  - [x] 5.1 Définir le type `NavItem { key: string; label: string; icon: LucideIcon; path: string }`
  - [x] 5.2 Exporter `navItems: NavItem[]` avec les 5 entrées de la bottom nav
  - [x] 5.3 Les `path` doivent correspondre aux routes existantes ou prévues (story 17.8)

- [x] Task 6: Vérifier la non-régression (AC: #6)
  - [x] 6.1 Lancer `npm test` dans `frontend/` et s'assurer que tous les tests passent

## Dev Notes

### Valeurs exactes des tokens (depuis spec §3)

```css
:root {
  /* Text */
  --text-1: #1E1B2E;
  --text-2: rgba(30,27,46,0.72);
  --text-3: rgba(30,27,46,0.55);

  /* Background */
  --bg-top: #FDF5F8;
  --bg-mid: #D9CBE1;
  --bg-bot: #D8D0EE;

  /* Glass surfaces */
  --glass: rgba(255,255,255,0.55);
  --glass-2: rgba(255,255,255,0.38);
  --glass-border: rgba(255,255,255,0.65);

  /* Accent / CTA */
  --cta-l: #866CD0;
  --cta-r: #A190ED;

  /* Chips */
  --chip: #C6B9E5;

  /* Nav */
  --nav-glass: rgba(255,255,255,0.55);
  --nav-border: rgba(255,255,255,0.65);

  /* Shadows */
  --shadow-card: 0 18px 40px rgba(20,20,40,0.12);
  --shadow-nav:  0 10px 30px rgba(20,20,40,0.18);

  /* Badge accents (§2.1) */
  --badge-chat: #E1F0EA;
  --badge-tirage: #F8CAA5;
  --badge-amour: #EBA4C9;
  --badge-travail: #AABEEF;
  --badge-energie: #F6D2A7;
}

.dark {
  --text-1: rgba(245,245,255,0.92);
  --text-2: rgba(235,235,245,0.72);
  --text-3: rgba(235,235,245,0.55);

  --bg-top: #181626;
  --bg-mid: #0F0E18;
  --bg-bot: #2A2436;

  --glass: rgba(255,255,255,0.08);
  --glass-2: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.12);

  --cta-l: #37226E;
  --cta-r: #5839B8;

  --chip: #4F3F71;

  --nav-glass: rgba(255,255,255,0.08);
  --nav-border: rgba(255,255,255,0.12);

  --shadow-card: 0 18px 40px rgba(0,0,0,0.45);
  --shadow-nav:  0 10px 30px rgba(0,0,0,0.55);

  /* Badge accents (§2.2) */
  --badge-chat: #E4F2EC;
  --badge-tirage: #D5946A;
  --badge-amour: #E779B4;
  --badge-travail: #A8ACEF;
  --badge-energie: #E5B270;
}
```

### Icônes Lucide à exporter (icons.tsx)

```typescript
export type { LucideIcon } from 'lucide-react'

export {
  // Navigation (bottom nav)
  CalendarDays,   // Aujourd'hui → /dashboard
  MessageCircle,  // Chat → /chat
  Star,           // Thème natal → /natal
  Layers,         // Tirages → /consultations
  User,           // Profil → /settings/account

  // Hero card
  ChevronRight,   // CTA + section headers

  // Mini cards (raccourcis)
  Heart,          // Amour
  Briefcase,      // Travail
  Zap,            // Énergie

  // System
  Settings,
  Bell,
  Shield,
  Moon,
  LogOut,
  Loader2,
  FileText,
} from 'lucide-react'
```

### Import order dans main.tsx

```typescript
import './styles/theme.css'  // tokens en premier
import './index.css'          // reset/globals ensuite
```

### Arborescence cible

```
frontend/src/
├── styles/
│   └── theme.css         ← NOUVEAU (21 variables CSS)
└── ui/
    ├── index.ts           ← NOUVEAU (barrel export)
    ├── icons.tsx          ← NOUVEAU (17 icônes + type)
    └── nav.ts             ← NOUVEAU (5 navItems)
```

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §2, §3, §4, §9]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light), docs/interfaces/ChatGPT Image 23 févr. 2026, 15_12_17.png (dark)]

## File List

### New Files
- `frontend/src/styles/theme.css` — Tokens CSS pour les thèmes Light et Dark Cosmic (21 variables × 2 thèmes + typographie)
- `frontend/src/styles/backgrounds.css` — Styles pour les fonds premium (gradients, noise, starfield) séparés du socle de tokens
- `frontend/src/ui/icons.tsx` — Barrel export des icônes Lucide + type LucideIcon
- `frontend/src/ui/nav.ts` — Configuration des 5 items de la bottom navigation (paths corrigés)
- `frontend/src/ui/index.ts` — Barrel export centralisé pour ui/
- `frontend/src/tests/ui-icons.test.tsx` — Tests unitaires pour icons.tsx (33 tests)
- `frontend/src/tests/ui-nav.test.ts` — Tests unitaires pour nav.ts (5 tests)
- `frontend/src/tests/theme-tokens.test.ts` — Tests de validation des tokens CSS light et dark (46 tests)
- `frontend/src/tests/ui-barrel.test.ts` — Tests pour le barrel ui/index.ts (4 tests)

### Modified Files
- `frontend/package.json` — Ajout de la dépendance `lucide-react@^0.575.0`
- `frontend/package-lock.json` — Lock file mis à jour
- `frontend/src/main.tsx` — Import ordonné : `theme.css` -> `backgrounds.css` -> `index.css`
- `frontend/src/tests/SettingsPage.test.tsx` — Corrigé les sélecteurs de liens ambigus (IDs vs Roles)
- `frontend/src/tests/AppBgStyles.test.ts` — Mis à jour pour lire les styles depuis les deux fichiers CSS

## Dev Agent Record

### Implementation Notes
- `lucide-react@^0.575.0` installé avec succès
- `theme.css` créé avec les 21 variables CSS pour `:root` (Light Pastel Premium) et `.dark` (Dark Cosmic), conformément à la spec §3
- Variables badges ajoutées : `--badge-chat`, `--badge-tirage`, `--badge-amour`, `--badge-travail`, `--badge-energie` (spec §2.1, §2.2)
- Typographie system stack appliquée via `html, body { font-family: ... }` (spec §4.2)
- `backgrounds.css` isolé pour les effets visuels complexes (gradients, noise, starfield), garantissant une séparation nette entre tokens et implémentation visuelle.
- `icons.tsx` exporte 16 icônes Lucide groupées par catégorie + type `LucideIcon` (mapping spec §9)
- `nav.ts` définit le type `NavItem` et exporte `navItems` avec les 5 entrées de navigation (paths corrigés vers routes existantes)
- Import order dans `main.tsx` respecté : `theme.css` avant `index.css` (corrigé après review)

### Code Review Fixes (2026-02-23)
- **HIGH-1 (Import Order)**: Corrigé l'ordre d'import dans `main.tsx` (`theme.css` avant `index.css`) pour garantir la priorité des tokens.
- **HIGH-2 (Paths)**: Corrigé les paths dans `nav.ts` (`/today` → `/dashboard`, `/tirages` → `/consultations`, `/profile` → `/settings/account`).
- **HIGH-3 (Badges)**: Ajouté les 5 variables CSS des badges dans `:root` et `.dark` conformément à la spec §2.
- **MEDIUM-1 (Test Quality)**: Réécrit `theme-tokens.test.ts` pour effectuer une analyse statique réelle du fichier `theme.css` (vérification de la présence des 21 variables) au lieu d'utiliser des valeurs hardcodées.
- **MEDIUM-2 (Barrel)**: Exporté le type `LucideIcon` depuis `icons.tsx` et créé `ui/index.ts` pour une consommation propre.
- **MEDIUM-3 (Scope Isolation)**: Déplacé les styles de background vers `backgrounds.css` pour respecter le périmètre "Fondations" et éviter le scope creep dans le fichier de tokens.
- **MEDIUM-4 (Fix Pre-existing)**: Corrigé les tests de `SettingsPage.test.tsx` qui échouaient à cause de liens ambigus (multiples liens "Abonnement", "Compte" dans le DOM de test).
- **LOW-1 (Documentation)**: Aligné le décompte des icônes (16) et des variables (21) dans la documentation technique.

### Test Results
- **840 tests passent / 840 total** (Succès 100%, y compris les correctifs de tests préexistants).
- `theme-tokens.test.ts` (46 tests) et `AppBgStyles.test.ts` (46 tests) valident désormais les fichiers CSS réels.
- Aucune régression introduite ; tous les tests de navigation (`SettingsPage`) sont désormais stables.

## Change Log

| Date | Description |
|------|-------------|
| 2026-02-23 | Story 17-1 implémentée : tokens CSS (theme.css), installation lucide-react, barrel icons.tsx, configuration nav.ts |
| 2026-02-23 | Code review #1 : corrections HIGH-1, HIGH-2, MEDIUM-1, MEDIUM-3 appliquées |
| 2026-02-23 | Code review #2 : mise à jour AC5 paths, ajout test theme-tokens.test.ts, correction Dev Notes |
| 2026-02-23 | Code review #3 : ajout ui/index.ts barrel, tests dark theme (44), tests barrel (4), mise à jour Dev Notes badges |
| 2026-02-23 | Code review #4 : corrections documentaires (arborescence, count variables 21, test count 663) |
| 2026-02-23 | Code review #5 : correction File List et Implementation Notes (18 → 21 variables) |
