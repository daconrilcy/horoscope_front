# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `beginner_summary_v1` is documented. | `docs/architecture/beginner-summary-v1-contract.md` created as the canonical contract. | `python -B -c "from pathlib import Path; assert Path('docs/architecture/beginner-summary-v1-contract.md').exists()"` PASS. | PASS |
| AC2 | Authorized client fields are explicit. | Contract lists signes principaux, ascendant, maison dominante and thèmes dominants in `allowed_fields`. | `rg -n "signes principaux|ascendant|maison dominante|thèmes dominants" docs/architecture/beginner-summary-v1-contract.md` PASS. | PASS |
| AC3 | Client states are deterministic. | Contract defines exclusive `loading`, `empty`, `degraded`, `unavailable` states with trigger rules. | `rg -n "loading|empty|degraded|unavailable|trigger" docs/architecture/beginner-summary-v1-contract.md` PASS. | PASS |
| AC4 | Missing birth time behavior is explicit. | Contract documents `no_time`, withheld ascendant, withheld maison dominante and house-dependent withholding. | `rg -n "heure de naissance|ascendant|house-dependent|degraded_reason" docs/architecture/beginner-summary-v1-contract.md` PASS. | PASS |
| AC5 | `structured_facts_v1` source linkage is explicit. | Contract names `structured_facts_v1` as the upstream factual source and rejects direct public payload semantics. | `rg -n "structured_facts_v1|upstream factual source|direct public payload" docs/architecture/beginner-summary-v1-contract.md` PASS. | PASS |
| AC6 | Technical payload exposure is forbidden. | Contract excludes full facts, raw runtime, debug, audit, traceback, prompt and internal payloads. | `rg -n "controlled error|raw runtime|debug|audit|premium" docs/architecture/beginner-summary-v1-contract.md` PASS. | PASS |
| AC7 | Free/basic compatibility is explicit. | Contract role and registry row state B2C, free/basic and premium exclusion. | `rg -n "beginner_summary_v1|B2C|free|basic" docs/architecture/beginner-summary-v1-contract.md` PASS; registry scan PASS. | PASS |
| AC8 | Public API surface stays unchanged. | No backend API route, OpenAPI schema, frontend client or runtime builder was added. | `PYTHONPATH=backend python -B -c "from app.main import app; assert 'beginner_summary_v1' not in str(app.openapi())"` PASS; route check PASS. | PASS |
| AC9 | Application source surfaces remain unchanged. | No changes under `backend/app`, `frontend/src`, `backend/tests` or `backend/migrations`. | `git status --short -- backend/app frontend/src backend/tests backend/migrations` PASS with no output. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/validation.txt`, `evidence/app-surface-status.txt`, `evidence/source-checklist.md`, generated traceability and final evidence updated. | `python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/validation.txt').exists()"` PASS after artifact creation. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
