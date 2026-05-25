<!-- Commentaire global: ce document formalise la demande d'approbation DPO/securite avant toute implementation runtime replay_snapshot_v1. -->

# replay_snapshot_v1 DPO/Security Approval Request

`decision_id`: `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`

## Decision state

`approval_state`: `pending`

This document does not approve runtime replay storage. It records the exact
decision package required before CS-278 may implement `replay_snapshot_v1`.

## Required approval scope

The DPO/security decision must explicitly approve or reject:

- the purpose of replay snapshots;
- the maximum retention duration;
- the legal basis or product/security justification;
- the allowed stored fields;
- the forbidden data categories;
- the encryption and key-management boundary;
- the purge owner and purge triggers;
- the authorized internal roles;
- the audit-log requirements for reads, exports, replays and purges.

## Allowed purpose proposal

Replay snapshots may only be considered for controlled internal support,
debugging, quality investigation and incident analysis.

They must not be used for marketing, model training, client-facing replay,
free-form admin browsing or broad analytics.

## Forbidden data proposal

The implementation remains blocked unless the approval decision confirms that
these categories are forbidden or strictly transformed before storage:

- raw birth data;
- exact coordinates;
- direct identifiers;
- raw prompts;
- raw model payloads;
- secrets, API keys, credentials and provider tokens;
- user-authored free text unless an approved isolated encrypted boundary exists.

## Retention proposal to approve

The approval must name one concrete retention duration and one purge mechanism.
Until then, `docs/architecture/replay-snapshot-v1-storage-security-model.md`
keeps `approval_state` as `non approuve`.

## Runtime gate

CS-278 must remain blocked until this document, or an equivalent signed
DPO/security artifact, is updated with:

```text
approval_state: approved
approved_by: <name and role>
approved_at: <date>
retention_policy: <duration and purge rule>
authorized_roles: <approved roles>
required_controls: <audit, encryption, redaction and purge controls>
```

No backend API, service, model, migration, frontend UI, OpenAPI client,
background purge job or replay executor may be added before that approval.
