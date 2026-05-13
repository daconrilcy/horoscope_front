# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Context/repo tests | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_context_loader.py` | `backend` | yes | pass |
| Scoring non-regression | targeted pytest bundle | `backend` | yes | pass |
| Old symbol scan | `rg -n "HouseProfileData" app tests -g "*.py"` | `backend` | yes | zero hit |
| Product field scan | `rg -n "visibility_weight|base_priority|routing_role" app/domain/astrology -g "*.py"` | `backend` | yes | zero hit |
