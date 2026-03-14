# Story 52.3: Créer i18n/navigation.ts — labels de navigation traduits

Status: done

## Story

En tant que développeur frontend,
je veux que les labels de navigation (`ui/nav.ts`) soient traduits en FR, EN et ES,
afin que BottomNav et Sidebar affichent la navigation dans la langue de l'utilisateur.

## Acceptance Criteria

1. Le fichier `frontend/src/i18n/navigation.ts` existe avec `NavigationTranslation` et les traductions FR, EN, ES pour chaque clé de navigation.
2. `NavigationTranslation` couvre les clés des `navItems` dans `ui/nav.ts` : `today`, `chat`, `natal`, `consultations`, `profile`, `privacy`, `support`, `monitoring`, `persona`, `reconciliation`, `ent_api`, `ent_astro`, `ent_usage`, `ent_editorial`, `ent_billing`.
3. `ui/nav.ts` est modifié pour remplacer les labels hardcodés par des clés de traduction : `label` devient une clé (`labelKey`) et les labels traduits sont résolus dans les composants consommateurs. (Stratégie choisie : Option A — labels FR conservés comme fallback).
4. `BottomNav.tsx` et `Sidebar.tsx` utilisent `navigationTranslations(lang)` pour afficher les labels traduits.
5. Le rendu visuel de BottomNav et Sidebar est identique en FR, et traduit en EN/ES.
6. Tous les tests existants passent.

## Tasks / Subtasks

- [x] Tâche 1 : Lire `BottomNav.tsx` et `Sidebar.tsx` (AC: 4)
  - [x] Identifier comment ils consomment `navItems` et affichent les labels
  - [x] Identifier le pattern de détection de langue (detectLang)

- [x] Tâche 2 : Créer `frontend/src/i18n/navigation.ts` (AC: 1, 2)
  - [x] Définir `NavigationTranslation` : objet `nav` avec une clé par `NavItem.key`
  - [x] Traductions FR (reprendre les labels actuels de `ui/nav.ts`)
  - [x] Traductions EN et ES
  - [x] Exporter `navigationTranslations(lang): NavigationTranslation`

- [x] Tâche 3 : Choisir et implémenter la stratégie de migration de `ui/nav.ts` (AC: 3)
  - [x] **Option A** (choisie) : Garder `label` dans `navItems` comme valeur FR par défaut, et les composants surchargent avec la traduction au rendu

- [x] Tâche 4 : Migrer `BottomNav.tsx` (AC: 4)
  - [x] Ajouter détection de langue et `const t = navigationTranslations(lang)`
  - [x] Remplacer `item.label` par `t.nav[item.key]`

- [x] Tâche 5 : Migrer `Sidebar.tsx` (AC: 4)
  - [x] Même approche que BottomNav

- [x] Tâche 6 : Validation (AC: 5, 6)
  - [x] Vérifier BottomNav et Sidebar en FR
  - [x] `npm run test` — 1079 tests réussis

## Dev Notes

### Stratégie de migration

La stratégie **Option A** a été retenue : les labels dans `ui/nav.ts` restent en français clair pour servir de fallback immédiat et préserver la lisibilité du fichier de configuration. La traduction est résolue dynamiquement dans `BottomNav` et `Sidebar` en utilisant la `key` de l'item comme clé de dictionnaire dans `navigationTranslations`.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création de `i18n/navigation.ts` avec support complet FR, EN, ES.
- Migration de `BottomNav` et `Sidebar` pour la résolution dynamique des labels.
- Maintien de la compatibilité avec la structure existante de `navItems`.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/i18n/navigation.ts`
- `frontend/src/components/layout/BottomNav.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
