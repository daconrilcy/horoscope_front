# Story 46.4: Revoir navigation, dashboard et wording i18n des consultations

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product-facing frontend engineer,
I want remplacer partout la sémantique de tirage par celle de consultations astrologiques ciblées,
so that l'expérience soit plus fluide et les conseils plus structurés (points clés, conseils actionnables).

## Acceptance Criteria

- [x] AC1: L'entrée de navigation menant à `/consultations` ne s'appelle plus `Tirages`; elle est renommée de manière cohérente avec le périmètre cible, par exemple `Consultations`.
- [x] AC2: Le dashboard ne promeut plus `Tirage du jour` ni ses variantes EN/ES; le raccourci concerné est renommé vers une sémantique de consultation ciblée.
- [x] AC3: Les chaînes utilisateur visibles dans FR, EN et ES ne mentionnent plus `tirage`, `cartes`, `runes`, `tarot`, `spread` ou équivalent pour le parcours consultations.
- [x] AC4: Les handlers, clés et tokens frontend les plus visibles sont réalignés pour éviter la confusion de maintenance:
   - [x] `tirages` -> `consultations`
   - [x] `onTirageClick` -> `onConsultationClick`
   - [x] `tirageTitle` -> `consultationTitle`, `tirageSubtitle` -> `consultationSubtitle`
   - [x] `--badge-tirage` -> `--badge-consultation`
- [x] AC5: La route `/consultations` ne change pas et les autres raccourcis dashboard restent fonctionnels.
- [x] AC6: Les tests frontend couvrent le renommage navigation/dashboard et la cohérence i18n minimale sur le nouveau libellé.

## Tasks / Subtasks

- [x] Task 1: Renommer la navigation principale sans casser les chemins (AC: 1, 5)
  - [x] Mettre à jour `frontend/src/ui/nav.ts`
  - [x] Conserver `path: '/consultations'`
  - [x] Réviser les éventuelles attentes de tests liées au label `Tirages`
  - [x] Vérifier la cohérence mobile/desktop du bottom nav

- [x] Task 2: Recomposer le raccourci dashboard lié aux consultations (AC: 2, 4, 5)
  - [x] Mettre à jour `frontend/src/components/ShortcutsSection.tsx`
  - [x] Renommer `onTirageClick` et les clés internes `tirage*`
  - [x] Remplacer le titre/sous-titre par une promesse consultation pertinente
  - [x] Réviser si besoin l'icône ou le badge pour refléter la nouvelle sémantique

- [x] Task 3: Nettoyer le catalogue i18n dashboard et consultations (AC: 2, 3, 4)
  - [x] Mettre à jour `frontend/src/i18n/dashboard.tsx`
  - [x] Mettre à jour `frontend/src/i18n/consultations.ts`
  - [x] Vérifier la parité FR/EN/ES sur toutes les nouvelles clés
  - [x] Supprimer les variantes lexicales qui continueraient à évoquer un tirage

- [x] Task 4: Réviser les tokens et noms techniques trop exposés (AC: 4)
  - [x] Remplacer `--badge-tirage` par un nom neutre ou consultation-centric
  - [x] Supprimer les clés `tirage` trop visibles dans les composants si elles ne servent plus qu'historiquement
  - [x] Éviter les renommages destructifs inutiles si un alias transitoire est nécessaire pour limiter le delta

- [x] Task 5: Tester la cohérence visible du renommage (AC: 1, 2, 3, 5, 6)
  - [x] Ajouter ou mettre à jour les tests du nav
  - [x] Ajouter ou mettre à jour les tests du dashboard shortcut
  - [x] Vérifier qu'aucune chaîne UI visible ne contient encore `tirage` dans le parcours principal
  - [x] Vérifier que les liens et clics vers `/consultations` sont inchangés

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Renamed nav items in ui/nav.ts.
- Updated ShortcutsSection.tsx props and keys.
- Renamed --badge-tirage to --badge-consultation in theme.css.
- Cleaned up consultations.ts and dashboard.tsx i18n files.
- Updated ui-nav.test.ts and theme-tokens.test.ts.

### Completion Notes List

- Successfully renamed all visible user-facing semantics from "Tirage" to "Consultation".
- Maintained deep link stability for /consultations.
- Updated i18n for FR, EN, ES.
- Aligned technical names (CSS tokens, props) to avoid future confusion.

### File List

- frontend/src/ui/nav.ts
- frontend/src/components/ShortcutsSection.tsx
- frontend/src/i18n/dashboard.tsx
- frontend/src/i18n/consultations.ts
- frontend/src/styles/theme.css
- frontend/src/tests/ui-nav.test.ts
- frontend/src/tests/theme-tokens.test.ts
