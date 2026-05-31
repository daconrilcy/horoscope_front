# Eligibility Before

- No canonical `EligibilityContext` owner existed at `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py`.
- `llm_astrology_input_v1.py` copied `structured_facts_v1.structural_facts.houses` and position `house_number` into prompt-visible facts without a Basic eligibility gate.
- `structured_facts_v1_builder.py` exposed `birth_time` but not `birth_timezone` in `missing_data`, so missing timezone could not be classified separately from full-time confidence.
- `generated/11-code-review.md` was a story-writing review, not implementation evidence.
