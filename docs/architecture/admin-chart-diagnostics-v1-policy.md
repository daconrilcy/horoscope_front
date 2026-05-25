<!-- Politique canonique de retention, redaction et replay pour les diagnostics admin de calcul astrologique. -->

# admin_chart_diagnostics_v1 policy

## Contract identity

| Field | Value |
|---|---|
| `policy_id` | `admin_chart_diagnostics_v1_policy` |
| `diagnostic_surface` | `admin_chart_diagnostics_v1` |
| `classification` | Protected admin debug policy with no client exposure. |

This policy decides the documentation contract for `admin_chart_diagnostics_v1`.
It does not create a route, a service, a replay snapshot, a database table, a
migration, a generated client, a frontend screen or a public OpenAPI contract.

## retained_diagnostic_data

`admin_chart_diagnostics_v1` may retain only redacted calculation diagnostic
facts needed to explain an admin support decision:

| Category | Retention decision | Notes |
|---|---|---|
| calculation facts | DPO-open | Derived non-client facts may be retained only after approval of retention target and purge rules. |
| graph node status | DPO-open | Node code, status, cache hit/miss and normalized error kind are allowed candidates; raw graph payloads are denied. |
| source versions | DPO-open | Graph version, contract version and source/provenance references may be retained as version identity metadata. |
| proof references | DPO-open | Proof ids, source ids and redacted provenance refs may be retained without raw provider dumps. |
| diagnostic timings | DPO-open | Non-sensitive timings such as duration_ms and latency_ms may be retained for observability. |

The default retention_state is `DPO-open`. The blocked implementation surfaces
are `backend/app/api/**`, `backend/app/services/**`, `backend/app/infra/db/**`,
`backend/migrations/**`, `frontend/src/**`, generated OpenAPI clients and public
B2C projection contracts. No implementation may start until the DPO/security
decision records a concrete retention target, purge rule, storage owner and
access-control owner.

## sensitive_data

The following fields are sensitive and must be masked, truncated, hashed or
explicitly justified before any protected admin access:

| Data | Classification | Required treatment |
|---|---|---|
| birth date | derived sensitive domain data | mask or truncate; no raw value in diagnostic payloads. |
| birth time | derived sensitive domain data | mask or truncate; no raw value in diagnostic payloads. |
| birth place | derived sensitive domain data | mask, truncate or replace with a coarse locality label. |
| coordinates | derived sensitive domain data | truncate or remove precision; no raw latitude/longitude pair. |
| user id | correlable business identifier | hash or mask unless a subject reference is strictly required. |
| chart id | correlable business identifier | hash or mask unless a subject reference is strictly required. |
| raw input references | derived sensitive domain data | deny by default; justify any retained pointer. |

## redaction_policy

The policy reuses `backend/app/core/sensitive_data.py` categories and sink
treatments. Raw birth data, precise coordinates, direct identifiers, raw graph
payloads, replay inputs and provider debug dumps are denied. Diagnostic payloads
must expose only masked values, truncated values, hashes, non-sensitive key
names, normalized statuses, source version labels and proof references.

## retention_policy

Retention target: `DPO-open`.

Until approval, this policy is documentation-only. The blocked surfaces are the
runtime diagnostic route, replay service, replay storage model, persistence
migration, generated client, frontend screen, public OpenAPI exposure and any
batch export. An approved follow-up must name the retention duration, purge
owner, deletion trigger, storage location, encryption requirement and audit-log
retention before code or schema work begins.

## replay_boundary

Current diagnostics are not replay snapshots. `admin_chart_diagnostics_v1`
describes redacted execution facts and support diagnostics only. It must remain
separate from calculation replay, LLM replay, narrative answer audit and public
projection payloads.

## replay_prerequisites

Replay can be designed only by a later storage and security story after these
prerequisites are approved:

| Prerequisite | Required decision |
|---|---|
| storage owner | A canonical replay_snapshot_v1 storage owner and encryption boundary. |
| input reconstruction | A rule for which inputs can be reconstructed without raw birth data leakage. |
| version identity | Graph version, source version, contract version and calculation code identity. |
| retention approval | DPO/security approval for duration, purge rules and legal basis. |
| purge rules | Explicit deletion trigger, audit evidence and operational owner. |

## admin_access_log_fields

Every policy-protected consultation must create an admin consultation log that
is separate from narrative answer audit. Required fields are:

- actor
- role
- action
- decision
- timestamp
- subject reference
- correlation id

The log records the consultation decision and correlation metadata, not the raw
diagnostic payload.

## denied_surfaces

Denied surfaces for this story are clients, public OpenAPI, frontend files,
generated clients, public B2C projection contracts, narrative answer audit, LLM
replay, API routers, services, database models, migrations, seeds, builders and
serializers. The phrase `admin_chart_diagnostics_v1` must not appear in
`app.routes` or `app.openapi()` until an explicitly approved implementation
story changes that runtime boundary.
