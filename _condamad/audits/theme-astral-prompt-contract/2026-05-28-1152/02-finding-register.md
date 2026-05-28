# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | theme-astral-prompt-contract | E-004, E-005, E-006 | Rich interpretive sources exist, but current provider handoff is mainly facts/codes/short hints. | Define a target `theme_astral_llm_input_v1` contract and material owner before implementation. | yes |
| F-002 | High | High | missing-canonical-owner | theme-astral-prompt-contract | E-005, E-006, E-008 | Provider payload shape has no stable table-derived interpretation material block, so enrichment can be duplicated or ad hoc. | Add a stable provider payload builder contract after CS-363/CS-365 define the material source. | yes |
| F-003 | Medium | Medium | duplicate-responsibility | theme-astral-prompt-contract | E-004, E-005, E-007 | Seed/admin/reference text owners are numerous and not routed by one prompt-visible selection rule. | Version and persist contract/source ownership decisions before wiring material into runtime. | yes |
| F-004 | Medium | High | missing-guard | theme-astral-prompt-contract | E-001, E-007, E-009 | Existing guards protect adjacent prompt and astrology surfaces but do not prove rich-source reachability after future migration. | Add closure audit and guards that distinguish source existence, projection reach, LLM input reach and provider reach. | yes |

## F-001 Rich source material does not reach provider as controlled prose

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: theme-astral-prompt-contract
- Evidence: E-004, E-005, E-006
- Expected rule: Existing interpretive tables and references must not be confused with effective prompt-visible material; runtime reach must be explicit.
- Actual state: The handoff sends facts, signals, limits and shaping. Rich house, planet, aspect and reference prose is not proven provider-visible.
- Impact: Rich interpretive sources exist, but current provider handoff is mainly facts/codes/short hints.
- Recommended action: Define a target `theme_astral_llm_input_v1` contract and material owner before implementation.
- Story candidate: yes
- Suggested archetype: contract-shape-audit followed by architecture story.

## F-002 Provider payload lacks stable table-derived material block

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: theme-astral-prompt-contract
- Evidence: E-005, E-006, E-008
- Expected rule: Provider payload composition should have one canonical owner for prompt-visible interpretive material.
- Actual state: `LLMGateway` filters the current internal contract correctly, but examples show short hints rather than stable table-derived material.
- Impact: Provider payload shape has no stable table-derived interpretation material block, so enrichment can be duplicated or ad hoc.
- Recommended action: Add a stable provider payload builder contract after CS-363/CS-365 define the material source.
- Story candidate: yes
- Suggested archetype: provider-payload-builder-convergence.

## F-003 Multiple text owners lack one runtime selection decision

- Severity: Medium
- Confidence: Medium
- Category: duplicate-responsibility
- Domain: theme-astral-prompt-contract
- Evidence: E-004, E-005, E-007
- Expected rule: Seed, DB, repository and static catalog sources need clear ownership before prompt-visible runtime selection.
- Actual state: Source families are split across DB models, seed JSON, seed services, repositories, static catalogs and docs.
- Impact: Seed/admin/reference text owners are numerous and not routed by one prompt-visible selection rule.
- Recommended action: Version and persist contract/source ownership decisions before wiring material into runtime.
- Story candidate: yes
- Suggested archetype: persistence-contract-ownership.

## F-004 Future closure needs reachability guardrails

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: theme-astral-prompt-contract
- Evidence: E-001, E-007, E-009
- Expected rule: A future closure audit must prove each source family as source existence, projection reach, LLM input reach and provider reach.
- Actual state: Current tests prove payload boundaries and signal presence, not rich-source reachability after the planned migration.
- Impact: Existing guards protect adjacent prompt and astrology surfaces but do not prove rich-source reachability after future migration.
- Recommended action: Add closure audit and guards that distinguish source existence, projection reach, LLM input reach and provider reach.
- Story candidate: yes
- Suggested archetype: closure-audit-guard-hardening.
