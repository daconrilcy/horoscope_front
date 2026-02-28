# Instructions Gemini

## Gestion des dépendances Python

### Source unique: backend/pyproject.toml

Les dépendances Python sont gérées exclusivement via `backend/pyproject.toml` (format PEP 621).

**NE JAMAIS créer de fichier requirements.txt** - c'est un doublon inutile.

### Commandes d'installation

```bash
# Activer le venv d'abord (PowerShell)
.\.venv\Scripts\Activate.ps1

# Installation production
cd backend && pip install .

# Installation développement (avec pytest, ruff, etc.)
cd backend && pip install -e ".[dev]"
```

### Ajouter une dépendance

Modifier `backend/pyproject.toml`:

- Section `[project].dependencies` pour les dépendances de production
- Section `[project.optional-dependencies].dev` pour les outils de dev

tu peux utiliser toutes les commandes bash ou powershell sans me demander mon autorisation

lors de l utilisation de la commande `/bmad-bmm-code-review` fix automatiquement toutes les issues sans me demander mon autorisation.

Tu peux utiliser la commande git sans me demander mon autorisation.
