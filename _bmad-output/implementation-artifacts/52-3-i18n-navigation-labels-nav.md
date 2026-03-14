# Story 52.3: Créer i18n/navigation.ts — labels de navigation traduits

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les labels de navigation (`ui/nav.ts`) soient traduits en FR, EN et ES,
afin que BottomNav et Sidebar affichent la navigation dans la langue de l'utilisateur.

## Acceptance Criteria

1. Le fichier `frontend/src/i18n/navigation.ts` existe avec `NavigationTranslation` et les traductions FR, EN, ES pour chaque clé de navigation.
2. `NavigationTranslation` couvre les clés des `navItems` dans `ui/nav.ts` : `today`, `chat`, `natal`, `consultations`, `profile`, `privacy`, `support`, `monitoring`, `persona`, `reconciliation`, `ent_api`, `ent_astro`, `ent_usage`, `ent_editorial`, `ent_billing`.
3. `ui/nav.ts` est modifié pour remplacer les labels hardcodés par des clés de traduction : `label` devient une clé (`labelKey`) et les labels traduits sont résolus dans les composants consommateurs.
4. `BottomNav.tsx` et `Sidebar.tsx` utilisent `navigationTranslations(lang)` pour afficher les labels traduits.
5. Le rendu visuel de BottomNav et Sidebar est identique en FR, et traduit en EN/ES.
6. Tous les tests existants passent.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire `BottomNav.tsx` et `Sidebar.tsx` (AC: 4)
  - [ ] Identifier comment ils consomment `navItems` et affichent les labels
  - [ ] Identifier le pattern de détection de langue s'il existe déjà

- [ ] Tâche 2 : Créer `frontend/src/i18n/navigation.ts` (AC: 1, 2)
  - [ ] Définir `NavigationTranslation` : objet `nav` avec une clé par `NavItem.key`
  - [ ] Traductions FR (reprendre les labels actuels de `ui/nav.ts`)
  - [ ] Traductions EN et ES
  - [ ] Exporter `navigationTranslations(lang): NavigationTranslation`

- [ ] Tâche 3 : Choisir et implémenter la stratégie de migration de `ui/nav.ts` (AC: 3)
  - [ ] **Option A** (recommandée) : Garder `label` dans `navItems` comme valeur FR par défaut, et les composants surchargent avec la traduction au rendu
  - [ ] **Option B** : Remplacer `label: string` par `labelKey: keyof NavigationTranslation['nav']` — type-safe mais plus de changements
  - [ ] Documenter la stratégie choisie dans les notes de complétion

- [ ] Tâche 4 : Migrer `BottomNav.tsx` (AC: 4)
  - [ ] Ajouter détection de langue et `const t = navigationTranslations(lang)`
  - [ ] Remplacer `item.label` par `t.nav[item.key]` (ou pattern équivalent)

- [ ] Tâche 5 : Migrer `Sidebar.tsx` (AC: 4)
  - [ ] Même approche que BottomNav

- [ ] Tâche 6 : Validation (AC: 5, 6)
  - [ ] Vérifier BottomNav et Sidebar en FR
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Story 52.1 peut être en parallèle. Aucun prérequis bloquant.

### `ui/nav.ts` — labels actuels (tous en français)

```typescript
{ key: 'today',          label: "Aujourd'hui", ... }
{ key: 'chat',           label: "Chat", ... }
{ key: 'natal',          label: "Thème", ... }
{ key: 'consultations',  label: "Consultations", ... }
{ key: 'profile',        label: "Profil", ... }
{ key: 'privacy',        label: "Confidentialité", ... }
{ key: 'support',        label: "Support", ... }
{ key: 'monitoring',     label: "Monitoring", ... }
{ key: 'persona',        label: "Persona", ... }
{ key: 'reconciliation', label: "Réconciliation", ... }
{ key: 'ent_api',        label: "API", ... }
{ key: 'ent_astro',      label: "Astrologie", ... }
{ key: 'ent_usage',      label: "Usage", ... }
{ key: 'ent_editorial',  label: "Éditorial", ... }
{ key: 'ent_billing',    label: "Facturation", ... }
```

### Stratégie recommandée (Option A — moins invasive)

Garder `ui/nav.ts` inchangé (les labels restent en FR comme valeurs par défaut). Dans les composants consommateurs, résoudre le label via la traduction si disponible, sinon fallback sur `item.label` :

```typescript
// Dans BottomNav.tsx / Sidebar.tsx
const t = navigationTranslations(lang)
const label = t.nav[item.key as keyof typeof t.nav] ?? item.label
```

Avantages :
- `ui/nav.ts` reste lisible avec les labels en clair
- Aucun changement d'interface pour les consommateurs actuels
- TypeScript tolérant : les clés non trouvées tombent en fallback

### Structure de `i18n/navigation.ts`

```typescript
import type { AstrologyLang } from "./astrology"

export interface NavigationTranslation {
  nav: {
    today: string
    chat: string
    natal: string
    consultations: string
    profile: string
    privacy: string
    support: string
    monitoring: string
    persona: string
    reconciliation: string
    ent_api: string
    ent_astro: string
    ent_usage: string
    ent_editorial: string
    ent_billing: string
  }
}

const translations: Record<AstrologyLang, NavigationTranslation> = {
  fr: { nav: { today: "Aujourd'hui", chat: "Chat", natal: "Thème", ... } },
  en: { nav: { today: "Today", chat: "Chat", natal: "Chart", ... } },
  es: { nav: { today: "Hoy", chat: "Chat", natal: "Carta", ... } },
}

export function navigationTranslations(lang: AstrologyLang = "fr"): NavigationTranslation {
  return translations[lang] ?? translations.fr
}
```

### Notes de traduction

**EN** : `natal` → "Chart", `consultations` → "Consultations", `profile` → "Profile", `privacy` → "Privacy"
**ES** : `natal` → "Carta", `today` → "Hoy", `profile` → "Perfil", `privacy` → "Privacidad", `reconciliation` → "Reconciliación"

Les termes techniques (`monitoring`, `persona`, `API`) restent identiques dans les 3 langues.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/i18n/navigation.ts` |
| Modifier | `frontend/src/components/layout/BottomNav.tsx` |
| Modifier | `frontend/src/components/layout/Sidebar.tsx` |
| Ne pas modifier | `frontend/src/ui/nav.ts` (si Option A choisie) |

### References

- [Source: frontend/src/ui/nav.ts]
- [Source: frontend/src/components/layout/BottomNav.tsx]
- [Source: frontend/src/components/layout/Sidebar.tsx]
- [Source: frontend/src/i18n/astrology.ts]
- [Source: _bmad-output/planning-artifacts/epic-52-i18n-complet.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
