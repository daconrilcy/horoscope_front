<!-- Commentaire global: candidats de suite issus de l'audit CS-347. -->

# Story Candidates

## SC-001 - Close Semantic Grounding Architecture And Reporting Map

- Candidate ID: SC-001
- Source finding: F-004
- Suggested story title: Close prompt-generation semantic grounding and audit reporting map
- Suggested archetype: prompt-generation-architecture-closure
- Primary domain: backend-domain
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: In CS-348 and CS-350, document the finite closure map that separates schema validation, semantic grounding, rejection, audit persistence, replay, and reporting proof.
- Closure intent: full-closure
- Must include: current evidence refs checks, rejection policy checks, prompt/input/audit anchors, admin/replay visibility, and explicit semantic-proof limits.
- Validation hints: reuse E-015 through E-021, plus report scans for `CS-348`, `CS-350`, `semantic gap`, `observability gap`, and `replay gap`.
- Blockers: stop if product expects a stronger semantic verifier than evidence refs and policy checks; that is not inferable from repository evidence.

## Exhaustive Files To Modify

### F-004

- Application files: none for this audit finding.
- Governance/test files: CS-348 and CS-350 story/report artifacts only.
- Audit files: `_condamad/audits/prompt-generation-cartography/**`.
- Stop condition: the architecture/report artifacts explicitly state which claims are schema-valid, evidence-ref-grounded, audit-only, replayable, or not semantically proven.
- No-wildcard allowlist: no broad folder exceptions; cite exact source/test paths.
- No Legacy checks: do not reclassify provider handoff, persisted anchors, or replay metadata as proof of prompt correctness.
- Before evidence: this audit folder and `output-validation-scan-baseline.txt`.
- After evidence: CS-348/CS-350 report scans proving the semantic limit and closure map.

## Deferred Non-Domain Context

- Frontend UI: out of scope.
- Database schema changes: out of scope.
- Provider calls: out of scope.
- Runtime validation implementation: out of scope for CS-347.
