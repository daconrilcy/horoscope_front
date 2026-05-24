# Audit Bundle Ingestion

Use this reference when audits are stored as CONDAMAD-style bundles under `_condamad/audits/**`.

## Expected files

A complete audit bundle commonly contains:

- `00-audit-report.md`: scope, closure analysis, domain matrices, file usage, active finding surface, deferred context.
- `01-evidence-log.md`: reproducible evidence IDs, commands, inspected surfaces, results, limitations.
- `02-finding-register.md`: finding table and detailed finding sections.
- `03-story-candidates.md`: proposed stories, source labels, blockers, files to modify, stop conditions.
- `04-risk-matrix.md`: severity, probability, blast radius, regression risk, effort, priority.
- `05-executive-summary.md`: decision summary, severity grouping, story routing, validation snapshot.

Do not require all six files for non-CONDAMAD audits. If a CONDAMAD bundle is missing files, record the gap in `Missing Evidence`.

## Extraction rules

Extract from `00-audit-report.md`:

- Audit scope and domain key.
- Closure status.
- Matrices already present in the audit.
- File usage classification.
- Active finding surface.
- Deferred non-domain context.
- DRY, No Legacy, mono-domain, and dependency direction notes when present.

Extract from `01-evidence-log.md`:

- Evidence IDs.
- Commands or source documents.
- Inspected surfaces.
- PASS/FAIL result.
- Reproducible limitation.

Extract from `02-finding-register.md`:

- Finding IDs, severity, confidence, category and domain.
- Evidence ID links.
- Expected rule versus actual state.
- Impact.
- Recommended action.
- Closure decision.
- Suggested archetype.

Extract from `03-story-candidates.md`:

- Story candidate IDs.
- Source finding links.
- Source labels from briefs or audits.
- Required contracts.
- Objective.
- Must include.
- Validation hints.
- Blockers.
- Files to modify.
- Before/after evidence.
- Stop condition.

Extract from `04-risk-matrix.md`:

- Priority.
- Blast radius.
- Regression risk.
- Effort.

Extract from `05-executive-summary.md`:

- Decision summary.
- Highest-severity findings.
- Story routing.
- Validation snapshot.

## Story label caveats

Treat audit story labels as provenance, not authority.

If an audit says that a source label such as `CS-123` is already allocated or must be remapped:

- Preserve the original source label in roadmap stories.
- Do not use the source label as the final story ID.
- Mark the implementation story ID as `next-available-id` or `needs-tracker-remap`.
- Add the tracker conflict to blockers if implementation cannot proceed safely without remapping.

## Domain specificity

Keep domain terms from the audit in rows and examples, but do not hard-code them into the skill output model.

For example, a domain-specific audit may call a capability family a graph family, plan family, workflow, document type, or calculation mode. Preserve that vocabulary in the matrix row labels while keeping the columns generic.

## Evidence integrity

When a final architecture decision depends on audit evidence, cite both the audit and the original evidence IDs when available.

Use `assumption` only when the source audit does not provide evidence and the user has not supplied a stronger source.
