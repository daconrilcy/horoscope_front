# Backend Test Files Before

Baseline capture avant modification de la garde pour la story
`guard-backend-pytest-test-roots`.

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

- `rg --files backend\app -g 'test_*.py' -g '*_test.py' -g '!backend/app/tests/**' -g '!backend/.tmp-pytest/**'` retourne zero fichier.
- `rg --files backend\app\domain\llm\prompting\tests -g 'test_*.py' -g '*_test.py'` retourne zero fichier.
