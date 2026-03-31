---
description: Lancer le linting, le formattage et les tests automatiquement
---
// turbo-all

Ce workflow permet d'uniformiser le code, vérifier les erreurs et exécuter les tests du backend automatiquement sans requérir de validation pour l'exécution des scripts PowerShell.

1. Activer l'environnement et formater : utilise `run_command` pour exécuter `cd backend; .\.venv\Scripts\Activate.ps1; ruff format .`
2. Linter le code : utilise `run_command` pour exécuter `cd backend; .\.venv\Scripts\Activate.ps1; ruff check . --fix`
3. Exécuter les tests unitaires : utilise `run_command` pour exécuter `cd backend; .\.venv\Scripts\Activate.ps1; pytest -q --tb=short`
