<!-- Commentaire global: ce document definit le modele de stockage et de securite de replay_snapshot_v1 sans autoriser son execution runtime. -->

# replay_snapshot_v1 Storage Security Model

## Identite du contrat

| Field | Value |
|---|---|
| `model_id` | `replay_snapshot_v1_storage_security_model` |
| `snapshot_type` | `replay_snapshot_v1` |
| `classification` | Protected internal replay support and debug data. |
| `approval_state` | `non approuve` tant que la decision DPO/security `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001` reste ouverte. |

`replay_snapshot_v1` est un contrat interne protege pour cadrer un futur stockage de support et de debug. Il ne cree pas de replay
executor, replay builder, replay service, route, modele de base de donnees, migration, client genere, UI frontend ou exposition
OpenAPI publique. La production replay execution n'est pas approuvee par cette story.

## minimal_stored_content

Le contenu minimal stockable, apres approbation DPO/security, est limite aux metadonnees necessaires a la reconstruction controlee:

| Category | Allowed content | Boundary |
|---|---|---|
| calculation identity | `calculation_id`, `chart_reference_hash`, graph family and normalized status. | No raw chart payload. |
| input reconstruction reference | `input_ref`, `birth_data_ref_hash`, coarse input schema version. | Reference only; raw birth data is forbidden. |
| version identity | graph version, projection contract version, prompt template version and source version labels. | Version labels only; no prompt body. |
| provenance | source ids, evidence refs, request correlation id and creation timestamp. | Correlation metadata, not direct identifiers. |
| diagnostics link | reference to redacted `admin_chart_diagnostics_v1` metadata. | Link only; diagnostics payload is not embedded. |
| AI audit link | reference to `narrative_answer_audit_v1` or rejected-answer audit metadata. | Link only; audit record is not merged. |

## forbidden_data

The default storage policy denies these categories:

| Data category | Decision |
|---|---|
| raw birth data | Forbidden as stored content; use a hashed or tokenized reconstruction reference. |
| exact coordinates | Forbidden; use no coordinate value or an approved coarse locality reference. |
| direct identifiers | Forbidden by default; replace user id, email, name and chart id with hashes or subject references. |
| raw prompts | Forbidden; store prompt template version and prompt ref only. |
| raw model payloads | Forbidden; store provider call id, model version and redacted audit link only. |
| secrets | Forbidden; API keys, tokens, credentials and provider secrets must never be stored. |

## masking_policy

| Sensitive category | Required treatment |
|---|---|
| birth date, birth time and birth place | mask, truncate or replace with `birth_data_ref_hash`. |
| latitude and longitude | deny exact values; truncate only if a DPO/security decision approves a coarse precision. |
| user, email, name, chart and consultation identifiers | hash, tokenize or replace with a scoped subject reference. |
| prompts and model payloads | deny raw storage; keep version identity and narrative answer audit references. |
| secrets and credentials | deny storage and fail validation if detected. |

The policy reuses `backend/app/core/sensitive_data.py` for sensitive replay and birth-data classification. A future implementation must
use that owner rather than adding an ad hoc replay sanitizer.

## authorized_roles

Access is limited to the internal role vocabulary from CS-270 and the permission domains from CS-271:

| Role | Current state | Allowed scope for this contract |
|---|---|---|
| `ADMIN` | active | May request or view replay snapshot metadata after DPO/security approval and audit logging. |
| `TECHNO` | target-only, inactive until RBAC | Target role for technical diagnostics only; no current access grant. |
| `ASTRO_EXPERT` | target-only, inactive until RBAC | Target role for astrology quality review only; no current access grant. |

`MARKETER` is not an authorized role for `replay_snapshot_v1` because CS-271 denies debug replay access for marketing use.

## denied_roles

Denied by default:

- client B2C users;
- public or anonymous callers;
- B2B account roles and `enterprise_admin`;
- marketing-only users, including `MARKETER`;
- preexisting runtime roles such as `support` and `ops` unless a future RBAC story maps them explicitly;
- any unauthorized admin class without CS-270/CS-271 role and audit approval.

## retention_policy

Retention target: `DPO-open`.

Decision blocker: `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.

Held-back implementation surfaces until the blocker is resolved:

- `backend/app/api/**`;
- `backend/app/services/**`;
- `backend/app/infra/db/**`;
- `backend/migrations/**`;
- `frontend/src/**`;
- generated OpenAPI clients;
- public B2C projection contracts;
- background purge jobs and batch exports.

The required decision must name the retention duration, legal basis, storage owner, encryption boundary, purge owner, deletion triggers,
access-log retention and operational audit trail. Until then, the contract remains documentation-only and `approval_state` stays
`non approuve`.

## purge_policy

| Trigger | Required behavior |
|---|---|
| expiry purge | Delete the replay snapshot record and payload reference after the approved retention duration. |
| manual deletion | Delete by subject/reference request after authorization, with an audit log of actor, reason, timestamp and correlation id. |
| linked diagnostics | Keep redacted `admin_chart_diagnostics_v1` records separate; replace replay links with tombstone metadata after purge. |
| linked AI audit | Keep narrative answer audit records separate; remove replay snapshot pointer while preserving audit retention rules. |

Purge must not delete unrelated diagnostics or AI audit records by cascade. It may only remove the replay snapshot and update link metadata.

## diagnostics_link

`replay_snapshot_v1` may link to `admin_chart_diagnostics_v1` through a redacted correlation id, diagnostic id or metadata reference.
Diagnostics remain current redacted support facts, not replay snapshots. The diagnostics record must not embed replay payloads, input
reconstruction data, raw prompts, model payloads or secrets.

## ai_audit_link

`replay_snapshot_v1` may link to `narrative_answer_audit_v1` and rejected-answer audit records through metadata references. The AI audit
record remains the owner of prompt evidence, grounding state, rejection state and provider audit metadata. Replay storage must not merge,
copy or replace narrative answer audit records.

## Surfaces refusees

This story explicitly denies replay routes, replay services, replay builders, database models, Alembic migrations, frontend UI, generated
clients, public OpenAPI paths, RGPD policy changes, fallback storage paths, compatibility aliases and silent fallback behavior.
