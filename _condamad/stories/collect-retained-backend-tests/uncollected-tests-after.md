# Uncollected Tests After

Static files: 426
Collected files: 425
Uncollected retained files: 0
Opt-in exceptions: 1

## Uncollected retained files

```text
```

## Opt-in exceptions

| File | Reason |
|---|---|
| `app/domain/llm/prompting/tests/test_qualified_context.py` | Package-level collection imports `app/domain/llm/prompting/tests/__init__.py`, which requires missing local `tests/data/prompt_governance_registry.json`; keep exact opt-in until the dedicated topology-convergence story decides whether to move or retire this embedded suite. |
