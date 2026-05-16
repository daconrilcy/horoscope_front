# Validation Plan - CS-174

Toutes les commandes Python doivent etre lancees apres activation du venv.

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py
pytest -q app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py
pytest -q app/tests/unit/test_astrology_localization_guardrails.py
$hits = rg -n "SIGN_NAMES_FR|\bSIGNS\s*=\s*\[|SIGN_LABELS" app/services -g "*.py"; $bad = @($hits | Where-Object { $_ -notmatch "app[\\/]services[\\/]natal[\\/]pdf_export_service.py" }); if ($bad.Count -gt 0) { $bad; exit 1 }
rg -n "AstrologyTranslationResolver|astrology_translation_resolver|translated_name|LanguageModel" app/domain/astrology
```
