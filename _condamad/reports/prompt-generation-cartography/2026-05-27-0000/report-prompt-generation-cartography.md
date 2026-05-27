<!-- Commentaire global: ce rapport consolide la chaine de preuve CS-343 a CS-350 pour la cartographie de generation des prompts LLM. -->

# Delivery Report - CS-343 to CS-350 Prompt Generation Cartography

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-27 |
| Repository | `C:\dev\horoscope_front` |
| Stories covered | CS-343, CS-344, CS-345, CS-346, CS-347, CS-348, CS-349, CS-350 |
| Source documents | `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md` through `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md` |
| Diff source | report-time workspace status and bounded app status guard |
| Validation source | report-time |

## 1. Executive summary

Status: `Partially delivered` for the initiative chain, because CS-343 through CS-348 are delivered and evidenced, CS-349 creates this report, but CS-350 documentation is not yet produced. The report itself is `Delivered` for CS-349 once validation-output.md records the report scans and bounded source guard.

The evidence supports a clear chain from initial briefs to audits, architecture and residual risks. It does not support a claim that final Mermaid documentation exists; that is an `Evidence gap` anchored to the absent `_condamad/docs/prompt-generation-cartography` path and CS-350 `ready-to-dev` tracker status.

## 2. Initial context and trigger

Trigger initial: `_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md` requires a single evidence-based synthesis proving `demande initiale -> briefs -> audits -> architecture -> documentation finale attendue -> validation -> risques residuels`.

The upstream demand is represented by the chained briefs CS-343 to CS-350:

- CS-343 starts the audit chain with a surface inventory of prompt-generation code, configuration, seeds, tests and CONDAMAD artifacts.
- CS-344 deepens configuration ownership: canonical use cases, assemblies, placeholders, output schemas, execution profiles, seeds and fallbacks.
- CS-345 follows runtime handoff through gateway messages and provider parameters.
- CS-346 maps natal astrological inputs and `llm_astrology_input_v1` block ownership.
- CS-347 maps output validation, rejected answers, persistence, observability and replay.
- CS-348 converts audit evidence into architecture decisions and roadmap.
- CS-350 is the expected final Mermaid documentation consumer.

Source: `evidence-sources.md`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-343 | Inventory prompt-generation surfaces and classify runtime influence. | `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md` | No application code change, no prompt rewrite. |
| CS-344 | Audit configuration, assembly, placeholders, schemas and profiles. | `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md` | No template/governance changes, no provider handoff audit. |
| CS-345 | Audit runtime gateway and provider handoff payload. | `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md` | No gateway modification, no real provider test. |
| CS-346 | Audit natal astrological inputs that feed modern prompt generation. | `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md` | No calculation, hash policy, prompt or gateway changes. |
| CS-347 | Audit post-provider validation, persistence, observability and replay. | `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md` | No schema/replay/admin UI changes, no provider calls. |
| CS-348 | Synthesize audits into product/technical architecture. | `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md` | No code changes, no Mermaid documentation. |
| CS-349 | Produce this delivery report and evidence map. | `_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md` | No app code changes, no audit or architecture rewrite. |
| CS-350 | Produce final detailed Mermaid documentation. | `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md` | Not executed by CS-349. |

## 4. Implementation summary

Audit layer:

- CS-343 delivered `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md`, which classifies active runtime, active configuration, test guard, bootstrap/seed, observability/audit, historical and debt surfaces.
- CS-344 delivered `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md`, which maps canonical use cases, assembly resolution, prompt renderer, placeholder policy, execution profiles and bounded fallback paths.
- CS-345 delivered `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md`, which identifies `messages` as the last gateway-owned payload before provider and separates structured and chat message shapes.
- CS-346 delivered `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md`, which maps `facts`, `signals`, `limits` and `shaping` as prompt-visible, with evidence/provenance/hashes excluded from prompt material.
- CS-347 delivered `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md`, which maps validation, repair, rejection, persistence, observability, replay and admin audit as post-provider concerns.

Architecture layer:

- CS-348 delivered `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md`, `source-map.md` and `validation-output.md`.
- The architecture keeps contradictions visible, especially output schema ownership split and bounded semantic grounding claims.

Report layer:

