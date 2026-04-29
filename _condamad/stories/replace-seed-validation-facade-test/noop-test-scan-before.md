# No-op Test Scan Before

Command run before implementation:

```powershell
rg -n "assert True|pass$" backend/app/tests backend/tests -g test_*.py
```

Relevant baseline findings:

- `backend/app/tests/unit/test_seed_validation.py:5` contained a collected test whose executable body was only `pass`.
- `backend/app/tests/unit/test_pricing_experiment_service.py:76` used `assert True` in the success branch of an exception-based assertion.
- Other `pass$` hits were nested helper/control-flow statements inside existing tests, not direct empty collected test bodies.

Decision:

- Replace the seed facade with executable seed validation assertions.
- Replace the `assert True` pricing assertion with `pytest.raises`.
- Add an AST guard that distinguishes direct no-op test bodies from nested `pass` control-flow statements.
