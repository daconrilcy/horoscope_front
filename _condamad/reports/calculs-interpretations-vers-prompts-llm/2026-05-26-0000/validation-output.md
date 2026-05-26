# Validation Output

<!-- Commentaire global: ce fichier conserve les commandes de validation executees pour CS-329. -->

## Commands run

| Command | Result | Evidence summary |
|---|---|---|
| `Test-Path .\_condamad\reports\calculs-interpretations-vers-prompts-llm` | PASS | Returned `True`. |
| `python -c "... assert root.exists() ..."` | PASS | Returned `report root: OK`. |
| `python -c "... rapport-transition-injection-prompts-llm.md ..."` | PASS | Returned `report file: OK`. |
| `rg -n "CS-324|CS-325|CS-326|CS-327|CS-328" _condamad\reports\calculs-interpretations-vers-prompts-llm` | PASS | All five source IDs found in report/evidence files. |
| `rg -n "legacy|recent-refonte|contrat cible|chart_json|structured_facts_v1" _condamad\reports\calculs-interpretations-vers-prompts-llm` | PASS | Current, legacy and target vocabulary found. |
| `rg -n "AINarrativeInput|NatalExecutionInput|ExecutionContext|Stories de refactor recommandees" _condamad\reports\calculs-interpretations-vers-prompts-llm` | PASS | Target contract and required story section found. |
| `rg -n "Executive summary|Etat actuel de l'injection LLM|Annexes de preuves|..." rapport-transition-injection-prompts-llm.md` | PASS | All twelve mandatory section headings found. |
| `python -c "... evidence-sources.md ... validation-output.md ..."` | PASS | Returned `evidence files: OK`. |
| `git status --short -- backend/app backend/tests frontend/src backend/migrations` | PASS | Returned no output; no application surface changed. |
| `git status --short -- _condamad _story_briefs backend/app backend/tests` | PASS | Returned CS-329 report artifacts and existing `_condamad/run-state.json`; no app/test changes. |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ...\00-story.md` | PASS | `CONDAMAD story validation: PASS`. |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ...\00-story.md` | PASS | `CONDAMAD story lint: PASS`. |
| `git diff --check -- _condamad\reports\calculs-interpretations-vers-prompts-llm ...` | PASS | Exit 0; Git emitted existing LF-to-CRLF working-copy warnings only. |
| `Select-String -Path _condamad\stories\story-status.md -Pattern 'CS-329'` | PASS | CS-329 row shows `done` and date `2026-05-27`. |

All Python commands above were executed after activating `.\.venv\Scripts\Activate.ps1`.

## Commands skipped

| Command | Reason | Risk | Compensating evidence |
|---|---|---|---|
| Full backend pytest / ruff suite | CS-329 is report-only and no backend code or backend tests changed. | Low: application behavior is not exercised. | No-app-change guard returned no output. |
| Frontend lint/tests | No frontend file changed. | Low: frontend behavior is outside scope. | No-app-change guard returned no output for `frontend/src`. |
| Local app startup | No application runtime change was made. | Low: report artifacts do not affect startup. | No-app-change guard plus report content validations. |

## Residual validation note

The tracker rows for CS-324 to CS-328 still show `ready-to-dev`, but their deliverable folders exist and were used as the
source of truth for this report. This is recorded as a governance mismatch, not an implementation blocker for CS-329.
