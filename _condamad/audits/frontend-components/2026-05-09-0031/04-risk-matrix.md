<!-- Matrice des risques de l'audit CONDAMAD de continuite frontend components. -->

# Risk Matrix - frontend-components

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Low | Medium | Components, feature/page owners that may later adopt exact containers | Low, because `RG-069` and exact `COMPONENT_API_IMPORT_EXCEPTIONS` block unclassified growth | None in component domain | Observe |
| F-002 | Info | Low | Component TypeScript checking | Low, because `RG-070` and zero-hit scan block reintroduction | None | Closed |
| F-003 | Info | Low | Natal interpretation component tree | Low, because `RG-071` and extracted files guard the owner split | None | Closed |
| F-004 | Info | Low | Component inventory and barrel/public exports | Low, because `RG-072` and exact usage classifications block unclassified growth | None | Closed |
| F-005 | Info | Low | Component validation suite | Low, targeted tests and lint passed | None | Closed |
