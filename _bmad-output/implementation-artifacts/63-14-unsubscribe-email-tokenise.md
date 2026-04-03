# Story 63.14: Désabonnement email tokenisé

Status: ready-for-dev

## Story

As a utilisateur ayant reçu un email de l'application,
I want pouvoir me désabonner des emails marketing en un clic,
so que je garde le contrôle sur mes préférences de communication.

## Acceptance Criteria

### AC1 — Token de désabonnement

1. Un token de désabonnement unique est généré pour chaque **email marketing** envoyé.
2. Le token est un JWT signé avec `SECRET_KEY` contenant `user_id`, `email_type=marketing`, et `exp` (30 jours).
3. Le token est inclus dans chaque template email comme paramètre du lien : `/api/email/unsubscribe?token={token}`.
4. La génération du token est faite dans `email_service.py` (ou un helper dédié) et passée aux templates marketing.

### AC2 — Endpoint de désabonnement

5. `GET /api/email/unsubscribe?token={token}` :
   - Valide le JWT (signature + expiry)
   - Marque `user.email_unsubscribed = True` en base
   - Retourne HTTP 200 avec une page HTML simple de confirmation ("Vous avez bien été désabonné")
   - **Pas de redirect vers l'app frontend** — réponse HTML autonome
6. Token invalide ou expiré → HTTP 400 avec message explicite (pas de 500).
7. Désabonnement déjà effectué → HTTP 200 idempotent (pas d'erreur).

### AC3 — Modèle utilisateur

8. Colonne `email_unsubscribed` (boolean, default `False`) ajoutée au modèle `User` existant.
9. Migration Alembic créée et réversible.
10. Les emails ultérieurs vérifient `user.email_unsubscribed` avant envoi et skippent si `True`.

### AC4 — Scope de désabonnement

11. Désabonnement de type `marketing` uniquement : les emails transactionnels (confirmation de compte, reset password) **continuent d'être envoyés** même si `email_unsubscribed=True`.
12. La logique de vérification pré-envoi applique `email_unsubscribed` **uniquement** aux emails marketing.

### Definition of Done QA

- [ ] Clic sur le lien désabonnement d'un email → `email_unsubscribed=True` en base
- [ ] Nouveau clic sur le même lien → HTTP 200 idempotent, pas d'erreur
- [ ] Token expiré → HTTP 400 avec message clair
- [ ] Email J0 transactionnel continue d'être envoyé même si `email_unsubscribed=True`
- [ ] Migration Alembic réversible

## Tasks / Subtasks

- [ ] T1 — Génération token JWT (AC: 1–4)
  - [ ] Fonction `generate_unsubscribe_token(user_id, email_type)` dans `email_service.py`
- [ ] T2 — Endpoint unsubscribe (AC: 5–7)
  - [ ] `backend/app/api/v1/routers/email.py` — GET `/api/email/unsubscribe`
  - [ ] Validation JWT + mise à jour base
  - [ ] Réponse HTML de confirmation
- [ ] T3 — Modèle User (AC: 8, 9, 10)
  - [ ] Colonne `email_unsubscribed` + migration Alembic
  - [ ] Vérification pré-envoi dans `email_service.py`
- [ ] T4 — Scope transactionnel vs marketing (AC: 11, 12)

## Dev Notes

- Dépend de stories 63.13 et du mécanisme de templates marketing consommé ensuite par 63.15.
- Cette story prépare l'infrastructure de désabonnement réutilisée par 63.15. Elle ne doit pas rétro-injecter d'unsubscribe dans l'email transactionnel J0.
- Utiliser `python-jose` ou `PyJWT` pour la génération/validation JWT — vérifier si déjà présent dans `backend/pyproject.toml`.
- La réponse de l'endpoint est un HTML minimal standalone (pas de template React) — quelques lignes HTML suffisent.

### References

- Story 63.12 : `_bmad-output/implementation-artifacts/63-12-email-bienvenue-j0-transactionnel.md`
- Story 63.13 : `_bmad-output/implementation-artifacts/63-13-emaillog-abstraction-provider.md`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
