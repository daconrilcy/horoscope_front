# Story 65.11 : Support — consultation tickets et contenus signalés

Status: done

## Story

En tant qu'**admin support**,  
je veux consulter les tickets ouverts et les contenus signalés depuis l'espace admin,  
afin de traiter les demandes utilisateurs et modérer le contenu problématique.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/support`  
   **When** la page charge  
   **Then** la liste des tickets support ouverts est affichée (titre, auteur, statut, date, catégorie)  
   **And** un filtre par statut (ouvert / en cours / résolu) et par catégorie est disponible

2. **Given** l'admin clique sur un ticket  
   **When** le détail s'ouvre  
   **Then** le contexte complet est visible : description initiale, historique des échanges, actions admin déjà effectuées sur ce dossier (audit trail du ticket)  
   **And** un lien direct vers la fiche utilisateur correspondante est présent

3. **Given** l'admin accède à la section "Contenus signalés"  
   **When** la liste s'affiche  
   **Then** chaque entrée montre : type de contenu (génération / chat), extrait, utilisateur, date du signalement  
   **And** les actions disponibles sont : marquer comme traité, accéder à la fiche utilisateur

4. **Given** l'admin effectue une action sur un ticket ou un contenu signalé  
   **When** l'action est complétée  
   **Then** un audit log est généré : `action: "support_ticket_action"` ou `"flagged_content_reviewed"`, acteur, cible, date

## Tasks / Subtasks

- [x] Migration Alembic : créer table `flagged_contents` (AC: 3)
- [x] Créer le router `backend/app/api/v1/routers/admin_support.py` (AC: 1, 2, 3, 4)
  - [x] `GET /api/v1/admin/support/tickets`
  - [x] `GET /api/v1/admin/support/tickets/{ticket_id}`
  - [x] `PATCH /api/v1/admin/support/tickets/{ticket_id}` (update statut)
  - [x] `GET /api/v1/admin/support/flagged-content`
  - [x] `PATCH /api/v1/admin/support/flagged-content/{content_id}` (review)
- [x] Créer les schémas Pydantic `backend/app/api/v1/schemas/admin_support.py`
- [x] Le détail ticket expose un `audit_trail` backend pour les actions admin déjà effectuées
- [x] Créer `frontend/src/pages/admin/AdminSupportPage.tsx` (AC: 1, 3)
  - [x] Onglets Tickets / Contenus signalés
  - [x] Filtres de statut pour les tickets
  - [x] Actions de revue pour les contenus signalés
- [x] CSS dans `AdminSupportPage.css`
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_support_api.py`

### File List
- `backend/app/infra/db/models/flagged_content.py`
- `backend/migrations/versions/133a10b2582b_create_flagged_contents_table.py`
- `backend/app/api/v1/routers/admin_support.py`
- `backend/app/api/v1/schemas/admin_support.py`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.css`
- `backend/app/tests/integration/test_admin_support_api.py`
