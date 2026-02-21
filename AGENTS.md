Objectif: produire une application web maintenable, testée, sécurisée, et cohérente.
Stack imposée:
- Backend: Python 3.13
- Frontend: React (obligatoire)
- OS cible dev: Windows / PowerShell

1) Règle absolue: environnement Python
- Toute commande Python (tests, lint, run, scripts) DOIT être exécutée après activation du venv:
  - PowerShell: .\.venv\Scripts\Activate.ps1
- Si le venv n’existe pas, le créer en premier, puis l’activer, puis installer les dépendances.
- Ne jamais exécuter "python", "pip", "pytest", "ruff", etc. hors venv.

2) Règles d’or de dev (non négociables)
- DRY: pas de duplication. Si tu copies/colles, c’est que tu dois refactor.
- SOLID / orienté objet quand pertinent (pas de classes “fourre-tout”).
- KISS: pas d’over-engineering.
- Vérifier ton travail: tests + lint + exécution locale. Pas de “ça doit marcher”.
- Lisibilité > astuce. Noms explicites, petites fonctions, responsabilités claires.

3) Workflow attendu à CHAQUE changement
- Comprendre la demande, proposer un mini-plan (3–7 étapes max).
- Modifier le code avec le plus petit delta cohérent.
- Ajouter/mettre à jour les tests.
- Exécuter localement: lint + tests (dans le venv).
- Finir avec un récap: ce qui a été fait, comment tester, risques/limites.

4) Architecture de référence (proposée, à respecter)
Monorepo:
- backend/
- frontend/
- shared/ (optionnel: contrats, types, OpenAPI, etc.)

Backend (recommandé):
- Framework API: FastAPI
- Structure:
  backend/
    app/
      api/          (routers)
      core/         (config, logging, sécurité)
      domain/       (entités, règles métier)
      services/     (use-cases)
      infra/        (db, clients externes)
      tests/
    pyproject.toml

Frontend (React obligatoire):
- Vite + React recommandé
- Structure:
  frontend/
    src/
      api/          (client HTTP + hooks)
      components/
      pages/
      state/        (store si besoin)
      utils/
      tests/

5) Qualité Python (recommandations fortes)
- Typage: type hints partout sur le code applicatif.
- Validation d’entrées/sorties: Pydantic.
- Lint/format: Ruff (format + lint) recommandé.
- Tests: Pytest.
- Logging structuré, pas de prints.

Commandes standard (exemples PowerShell, toujours après activation venv):
- Lint/format:
  - ruff format .
  - ruff check .
- Tests:
  - pytest -q

6) Qualité Front (recommandations fortes)
- React en TypeScript recommandé.
- ESLint + Prettier.
- Tests: Vitest + Testing Library (minimum sur les composants critiques).
- Pas de logique métier “importante” dans les composants UI: extraire en hooks/services.

7) Contrats API et intégration front/back
- Le contrat d’API doit être explicite:
  - OpenAPI généré côté backend (FastAPI le fait nativement).
- Le front consomme via un client central (fetch/axios) + gestion d’erreurs uniforme.
- Toujours gérer:
  - loading / error / empty states
  - timeouts côté client si pertinent

8) Données, sécurité, et secrets
- Jamais de secrets en dur. Utiliser variables d’environnement + fichier .env (non commité).
- Valider et sanitizer les entrées.
- CORS: restrictif par défaut (pas de "*") sauf besoin clair.
- AuthN/AuthZ: ne pas improviser. Si demandé, proposer une implémentation standard (JWT/OAuth) + tests.

9) DB / migrations (si base de données)
- Utiliser un ORM standard (SQLAlchemy) + migrations (Alembic).
- Pas de requêtes SQL “cachées” dans la couche UI.
- Les accès DB passent par une couche infra/repo.

10) Performance et robustesse
- Éviter le travail bloquant dans les handlers (I/O lourde => background tasks/queue si requis).
- Pagination sur endpoints listant des collections.
- Timeout sur appels externes.
- Gestion propre des exceptions + réponses d’erreur cohérentes.

11) Git et discipline de commits
- Petits commits, message clair.
- Ne jamais commiter:
  - .env
  - .venv
  - node_modules
- Mettre à jour README si le mode d’exécution change.

12) Ce que l’agent NE DOIT PAS faire
- Ne pas inventer des dépendances “magiques” non nécessaires.
- Ne pas changer la stack (React obligatoire, Python 3.13 côté back).
- Ne pas introduire 3 façons différentes de faire la même chose.
- Ne pas “corriger” du style sans raison (refactor massif uniquement si demandé ou si nécessaire).

13) Checklist de fin (obligatoire avant de conclure)
- Le venv était activé pour toutes les commandes Python.
- Lint/format OK.
- Tests OK.
- L’app démarre localement (ou instructions exactes pour le faire).
- Pas de duplication introduite.
- Les erreurs sont gérées (status codes, messages).
