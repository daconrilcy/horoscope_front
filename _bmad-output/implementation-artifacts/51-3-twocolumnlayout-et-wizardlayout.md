# Story 51.3: Créer TwoColumnLayout (Chat) et WizardLayout (ConsultationWizard)

Status: done

## Story

En tant que développeur frontend,
je veux des layouts spécialisés `TwoColumnLayout` et `WizardLayout` extraits de leurs pages respectives,
afin que la mise en page deux-colonnes du Chat et la progression du Wizard de consultation soient réutilisables et séparées de la logique des pages.

## Acceptance Criteria

1. `frontend/src/layouts/TwoColumnLayout.tsx` existe avec les props `sidebar` (slot ReactNode), `main` (slot ReactNode), `sidebarWidth?`, `collapsibleOnMobile?`.
2. `frontend/src/layouts/WizardLayout.tsx` existe avec les props `steps` (tableau de labels), `currentStep` (index), `children` et `onBack?`.
3. `WizardLayout` affiche une barre de progression visuelle en haut avec les étapes numérotées/labellisées (ou accepte un `customProgress`).
4. `ChatPage.tsx` utilise `TwoColumnLayout` (via `ChatLayout`) pour sa structure deux-colonnes — la logique métier reste dans ChatPage.
5. `ConsultationWizardPage.tsx` utilise `WizardLayout` pour sa barre de progression — la logique du wizard reste dans ConsultationWizardPage.
6. Le rendu visuel de ChatPage et ConsultationWizardPage est identique avant/après la migration.
7. Les tests existants de ces pages passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Lire et analyser `ChatPage.tsx` (AC: 1, 4)
  - [x] Identification de `ChatLayout` comme wrapper actuel.

- [x] Tâche 2 : Lire et analyser `ConsultationWizardPage.tsx` (AC: 2, 3, 5)
  - [x] Identification de `WizardProgress` existant.

- [x] Tâche 3 : Créer `TwoColumnLayout.tsx` et `TwoColumnLayout.css` (AC: 1)
  - [x] Implémentation de la structure grid responsive.

- [x] Tâche 4 : Créer `WizardLayout.tsx` et `WizardLayout.css` (AC: 2, 3)
  - [x] Ajout du support `customProgress` pour réutiliser `WizardProgress` sans duplication.

- [x] Tâche 5 : Migrer `ChatPage.tsx` → utiliser `TwoColumnLayout` (AC: 4, 6)
  - [x] Mise à jour de `ChatLayout.tsx` (utilisé par ChatPage) pour consommer `TwoColumnLayout` en mode desktop.

- [x] Tâche 6 : Migrer `ConsultationWizardPage.tsx` → utiliser `WizardLayout` (AC: 5, 6)
  - [x] Enveloppement du contenu par `WizardLayout` en injectant `WizardProgress`.

- [x] Tâche 7 : Validation (AC: 6, 7)
  - [x] `npm run test` — 1079 tests réussis.

## Dev Notes

### Intégration de TwoColumnLayout dans ChatLayout

Plutôt que de modifier directement `ChatPage.tsx` qui est déjà complexe, j'ai choisi de refactoriser `ChatLayout.tsx` (le composant de structure de la feature chat). Il utilise désormais `TwoColumnLayout` pour sa version desktop, ce qui centralise la gestion des colonnes tout en préservant la logique mobile spécifique à cette feature.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création de `TwoColumnLayout` avec support responsive.
- Création de `WizardLayout` avec slots pour la progression.
- Migration de la feature Chat vers `TwoColumnLayout`.
- Migration de la feature Consultation vers `WizardLayout`.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/layouts/WizardLayout.tsx`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/features/chat/components/ChatLayout.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
