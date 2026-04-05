# Story 65.13 : Matrice entitlements — édition quotas et feature flags avec audit

Status: done

## Story

En tant qu'**admin ops**,  
je veux pouvoir modifier les valeurs de quotas et les flags de features directement depuis la matrice,  
afin d'ajuster les droits d'accès sans déploiement et avec traçabilité complète.

## Acceptance Criteria

1. **Given** l'admin est sur la vue matrice  
   **When** il active le mode édition (bouton "Modifier" explicite)  
   **Then** les cellules éditables (quotas, mode d'accès, flags teaser) deviennent interactives  
   **And** un bandeau "Mode édition — toute modification génère un audit log" est visible

2. **Given** l'admin modifie la valeur d'un quota dans une cellule  
   **When** il valide la cellule  
   **Then** une modale de confirmation s'ouvre affichant : plan, feature, valeur avant, valeur après  
   **And** l'admin doit confirmer explicitement (bouton "Confirmer la modification")

3. **Given** la modification est confirmée  
   **When** la requête est envoyée  
   **Then** la valeur en DB est mise à jour  
   **And** un audit log est généré : `action: "entitlement_quota_updated"`, `target_type: "plan_entitlement"`, `details: {plan_code, feature_code, before: {quota: N}, after: {quota: M}}`  
   **And** la matrice se rafraîchit avec la nouvelle valeur

4. **Given** l'admin tente de modifier un variant de prompt LLM depuis la matrice  
   **When** il inspecte la cellule correspondante  
   **Then** le champ est en lecture seule avec la mention "Configurable dans Prompts & Personas"

## Tasks / Subtasks

- [x] Créer l'endpoint `PATCH /api/v1/admin/entitlements/{plan_id}/{feature_id}` (AC: 2, 3)
  - [x] Body : `{ quota_limit, access_mode, is_enabled }`
  - [x] Audit log complet avec before/after
  - [x] Utilisation de `.unique()` pour les requêtes SQLAlchemy avec eager load
- [x] Créer le schéma `AdminEntitlementUpdate` dans `admin_entitlements.py`
- [x] Mettre à jour `frontend/src/pages/admin/AdminEntitlementsPage.tsx` (AC: 1, 2, 3, 4)
  - [x] Toggle `isEditing` state
  - [x] Rendu conditionnel des inputs/selects en mode édition
  - [x] Modale de confirmation native (`window.confirm`)
  - [x] Mutation React Query et invalidation cache
- [x] CSS pour le mode édition dans `AdminEntitlementsPage.css` (AC: 1)
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_entitlements_api.py`

### File List
- `backend/app/api/v1/routers/admin_entitlements.py`
- `backend/app/api/v1/schemas/admin_entitlements.py`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `backend/app/tests/integration/test_admin_entitlements_api.py`
