<!-- Commentaire global: ce contrat cadre les futurs flows admin d'audit et de replay sans creer de surface publique ni exposer de donnees sensibles. -->

# Admin Audit And Replay Flows

## Portee

Ce document est le contrat canonique pour une future UI admin interne capable de consulter les reponses rejetees, les journaux d'audit autorises et les metadonnees `replay_snapshot_v1`, puis de lancer une tentative de replay controlee ou une purge manuelle auditee.

La story ne cree aucun ecran React, route backend, schema, migration, client genere, role ou permission supplementaire. Toute implementation frontend/admin reste bloquee tant que les trois preuves suivantes ne sont pas disponibles dans la branche d'implementation concernee:

- AuthN/AuthZ admin interne existante sur chaque endpoint consomme via `require_admin_user`;
- audit logs pour les lectures, changements de statut, tentatives replay et purges;
- masquage ou exclusion des donnees sensibles selon les politiques replay et answer-audit existantes.

Les surfaces B2C, publiques, support large, export massif, replay client-facing, replay automatique et navigation libre dans les donnees brutes sont interdites.

## Endpoints runtime consommes

Inventaire issu de `app.routes` et `app.openapi()`; les chemins consommes par ce contrat pour audit, replay et answer-audits doivent rester sous `/v1/admin/`.

| Flow | Methode | Chemin | Objectif admin | Preuve runtime | Gate |
|---|---:|---|---|---|---|
| Reponses rejetees - liste | GET | `/v1/admin/answer-audits/rejected` | Lister les reponses narratives rejetees avec pagination et filtre `review_status`. | `app.routes` et OpenAPI | `require_admin_user` |
| Reponses rejetees - detail | GET | `/v1/admin/answer-audits/rejected/{answer_id}` | Lire un detail protege avec preuve de journalisation. | `app.routes` et OpenAPI | `require_admin_user` |
| Reponses rejetees - revue | PATCH | `/v1/admin/answer-audits/rejected/{answer_id}/review` | Mettre a jour le statut interne de revue sans publier la reponse rejetee. | `app.routes` et OpenAPI | `require_admin_user` |
| Audit autorise | GET | `/v1/admin/audit` | Lire les evenements d'audit masques et pagines. | `app.routes` et OpenAPI | `require_admin_user` |
| Replay snapshot - metadonnees | GET | `/v1/admin/audit/replay_snapshot_v1/{snapshot_id}` | Lire les metadonnees replay expurgees sans payload source. | `app.routes` et OpenAPI | `require_admin_user` |
| Replay snapshot - tentative controlee | POST | `/v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt` | Demander une tentative replay auditee et asynchrone, sans retour du payload source. | `app.routes` et OpenAPI | `require_admin_user` |
| Replay snapshot - purge manuelle | DELETE | `/v1/admin/audit/replay_snapshot_v1/{snapshot_id}` | Purger manuellement le snapshot replay et conserver l'audit. | `app.routes` et OpenAPI | `require_admin_user` |

Les endpoints `/v1/admin/audit/export`, `/v1/admin/llm/replay` et `/v1/admin/llm/call-logs/purge` existent hors de ce flow minimal. Ils ne sont pas consommes par cette UI tant qu'un contrat separe ne prouve pas le besoin, le masquage, l'audit et l'absence d'export massif.

## Ecrans et flows minimaux

Chaque ecran doit declarer `screen_id`, `endpoint`, `visible_fields`, `masked_fields`, `audit_event` et `blocked_gate` dans son implementation future.

