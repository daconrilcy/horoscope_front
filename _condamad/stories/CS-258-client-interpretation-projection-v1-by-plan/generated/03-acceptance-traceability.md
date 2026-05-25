# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `client_interpretation_projection_v1` is documented. | `docs/architecture/client-interpretation-projection-v1-contract.md`; registry row in `docs/architecture/official-product-primitives-public-projections.md`. | `python -B -c` path check PASS; `rg` targeted contract scan PASS. | PASS |
| AC2 | Plan sections are explicit. | Contract section "Matrice des sections par plan" defines `free`, `basic`, `premium` section sets. | `rg -n "client_interpretation_projection_v1\|free\|basic\|premium"` PASS. | PASS |
| AC3 | Narrative depth rules are explicit. | Contract section "Profondeur narrative" defines `section_count`, `personalization_depth`, `predictions_depth`, `explanatory_richness`. | `rg` targeted depth scan PASS. | PASS |
| AC4 | Client support elements are vulgarized. | Contract section "Elements d'appui vulgarises" defines highlights, confidence wording, source labels, display hints and personalization notes as client-readable support elements. | `rg` targeted support-elements scan PASS. | PASS |
| AC5 | Technical payload exposure is forbidden. | Contract section "Exclusions techniques client" forbids runtime technique brut, proof internals, prompt internals, provider internals, audit internals and raw factual dumps. | `rg` targeted forbidden-symbol wording scan PASS; `git status --short -- backend/app frontend/src` shows no application source drift. | PASS |
| AC6 | Source linkage is explicit. | Contract links `structured_facts_v1`, `beginner_summary_v1`, `AINarrativeInterpretiveSignals` and LLM `rédacteur` role. | Targeted `rg` scan PASS; existing AI narrative unit and architecture tests PASS. | PASS |
| AC7 | Expert projection remains out of scope. | Contract excludes `expert_technical_projection_v1`, champs expert, admin roles and diagnostics administrateur. | `rg -n "expert_technical_projection_v1\|provider implementation\|definitive prompt\|admin roles"` PASS. | PASS |
| AC8 | Public API surface stays unchanged. | No backend route, serializer or OpenAPI code was changed. | `python -B -c "from app.main import app; assert 'client_interpretation_projection_v1' not in str(app.openapi())"` PASS; route assertion PASS. | PASS |
| AC9 | Application source surfaces remain unchanged. | No `backend/app` or `frontend/src` files modified. | `git status --short -- backend/app frontend/src` returned no entries. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/validation.txt`, `evidence/app-surface-status.txt`, this traceability file and `generated/10-final-evidence.md`. | `condamad_validate.py` PASS after capsule generation; final evidence updated. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
