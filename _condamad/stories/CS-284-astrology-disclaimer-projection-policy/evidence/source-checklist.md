<!-- Commentaire global: cette checklist prouve que les sources nommees par CS-284 et CS-293 ont ete consultees sans elargir le scope. -->

# Source Checklist

| source | status | evidence |
|---|---|---|
| `_story_briefs/cs-293-close-astrology-disclaimer-projection-policy-evidence.md` | PASS | brief source read; scope limited to policy and evidence closure |
| `_condamad/stories/CS-293-close-astrology-disclaimer-projection-policy-evidence/00-story.md` | PASS | AC1-AC10 loaded |
| `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md` | PASS | closure contract read |
| `backend/app/services/resources/templates/disclaimer_registry.py` | PASS | static registry and `get_disclaimers(locale)` identified |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | PASS | application disclaimer injection identified |
| `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py` | PASS | `ASTROLOGY_GENERAL_LIMITATION` and `ASTROLOGY_MISSING_BIRTH_TIME` identified |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | PASS | plan-specific projection disclaimer reuse identified |
| `backend/app/services/llm_generation/shared/natal_context.py` | PASS | degraded mode vocabulary identified |
| `backend/app/services/llm_generation/guidance/guidance_service.py` | PASS | guidance local disclaimer behavior inventoried; future alignment required only if promoted to official B2C projection |
| `docs/architecture/official-product-primitives-public-projections.md` | PASS | projection governance consulted; no runtime drift introduced |
| `docs/architecture/beginner-summary-v1-contract.md` | PASS | missing birth time coverage consulted |
| `docs/architecture/client-interpretation-projection-v1-contract.md` | PASS | plan depth and LLM boundary consulted |
| `docs/architecture/b2c-projection-entitlement-policy.md` | PASS | `free`, `basic`, `premium` policy consulted |
| `_condamad/stories/regression-guardrails.md` | PASS | scoped RG-002 row found by targeted search |

## No Legacy / DRY Result

- No shim, alias, wrapper, route, prompt owner or frontend-only owner was added.
- No duplicate disclaimer registry was created.
- Existing projection builders and static registry remain the cited owners.
- CS-293 adds policy/evidence only.
