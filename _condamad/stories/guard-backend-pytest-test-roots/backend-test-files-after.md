# Backend Test Files After

Inventaire final attendu apres durcissement de la garde. La story ne deplace
aucun fichier de test; les compteurs doivent donc rester identiques au baseline.

## Commande

```powershell
rg --files backend -g 'test_*.py' -g '*_test.py' -g '!backend/.tmp-pytest/**'
```

## Synthese

| Racine detectee | Fichiers |
|---|---:|
| `backend/app/tests` | 339 |
| `backend/tests/evaluation` | 3 |
| `backend/tests/integration` | 25 |
| `backend/tests/llm_orchestration` | 40 |
| `backend/tests/unit` | 24 |
| Autre | 0 |
| Total | 431 |

## Verification hors racines

- `pytest -q app/tests/unit/test_backend_test_topology.py` valide que tous les fichiers de tests backend sont sous les racines documentees.
- La comparaison avant/apres n'autorise aucun ajout sous une racine cachee.
