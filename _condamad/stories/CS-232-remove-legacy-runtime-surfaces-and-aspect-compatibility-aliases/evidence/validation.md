# CS-232 Validation Evidence

## Changements validés

- `AspectRuntimeData.interpretation` supprimé.
- `AspectInterpretationRuntimeData` supprimé du runtime structurel et des exports paresseux; le contrat homonyme sous `domain/astrology/interpretation` reste hors surface structurelle.
- `build_aspect_runtime_data` ne reçoit plus de bloc interprétatif.
- `json_builder` conserve les clés publiques `interpretive_valence` et `energy_type` via `_public_aspect_interpretive_fields`.
- `AspectResult` conserve les champs plats legacy en entrée interne exclue, sans les exposer dans `model_dump()` ni dans OpenAPI.
- `docs/architecture/astrology-runtime-surfaces.md` ne documente plus `AspectRuntimeData.interpretation` comme projection legacy.
- `backend/tests/architecture/test_structural_runtime_boundary.py` ajouté.
- `backend/tests/architecture/test_api_contract_neutrality.py` bloque le retour des champs legacy dans le schema public `AspectResult`.

## Commandes

Toutes les commandes Python ont été lancées après:

```powershell
.\.venv\Scripts\Activate.ps1
```

Format:

```powershell
ruff format backend\app\domain\astrology\runtime\aspect_runtime_data.py backend\app\domain\astrology\builders\aspect_runtime_builder.py backend\app\domain\astrology\natal_calculation.py backend\app\domain\astrology\runtime\__init__.py backend\app\services\chart\json_builder.py backend\tests\unit\domain\astrology\test_aspect_runtime_builder.py backend\tests\unit\domain\astrology\test_aspect_runtime_contracts.py backend\tests\architecture\test_astrology_runtime_boundary.py backend\tests\architecture\test_structural_runtime_boundary.py
```

Résultat: `1 file reformatted, 8 files left unchanged`.

Lint:

```powershell
ruff check backend
```

Résultat: `All checks passed!`

Tests ciblés:

```powershell
python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\architecture\test_structural_runtime_boundary.py backend\tests\architecture\test_chart_interpretation_input_boundary.py backend\app\tests\unit\test_chart_json_builder.py backend\tests\unit\domain\astrology\test_aspect_interpretive_hint_resolver.py backend\tests\architecture\test_api_contract_neutrality.py
```

Résultat après correction review-fix: `37 passed in 1.74s`.

Tests de régression ciblés aspect:

```powershell
python -B -m pytest -q backend\tests\unit\domain\astrology\test_aspect_runtime_builder.py backend\tests\unit\domain\astrology\test_aspect_runtime_contracts.py backend\tests\unit\domain\astrology\test_aspect_interpretive_hint_resolver.py backend\tests\architecture\test_structural_runtime_boundary.py backend\tests\architecture\test_astrology_runtime_boundary.py backend\app\tests\unit\test_chart_json_builder.py
```

Résultat: `44 passed in 0.71s`.

Suite backend:

```powershell
python -B -m pytest -q backend\tests
```

Résultat après correction d'alignement brief: `868 passed, 201 deselected in 25.51s`.

Review-fix alignement brief/code 2026-05-23:

```powershell
.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; s=app.openapi().get('components',{}).get('schemas',{}); print(s.get('AspectResult',{}).get('properties',{}).keys())"
```

Résultat: `dict_keys(['aspect_code', 'planet_a', 'planet_b', 'angle', 'orb', 'orb_used', 'orb_max', 'family', 'is_major', 'is_minor'])`.

```powershell
.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py backend\tests\architecture\test_structural_runtime_boundary.py backend\app\tests\unit\test_chart_json_builder.py
```

Résultat: `30 passed in 1.41s`.

```powershell
.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\architecture\test_chart_interpretation_input_boundary.py backend\tests\unit\domain\astrology\test_aspect_interpretive_hint_resolver.py backend\tests\architecture\test_astrology_runtime_boundary.py backend\tests\architecture\test_aspect_runtime_boundary.py
```

Résultat: `23 passed in 0.82s`.

Review-fix CS-232:

- Ajout d'une garde architecture vérifiant que `AspectModifierRuntimeData` et `AspectStructuralModifierRuntimeData` ne portent pas de champ interpretatif.
- Correction des preuves qui annonçaient un statut initial incohérent et un scan trop large `AspectInterpretationRuntimeData` en no-match.

## Scans

Commande:

```powershell
rg -n "AspectRuntimeData\.interpretation" backend/app backend/tests -g "*.py"
```

Résultat: PASS, no matches (`rg` exit code 1 attendu).

```powershell
rg -n "AspectInterpretationRuntimeData" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders backend/app/services/chart backend/tests/architecture backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py -g "*.py"
```

Résultat: PASS, no matches (`rg` exit code 1 attendu). Les occurrences restantes sous `backend/app/domain/astrology/interpretation` appartiennent au contrat d'input interpretatif et ne sont pas l'ancien alias runtime.

Commande:

```powershell
rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight" backend/app/domain/astrology/runtime backend/app/domain/astrology/calculators backend/app/domain/astrology/builders backend/app/services/chart backend/app/domain/prediction backend/app/services/prediction -g "*.py"
```

Résultat: hits classés comme hints/profils interpretatifs, projection publique `json_builder`, contrats prediction dédiés ou legacy reference temporaire documentée.

Commande:

```powershell
rg -n "planet_positions|astral_points|houses|advanced_conditions|dignities|fixed_star_conjunctions" backend/app/domain/astrology backend/app/services/chart backend/app/domain/prediction backend/app/services/prediction -g "*.py"
```

Résultat: hits classés comme projection publique, graph outputs, prediction chart-json, reference data ou tests d'architecture existants; pas de nouveau consommateur interne legacy introduit.

## Limites

- La capsule `generated/` n'a pas pu être préparée: le skill `condamad-dev-story` et ses scripts demandés sont absents dans ce workspace.
- Aucun fichier frontend n'a été modifié, car aucun delta public n'a été introduit.
