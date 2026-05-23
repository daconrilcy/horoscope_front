# Executive Summary - Astro Calculation Interpretation Boundary

## Decision Summary

The backend currently has a solid structural/interpretive split: calculation nodes produce facts, astrology interpretation contracts build pre-narrative inputs, LLM runtime owns prompt/message execution, and product prediction surfaces own final narrative projection.

The audited domain is not fully closed. The remaining risks are governance and guardrail gaps, not evidence of calculators actively generating final text.

## Findings By Severity

- High: 1 finding. F-001 requires an explicit `ChartInterpretationInput` internal/public/LLM contract split.
- Medium: 2 findings. F-002 needs a compact interpretation-readiness projection; F-003 needs lexical narrative-token guards for structural runtime.
- Low: 1 finding. F-004 notes old docs still reference removed historical namespaces.

## Recommended Next Action

Prioritize CS-252 first. It decides the contract boundary that CS-253 and CS-254 should protect. Then implement CS-253 for readiness projection and CS-254 for guard hardening.

## Validation Focus

- Prove `ChartInterpretationInputRuntimeData` is not exposed raw as a public API.
- Prove readiness projection contains no LLM/provider dependency.
- Prove structural runtime roots reject both interpretive identifiers and final-user narrative phrases.
- Keep all prompt, projection and public contract changes out of calculators.
