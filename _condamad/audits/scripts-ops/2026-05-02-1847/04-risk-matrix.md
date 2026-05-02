# Risk Matrix - scripts-ops

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | scripts root / CONDAMAD story tooling | Medium | Low | P1 |
| F-002 | Medium | Medium | Stripe local dev docs/tests | Medium | Low | P2 / needs-user-decision |
| F-003 | Medium | High | all root scripts | High | Medium | P2 |
| F-004 | Medium | Medium | local dev startup | Medium | Low | P2 |
| F-005 | Medium | High | load/perf campaigns | Medium | Medium | P2 |
| F-006 | Low | Medium | LLM release readiness | Low | Low | P3 |
| F-007 | Low | Medium | natal dev reporting | Low | Low | P3 |
| F-008 | Info | Low | supported ops scripts | Low | Low | P4 |

## Top Risks

1. `scripts/validate_route_removal_audit.py` est le meilleur candidat suppression: usage ponctuel, story-specifique, racine polluee.
2. Le dossier plat rend les futurs ajouts ambigus: sans index, chaque nouveau script risque de devenir legacy silencieux.
3. Le load-test critique contient des scenarios destructifs ou historiques actifs; il faut separer smoke, perf LLM et privacy delete.
4. `start-dev-stack.ps1` est pratique mais impose Stripe a tout demarrage local et n'a pas encore de garde.
