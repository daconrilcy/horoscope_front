# Story 65.9 : Actions applicatives sur compte (suspension, reset quota, déblocage)

Status: ready-for-dev

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

- [ ] **Migration Alembic — PREMIÈRE ÉTAPE OBLIGATOIRE** (AC: 1, 2, 4)
  - [ ] Créer `backend/alembic/versions/XXXX_add_is_suspended_is_locked_to_users.py`
  - [ ] Ajouter `is_suspended: bool = False` (NOT NULL, DEFAULT FALSE) sur table `users`
  - [ ] Ajouter `is_locked: bool = False` (NOT NULL, DEFAULT FALSE) sur table `users`
  - [ ] Mettre à jour `UserModel` dans `backend/app/infra/db/models/user.py` pour ajouter les deux champs
- [ ] Implémenter la vérification de suspension dans l'auth (AC: 1)
  - [ ] Dans `require_authenticated_user` (ou middleware), vérifier `user.is_suspended` après validation du JWT
  - [ ] Si suspendu : lever `HTTPException(403, detail={"code": "account_suspended"})` ou `401`
  - [ ] Vérifier si ce check doit être dans `require_authenticated_user` ou dans un middleware séparé — consulter l'architecture auth existante
- [ ] Créer les endpoints dans `admin_users.py` (AC: 1, 2, 3, 4)
  - [ ] `POST /api/v1/admin/users/{user_id}/suspend` — set `is_suspended=True` + audit
  - [ ] `POST /api/v1/admin/users/{user_id}/unsuspend` — set `is_suspended=False` + audit
  - [ ] `POST /api/v1/admin/users/{user_id}/unlock` — set `is_locked=False` + audit
  - [ ] `POST /api/v1/admin/users/{user_id}/reset-quota` body: `{feature_code: str}` — reset compteur + audit
  - [ ] Chaque endpoint appelle `AuditService.create_event()` avec `before`/`after` dans `details`
- [ ] Implémenter le reset de quota (AC: 3)
  - [ ] Identifier la table de quotas/usage canonique (Epic 61 a refactorisé — vérifier `token_usage_log` ou `usage_window` ou équivalent)
  - [ ] Reset = mettre le compteur à 0 pour la fenêtre courante de `feature_code`
- [ ] Mettre à jour `frontend/src/pages/admin/AdminUserDetailPage.tsx` (AC: 1, 2, 3, 4, 5)
  - [ ] Bouton "Suspendre" / "Réactiver" conditionnel selon `is_suspended`
  - [ ] Bouton "Débloquer" conditionnel selon `is_locked`
  - [ ] Boutons "Réinitialiser quota" pour chaque feature dans la section Quotas
  - [ ] Modale de confirmation avant chaque action (composant `Modal` existant du projet — vérifier `frontend/src/components/Modal.tsx` ou équivalent)
  - [ ] Spinner sur le bouton en ≤ 200ms après clic (AC: 5) — désactiver le bouton immédiatement au clic, afficher spinner localement
  - [ ] Mise à jour optimiste du badge de statut après succès
- [ ] CSS pour les modales et boutons d'action (AC: 5)
  - [ ] `.btn--loading` avec spinner intégré
  - [ ] `.badge--suspended` avec `var(--danger)`, `.badge--locked` avec `var(--danger)`

## Dev Notes

### Migration DB — CRITIQUE
**La migration Alembic doit être la première tâche** — sans `is_suspended` et `is_locked` en DB, tous les endpoints échoueront. Suivre le pattern des migrations existantes dans `backend/alembic/versions/`. Ne pas oublier de mettre à jour `UserModel` en parallèle.

### AuditService
- Vérifier l'interface de `AuditService.create_event()` — probablement dans `backend/app/services/audit_service.py`
- Format attendu des `details` JSON : `{"before": {...}, "after": {...}, "reason": "..."}` — les champs `before`/`after` sont des dicts avec les valeurs avant/après la modification

### Suspension et JWT
La suspension doit bloquer **les nouvelles requêtes** — les tokens JWT existants déjà émis doivent être rejetés. Deux approches :
1. Vérifier `is_suspended` dans la DB à chaque requête (dans `require_authenticated_user`) — plus sûr mais requête DB supplémentaire
2. Ajouter `is_suspended` dans le payload JWT et invalider côté refresh — plus performant mais delay potentiel
Option 1 recommandée pour MVP — vérifier comment `require_authenticated_user` charge l'utilisateur depuis la DB.

### Reset quota canonique
L'Epic 61 a refactorisé complètement les entitlements/quotas. La table de quotas canonique est probablement `usage_window` ou `token_usage`. Vérifier les modèles créés dans Epic 61 avant d'implémenter le reset. La logique de reset = mettre le compteur à 0 pour la fenêtre active de la feature.

### Modale de confirmation
Utiliser le composant `Modal` existant du projet (Epic 50 a créé un composant modal générique — `frontend/src/components/Modal.tsx`). Ne pas recréer une modale.

### Project Structure Notes
- **OBLIGATOIRE en premier** : migration Alembic + update `UserModel`
- Modifier : `admin_users.py` router (endpoints suspend/unsuspend/unlock/reset-quota)
- Modifier : `AdminUserDetailPage.tsx` (boutons d'action + modales)
- Modifier : `backend/app/api/dependencies/auth.py` (ajout vérification suspension)

### References
- `backend/app/infra/db/models/user.py` — structure actuelle de `UserModel` [Source: session context]
- `backend/app/infra/db/models/audit_event.py` — `AuditEventModel` [Source: session context]
- NFR3 (feedback ≤ 200ms), NFR8 (journalisation actions sensibles) : `_bmad-output/planning-artifacts/epic-65-espace-admin.md`
- Epic 65 FR65-3, FR65-14 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-9`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
