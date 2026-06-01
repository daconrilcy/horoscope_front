# Replay Free -> Basic -> generate_full

Status: PASS

Preuve runtime:

- Test: `python -B -m pytest -q backend\tests\integration\test_theme_natal_bigbang_replay.py --tb=short`
- Resultat observe pendant validation ciblee: inclus dans `8 passed, 5 deselected`.
- Le test cree un slot `free_preview` accepte via `build_contractual_theme_natal_free_preview()`.
- Le replay Free avec une seconde `client_request_id` reutilise le meme slot public.
- Le runtime `ThemeNatalBasicFullReadingRuntime.generate` cree ensuite un slot `basic_full_reading` accepte pour le meme `chart_id`.

Contrat prouve:

| chart_id | output_variant | accepted_count |
|---|---:|---:|
| `chart-cs-435-replay` | `free_preview` | 1 |
| `chart-cs-435-replay` | `basic_full_reading` | 1 |

Champs contractuels Basic verifies:

- `generation_contract_key = theme_natal.reading.basic_full_reading.v1`
- `generation_contract_hash` present sur le resultat runtime et le run persiste
- `generation_contract_snapshot_id` present
- `output_schema_version = theme_natal.output_contract.v1`
- `data_hash` present et identique entre resultat runtime et run persiste
- `public_payload.schema_version = theme_natal_basic_full_public_v1`

AC couverts: AC1, AC2, AC3, AC4, AC9.
