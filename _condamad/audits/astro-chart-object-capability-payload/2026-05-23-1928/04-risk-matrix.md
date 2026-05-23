# Risk Matrix - Astro Chart Object Capability Payload

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | All future chart object families and consumers | New object families can duplicate capability semantics or bypass canonical selection | Medium | P0 |
| F-002 | High | Medium | Runtime graph enrichment phases and object payload invariants | Payload/capability mismatches can be introduced outside constructor validation | Medium | P0 |
| F-003 | Medium | Medium | Lots, midpoints, derived points and public taxonomy | Future implementation may choose the wrong object family and require migration | Medium | P1 |
| F-004 | Medium | Medium | Aspect engine, angle semantics and graph options | Aspect participation can diverge between builder defaults and graph behavior | Low | P1 |
| F-005 | Medium | Medium | Nodes, astral points and point-aspect policy | Nodes may be treated inconsistently as planets, points or dedicated objects | Low | P1 |
| F-006 | Info | Low | Public projection and interpretation surfaces | Raw fixed-star payload exposure would be harmful, but existing guards keep it internal | Low | P2 |
