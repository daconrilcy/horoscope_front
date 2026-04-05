# Story 65.11 : Support — consultation tickets et contenus signalés

Status: ready-for-dev

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

- [ ] Créer le router `backend/app/api/v1/routers/admin_support.py` (AC: 1, 2, 3, 4)
  - [ ] `GET /api/v1/admin/support/tickets?status=open&category=all` — liste tickets filtrée
  - [ ] `GET /api/v1/admin/support/tickets/{ticket_id}` — détail ticket avec historique
  - [ ] `PATCH /api/v1/admin/support/tickets/{ticket_id}` body: `{status: str}` — update statut + audit
  - [ ] `GET /api/v1/admin/support/flagged-content` — liste contenus signalés
  - [ ] `PATCH /api/v1/admin/support/flagged-content/{content_id}` body: `{reviewed: true}` — marquer traité + audit
  - [ ] Guard `require_admin_user` sur tous les endpoints
- [ ] Explorer les tables support existantes avant d'implémenter (AC: 1, 2, 3)
  - [ ] Vérifier `support_incidents`, `support_ticket_category` dans les modèles DB
  - [ ] Vérifier si une table "contenus signalés" existe ou doit être créée
  - [ ] Si les tables n'existent pas : créer via Alembic (migration) — schema minimal: `id`, `user_id`, `content_type`, `content_ref_id`, `excerpt`, `reported_at`, `reviewed_at`, `reviewed_by`
- [ ] Créer les schémas Pydantic `backend/app/api/v1/schemas/admin_support.py` (AC: 1, 2, 3)
- [ ] Créer `frontend/src/pages/admin/AdminSupportPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Deux onglets : "Tickets" et "Contenus signalés"
  - [ ] Liste tickets avec filtres statut/catégorie
  - [ ] Détail ticket dans un panneau latéral ou une sous-route
  - [ ] Liste contenus signalés avec bouton "Marquer traité"
  - [ ] Lien vers la fiche utilisateur (navigation vers `/admin/users/{user_id}`)
- [ ] CSS dans `frontend/src/pages/admin/AdminSupportPage.css` (AC: 1, 2, 3)

## Dev Notes

### Tables support existantes
**Avant d'écrire du code**, vérifier l'existence de :
- `support_incidents` — probablement utilisée dans Epic 6 (Story 6-1 : "outillage support compte incidents")
- `support_ticket_category` — catégories de tickets
- Tables de "flagged content" — vérifier si un mécanisme de signalement existe déjà

Si les tables existent : utiliser telles quelles. Si elles manquent : créer des migrations minimales.

### Audit trail des tickets
Les actions admin sur les tickets doivent être tracées dans `audit_events` via `AuditService`. Format :
- `action: "support_ticket_action"`, `target_type: "support_ticket"`, `target_id: ticket_id`
- `details: {action_type: "status_changed", from: "open", to: "in_progress"}`

### Lien fiche utilisateur
Chaque ticket et chaque contenu signalé doit avoir un lien direct vers `/admin/users/{user_id}` — la page `AdminUserDetailPage` est créée en Story 65-8.

### Project Structure Notes
- Nouveaux fichiers backend : `admin_support.py` router + schemas
- Nouveau fichier frontend : `AdminSupportPage.tsx` + `.css`
- Enregistrer le router dans le fichier central

### References
- `backend/app/infra/db/models/audit_event.py` — `AuditEventModel` [Source: session context]
- Epic 6, Story 6-1 : support incidents existants [Source: sprint-status.yaml]
- Epic 65 FR65-8 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-11`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
