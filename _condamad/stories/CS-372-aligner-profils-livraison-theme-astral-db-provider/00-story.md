# Story CS-372 aligner-profils-livraison-theme-astral-db-provider: Align Theme Astral Delivery Profiles Across DB And Provider
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-372-aligner-delivery-profiles-db-provider-theme-astral.md`.
- Selected mode: Repo-informed story.
- Source problem statement: the `theme_astral` provider exposes `essential`, `expanded`, and `complete`, while persisted DB contracts still use `essential` and `deep`.
- Source stakes:
  - User impact: persisted prompt assemblies can diverge from payloads that are actually sent to the LLM.
  - Technical risk: tests currently lock a two-depth DB contract that contradicts the provider contract.
  - Closure expectation: constants, seed, active reads, persistence tests, docs, examples, and delivery report must agree on one canonical depth set.
  - Forbidden regression: commercial labels `free`, `basic`, and `premium` must not become LLM-visible payload values.
- Source-alignment evidence: objective, ACs, tasks, scans, and guardrails map to every included source item from the brief.

## Objective

Align the canonical `theme_astral` delivery profile depths to `essential`, `expanded`, and `complete` across domain constants, DB seed assemblies,
active contract resolution, persistence tests, provider payload tests, and impacted documentation evidence.

## Target State

- `THEME_ASTRAL_DELIVERY_PROFILES` exposes exactly `essential`, `expanded`, and `complete`.
- `THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES` still resolves commercial plans to non-commercial delivery depths.
- Seeding publishes one active assembly for each canonical depth.
- Active contract resolution accepts the three canonical depths.
- Existing active `deep` assemblies are archived or invalidated during the next seed run.
- Tests prove persistence, versioning, active reads, provider payload privacy, and absence of active `deep`.
- Documentation, examples, and the CS-361 to CS-371 delivery report stop contradicting the canonical DB depth set.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-372-aligner-delivery-profiles-db-provider-theme-astral.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-372` after `CS-371`.
- Evidence 3: `backend/app/domain/llm/configuration/theme_astral_contracts.py` - targeted scan found `THEME_ASTRAL_DELIVERY_PROFILES` with `essential` and `deep`.
- Evidence 4: `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` - targeted scan found persistence assertions for active `deep`.
- Evidence 5: `.agents/skills/condamad-story-writer/scripts/resolve_guardrails.py` - resolver returned local guardrails `RG-002` and `RG-022`.
- Evidence 6: `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - targeted scan found delivery profile docs in scope.

## Domain Boundary

- Domain: backend-llm-prompt-contract
- In scope:
  - `theme_astral` delivery profile constants.
  - Seeded prompt contract assemblies for `theme_astral`.
  - Active prompt contract resolution for `theme_astral`.
  - Provider payload depth mapping and privacy checks.
  - Persistence, integration, and orchestration tests named in the source brief.
  - Impacted prompt-generation documentation, examples, and delivery report.
- Out of scope:
  - Frontend UI, auth, i18n, styling, unrelated API routes, unrelated DB domains, build tooling, and migrations outside `theme_astral`.
  - Changing commercial backend plan names `free`, `basic`, and `premium`.
  - Modifying the LLM provider integration.
  - Changing another feature family.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No new prompt provider behavior beyond the canonical depth alignment.
  - No broad persistence refactor outside the prompt contract seed and read path.

## Operation Contract

- Operation type: converge
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Align only the `theme_astral` delivery depth contract.
  - The only allowed active depth set is `essential`, `expanded`, and `complete`.
  - Commercial plan names remain backend-side inputs only.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: runtime evidence proves external active consumers require active `deep`.
- Additional validation rules:
  - `AST guard` or targeted `rg` must prove no active runtime `deep` branch remains in the scoped files.
  - `pytest -q backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` must prove DB seed and read behavior.
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` must prove provider payload privacy.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | DB seed, active resolver, provider builder tests, and loaded test DB behavior prove the runtime contract. |
| Baseline Snapshot | yes | Before and after evidence must show the delivery depth set changed to the canonical three-depth set. |
| Ownership Routing | yes | Domain constants, seed behavior, docs, and tests have separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for active `deep` or commercial labels in LLM payloads. |
| Contract Shape | yes | Delivery profile fields, depth values, active assembly shape, and provider payload privacy are exact contracts. |
| Batch Migration | no | No broad batch conversion or Alembic migration is in scope for this story. |
| Reintroduction Guard | yes | Active `deep` and LLM-visible commercial labels must stay absent from runtime surfaces. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Persisted active depths are canonical. | Evidence profile: json_contract_shape; `pytest`; `tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC2 | Provider depths match persisted depths. | Evidence profile: json_contract_shape; `pytest`; `tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC3 | Seed publishes one assembly per depth. | Evidence profile: json_contract_shape; `pytest`; `tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC4 | Active resolution accepts canonical depths. | Evidence profile: json_contract_shape; `pytest`; `tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC5 | Active `deep` is not published after seed. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan plus persistence `pytest`. |
| AC6 | Provider payloads do not expose commercial labels. | Evidence profile: targeted_forbidden_symbol_scan; `rg` provider JSON; `pytest` provider tests. |
| AC7 | Documentation matches canonical depths. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` persistence tests; `rg` docs. |
| AC8 | Examples match canonical depths. | Evidence profile: targeted_forbidden_symbol_scan; `rg` example files; provider `pytest`. |
| AC9 | Delivery report matches canonical depths. | Evidence profile: targeted_forbidden_symbol_scan; `rg` delivery report. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the story evidence directory. |

## Implementation Tasks

- [ ] Task 1: Inspect the current domain constants and classify active depth owners. (AC: AC1, AC2)
- [ ] Task 2: Align `THEME_ASTRAL_DELIVERY_PROFILES` to `essential`, `expanded`, and `complete`. (AC: AC1, AC2)
- [ ] Task 3: Align the seed so it publishes exactly one active assembly per canonical depth. (AC: AC3)
- [ ] Task 4: Archive or invalidate active `deep` assemblies during the next seed run. (AC: AC5)
- [ ] Task 5: Align active contract resolution so it accepts the three canonical depths. (AC: AC4)
- [ ] Task 6: Update persistence and bigbang tests to prove canonical seeded assemblies. (AC: AC1, AC3, AC4, AC5)
- [ ] Task 7: Update provider payload tests so commercial labels remain backend-only. (AC: AC2, AC6)
- [ ] Task 8: Update impacted docs and delivery report with canonical depth wording. (AC: AC7, AC9)
- [ ] Task 9: Update impacted examples with canonical depth wording. (AC: AC8)
- [ ] Task 10: Persist before and after evidence artifacts plus validation output. (AC: AC10)

## Files to Inspect First

- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`

