# CS-248 Trace Before

- Baseline: aucun module `calculation_graph_execution_trace.py` n'existait dans `backend/app/domain/astrology/runtime`.
- Le runner CS-227 produisait `CalculationGraphExecutionResult` avec `outputs`, `node_results`, `execution_order`, `cache_hits`, `provenance` et `errors`.
- Aucune trace versionnee interne n'etait attachee au resultat du runner.
- La provenance du runner restait une surface distincte et pouvait contenir la valeur `output`, donc elle ne devait pas etre reutilisee comme trace redigee.
