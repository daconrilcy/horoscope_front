<!-- Commentaire global: cet inventaire borne les sources de disclaimers astrologiques existantes pour la cloture CS-284. -->

# Disclaimer Inventory

`inventory_scope`: backend, frontend, docs and story briefs.

## Bounded Scans

| scope | command | result |
|---|---|---|
| backend application | `rg -n "disclaimer|disclaimers|avertissement|medical|professionnel|non scientifique|non pred|libre arbitre|heure de naissance|degraded|degrade|mode degrade|IA|LLM" backend/app -g "*.py"` | existing registry, natal injection, projection builders, public contracts and admin/LLM diagnostic surfaces found |
| frontend source | `rg -n "disclaimer|disclaimers|avertissement|medical|professionnel|heure de naissance|degraded|IA|LLM" frontend/src -g "*.ts" -g "*.tsx"` | no canonical B2C disclaimer owner retained for this policy |
| architecture docs | `rg -n "beginner_summary_v1|client_interpretation_projection_v1|free|basic|premium|disclaimer|heure de naissance|degraded|LLM" docs/architecture -g "*.md"` | CS-257/CS-258/CS-283 contracts found |
| story briefs | `rg -n "CS-257|CS-258|CS-283|CS-284|CS-293|disclaimer|projection|LLM|heure de naissance|mode degrade" _story_briefs -g "*.md"` | source brief alignment confirmed |

## Existing Runtime And Contract Sources

| source_owner | evidence | usage_class | classification |
|---|---|---|---|
| `backend/app/services/resources/templates/disclaimer_registry.py` | static locale disclaimers and `get_disclaimers(locale)` | natal, AI | canonical static text registry for current natal interpretation payloads |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | calls `get_disclaimers(locale)` after gateway output and before client payload construction | natal, degraded mode, AI | application injection; LLM output is not the disclaimer source |
| `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py` | `BEGINNER_SUMMARY_V1_DISCLAIMER_CODES`, `BEGINNER_SUMMARY_V1_NO_TIME_DISCLAIMER_CODES`, `BGS_DEGRADED_NO_TIME` | natal, degraded mode, missing birth time | projection builder owns deterministic disclaimer codes |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | imports beginner disclaimer codes and applies them by plan/state | natal, prediction, AI, degraded mode, missing birth time | projection builder reuses canonical code set |
| `backend/app/services/llm_generation/shared/natal_context.py` | `detect_degraded_natal_mode`, `no_time`, `no_location`, `no_location_no_time` | degraded mode, missing birth time | source vocabulary for degraded natal context |
| `backend/app/services/llm_generation/guidance/guidance_service.py` | local guidance disclaimer fallback text and parsed LLM disclaimer fields | prediction, AI | product gap if guidance becomes an official B2C projection; not the CS-257/CS-258 owner |
| `docs/architecture/beginner-summary-v1-contract.md` | `degraded`, `BGS_DEGRADED_NO_TIME`, no raw LLM response | missing birth time, degraded mode | public contract evidence |
| `docs/architecture/client-interpretation-projection-v1-contract.md` | plan variants and LLM role as writer, not calculator/source | prediction, AI | public contract evidence |
| `docs/architecture/b2c-projection-entitlement-policy.md` | `free`, `basic`, `premium`, `beginner_summary_v1`, `client_interpretation_projection_v1` | prediction | plan entitlement evidence |

## Plan Mapping Summary

| projection_id | free | basic | premium |
|---|---|---|---|
| `beginner_summary_v1` | `ASTROLOGY_GENERAL_LIMITATION`; add `ASTROLOGY_MISSING_BIRTH_TIME` on `no_time` | `ASTROLOGY_GENERAL_LIMITATION`; add `ASTROLOGY_MISSING_BIRTH_TIME` on `no_time` | sibling/simple reuse only; same disclaimer codes if reused |
| `client_interpretation_projection_v1` | `ASTROLOGY_GENERAL_LIMITATION`; add `ASTROLOGY_MISSING_BIRTH_TIME` on `no_time` | `ASTROLOGY_GENERAL_LIMITATION`; add `ASTROLOGY_MISSING_BIRTH_TIME` on `no_time` | `ASTROLOGY_GENERAL_LIMITATION`; add `ASTROLOGY_MISSING_BIRTH_TIME` on `no_time` |

## Gap Handling

- `gap_status`: covered for `beginner_summary_v1` and
  `client_interpretation_projection_v1` because disclaimer codes and degraded
  state handling are application-owned.
- `gap_status`: product gap for standalone guidance disclaimer text if a future
  story promotes guidance outputs to an official B2C projection. Owner:
  Product + Architecture. Next action: decide whether to reuse the projection
  disclaimer codes or migrate guidance to the static registry.
- `text_delta_justification`: none. No disclaimer text was created or changed.
