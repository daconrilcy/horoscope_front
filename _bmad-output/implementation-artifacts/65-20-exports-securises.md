# Story 65.20 : Exports sécurisés — utilisateurs, générations, billing

Status: ready-for-dev

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
   **And** un audit log : `action: "sensitive_data_exported"`, `details: {export_type, filters, record_count, actor_user_id}`

4. **Given** les données exportées contiennent des identifiants Stripe ou des données personnelles  
   **When** le fichier est généré  
   **Then** les IDs Stripe sont présents mais les données bancaires ne le sont pas (numéros de carte jamais exportés)

## Tasks / Subtasks

- [ ] Créer les endpoints dans `backend/app/api/v1/routers/admin_exports.py` (AC: 1, 3, 4)
  - [ ] `POST /api/v1/admin/exports/users` body: `{period?: {start, end}}` — export CSV utilisateurs
  - [ ] `POST /api/v1/admin/exports/generations` body: `{period?: {start, end}, format: "csv"|"json"}` — export générations LLM
  - [ ] `POST /api/v1/admin/exports/billing` body: `{period?: {start, end}}` — export billing
  - [ ] Guard `require_admin_user` sur tous
  - [ ] Générer l'audit log **avant** de retourner le fichier (traçabilité garantie même si la connection coupe)
  - [ ] Limite : 5 000 lignes max (MVP synchrone) — retourner un header `X-Export-Truncated: true` si tronqué
- [ ] Implémenter l'export utilisateurs (AC: 1, 4)
  - [ ] Colonnes : id, email, role, plan_code, subscription_status, created_at, is_suspended, email_unsubscribed
  - [ ] Exclure : password_hash, tokens de session, toute donnée bancaire
  - [ ] ID Stripe (`stripe_customer_id`) : inclus mais PAS les données de carte
- [ ] Implémenter l'export générations (AC: 1, 3)
  - [ ] Colonnes : id, user_id (pas email), use_case, status, tokens_prompt, tokens_completion, duration_ms, created_at
  - [ ] Exclure le contenu des messages/réponses (données personnelles sensibles)
- [ ] Implémenter l'export billing (AC: 1, 4)
  - [ ] Colonnes : user_id, email, plan_code, subscription_status, monthly_price_cents, started_at, failure_reason
  - [ ] Exclure : informations de carte de paiement (jamais stockées en DB de toute façon)
- [ ] Adapter `frontend/src/pages/admin/AdminSettingsPage.tsx` — section "Exports" (AC: 1, 2, 3)
  - [ ] Liste des 3 types d'export avec description
  - [ ] Modale d'export : avertissement + filtre période + checkbox confirmation + bouton confirmer
  - [ ] Le bouton "Confirmer l'export" est désactivé tant que la checkbox n'est pas cochée
  - [ ] Feedback pendant la génération (spinner / "Génération en cours...")
  - [ ] Download déclenché automatiquement quand le fichier est prêt
- [ ] CSS dans `AdminSettingsPage.css` pour la section exports (AC: 2)

## Dev Notes

### StreamingResponse FastAPI
Utiliser `StreamingResponse` pour les exports CSV :
```python
from fastapi.responses import StreamingResponse
import csv, io

def generate_csv(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=[...])
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)
    yield buffer.read()

return StreamingResponse(
    generate_csv(rows),
    media_type="text/csv",
    headers={"Content-Disposition": "attachment; filename=users_export.csv"}
)
```

### Audit log obligatoire AVANT le fichier
L'audit log doit être créé **avant** de générer et retourner le fichier. Cela garantit que même si la connexion est coupée pendant le download, l'action est tracée. Utiliser `await AuditService.create_event(...)` avant le `return StreamingResponse(...)`.

### Données bancaires — jamais exportées
Les numéros de carte, CVV et informations de paiement ne sont jamais stockés dans la DB applicative (stockés chez Stripe uniquement). Donc l'AC 4 est naturellement respecté — documenter ce point dans le code pour que les futurs développeurs comprennent pourquoi.

### Double confirmation frontend
Pattern identique à Story 65-19 (export journal d'audit) :
1. Bouton "Exporter [type]" → ouvre modale
2. Modale : avertissement + filtre période + `<input type="checkbox" id="confirm-export">` + label
3. Bouton "Confirmer l'export" : `disabled={!confirmed}` where `confirmed` = état de la checkbox

### Project Structure Notes
- Nouveau fichier backend : `admin_exports.py` router
- Modifier : `AdminSettingsPage.tsx` (ajout section Exports)
- Prerequisite : Story 65-19 (page Settings créée)

### References
- `backend/app/infra/db/models/user.py`, `billing.py`, `audit_event.py` [Source: session context]
- `LlmCallLogModel` pour l'export générations [Source: architecture]
- Epic 65 FR65-9, NFR5, NFR8 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-20`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
