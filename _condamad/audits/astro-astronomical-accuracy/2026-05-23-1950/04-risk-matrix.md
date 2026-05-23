# Risk Matrix - Astro Astronomical Accuracy

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Production natal calculation mode and accurate public flows | High: simplified path can remain silently selectable if guards are weak | Medium | P1 |
| F-002 | High | High | Astronomical golden baseline and sensitive temporal/house cases | High: regressions in DST, high latitude or house-system outputs can pass current contracts | Medium | P1 |
| F-003 | Medium | Medium | Ephemeris metadata and chart trace reproducibility | Medium: dataset drift can be hard to diagnose after persistence | Medium | P2 |
| F-004 | Medium | Medium | Sidereal, topocentric, whole sign and Placidus edge modes | Medium: option propagation can pass without reference accuracy proof | Medium | P2 |
| F-005 | Low | Medium | Future story guardrails and evidence vocabulary | Low: adjacent guards exist but are not exact | Low | P3 |

## Astronomical Versus Architecture Risk Separation

- Astronomical precision risks: F-002 and F-004.
- Reproducibility and trace risks: F-003.
- Architecture and mode-routing risks: F-001 and F-005.
