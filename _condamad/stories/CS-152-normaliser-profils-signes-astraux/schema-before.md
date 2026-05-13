# Schema Before CS-152

## Active Runtime Models

| Responsibility | Model | Table | Columns relevant to story |
|---|---|---|---|
| Signes | `SignModel` | `signs` | `id`, `code`, `name` |
| Maîtrises | `SignRulershipModel` | `sign_rulerships` | `id`, `reference_version_id`, `sign_id`, `planet_id`, `rulership_type`, `weight`, `is_primary` |

## Missing Target Tables

- `astral_signs`
- `astral_elements`
- `astral_modalities`
- `astral_polarities`
- `astral_sign_profiles`
- `astral_sign_rulerships`

## Seed Baseline

- Les 12 signes sont alimentés par `ReferenceRepository.seed_version_defaults`.
- Les 12 maîtrises traditionnelles sont alimentées par `run_prediction_reference_seed`.
- Les maîtrises sont encore filtrées par `reference_version_id`.

## Baseline Evidence

- `backend/app/infra/db/models/reference.py`: `SignModel.__tablename__ = "signs"`.
- `backend/app/infra/db/models/prediction_reference.py`: `SignRulershipModel.__tablename__ = "sign_rulerships"`.
- `backend/app/infra/db/repositories/prediction_reference_repository.py`: `get_sign_rulerships(reference_version_id)`.
