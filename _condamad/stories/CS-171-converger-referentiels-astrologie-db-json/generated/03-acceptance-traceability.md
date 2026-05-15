# Acceptance Traceability

| Critere | Preuve |
|---|---|
| `astral_aspect_families` n'est plus vide apres migration | `reference-runtime-after.md`: familles = 3 |
| Les aspects rejoignent leur famille | `reference-runtime-after.md`: aspects joints = 20, references invalides = 0 |
| Le payload `ReferenceDataService` expose les aspects | `reference-runtime-after.md`: payload aspects = 20 |
| Le fichier singulier est retire | `git status`: `D docs/recherches astro/astral_aspect_family.json` |
| Les constantes actives dupliquees sont retirees | `test_astrology_reference_catalog_guard.py` + scans `rg` sans hit |
| Les helpers dupliques ont un owner unique | `test_astrology_reference_catalog_guard.py::test_runtime_helper_owners_are_unique` |
| Migration Alembic ajoutee | `backend/migrations/versions/20260514_0107_repair_astral_aspect_families_seed.py` |
| Seed applicatif branche sur JSON pluriel | `backend/app/services/prediction/reference_seed_service.py` et `backend/app/infra/db/repositories/astrology_reference_sources.py` |

