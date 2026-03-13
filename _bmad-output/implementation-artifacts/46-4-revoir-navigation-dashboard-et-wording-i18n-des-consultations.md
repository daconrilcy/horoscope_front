# Story 46.4: Revoir navigation, dashboard et wording i18n des consultations

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product-facing frontend engineer,
I want remplacer partout la sémantique de tirage par celle de consultations astrologiques ciblées,
so that l'application ne présente plus de fonctionnalité hors périmètre tout en gardant un accès clair aux parcours `/consultations`.

## Acceptance Criteria

1. L'entrée de navigation menant à `/consultations` ne s'appelle plus `Tirages`; elle est renommée de manière cohérente avec le périmètre cible, par exemple `Consultations`.
2. Le dashboard ne promeut plus `Tirage du jour` ni ses variantes EN/ES; le raccourci concerné est renommé vers une sémantique de consultation ciblée.
3. Les chaînes utilisateur visibles dans FR, EN et ES ne mentionnent plus `tirage`, `cartes`, `runes`, `tarot`, `spread` ou équivalent pour le parcours consultations.
4. Les handlers, clés et tokens frontend les plus visibles sont réalignés pour éviter la confusion de maintenance:
   - `tirages` / `tirage`
   - `onTirageClick`
   - `tirageTitle`, `tirageSubtitle`
   - `--badge-tirage`
5. La route `/consultations` ne change pas et les autres raccourcis dashboard restent fonctionnels.
6. Les tests frontend couvrent le renommage navigation/dashboard et la cohérence i18n minimale sur le nouveau libellé.

## Tasks / Subtasks

- [ ] Task 1: Renommer la navigation principale sans casser les chemins (AC: 1, 5)
  - [ ] Mettre à jour `frontend/src/ui/nav.ts`
  - [ ] Conserver `path: '/consultations'`
  - [ ] Réviser les éventuelles attentes de tests liées au label `Tirages`
  - [ ] Vérifier la cohérence mobile/desktop du bottom nav

- [ ] Task 2: Recomposer le raccourci dashboard lié aux consultations (AC: 2, 4, 5)
  - [ ] Mettre à jour `frontend/src/components/ShortcutsSection.tsx`
  - [ ] Renommer `onTirageClick` et les clés internes `tirage*`
  - [ ] Remplacer le titre/sous-titre par une promesse consultation pertinente
  - [ ] Réviser si besoin l'icône ou le badge pour refléter la nouvelle sémantique

- [ ] Task 3: Nettoyer le catalogue i18n dashboard et consultations (AC: 2, 3, 4)
  - [ ] Mettre à jour `frontend/src/i18n/dashboard.tsx`
  - [ ] Mettre à jour `frontend/src/i18n/consultations.ts`
  - [ ] Vérifier la parité FR/EN/ES sur toutes les nouvelles clés
  - [ ] Supprimer les variantes lexicales qui continueraient à évoquer un tirage

- [ ] Task 4: Réviser les tokens et noms techniques trop exposés (AC: 4)
  - [ ] Remplacer `--badge-tirage` par un nom neutre ou consultation-centric
  - [ ] Supprimer les clés `tirage` trop visibles dans les composants si elles ne servent plus qu'historiquement
  - [ ] Éviter les renommages destructifs inutiles si un alias transitoire est nécessaire pour limiter le delta

- [ ] Task 5: Tester la cohérence visible du renommage (AC: 1, 2, 3, 5, 6)
  - [ ] Ajouter ou mettre à jour les tests du nav
  - [ ] Ajouter ou mettre à jour les tests du dashboard shortcut
  - [ ] Vérifier qu'aucune chaîne UI visible ne contient encore `tirage` dans le parcours principal
  - [ ] Vérifier que les liens et clics vers `/consultations` sont inchangés

## Dev Notes

- Cette story traite la sémantique visible et le vocabulaire. Elle ne doit pas réintroduire de logique métier ni masquer un backend encore actif.
- Les références historiques dans les artefacts BMAD 17.1, 17.5 et 45.2 montrent que le mot `tirage` a été largement diffusé dans la navigation et le dashboard. Il faut le retirer de manière cohérente.
- Le renommage doit être pragmatique: route stable, libellé corrigé.

### Previous Story Intelligence

- Story 17.1 a ancré le menu `/consultations` sous le libellé `Tirages`.
- Story 17.5 a diffusé la carte `Tirage du jour`, les clés `tirageTitle`/`tirageSubtitle` et le badge `--badge-tirage`.
- Story 45.2 a réutilisé ce raccourci sur la landing dashboard.
- Story 45.1 impose explicitement la stabilité des deep links `/consultations`.

### Project Structure Notes

- Fichiers principalement concernés:
  - `frontend/src/ui/nav.ts`
  - `frontend/src/components/ShortcutsSection.tsx`
  - `frontend/src/i18n/dashboard.tsx`
  - `frontend/src/i18n/consultations.ts`
  - styles associés dans `frontend/src/App.css` si un badge dédié existe encore

### Technical Requirements

- Préserver les paths et la structure des objets de navigation autant que possible.
- Les nouveaux labels doivent être centralisés dans l'i18n et non codés en dur.
- Le renommage des handlers et tokens doit rester cohérent pour la maintenance future.

### Architecture Compliance

- Le dashboard continue à réutiliser `ShortcutsSection`.
- Le nav continue à être piloté par `navItems`.
- L'i18n reste centralisé dans les catalogues dédiés.

### Testing Requirements

- Tests de navigation mobile si existants.
- Tests du `ShortcutCard`/`ShortcutsSection`.
- Vérification textuelle FR/EN/ES sur les clés les plus visibles.

### References

- [Source: frontend/src/ui/nav.ts]
- [Source: frontend/src/components/ShortcutsSection.tsx]
- [Source: frontend/src/i18n/dashboard.tsx]
- [Source: frontend/src/i18n/consultations.ts]
- [Source: _bmad-output/implementation-artifacts/17-1-fondations-ui-tokens-typo-lucide.md]
- [Source: _bmad-output/implementation-artifacts/17-5-raccourcis-shortcut-card.md]
- [Source: _bmad-output/implementation-artifacts/45-1-refondre-le-routing-dashboard-et-isoler-la-page-horoscope-detaillee.md]
- [Source: _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

### Completion Notes List

### File List
