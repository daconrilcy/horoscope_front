# Unclassified Rule Guard

Guard owner:

- `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`

Canonical classification owner:

- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`

Guard behavior:

- Parses Python files under `backend/app/domain/astrology`.
- Detects AST names, attributes, args, class/function names, and string constants containing `threshold`, `weight`, `profile`, `school`, or `doctrine`.
- Requires every existing marker surface to be listed in `GOVERNED_RULE_SOURCE_SURFACES`.
- Proves a synthetic unclassified `new_school_weights.py` marker is rejected.

Validation:

- `python -B -m pytest -q backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`
- Covered again in full `backend/tests` run.

Result: PASS.
