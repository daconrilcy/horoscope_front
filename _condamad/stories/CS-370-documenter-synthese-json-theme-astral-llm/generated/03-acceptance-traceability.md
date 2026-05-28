# Acceptance Traceability

<!-- Commentaire global: cette trace relie chaque critere CS-370 au document cree et aux validations persistantes. -->

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The synthesis document exists. | `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` created. | VC1 in `evidence/validation.txt`; `docs-baseline.txt` and `docs-after.txt`. | PASS |
| AC2 | All mandatory sections are present. | Target document contains the ten required sections from `00-story.md`. | VC2 heading check in `evidence/validation.txt`. | PASS |
| AC3 | The canonical skeleton is documented. | JSON skeleton documents `runtime_contract`, `safety_contract`, `astrologer_voice`, `feature_context`, `delivery_profile`, `input_data.*`, and `output_contract`. | VC3/VC4 skeleton scans in `evidence/validation.txt`. | PASS |
| AC4 | Every block has source evidence. | `Description des blocs` table includes source column for every canonical block. | VC5 table parser in `evidence/validation.txt`. | PASS |
| AC5 | Delivery profile variation is explained. | `Variations par delivery profile` explains backend resolution and allowed variation axes. | VC6 `delivery_profile`/backend resolution scan in `evidence/validation.txt`. | PASS |
| AC6 | Commercial plan labels stay backend-only. | Boundary and variation sections state commercial inputs remain backend-only and are not LLM payload data. | VC7 forbidden plan-label scan in `evidence/validation.txt`. | PASS |
| AC7 | Interpretation material provenance is explicit. | Source-traceable backend row and block table cite table-backed/runtime-owned material owners. | VC8 provenance scan in `evidence/validation.txt`. | PASS |
| AC8 | Astrologer voice is style-only. | Principles, block table, diagram and checklist limit voice to style, tone, emphases and lexicon. | VC9 voice-boundary scan in `evidence/validation.txt`. | PASS |
| AC9 | Two Mermaid diagrams are present. | `Diagrammes Mermaid` contains construction and boundary diagrams. | VC10 Mermaid parser in `evidence/validation.txt`. | PASS |
| AC10 | CS-371 example ownership is linked. | Final section names CS-371 as owner of complete profile examples and avoids generating them. | VC11 CS-371 scan in `evidence/validation.txt`. | PASS |
| AC11 | Application code remains unchanged. | No edits to `backend/app`, `backend/tests`, or `frontend/src`. | VC12 bounded git status checks in `evidence/validation.txt`. | PASS |
| AC12 | Persistent evidence is stored. | `evidence/source-coverage.md`, `guardrails.txt`, `docs-baseline.txt`, `docs-after.txt`, `validation.txt`; generated trace/final evidence. | VC13 evidence path checks and capsule validation in `evidence/validation.txt`. | PASS |
| AC13 | Every block has a visibility rule. | `Description des blocs` table includes visibility column for every canonical block. | VC5 table parser in `evidence/validation.txt`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
