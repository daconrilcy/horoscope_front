# Instructions Claude Code

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

### style
- Aucun style inline : tout doit etre mis en oeuvre dans le fichier .css ou .scss approprie
- utiliser et reutiliser les variables de couleurs, bordure, marge, etc. present dans les feuilles styles. Verifier leur presence avant de les re creer.
