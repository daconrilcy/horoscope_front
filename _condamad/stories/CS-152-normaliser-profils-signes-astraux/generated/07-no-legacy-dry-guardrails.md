# No Legacy / DRY Guardrails

## Canonical Owners

- Signes: `AstralSignModel` dans `backend/app/infra/db/models/reference.py`.
- Profils: `AstralSignProfileModel` et taxonomies `astral_*`.
- Maîtrises: `AstralSignRulershipModel` dans `backend/app/infra/db/models/prediction_reference.py`.
- Seed: `backend/app/services/prediction/reference_seed_service.py`.

## Forbidden Active Surfaces

- `__tablename__ = "signs"`
- `__tablename__ = "sign_rulerships"`
- `SignRulershipModel.reference_version_id`
- `SignRulershipModel(reference_version_id=...)`
- Vue, alias ORM, re-export durable ou shim conservant `signs` ou `sign_rulerships`.
- `AstroCharacteristicModel` ou `astro_characteristics`.

## Required Evidence

- Tests de migration inspectant les tables et contraintes.
- Tests de seed prouvant les 12 profils, taxonomies et maîtrises.
- Tests repository prouvant la lecture des maîtrises sans version.
- Scans anti-retour avec classification des hits restants.