## Runtime Source of Truth

- Primary source of truth:
  - `THEME_ASTRAL_DELIVERY_PROFILES`.
  - DB schema-backed prompt assembly records loaded by pytest integration tests.
  - `AST guard` or targeted import scan for active runtime symbols.
  - Seeded `theme_astral` prompt assemblies in the test DB.
  - `resolve_active_theme_astral_prompt_contract`.
  - Provider payload builder tests for commercial-plan resolution.
- Secondary evidence:
  - Targeted `rg` scans for `deep`, canonical depth names, and commercial label leakage.
- Static scans alone are not sufficient for this story because:
  - Seed behavior and active resolver behavior must be proven against runtime DB state.

## Contract Shape

- Contract type:
  - Versioned prompt contract delivery profile for `theme_astral`.
- Fields:
  - `profile_id`: non-commercial profile identifier.
  - `depth`: one of `essential`, `expanded`, or `complete`.
  - `selection_policy`: policy matching the canonical depth.
  - `max_sections`: numeric bound matching the canonical depth.
  - `detail_level`: non-commercial detail descriptor.
- Required fields:
  - `profile_id`
  - `depth`
  - `selection_policy`
  - `max_sections`
  - `detail_level`
- Optional fields:
  - none newly authorized by this story.
- Status codes:
  - none; this backend domain story does not define an HTTP response contract.
