# CS-395 Final Evidence

Status: done with local QA blocker (fix review 2026-05-30).

## AC validation
| AC | Status | Evidence |
|---|---|---|
| AC1 frontière backend | PASS | `test_narrative_natal_reading_public_boundary.py` |
| AC2 garde DOM | PASS | `natalPublicDomGuard.test.tsx` |
| AC3 historique Alembic | PASS | révision no-op et garde `DELETE FROM` |
| AC4 registre RG | PASS | RG-152, RG-153, RG-154 |
| AC5 QA responsive documentée | PASS | rapport CS-395 |

## Commands
```text
pytest -q tests -> 1263 passed, 1 skipped, 241 deselected
pnpm --dir frontend test -- NatalChartPage natalInterpretation natalInterpretationEvidence NatalAstrologerMode natalNarrativeReading natalPublicDomGuard -> 113 passed
pnpm --dir frontend lint -> PASS
pnpm --dir frontend build -> PASS
Invoke-WebRequest http://127.0.0.1:8001/health -> 200
Invoke-WebRequest http://127.0.0.1:5173/login -> 200
```

## Local QA blocker
- Le navigateur MCP est indisponible: `windows sandbox failed: spawn setup refresh`.
- Le fallback Playwright atteint `/login`, puis le compte de test documenté répond `Invalid credentials`.
- Captures disponibles: `output/playwright/cs-395-natal-initial.png` et `output/playwright/cs-395-login-result.png`.
