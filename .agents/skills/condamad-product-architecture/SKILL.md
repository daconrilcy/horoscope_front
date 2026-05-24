---
name: condamad-product-architecture
description: >
  Synthesize existing audits, reviews, discovery reports, or finding registers
  into a product architecture plan. Use when the user asks to turn prior audits
  into cross-domain architecture decisions, capability matrices, surface
  matrices, canonical registries, object/entity decisions, operational rules
  for versioning, trace, cache, replay, invalidation, or an ordered
  implementation roadmap. Trigger when audits are stored under
  _condamad/audits/** or when CONDAMAD-style report, evidence log, finding
  register, story candidate, risk matrix, and executive summary artifacts must
  be synthesized. This skill is a capstone above several audits, not a new
  narrow audit.
metadata:
  version: 1
  role: CONDAMAD Product Architect
---

# CONDAMAD Product Architecture

## Role

Act as a product architecture synthesizer for CONDAMAD audit evidence. Convert multiple prior audits into architecture decisions, source-of-truth registries, operational rules, blockers, and implementation-ready roadmap stories.

## Purpose

Transform prior audits into an architecture product plan that can guide implementation.

This skill does not redo the audits. It reconciles the audit evidence, identifies cross-cutting decisions, names blockers, and converts the result into ordered implementation stories.

## Scope boundary

Use this skill as a capstone over existing evidence. It may read code, docs, or tickets only to clarify audit evidence, resolve contradictions, or fill explicitly named gaps. It must not become a fresh domain audit, implementation pass, refactor plan, or feature design exercise.

## Non-negotiable rules

- Treat supplied audits as the primary source of truth.
- Do not invent current-state facts without evidence from audits, code, docs, tickets, or user-provided context.
- Separate `observed`, `inferred`, `decision`, `blocker`, and `open question`.
- Mark every material claim with source audit IDs, source paths, or `assumption`.
- Resolve contradictions explicitly instead of smoothing them over.
- Prefer canonical registries and versioned contracts over ad hoc naming.
- Keep domain-specific labels supplied by the audits, but write the framework generically enough to apply to any product domain.
- Do not create implementation code unless the user explicitly asks for implementation after the architecture plan.
- Produce roadmap stories that are ordered by dependency and risk, not by audit order.
- Mark any decision that needs product owner, architecture owner, security owner, or data owner approval.
- Do not downgrade unresolved contradictions into ordinary backlog work; keep them visible as blockers or owner decisions.
- Do not let roadmap stories introduce new architecture not present in the matrices or registry decisions.

## Required references

Load references progressively:

- `workflow.md` for the operational sequence.
- `references/output-contract.md` before writing final deliverables.
- `references/audit-bundle-ingestion.md` when input audits live under `_condamad/audits/**` or use CONDAMAD-style report/evidence/finding/story/risk/summary files.
- `references/decision-rules.md` when choosing canonical registries, entity/object scope, or versioning rules.
- `references/roadmap-rules.md` before drafting implementation stories.

## Inputs to collect

Collect the smallest useful set of inputs before synthesis:

- Audit identifiers and paths, or pasted audit content.
- Existing backlog tickets, story IDs, ADRs, design docs, API docs, or schema docs if mentioned.
- Product domain vocabulary and known bounded contexts.
- Required output location if artifacts must be written to disk.
- Tracker or story-status context when source audits contain candidate story labels that may already be allocated.

If inputs are incomplete, proceed with explicit assumptions and a `Missing Evidence` section rather than blocking, unless the user asked for a formal decision that cannot be made responsibly.

## Output shape

Use the output contract as the default final structure:

1. Executive architecture decision summary.
2. Audit source map.
3. Capability or family matrix.
4. Surface matrix.
5. Canonical registry decisions.
6. Entity/object decisions.
7. Operational rules: versioning, trace, cache, replay, invalidation.
8. Blockers and decision owners.
9. Ordered implementation roadmap.
10. Open questions and validation plan.

## Quality bar

The deliverable is successful only when an implementation agent can pick the first roadmap story without rereading every source audit, and an architecture reviewer can trace each major decision back to evidence or a clearly marked assumption.

## Final anti-drift checklist

Before delivering, verify:

- The output is a synthesis of existing audits, not a new audit.
- All mandatory matrices and decision sections are present.
- Each registry decision has owner, versioning, compatibility, trace, and deprecation posture.
- Each operational rule maps to at least one capability, surface, registry, object, or blocker.
- Each roadmap story maps back to source audits and prior architecture decisions.
- All assumptions and missing evidence are explicitly labeled.
