---
name: condamad-domain-auditor
description: >
  Audit the current implementation of one bounded application domain or layer
  and generate an evidence-backed CONDAMAD domain audit report. Use when the
  user asks to audit backend/app/api, backend/app/domain, services, auth,
  entitlement, infra/db, LLM domains, dependency boundaries, legacy surfaces,
  DRY violations, No Legacy risks, security or policy enforcement. Produces
  structured audit reports, finding registers, evidence logs, risk matrices,
  and story candidates for condamad-story-writer. Read-only by default.
---

<!-- Skill CONDAMAD d'audit read-only d'un domaine applicatif borne. -->

# CONDAMAD Domain Auditor

## Purpose

Audit one bounded implementation domain and produce a versioned, evidence-backed report.

This skill does not fix code. It does not refactor. It does not generate final implementation stories directly. It produces findings and story candidates.

## Non-negotiable rules

- Audit exactly one target domain per run unless the user explicitly asks for a comparative audit.
- Stay read-only by default.
- Do not modify application code.
- Do not format, migrate, delete, or rewrite files.
- Only write audit artifacts under `_condamad/audits/**`, except creating or
  updating `_condamad/stories/regression-guardrails.md` through
  `condamad-regression-guardrails`.
- Every finding must include evidence.
- Every High or Critical finding must include a recommended action or `needs-user-decision`.
- Every story candidate must map to at least one finding.
- DRY, No Legacy, mono-domain, and dependency direction are mandatory audit dimensions.
- Static scans are supporting evidence; runtime or structural evidence must be used when available.
- Ensure `_condamad/stories/regression-guardrails.md` exists, read it before
  producing findings, and map relevant existing invariants to story candidates.
- Before emitting new findings or story candidates, inspect the latest audits
  for the same domain and the CONDAMAD stories already produced from them.
  Classify each prior finding as `closed`, `still-active`, `superseded`,
  `non-domain`, or `needs-user-decision` using current evidence.
- Do not emit repetitive "next batch", "next cluster", or "continue reducing"
  candidates unless the audit also provides a complete closure plan for the
  source finding: exhaustive remaining surface, ordered implementation slices,
  stop condition, required guards, and evidence proving when no further story
  is needed.
- Prefer a closure-ready story candidate over a micro-candidate. A candidate is
  closure-ready only when it can satisfy the finding without known residual
  implementation work inside the audited domain, or when it explicitly states
  that a user decision blocks full closure.
- Any residual issue outside the audited domain must be classified as deferred
  non-domain context and must not keep the audited finding open.

## Required references

Read the relevant references depending on the audit target:

- `references/audit-principles.md`
- `references/audit-archetypes.md`
- `references/finding-taxonomy.md`
- `references/evidence-profiles.md`
- `references/report-output-contract.md`
- `references/story-candidate-contract.md`
- plus the domain-specific contract matching the selected archetype.
- `../condamad-regression-guardrails/SKILL.md`
- `workflow.md` for the full operational workflow.

## Output

Create an audit folder:

`_condamad/audits/<domain-key>/<YYYY-MM-DD-HHMM>/`

with:

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`

When the audit discovers a durable invariant already enforced by the current
implementation, update `_condamad/stories/regression-guardrails.md` only if it
is directly evidenced and useful for future stories. Otherwise, reference the
candidate invariant in `03-story-candidates.md` for later story-writer handling.

## Closure-quality requirements

Every audit report must include a concise closure analysis for the audited
domain:

- prior audit folders and story keys consulted;
- active findings that remain after the implemented stories;
- findings that are now closed, with evidence and guardrail IDs;
- complete exhaustive file/surface list for each active implementation finding;
- explicit separation between implementation files, governance/test files, and
  deferred non-domain concerns.

Every story candidate for a remediation finding must include:

- source finding ID and whether the candidate is intended to close the finding
  fully or only execute an explicitly bounded phase;
- exact files or exact selection rule for the full affected surface;
- before/after evidence artifacts required to prove closure;
- ownership routing decisions expected from implementation;
- mandatory no-wildcard allowlist and No Legacy checks;
- reintroduction guard requirements;
- validation commands and targeted scans;
- blocker conditions that require stopping instead of emitting another
  follow-up candidate.

For design-system, frontend architecture, No Legacy, CSS fallback, inline-style,
or token ownership audits, broad residual categories must be converted into a
finite closure map. The audit may recommend several coherent implementation
slices, but it must make the total expected closure visible in the same audit so
the implementer is not forced to rediscover the remaining work through repeated
audit/story cycles.

## Workflow

Follow `workflow.md`.

## Validation

Run from the skill directory:

```bash
python -S -B scripts/condamad_domain_audit_validate.py <audit_folder>
python -S -B scripts/condamad_domain_audit_validate.py <audit_folder> --explain-audit
python -S -B scripts/condamad_domain_audit_lint.py <audit_folder>
```

Run from repository root:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit_folder>
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit_folder> --explain-audit
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py <audit_folder>
```

For direct self-test diagnostics:

```bash
python -S -B -m unittest discover -s .agents/skills/condamad-domain-auditor/scripts/self_tests -p "*selftest.py" -v
```

## Full skill validation

Official package self-validation command from the repository root:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_self_validate.py
```

The direct `unittest discover` command remains useful for diagnostics when the wrapper reports a failure.

Wrapper smoke test to run before packaging or releasing the skill:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/self_tests/condamad_domain_audit_wrapper_smoke.py
```

For strict lint:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py <audit_folder> --strict
```

Before packaging, verify that the skill contains no `__pycache__`, `.pyc`, or `.pyo`.
