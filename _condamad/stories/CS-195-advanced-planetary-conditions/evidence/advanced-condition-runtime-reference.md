# Advanced Condition Runtime Reference Evidence

- Tables added: `astral_advanced_condition_types`,
  `astral_advanced_condition_score_profiles`,
  `astral_advanced_condition_weights`.
- Active parent condition types loaded: mutual reception, hayz, out of sect,
  stationary, besiegement, bonification, maltreatment, fast/slow motion,
  heliacal rising/setting, oriental, occidental.
- Active profile loaded: `traditional_advanced_v1`.
- Runtime repository validation requires exact type and weight coverage for the
  active profile.
- Validation: `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
  passed as part of the targeted and full suites.