- Serialization names:
  - `depth` is emitted as `depth`.
  - `delivery_profile` is emitted as `delivery_profile`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - Generated provider examples must not contain commercial labels as JSON values.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/depths-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/depths-after.txt`
- Expected invariant:
  - The only intended depth-set change is from `essential` and `deep` to `essential`, `expanded`, and `complete`.
- Required proof:
  - Before and after artifacts must include the targeted `rg` outputs and the targeted pytest command results.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Delivery profile constants | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Seed-local duplicated profile maps |
| Seeded prompt assemblies | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | Test fixtures as runtime source |
| Active read behavior | prompt contract persistence resolver path | Provider payload builder code |
| Provider plan resolution | `THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES` | DB seed logic |
| Documentation evidence | `_condamad/docs` and `_condamad/examples` scoped files | Backend runtime code comments |

## Mandatory Reuse / DRY Constraints

- Reuse the canonical delivery profile constants for seed assembly generation.
- Do not duplicate full delivery profile maps in tests.
- Tests may assert the canonical set, but runtime values must come from the domain contract owner.
- Documentation examples must describe the same non-commercial depths as runtime code.
- Keep the provider mapping as resolution from commercial plans to non-commercial delivery depths.

## No Legacy / Forbidden Paths

- No legacy active `deep` delivery profile may remain for `theme_astral`.
- No compatibility mapping may keep `deep` active for seeded assemblies.
- No fallback mapping may translate `deep` to a canonical depth at runtime.
- No commercial label may be serialized into LLM-visible provider payload values.
- Historical mentions of `deep` are allowed only in evidence or documentation that explicitly marks them as non-runtime history.

## Removal Classification Rules

- `canonical-active`: `essential`, `expanded`, and `complete` delivery depths owned by the canonical domain constants.
- `external-active`: an externally consumed active `deep` contract proven by scoped docs, generated payloads, or runtime evidence.
- `historical-facade`: a non-runtime `deep` mention kept only to describe previous behavior.
- `dead`: a `deep` runtime branch, seeded active assembly, or test fixture with zero authorized current consumers.
- `needs-user-decision`: a `deep` consumer with proven external active usage and no safe canonical replacement.

## Removal Audit Format

The implementation must write this audit table to
`_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/deep-consumption-audit.md`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Canonical delivery depths | `THEME_ASTRAL_DELIVERY_PROFILES` | Active `deep` seed rows and duplicated fixture maps |
| Provider plan to depth mapping | `THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES` | Commercial labels in LLM-visible payload fields |
| Active persisted assemblies | Seeded prompt contract assembly records | Historical active `deep` rows |
| Human evidence | Scoped `_condamad` docs, examples, reports | Runtime code comments as sole proof |

## Delete-Only Rule

- Runtime `deep` surfaces classified as `dead` must be deleted from active code paths or made inactive in seeded DB records.
- Do not redirect `deep` to `expanded` or `complete`.
- Do not preserve a wrapper for `deep`.
- Do not add a compatibility alias for `deep`.
- Do not replace active `deep` with a soft-disable branch that remains accepted by active resolution.

## External Usage Blocker

- External usage blocker: active `deep` may remain only when scoped evidence proves external active consumption.
- Required blocker evidence:
  - exact file path or generated artifact path;
  - consumer owner;
  - risk of deleting active `deep`;
  - user decision required before implementation continues.

## Generated Contract Check

- Generated contract check: required for generated provider examples.
- Required proof:
  - `rg` checks the scoped provider JSON examples for commercial labels as JSON values.
  - `rg` checks `:\s*"(free|basic|premium)"` in scoped provider JSON examples.
  - `rg` checks scoped docs and examples for `deep` and classifies any remaining mention as non-runtime history.

## Reintroduction Guard

- Forbidden runtime symbols or states:
  - active `deep` in `THEME_ASTRAL_DELIVERY_PROFILES`;
  - seeded active `deep` prompt assembly;
  - resolver acceptance of `depth="deep"`;
  - JSON payload values `"free"`, `"basic"`, or `"premium"` in LLM-visible provider examples.
- Required deterministic guard:
  - `pytest -q backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
  - `rg -n "deep" app/domain/llm/configuration/theme_astral_contracts.py`
  - `rg -n "deep" app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
  - `rg -n "deep" tests/integration/test_theme_astral_prompt_contract_persistence.py`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend logic must not drift into unrelated API routing surfaces. | Targeted `rg`; backend `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must point to collected pytest files. | `pytest` paths listed in Validation Plan. |
