# Fact Graph After — CS-411

- Canonical model owner added: `backend/app/domain/astrology/interpretation/natal_fact_graph.py`.
- Canonical builder owner added: `backend/app/domain/astrology/interpretation/natal_fact_graph_builder.py`.
- Fact families emitted: `luminary_fact`, `angle_fact`, `planet_position_fact`, `house_emphasis_fact`, `sign_emphasis_fact`, `element_balance_fact`, `modality_balance_fact`, `aspect_fact`, `rulership_fact`, `condition_fact`, `node_fact`.
- Date-only gating removes angle, house and rulership facts while keeping non-time-dependent facts.
- Internal payload keeps `source_paths`; editorial candidate payload omits them.
- Validation: targeted pytest `18 passed`, `ruff check .` PASS, negative scans PASS.
