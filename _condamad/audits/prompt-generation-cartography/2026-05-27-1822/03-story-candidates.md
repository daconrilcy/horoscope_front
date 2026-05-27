<!-- Commentaire global: propositions de stories issues de l'audit CS-345 du handoff runtime provider LLM. -->

# Story Candidates - prompt-generation-cartography - 2026-05-27-1822

No implementation story candidate is emitted by this audit.

## Exhaustive Files To Modify

| Finding | Application files | Governance or test files | Deferred non-domain context | Stop condition |
|---|---|---|---|---|
| F-001 | none | none | CS-348 to CS-350 may consume this audit as source material. | Runtime handoff report exists and validation passes. |
| F-002 | none | none | CS-346 owns production of `llm_astrology_input_v1`; CS-347 owns output validation and persistence audit. | Existing boundary tests remain green. |
| F-003 | none | none | Any behavioral recovery change belongs to CS-347 or a later implementation story. | Repair and fallback remain classified as non nominal. |
| F-004 | none | none | Registry enrichment would require a separate authorized guardrail story. | Registry gap is recorded without editing guardrails. |

## Deferred Non-Domain Context

- CS-346: production/source completeness of `llm_astrology_input_v1`.
- CS-347: output validation, repair persistence and observability completeness.
- CS-348 to CS-350: architecture/report/documentation synthesis from the cartography series.

