# Acceptance Traceability - CS-216

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Contrats interpretatifs immuables. | Added immutable enums/dataclass in `contracts.py`. | `pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` PASS. | PASS |
| AC2 | Catalogue avec les onze cles minimales. | Added immutable catalog entries. | Profile runtime tests inspect required keys: PASS. | PASS |
| AC3 | Runtime extrait des profils depuis chaque famille contractuelle. | Added `resolve_advanced_condition_profiles`. | Profile runtime tests: PASS. | PASS |
| AC4 | L'ordre de priorite de resolution est respecte. | Runtime priority: planet+tradition, planet, tradition, global. | Profile runtime tests: PASS. | PASS |
| AC5 | Resolution generique si aucun profil specifique. | Static generic lookup, no dynamic generation. | Profile runtime tests: PASS. | PASS |
| AC6 | Plusieurs profils par planete sont supportes. | Returns tuple of all condition profiles in deterministic order. | Profile runtime tests: PASS. | PASS |
| AC7 | Conditions absentes tolerees sans exception. | Runtime skips missing condition objects. | Profile runtime tests: PASS. | PASS |
| AC8 | Profil specifique manquant sans blocage global. | Missing condition keys return no profile for that key only. | Profile runtime tests: PASS. | PASS |
| AC9 | `combust` inclut `hidden`, `burned`, `overpowered`. | Catalog entry for combust keywords. | Profile runtime tests: PASS. | PASS |
| AC10 | `retrograde` inclut `internalized`, `revisiting`, `reprocessing`. | Catalog entry for retrograde keywords. | Profile runtime tests: PASS. | PASS |
| AC11 | Les phases lunaires resolvent des profils dedies. | Moon-only full/new moon extraction. | Profile runtime tests: PASS. | PASS |
| AC12 | Runtime natal expose les profils par planete en champ interne. | Added excluded field and populated it. | NatalResult integration tests: PASS. | PASS |
| AC13 | Aucun scoring dans les nouveaux modules. | Avoided scoring symbols in new package. | Forbidden scoring scan: zero hits. | PASS |
| AC14 | Les surfaces externes interdites sont absentes. | Kept package pure domain. | Forbidden surface scan and tests: PASS. | PASS |
| AC15 | Aucun texte final utilisateur ni paragraphe narratif. | Catalog uses bounded fragments only. | Profile runtime tests and final-text scan: PASS. | PASS |
| AC16 | Aucun recalcul des calculateurs CS-209 a CS-214. | Runtime consumes contracts only. | Duplication scan zero hits; adjacent diff empty. | PASS |
| AC17 | `RG-143` existe dans le registre de guardrails. | No code change needed. | `rg -n "RG-143" _condamad/stories/regression-guardrails.md` PASS. | PASS |
| AC18 | Validation complete sous venv. | Evidence and status updates completed. | Required validation commands PASS; first full pytest attempt timed out and rerun passed. | PASS |
