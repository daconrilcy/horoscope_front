# CS-299 — Close replay_snapshot_v1 Runtime Validation

## Résumé

Clôturer le runtime `replay_snapshot_v1` avec preuves CONDAMAD, tests complets, scans de non-exposition publique et mise à jour du rapport.

## Contexte

CS-295 à CS-298 doivent livrer stockage, service, API admin interne, replay contrôlé, audit logs et purge. Il faut une story de clôture qui vérifie l'ensemble et synchronise les preuves.

## Objectif

Produire la preuve finale de livraison runtime CS-278 sans ajouter de nouveau comportement fonctionnel.

## Préalable obligatoire

Relire toutes les preuves CS-295 à CS-298, les docs DPO/sécurité et le rapport `_condamad/reports/CS-256-CS-291-delivery-report.md`.

## Périmètre inclus

1. Vérifier que CS-278 peut passer de `ready-to-dev` à `done`.
2. Produire ou mettre à jour `generated/10-final-evidence.md` CS-278.
3. Exécuter lint + tests complets backend.
4. Vérifier OpenAPI et routes publiques.
5. Vérifier absence de données interdites dans DB/logs/tests.
6. Mettre à jour le rapport de livraison.
7. Documenter les risques résiduels.

## Hors périmètre

- Ajouter du nouveau runtime.
- Ajouter frontend.
- Modifier l'approbation DPO/sécurité.
- Étendre les rôles au-delà du périmètre approuvé.

## Critères d'acceptation

1. CS-278 est `done` uniquement si les AC runtime sont prouvés.
2. Le rapport reflète l'état final.
3. `ruff check .` passe.
4. Le pytest complet backend passe.
5. Les scans confirment aucune exposition publique/client replay.
6. Les preuves CONDAMAD sont persistées.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q --tb=short
python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi()['paths']"
```

## Dépendances

- CS-295.
- CS-296.
- CS-297.
- CS-298.

## Risques

Le risque principal est de marquer CS-278 livré alors qu'un seul sous-ensemble est prouvé. Cette story doit être stricte : si un AC runtime manque, CS-278 reste partiel.
