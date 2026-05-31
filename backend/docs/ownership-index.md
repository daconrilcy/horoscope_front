# Backend Docs Ownership Index

Cet index classe chaque fichier suivi sous `backend/docs/` afin que les artefacts
documentaires backend aient un owner explicite et une garde determinee.

## Allowed Artifact Types

| Artifact type | Meaning |
|---|---|
| `generated-doc` | Document regenere ou compare depuis une source executable. |
| `executable-registry` | Registre lu par du code ou un validateur. |
| `canonical-spec` | Specification canonique gardee par runtime, tests ou snapshots. |
| `human-runbook` | Procedure humaine non source de verite runtime. |
| `historical-note` | Note historique ou decisionnelle non canonique. |
| `governance-doc` | Document de gouvernance locale ou index. |
| `generated-artifact` | Artefact produit par un job ou script, non edite comme prose. |

## Ownership Rows

| File | Owner | Artifact type | Canonical status | Expected guard |
|---|---|---|---|---|
| `backend/docs/README.md` | Backend docs governance | governance-doc | canonical-guarded | `pytest -q app/tests/unit/test_backend_docs_ownership.py` |
| `backend/docs/ownership-index.md` | Backend docs governance | governance-doc | canonical-guarded | `pytest -q app/tests/unit/test_backend_docs_ownership.py` |
| `backend/docs/astrology-zodiac-runtime-contract.md` | Backend astrology runtime | canonical-spec | canonical-guarded | `pytest -q tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_ephemeris_provider.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_calculation_service.py` |
| `backend/docs/basic-natal-reading-v2-contract.md` | Lecture natale Basic V2 | canonical-spec | canonical-guarded | `pytest -q tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py` |
| `backend/docs/narrative-natal-reading-v1-contract.md` | Lecture natale narrative publique | canonical-spec | canonical-guarded | `pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_narrative_natal_reading_public_boundary.py` |
| `backend/docs/examples/narrative-natal-reading-v1-basic.json` | Lecture natale narrative publique | generated-artifact | generated-artifact | `pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_narrative_natal_reading_public_boundary.py` |
| `backend/docs/examples/narrative-natal-reading-v1-free.json` | Lecture natale narrative publique | generated-artifact | generated-artifact | `pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_narrative_natal_reading_public_boundary.py` |
| `backend/docs/examples/narrative-natal-reading-v1-premium.json` | Lecture natale narrative publique | generated-artifact | generated-artifact | `pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_narrative_natal_reading_public_boundary.py` |
| `backend/docs/openapi-public-internal-boundary.md` | Backend API contract governance | canonical-spec | canonical-guarded | `pytest -q tests/architecture/test_api_contract_neutrality.py app/tests/integration/test_api_openapi_contract.py --long` |
| `backend/docs/guarded-artifacts/llm-model-structure.md` | LLM model structure generator | generated-doc | canonical-guarded | `pytest -q tests/unit/test_llm_canonical_perimeter.py` |
| `backend/docs/guarded-artifacts/llm-db-cleanup-registry.json` | LLM DB cleanup validator | executable-registry | canonical-guarded | `pytest -q tests/integration/test_llm_db_cleanup_registry.py` |
