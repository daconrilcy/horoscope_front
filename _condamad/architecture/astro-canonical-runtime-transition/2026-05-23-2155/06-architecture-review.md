# Architecture Review - CS-245 Canonical Runtime Transition

## Verdict

CLEAN after hardening.

## Review Scope

- Reviewed artifact folder: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/`.
- Review type: architecture artifact review, not application code review.
- Application code, frontend, migrations, seeds and serializers remain out of scope.

## Findings Closed

### AR-001 - Temporal implementation was not explicitly gated by astronomical proof

Status: closed.

Risk: the roadmap could be read as allowing a public temporal runtime implementation before CS-241 production-mode proof and sensitive golden cases are hardened.

Correction:

- `00-architecture-plan.md` now places `SC-Astronomy-Proof` before `SC-First-Temporal` in the ordered roadmap.
- `SC-First-Temporal` now depends on `SC-Astronomy-Proof`.
- `03-story-candidates.md`, `04-risk-matrix.md`, `02-gap-register.md` and `05-executive-summary.md` now state that public temporal runtime implementation is gated by astronomy proof or explicit product risk acceptance.

### AR-002 - Architecture review evidence was embedded but not dedicated

Status: closed.

Risk: the evidence log mentioned review status, but there was no architecture-local review artifact.

Correction:

- This file records the architecture review outcome and the corrections made after review.
- `05-executive-summary.md` references this dedicated review.

### AR-003 - `needs-tracker-remap` was correct but not operational enough

Status: closed.

Risk: implementers could generate follow-up stories from source labels such as CS-243, CS-244 or CS-245 even though those IDs are already allocated.

Correction:

- `00-architecture-plan.md` now forbids implementation story generation before `_condamad/stories/story-status.md` receives concrete new IDs.
- `03-story-candidates.md` now repeats that no implementation story should be generated until tracker remap is done.
- `02-gap-register.md`, `04-risk-matrix.md` and `05-executive-summary.md` make tracker remap an implementation gate.

## Final Architecture Checks

- Runtime decision remains stable: `ChartObjectRuntimeData` is internal canonical runtime, not public payload.
- Graph decision remains stable: `CalculationGraph` is the target orchestration mechanism, gated by registry, manifest, node IO schema, trace and cache/invalidation ownership.
- Public projection decision remains stable: product/API/frontend must consume named projections, not raw runtime objects.
- Temporal implementation gate is now explicit: astronomy proof precedes public temporal runtime.
- Tracker gate is now explicit: remapped story IDs precede implementation story generation.

## Residual Risks

- Product still needs to choose the first temporal technique.
- Security/product still need to decide admin/debug/replay exposure.
- Doctrine/product still need to decide non-planetary taxonomy, school governance and aspectability policy.
- Tracker owner still needs to assign concrete IDs for all `needs-tracker-remap` candidates.
