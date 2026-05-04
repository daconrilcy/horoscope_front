# Inventaire apres suppression

## Resultat attendu

Le dossier `backend/app/prediction` est absent. Les fichiers suivis ont ete deplaces sous `backend/app/domain/prediction` et tous les imports actifs ont ete migres vers `app.domain.prediction`.

## Commandes executees

| Commande | Repertoire | Resultat |
|---|---|---|
| `rg --files app/prediction` | `backend/` | Aucun fichier; `rg` retourne 1 avec erreur OS car le chemin n'existe plus. |
| `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend/` | Zero-hit. |
| `rg -n "from app\.prediction\|import app\.prediction" ..\backend\tests -g "*.py"` | `backend/` | Zero-hit. |
| `python -c "import importlib.util; assert importlib.util.find_spec('app.prediction') is None; import app.main"` | `backend/`, venv active | PASS. |

## Owner runtime apres migration

- Owner canonique effectif pour les modules historiques: `backend/app/domain/prediction`.
- Consumers applicatifs, API, infra et tests: imports directs `app.domain.prediction.*`.
- Ancien owner: aucun fichier sous `backend/app/prediction`, aucun package importable `app.prediction`.
