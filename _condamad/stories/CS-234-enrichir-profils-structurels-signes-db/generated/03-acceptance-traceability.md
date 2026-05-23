# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Four structural sign attributes exist. | `AstralSignProfileModel` now has non-null FK columns `seasonal_quadrant_id`, `fertility_class_id`, `voice_class_id`, `form_class_id`; migration `20260523_0137_enrich_astral_sign_profiles.py` creates four taxonomy tables. | `python -B -m pytest -q app/tests/integration/test_reference_data_migrations.py app/tests/unit/test_prediction_reference_repository.py` - PASS. | PASS |
| AC2 | The twelve signs have complete seeded values. | `docs/db_seeder/astrology/astral_structural_reference_catalog.json` contains twelve enriched sign rows; `ensure_astral_sign_profiles` loads them. | Targeted pytest - PASS; `evidence/seed-check.txt` records all expected mappings. | PASS |
| AC3 | Expected taxonomy codes are persisted. | JSON catalog and migration seed `spring/summer/autumn/winter`, `fruitful/semi_fruitful/barren`, `vocal/semi_vocal/mute`, `humane/bestial/double_bodied/hybrid`. | Integration test asserts table counts, profile joins and expected code matrix. | PASS |
| AC4 | Editorial keyword fields stay non-structural. | New structural fields are sourced from `astral_structural_reference_catalog.json`; sign keywords remain loaded only by `_load_sign_keywords`. | Integration test still asserts keyword fields are present while structural joins use dedicated taxonomies. | PASS |
| AC5 | Domain astrology has no new local mappings. | No production change under `backend/app/domain/astrology`. | `rg -n "\b(seasonal_quadrant|fertility|voice|humane|bestial|fruitful|barren|mute)\b" backend\app\domain\astrology backend\app\services\natal -g "*.py"` - PASS: no matches. | PASS |
| AC6 | Natal services have no new local mappings. | No production change under `backend/app/services/natal`. | Same targeted `rg` scan - PASS: no matches. | PASS |
| AC7 | Old `signs` tables are not restored at head. | Migration down_revision extends current astral head and does not create `signs` or `sign_rulerships`. | Integration test keeps assertions that `signs`, `sign_rulerships`, and `astral_sign_rulerships` are absent at head. | PASS |
| AC8 | Story evidence artifacts are persisted. | `evidence/schema-before.txt`, `schema-after.txt`, `seed-check.txt`, `source-decision.txt`, `validation.txt` added. | Capsule evidence files present; `condamad_validate.py` was run before implementation and passed. | PASS |
| AC9 | Conditional sect or gender traits are decided from sources. | No new sect/gender sign-profile FK added; existing `astral_sect` and `astral_sign_genders` references remain in dignity seed ownership. | `rg -n "sect|gender" docs\"recherches astro" docs\db_seeder\astrology` reviewed; decision recorded in `evidence/source-decision.txt`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
