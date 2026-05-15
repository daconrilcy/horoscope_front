# No Legacy / DRY Guardrails

## Scans

Commandes utilisees:

```powershell
$catalogPattern = "astral_aspect_family\.json|ASPECT_FAMILY_ROWS|ASPECT_ROWS|DEFAULT_ASPECT_ORBS|planet_rows|sign_rows|dignity_type_rows|house_rows"
$constantPattern = "MAJOR_ASPECTS|PLANET_CLASS_BY_CODE|ANGLE_CODES|ANGULAR_HOUSES|SUCCEDENT_HOUSES|DEFAULT_TRADITIONAL_SIGN_RULERSHIPS|_HOUSE_SYSTEM_CODES|MAJOR_ASPECT_CODES"
$helperPattern = "_norm360|_normalize_longitude|_sign_from_longitude|_get_swe_module|_profile_list|_require_list"
rg -n $catalogPattern app tests ../docs -g "*.py" -g "*.md" -g "*.json"
rg -n $constantPattern app tests ../docs -g "*.py" -g "*.md" -g "*.json"
rg -n $helperPattern app tests ../docs -g "*.py" -g "*.md" -g "*.json"
```

Resultat: aucun hit sur les sources actives apres convergence.

## Test garde

`backend/app/tests/unit/test_astrology_reference_catalog_guard.py` formalise ces scans via AST et verification de contenu.
