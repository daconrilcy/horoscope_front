# Runbook: RGPD Operational Evidence (Export / Delete / Audit)

## Objective

Generate a reproducible evidence dossier proving that RGPD privacy flows are operational:

- personal data export,
- personal data deletion,
- related audit traces.

## Preconditions

- Backend running on `http://127.0.0.1:8000`.
- A `support` or `ops` access token is available.
- Target user has already triggered export and delete privacy flows.

## Command

```powershell
.\scripts\generate-rgpd-evidence.ps1 `
  -BaseUrl "http://127.0.0.1:8000" `
  -AccessToken "<SUPPORT_OR_OPS_ACCESS_TOKEN>" `
  -TargetUserId 42
```

## Outputs

By default the command writes:

- `artifacts/privacy/rgpd-evidence-user-<user_id>.json`
- `artifacts/privacy/rgpd-evidence-user-<user_id>.md`

## Reproducibility Rule

For an unchanged dataset, repeated executions must produce the same `data` payload for the same `TargetUserId`.

## Error Handling

- `insufficient_role`: token role is not `support` or `ops`.
- `privacy_evidence_incomplete`: export/delete/audit proof is missing for target user.
- `audit_unavailable`: audit persistence unavailable while generating evidence.
