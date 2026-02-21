# Secrets Management and Rotation Runbook (Story 9.1)

## Policy

1. No secret must be hardcoded in application code, scripts, or committed runtime files.
2. Production requires explicit environment values for:
   - `JWT_SECRET_KEY`
   - `API_CREDENTIALS_SECRET_KEY`
   - `LLM_ANONYMIZATION_SALT`
   - `REFERENCE_SEED_ADMIN_TOKEN`
3. Secrets are read from environment variables only.
4. Secret leakage prevention is enforced by `scripts/scan-secrets.ps1`, integrated in quality gates.

## Rotation Strategy

### JWT

- Current signing key: `JWT_SECRET_KEY`
- Verification grace keys: `JWT_PREVIOUS_SECRET_KEYS` (comma-separated)
- Process:
  1. Generate a new `JWT_SECRET_KEY`.
  2. Move previous key to `JWT_PREVIOUS_SECRET_KEYS`.
  3. Deploy.
  4. Wait for refresh/access token grace window to elapse.
  5. Remove obsolete keys from `JWT_PREVIOUS_SECRET_KEYS`.

### Enterprise API Credential Hash Secret

- Current HMAC key: `API_CREDENTIALS_SECRET_KEY`
- Previous keys: `API_CREDENTIALS_PREVIOUS_SECRET_KEYS` (comma-separated)
- Process:
  1. Generate a new `API_CREDENTIALS_SECRET_KEY`.
  2. Append previous key to `API_CREDENTIALS_PREVIOUS_SECRET_KEYS`.
  3. Deploy.
  4. Rotate enterprise API credentials progressively.
  5. Remove old keys after all credentials are renewed.

### LLM Anonymization Salt

- Secret: `LLM_ANONYMIZATION_SALT`
- Rotation may change anonymization token mapping.
- Process:
  1. Generate and set new salt.
  2. Deploy in low-traffic window.
  3. Validate anonymization output format and audit logs.

### Reference Seed Admin Token

- Secret: `REFERENCE_SEED_ADMIN_TOKEN`
- Process:
  1. Generate new token.
  2. Update secure storage and operator tooling.
  3. Deploy.
  4. Validate seeding endpoint access with new token only.

## Validation Checklist (Post-Rotation)

- [ ] Authentication (`/v1/auth/login`, refresh flow) still works.
- [ ] Existing sessions remain valid through grace-period policy.
- [ ] B2B authenticated endpoints still accept active API keys.
- [ ] No new 5xx spikes linked to auth/credentials.
- [ ] Secrets scan returns `secrets_scan_ok`.

## Rollback

1. Revert to previous primary secret values.
2. Keep new values in previous-key lists when compatible.
3. Redeploy.
4. Re-run startup smoke and key API checks.
