# No Legacy / DRY Guardrails

## Canonical ownership

- `scripts/natal-cross-tool-report-dev.py`: commande racine dev-only.
- `backend/scripts/cross_tool_report.py`: helper existant pour le rapport cross-tool.
- `backend/app/tests/golden`: fixtures golden uniquement pour dev/test.

## Forbidden patterns

- Execution CI nominale du script dev-only.
- Import runtime backend de `app.tests.golden`.
- Nouveau helper `cross_tool_report` sous le dossier racine `scripts/`.
- Wrapper, alias, fallback ou re-export pour masquer un mauvais owner.

## Required evidence

- Test de refus `CI=true`.
- Test ou scan qui prouve que `app.tests.golden` n'est pas consomme par le runtime backend.
- Scan qui prouve l'absence de duplication du helper.
- Documentation de commande avec venv actif.

## Guardrail mapping

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-013 | La story touche une frontiere d'import de modules de tests. | Test AST/import boundary + scan `app.tests.golden`. |
| RG-015 | La story touche un script ops/dev et son ownership. | `scripts/ownership-index.md` et doc dev-only. |
| RG-023 | La story touche un script racine. | Registre `scripts/ownership-index.md` reste exact; aucun script ajoute. |
