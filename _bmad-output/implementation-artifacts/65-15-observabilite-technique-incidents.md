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

### Completion Notes List

- Revue AI du 2026-04-06 : correction des alertes quotas pour lire le vrai plan et la vraie limite depuis la matrice d'entitlements, ajout des filtres LLM côté frontend, et remplacement du faux bouton replay par une modale de confirmation fonctionnelle.

## Senior Developer Review (AI)

- Corrigé un défaut bloquant dans `admin_logs.py` : la requête de quotas était laissée dans un état de démonstration avec un commentaire `very broken join`, un plan `unknown` et une limite hardcodée.
- Corrigé un défaut AC côté frontend : le replay LLM n'était pas exécutable et l'écran n'exposait pas les filtres annoncés. La story reste `done` après mise en conformité du cockpit technique livré.
