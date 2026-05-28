# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Obsolete CS-371 future wording is absent. | `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` replaces the future CS-371 sentence with existing artifact links. | `evidence/validation.txt` VC1: forbidden scan PASS no matches. | PASS |
| AC2 | Canonical depths are documented. | Target doc states DB/provider canonical depths `essential`, `expanded`, `complete`; `structure-comparison.md` keeps the same profile mapping. | `evidence/validation.txt` VC2 PASS. | PASS |
| AC3 | Structured birth context is documented. | Target doc and example README document `birth_date`, `birth_time_local`, and `birth_place` under `input_data.birth_context`. | `evidence/validation.txt` VC2 PASS. | PASS |
| AC4 | Interpretation source status is explicit. | Target doc adds `mixed` source status and `production-like` fixture classification; example README/comparison retain source labels. | `evidence/validation.txt` VC4 PASS. | PASS |
| AC5 | CS-371 example links are exact. | Target doc lists README, structure comparison, and all three provider payload paths under the CS-371 example root. | `evidence/validation.txt` VC3 and VC6 PASS. | PASS |
| AC6 | Mermaid diagrams remain coherent. | No Mermaid block was structurally changed; manual review confirms JSON construction and backend-only boundary still match the documented shape. | `evidence/validation.txt` VC6b PASS; `evidence/mermaid-check.md` PASS. | PASS |
| AC7 | No placeholder remains in scoped docs. | Scoped docs contain no TODO/TBD/template marker and no unclassified active `deep` wording in the target doc. | `evidence/validation.txt` VC1 PASS no matches. | PASS |
| AC8 | Report status is historical or updated. | Delivery report adds explicit historical status after CS-372 to CS-375 corrections. | `evidence/docs-after.txt` includes the historical status wording. | PASS |
| AC9 | Protected application surfaces are unchanged. | Backend app/tests, frontend source, migrations, and provider payload JSON stayed untouched. | `evidence/validation.txt` VC8/VC9 PASS; `evidence/protected-surfaces.txt` PASS. | PASS |
| AC10 | Persistent evidence is stored. | `evidence/docs-baseline.txt`, `docs-after.txt`, `guardrails.txt`, `mermaid-check.md`, `protected-surfaces.txt`, and `validation.txt` exist. | `evidence/validation.txt` VC10 PASS; capsule validation PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
