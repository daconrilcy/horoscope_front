# Story 65.8 : Fiche utilisateur — recherche et consultation complète

Status: done

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
   - tickets support : 5 derniers ouverts (titre, statut, date)
   - Audit : 10 derniers événements d'audit le concernant (action, acteur, date)

3. **Given** l'admin consulte la fiche  
   **When** les données Stripe sont affichées  
   **Then** l'ID Stripe est masqué (`cus_xxx...xxx` — seuls les 4 premiers et 4 derniers caractères visibles)  
   **And** la révélation complète nécessite un clic explicite qui génère un audit log `action: "sensitive_data_revealed"`

## Tasks / Subtasks

- [x] Créer le router `backend/app/api/v1/routers/admin_users.py` (AC: 1, 2, 3)
  - [x] `GET /api/v1/admin/users?q={email_or_id}&limit=20`
  - [x] `GET /api/v1/admin/users/{user_id}`
  - [x] `POST /api/v1/admin/users/{user_id}/reveal-stripe-id`
- [x] Implémenter la recherche (AC: 1)
  - [x] Support du filtre spécial `q=payment_failure` pour le dashboard
- [x] Implémenter la fiche complète `/users/{user_id}` (AC: 2, 3)
  - [x] Masquage ID Stripe côté backend
  - [x] Agrégation Profil, Plan, Stripe, Quotas, Tickets, Audit
- [x] Créer les schémas Pydantic dans `backend/app/api/v1/schemas/admin_users.py` (AC: 1, 2)
- [x] Créer `frontend/src/pages/admin/AdminUsersPage.tsx` (AC: 1)
  - [x] Gestion du `useSearchParams` pour `?filter=payment_failure`
- [x] Créer `frontend/src/pages/admin/AdminUserDetailPage.tsx` (AC: 2, 3)
- [x] CSS dans `AdminUsersPage.css` et `AdminUserDetailPage.css`
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_dashboard_api.py`

### File List
- `backend/app/api/v1/routers/admin_users.py`
- `backend/app/api/v1/schemas/admin_users.py`
- `backend/app/main.py`
- `backend/app/tests/integration/test_admin_actions_api.py`
- `frontend/src/pages/admin/AdminUsersPage.tsx`
- `frontend/src/pages/admin/AdminUsersPage.css`
- `frontend/src/pages/admin/AdminUserDetailPage.tsx`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `frontend/src/pages/admin/index.ts`
- `frontend/src/app/routes.tsx`

### Completion Notes List

- **Fix (code review)** : La barre de progression des quotas (`quota-bar-fill`) utilisait un style inline `style={{ width: ... }}` pour la largeur dynamique — violation de la règle "aucun style inline". Corrigé via une CSS custom property `--quota-fill-width` définie sur l'élément (seule façon de passer une valeur dynamique calculée sans inline style pour une propriété non-standard) ; la règle CSS `.quota-bar-fill` lit `width: var(--quota-fill-width, 0%)`.
- **Amélioration UX** : le bouton de retour de la fiche utilisateur renvoie désormais vers `/admin/users` au lieu du hub admin.
- **Visibilité support** : la fiche utilisateur expose maintenant un bloc `Activité` avec les tokens totaux / envoyés / reçus, le nombre de messages et le volume de thèmes natals (total, short, complete).
- **Correctif quota** : la section `Quotas` ne dépend plus uniquement des compteurs bruts. Elle privilégie la résolution canonique `plan + quota courant` utilisée par la facturation pour afficher des valeurs `consommé / autorisé` cohérentes dans les fiches utilisateurs.
- **Complément quota** : la fiche admin affiche désormais l'ensemble des fenêtres de quota configurées pour le plan actif sur `astrologer_chat` (journalier, hebdomadaire, mensuel), et non plus uniquement le quota mensuel.
