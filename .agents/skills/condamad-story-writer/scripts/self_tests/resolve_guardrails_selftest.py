import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "resolve_guardrails.py"
SPEC = importlib.util.spec_from_file_location("resolve_guardrails", SCRIPT_PATH)
assert SPEC is not None
resolve_guardrails = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(resolve_guardrails)


REGISTRY = """
| ID | Source story | Surface protegee | Invariant | Guard attendu |
|---|---|---|---|---|
| RG-002 | `bootstrap-backend-layout` | Structure backend racine | Backend layout. | guard |
| RG-003 | `bootstrap-api-boundary` | `backend/app/api` | API boundary. | guard |
| RG-007 | `bootstrap-api-contracts` | Contrats API | API contracts. | guard |
| RG-020 | `bootstrap-auth-security` | Authentification et autorisation | Auth. | guard |
| RG-022 | `bootstrap-tests` | Topologie des tests Python | Tests. | guard |
| RG-027 | `bootstrap-frontend-layout` | Structure frontend React/Vite | Frontend. | guard |
| RG-041 | `bootstrap-build` | Build Vite | Build. | guard |
| RG-047 | `bootstrap-local-validation` | Validation locale sans CI | Validation. | guard |
| RG-052 | `bootstrap-no-legacy` | No Legacy | No legacy. | guard |
| RG-053 | `health-endpoint` | `GET /health` backend API | Health. | guard |
"""


class ResolveGuardrailsSelfTest(unittest.TestCase):
    def test_backend_health_scope_selects_local_subset(self) -> None:
        rows = resolve_guardrails.parse_guardrail_rows(REGISTRY)
        scope = resolve_guardrails.normalize_scope(
            [
                "create",
                "backend-api",
                "backend/app/api",
                "backend/tests/api",
                "GET /health",
                "openapi",
                "json-response",
            ]
        )

        selection = resolve_guardrails.select_guardrail_ids(scope, rows)

        self.assertEqual(selection["universal"], ["RG-047", "RG-052"])
        self.assertEqual(
            selection["applicable"],
            ["RG-002", "RG-003", "RG-007", "RG-022", "RG-053"],
        )
        self.assertEqual(selection["non_applicable_examples"], ["RG-041", "RG-020"])

    def test_unknown_scope_keeps_only_universal(self) -> None:
        rows = resolve_guardrails.parse_guardrail_rows(REGISTRY)
        selection = resolve_guardrails.select_guardrail_ids("documentation", rows)

        self.assertEqual(selection["universal"], ["RG-047", "RG-052"])
        self.assertEqual(selection["applicable"], [])


if __name__ == "__main__":
    unittest.main()
