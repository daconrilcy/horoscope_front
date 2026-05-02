# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- `_condamad/stories/regression-guardrails.md`
- `scripts/validate_route_removal_audit.py`
- `_condamad/stories/remove-historical-facade-routes/00-story.md`
- `_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md`
- `_condamad/stories/remove-historical-facade-routes/generated/03-acceptance-traceability.md`
- `_condamad/stories/remove-historical-facade-routes/generated/06-validation-plan.md`
- `_condamad/stories/remove-historical-facade-routes/generated/10-final-evidence.md`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`

## Required searches before editing

```bash
rg -n "validate_route_removal_audit.py|validate_route_removal_audit" . -g '!artifacts/**' -g '!.codex-artifacts/**'
rg -n "validate_route_removal_audit.py" scripts backend frontend docs
rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes
```

Adapt searches to the story and repository layout.

## Likely modified files

- `_condamad/stories/remove-root-route-removal-audit-validator/removal-audit.md`
- `_condamad/stories/remove-root-route-removal-audit-validator/reference-baseline.txt`
- `_condamad/stories/remove-root-route-removal-audit-validator/reference-after.txt`
- `_condamad/stories/remove-root-route-removal-audit-validator/generated/*`
- `_condamad/stories/remove-historical-facade-routes/00-story.md`
- `_condamad/stories/remove-historical-facade-routes/generated/03-acceptance-traceability.md`
- `_condamad/stories/remove-historical-facade-routes/generated/06-validation-plan.md`
- `_condamad/stories/remove-historical-facade-routes/generated/10-final-evidence.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`

## Likely deleted files

- `scripts/validate_route_removal_audit.py`

## Forbidden or high-risk files

- Backend/frontend runtime files are forbidden unless a direct consumer is discovered.
- `scripts/stripe-listen-webhook.sh` is explicitly out of scope.
