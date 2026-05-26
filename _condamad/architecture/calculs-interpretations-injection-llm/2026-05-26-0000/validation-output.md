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
