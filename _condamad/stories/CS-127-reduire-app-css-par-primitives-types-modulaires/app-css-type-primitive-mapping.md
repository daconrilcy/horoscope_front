# App CSS type primitive mapping after CS-127

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.chat-error` | class | canonical-active | TSX + CSS | `.notice.notice--error` composition where migrated | retained | existing active selector still owns legacy visual surface while primitive composition starts | low visual drift |
| `.app-state--loading` | class | canonical-active | route fallback and app states | `.state-centered` composition where centered | retained | route fallback composes primitive | low |
| `.summary-card` | class | canonical-active | dashboard cards | `.select-card` composition | retained | DashboardCard composes primitive | low |
| `.person-option` | class | canonical-active | consultation astrologer selection | `.select-card` composition | retained | AstrologerSelectStep composes primitive | low |
| `.activity-card-premium` | class | canonical-active | consultation catalogue | `.select-card` composition | retained | ConsultationsPage composes primitive | low |
| `.field__input` | class | canonical-active | shared Field input | `.form-control` composition | retained | Field input composes primitive | medium because shared UI input cascade should be reviewed |
