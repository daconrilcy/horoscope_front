<!-- Commentaire global: ce document formalise la demande d'approbation DPO/securite avant toute implementation runtime replay_snapshot_v1. -->

# replay_snapshot_v1 DPO/Security Approval Request

`decision_id`: `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`

## Decision state

`approval_state`: `approved`

`approved_by`: `DPO/security validation communicated by user`

`approved_at`: `2026-05-25`

`retention_policy`: `30 days maximum, with automatic purge and auditable manual purge`

`authorized_roles`: `ADMIN for metadata access after authorization; TECHNO and ASTRO_EXPERT only when RBAC maps them explicitly for technical diagnostics or astrology quality review`

`required_controls`: `redaction, no raw prompt storage, no raw birth data, no direct identifiers, encryption at rest for any isolated payload reference, access audit logs for reads/replays/exports/purges, no public/client OpenAPI exposure`

This document approves CS-278 to start implementation of `replay_snapshot_v1`
under the constraints below. It does not itself create runtime replay storage,
routes, services, models, migrations or purge jobs.

## Approved scope

The DPO/security decision approves:

- the purpose of replay snapshots;
- the maximum retention duration;
- the legal basis or product/security justification;
- the allowed stored fields;
- the forbidden data categories;
- the encryption and key-management boundary;
- the purge owner and purge triggers;
- the authorized internal roles;
- the audit-log requirements for reads, exports, replays and purges.

## Allowed purpose

Replay snapshots may only be considered for controlled internal support,
debugging, quality investigation and incident analysis.

They must not be used for marketing, model training, client-facing replay,
free-form admin browsing or broad analytics.

## Forbidden data

The approval confirms that these categories are forbidden or strictly
transformed before storage:

- raw birth data;
- exact coordinates;
- direct identifiers;
- raw prompts;
- raw model payloads;
- secrets, API keys, credentials and provider tokens;
- user-authored free text unless an approved isolated encrypted boundary exists.

## Approved retention

Replay snapshots may be retained for a maximum of 30 days.

The implementation must provide automatic expiry purge and an auditable manual
purge path. Purge must remove the replay snapshot and payload reference without
cascading into unrelated diagnostics or narrative answer audit records.

## Runtime gate

CS-278 is unblocked for implementation only under this approved scope:

```text
approval_state: approved
decision_id: DPO-REPLAY-SNAPSHOT-V1-RETENTION-001
approved_by: DPO/security validation communicated by user
approved_at: 2026-05-25
retention_policy: 30 days maximum, automatic purge, auditable manual purge
authorized_roles: ADMIN; TECHNO and ASTRO_EXPERT only after explicit RBAC mapping
required_controls: audit, encryption at rest, redaction, forbidden raw sensitive data, purge controls, no public/client exposure
```

Any implementation that needs broader retention, broader roles, raw prompt
storage, raw birth data, exact coordinates, direct identifiers or public/client
exposure must return to DPO/security review before code is added.
