# Persistent Evidence Contract

<!-- Contrat transverse pour conserver les audits et snapshots critiques. -->

Use this contract when the story requires audit, snapshot, baseline, OpenAPI
diff, route inventory, migration mapping, allowlist register, or exception
register evidence.

## Rule

Critical audit evidence must be written to a repository artifact. Console output
alone is not enough.

## Required Story Content

The story must include:

| Artifact | Path | Purpose |
|---|---|---|

## Acceptable Artifacts

- route audit markdown;
- OpenAPI baseline and diff;
- migration mapping table;
- allowlist register;
- exception register;
- generated manifest snapshot;
- architecture guard report.
