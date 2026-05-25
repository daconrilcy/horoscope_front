# CS-301 — Revalidate replay_snapshot_v1 Runtime Closure After Integrity Fix

## Résumé

Revalider la clôture runtime `replay_snapshot_v1` après correction de l'intégrité payload/hash, puis mettre à jour les preuves CONDAMAD et le rapport de livraison.

## Contexte

CS-299 a marqué le runtime replay comme clôturé, mais la revue post-implémentation a identifié un défaut bloquant : le chemin réel `log_call -> snapshot persisté -> replay` n'était pas couvert et échoue avec un hash divergent.

CS-301 ne doit pas ajouter de comportement fonctionnel nouveau. Elle sert à prouver que CS-300 a corrigé le défaut et que CS-278 peut rester `done` avec une preuve fiable.

## Objectif

Produire une preuve finale mise à jour qui démontre :

- le replay réel fonctionne avec les snapshots produits par `log_call` ;
- les contraintes DPO/sécurité restent respectées ;
- les routes restent strictement admin/interne ;
- le rapport `_condamad/reports/CS-256-CS-291-delivery-report.md` ne revendique plus une clôture fondée sur des tests insuffisants.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md`
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md`
- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- les preuves et tests ajoutés par CS-300

## Périmètre inclus

1. Rejouer les validations replay ciblées après CS-300.
2. Exécuter `ruff check .`.
3. Exécuter le pytest backend complet si possible.
4. Vérifier OpenAPI et routes runtime contre toute exposition publique/client.
5. Vérifier les scans de données interdites avec `email`, `payload_enc`, `birth_date`, `birth_time`, `birth_place`, `latitude`, `longitude`, `raw_prompt`, `raw_output`, `structured_output`, `password`, `api_key`.
6. Mettre à jour les final evidences CS-278 et CS-299 si elles sont conservées comme preuves de clôture.
7. Mettre à jour le rapport de livraison avec l'état réel après CS-300.
8. Documenter explicitement le défaut initial et la preuve de non-régression.

## Hors périmètre

- Ajouter un nouveau service replay.
- Modifier le modèle DPO/sécurité.
- Ajouter frontend, client généré ou route publique.
- Étendre les rôles d'accès.
- Ajouter un export massif.

## Critères d'acceptation

1. La preuve CONDAMAD mentionne explicitement le test bout-en-bout `log_call -> snapshot -> replay`.
2. Les tests ne reposent plus uniquement sur un snapshot fabriqué avec `encrypt_input(user_input)` hors chemin applicatif.
3. Le rapport indique que CS-278 est clôturé seulement après correction CS-300.
4. Les validations replay ciblées passent.
5. `ruff check .` passe.
6. Le pytest complet backend passe ou, s'il est impossible localement, l'échec est documenté avec un lot ciblé suffisant et une action CI explicite.
7. Aucune exposition publique/client `replay_snapshot_v1` n'apparaît dans `app.routes`, OpenAPI ou `frontend/src`.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py tests\integration\test_replay_snapshot_v1_db_redaction.py tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_replay_snapshot_v1_execution_boundary.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short
python -B -m pytest -q --tb=short
python -B -c "from app.main import app; paths=set(app.openapi()['paths']); assert all(path.startswith('/v1/admin/audit') for path in paths if 'replay_snapshot_v1' in path)"
```

## Dépendances

- CS-300.
- CS-278.
- CS-295 à CS-299.

## Risques

Le risque principal est de fermer administrativement CS-278 sans prouver le chemin réel qui avait échappé à CS-299. Cette story doit rester une story de preuve : si le replay bout-en-bout ne passe pas, le rapport doit le dire clairement et CS-278 doit être reclassé en non conforme jusqu'à correction.
