# No Legacy / DRY Guardrails - CS-174

## Interdits

- `SIGN_NAMES_FR` dans les surfaces applicatives ciblees.
- Liste locale `SIGNS = [...]` dans les services LLM.
- Re-export de `SIGN_NAMES_FR` depuis `prompt_context.py`.
- Import du resolver ou des modeles de traduction depuis `backend/app/domain/astrology`.
- Mapping concurrent de signes hors exception PDF documentee.

## Preuves requises

- Tests unitaires ciblant le resolver et les consommateurs.
- Test d'architecture documentant l'exception PDF.
- Scans negatifs des symboles interdits.
