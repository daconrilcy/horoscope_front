# Schema After CS-152

## Canonical Tables

| Responsibility | Table | Key columns |
|---|---|---|
| Signes | `astral_signs` | `id`, `code`, `name` |
| Éléments | `astral_elements` | `id`, `code`, `name` |
| Modalités | `astral_modalities` | `id`, `code`, `name` |
| Polarités | `astral_polarities` | `id`, `code`, `name` |
| Profils de signes | `astral_sign_profiles` | `astral_sign_id`, `astral_element_id`, `astral_modality_id`, `astral_polarity_id`, `keywords_json`, `shadow_keywords_json` |
| Maîtrises | `astral_sign_rulerships` | `astral_sign_id`, `planet_id`, `rulership_type`, `system`, `weight`, `is_primary` |

## Constraints

- `astral_sign_profiles` garde une unicité uniquement sur `astral_sign_id`.
- `astral_element_id`, `astral_modality_id` et `astral_polarity_id` ne sont pas uniques, car leurs valeurs sont partagées entre signes.
- `astral_sign_rulerships` n'a plus `reference_version_id`.
- `astral_sign_rulerships` porte `system`.

## Removed Active Tables

- `signs`
- `sign_rulerships`

## Validation Evidence

- `pytest app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py -q` - PASS, 4 tests.
- Scans anti-retour `__tablename__ = "signs"` et `__tablename__ = "sign_rulerships"` - zéro hit actif dans `backend/app` et `backend/tests`.
