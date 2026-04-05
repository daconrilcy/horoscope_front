# Story 65.20 : Exports sécurisés — utilisateurs, générations, billing

Status: done

## Story

En tant qu'**admin (super-admin futur)**,  
je veux exporter des données sensibles en format structuré avec double confirmation,  
afin de produire des rapports ou de transférer des données en respectant les processus de sécurité.

## Acceptance Criteria

1. **Given** l'admin accède à la section "Exports" dans `/admin/settings`  
   **When** la page charge  
   **Then** les exports disponibles sont listés : "Liste utilisateurs (CSV)", "Historique générations (CSV/JSON)", "Données billing (CSV)"

2. **Given** l'admin clique sur un export  
   **When** la modale s'ouvre  
   **Then** un avertissement explicite est visible : "Cet export contient des données sensibles. Il sera journalisé."  
   **And** un champ de filtre de période est disponible  
   **And** une double confirmation est requise (cocher une case + cliquer "Confirmer l'export")

3. **Given** l'export est confirmé  
   **When** le fichier est généré  
   **Then** le download démarre  
   **And** un audit log : `action: "sensitive_data_exported"`, `details: {export_type, filters, record_count}`

4. **Given** les données exportées contiennent des identifiants Stripe ou des données personnelles  
   **When** le fichier est généré  
   **Then** les IDs Stripe sont présents mais les données bancaires ne le sont pas (numéros de carte jamais exportés)

## Tasks / Subtasks

- [x] Créer les endpoints dans `backend/app/api/v1/routers/admin_exports.py` (AC: 1, 3, 4)
  - [x] `POST /api/v1/admin/exports/users`
  - [x] `POST /api/v1/admin/exports/generations`
  - [x] `POST /api/v1/admin/exports/billing`
  - [x] Audit log obligatoire AVANT le retour du fichier
  - [x] Masquage des données sensibles
- [x] Créer les schémas `backend/app/api/v1/schemas/admin_exports.py`
- [x] Mettre à jour `backend/app/main.py` : ajout du router `admin_exports_router`
- [x] Mettre à jour `frontend/src/pages/admin/AdminSettingsPage.tsx` (AC: 1, 2, 3)
  - [x] Section Exports avec 3 types
  - [x] Modale d'export avec filtres et double confirmation
  - [x] Gestion du téléchargement du Blob
- [x] CSS dans `AdminSettingsPage.css` pour les modales et cards d'export
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_exports_api.py`

### File List
- `backend/app/api/v1/routers/admin_exports.py`
- `backend/app/api/v1/schemas/admin_exports.py`
- `backend/app/main.py`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `backend/app/tests/integration/test_admin_exports_api.py`
