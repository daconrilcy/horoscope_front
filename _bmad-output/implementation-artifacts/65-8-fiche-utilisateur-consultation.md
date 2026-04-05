# Story 65.8 : Fiche utilisateur — recherche et consultation complète

Status: ready-for-dev

## Story

En tant qu'**admin support**,  
je veux retrouver un utilisateur et consulter sa fiche complète,  
afin de comprendre son état exact et répondre efficacement à toute demande.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/users`  
   **When** il saisit un email ou un ID numérique dans la barre de recherche et valide  
   **Then** la liste des utilisateurs correspondants s'affiche (nom/email, plan, statut, date d'inscription)  
   **And** la recherche par email partiel fonctionne (ILIKE sur PostgreSQL)

2. **Given** l'admin clique sur un utilisateur dans les résultats  
   **When** la fiche s'ouvre  
   **Then** les sections suivantes sont visibles :
   - Profil : email, rôle, date de création, statut (actif / suspendu / verrouillé)
   - Plan actif : code plan, statut abonnement, date de début
   - Stripe : ID client Stripe (masqué partiellement), statut abonnement Stripe, méthode de paiement (type + 4 derniers chiffres), dernière facture (date + montant)
   - Quotas : consommés vs autorisés pour la période courante (par feature)
   - Générations récentes : 20 dernières (use case, date, statut succès/échec, tokens utilisés)
   - Tickets support : 5 derniers ouverts (titre, statut, date)
   - Audit : 10 derniers événements d'audit le concernant (action, acteur, date)

3. **Given** l'admin consulte la fiche  
   **When** les données Stripe sont affichées  
   **Then** l'ID Stripe est masqué (`cus_xxx...xxx` — seuls les 4 premiers et 4 derniers caractères visibles)  
   **And** la révélation complète nécessite un clic explicite qui génère un audit log `action: "sensitive_data_revealed"`

## Tasks / Subtasks

- [ ] Créer le router `backend/app/api/v1/routers/admin_users.py` (AC: 1, 2, 3)
  - [ ] `GET /api/v1/admin/users?q={email_or_id}&limit=20` : recherche ILIKE sur email, ou match exact sur id
  - [ ] `GET /api/v1/admin/users/{user_id}` : fiche complète agrégée
  - [ ] Guard `require_admin_user` sur les deux endpoints
- [ ] Implémenter la recherche (AC: 1)
  - [ ] Query : `SELECT * FROM users WHERE email ILIKE '%query%' OR id = query LIMIT 20`
  - [ ] Retourner email, id, role, plan_code (JOIN user_subscriptions), statut, created_at
- [ ] Implémenter la fiche complète `/users/{user_id}` (AC: 2, 3)
  - [ ] Profil : depuis `users`
  - [ ] Plan / Abonnement : JOIN `user_subscriptions` + `billing_plans`
  - [ ] Stripe : depuis `stripe_billing` ou champ sur `user_subscriptions` — identifier la table qui stocke `stripe_customer_id` et les infos PM
  - [ ] Masquage ID Stripe côté backend : ne retourner que `cus_XXXX...XXXX` (4 premiers + "..." + 4 derniers)
  - [ ] Quotas : depuis `token_usage_log` ou table de quotas — identifier la source
  - [ ] Générations récentes : `SELECT * FROM llm_call_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 20`
  - [ ] Tickets support : `SELECT * FROM support_incidents WHERE user_id = ? ORDER BY created_at DESC LIMIT 5`
  - [ ] Audit : `SELECT * FROM audit_events WHERE target_id = ? AND target_type = 'user' ORDER BY created_at DESC LIMIT 10`
- [ ] Endpoint `POST /api/v1/admin/users/{user_id}/reveal-stripe-id` (AC: 3)
  - [ ] Retourne l'ID Stripe complet
  - [ ] Génère un audit log : `action: "sensitive_data_revealed"`, `target_type: "user"`, `target_id: user_id`
- [ ] Créer les schémas Pydantic dans `backend/app/api/v1/schemas/admin_users.py` (AC: 1, 2)
- [ ] Créer `frontend/src/pages/admin/AdminUsersPage.tsx` (AC: 1)
  - [ ] Barre de recherche + liste résultats
  - [ ] Navigation vers la fiche
- [ ] Créer `frontend/src/pages/admin/AdminUserDetailPage.tsx` (AC: 2, 3)
  - [ ] Sections : profil, plan, stripe, quotas, générations, tickets, audit
  - [ ] Bouton "Révéler ID Stripe" avec appel POST + mise à jour locale
  - [ ] Badge de statut (actif / suspendu / verrouillé) utilisant `var(--success)`, `var(--danger)`
- [ ] CSS dans `AdminUsersPage.css` et `AdminUserDetailPage.css` (AC: 2)
  - [ ] Aucun style inline — CSS variables uniquement

## Dev Notes

### Contexte architectural
- **`UserModel`** : `id`, `email`, `password_hash`, `role`, `astrologer_profile`, `default_astrologer_id`, `email_unsubscribed`, `created_at`, `updated_at`. **Note** : les colonnes `is_suspended` et `is_locked` sont ajoutées en Story 65-9 — dans cette story, afficher le statut basé sur ce qui existe en DB (`email_unsubscribed` ou autre flag existant) et prévoir l'affichage de `is_suspended`/`is_locked` quand ils seront disponibles
- **Stripe data** : localiser où est stocké le `stripe_customer_id` — probablement dans `UserSubscriptionModel` ou une table `stripe_billing`. Vérifier `backend/app/infra/db/models/`
- **Quotas** : identifier la table de quotas/usage — probablement `token_usage_log` ou `usage_summary`. Vérifier le modèle de données canonique (Epic 61 a refactorisé les entitlements)
- **`LlmCallLogModel`** : table `llm_call_logs` ou `llm_observability` — vérifier le nom exact de la table et les champs disponibles
- **`support_incidents`** : table existante pour les tickets support — vérifier sa structure avant d'implémenter

### Masquage données sensibles — CRITIQUE
- Le masquage de l'ID Stripe doit être fait côté **backend** — ne jamais retourner l'ID complet dans la réponse GET standard
- La fonction de masquage : `masked = id[:7] + "..." + id[-4:]` si `len(id) > 11` else id
- L'endpoint de révélation (`POST .../reveal-stripe-id`) retourne l'ID complet ET génère un audit log immédiatement

### Project Structure Notes
- Nouveaux fichiers backend : `admin_users.py` router + `admin_users.py` schemas
- Nouveaux fichiers frontend : `AdminUsersPage.tsx`, `AdminUserDetailPage.tsx` + CSS
- Enregistrer le router dans le fichier central de routing

### References
- `backend/app/infra/db/models/user.py` [Source: session context]
- `backend/app/infra/db/models/billing.py` [Source: session context]
- `backend/app/infra/db/models/audit_event.py` [Source: session context]
- Epic 65 FR65-2, FR65-14, NFR5 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-8`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
