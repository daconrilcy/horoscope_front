# Story 65.15 : Observabilité technique — incidents, erreurs applicatives, logs LLM, replay

Status: ready-for-dev

## Story

En tant qu'**admin technique (ops)**,  
je veux un cockpit technique centralisant erreurs applicatives, incidents Stripe et logs LLM,  
afin de diagnostiquer et rejouer les cas problématiques sans accès direct aux serveurs.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/logs`  
   **When** la page charge  
   **Then** trois onglets sont disponibles : "Erreurs applicatives", "Logs LLM", "Événements Stripe"

2. **Given** l'onglet "Logs LLM" est actif  
   **When** l'admin applique des filtres (use case, statut succès/échec, période)  
   **Then** la liste filtrée des appels LLM s'affiche (timestamp, use case, statut, durée, tokens, error_code si échec)

3. **Given** l'admin sélectionne un log LLM en échec  
   **When** il clique "Rejouer cet appel"  
   **Then** une modale de confirmation s'affiche avec le contexte de l'appel (use case, persona, prompt version)  
   **And** après confirmation, le service de replay est appelé et le résultat est affiché (succès/échec, nouvelle réponse)  
   **And** un audit log est généré : `action: "llm_call_replayed"`, `details: {original_log_id, replay_result}`

4. **Given** l'onglet "Événements Stripe" est actif  
   **When** la liste s'affiche  
   **Then** les webhooks Stripe non traités ou en erreur sont mis en évidence avec leur type d'événement et le motif d'échec

5. **Given** l'admin consulte les alertes sur quotas  
   **When** un utilisateur est à > 90% de son quota  
   **Then** il apparaît dans une section "Alertes quotas" avec son email (masqué partiellement), son plan et son taux de consommation

## Tasks / Subtasks

- [ ] Créer le router `backend/app/api/v1/routers/admin_logs.py` (AC: 1, 2, 3, 4, 5)
  - [ ] `GET /api/v1/admin/logs/llm?use_case=&status=&period=7d&page=1` — logs LLM filtrés paginés
  - [ ] `POST /api/v1/admin/logs/llm/{log_id}/replay` — déclenche le replay via `ReplayService`
  - [ ] `GET /api/v1/admin/logs/stripe` — webhooks Stripe non traités ou en erreur
  - [ ] `GET /api/v1/admin/logs/errors` — erreurs applicatives (HTTP 5xx, exceptions)
  - [ ] `GET /api/v1/admin/logs/quota-alerts` — users à > 90% de quota
  - [ ] Guard `require_admin_user` sur tous les endpoints
- [ ] Intégrer `ReplayService` pour le replay LLM (AC: 3)
  - [ ] `ReplayService` est déjà implémenté dans `admin_llm.py` — extraire/utiliser le service directement
  - [ ] Audit log après replay : `AuditService.create_event(action="llm_call_replayed", ...)`
- [ ] Implémenter la source des erreurs applicatives (AC: 1)
  - [ ] Vérifier si le projet log les erreurs HTTP 5xx dans une table DB — si oui, requêter cette table
  - [ ] Si non (logs fichiers), retourner les 50 dernières entrées de `audit_events` avec `status = "error"` comme fallback MVP
- [ ] Implémenter les événements Stripe (AC: 4)
  - [ ] Vérifier si le projet stocke les webhooks Stripe en DB (probable dans Epic 61) — chercher une table `stripe_events` ou `webhook_events`
  - [ ] Filtrer les webhooks avec `status = "failed"` ou `processed = false`
- [ ] Implémenter les alertes quotas (AC: 5)
  - [ ] Query : users où `usage_current / quota_limit > 0.9` — identifier les tables de quotas canoniques
  - [ ] Masquer l'email : `email[:3] + "***" + email[email.index("@"):]`
- [ ] Créer `frontend/src/pages/admin/AdminLogsPage.tsx` (AC: 1, 2, 3, 4, 5)
  - [ ] Onglets : "Erreurs", "Logs LLM", "Stripe"
  - [ ] Section "Alertes quotas" en haut de page (visible quel que soit l'onglet actif)
  - [ ] Onglet "Logs LLM" : filtres + liste + bouton "Rejouer" sur les lignes en échec
  - [ ] Modale de confirmation replay avec contexte de l'appel
  - [ ] Résultat du replay affiché dans la modale (toast ou dans la modale)
- [ ] CSS dans `AdminLogsPage.css` (AC: 1, 3)

## Dev Notes

### ReplayService existant
`ReplayService` est déjà implémenté dans `backend/app/api/v1/routers/admin_llm.py`. Avant de créer de nouveaux endpoints, **lire `admin_llm.py`** pour comprendre comment le replay est actuellement exposé. Idéalement, déplacer la logique dans un service `backend/app/services/replay_service.py` si ce n'est pas déjà fait, puis l'utiliser depuis `admin_logs.py`.

### Distinction avec Story 65-14
- Story 65-14 = vue **métier** agrégée (KPIs, tendances, coûts)
- Cette story = vue **technique** détaillée (logs filtrables, incidents, replay individuel)
- Ne pas dupliquer les agrégats de 65-14 ici

### Stripe webhooks
L'Epic 61 a implémenté le traitement des webhooks Stripe. Chercher la table/modèle qui stocke l'historique des événements Stripe — probablement `stripe_webhook_event` ou équivalent. Si aucune table de stockage n'existe, implémenter un GET simplifié qui liste les abonnements `user_subscriptions` avec `failure_reason IS NOT NULL` comme proxy pour les incidents Stripe.

### NFR20 : réponses hors-scope
L'exigence NFR20 demande que les réponses LLM hors-scope soient détectables depuis cet écran. Vérifier si `LlmCallLogModel` a un champ `out_of_scope: bool` ou `quality_score`. Si oui, ajouter un filtre correspondant dans le endpoint logs LLM.

### Project Structure Notes
- Nouveau fichier backend : `admin_logs.py` router + schemas si nécessaire
- Nouveau frontend : `AdminLogsPage.tsx` + `.css`
- `ReplayService` : réutiliser depuis `admin_llm.py` sans dupliquer

### References
- `backend/app/api/v1/routers/admin_llm.py` — `ReplayService` existant [Source: session context]
- `LlmCallLogModel`, `LlmPersonaModel`, `LlmPromptVersionModel` [Source: session context]
- Epic 65 FR65-7, NFR20 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-15`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
