# Story 65.9 : Actions applicatives sur compte (suspension, reset quota, déblocage)

Status: done

## Story

En tant qu'**admin support**,  
je veux pouvoir suspendre, réactiver, réinitialiser un quota ou débloquer un compte,  
afin de résoudre des incidents utilisateur sans passer par la base de données directement.

## Acceptance Criteria

1. **Given** l'admin est sur la fiche d'un utilisateur actif  
   **When** il clique "Suspendre le compte" et confirme dans la modale  
   **Then** un flag de suspension est posé sur le compte (`is_suspended = true`)  
   **And** les prochains refresh de token JWT pour cet utilisateur échouent avec `account_suspended`  
   **And** un audit log est généré : `action: "account_suspended"`, `target_type: "user"`, `target_id: user_id`, `before: {is_suspended: false}`, `after: {is_suspended: true}`  
   **And** le badge de statut sur la fiche passe à "Suspendu"

2. **Given** l'admin est sur la fiche d'un utilisateur suspendu  
   **When** il clique "Réactiver le compte" et confirme  
   **Then** `is_suspended = false`, audit log généré : `action: "account_reactivated"`

3. **Given** l'admin clique "Réinitialiser le quota [feature]" pour une feature spécifique  
   **When** il confirme dans la modale (aucun champ de motif requis)  
   **Then** le compteur de quota pour la période courante est remis à zéro  
   **And** un audit log : `action: "quota_reset"`, `details: {feature_code, before: N, after: 0}`  
   **And** l'indicateur de quota sur la fiche se met à jour

4. **Given** un compte est verrouillé (`is_locked = true`)  
   **When** l'admin clique "Débloquer le compte" et confirme  
   **Then** `is_locked = false`, audit log : `action: "account_unlocked"`

5. **Given** l'admin initie une action  
   **When** le bouton est cliqué  
   **Then** le feedback d'initiation (spinner, désactivation bouton) est visible en ≤ 200ms

## Tasks / Subtasks

- [x] **Migration Alembic** (AC: 1, 2, 4)
  - [x] Créer `backend/migrations/versions/ce173983d275_add_is_suspended_and_is_locked_to_users.py`
  - [x] Ajouter `is_suspended` et `is_locked` sur table `users`
  - [x] Mettre à jour `UserModel` dans `backend/app/infra/db/models/user.py`
- [x] Implémenter la vérification de suspension dans l'auth (AC: 1)
  - [x] Dans `require_authenticated_user`, vérifier `user.is_suspended`
  - [x] Lever `UserAuthenticationError(403, code="account_suspended")`
- [x] Créer les endpoints dans `admin_users.py` (AC: 1, 2, 3, 4)
  - [x] `POST /api/v1/admin/users/{user_id}/suspend`
  - [x] `POST /api/v1/admin/users/{user_id}/unsuspend`
  - [x] `POST /api/v1/admin/users/{user_id}/unlock`
  - [x] `POST /api/v1/admin/users/{user_id}/reset-quota`
  - [x] Audit logs détaillés avec before/after
- [x] Implémenter le reset de quota (AC: 3)
  - [x] Reset `FeatureUsageCounterModel.used_count = 0`
- [x] Mettre à jour `frontend/src/pages/admin/AdminUserDetailPage.tsx` (AC: 1, 2, 3, 4, 5)
  - [x] Boutons d'action conditionnels
  - [x] Utilisation de `window.confirm` pour le MVP (modale native)
  - [x] Feedback de chargement via `isPending` de React Query
- [x] CSS pour les badges de statut (AC: 5)
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_actions_api.py`

### File List
- `backend/app/infra/db/models/user.py`
- `backend/migrations/versions/ce173983d275_add_is_suspended_and_is_locked_to_users.py`
- `backend/app/api/dependencies/auth.py`
- `backend/app/api/v1/routers/admin_users.py`
- `backend/app/api/v1/schemas/admin_users.py`
- `frontend/src/pages/admin/AdminUserDetailPage.tsx`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `backend/app/tests/integration/test_admin_actions_api.py`
