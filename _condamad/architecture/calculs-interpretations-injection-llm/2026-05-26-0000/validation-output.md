# Validation Output

## Source Audit Folders

Command:

```powershell
Test-Path .\_condamad\audits\calculs-interpretations-vers-llm
Test-Path .\_condamad\audits\pipeline-prompt-llm-natal
Test-Path .\_condamad\audits\projections-interpretatives-llm-input-readiness
Test-Path .\_condamad\audits\configuration-prompts-placeholders-input-schema
```

Result:

```text
True
True
True
True
```

## Required Audit IDs

Command:

```powershell
rg -n "CS-324|CS-325|CS-326|CS-327" _condamad/architecture/calculs-interpretations-injection-llm
```

Result: PASS. Matches found in `00-architecture.md`, `01-evidence-map.md`, `02-target-contract.md`, `03-legacy-transition.md`, `04-story-candidates.md` and `05-risk-register.md`.

## Target Flow Tokens

Command:

```powershell
rg -n "CalculationGraph|ChartObjectRuntimeData|ChartInterpretationInput|prompt runtime" _condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md
```

Result: PASS. Matches found in the executive summary, target flow, capability matrix, surface matrix, registries, object decisions, operational rules and validation plan.

## Required Contract Tokens

Command:

```powershell
rg -n "chart_json|natal_data|astro_context|evidence_catalog|AINarrativeInputContract" _condamad/architecture/calculs-interpretations-injection-llm
rg -n "projection_hash|llm_input_hash|evidence_refs|transition-condition" _condamad/architecture/calculs-interpretations-injection-llm
rg -n "faits structurels|Source interdite|Action recommandee|Priorite|Validation attendue" _condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000
```

Result: PASS. Required source surfaces, hash/audit tokens and matrix headings are present.

## Required Files

Command:

```powershell
.\.venv\Scripts\Activate.ps1
python -c "from pathlib import Path; root=Path('_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000'); required=['00-architecture.md','01-evidence-map.md','02-target-contract.md','03-legacy-transition.md','04-story-candidates.md','05-risk-register.md']; missing=[name for name in required if not (root/name).exists()]; assert not missing, missing; print('required architecture files: OK')"
```

Result:

```text
required architecture files: OK
```

## Application Surface Guard

Command:

```powershell
git status --short -- backend/app backend/tests frontend/src backend/migrations
```

Result: PASS. Command returned no output.

## Fresh Architecture Review - 2026-05-27

Scope reviewed:

- Story contract: `_condamad/stories/CS-328-architecture-transition-calculs-interpretations-injection-llm/00-story.md`.
- Source brief: `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`.
- Architecture output contract: `.agents/skills/condamad-product-architecture/references/output-contract.md`.
- Source audits: CS-324, CS-325, CS-326 and CS-327 under `_condamad/audits/**/2026-05-26-0000/`.

Corrections applied:

- `00-architecture.md` now includes `Target Layer Owners And Runtime Mapping`, explicitly mapping the target contract to `NatalExecutionInput` / `ExecutionContext` while preserving the no-implementation boundary.
- `03-legacy-transition.md` now records that no audit provides a calendar retirement date and therefore uses source-backed withdrawal conditions plus owner decisions.

Fresh checks executed:

```powershell
Test-Path .\_condamad\audits\calculs-interpretations-vers-llm
Test-Path .\_condamad\audits\pipeline-prompt-llm-natal
Test-Path .\_condamad\audits\projections-interpretatives-llm-input-readiness
Test-Path .\_condamad\audits\configuration-prompts-placeholders-input-schema
rg -n "CS-324|CS-325|CS-326|CS-327" _condamad\architecture\calculs-interpretations-injection-llm\2026-05-26-0000
rg -n "CalculationGraph|ChartObjectRuntimeData|ChartInterpretationInput|prompt runtime|NatalExecutionInput|ExecutionContext" _condamad\architecture\calculs-interpretations-injection-llm\2026-05-26-0000\00-architecture.md
rg -n "chart_json|natal_data|astro_context|evidence_catalog|AINarrativeInputContract|projection_hash|llm_input_hash|evidence_refs|transition-condition" _condamad\architecture\calculs-interpretations-injection-llm\2026-05-26-0000
rg -n "faits structurels|Source interdite|Action recommandee|Priorite|Validation attendue|Calendar date|Withdrawal condition|not sourced" _condamad\architecture\calculs-interpretations-injection-llm\2026-05-26-0000
.\.venv\Scripts\Activate.ps1; python -c "from pathlib import Path; root=Path('_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000'); required=['00-architecture.md','01-evidence-map.md','02-target-contract.md','03-legacy-transition.md','04-story-candidates.md','05-risk-register.md']; missing=[name for name in required if not (root/name).exists()]; assert not missing, missing; print('required architecture files: OK')"
git status --short -- backend/app backend/tests frontend/src backend/migrations
```

Result: PASS.

- The four required audit folders exist.
- All required audit IDs, target-flow primitives, legacy surfaces, target contract tokens, hash/audit tokens and mandatory matrix headings are present.
- The six required architecture files exist.
- The report now covers all seven mandatory questions from the source brief and story, including the `NatalExecutionInput` / `ExecutionContext` mapping and condition-based legacy retirement posture.
- `backend/app`, `backend/tests`, `frontend/src` and `backend/migrations` remain unchanged.
