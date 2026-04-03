# Story 63.12: Email de bienvenue J0 — transactionnel post-inscription

Status: ready-for-dev

## Story

As a utilisateur venant de créer son compte,
I want recevoir immédiatement un email de bienvenue avec un lien vers le premier pas dans l'app,
so que je sois guidé vers l'action d'activation sans avoir à retrouver l'URL par moi-même.

## Acceptance Criteria

### AC1 — Déclenchement

1. L'email J0 est envoyé **automatiquement et immédiatement** au moment de la validation de la création de compte dans le service d'inscription backend.
2. Le déclenchement est synchrone (best effort) — si l'envoi échoue, l'inscription **ne doit pas être bloquée** : l'erreur est loguée mais l'utilisateur est créé normalement.
3. L'envoi n'est déclenché qu'une seule fois par utilisateur (idempotence : si l'utilisateur est recréé ou si l'endpoint est appelé deux fois, l'email J0 n'est envoyé qu'une fois).

### AC2 — Contenu de l'email J0

4. **Objet** : "Bienvenue dans votre univers astrologique ✨" (ou équivalent non-trompeur)
5. **Corps** :
   - Salutation avec le prénom si disponible, sinon "Bonjour,"
   - Confirmation de création de compte (email de l'utilisateur)
   - Lien direct vers `/profile` (première étape onboarding : saisie données natales)
   - 1 phrase sur la valeur immédiate attendue
   - Lien de support ou d'aide simple vers l'application
6. L'email ne contient **aucune promesse chiffrée non vérifiée**, aucun prix, aucune offre commerciale.
7. L'email est en texte et HTML (multipart) — template Jinja2.

### AC3 — Infrastructure email

8. Un service `backend/app/services/email_service.py` est créé avec :
   - Fonction `send_welcome_email(user_id: int, email: str, firstname: str | None) -> bool`
   - Retourne `True` si envoi réussi, `False` si erreur (avec log)
9. Le provider email est configurable via `EMAIL_PROVIDER` (`brevo` | `sendgrid` | `smtp`) dans les variables d'environnement.
10. En dev/test (`EMAIL_PROVIDER=noop` ou `ENABLE_EMAIL=false`), les emails ne sont pas envoyés — le contenu est loggé à `DEBUG` level.

### AC4 — Template HTML

11. Template Jinja2 dans `backend/app/templates/emails/welcome.html`.
12. Le template est responsive (base HTML email compatible Gmail/Outlook) avec un style inline minimal (les emails HTML requièrent du style inline — exception justifiée à la règle générale no-inline-styles).
13. Un template base `backend/app/templates/emails/base.html` est créé avec header/footer commun (logo, lien désabonnement).
14. Le template est testable indépendamment (rendu HTML générable sans envoi).

### AC5 — Périmètre transactionnel strict

15. L'email J0 est **transactionnel** : il ne dépend pas du mécanisme de désabonnement marketing.
16. Aucun lien de désabonnement marketing n'est injecté dans cet email.
17. Les préférences marketing et le lien d'unsubscribe sont traités par les stories 63.14 et 63.15, pas ici.

### AC6 — Observabilité minimale

18. Un log applicatif explicite est produit sur succès et sur échec d'envoi.
19. Si la story 63.13 est implémentée avant ou en même temps, `welcome` est aussi tracé dans `email_logs`.

### AC7 — Feature flag

21. L'envoi email est conditionné par `ENABLE_EMAIL=true` (variable d'environnement, `false` par défaut en dev/test).
22. En CI, `ENABLE_EMAIL=false` est obligatoire.

### Definition of Done QA

- [ ] Email reçu dans les 30 secondes après inscription (en staging avec vrai provider)
- [ ] Si provider en erreur, inscription complète quand même
- [ ] Deux inscriptions avec le même email → email envoyé une seule fois
- [ ] En dev avec `ENABLE_EMAIL=false` → aucun appel réseau vers le provider
- [ ] L'email J0 ne contient ni prix, ni offre commerciale, ni lien d'unsubscribe marketing

## Tasks / Subtasks

- [ ] T1 — Service email (AC: 8, 9, 10)
  - [ ] Créer `backend/app/services/email_service.py`
  - [ ] `send_welcome_email()` avec provider abstraction
  - [ ] `noop` provider pour dev/test
- [ ] T2 — Templates Jinja2 (AC: 11–14)
  - [ ] `backend/app/templates/emails/base.html`
  - [ ] `backend/app/templates/emails/welcome.html`
  - [ ] Test de rendu indépendant
- [ ] T3 — Déclenchement post-inscription (AC: 1–3)
  - [ ] Hook dans le service auth existant
  - [ ] Gestion erreur non-bloquante
  - [ ] Idempotence (vérifier email_logs avant envoi)
- [ ] T4 — Gardes de périmètre transactionnel (AC: 15–17)
  - [ ] Vérifier qu'aucun prix, aucune offre et aucun unsubscribe marketing ne sont injectés dans le template
- [ ] T5 — Feature flag (AC: 21, 22)
  - [ ] `ENABLE_EMAIL` env var

## Dev Notes

- **Provider recommandé MVP** : Brevo (ex-Sendinblue) — tier gratuit 300 emails/jour, API simple, pas de coût initial. Ajouter `brevo` (client Python officiel `sib-api-v3-sdk` ou `brevo-python`) dans `backend/pyproject.toml`. **NE PAS créer de requirements.txt**.
- **Style inline dans les templates email** : c'est une exception justifiée aux règles CSS du projet — les clients email (Gmail, Outlook) ignorent les stylesheets. Utiliser `style=""` dans les templates Jinja2 email uniquement.
- **Vérifier le service auth existant** : chercher `backend/app/services/auth_service.py` ou équivalent — le hook d'envoi J0 doit être ajouté après la création utilisateur confirmée.
- **Ne pas implémenter les emails J1–J7 ici** : ce sera la story 63.15 (scheduler séquence).
- **Ne pas implémenter le désabonnement ici** : ce sera la story 63.14 (emails marketing uniquement).

### Project Structure Notes

```
backend/
├── app/
│   ├── services/
│   │   └── email_service.py             # nouveau
│   └── templates/
│       └── emails/
│           ├── base.html               # nouveau
│           └── welcome.html            # nouveau
└── pyproject.toml                         # modifier — ajouter dépendance provider email
```

### References

- Service auth backend : `backend/app/services/` (chercher auth_service.py)
- pyproject.toml : [backend/pyproject.toml](backend/pyproject.toml) (NE PAS créer requirements.txt)
- Document funnel — Email 1 : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#email-1--welcome--livraison-de-valeur-j0-immédiat)
- Story 63.13 : `_bmad-output/implementation-artifacts/63-13-emaillog-abstraction-provider.md`
- Story 63.14 : `_bmad-output/implementation-artifacts/63-14-unsubscribe-email-tokenise.md`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
