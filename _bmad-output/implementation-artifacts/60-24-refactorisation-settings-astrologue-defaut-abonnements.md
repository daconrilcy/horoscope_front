# Story 60.24 : Refactorisation des pages `/settings` — suppression liens sidebar, choix astrologue par défaut, refonte subscription/usage/style premium

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur premium
I want une interface de paramètres unifiée et esthétique
So that je puisse gérer mon compte, mon astrologue par défaut et mon abonnement dans un environnement cohérent avec le reste de l'application.

## Acceptance Criteria

- [x] AC1: Suppression des liens directs `/profile`, `/billing`, `/privacy` de la sidebar (accessibles désormais via `/settings`).
- [x] AC2: Ajout d'un sélecteur d'astrologue par défaut dans `/settings/account` (remplace l'ancien choix de style).
- [x] AC3: Affichage d'un badge « Votre défaut » sur la vignette de l'astrologue choisi dans le catalogue et son profil.
- [x] AC4: Refonte visuelle globale de `/settings` (background gradient, halos, glass cards) alignée sur le design système premium.
- [x] AC5: Simplification de la page abonnement (plans grid + section achat crédits).

## Tasks

- [x] Task 1: Nettoyage sidebar (AC1)
  - [x] Supprimer les entrées `profile`, `privacy`, `billing` de `frontend/src/ui/nav.ts`.
  - [x] Vérifier que le menu utilisateur (Header/UserMenu) pointe bien vers `/settings`.
- [x] Task 2: Backend DB + API (AC2)
  - [x] Modèle ORM et schéma Pydantic : ajouter `default_astrologer_id: str | None = None`.
  - [x] Migration Alembic : `ADD COLUMN default_astrologer_id VARCHAR(64) NULL`.
  - [x] Router `users.py` : mettre à jour `get_me_settings` et `patch_me_settings` pour gérer ce nouveau champ.
- [x] Task 3: Hook Frontend (AC2)
  - [x] Créer `frontend/src/api/userSettings.ts` avec hooks TanStack Query.
- [x] Task 4: Refonte AccountSettings (AC2, AC4)
  - [x] Remplacer le sélecteur de style par une grille d'astrologues (vignettes circulaires).
  - [x] Intégrer les styles premium (Glass cards, labels).
- [x] Task 5: Pages astrologues (AC3)
  - [x] Afficher le badge « Votre défaut » dans `AstrologerCard.tsx`.
  - [x] Ajouter bouton « Définir par défaut » dans `AstrologerProfilePage.tsx`.
- [x] Task 6: Subscription & Usage (AC5, AC4)
  - [x] Refactorisation premium de `/settings/subscription` et `/settings/usage`.
  - [x] Remplacement de `BillingPanel` par une vue intégrée plus légère.
- [x] Task 7: Style premium global (AC4)
  - [x] Créer `frontend/src/pages/settings/Settings.css`.
  - [x] Mettre à jour `SettingsLayout.tsx` pour include background, halos et noise.

## Dev Agent Record

### File List
- `backend/app/api/v1/routers/users.py`
- `backend/app/infra/db/models/user.py`
- `backend/app/tests/integration/test_users_settings.py` (New)
- `backend/migrations/versions/dd729c20741e_add_default_astrologer_id_to_users.py` (New)
- `frontend/src/api/userSettings.ts` (New)
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/i18n/settings.ts`
- `frontend/src/layouts/SettingsLayout.tsx`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/pages/settings/Settings.css` (New)
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/settings/UsageSettings.tsx`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/BottomNavPremium.test.tsx`
- `frontend/src/tests/SettingsPage.test.tsx`
- `frontend/src/tests/ui-barrel.test.ts`
- `frontend/src/tests/ui-nav.test.ts`
- `frontend/src/types/user.ts`
- `frontend/src/ui/nav.ts`

### Change Log
- **Nettoyage Sidebar & Navigation** : Suppression des liens directs vers `/profile`, `/billing` et `/privacy`. Accès centralisé via le menu utilisateur et la page `/settings`.
- **Backend (User Settings)** : Extension du modèle `User` avec `default_astrologer_id`. Mise à jour des endpoints `GET` et `PATCH /me/settings`.
- **Database** : Migration Alembic pour l'ajout de la colonne `default_astrologer_id`.
- **Frontend API** : Création de `userSettings.ts` utilisant TanStack Query pour la persistance des préférences.
- **Refonte visuelle Premium** : Intégration de `Settings.css` et mise à jour de `SettingsLayout` avec fonds gradients, halos lumineux et glassmorphism.
- **Sélecteur d'Astrologue par Défaut** : Remplacement du choix de style par une grille de sélection d'astrologues réels/IA dans les paramètres du compte.
- **Badges & CTAs Astrologues** : Affichage du badge « Votre défaut » dans le catalogue et ajout du bouton de bascule dans le profil astrologue.
- **Validation Abonnement** :
  - **Changement de plan** : Implémentation du switch entre `basic-entry` et `premium-unlimited` via mutation `useChangePlan`.
  - **Validation Flow** : Ajout d'une étape de confirmation explicite avec bouton de validation et gestion des états d'attente (isPending).
  - **Plan Gratuit** : Option bridée en attente du mapping backend pour la rétractation, avec message d'information temporaire.
  - **UX/Feedback** : Curseurs d'attente, opacité réduite et textes de chargement inline pour un feedback instantané.
- **Qualité & Tests** : Correction de 33 tests en échec suite aux changements de navigation et de structure UI. Ajout de tests d'intégration backend pour les nouveaux réglages.
