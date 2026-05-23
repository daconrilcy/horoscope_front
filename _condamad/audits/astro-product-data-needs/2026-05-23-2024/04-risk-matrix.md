# Risk Matrix - Astro Product Data Needs

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Expert natal chart, public JSON, runtime boundary | High: new expert fields can couple frontend to internal runtime | Medium | P0 |
| F-002 | High | High | Beginner/public UI, AI interpretation, translations | High: beginner contract can drift into technical or LLM-only data | Medium | P0 |
| F-003 | Medium | Medium | Fixed-star product section, interpretation evidence | Medium: feature may be skipped or exposed through raw runtime | Medium | P1 |
| F-004 | Medium | Medium | Debug, astrologer workflow, public expert panel, PDF | Medium: wrong audience can receive diagnostic data | High | P1 |
| F-005 | Low | Medium | Audit governance | Low: current story has local guard, future stories may omit it | Low | P2 |

## Risk Notes

- Product risk: beginner, expert, astrologer, debug, AI, PDF and public-user needs must not share one undifferentiated payload.
- Contract risk: public projections must stay separate from `chart_objects`, `advanced_planetary_conditions` and `interpretation_input`.
- Frontend risk: React screens currently consume public API fields directly; new fields need a named projection and translation owner.
- Translation risk: existing resolver covers core labels, but candidate projections must specify labels for expert/fixed-star concepts before display.
- Score risk: dignity, dominance and condition scores are useful, but beginner screens need masked or qualitative forms.
- Complexity risk: debug and expert details are legitimate only with audience-specific contracts.
