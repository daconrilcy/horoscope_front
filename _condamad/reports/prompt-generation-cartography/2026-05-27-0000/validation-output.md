<!-- Commentaire global: ce fichier persiste les validations executees pour le rapport CS-349. -->

# Validation Output - CS-349

## Commandes executees

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `rg -n "Evidence gap\|residual risk\|validation\|CS-343\|CS-348\|CS-350" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Report folder contains required IDs, validation terms, evidence gaps and residual risks. |
| `rg -n "CS-343\|CS-348\|CS-350" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Story map covers source audit, architecture and downstream documentation dependency. |
| `rg -n "Evidence path\|Source\|Evidence gap" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Source evidence matrix contains anchors and explicit missing-proof labels. |
| `rg -n "Evidence gap" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Missing CS-350 documentation and bounded semantic/provider evidence are labeled. |
| `rg -n "contradiction\|Gaps" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Output schema ownership and audit-correctness contradiction are visible. |
| `rg -n "Validation evidence\|validation" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Report and evidence source files include validation anchors. |
| `rg -n "residual risk\|Risques residuels" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000` | `C:\dev\horoscope_front` | PASS | Residual risks are present in the final report. |
| `rg -n "report-prompt-generation-cartography" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000 .\_condamad\stories\CS-349-report-cartographie-generation-prompt-llm` | `C:\dev\horoscope_front` | PASS | Report artifact is referenced by report folder and story contract. |
| `.\.venv\Scripts\Activate.ps1; python -B -c "from pathlib import Path; paths=[Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md'),Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/evidence-sources.md'),Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/validation-output.md')]; missing=[str(p) for p in paths if not p.is_file()]; print('PASS' if not missing else 'FAIL '+repr(missing))"` | `C:\dev\horoscope_front` | PASS | Required report, source evidence and validation output files exist. |
| `git status --short -- backend/app backend/tests frontend/src` | `C:\dev\horoscope_front` | PASS | No entries; application source, backend tests and frontend source remain unchanged. |
| `.\.venv\Scripts\Activate.ps1; python -B .\.agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-349-report-cartographie-generation-prompt-llm` | `C:\dev\horoscope_front` | PASS | CONDAMAD capsule validation passed after evidence updates. |
| `rg -n "\| CS-349 \|" .\_condamad\stories\story-status.md` | `C:\dev\horoscope_front` | PASS | Story registry row is `ready-to-review` with the expected story and brief paths. |
| `git diff --check -- .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000 .\_condamad\stories\CS-349-report-cartographie-generation-prompt-llm .\_condamad\stories\story-status.md` | `C:\dev\horoscope_front` | PASS | No whitespace errors reported; Git warned that `story-status.md` line endings may be normalized on future Git touch. |

## Commandes non lancees

- `ruff check .`: SKIPPED. CS-349 is report-only and changed no Python application files; targeted report scans and capsule validation cover this story scope.
- `python -B -m pytest -q --tb=short`: SKIPPED. No runtime, backend test, frontend or migration code changed; upstream story-time tests are cited in `evidence-sources.md`.
