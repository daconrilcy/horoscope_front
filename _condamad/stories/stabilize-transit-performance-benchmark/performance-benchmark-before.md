# Baseline avant stabilisation

## Etat initial

- Fichier cible: `backend/app/tests/unit/test_transit_performance.py`.
- Le test `test_v3_layers_performance_benchmark` mesure `dur_t`, `dur_a` et `dur_agg` avec `time.perf_counter()`.
- Le chemin pytest standard contenait deux assertions wall-clock strictes:
  - `assert dur_t < TransitSignalBuilder.TARGET_BUDGET_MS`
  - `assert dur_a < IntradayActivationBuilder.TARGET_BUDGET_MS`
- Les diagnostics `budget_target_ms` et `sample_count` etaient deja verifies pour transit et activation.

## Budget constants avant changement

Commande:

```powershell
rg -n "assert dur_.*< .*TARGET_BUDGET_MS|TARGET_BUDGET_MS = " backend\app\tests\unit\test_transit_performance.py backend\app\prediction
```

Resultat observe:

```text
backend\app\tests\unit\test_transit_performance.py:116:    assert dur_t < TransitSignalBuilder.TARGET_BUDGET_MS
backend\app\tests\unit\test_transit_performance.py:122:    assert dur_a < IntradayActivationBuilder.TARGET_BUDGET_MS
backend\app\prediction\impulse_signal_builder.py:39:    TARGET_BUDGET_MS = 50.0
backend\app\prediction\intraday_activation_builder.py:39:    TARGET_BUDGET_MS = 50.0
backend\app\prediction\transit_signal_builder.py:36:    TARGET_BUDGET_MS = 100.0
```

## Baseline runtime

Commande executee avec venv actif:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_transit_performance.py::test_v3_layers_performance_benchmark
```

Resultat observe:

```text
1 passed in 0.38s
```

Le passage isole confirme que le test peut passer localement, mais la story
source documente un echec full-suite precedent a `104.02ms` contre `100ms`.
La surface instable est donc l'assertion wall-clock dans la suite standard.
