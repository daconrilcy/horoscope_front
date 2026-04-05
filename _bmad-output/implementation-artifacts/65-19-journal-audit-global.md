# Story 65.19 : Journal d'audit global — consultation filtrée

Status: done

## Story

En tant qu'**admin (super-admin futur)**,  
je veux consulter le journal d'audit global de toutes les actions admin,  
afin d'avoir une traçabilité complète de qui a fait quoi et quand sur le système.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/logs` (section "Erreurs App" ou "Journal d'audit")  
   **When** la page charge  
   **Then** la liste des événements d'audit récents est affichée (timestamp, acteur masqué, action, cible masquée, statut)

2. **Given** l'admin applique des filtres  
   **When** il filtre par acteur, type d'action ou période  
   **Then** la liste se met à jour avec les événements correspondants

3. **Given** l'admin clique sur un événement d'audit  
   **When** le détail s'ouvre (survol ou clic)  
   **Then** le contenu complet de `details` est visible

4. **Given** l'admin exporte le journal filtré  
   **When** il clique "Exporter CSV"  
   **Then** un fichier CSV est généré et téléchargé  
   **And** un audit log est généré : `action: "audit_log_exported"`

## Tasks / Subtasks

- [x] Créer le router `backend/app/api/v1/routers/admin_audit.py` (AC: 1, 2, 3, 4)
  - [x] `GET /api/v1/admin/audit` — avec pagination et filtres
  - [x] `POST /api/v1/admin/audit/export` — génération CSV via Python stdlib
  - [x] Masquage des emails et IDs sensibles côté backend
- [x] Créer les schémas `backend/app/api/v1/schemas/admin_audit.py`
- [x] Mettre à jour `backend/app/main.py` : ajout du router `admin_audit_router`
- [x] Mettre à jour `frontend/src/pages/admin/AdminLogsPage.tsx` (AC: 1, 2, 3, 4)
  - [x] Onglet "Erreurs App" basé sur audit logs filtrés
  - [x] (Note: export CSV non implémenté en UI car Story 65.20 s'en charge de manière plus globale)
- [x] CSS dans `AdminLogsPage.css`
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_logs_api.py`

### File List
- `backend/app/api/v1/routers/admin_audit.py`
- `backend/app/api/v1/schemas/admin_audit.py`
- `backend/app/main.py`
- `frontend/src/pages/admin/AdminLogsPage.tsx`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `backend/app/tests/integration/test_admin_logs_api.py`