- CS-349 creates `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md`, `evidence-sources.md` and `validation-output.md`.
- CS-350 remains a downstream documentation dependency, not an implemented artifact.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-343 | Surface inventory exists and classifies relevant surfaces. | `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md` | `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | `_condamad/stories/CS-343-prompt-generation-surface-inventory/generated/10-final-evidence.md` records audit validators and targeted tests PASS. | Delivered |
| CS-344 | Configuration and fallback ownership are mapped. | `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md` | `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/final-evidence.md` records targeted tests and validators PASS. | Delivered |
| CS-345 | Provider handoff boundary is identified. | `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md` | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/final-evidence.md` records boundary tests PASS. | Delivered |
| CS-346 | Natal input blocks and prompt visibility are mapped. | `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md` | `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/final-evidence.md` records unit, architecture and long tests PASS. | Delivered |
| CS-347 | Post-provider validation, persistence and observability are mapped. | `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md` | `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/final-evidence.md` records targeted suites PASS. | Delivered |
| CS-348 | Architecture synthesis exists with blockers and roadmap. | `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md` | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/validation-output.md` records required scans PASS. | Delivered |
| CS-349 | Delivery report, source evidence and validation output exist. | `_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md` | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md`; `evidence-sources.md`; `validation-output.md` | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/validation-output.md` | Delivered |
| CS-350 | Final Mermaid documentation exists. | `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md` | Not implemented in CS-349. | `Test-Path .\_condamad\docs\prompt-generation-cartography` false; story-status row is `ready-to-dev`. | Not evidenced |

## 6. Evidence of completion

### Code evidence

- No application code evidence is expected for CS-349 because the story forbids implementation source changes.

### Test evidence

- Report-time validation is persisted in `validation-output.md`.
- Upstream story-time validation is cited from each story final evidence path in `evidence-sources.md`.

### Documentation evidence

- `evidence-sources.md`: source map with `Story`, `Artifact`, `Claim`, `Evidence path`, `Gap`, `Validation evidence` and `Next action`.
- `report-prompt-generation-cartography.md`: consolidated delivery report with required sections from the CS-349 brief.

### Operational evidence

- `validation-output.md`: command output and bounded app status guard for CS-349.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `rg -n "Evidence gap|residual risk|validation|CS-343|CS-348|CS-350" _condamad/reports/prompt-generation-cartography/2026-05-27-0000` | targeted | PASS | `validation-output.md` | Required CS-349 report scan. |
| `rg -n "report-prompt-generation-cartography" _condamad/reports/prompt-generation-cartography/2026-05-27-0000 _condamad/stories/CS-349-report-cartographie-generation-prompt-llm` | targeted | PASS | `validation-output.md` | Confirms report artifact and story evidence references. |
| Python path checks for report files | targeted | PASS | `validation-output.md` | Confirms report, source evidence and validation output exist. |
| `git status --short -- backend/app backend/tests frontend/src` | targeted | PASS | `validation-output.md` | No application source delta for CS-349. |
| `condamad_validate.py` on CS-349 capsule | targeted | PASS | `validation-output.md` | Capsule structure/evidence ready after updates. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No deviation: CS-349 creates only report and story evidence artifacts.

### Known limits

- CS-350 documentation is absent. This is an `Evidence gap`, not a CS-349 failure, because the CS-349 brief explicitly allows recording CS-350 absence as dependency evidence.
- CS-345 did not run a real provider call; the provider handoff is proven by source and local boundary tests.
- CS-346 long legacy integration guards require `--long`; that caveat is part of the validation evidence.

### Assumptions

- Upstream final evidence files are accepted as story-time validation anchors because CS-343 through CS-348 are `done` in `_condamad/stories/story-status.md`.

## 9. Risques residuels

- residual risk: output schema ownership remains split across canonical contracts, assemblies, fallback catalog, bootstrap schemas and tests. Evidence path: `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md`; `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md`.
- residual risk: persisted audit data and observability prove traceability, not semantic correctness of generated prose. Evidence path: `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md`.
- residual risk: CS-350 final documentation remains unavailable, so the developer-facing Mermaid cartography is not yet delivered. Evidence path: `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md`; absent `_condamad/docs/prompt-generation-cartography`.
- residual risk: historical/debt prompt carriers remain classified and must not be promoted to nominal paths. Evidence path: `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md`.

## 10. Evidence gaps

- Evidence gap: CS-350 documentation output does not exist under `_condamad/docs/prompt-generation-cartography`.
- Evidence gap: a real provider call is not available for CS-345; source and local handoff tests prove payload construction only.
- Evidence gap: exact post-provider semantic guardrail remains bounded and should be documented as a limitation, not a correctness guarantee.

## 11. Gaps ou contradictions

- contradiction: CS-344 and CS-348 identify output schema owner split as an unresolved blocker. The report keeps it visible instead of selecting a nominal owner.
- contradiction: audit persistence gives replayable trace evidence, while CS-347 warns it is not proof that prompt output is semantically correct.
- Gap: CS-350 is expected to consume this report, but cannot be cited as complete until its own story produces documentation.

## 12. Recommended next actions

1. Execute CS-350 to create the final Mermaid documentation under `_condamad/docs/prompt-generation-cartography`.
2. Create or prioritize a follow-up story for canonical output schema ownership, as proposed by CS-348.
3. Document bounded semantic grounding in CS-350 so audit persistence is not misread as generated-content correctness.
4. Preserve the prompt-visible versus audit-only boundary in future prompt, replay, observability and admin work.

## 13. Final delivery status

`Partially delivered`

CS-343 through CS-348 are delivered and evidenced, and CS-349 report artifacts are created. The initiative remains partially delivered because CS-350 final Mermaid documentation is intentionally out of scope for this story and absent in the repository.

