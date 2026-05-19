<!-- Rapport de garde anti-regression CS-192. -->

# Condition Guard Evidence

Validation:

- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - PASS
- `pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py::test_astrology_domain_does_not_carry_product_symbols` - PASS
- `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" backend/app/domain/astrology/condition -g "*.py"` - PASS, zero hit
- `rg -n "OpenAI|AIEngineAdapter|chat\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/condition -g "*.py"` - PASS, zero hit
- `rg -n "VISIBILITY_WEIGHTS|CONDITION_SCORES|CONDITION_LEVELS|astral_chart_planet_condition_profiles" backend/app backend/migrations backend/tests -g "*.py"` - PASS, zero hit

OpenAPI:

- Aucune route nouvelle n'est creee.
- Le payload `chart_json` est construit dynamiquement par
  `build_chart_json`; la story ajoute `planet_condition_profiles` a cette
  projection sans schema OpenAPI dedie modifie.

Guardrails:

- `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116`, `RG-118` preserves.
- `RG-119` couvert par le test de garde condition et les scans ci-dessus.
