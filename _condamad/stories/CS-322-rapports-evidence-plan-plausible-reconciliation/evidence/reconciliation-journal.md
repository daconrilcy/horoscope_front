# CS-322 Reconciliation Journal

<!-- Commentaire global: ce journal relie chaque artefact reconcilié aux décisions CS-320 et CS-321 sans modifier le runtime applicatif. -->

## Source Decisions

| Decision | Current source | Applied rule |
|---|---|---|
| Plan availability | `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` | `client_interpretation_projection_v1` remains available for `free`, `basic` and `premium`. |
| Commercial differentiation | `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` | Differentiation is routed to LLM inputs, editorial depth and frontend sections. |
| Analytics provider | `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` | Plausible is the preparation target; Matomo is not currently used. |
| Matomo removal | CS-323 story track | Matomo code removal is routed separately and is not implemented in CS-322. |

## Artifact Reconciliation Ledger

| artifact_path | decision_topic | before_term | after_term | evidence_command | runtime_surface |
|---|---|---|---|---|---|
| `_condamad/reports/CS-312-CS-316-delivery-report.md` | plan-availability | `Delivered with routed backend follow-up`; backend/product mismatch; premium-only expectation | Delivered repository evidence; all plans remain aligned for `client_interpretation_projection_v1`; CS-320 owns LLM/front differentiation | `rg -n "CS-320\|client_interpretation_projection_v1\|free\|basic\|premium" _condamad/reports/CS-312-CS-316-delivery-report.md` | unchanged |
| `_condamad/reports/CS-312-CS-316-delivery-report.md` | analytics-provider | `Plausible/Matomo` shared external sink | Plausible external observation required; Matomo not currently used and routed to CS-323 | `rg -n "Plausible\|Matomo\|CS-321\|CS-323" _condamad/reports/CS-312-CS-316-delivery-report.md` | unchanged |
| `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md` | closure-status | Backend/product divergence remains open against premium-only visibility | No backend entitlement divergence remains; CS-320 owns LLM/front differentiation | `rg -n "CS-320\|backend entitlement divergence\|client_interpretation_projection_v1" _condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md` | unchanged |
| `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` | analytics-provider | External Plausible/Matomo dashboard observation | External Plausible observation remains blocked without provider environment; Matomo removal routed separately | `rg -n "Plausible\|Matomo" _condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` | unchanged |

## Stale Wording Scan Results

- Before scan: `evidence/stale-wording-before.txt`.
- After scan: `evidence/stale-wording-after.txt`.
- The only remaining matches in the unfiltered source scan are in `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md`, which is the immutable source brief and intentionally lists stale terms as context.
- The active-target scan excluding the immutable CS-322 source brief has no stale contradiction match.

## Provider Wording Scan Results

- `_condamad/reports/CS-312-CS-316-delivery-report.md` now names Plausible observation and routes Matomo code removal to CS-323.
- CS-318 final evidence now says Plausible is the observable provider target and Matomo is not currently used.

## No-Runtime-Change Proof

- Backend, frontend and shared runtime directories are out of scope.
- Runtime diff proof is recorded in `evidence/runtime-diff.txt`.
- No backend, frontend, shared, migration, package, build, provider runtime, or test source file was edited by CS-322.
