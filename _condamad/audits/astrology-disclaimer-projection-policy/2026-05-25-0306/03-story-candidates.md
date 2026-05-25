# Story Candidates

## SC-001 Canonical CS-284 Disclaimer Projection Policy

- Source finding: F-001
- Suggested story title: Create canonical astrology disclaimer projection policy
- Suggested archetype: documentation-policy-convergence
- Primary domain: astrology-disclaimer-projection-policy
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Create the documentation-only `astrology_disclaimer_projection_policy` and evidence inventory that maps static application-controlled disclaimers to B2C projection plans without changing application code.
- Closure intent: full-closure
- Must include: exact `policy_id`, inventory scope backend/frontend/docs/briefs, usage classes `natal`, `prediction`, `AI`, `degraded mode`, `missing birth time`, plan matrix for `free`, `basic`, `premium`, LLM non-authorship rule, admin-exposure exclusion, text-delta justification section, and source checklist.
- Validation hints: `rg -n "astrology_disclaimer_projection_policy|disclaimer_registry|get_disclaimers" docs/architecture/astrology-disclaimer-projection-policy.md`; `rg -n "natal|prediction|AI|degraded mode|missing birth time" docs/architecture/astrology-disclaimer-projection-policy.md`; `rg -n "free|basic|premium|projection plan|B2C" docs/architecture/astrology-disclaimer-projection-policy.md`; `git status --short -- backend/app frontend/src backend/tests backend/migrations`.
- Blockers: Stop and request product/legal decision if the story requires new legal wording beyond an identified inventory gap.

### Exhaustive Files To Modify

- Application files: none.
- Governance/docs files: `docs/architecture/astrology-disclaimer-projection-policy.md`, `docs/architecture/official-product-primitives-public-projections.md`.
- CONDAMAD evidence files: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`, `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt`, `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt`, `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md`.

### Closure Proof Required

- Before evidence: absence of policy/evidence artifacts and current inventory scan.
- After evidence: policy document exists and contains required fields; inventory artifact covers backend, frontend, docs, and brief; app/API scoped status shows no implementation drift.
- Reintroduction guard: scoped scans for LLM non-authorship, plan mapping, degraded/no-time coverage, and no new route/OpenAPI surface.
- Allowlist policy: no wildcard allowlist; any excluded surface must be named with reason.
- Stop condition: finding is closed when the policy and evidence artifacts exist and all required scans pass with no app code changes.

### Expected File Classification Changes

- `docs/architecture/astrology-disclaimer-projection-policy.md`: `needs-user-decision` to `used`.
- CS-284 evidence artifacts: absent to `test-only` or governance evidence.
- Application source surfaces: remain `used` or `out-of-domain`; none should move to `delete-candidate`.

## SC-002 Degraded And Missing Birth Time Disclaimer Matrix

- Source finding: F-003
- Suggested story title: Map degraded and missing birth time disclaimers for B2C projections
- Suggested archetype: documentation-policy-convergence
- Primary domain: astrology-disclaimer-projection-policy
- Required contracts: Contract Shape, Ownership Routing, Persistent Evidence, Reintroduction Guard
- Draft objective: Extend the CS-284 policy with a finite matrix for `no_time`, `no_location`, and `no_location_no_time` disclaimer coverage by free/basic/premium projection plan.
- Closure intent: full-closure
- Must include: reuse `natal_context.py` degraded mode names, state whether current static registry text covers each state, record product gaps with owner and next action where copy is absent, and avoid adding runtime behavior unless separately authorized.
- Validation hints: `rg -n "no_time|no_location|no_location_no_time|missing birth time|degraded mode" docs/architecture/astrology-disclaimer-projection-policy.md`; `rg -n "free|basic|premium|gap_status|next_action" docs/architecture/astrology-disclaimer-projection-policy.md`.
- Blockers: Product/legal decision required if a new no-time or degraded-state disclaimer text must be authored.

### Exhaustive Files To Modify

- Application files: none.
- Governance/docs files: `docs/architecture/astrology-disclaimer-projection-policy.md`.
- CONDAMAD evidence files: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`, `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md`.

### Closure Proof Required

- Before evidence: current degraded terminology scan and absent CS-284 matrix.
- After evidence: policy matrix names every degraded mode and every B2C plan or records a product gap with owner and next action.
- Reintroduction guard: targeted scan for all degraded mode identifiers and plan codes in the policy.
- Stop condition: no degraded/missing-birth-time state remains unmapped or without explicit product-gap owner.

### Expected File Classification Changes

- `backend/app/services/llm_generation/shared/natal_context.py`: remains `used` as terminology owner and is not modified.
- `docs/architecture/astrology-disclaimer-projection-policy.md`: becomes `used` as policy owner after SC-001/SC-002.

## Deferred Non-Domain Candidates

- Guidance disclaimer runtime convergence for `F-002` should be handled by a separate `backend/app/services/llm_generation/guidance` service-boundary story after SC-001 establishes the canonical policy owner. Exact future surfaces: `backend/app/services/llm_generation/guidance/guidance_service.py`, `backend/app/tests/unit/test_guidance_service.py`, and `backend/app/tests/integration/test_guidance_api.py`. CS-284 must not implement this code change.
- Prompt seed cleanup for `backend/app/ops/llm/bootstrap/seed_29_prompts.py` should be handled by prompt-generation governance if those seeds are still active. This audit does not recommend deletion because ownership cannot be proven from the disclaimer policy boundary alone.
- LLM schema compatibility for older `AstroResponseV1/V2` disclaimer fields needs a separate contract-shape decision if runtime compatibility requires those fields to remain.
