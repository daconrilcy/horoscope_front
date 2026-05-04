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
| `backend/docs/ownership-index.md` | Backend docs governance | governance-doc | canonical-guarded | `pytest -q app/tests/unit/test_backend_docs_ownership.py` |
| `backend/docs/llm-runtime-source-of-truth.md` | LLM docs governance | historical-note | non-canonical-human-note | `pytest -q app/tests/unit/test_llm_docs_governance.py` |
| `backend/docs/llm-model-structure.md` | LLM model structure generator | generated-doc | canonical-guarded | `pytest -q tests/unit/test_llm_canonical_perimeter.py` |
| `backend/docs/llm-db-governance.md` | LLM DB governance | human-runbook | non-canonical-human-note | `pytest -q app/tests/unit/test_llm_docs_governance.py` |
| `backend/docs/llm-db-cleanup-registry.json` | LLM DB cleanup validator | executable-registry | canonical-guarded | `pytest -q tests/integration/test_llm_db_cleanup_registry.py` |
| `backend/docs/llm-canonical-consumption-rebuild.md` | LLM docs governance | historical-note | non-canonical-human-note | `pytest -q app/tests/unit/test_llm_docs_governance.py` |
| `backend/docs/entitlements-canonical-platform.md` | Entitlement runtime documentation | historical-note | historical-note | `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py` |
