# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `DignityRuntimePayload` expose une projection calculatoire stable. | `chart_object_runtime_data.py`, tests dignity runtime | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py` | PASS |
| AC2 | `DominanceRuntimePayload` porte une contribution objet sans remplacer `DominantPlanetsResult`. | `chart_object_runtime_data.py`, dominance projector | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py` | PASS |
| AC3 | `ChartObjectPayloads` expose les payloads CS-220 avec validation par phase. | payloads + `validate_*_payloads` | builder/runtime tests | PASS |
| AC4 | `DignityChartObjectSelector` selectionne par `supports_dignities=True`. | `dignities/chart_object_inputs.py` | dignity runtime selector test | PASS |
| AC5 | `DominanceChartObjectSelector` selectionne par `supports_dominance=True`. | `dominance/chart_object_inputs.py` | dominance runtime selector test | PASS |
| AC6 | Les projectors d'entree dignity consomment `ChartObjectRuntimeData` sans `object_type`. | dignity input projector | dignity runtime + architecture guard | PASS |
| AC7 | Les projectors de resultats dignity ne recalculent pas les scores. | dignity payload projector | payload projector test avec total non additionne | PASS |
| AC8 | Les enrichers dignity retournent de nouvelles instances. | dignity enricher | enricher immutability test | PASS |
| AC9 | L'orchestrateur natal execute le flux multi-passes CS-220. | `natal_calculation.py` | natal chart objects integration test | PASS |
| AC10 | Les sorties historiques restent disponibles avec les nouveaux payloads chart-object. | `NatalResult` inchangé + chart objects enrichis | natal result contract + chart object tests | PASS |
| AC11 | Les golden cases de dignite/dominance restent stables. | calculateurs preserves | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | PASS |
| AC12 | Les nouveaux consommateurs runtime ne retournent pas vers `planet_positions`. | new projectors + engine argument renomme | architecture guard + scans | PASS |
| AC13 | Aucun payload runtime dignity ne contient de texte narratif. | payload fields factuels | dignity runtime non-narrative test + scan classe | PASS |
| AC14 | Les objets non concernes ne recoivent pas de payload incoherent. | validation payload sans capacite | builder/natal tests | PASS |
| AC15 | Le guardrail bloque l'eligibilite par `object_type`. | architecture guard | `test_chart_object_runtime_architecture.py` | PASS |
| AC16 | L'evidence finale CS-220 est persistee. | `evidence/validation.md`, final evidence | `rg -n "CS-220 Final Evidence" ...` | PASS |
| AC17 | Les entrees dominance viennent de `ChartObjectRuntimeData` sans `object_type`. | dominance input projector | dominance runtime + architecture guard | PASS |
| AC18 | Les projectors de resultats dominance ne recalculent pas les scores. | dominance payload projector | payload projector test | PASS |
| AC19 | Les enrichers dominance retournent de nouvelles instances. | dominance enricher | enricher immutability test | PASS |
| AC20 | Aucun payload runtime dominance ne contient de texte narratif. | payload fields factuels | dominance runtime non-narrative test + scan classe | PASS |
| AC21 | Un objet dignity-capable sans donnees minimales produit une erreur explicite. | dignity input validation | invalid dignity test | PASS |
| AC22 | Un payload dignity/dominance sans capacite ou cible inconnue produit une erreur. | runtime validation + enrichers | builder/runtime tests | PASS |
| AC23 | Les objets sans doctrine explicite ne deviennent pas dignifiables par defaut. | builder capabilities | builder/natal tests | PASS |
| AC24 | Le guardrail bloque l'eligibilite par code nominal ou liste traditionnelle. | architecture guard CS-220 | `test_chart_object_runtime_architecture.py` + scans classes | PASS |
