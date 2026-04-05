# Story 65.19 : Journal d'audit global — consultation filtrée

Status: ready-for-dev

## Story

En tant qu'**admin (super-admin futur)**,  
je veux consulter le journal d'audit global de toutes les actions admin,  
afin d'avoir une traçabilité complète de qui a fait quoi et quand sur le système.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/settings` (section "Journal d'audit")  
   **When** la page charge  
   **Then** la liste des événements d'audit récents est affichée (50 par page, paginée) avec : timestamp, acteur (email masqué partiellement), action, cible (type + id masqué), statut

2. **Given** l'admin applique des filtres  
   **When** il filtre par acteur, type d'action (ex : `account_suspended`, `prompt_rollback`) ou période  
   **Then** la liste se met à jour avec les événements correspondants

3. **Given** l'admin clique sur un événement d'audit  
   **When** le détail s'ouvre  
   **Then** le contenu complet de `details` est visible : `before`, `after`, `reason` si présents  
   **And** un lien vers la fiche utilisateur cible est présent si `target_type = "user"`

4. **Given** l'admin exporte le journal filtré  
   **When** il clique "Exporter" et confirme (double confirmation)  
   **Then** un fichier CSV est généré et téléchargé  
   **And** un audit log est généré : `action: "audit_log_exported"`, `details: {filters_applied, record_count}`

## Tasks / Subtasks

- [ ] Créer le router `backend/app/api/v1/routers/admin_audit.py` (AC: 1, 2, 3, 4)
  - [ ] `GET /api/v1/admin/audit?actor=&action=&target_type=&period=&page=1&per_page=50`
  - [ ] Filtre `actor` : ILIKE sur `actor_user_id` via join `users.email` — ou sur `actor_role`
  - [ ] Filtre `action` : exact match sur `audit_events.action`
  - [ ] Pagination offset : `LIMIT 50 OFFSET (page-1)*50`, inclure `total_count` dans la réponse
  - [ ] Masquage : email de l'acteur → `email[:3] + "***" + email[email.index("@"):]`, target_id → `str(id)[:4] + "..."` si numérique
  - [ ] `POST /api/v1/admin/audit/export` body: `{filters: {...}}` — génère CSV + audit log
  - [ ] Guard `require_admin_user` sur tous les endpoints
- [ ] Implémenter l'export CSV (AC: 4)
  - [ ] Python stdlib `csv.DictWriter` — pas de lib externe
  - [ ] Colonnes : timestamp, actor_email (masqué), actor_role, action, target_type, target_id (masqué), status, before, after, reason
  - [ ] Retourner comme `StreamingResponse` avec `Content-Disposition: attachment; filename=audit_log.csv`
  - [ ] Limiter à 5 000 lignes par export (MVP)
  - [ ] Générer l'audit log AVANT de retourner le fichier (pour que l'export lui-même soit tracé)
- [ ] Créer `frontend/src/pages/admin/AdminSettingsPage.tsx` avec section "Journal d'audit" (AC: 1, 2, 3, 4)
  - [ ] Ou sous-composant `AdminAuditLogSection.tsx` dans la page Settings
  - [ ] Filtres : acteur (input text), type d'action (select ou autocomplete), période
  - [ ] Liste paginée avec navigation page précédente/suivante
  - [ ] Clic sur ligne → panneau de détail avec `details` JSON formaté
  - [ ] Lien vers `/admin/users/{target_id}` si `target_type = "user"` (AC: 3)
  - [ ] Bouton "Exporter CSV" + modale de double confirmation (cocher une case + confirmer)
- [ ] CSS dans `AdminSettingsPage.css` (AC: 1)

## Dev Notes

### AuditEventModel existant
`AuditEventModel` dans `backend/app/infra/db/models/audit_event.py` est la table source. Champs : `id`, `request_id`, `actor_user_id` (FK), `actor_role`, `action`, `target_type`, `target_id`, `status`, `details` (JSON), `created_at`.

Les champs `before`/`after`/`reason` sont dans `details` (JSON) — le frontend doit afficher `details.before`, `details.after`, `details.reason` si présents.

### Masquage des données sensibles
- Email de l'acteur : `email[:3] + "***@" + email.split("@")[1]` (ex : `adm***@test.com`)
- target_id : masquer si c'est un ID numérique d'utilisateur — afficher partiellement pour les autres types
- Le masquage est côté backend — ne jamais retourner un email complet dans ce endpoint

### Double confirmation pour l'export
L'AC 4 requiert une double confirmation : 
1. Modal s'ouvre avec avertissement "Cet export sera journalisé"
2. Checkbox "Je confirme vouloir exporter ces données"
3. Bouton "Confirmer l'export" (actif seulement si checkbox cochée)

### Pagination
Implémenter une pagination simple côté backend (offset) avec `total_count` dans la réponse. Le frontend affiche "Page N / M" et des boutons Précédent/Suivant. Pas de cursor-based pagination nécessaire pour le MVP.

### Project Structure Notes
- Nouveau fichier backend : `admin_audit.py` router
- Nouveau fichier frontend : `AdminSettingsPage.tsx` (ou enrichissement si existe déjà) + `.css`
- Intégrer sous `/admin/settings` dans la navigation (Story 65-4)

### References
- `backend/app/infra/db/models/audit_event.py` — `AuditEventModel` [Source: session context]
- `AuditService` : `backend/app/services/` [Source: architecture]
- Epic 65 FR65-9, FR65-14 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-19`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
