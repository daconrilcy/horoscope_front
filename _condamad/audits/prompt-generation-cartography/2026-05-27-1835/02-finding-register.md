<!-- Commentaire global: registre des findings informatifs pour l'audit CS-346. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | backend-domain | E-004, E-005, E-006, E-007, E-014 | Ownership is mapped and no remediation is required. | Keep using current canonical builders. | no |
| F-002 | Info | High | boundary-violation | backend-domain | E-004, E-009, E-012 | Role separation is enforced; no boundary violation remains. | Preserve role reuse through `LLM_ASTROLOGY_INPUT_DATA_ROLES`. | no |
| F-003 | Info | High | legacy-surface | backend-domain | E-004, E-009, E-012, E-013 | Legacy carrier risk is currently guarded for the modern natal prompt. | Keep legacy carrier tests active with `--long` for integration guards. | no |
| F-004 | Info | High | data-integrity-risk | backend-domain | E-008, E-010, E-011, E-014 | Hash and evidence policies are reproducible and test-backed. | Preserve hash material and evidence validation owners. | no |

## F-001 - Canonical Block Ownership Is Traceable

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend-domain
- Evidence: E-004, E-005, E-006, E-007, E-014
- Expected rule: Every `llm_astrology_input_v1` block has one owner and source.
- Actual state: `facts` come from `StructuredFactsV1Builder`, `signals` from `AINarrativeInputContract`, `shaping` from client projection, and the wrapper owns `limits`, `evidence`, `provenance`, `exclusions`, and `data_roles`.
- Impact: Ownership is mapped and no remediation is required.
- Recommended action: Keep using current canonical builders.
- Story candidate: no
- Suggested archetype: audit-observation

## F-002 - Prompt And Backend-Only Roles Are Separated

- Severity: Info
- Confidence: High
- Category: boundary-violation
- Domain: backend-domain
- Evidence: E-004, E-009, E-012
- Expected rule: Prompt-visible fields must stay distinct from runtime-only, validation-only, and audit-only fields.
- Actual state: Gateway projection reuses `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` and recursively excludes validation/audit keys.
- Impact: Role separation is enforced; no boundary violation remains.
- Recommended action: Preserve role reuse through `LLM_ASTROLOGY_INPUT_DATA_ROLES`.
- Story candidate: no
- Suggested archetype: audit-observation

## F-003 - Legacy Carriers Are Forbidden For Modern Natal Prompt

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: backend-domain
- Evidence: E-004, E-009, E-012, E-013
- Expected rule: `chart_json` and `natal_data` must not become modern natal prompt carriers.
- Actual state: They are classified as runtime-only/excluded surfaces and tests prove they are absent from modern prompt payloads.
- Impact: Legacy carrier risk is currently guarded for the modern natal prompt.
- Recommended action: Keep legacy carrier tests active with `--long` for integration guards.
- Story candidate: no
- Suggested archetype: audit-observation

## F-004 - Hash And Evidence Policies Are Source-Backed

- Severity: Info
- Confidence: High
- Category: data-integrity-risk
- Domain: backend-domain
- Evidence: E-008, E-010, E-011, E-014
- Expected rule: Hash and evidence claims must name active helpers and tests.
- Actual state: `build_llm_input_hash_material` covers prompt-visible blocks only; service audit helpers read hash/evidence fields from the full object.
- Impact: Hash and evidence policies are reproducible and test-backed.
- Recommended action: Preserve hash material and evidence validation owners.
- Story candidate: no
- Suggested archetype: audit-observation
