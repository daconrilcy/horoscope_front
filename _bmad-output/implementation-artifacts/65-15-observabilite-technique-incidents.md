# Story 65.15 : Observabilité technique — incidents, erreurs applicatives, logs LLM, replay

Status: done

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

- [x] Créer le router `backend/app/api/v1/routers/admin_logs.py` (AC: 1, 4, 5)
  - [x] `GET /api/v1/admin/logs/errors`
  - [x] `GET /api/v1/admin/logs/stripe`
  - [x] `GET /api/v1/admin/logs/quota-alerts`
- [x] Intégrer les logs LLM existants via `admin_llm.py` (AC: 2)
- [x] Créer les schémas `backend/app/api/v1/schemas/admin_logs.py`
- [x] Mettre à jour `backend/app/main.py` : ajout du router `admin_logs_router`
- [x] Créer `frontend/src/pages/admin/AdminLogsPage.tsx` (AC: 1, 2, 3, 4, 5)
  - [x] Gestion des onglets techniques
  - [x] Bandeau d'alertes quotas dynamiques
  - [x] Liste des erreurs app et événements Stripe
- [x] CSS dans `AdminLogsPage.css`
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_logs_api.py`

### File List
- `backend/app/api/v1/routers/admin_logs.py`
- `backend/app/api/v1/schemas/admin_logs.py`
- `backend/app/main.py`
- `frontend/src/pages/admin/AdminLogsPage.tsx`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `backend/app/tests/integration/test_admin_logs_api.py`
