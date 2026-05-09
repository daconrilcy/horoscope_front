<!-- Matrice de risque du re-audit App.css apres CS-121 a CS-124. -->

# Risk Matrix - frontend-app-css-standardization

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | `frontend/src/App.css` and App class consumers | High: new prefixes can grow without failing guards | Medium | P1 |
| F-002 | Medium | Medium | `precision/evidence` App visual families | Medium: residual family can expand outside SC-003 closure | Low | P2 |
