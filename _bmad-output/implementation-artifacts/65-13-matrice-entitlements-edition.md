# Story 65.13 : Matrice entitlements — édition quotas et feature flags avec audit

Status: ready-for-dev

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

- [ ] Créer l'endpoint `PATCH /api/v1/admin/entitlements/{plan_code}/{feature_code}` dans `admin_entitlements.py` (AC: 2, 3)
  - [ ] Guard `require_admin_user`
  - [ ] Body : `{ quota_value?: int, access_mode?: str, is_teaser?: bool }` — champs éditables uniquement
  - [ ] Validation stricte : seuls `quota_value`, `access_mode`, `is_teaser` sont acceptés — tout autre champ → 422
  - [ ] Lire la valeur actuelle (avant) depuis DB
  - [ ] Mettre à jour le champ en DB
  - [ ] Générer l'audit log via `AuditService` avec `before` et `after`
- [ ] Créer le schéma `EntitlementUpdateRequest` (AC: 2, 3)
  - [ ] Validation Pydantic : `access_mode` doit être dans `{"disabled", "quota", "unlimited"}` si fourni
  - [ ] Au moins un champ doit être non null
- [ ] Mettre à jour `frontend/src/pages/admin/AdminEntitlementsPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Bouton "Mode édition" → état `isEditing: boolean`
  - [ ] En mode édition : bandeau d'avertissement visible + cellules éditables interactives
  - [ ] Cellule `quota_value` : `<input type="number">` en mode édition, `<span>` en mode lecture
  - [ ] Cellule `access_mode` : `<select>` (disabled/quota/unlimited) en mode édition
  - [ ] Cellule `is_teaser` : `<input type="checkbox">` en mode édition
  - [ ] Cellule "llm_variant" : toujours `<span>` avec mention "Configurable dans Prompts & Personas" (AC: 4)
  - [ ] Au `blur` ou `onChange` → ouvrir modale de confirmation avec plan/feature/avant/après
  - [ ] Après confirmation → PATCH + rafraîchissement de la matrice
- [ ] CSS pour le mode édition (AC: 1)
  - [ ] `.matrix--editing` : bandeau avec `var(--primary)` ou `var(--danger)` light
  - [ ] `.cell--editable` : border `var(--primary)` en mode édition
  - [ ] Input/select dans les cellules : sans border propre, inherit du style de la cellule

## Dev Notes

### Champs éditables — périmètre strict
Seuls `quota_value`, `access_mode`, `is_teaser` sont modifiables depuis cet écran. Le backend doit refuser toute tentative de modifier d'autres champs (ex : `llm_variant`, `reset_period`). Cette restriction est une exigence FR65-4b.

### Double confirmation
L'AC 2 requiert une modale affichant les valeurs **avant et après** avant de confirmer. Le frontend doit :
1. Capturer la valeur "avant" au moment de l'entrée en mode édition (ou depuis l'état courant de la matrice)
2. Afficher dans la modale : `plan: basic, feature: chat, quota: 10 → 20`
3. Envoyer le PATCH seulement après confirmation explicite

### Audit log format
```json
{
  "action": "entitlement_quota_updated",
  "target_type": "plan_entitlement",
  "target_id": "basic:chat",
  "details": {
    "plan_code": "basic",
    "feature_code": "chat",
    "before": {"quota_value": 10},
    "after": {"quota_value": 20}
  }
}
```

### Mode édition vs lecture
Le bouton "Mode édition" peut être conditionné par `canEdit("entitlements")` depuis `AdminPermissionsContext` (Story 65-4 crée le contexte, Story 65-21 finalise). Pour MVP : `canEdit` retourne `true` pour tous les admins.

### Project Structure Notes
- Modifier : `backend/app/api/v1/routers/admin_entitlements.py` (ajout PATCH endpoint)
- Modifier : `frontend/src/pages/admin/AdminEntitlementsPage.tsx` + `.css`
- Prerequisite : Story 65-12 (matrice consultation créée)

### References
- Modèles entitlements Epic 61 : `ProductEntitlements` [Source: sprint-status.yaml]
- `AuditEventModel` : `backend/app/infra/db/models/audit_event.py` [Source: session context]
- Epic 65 FR65-4b, FR65-15 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-13`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
