<!-- Commentaire global: matrice de risques pour l'audit CS-352 de concordance code-document prompt LLM. -->

# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | Documentation agents and future prompt-boundary stories | Medium: wording can reclassify audit evidence as prompt material if copied into future stories | Low | P2 |
| F-002 | Low | Medium | Documentation and provider-boundary reasoning | Low: runtime code is correct, but wording can mislead security/privacy analysis | Low | P3 |
| F-003 | Info | Medium | Documentation governance only | Low: executable boundary tests still cover runtime behavior | Medium | P4 |

## Top Risks

- The highest risk is not runtime behavior; it is future story drift caused by ambiguous documentation wording.
- The provider metadata wording deserves correction before a security or provider privacy audit consumes the cartography as a source of truth.
- The absence of an exact code-document concordance guardrail is acceptable for this audit but should remain visible.

## Review Limitation

- The CS-352 persistent evidence baseline was absent at review start and was reconstructed during review. This is now documented in E-014, E-015 and the story evidence folder; it does not change the runtime concordance findings, but it remains a delivery-process limitation for AC10 traceability.
