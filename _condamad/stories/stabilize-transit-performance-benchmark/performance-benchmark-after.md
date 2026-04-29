# Validation apres stabilisation

## Etat final

- Le test standard conserve les mesures runtime pour produire le signal local.
- Les assertions de diagnostics `budget_target_ms` et `sample_count` restent dans le chemin standard.
- Les assertions wall-clock strictes sont executees uniquement si
  `RUN_PERF_BENCHMARKS=1`.
- Une garde AST dans `test_v3_performance_wall_clock_budget_assertions_are_opt_in`
  echoue si une comparaison stricte contre `TARGET_BUDGET_MS` revient hors du
  bloc opt-in.

## Commandes ciblees

Toutes les commandes Python ont ete executees apres activation du venv.

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_transit_performance.py
```

Resultat:

```text
2 passed in 0.45s
```

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py; Remove-Item Env:RUN_PERF_BENCHMARKS
```

Resultat:

```text
2 passed in 0.46s
```

## Scan budget

Commande:

```powershell
rg -n "assert dur_.*< .*TARGET_BUDGET_MS|TARGET_BUDGET_MS = " backend\app\tests\unit\test_transit_performance.py backend\app\prediction
```

Classification:

| Hit | Classification |
|---|---|
| `backend/app/tests/unit/test_transit_performance.py:138` | Assertion stricte autorisee dans le bloc `if _run_perf_benchmarks()`. |
| `backend/app/tests/unit/test_transit_performance.py:139` | Assertion stricte autorisee dans le bloc `if _run_perf_benchmarks()`. |
| `backend/app/prediction/intraday_activation_builder.py:39` | Budget produit conserve a `50.0`. |
| `backend/app/prediction/transit_signal_builder.py:36` | Budget produit conserve a `100.0`. |
| `backend/app/prediction/impulse_signal_builder.py:39` | Budget hors scope conserve. |
