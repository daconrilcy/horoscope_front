# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Tous les fichiers story-numbered sont classes. | Ajouter `story-test-inventory-before.md`, `story-test-inventory-after.md` et `story-guard-mapping.md`. | Mapping scan sur `test_story_` et `RG-`; `pytest -q app/tests/unit/test_backend_story_guard_names.py`. | PASS |
| AC2 | Les guards conserves ont un invariant. | Chaque ligne du mapping porte un invariant durable ou RG existant. | Mapping scan sur `RG-00[1-9]` et `invariant`; test de mapping. | PASS |
| AC3 | Un premier lot garde ses assertions. | Renommer le premier lot services puis tous les autres fichiers story-numbered vers des noms durables; seules les auto-references et fonctions `test_story_*` ont ete renommees. | Tests cibles du catalogue, du lot services, et des fichiers avec fonctions renommees. | PASS |
| AC4 | Aucun fichier story-numbered non classifie ne reste. | Guard pytest exige zero fichier backend `test_story_*.py` actif et verifie les cibles migrees. | `pytest -q app/tests/unit/test_backend_story_guard_names.py`; `rg --files backend -g test_story_*.py` zero-hit. | PASS |
| AC5 | Une garde bloque les nouveaux noms non approuves. | `test_backend_story_guard_names.py` echoue si un fichier backend `test_story_*.py` reapparait ou si une cible migree manque. | `pytest -q app/tests/unit/test_backend_story_guard_names.py`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
