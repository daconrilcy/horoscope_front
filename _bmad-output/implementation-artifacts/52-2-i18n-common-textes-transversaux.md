# Story 52.2: Créer i18n/common.ts — textes transversaux Header, actions génériques, états

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux un fichier `i18n/common.ts` centralisant tous les textes transversaux du produit (navigation globale, actions génériques, états de chargement),
afin que Header, HeroHoroscopeCard et les messages d'état partagés n'aient plus de strings hardcodées.

## Acceptance Criteria

1. Le fichier `frontend/src/i18n/common.ts` existe avec `CommonTranslation` et les traductions FR, EN, ES.
2. `CommonTranslation` couvre : actions génériques (Fermer, Annuler, Confirmer, Réessayer, Retour, Suivant), états (Chargement, Erreur, Vide), Header (Se déconnecter, Utilisateur, titre app), HeroHoroscopeCard (boutons d'action).
3. Une fonction `commonTranslations(lang): CommonTranslation` est exportée.
4. `Header.tsx` utilise `commonTranslations(lang)` pour "Se déconnecter" et "Utilisateur".
5. `HeroHoroscopeCard.tsx` utilise `commonTranslations(lang)` pour "Lire en 2 min" et "Version détaillée".
6. Les composants `<Modal>` (story 50.5) et `<EmptyState>` (story 50.7) utilisent les clés `common` pour leurs textes par défaut (ou acceptent des props string si déjà traités en props).
7. Tous les tests existants passent.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire `HeroHoroscopeCard.tsx` pour inventorier ses strings (AC: 2, 5)
  - [ ] Lister tous les textes hardcodés (boutons, aria-labels, titres)

- [ ] Tâche 2 : Créer `frontend/src/i18n/common.ts` (AC: 1, 2, 3)
  - [ ] Définir `CommonTranslation` avec toutes les sections identifiées
  - [ ] Traductions FR, EN, ES pour chaque clé
  - [ ] Exporter `commonTranslations(lang: AstrologyLang): CommonTranslation`

- [ ] Tâche 3 : Migrer `Header.tsx` (AC: 4)
  - [ ] Ajouter `const lang = detectLang()` et `const t = commonTranslations(lang)`
  - [ ] Remplacer "Se déconnecter" → `t.header.logout`
  - [ ] Remplacer `"Utilisateur"` (fallback rôle) → `t.header.defaultRole`
  - [ ] Remplacer `"Horoscope"` (titre app) → `t.header.appTitle` ou constante

- [ ] Tâche 4 : Migrer `HeroHoroscopeCard.tsx` (AC: 5)
  - [ ] Ajouter la détection de langue
  - [ ] Remplacer les boutons hardcodés par les clés `t.heroCard.*`
  - [ ] Remplacer les aria-labels hardcodés si présents

- [ ] Tâche 5 : Vérifier les composants UI de l'Epic 50 (AC: 6)
  - [ ] `Modal.tsx` (story 50.5) : si le bouton ✕ a un aria-label hardcodé → utiliser `t.actions.close`
  - [ ] `EmptyState.tsx` (story 50.7) : si texte par défaut hardcodé → utiliser `t.states.empty`
  - [ ] **Ne pas bloquer sur cette tâche si les composants Epic 50 ne sont pas encore créés** — noter pour review post-50

- [ ] Tâche 6 : Validation
  - [ ] `npm run test`
  - [ ] Vérifier Header visuellement (logout button, rôle affiché)
  - [ ] Vérifier HeroHoroscopeCard boutons d'action

## Dev Notes

### Contexte technique

**Prérequis** : Story 52.1 peut être en cours en parallèle. Aucun prérequis bloquant.

### Inventaire des strings à couvrir dans CommonTranslation

**Header.tsx** (lignes 32, 40) :
```
"Utilisateur"           → t.header.defaultRole   (fallback quand role = "user")
"Se déconnecter"        → t.header.logout
"Horoscope"             → t.header.appTitle       (titre de l'app dans le header)
```

**HeroHoroscopeCard.tsx** (lignes ~85, ~95) :
```
"Lire en 2 min"         → t.heroCard.readShort
"Version détaillée"     → t.heroCard.readDetailed
```

**Actions génériques** (pour Modal, EmptyState, etc.) :
```
"Fermer"                → t.actions.close
"Annuler"               → t.actions.cancel
"Confirmer"             → t.actions.confirm
"Réessayer"             → t.actions.retry
"Retour"                → t.actions.back
"Suivant"               → t.actions.next
"Supprimer"             → t.actions.delete
"Enregistrer"           → t.actions.save
```

**États visuels** :
```
"Chargement..."         → t.states.loading
"Erreur"                → t.states.error
"Aucun résultat"        → t.states.empty
"Aucune donnée disponible" → t.states.noData
```

### Structure de `i18n/common.ts`

```typescript
import type { AstrologyLang } from "./astrology"

export interface CommonTranslation {
  header: {
    appTitle: string
    logout: string
    defaultRole: string
  }
  heroCard: {
    readShort: string
    readDetailed: string
  }
  actions: {
    close: string
    cancel: string
    confirm: string
    retry: string
    back: string
    next: string
    delete: string
    save: string
  }
  states: {
    loading: string
    error: string
    empty: string
    noData: string
  }
}

const translations: Record<AstrologyLang, CommonTranslation> = {
  fr: {
    header: { appTitle: "Horoscope", logout: "Se déconnecter", defaultRole: "Utilisateur" },
    heroCard: { readShort: "Lire en 2 min", readDetailed: "Version détaillée" },
    actions: { close: "Fermer", cancel: "Annuler", confirm: "Confirmer", retry: "Réessayer", back: "Retour", next: "Suivant", delete: "Supprimer", save: "Enregistrer" },
    states: { loading: "Chargement...", error: "Erreur", empty: "Aucun résultat", noData: "Aucune donnée disponible" },
  },
  en: { ... },
  es: { ... },
}

export function commonTranslations(lang: AstrologyLang = "fr"): CommonTranslation {
  return translations[lang] ?? translations.fr
}
```

### Note sur le titre "Horoscope" dans Header

Le titre "Horoscope" dans `Header.tsx` est affiché conditionnellement (`showTitle = !isDashboard`). Ce n'est pas vraiment une traduction — c'est le nom du produit. Le mettre dans `t.header.appTitle` permet de le modifier facilement, même si en pratique il ne change pas entre les langues.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/i18n/common.ts` |
| Modifier | `frontend/src/components/layout/Header.tsx` |
| Modifier | `frontend/src/components/HeroHoroscopeCard.tsx` |
| Vérifier/modifier | `frontend/src/components/ui/Modal/Modal.tsx` (si créé en Epic 50) |
| Vérifier/modifier | `frontend/src/components/ui/EmptyState/EmptyState.tsx` (si créé en Epic 50) |

### References

- [Source: frontend/src/components/layout/Header.tsx]
- [Source: frontend/src/components/HeroHoroscopeCard.tsx]
- [Source: frontend/src/i18n/astrology.ts] (AstrologyLang, detectLang)
- [Source: frontend/src/i18n/dashboard.tsx] (pattern de référence)
- [Source: _bmad-output/planning-artifacts/epic-52-i18n-complet.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
