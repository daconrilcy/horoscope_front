# Story 52.2: Créer i18n/common.ts — textes transversaux Header, actions génériques, états

Status: done

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

- [x] Tâche 1 : Lire `HeroHoroscopeCard.tsx` pour inventorier ses strings (AC: 2, 5)
  - [x] Lister tous les textes hardcodés (boutons, aria-labels, titres)

- [x] Tâche 2 : Créer `frontend/src/i18n/common.ts` (AC: 1, 2, 3)
  - [x] Définir `CommonTranslation` avec toutes les sections identifiées
  - [x] Traductions FR, EN, ES pour chaque clé
  - [x] Exporter `commonTranslations(lang: AstrologyLang): CommonTranslation`

- [x] Tâche 3 : Migrer `Header.tsx` (AC: 4)
  - [x] Ajouter `const lang = detectLang()` et `const t = commonTranslations(lang)`
  - [x] Remplacer "Se déconnecter" → `t.header.logout`
  - [x] Remplacer `"Utilisateur"` (fallback rôle) → `t.header.defaultRole`
  - [x] Remplacer `"Horoscope"` (titre app) → `t.header.appTitle`

- [x] Tâche 4 : Migrer `HeroHoroscopeCard.tsx` (AC: 5)
  - [x] Ajouter la détection de langue
  - [x] Remplacer les boutons hardcodés par les clés `t.heroCard.*`
  - [x] Remplacer les aria-labels hardcodés

- [x] Tâche 5 : Vérifier les composants UI de l'Epic 50 (AC: 6)
  - [x] `Modal.tsx` : mise à jour de l'aria-label de fermeture par défaut
  - [x] `EmptyState.tsx` : déjà piloté par props (titre et description requis) — pas de changement nécessaire

- [x] Tâche 6 : Validation (AC: 7)
  - [x] `npm run test` — 1079 tests réussis
  - [x] Vérifier Header visuellement (logout button, rôle affiché)
  - [x] Vérifier HeroHoroscopeCard boutons d'action

## Dev Notes

### Stratégie de préservation des tests (Stories 52.1 & 52.2)

Le projet présentait une incohérence dans ses tests :
- Les anciens tests (SignIn, Header, etc.) s'attendaient à du français sans mocker la langue.
- Les nouveaux tests (Consultations) s'attendaient à de l'anglais sans mocker la langue.
- Vitest/jsdom renvoyant `en-US` par défaut, l'introduction de l'i18n a cassé les anciens tests.

**Solution mise en place :**
1. Mise à jour de `frontend/src/tests/setup.ts` pour stubber `navigator.language` à `fr-FR` par défaut. Cela répare tous les anciens tests s'attendant à du français.
2. Mise à jour de `frontend/src/tests/ConsultationsPage.test.tsx` pour forcer explicitement `en` dans `localStorage` au début de chaque test. Cela répare les tests récents qui s'attendaient à de l'anglais.
3. Les tests qui stubbent explicitement `navigator.language` continuent de fonctionner car leur stub local prime sur le stub global de `setup.ts`.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création de `i18n/common.ts` centralisant les actions et états transversaux.
- Migration de `Header` et `HeroHoroscopeCard`.
- Mise à jour de `Modal` pour l'internationalisation de ses labels internes.
- Résolution globale des conflits de langue dans les tests via `setup.ts` et correctifs ciblés.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/i18n/common.ts`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/HeroHoroscopeCard.tsx`
- `frontend/src/components/ui/Modal/Modal.tsx`
- `frontend/src/tests/setup.ts`
- `frontend/src/tests/ConsultationsPage.test.tsx`
