<!-- Commentaire global: matrice de risque pour l'audit de cloture documentaire CS-355. -->

# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Future documentation agents and prompt-boundary stories | High: audit evidence can be mistaken for prompt material or unrelated validation data | Low | P1 |
| F-002 | High | High | Provider metadata, privacy and runtime-boundary reasoning | High: provider-visible headers can be mislabeled as backend-only memory | Low | P1 |
| F-003 | High | High | Prompt-generation architecture, docs and future LLM flow changes | High: non-natal provider-capable flows can be collapsed into the nominal natal carrier | Medium | P1 |
| F-004 | Medium | Medium | Product and architecture ownership for legacy/debt guidance path | Medium: `event_guidance` can be promoted or ignored without owner decision | Medium | P2 |
| F-005 | Medium | Medium | Admin LLM execution policy and sample-payload boundaries | Medium: admin provider-capable execution can be hidden by public-runtime wording | Medium | P2 |
| F-006 | Medium | Medium | Documentation governance and future CONDAMAD stories | Medium: accepted classifications can drift after correction if unguarded | Low | P3 |

## Top Risks

- The current final document cannot be validated as final because required CS-351/CS-352 wording corrections are still absent.
- The current final document cannot be validated as complete because CS-353/CS-354 process classifications are not reflected in CS-350.
- Two owner decisions remain unresolved: `event_guidance` debt status and admin manual execution policy.

## Review Limitation

This closure audit did not modify CS-350 and did not re-run all backend tests from CS-351 to CS-353. It relies on the current source artifacts plus targeted reproducible scans proving the required corrections are absent.