| screen_id | Endpoint | visible_fields | masked_fields | audit_event | Etats et sorties admin |
|---|---|---|---|---|---|
| `rejected_answer_list` | `GET /v1/admin/answer-audits/rejected` | `contract_id`, `answer_id`, `status`, `review_status`, `rejection_reason`, `missing_evidence_refs`, `prompt_version`, `projection_version`, `provider`, `model`, `created_at`, `reviewed_at`, `reviewed_by` | `raw_rejected_answer`, raw prompt, raw AI answer, raw provider payload, birth data, exact coordinates, secrets, free-form audit details | `admin_rejected_answer_review_accessed` avec `details.consultation=list` | `authorized`: liste paginee; `denied`: acces refuse; `incomplete`: store indisponible ou champs contractuels manquants |
| `rejected_answer_detail` | `GET /v1/admin/answer-audits/rejected/{answer_id}` | champs de liste, `manual_correction_limits`, `audit_event.event_id`, `audit_event.action`, `audit_event.status`, `audit_event.created_at` | `raw_rejected_answer`, full prompts, secrets, `birth_date`, `birth_time`, `birth_place`, `birth_lat`, `birth_lon`, `birth_timezone`, `review_note` dans l'audit trail | `admin_rejected_answer_review_accessed` avec `target_id=<answer_id>` | `authorized`: detail protege; `denied`: 401/403; `incomplete`: record introuvable ou audit absent |
| `rejected_answer_review_status` | `PATCH /v1/admin/answer-audits/rejected/{answer_id}/review` | `review_status`, statut de confirmation, horodatage issu du rafraichissement | valeurs hors enum, note libre dans audit details, donnees brutes de la reponse | `admin_rejected_answer_reviewed` avec `details.review_status` | `authorized`: statut mis a jour; `denied`: 401/403; `incomplete`: statut invalide ou record absent |
| `audit_log_review` | `GET /v1/admin/audit` | `id`, `timestamp`, `actor_email_masked`, `actor_role`, `action`, `target_type`, `target_id_masked`, `status`, `details` deja expurges, `page`, `per_page`, `total` | email complet, target id direct, prompt brut, payload provider brut, secrets, credentials, provider tokens, birth data brute | `admin_audit_log_accessed` attendu avant consommation UI; aucune exportation dans ce flow minimal | `authorized`: logs filtres et pagines; `denied`: acces refuse; `incomplete`: audit de lecture ou details expurges absents |
| `replay_snapshot_metadata` | `GET /v1/admin/audit/replay_snapshot_v1/{snapshot_id}` | `contract_id`, `snapshot_id`, `status`, `created_at`, `expires_at`, `redaction_state`, `version_identity`, `provenance_refs`, `audit_event_id` | payload replay, raw birth data, exact coordinates, raw prompts, raw model payloads, direct identifiers, secrets | `replay_snapshot_v1.metadata_read` | `authorized`: metadonnees expurgees; `denied`: 401/403; `expired`: snapshot expire; `purged`: deja purge; `incomplete`: metadonnees invalides |
| `replay_attempt_confirmation` | `POST /v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt` | `snapshot_id`, `status`, `redaction_state`, `replay_attempt_id`, `audit_event_id`, confirmation non automatique | payload source, entree utilisateur brute, sortie modele brute, provider request/response, donnees de naissance brutes | `replay_snapshot_v1.replay_attempt` | `authorized`: tentative acceptee en 202; `denied`: acces refuse; `expired` ou `purged`: action refusee; `incomplete`: replay non lance |
| `replay_snapshot_purge_confirmation` | `DELETE /v1/admin/audit/replay_snapshot_v1/{snapshot_id}` | confirmation 204, `snapshot_id` dans le contexte UI, raison operationnelle saisie hors audit details bruts si requise plus tard | payload reference, payload replay, donnees brutes liees, cascade vers diagnostics ou answer audit | `replay_snapshot_v1.purge` | `authorized`: purge auditee; `denied`: acces refuse; `expired` ou `purged`: etat terminal affiche; `incomplete`: purge non confirmee |

## Etats communs

- `authorized`: l'utilisateur est un admin interne authentifie, l'endpoint repond et l'audit attendu existe.
- `denied`: l'AuthN/AuthZ admin interne refuse l'action; l'UI n'affiche aucune donnee partielle.
- `expired`: le snapshot replay a depasse la retention approuvee et ne peut plus etre consulte ou rejoue.
- `purged`: le snapshot replay a ete purge; seule une confirmation/tombstone expurgee peut etre affichee.
- `incomplete`: le backend ou les preuves d'audit/redaction sont insuffisants; l'UI bloque l'action au lieu d'improviser un fallback.

## Donnees interdites

Ces champs sont toujours exclus des `visible_fields` et doivent rester absents des colonnes, details, exports, filtres libres et confirmations:

- raw prompt, full prompt, prompt body;
- raw provider payload, raw model payload, provider request, provider response;
- raw AI answer, `raw_rejected_answer`;
- raw birth date, raw birth time, raw birth place, `birth_date`, `birth_time`, `birth_place`, `birth_lat`, `birth_lon`, `birth_timezone`;
- latitude, longitude et exact coordinates;
- secrets, API keys, credentials, provider tokens;
- direct identifiers non deja masques par le contrat backend.

Les donnees autorisees sont uniquement les identifiants masques, references, statuts, versions, horodatages, hash ou metadonnees expurgees deja fournis par les contrats backend.

## Checklist bloquante pour implementation frontend/admin

- Confirmer par `app.openapi()` et `app.routes` que chaque chemin consomme reste sous `/v1/admin/`.
- Verifier avec `TestClient` que l'absence d'authentification retourne 401 et qu'un non-admin retourne 403 pour les flows sensibles.
- Verifier que chaque lecture/action sensible produit ou expose l'evenement d'audit attendu.
- Refuser toute UI qui affiche une valeur masquee, brute ou issue d'un payload source.
- Refuser tout export massif et toute route `/v1/public/**`, `/v1/support/**`, `/v1/replay_snapshot_v1` ou `/api/replay_snapshot_v1`.
- Bloquer l'ecran si l'etat est `incomplete` plutot que fournir un shim, alias, fallback silencieux ou chemin legacy.
