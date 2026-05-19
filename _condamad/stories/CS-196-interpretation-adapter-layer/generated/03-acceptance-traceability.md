# CS-196 Acceptance Traceability

| AC | Evidence |
| --- | --- |
| AC1 | Migration `20260519_0136`, models SQLAlchemy, JSON seeds, `pytest -q --long backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC2 | `AstrologyRuntimeReference.interpretation_adapter_reference`, `test_astrology_runtime_reference_repository.py`. |
| AC3 | `SignalBuilder`, `test_signal_builder.py`. |
| AC4 | `PriorityRanker`, `priority_default_rank`, `priority_override_rank`, `test_priority_ranker.py`. |
| AC5 | `ThemeAggregator`, `test_theme_aggregator.py`. |
| AC6 | `InterpretationAdapterEngine`, no narrative text, `test_interpretation_adapter_engine.py`, guard scans. |
| AC7 | `NatalResult.interpretation_adapter` after `dominant_planets`, `test_natal_result_contract.py`. |
| AC8 | `json_builder.py::_serialize_interpretation_adapter`, serializer guard. |
| AC9 | `test_chart_result_service.py` validates persisted chart payload path. |
| AC10 | `test_astrology_runtime_reference_guard.py` and RG-123 scans. |
| AC11 | Psychological axes as runtime categories: `dominant_axes`, `theme_category`, `test_interpretation_adapter_engine.py`. |
| AC12 | Functional axes as runtime categories: `support_patterns`, `test_theme_aggregator.py`. |
| AC13 | Tensions as codes: `tension_patterns`, `test_theme_aggregator.py`. |
| AC14 | Supports as codes: `support_patterns`, `test_theme_aggregator.py`. |
| AC15 | Before/after payload snapshots and `ruff check .`. |
