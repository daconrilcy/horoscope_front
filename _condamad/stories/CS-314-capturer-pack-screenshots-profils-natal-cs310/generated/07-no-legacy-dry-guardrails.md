# No Legacy / DRY Guardrails - CS-314

- No application runtime code is changed by this story.
- The screenshot replay is contained in one capsule evidence script, not an active runtime fallback.
- The script uses deterministic API routes only to replay CS-310 synthetic states in a browser; it does not introduce a product shim.
- RG-047 and RG-052 remain enforced through existing frontend guard tests.
- Sensitive evidence is limited to synthetic profile identifiers and screenshot paths; raw payloads and tokens are not persisted in ledgers or notes.
