# LLM Docs Governance

Ce registre classe les documents LLM gardes sous `backend/docs/` et les notes
humaines conservees sous `docs/llm/` pour eviter qu'une note humaine soit
interpretee comme source de verite runtime sans garde.

## Allowed statuses

| Status | Meaning |
|---|---|
| `generated-guarded` | Le document est genere ou compare depuis une source executable. |
| `executable-registry` | Le fichier est consomme directement par un validateur/runtime. |
| `non-canonical-human-note` | Le fichier est une note humaine non normative. |

## Documents

| File | Status | Runtime source | Guard |
|---|---|---|---|
| `backend/docs/guarded-artifacts/llm-model-structure.md` | generated-guarded | LLM canonical perimeter renderer | `pytest -q tests/unit/test_llm_canonical_perimeter.py` |
| `backend/docs/guarded-artifacts/llm-db-cleanup-registry.json` | executable-registry | `app.ops.llm.db_cleanup_validator.LlmDbCleanupValidator` | `pytest -q tests/integration/test_llm_db_cleanup_registry.py` |
| `docs/llm/llm-db-governance.md` | non-canonical-human-note | LLM DB models, migrations and cleanup registry | `pytest -q app/tests/unit/test_llm_docs_governance.py` |
| `docs/llm/llm-runtime-source-of-truth.md` | non-canonical-human-note | LLM runtime code, profiles, releases and assemblies | `pytest -q app/tests/unit/test_llm_docs_governance.py` |
| `docs/llm/llm-canonical-consumption-rebuild.md` | non-canonical-human-note | `LlmCanonicalConsumptionService` and persisted DB models | `pytest -q app/tests/unit/test_llm_docs_governance.py` |
