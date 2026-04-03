# Story 63.15: Scheduler séquence emails J1–J7 [V2 — post-MVP]

Status: done

## Story

As a utilisateur inscrit depuis quelques jours,
I want recevoir des emails de suivi progressifs (éducation, preuve sociale, objections, upgrade) au bon moment,
so que je sois guidé vers la valeur du produit et vers un plan payant à mon rythme.

## Note MVP / V2

**Cette story est de priorité V2.** Le quick win business est l'email J0 (story 63.12). Les emails J1–J7 apportent de la valeur mais nécessitent une infrastructure de scheduling stabilisée. Ne pas implémenter tant que 63.12, 63.13 et 63.14 ne sont pas validés en production.

## Acceptance Criteria

### AC1 — Infrastructure scheduler

1. Un scheduler de tâches différées est choisi et stabilisé : **APScheduler** (si le backend est single-process) ou **Celery + Redis** (si une queue de tâches existe déjà dans le projet).
2. **Avant d'implémenter, vérifier** si Celery ou APScheduler est déjà présent dans `backend/pyproject.toml` — s'il existe, l'utiliser sans en ajouter un second.
3. Le scheduler est configuré pour survivre aux redémarrages (jobs persistés en base ou en Redis, pas uniquement en mémoire).

### AC2 — Planification des 4 emails différés

4. Lors de la création de compte, 4 tâches différées sont planifiées :
   - Email 2 (Éducation) : J+1 après `user.created_at`
   - Email 3 (Preuve sociale) : J+3
   - Email 4 (Objections + confiance) : J+5
   - Email 5 (Offre upgrade) : J+7
5. La planification est annulée/skippée si `user.email_unsubscribed = True` au moment de l'envoi.
6. La planification est annulée pour l'email upgrade (J+7) si l'utilisateur a déjà un abonnement actif.

### AC3 — Contenu des 4 emails

7. **Email 2 — Éducation (J+1)** : objet "Comment lire votre horoscope personnalisé", corps : 3 étapes du mécanisme, CTA vers dashboard.
8. **Email 3 — Preuve sociale (J+3)** : objet inspiré d'un cas client, corps : mini-cas illustratif labelisé, CTA vers "Voir un exemple".
9. **Email 4 — Objections (J+5)** : objet "Vos questions sur [Nom App]", corps : 3 FAQ courtes, CTA "Continuer".
10. **Email 5 — Upgrade (J+7)** : objet "Débloquez vos insights premium", corps : 3 bénéfices Premium + prix réels (ou "À partir de…" si non disponibles), CTA vers `/settings/subscription`.
11. Tous les emails partagent le template base de la story 63.12 (header/footer commun).
12. **Compliance** : aucun chiffre inventé dans les emails (métriques, prix) — mêmes règles que les stories landing.
13. Les emails J+1 à J+7 sont des emails **marketing / lifecycle** et portent le lien de désabonnement défini en 63.14.

### AC4 — Templates Jinja2

14. 4 templates dans `backend/app/templates/emails/` :
    - `education.html`, `social_proof.html`, `objections.html`, `upgrade.html`
15. Chaque template hérite de `base.html` (story 63.12).
16. Les prix dans `upgrade.html` sont injectés depuis une source backend canonique de pricing — jamais hardcodés dans le template.

### Definition of Done QA

- [ ] User créé → 4 jobs planifiés dans le scheduler (vérifiable en admin du scheduler)
- [ ] Email J+7 non envoyé si user déjà abonné
- [ ] Email non envoyé si `email_unsubscribed=True`
- [ ] Redémarrage backend → jobs non perdus (persistance vérifiée)
- [ ] Prix dans upgrade.html non hardcodés

## Tasks / Subtasks

- [ ] T1 — Vérifier/installer scheduler (AC: 1, 2, 3)
  - [ ] Audit `backend/pyproject.toml` pour Celery/APScheduler existant
  - [ ] Configurer persistance jobs
- [ ] T2 — Planification post-inscription (AC: 4, 5, 6)
  - [ ] Hook dans service inscription (après J0)
  - [ ] Vérifications annulation (unsubscribed, déjà abonné)
- [ ] T3 — Templates emails J1–J7 (AC: 7–12, 13–15)
  - [ ] 4 templates Jinja2 héritant de base.html
  - [ ] Injection prix dynamique dans upgrade.html
- [ ] T4 — Tests intégration scheduler
  - [ ] Mock du scheduler en test (pas de vraies tâches planifiées en CI)

## Dev Notes

- **APScheduler vs Celery** : APScheduler est plus simple pour un backend single-process mais ne scale pas horizontalement. Celery est adapté si Redis est déjà présent. Choisir en fonction de l'infrastructure existante — ne pas choisir arbitrairement.
- **Compliance emails** : les mêmes règles que la landing s'appliquent aux emails — pas de chiffres fictifs, pas de promesses non vérifiables.
- Dépend de 63.12, 63.13, 63.14.

### References

- Story 63.12 : `_bmad-output/implementation-artifacts/63-12-email-bienvenue-j0-transactionnel.md`
- Document funnel — Emails 2-5 : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#email-automation--5-emails-types-templates-prêts-à-adapter)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
