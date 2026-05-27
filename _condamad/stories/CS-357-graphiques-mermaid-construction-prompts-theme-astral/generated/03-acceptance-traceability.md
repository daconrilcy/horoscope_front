# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Mermaid diagram document exists. | `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md` created. | `python -B -c` path check PASS. | PASS |
| AC2 | At least seven Mermaid diagrams are present. | Document contains 8 Mermaid blocks. | `python -B -c` counted `mermaid_blocks 8`. | PASS |
| AC3 | The three plans are covered. | `free`, `basic`, `premium` shown in plan diagram and notes. | `rg -n "free\|basic\|premium"` PASS. | PASS |
| AC4 | Global pipeline is diagrammed. | `Pipeline global theme astral` covers birth data, input, assembly, messages and no-call boundary. | Combined `rg` for `birth data`, `input`, `assembly`, `messages` PASS. | PASS |
| AC5 | Injected data construction is diagrammed. | `Construction des donnees injectees` shows `facts`, `signals`, `limits`, `shaping`. | Combined `rg` for those four blocks PASS. | PASS |
| AC6 | Persona is drawn separately. | `Introduction astrologue/persona` separates persona from `developer prompt` and cites owners. | Combined `rg` for `persona`, `developer prompt`, `assembly_resolver.py`, `gateway.py` PASS. | PASS |
| AC7 | Safety controls are drawn. | `Securite et non-invention` separates hard policy, non-invention, validation, repair, rejection. | Combined `rg` for safety terms PASS. | PASS |
| AC8 | Provider message order is exact. | `Messages finaux provider` lists `system_core`, `developer prompt`, optional persona, `payload user`. | Combined `rg` for ordered message labels PASS. | PASS |
| AC9 | Prompt exclusions are visible. | Boundary diagram classifies hashes, `provider_response`, `chart_json`, `natal_data`, observability outside prompt-visible. | Combined `rg` for exclusions and carriers PASS. | PASS |
| AC10 | No provider call is represented. | Intro and final diagram state the stop boundary before provider. | `rg -n "no provider call"` PASS. | PASS |
| AC11 | CS-356 integration is explicit. | `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` cites the Mermaid annex. | `rg -n "natal-prompt-construction-mermaid.md"` PASS. | PASS |
| AC12 | Application code remains unchanged. | No edits under `backend/app`, `backend/tests`, or `frontend/src`. | `git status --short -- backend/app backend/tests frontend/src` returned no entries. | PASS |
| AC13 | Persistent evidence is stored. | `evidence/docs-baseline.txt`, `docs-after.txt`, `guardrails.txt`, `validation.md` stored. | Path checks and final evidence update PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
