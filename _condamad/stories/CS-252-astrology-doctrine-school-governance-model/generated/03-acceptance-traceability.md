# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | All CS-240 rule families are registered. | `MANDATORY_RULE_FAMILIES`, `ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS`, `list_astrology_doctrine_governance()` in `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`. | `test_governance_declares_all_cs_240_rule_families_once`; `governance-after.json`. | PASS |
| AC2 | Each rule family exposes owner status. | `RuleSourceOwnerStatus`, `CanonicalRuleOwner`, and `AstrologyDoctrineGovernanceEntry.source_owner_status`. | `test_each_rule_family_exposes_required_contract_fields`; status scan in `evidence/validation.md`. | PASS |
| AC3 | CS-241 F-003 weighting owners are explicit. | `CS_241_F003_WEIGHTING_FAMILIES` entries for `dominance_weights`, `sign_profiles`, `house_weights`, `dignity_weights`. | `test_cs_241_f003_weighting_families_have_owner_or_blocker`. | PASS |
| AC4 | Doctrine decisions stay separate. | Separate `source_owner_status`, `canonical_owner`, `doctrine_decision_status`, `school_policy`, and `version_policy` fields. | `test_doctrine_decisions_are_separate_from_source_ownership`. | PASS |
| AC5 | Allowed transitions are enforced. | `ALLOWED_OWNER_STATUS_TRANSITIONS`, `ALLOWED_DOCTRINE_STATUS_TRANSITIONS`, transition validators. | `test_allowed_owner_and_doctrine_transitions_are_enforced`. | PASS |
| AC6 | `needs-user-decision` values are preserved. | Unresolved entries retain `DoctrineDecisionStatus.NEEDS_USER_DECISION` and non-empty blockers. | `test_needs_user_decision_values_are_preserved`. | PASS |
| AC7 | New unclassified rule markers fail. | `GOVERNED_RULE_SOURCE_SURFACES` plus AST guard in `test_astrology_doctrine_governance_guardrails.py`. | `test_rule_marker_surfaces_are_declared_in_doctrine_governance`; `test_unclassified_new_rule_marker_fails_guard`. | PASS |
| AC8 | Future temporal techniques can cite the model. | `TEMPORAL_TECHNIQUE_CITATION_NOTES` includes CS-253 and traditional/modern/forecasting note. | `test_future_temporal_techniques_can_cite_governance_model`; targeted `rg` scan. | PASS |
| AC9 | Public API runtime contract is unchanged. | No API route or serializer changed; API neutrality test extended for CS-252. | `test_astrology_doctrine_governance_is_not_public_api_contract`; `app.routes`; `app.openapi()` checks. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/governance-before.md`, `governance-after.json`, `unclassified-rule-guard.md`, `openapi-routes.md`, `validation.md`. | Evidence path checks and capsule validation. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
