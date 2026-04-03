# Story 63.13: EmailLog et abstraction provider email

Status: done

## Story

As a développeur backend,
I want une abstraction propre du provider email et une traçabilité des envois en base,
so que je puisse changer de provider sans impact applicatif et auditer les emails envoyés.

## Acceptance Criteria

### AC1 — Interface provider abstraite

1. Un protocole/interface `EmailProvider` est défini dans `backend/app/services/email_provider.py` :
   ```python
   class EmailProvider(Protocol):
       async def send(self, to: str, subject: str, html: str, text: str) -> str:
           """Retourne le message_id du provider ou lève une exception."""
   ```
2. Deux implémentations sont fournies :
   - `NoopEmailProvider` : loggue le contenu à niveau `DEBUG`, ne fait aucun appel réseau — utilisé en dev/test.
   - `BrevoEmailProvider` (ou `SmtpEmailProvider`) : envoi réel via le provider configuré.
3. Le provider actif est sélectionné par `EMAIL_PROVIDER` (`noop` | `brevo` | `smtp`) dans les variables d'environnement.
4. En l'absence de variable, le provider par défaut est `noop` (fail-safe).

### AC2 — Modèle EmailLog

5. Modèle SQLAlchemy `EmailLog` dans `backend/app/infra/db/models/email_log.py` :
   - `id` (PK)
   - `user_id` (FK vers users, nullable pour les emails sans compte)
   - `email_type` (string : `welcome`, `education`, `social_proof`, `objections`, `upgrade`)
   - `recipient_email` (string)
   - `sent_at` (datetime UTC)
   - `status` (`sent` | `failed` | `skipped`)
   - `provider_message_id` (string nullable)
   - `error_message` (text nullable)
6. Migration Alembic créée et réversible.
7. Index sur `(user_id, email_type)` pour la vérification d'idempotence.

### AC3 — Idempotence

8. Avant tout envoi, vérifier dans `email_logs` qu'aucun envoi de même `(user_id, email_type)` avec `status=sent` n'existe.
9. Si déjà envoyé → skiper silencieusement (log `INFO`), ne pas renvoyer.
10. Cette logique d'idempotence est centralisée dans `email_service.py` (story 63.12), pas dans chaque provider.

### AC4 — Tests

11. Test unitaire `NoopEmailProvider` : pas d'appel réseau, retourne un message_id fictif.
12. Test d'idempotence : deux appels identiques → un seul enregistrement `email_logs`.

### Definition of Done QA

- [ ] `EMAIL_PROVIDER=noop` en CI → aucun appel réseau dans les tests
- [ ] Migration Alembic réversible (downgrade sans erreur)
- [ ] Deux envois identiques → 1 seul `email_logs` avec `status=sent`
- [ ] `EmailLog` créé pour chaque tentative (y compris `status=failed`)

## Tasks / Subtasks

- [ ] T1 — Interface provider (AC: 1–4)
  - [ ] `backend/app/services/email_provider.py`
  - [ ] `NoopEmailProvider` + `BrevoEmailProvider`
  - [ ] Factory via `EMAIL_PROVIDER` env var
- [ ] T2 — Modèle EmailLog (AC: 5, 6, 7)
  - [ ] `backend/app/infra/db/models/email_log.py`
  - [ ] Migration Alembic avec index
- [ ] T3 — Idempotence (AC: 8, 9, 10)
  - [ ] Intégrer la vérification dans `email_service.py`
- [ ] T4 — Tests (AC: 11, 12)

## Dev Notes

- Dépendance story 63.12 : utilise le `email_service.py` créé en 63.12. Cette story enrichit ce service avec l'abstraction provider et le modèle de log.
- `brevo-python` ou `httpx` direct pour Brevo — ajouter dans `backend/pyproject.toml`. **NE PAS créer requirements.txt**.
- Garder les providers dans des fichiers séparés pour faciliter l'ajout futur (SendGrid, etc.).

### References

- Story 63.12 : `_bmad-output/implementation-artifacts/63-12-email-bienvenue-j0-transactionnel.md`
- pyproject.toml : [backend/pyproject.toml](backend/pyproject.toml)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
