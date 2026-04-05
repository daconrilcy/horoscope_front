# Story 65.2 : Guard admin backend — dépendance FastAPI centralisée

Status: in-progress

## Story

En tant que **développeur backend**,  
je veux une dépendance FastAPI `require_admin_user` centralisée,  
afin que tous les endpoints admin partagent une logique de contrôle d'accès cohérente et maintenable.

## Acceptance Criteria

1. **Given** un endpoint admin utilise `Depends(require_admin_user)`  
   **When** la requête arrive avec un token JWT valide et `role: "admin"`  
   **Then** l'endpoint s'exécute normalement et retourne `AuthenticatedUser` avec le rôle admin

2. **Given** un endpoint admin utilise `Depends(require_admin_user)`  
   **When** la requête arrive sans token ou avec un token invalide  
   **Then** l'endpoint retourne HTTP 401 avec le code `missing_access_token` ou `invalid_token`

3. **Given** un endpoint admin utilise `Depends(require_admin_user)`  
   **When** la requête arrive avec un token valide mais un rôle autre que `admin` (ex : `ops`, `user`, `support`)  
   **Then** l'endpoint retourne HTTP 403 avec le code `insufficient_role` et `details: {"required_role": "admin", "actual_role": "..."}`

4. **Given** les routers admin existants (`admin_llm.py`, `admin_pdf_templates.py`, `ops_monitoring.py`, `ops_persona.py`)  
   **When** la migration vers `require_admin_user` est effectuée  
   **Then** les checks inline `if user.role not in {...}` et le helper local `_ensure_admin_role()` sont supprimés  
   **And** le comportement fonctionnel des endpoints existants est inchangé (tests de non-régression passent)
Status: done

## Tasks / Subtasks

- [x] Ajouter `require_admin_user` dans `backend/app/api/dependencies/auth.py` (AC: 1, 2, 3)
  - [x] Implémenter comme `async def require_admin_user(user: AuthenticatedUser = Depends(require_authenticated_user)) -> AuthenticatedUser:`
  - [x] Vérifier `user.role == "admin"` — lever `UserAuthenticationError(403, ...)` si non
  - [x] Les erreurs 401 sont gérées automatiquement par `require_authenticated_user` (délégation)
- [x] Migrer `backend/app/api/v1/routers/admin_llm.py` (AC: 4)
  - [x] Remplacer `_ensure_admin_role(user)` par `Depends(require_admin_user)` sur chaque endpoint
  - [x] Supprimer la fonction locale `_ensure_admin_role()`
- [x] Migrer `backend/app/api/v1/routers/admin_pdf_templates.py` si existant (AC: 4)
  - [x] Remplacer les checks inline par `Depends(require_admin_user)`
- [x] Migrer `backend/app/api/v1/routers/ops_monitoring.py` (AC: 4)
  - [x] Remplacer les checks inline par `Depends(require_admin_user)`
- [x] Migrer `backend/app/api/v1/routers/ops_persona.py` (AC: 4)
  - [x] Remplacer les checks inline par `Depends(require_admin_user)`
- [x] Tests unitaires `backend/app/tests/unit/test_require_admin_user.py` (AC: 1, 2, 3)
  - [x] Test : token admin valide → 200
  - [x] Test : token invalide → 401
  - [x] Test : token valide rôle `ops` → 403 avec `insufficient_role`
  - [x] Test : token valide rôle `user` → 403
- [x] Tests de non-régression sur les endpoints migrés (AC: 4)

### File List
- `backend/app/api/dependencies/auth.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/api/v1/routers/admin_pdf_templates.py`
- `backend/app/api/v1/routers/ops_monitoring.py`
- `backend/app/api/v1/routers/ops_persona.py`
- `backend/app/tests/unit/test_require_admin_user.py`

### Completion Notes List

- **Fix (code review)** : La migration de `ops_monitoring.py` et `ops_persona.py` vers `require_admin_user` (rôle `admin` exclusif) était incorrecte — ces endpoints doivent rester accessibles au rôle `ops` (et `admin`). Ajout d'une dépendance `require_ops_user` dans `auth.py` qui autorise `{"ops", "admin"}`. `ops_monitoring.py` et `ops_persona.py` utilisent désormais `require_ops_user`. Les endpoints admin purs (`admin_llm.py`, `admin_pdf_templates.py`, tous les nouveaux routers admin Epic 65) conservent `require_admin_user`.

### Contexte architectural
- **Fichier cible** : `backend/app/api/dependencies/auth.py` — contient déjà `require_authenticated_user` et `AuthenticatedUser`
- **`AuthenticatedUser`** : modèle Pydantic avec champs `id: int`, `role: str`, `email: str`, `created_at: datetime` — **ne pas modifier** dans cette story (le champ `permissions: list[str]` est ajouté dans Story 65-21)
- **`require_authenticated_user`** : dépendance existante qui valide le JWT et retourne `AuthenticatedUser` — `require_admin_user` doit la composer via `Depends()`
- **Pattern de composition FastAPI** :
  ```python
  async def require_admin_user(
      user: AuthenticatedUser = Depends(require_authenticated_user)
  ) -> AuthenticatedUser:
      if user.role != "admin":
          raise HTTPException(
              status_code=403,
              detail={"code": "insufficient_role", "required_role": "admin", "actual_role": user.role}
          )
      return user
  ```
- **`admin_llm.py`** : contient `_ensure_admin_role(user)` — helper local à supprimer. Identifier tous les endpoints qui l'appellent et passer à `Depends(require_admin_user)` dans la signature de chaque endpoint
- **Endpoints non-admin qui acceptent `admin`** : ne pas toucher — ex : `chat.py` ou autres routers qui font `if user.role in {"admin", "ops"}` — ceux-ci conservent leur logique propre

### Attention : périmètre de migration
- Auditer **tous** les fichiers sous `backend/app/api/v1/routers/` qui contiennent `admin` ou `ops` dans leur nom — vérifier lesquels ont des checks inline à migrer
- Ne migrer **que** les endpoints qui sont admin-only. Les endpoints mixtes (admin + autre rôle) conservent leur propre guard

### Project Structure Notes
- Aucun nouveau fichier — modification de `auth.py` uniquement
- Les routers migrés ne changent pas de structure, seule la dépendance change dans la signature de chaque endpoint

### References
- `backend/app/api/dependencies/auth.py` — `require_authenticated_user`, `AuthenticatedUser` [Source: session context]
- `backend/app/api/v1/routers/admin_llm.py` — helper `_ensure_admin_role()` à supprimer [Source: session context]
- `backend/app/core/rbac.py` — `VALID_ROLES` [Source: session context]
- Epic 65 FR65-11 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-2`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
