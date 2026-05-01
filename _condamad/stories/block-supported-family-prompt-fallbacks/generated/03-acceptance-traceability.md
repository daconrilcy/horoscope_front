# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Supported fallback keys absent. | Suppression des cles interdites dans `PROMPT_FALLBACK_CONFIGS`; garde reintroduction. | `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py`; scan `rg`. | PASS |
| AC2 | Production missing assembly rejected. | Pas de fallback prompt pour les cles supportees; test production sur les quatre familles. | `pytest -q tests/llm_orchestration/test_assembly_resolution.py`. | PASS |
| AC3 | Bootstrap exceptions exact. | Audit persistant des exceptions et test d'allowlist exacte. | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`. | PASS |
| AC4 | QA pipeline remains canonical. | Garde anti-retour sans modification des routes QA ni du pipeline assembly. | `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py tests/integration/test_llm_legacy_extinction.py`. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
