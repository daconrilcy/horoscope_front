# Validation finale CS-342 - Evidence hors prompt natal

## Synthese

La frontiere finale est validee: le message utilisateur remis au provider natal ne recoit que les blocs `facts`, `signals`, `limits` et `shaping`. Les donnees `evidence`, `evidence_refs`, `grounding_status`, `validation_owner`, `provenance`, `projection_hash` et `llm_input_hash` restent internes au backend pour validation post-generation ou audit persistant.

Cette cloture ne lance aucun appel provider reel. La preuve repose sur les gardes AST, les tests de projection provider, les tests de validation des reponses generees et les tests d'audit natal.

## Blocs visibles dans le prompt

| Bloc | Statut | Owner canonique |
|---|---|---|
| `facts` | prompt-visible | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` |
| `signals` | prompt-visible | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` |
| `limits` | prompt-visible | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` |
| `shaping` | prompt-visible | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` |

Preuve runtime: `backend/app/domain/llm/runtime/gateway.py` derive `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS` depuis `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`, puis projette uniquement ces blocs dans le message provider.

## Donnees hors prompt

| Donnee | Classification finale | Owner |
|---|---|---|
| `evidence` | validation-only | `llm_astrology_input_v1.py` |
| `evidence_refs` | validation-only et audit persistante | `evidence_refs_validation.py`, `interpretation_service.py` |
| `grounding_status` | validation-only et audit persistante | `evidence_refs_validation.py`, `interpretation_service.py` |
| `validation_owner` | validation-only | `llm_astrology_input_v1.py` |
| `provenance` | audit-only | `llm_astrology_input_v1.py` |
| `projection_hash` | audit-only | `projection_hash.py`, `interpretation_service.py` |
| `llm_input_hash` | audit-only | `llm_astrology_input_v1.py`, `interpretation_service.py` |
| `provider_response` | audit-only | `interpretation_service.py` |
| `persisted_answer` | audit-only | `interpretation_service.py` |

## Preuve de handoff provider

Tests executables:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py::test_gateway_payload_projects_prompt_visible_role_blocks_only`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py::test_gateway_payload_makes_missing_data_limits_prompt_visible`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py::test_gateway_payload_does_not_promote_raw_or_legacy_prompt_owners`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py::test_gateway_prompt_projection_reuses_canonical_prompt_visible_roles`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py::test_gateway_prompt_projection_removes_nested_audit_and_validation_keys`

Resultat: le payload provider exclut `evidence`, `evidence_refs`, `grounding_status`, `validation_owner`, `provenance`, `projection_hash`, `llm_input_hash`, `chart_json` et `natal_data`.

## Preuve de validation post-generation

Tests executables:

- Cas conforme accepte: `test_grounded_validation_does_not_create_rejection`.
- Donnee inventee rejetee: `test_unsupported_generated_claim_becomes_rejected` et `test_backend_detects_unsupported_generated_claim_without_llm_marker`.
- Donnee manquante ou limite contredite rejetee: `test_missing_evidence_refs_on_required_sections_becomes_rejected`, `test_ignored_critical_limit_becomes_rejected` et `test_backend_detects_ignored_critical_limit_without_llm_marker`.
- Redaction interne non fondee rejetee: `test_ungrounded_validation_becomes_rejected_outcome` et `test_invalid_evidence_ref_hash_is_rejected`.

Resultat: la validation backend explique l'acceptation ou le rejet sans exposer les preuves au provider.

## Preuve d'audit persistant

Tests executables:

- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py::test_natal_audit_uses_llm_astrology_input_hashes_and_evidence_refs`
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py::test_runtime_only_request_id_does_not_change_audit_llm_input_hash`

Resultat: `projection_hash`, `llm_input_hash`, `grounding_status` et `evidence_refs` restent disponibles pour l'audit hors prompt.

## Classification des occurrences restantes

| Surface | Occurrences | Classification |
|---|---:|---|
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | evidence, hashes, roles | Contrat interne et validation owner |
| `backend/app/domain/llm/runtime/gateway.py` | exclusions prompt, context vars | Projection provider et garde de frontiere |
| `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | evidence refs, validation outcomes | Validation post-generation |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | audit fields, hash persistence | Audit persistant |
| `backend/tests/llm_orchestration/*` | forbidden provider keys | Guard test provider |
| `backend/tests/architecture/*` | AST guard symbols | Guard test architecture |
| `backend/tests/unit/*` et `backend/tests/integration/*` | validation/audit fixtures | Test owner |
| `_story_briefs/*`, `_condamad/stories/*`, `_condamad/reports/*` | historique et preuves | Evidence historique, non executable |

Les occurrences detectees dans `canonical_use_case_registry.py` et `prompting/context.py` concernent des use cases non natals ou le contexte interne historique; elles ne sont pas des dependances prompt natales actives pour `llm_astrology_input_v1`.

## Validations

- `python -B -m pytest -q backend\tests\llm_orchestration\test_llm_astrology_input_boundaries.py backend\tests\architecture\test_llm_astrology_input_payload_boundaries.py backend\tests\unit\domain\astrology\test_llm_astrology_input_evidence.py backend\tests\unit\test_rejected_narrative_answer_workflow.py backend\tests\integration\llm\test_natal_llm_astrology_input_audit.py --tb=short` - PASS, 21 passed, 2 deselected.
- `python -B -m pytest -q backend\tests --tb=short` - PASS.
- `ruff check .` - PASS.
- `condamad_validate.py _condamad\stories\CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal` - PASS.

## Risques residuels

- Aucun appel provider reel n'est execute par design; la garantie porte sur le contrat de handoff local et les validations backend.
- Les rapports et briefs historiques contiennent encore le vocabulaire `evidence`; ces occurrences sont classees comme preuves/historique et non comme surface executable.
