# Sprint Change Proposal - 2026-02-20

## 1) Issue Summary

### Trigger
- Triggering context: fin de cycle implementation BMAD.
- Evidence: `sprint-status.yaml` indique 7 epics done, 29 stories done, retrospectives done.

### Core Problem Statement
- Le MVP planifie est implemente, mais il n existe pas encore de plan BMAD formalise pour la phase post-MVP (mise en production robuste, qualite operationnelle, performance et extension produit).

### Issue Type
- New requirement emerged from stakeholders (besoin de clarifier "next steps a completer" apres MVP).
- Strategic transition (from feature delivery to production hardening and scale).

## 2) Impact Analysis

### Epic Impact
- Epic 1-7: aucun rollback requis, perimetre conserve.
- Nouveau besoin: ajouter un lot post-MVP structure en nouveaux epics pour continuer dans le cadre BMAD.

### Story/Backlog Impact
- Aucune story done n est a modifier.
- Nouvelles stories a creer dans un nouveau sprint pour la phase post-MVP.

### Artifact Conflicts
- `prd.md`: pas de conflit direct; besoin d extension section "post-MVP execution plan".
- `architecture.md`: besoin de completer la strategie ops/prod (CI/CD, observabilite, SLO, resilience).
- `ux-design-specification.md`: pas de conflit MVP; extension possible pour experiences B2B/front ops.

### Technical Impact
- Renforcement non-fonctionnel prioritaire:
  - CI/CD et quality gates.
  - Monitoring + alerting + runbooks.
  - Load/concurrency tests (chat, privacy, b2b usage/billing).
  - Security hardening (secrets, pentest, conformité RGPD operationnelle).

## 3) Path Forward Evaluation

### Option 1 - Direct Adjustment
- Viable: Oui.
- Description: garder les epics 1-7 comme baseline done et ouvrir une phase post-MVP via nouveaux epics.
- Effort: Medium.
- Risk: Low/Medium.

### Option 2 - Potential Rollback
- Viable: Non.
- Description: rollback inutile, le MVP est coherent et valide.
- Effort: High.
- Risk: High.

### Option 3 - PRD MVP Review
- Viable: Partiellement.
- Description: utile pour cadrer la suite, mais sans remettre en cause le MVP livre.
- Effort: Low/Medium.
- Risk: Low.

### Recommended Approach
- Selected approach: Hybrid (Option 1 + ciblage PRD post-MVP d Option 3).
- Rationale: preserve la valeur deja livree, minimise le risque, et structure la suite sans churn technique.

## 4) Detailed Change Proposals (Incremental-ready)

### Proposal A - Add Post-MVP Epic: Production Readiness & Reliability
- Type: New epic.
- Stories candidates:
  1. CI/CD pipeline + quality gates obligatoires (lint/tests/migrations/build).
  2. Observability baseline (dashboards, alerting, error budgets, tracing request_id).
  3. Backup/restore drills + runbooks incidents.
  4. Load & concurrency benchmarks on critical APIs.
- Rationale: fiabiliser avant acceleration business.

### Proposal B - Add Post-MVP Epic: Security & Compliance Hardening
- Type: New epic.
- Stories candidates:
  1. Secrets management and rotation policy (env, vault-style process).
  2. Security test pack (SAST/deps audit + pentest checklist).
  3. RGPD operational proof workflow (export/delete/audit evidence package).
- Rationale: limiter risque legal et reputational.

### Proposal C - Add Post-MVP Epic: B2B/B2C Operational Scale
- Type: New epic.
- Stories candidates:
  1. Frontend B2B test coverage completion.
  2. Billing/usage reconciliation dashboard for ops.
  3. SLO-driven performance tuning (DB indices, cache policy, retry budgets).
- Rationale: lever les risques de passage a l echelle.

### Proposal D - Add Post-MVP Epic: Product Expansion (Business Priority Queue)
- Type: New epic.
- Stories candidates:
  1. Multi-persona astrologer refinement.
  2. Tarot/runes modules behind feature flags.
  3. Packaging/pricing experiments instrumentation.
- Rationale: transformer le MVP en croissance produit.

## 5) PRD MVP Impact and Action Plan

### MVP Impact
- MVP scope: inchange et considere complete.
- Post-MVP scope: a formaliser dans PRD addendum (execution phase 2).

### High-level Action Plan
1. Create/add post-MVP epics and stories in planning artifacts.
2. Run `sprint-planning` to regenerate sprint-status with new backlog.
3. Execute story cycle (`create-story` -> `dev-story` -> `code-review`) by priority.

## 6) Handoff Plan

### Scope Classification
- Moderate (backlog reorganization + new epics/stories, no rollback).

### Recipients & Responsibilities
- Product Owner / Scrum Master:
  - Create epics/stories post-MVP and prioritize sequence.
  - Maintain sprint-status consistency.
- Dev team:
  - Implement reliability/security/scale stories with tests and review loop.
- Architect:
  - Validate architecture deltas (ops/security/performance).

### Success Criteria
- Nouveau sprint-status contenant epics post-MVP backlog.
- Quality gates automatisees sur pipeline.
- Monitoring/alerts actifs sur parcours critiques.
- Rapports de charge et securite avec plans d action.

## 7) Checklist Execution Status

### Section 1 - Trigger and Context
- [x] 1.1 Trigger identified
- [x] 1.2 Core problem defined
- [x] 1.3 Evidence collected

### Section 2 - Epic Impact
- [x] 2.1 Current epics evaluated
- [x] 2.2 Epic-level changes identified
- [x] 2.3 Remaining epics reviewed
- [x] 2.4 New epics required
- [x] 2.5 Epic priority/order impact identified

### Section 3 - Artifact Impact
- [x] 3.1 PRD impact assessed
- [x] 3.2 Architecture impact assessed
- [x] 3.3 UX impact assessed
- [x] 3.4 Other artifacts impact assessed

### Section 4 - Path Forward
- [x] 4.1 Option 1 evaluated
- [x] 4.2 Option 2 evaluated
- [x] 4.3 Option 3 evaluated
- [x] 4.4 Recommendation selected

### Section 5 - Proposal Components
- [x] 5.1 Issue summary complete
- [x] 5.2 Impact summary complete
- [x] 5.3 Recommended path documented
- [x] 5.4 MVP impact + action plan documented
- [x] 5.5 Handoff plan documented

### Section 6 - Final Review and Handoff
- [x] 6.1 Checklist complete
- [x] 6.2 Proposal consistency verified
- [x] 6.3 Explicit user approval obtained
- [x] 6.4 sprint-status updated with approved post-MVP epics
- [x] 6.5 Next-step handoff confirmed (resume story cycle)
