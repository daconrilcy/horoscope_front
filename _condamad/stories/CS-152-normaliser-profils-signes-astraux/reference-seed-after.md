# Reference Seed After CS-152

## Counts

| Seed surface | Count |
|---|---:|
| `astral_signs` | 12 |
| `astral_elements` | 4 |
| `astral_modalities` | 3 |
| `astral_polarities` | 2 |
| `astral_sign_profiles` | 12 |
| `astral_sign_rulerships` | 12 |

## Profile Mapping

| Sign | Element | Modality | Polarity |
|---|---|---|---|
| `aries` | `fire` | `cardinal` | `yang` |
| `taurus` | `earth` | `fixed` | `yin` |
| `gemini` | `air` | `mutable` | `yang` |
| `cancer` | `water` | `cardinal` | `yin` |
| `leo` | `fire` | `fixed` | `yang` |
| `virgo` | `earth` | `mutable` | `yin` |
| `libra` | `air` | `cardinal` | `yang` |
| `scorpio` | `water` | `fixed` | `yin` |
| `sagittarius` | `fire` | `mutable` | `yang` |
| `capricorn` | `earth` | `cardinal` | `yin` |
| `aquarius` | `air` | `fixed` | `yang` |
| `pisces` | `water` | `mutable` | `yin` |

## Keywords

- `keywords_json` et `shadow_keywords_json` sont chargés depuis `docs/recherches astro/signs_keywords.json`.
- Le seed échoue si un signe ou une liste `keywords` / `shadow_keywords` manque.
- Le test seed vérifie les 12 profils, les listes non vides et `aries` avec `initiative`.
- Le backend package aussi ce JSON via `backend/pyproject.toml` pour les installations `pip install .`.

## Rulerships

- Les 12 maîtrises seedees utilisent `rulership_type = "domicile"`, `system = "traditional"`, `weight = 1.0`, `is_primary = true`.
- Les maîtrises ne sont plus filtrées ni comptées par `reference_version_id`.

## Scan Classification

| Pattern | Result | Classification |
|---|---|---|
| `SignRulershipModel.reference_version_id` / `SignRulershipModel(reference_version_id` | zero active hit | `active_legacy_removed` |
| `get_sign_rulerships(reference_version_id)` / `__tablename__ = "signs"` | zero active hit | `active_legacy_removed` |
| `__tablename__ = "sign_rulerships"` | zero active hit | `active_legacy_removed` |
| `AstroCharacteristicModel|astro_characteristics` | hits only in migration guard test | `test_guard_expected_hit` |
