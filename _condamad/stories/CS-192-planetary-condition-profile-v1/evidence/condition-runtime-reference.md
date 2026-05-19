<!-- Rapport runtime des axes conditionnels CS-192. -->

# Condition Runtime Reference Evidence

Validation:

- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS
- `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` - PASS

Preuve:

- Les tables `astral_essential_dignity_score_weights` et
  `astral_accidental_dignity_score_weights` gagnent les colonnes
  `visibility_weight`, `stability_weight`, `coherence_weight`,
  `support_weight` et `constraint_weight`.
- La migration `20260519_0130` ajoute ces colonnes avec `server_default="0.0"`.
- Les modeles SQLAlchemy declarent les champs avec un defaut Python `0.0`.
- `DignityReferenceRepository`, `AstrologyRuntimeReferenceRepository`,
  `AstrologyRuntimeReferenceMapper` et `DignityScoreWeightReferenceData`
  transportent les cinq axes jusqu'au domaine.
- Le domaine expose ces axes sous noms conditionnels
  `condition_visibility`, `condition_stability`, `condition_coherence`,
  `condition_support` et `condition_constraint`; les noms de colonnes DB
  `*_weight` restent confines a l'infra et a la migration.
- Le test runtime verifie que les seeds existants chargent les axes avec
  valeur neutre `0.0`.
- Le test `test_mapper_rejects_missing_condition_weight_axes` verifie que le
  mapper refuse un payload infra incomplet au lieu de neutraliser en silence.
