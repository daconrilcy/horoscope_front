# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The main documentation file exists. | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` created. | `validation.txt` VC1 path check PASS; `docs-after.txt` records the file. | PASS |
| AC2 | The document includes every mandatory brief heading. | Main document contains the 19 required `##` sections from the brief. | `validation.txt` VC2 heading assertion PASS. | PASS |
| AC3 | At least six Mermaid diagrams are fenced. | Main document includes six fenced Mermaid diagrams: global, config, input, projection, provider, validation/audit. | `validation.txt` VC2 `text.count('```mermaid') >= 6` PASS and VC3 scan PASS. | PASS |
| AC4 | The prompt-visible boundary is explicit. | Section `Projection prompt-visible vs backend-only` separates prompt-visible, runtime-only, validation-only and audit-only surfaces. | `validation.txt` VC3 scan for `prompt-visible` and `backend-only` PASS. | PASS |
| AC5 | Source symbols are cited. | Document cites `LLMGateway`, `PromptRenderer`, `assemble_developer_prompt` and required backend paths; `source-coverage.md` maps all required sources. | `validation.txt` VC3 symbol scan PASS. | PASS |
| AC6 | Non-nominal paths are separated. | Sections for repair, fallback, rejection, degraded payloads, seeds/bootstrap and non-nominal paths are separated from nominal flow. | `validation.txt` VC4 scan for `nominal`, `fallback`, `repair`, `rejet`, `degrade` PASS. | PASS |
| AC7 | Guardrails are cited. | `Tests et guardrails` cites backend guard tests and `_condamad/stories/regression-guardrails.md` RG-002/RG-042 context. | `guardrails.txt` resolver scan persisted; `validation.txt` VC4 `guardrails` scan PASS. | PASS |
| AC8 | Gaps are marked without invented facts. | `Risques residuels et open questions` keeps output schema split, bounded semantic grounding, observability/replay limits and long-test caveat visible. | `source-coverage.md` records no missing mandatory artifact and known source-backed blockers. | PASS |
| AC9 | A developer can follow the natal prompt flow. | Main document traces natal flow from service/builders to `llm_astrology_input_v1`, gateway projection, messages, validation and audit. | `validation.txt` VC3/VC4 scans PASS; pytest regression PASS. | PASS |
| AC10 | Persistent evidence artifacts are stored. | `evidence/guardrails.txt`, `docs-baseline.txt`, `docs-after.txt`, `source-coverage.md`, `validation.txt`, `final-evidence.md` created. | `validation.txt` VC6 evidence path check PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
