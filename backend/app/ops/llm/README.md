# Ops LLM

Ce dossier centralise les scripts operationnels lies au process LLM.

## Structure

- `bootstrap/` : initialisation et seed operables.
- `migrations/` : scripts one-shot de migration.
- `release/` : generation et verification des artefacts de release.
- `legacy/` : diagnostics/transitions temporaires legacy.

## Usage

- Toujours activer le venv avant execution :
  - `.\.venv\Scripts\Activate.ps1`
- Exemple release candidate :
  - `cd backend`
  - `python -m app.ops.llm.release.build_release_candidate --help`

## Notes de transition

- Certains scripts restent physiquement sous `backend/scripts/` pendant la migration.
- Les points d entree canoniques sous `app.ops.llm` sont les chemins a utiliser des maintenant.
- Le registre `TRANSITION_WRAPPERS.md` a ete retire : plus de shims `app.llm_orchestration` ; le runtime LLM nominal vit sous `app.domain.llm.*`, `app.application.llm.*`, `app.infra.*` et `app.ops.llm.*`.
