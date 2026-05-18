# Acceptance Traceability - CS-185

| AC | Statut | Code evidence | Validation evidence |
|---|---|---|---|
| AC1 Repository joint les 12 profils de signes. | PASS | `AstrologyRuntimeReferenceRepository._load_sign_profiles()` joint `AstralSignProfileModel`, `AstralElementModel`, `AstralModalityModel`, `AstralPolarityModel` sans modifier le payload public. | `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`; `evidence/sign-profile-runtime-after.json`. |
| AC2 Dataclasses runtime sans `dict` metier. | PASS | `SignReferenceData` et `SignRuntimeData` exposent `element`, `modality`, `polarity` en champs types. | `pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py`; `pytest -q tests/unit/domain/astrology/test_sign_runtime_data.py`. |
| AC3 Profil manquant bloque le chargement. | PASS | `AstrologyRuntimeReferenceRepository._validate_sign_profiles()` et test de suppression DB. | `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC4 Signatures utilisent les profils runtime. | PASS | `build_sign_runtime_data()` propage les profils; `ChartSignatureCalculator` consomme les champs runtime `element` et `modality` existants. | `pytest -q tests/unit/domain/astrology/test_chart_signature.py`. |
| AC5 Champ non sourceable bloque sans fallback. | PASS | Le mapper exige les champs profile existants; aucun champ candidat absent du schema n'est ajoute. | `rg -n "seasonal_quadrant\|fertility\|humane\|bestial\|voice" app/domain/astrology app/services/natal -g "*.py"` retourne `NO_MATCH`. |
| AC6 Guardrails DB-backed restent verts. | PASS | `test_astrology_runtime_reference_guard.py` bloque les mappings locaux de profils de signes. | `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py`; `pytest -q app/tests/unit/test_astrology_prediction_boundary.py`. |
| AC7 Evidence artifacts are produced. | PASS | `evidence/sign-profile-runtime-before.json`, `evidence/sign-profile-runtime-after.json`, `evidence/openapi-impact.md`, `evidence/guard-evidence.md`. | Artefacts presents dans le dossier story. |
