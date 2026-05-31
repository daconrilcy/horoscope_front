# Traceability AC - CS-405

| AC | Requirement | Status | Evidence code/artefact | Validation |
|---|---|---|---|---|
| AC1 | The old live report is updated. | PASS | `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`; `evidence/cs-390-395-report-before.md`; `evidence/cs-390-395-report-after.md` | Baseline avant/apres conservee. |
| AC2 | The CS-400 closure report exists. | PASS | `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` | Rapport CS-400/CS-405 existe et contient le verdict actualise. |
| AC3 | Free QA is documented. | BLOCKED | `evidence/api-snapshot.json`; rapport CS-400/CS-405 | Le compte local est `basic`; preuve Free authentifiee non disponible dans cette session. |
| AC4 | Basic QA proves five chapters. | FAIL | `evidence/api-complete-generation-response.json`; `output/playwright/cs-400-basic-*.png` | Generation Basic `complete` HTTP OK mais `narrative_natal_reading_v1 = null`, sections = 0. |
| AC5 | Premium QA preserves astrologer mode. | BLOCKED | `evidence/frontend-targeted-tests.txt`; rapport CS-400/CS-405 | Vitest `NatalAstrologerMode` PASS, mais QA live Premium non rejouee apres blocage Basic. |
| AC6 | Viewport matrices are documented. | FAIL | `output/playwright/cs-400-basic-desktop.png`; `output/playwright/cs-400-basic-mobile.png` | Matrices desktop/mobile documentees, mais les deux captures prouvent `accordionCount = 0`. |
| AC7 | Modern accordions are verified. | FAIL | `evidence/frontend-targeted-tests.txt`; `evidence/browser-qa-basic.json` | Vitest accordions PASS; live Basic ne rend aucun accordion narratif. |
| AC8 | Public sources are non-empty. | FAIL | `evidence/api-complete-generation-response.json`; `evidence/backend-targeted-tests.txt` | Tests unitaires PASS, mais live Basic n'expose aucune source narrative. |
| AC9 | Basic remediation is verified. | FAIL | `evidence/backend-long-entitlement.txt`; `evidence/api-complete-generation-response.json` | Entitlement long PASS automatise, mais regeneration Basic live ne produit pas la narrative attendue. |
| AC10 | Rejection preserves quota. | PASS_WITH_LIMITATIONS | `evidence/backend-targeted-tests.txt`; `evidence/backend-long-entitlement.txt` | Rejet/quota PASS par tests; non rejoue en browser live. |
| AC11 | Basic coverage metrics are verified. | PASS_WITH_LIMITATIONS | `evidence/backend-targeted-tests.txt` | Couverture Basic PASS par tests; non confirmee en live a cause du payload V2. |
| AC12 | RG-155 to RG-158 evidence is listed. | PASS_WITH_LIMITATIONS | Rapport CS-400/CS-405 section Guardrails; scans cibles executes | RG-155 a RG-158 cites; RG-155/RG-158 restent en echec live. |
| AC13 | Screenshot evidence is persisted. | PASS_WITH_LIMITATIONS | `output/playwright/cs-400-basic-desktop.png`; `output/playwright/cs-400-basic-mobile.png` | Captures persistees pour Basic desktop/mobile; Free/Premium non capturees. |
| AC14 | No critical residual risk is hidden. | PASS | Rapport CS-400/CS-405 section Risques residuels | Risques critique/majeur explicites avec suivi CS-406/CS-407/CS-408. |

## Decision

Implementation closure status: `BLOCKED`. La story reste dans la file de developpement du registre car les AC live ne sont pas satisfaits et les stories de correction runtime suivantes sont deja planifiees.
