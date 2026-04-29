# Implementation Plan

## Current finding

Le harnais `backend/app/tests` remplace encore globalement `app.infra.db.session.engine` et `SessionLocal`. Plusieurs tests importent ensuite ces symboles directement. `backend/tests/integration/app_db.py` existe déjà comme helper pour les tests `backend/tests/integration`, mais il n'est pas encore utilisé par le lot `test_llm_release.py`.

## Target approach

1. Capturer l'inventaire avant.
2. Étendre/documenter le helper `tests/integration/app_db.py`.
3. Ajouter un helper `app/tests/helpers/db_session.py` dans l'arbre existant.
4. Migrer deux tests représentatifs: `tests/integration/test_llm_release.py` et `app/tests/integration/test_admin_content_api.py`.
5. Ajouter une garde AST path-based avec allowlist persistée.
6. Valider dans le venv.

## No Legacy stance

Les imports directs restants sont explicitement allowlistés. Les fichiers migrés sont retirés de l'allowlist pour empêcher leur retour.

## Rollback

Revenir aux imports directs dans les deux tests migrés et supprimer le helper/garde ajoutés si les tests ciblés démontrent une incompatibilité non réparable dans le scope.