| Registry gap `theme_astral-depths` | No exact route or profile-specific guardrail was found for this depth contract. | Resolver output and targeted registry `rg`. |

Non-applicable examples retained to prevent scope drift:

- `RG-047` frontend inline styles is out of scope because this story touches no TSX or CSS surface.
- `RG-052` frontend CSS namespaces is out of scope because no design-token or stylesheet migration is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before depth scan | `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/depths-before.txt` | Capture current profile divergence. |
| After depth scan | `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/depths-after.txt` | Prove canonical depth alignment. |
| Deep consumption audit | `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/deep-consumption-audit.md` | Classify remaining `deep` mentions. |
| Validation output | `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/validation.txt` | Keep final lint and test commands. |
| Review output | `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for active `deep` or commercial labels in LLM-visible provider payloads.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - canonical delivery profile constants and validation.
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` - seeded active assemblies and `deep` archival behavior.
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` - persistence, versioning, active read, and `deep` inactivity tests.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - provider mapping and commercial-label privacy tests.
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` - bigbang proof for canonical depths.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - canonical depth documentation.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` - example comparison.
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md` - delivery report note.

Likely tests:

- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/**` - out of scope unless existing seed persistence code already owns the active assembly update.
- `backend/alembic/**` - out of scope; no schema migration is authorized by this story.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after:

- `.\.venv\Scripts\Activate.ps1`

From `backend`:

- VC1: `ruff format .`
- VC2: `ruff check .`
- VC3: `python -B -m pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py --tb=short`
- VC4: `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
- VC5: `rg -n "essential|expanded|complete|deep|THEME_ASTRAL_DELIVERY_PROFILES|THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES" app tests`
- VC6: `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
- VC7: `rg -n "deep" app/domain/llm/configuration/theme_astral_contracts.py`
- VC8: `rg -n "deep" app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- VC9: `rg -n "deep" tests/integration/test_theme_astral_prompt_contract_persistence.py`

From repository root:

- VC10: `rg -n '"plan"\s*:|"free"\s*:|"basic"\s*:|"premium"\s*:' _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json`
- VC11: `rg -n '"plan"\s*:|"free"\s*:|"basic"\s*:|"premium"\s*:' _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
- VC12: `rg -n '"plan"\s*:|"free"\s*:|"basic"\s*:|"premium"\s*:'`
  `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- VC13: `rg -n ':\s*"(free|basic|premium)"' _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json`
- VC14: `rg -n "essential|expanded|complete|deep" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- VC15: `rg -n "essential|expanded|complete|deep" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- VC16: `rg -n "essential|expanded|complete|deep" _condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`
- VC17: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/evidence/validation.txt').exists()"`

Interpretation rule:

- VC7, VC8, and VC9 must fail or return only explicitly non-runtime historical mentions.
- VC10, VC11, and VC12 must return no JSON value exposure for commercial labels.

## Regression Risks

- Fixing only tests would leave seeded runtime contracts divergent from provider payloads.
- Fixing only provider constants would leave active DB assemblies stale.
- Keeping active `deep` as a compatibility path would preserve the divergence the story must close.
- Updating examples without tests would make documentation appear aligned while runtime remains unproven.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all new or significantly modified Python files documented with French module comments and French docstrings for public or non-trivial code.
- Do not add a base folder under `backend/` without explicit user agreement.
- Do not change commercial backend plan names.

## References

- `_story_briefs/cs-372-aligner-delivery-profiles-db-provider-theme-astral.md`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`
