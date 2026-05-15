# Audit duplication astrologie

## Portee

Audit realise pendant CS-171 sur les sources actives `backend/app`, `backend/tests` et `docs/recherches astro`.

## Sources de verite retenues

- Familles d'aspects: `docs/recherches astro/astral_aspect_families.json`
- Aspects: `docs/recherches astro/aspects.json`
- Vocabulaire structurel stable: `docs/recherches astro/structural_reference_catalog.json`
- Systemes astraux: `docs/recherches astro/astral_systems.json`
- Dignites signe-planete: `docs/recherches astro/planet_sign_diginities.json`
- Normalisation zodiacale: `backend/app/domain/astrology/zodiac.py`
- Chargement Swiss Ephemeris: `backend/app/domain/astrology/swisseph_runtime.py`
- Catalogues runtime corps/maisons/aspects: `backend/app/domain/astrology/celestial_runtime_catalog.py`
- Extraction de listes de profils d'interpretation: `backend/app/domain/astrology/interpretation/profile_fields.py`

## Classification

| Item | Decision | Owner canonique | Consommateurs | Preuve |
|---|---|---|---|---|
| `astral_aspect_family.json` | supprime | `astral_aspect_families.json` | seed reference, migration 0107 | scan sans hit |
| `ASPECT_FAMILY_ROWS`, `ASPECT_ROWS` | supprime | `aspects.json`, `astral_aspect_families.json` | `ReferenceRepository`, migration 0107 | test garde + scan |
| listes locales `planet_rows`, `sign_rows`, `dignity_type_rows`, `house_rows` | supprime | `structural_reference_catalog.json` | `ReferenceRepository.seed_version_defaults` | test garde + scan |
| systemes astraux locaux | supprime | `astral_systems.json` | `ReferenceRepository.seed_version_defaults` | loader `load_astral_system_names` |
| `DEFAULT_ASPECT_ORBS` | supprime du runtime actif | tables aspect definitions/orb rules | calcul natal, seed prediction | scan sans hit |
| `DEFAULT_TRADITIONAL_SIGN_RULERSHIPS` | supprime | `planet_sign_diginities.json` via DB | `NatalCalculationService`, `PredictionReferenceRepository` | tests natal verts |
| helpers longitude locaux | supprime | `zodiac.py` | providers/calculators | test owner unique |
| loaders Swiss Ephemeris locaux | supprime | `swisseph_runtime.py` | providers maisons/ephemerides | test owner unique |
| listes maisons angulaires/succedentes | centralise | `celestial_runtime_catalog.py` | astrology + prediction sensitivity | scan sans hit sur anciens noms |
| helpers `_profile_list`, `_require_list` | centralise | `profile_fields.py` | builders interpretation aspects | test owner unique |

## Garde ajoutee

`backend/app/tests/unit/test_astrology_reference_catalog_guard.py` bloque le retour du fichier singulier, des constantes dupliquees et des helpers locaux remplaces par des owners uniques.

## Exceptions

La migration 0107 lit les JSON canoniques au lieu de recopier les familles et rattachements. Elle reste une migration data-fix idempotente dont la seule responsabilite est de reparer les lignes deja presentes en base.
