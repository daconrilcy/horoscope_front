# Story 17.3: Header composant — Kicker, H1 et Avatar

Status: done

## Story

As a utilisateur de l'application horoscope,
I want voir en haut de la page "Aujourd'hui" un header lisible avec la mention "Aujourd'hui", le titre "Horoscope" et mon avatar,
So that j'identifie immédiatement la section et que l'application me reconnaisse visuellement.

## Contexte

La spec §7.1 définit le header de la page "Aujourd'hui" : kicker centré "Aujourd'hui" + H1 40px "Horoscope" + avatar rond 40×40 en haut à droite. Ce composant est distinct du `Header.tsx` existant (`frontend/src/components/layout/Header.tsx`) qui est une barre desktop avec logout.

Ce nouveau `TodayHeader.tsx` est spécifique à la page Today et ne remplace pas le layout global.

**Prérequis** : Story 17.1 (tokens CSS disponibles).

## Scope

### In-Scope
- Création de `frontend/src/components/TodayHeader.tsx`
- Kicker "Aujourd'hui" (13px, `--text-2`, letter-spacing 0.2px)
- H1 "Horoscope" (40px, weight 650, line-height 1.05, letter-spacing -0.5px, `--text-1`)
- Avatar rond 40×40 en haut à droite (initiales de l'utilisateur ou image)
- Padding-top `6px` sur le container header
- Alignement : kicker + H1 centrés ; avatar positionné en `absolute` top-right

### Out-of-Scope
- Navigation (dans BottomNav, story 17.7)
- Notifications bell icon (epic ultérieur)
- Avatar upload/modification (Settings)
- Version mobile ≠ desktop — layout fixe 390px mobile-first

## Acceptance Criteria

### AC1: Kicker rendu correctement
**Given** le composant `TodayHeader` est affiché
**When** on inspecte l'élément texte "Aujourd'hui"
**Then** il est centré horizontalement
**And** sa taille est 13px, son opacité correspond à `--text-2`
**And** son `letter-spacing` est 0.2px

### AC2: H1 "Horoscope" rendu correctement
**Given** le composant `TodayHeader` est affiché
**When** on inspecte l'élément H1
**Then** son contenu est "Horoscope"
**And** sa taille est 40px, son poids 650, son line-height 1.05, son letter-spacing -0.5px
**And** sa couleur est `--text-1`

### AC3: Avatar rond positionné en haut à droite
**Given** l'utilisateur est connecté avec un profil
**When** on affiche `TodayHeader`
**Then** un avatar 40×40px est positionné en haut à droite du header
**And** l'avatar est rond (`border-radius: 999px`)
**And** il a un border `1px solid rgba(255,255,255,0.4)` translucide
**And** si l'utilisateur n'a pas de photo : les initiales du prénom sont affichées sur fond `--chip`

### AC4: Structure HTML sémantique
**Given** le composant est rendu
**When** on inspecte le DOM
**Then** le titre "Horoscope" est un `<h1>`
**And** le kicker est un `<p>` ou `<span>` avec rôle purement décoratif/informatif

### AC5: Thème dark/light respecté
**Given** le thème dark est actif
**When** on affiche `TodayHeader`
**Then** les couleurs `--text-1` et `--text-2` basculent vers leurs valeurs dark
**And** l'avatar conserve son aspect (fond `--chip` dark = `#4F3F71`)

## Tasks

- [x] Task 1: Créer `frontend/src/components/TodayHeader.tsx` (AC: #1, #2, #3, #4)
  - [x] 1.1 Définir l'interface `TodayHeaderProps { userName?: string; avatarUrl?: string }`
  - [x] 1.2 Implémenter le container : `position: relative`, `padding-top: 6px`, `text-align: center`
  - [x] 1.3 Kicker : `<p>` "Aujourd'hui" avec les styles de l'overline (13px, `--text-2`, letter-spacing 0.2px)
  - [x] 1.4 H1 : "Horoscope" avec styles exacts (40px, font-weight 650, line-height 1.05, letter-spacing -0.5px, `--text-1`)
  - [x] 1.5 Avatar : `<div>` 40×40px `border-radius: 999px`, positionné en `absolute` à `top: 0; right: 0`
  - [x] 1.6 Si `avatarUrl` fourni : `<img>` avec `object-fit: cover`; sinon : initiales centrées sur fond `--chip`

- [x] Task 2: Styles CSS (AC: #1, #2, #3, #5)
  - [x] 2.1 Ajouter les styles dans `App.css` sous la section `/* === TodayHeader === */`
  - [x] 2.2 Utiliser uniquement des variables CSS `--text-1`, `--text-2`, `--chip` (pas de couleurs hardcodées)

- [x] Task 3: Test unitaire (AC: #1, #2, #3, #4)
  - [x] 3.1 Créer `frontend/src/tests/TodayHeader.test.tsx`
  - [x] 3.2 Tester le rendu du kicker "Aujourd'hui"
  - [x] 3.3 Tester le rendu du H1 "Horoscope"
  - [x] 3.4 Tester l'avatar avec `avatarUrl` fourni (img présente)
  - [x] 3.5 Tester l'avatar sans `avatarUrl` (initiales affichées)

## Dev Notes

### Structure JSX indicative

```tsx
export function TodayHeader({ userName = 'U', avatarUrl }: TodayHeaderProps) {
  const initials = userName.slice(0, 2).toUpperCase()

  return (
    <header className="today-header">
      <p className="today-header__kicker">Aujourd'hui</p>
      <h1 className="today-header__title">Horoscope</h1>
      <div className="today-header__avatar" aria-label={`Profil de ${userName}`}>
        {avatarUrl
          ? <img src={avatarUrl} alt={userName} />
          : <span>{initials}</span>
        }
      </div>
    </header>
  )
}
```

### CSS cible

```css
/* === TodayHeader === */
.today-header {
  position: relative;
  padding-top: 6px;
  text-align: center;
}

.today-header__kicker {
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.2px;
  color: var(--text-2);
  margin: 0;
}

.today-header__title {
  font-size: 40px;
  font-weight: 650;
  line-height: 1.05;
  letter-spacing: -0.5px;
  color: var(--text-1);
  margin: 0;
}

.today-header__avatar {
  position: absolute;
  top: 0;
  right: 0;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  overflow: hidden;
  background: var(--chip);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-1);
}

.today-header__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §7.1]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light)]

## Dev Agent Record

### Implementation Plan

Implémentation red-green-refactor :
1. Tests créés en premier (phase RED) — échec confirmé car composant absent
2. Composant `TodayHeader.tsx` créé (phase GREEN) — 11 tests passent
3. CSS ajouté dans `App.css` sous `/* === TodayHeader === */` avec variables CSS uniquement
4. Revue de code (Adversarial) : corrections appliquées pour accessibilité, résilience et robustesse.

### Completion Notes

- Composant `TodayHeader` implémenté selon la spec Dev Notes de la story
- Props : `userName?: string` (défaut `"U"`), `avatarUrl?: string`
- Initiales améliorées : Prénom + Nom (ex: "John Doe" -> "JD")
- Resilience : Fallback automatique vers les initiales si l'image (`avatarUrl`) échoue au chargement.
- Accessibilité : `role="img"` sur le container d'avatar, `alt=""` sur l'image interne pour éviter la redondance.
- Thème dark/light respecté via variables CSS.
- 13 tests unitaires (couvrant les edge cases et le fallback d'image), 0 régression introduite.

### Debug Log

| Date | Issue | Resolution |
|------|-------|------------|
| 2026-02-23 | Tests SettingsPage échouaient déjà avant cette story | Confirmé pré-existant via git stash — non lié à TodayHeader |
| 2026-02-23 | Revue de code : initiales simplistes | Implémenté split multi-mots |
| 2026-02-23 | Revue de code : accessibilité avatar | Ajout role="img" et gestion aria-label/alt |
| 2026-02-23 | Revue de code : fragilité image | Ajout state imgError et event onError |

## File List

- `frontend/src/components/TodayHeader.tsx` (created)
- `frontend/src/tests/TodayHeader.test.tsx` (created)
- `frontend/src/App.css` (modified — ajout section `/* === TodayHeader === */`)
- `_bmad-output/implementation-artifacts/17-3-header-composant.md` (modified — status, tasks, Dev Agent Record)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified — status: done)

## Change Log

- 2026-02-23 : Implémentation story 17.3 — composant TodayHeader, styles CSS, 13 tests unitaires
