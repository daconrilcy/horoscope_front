# CS-196 Guard Evidence

## Domain Boundary

Commands:

- `rg -n "INTERPRETATION_RULES|SIGNAL_TYPES|THEME_CODES|PRIORITY_ORDER|ADAPTER_RULES|DOMINANT_MARS_SIGNATURE|HIGH_EXTERNALIZATION_THRESHOLD|CONSTRAINT_ON_ACTION_THRESHOLD" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"`
- `rg -n "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api|from app\\.domain\\.prediction|from app\\.services\\.prediction" backend/app/domain/astrology/interpretation_adapters -g "*.py"`
- `rg -n "OpenAI|AIEngineAdapter|chat\\.completions|\\bprompt\\b|narration|persona|horoscope|matching" backend/app/domain/astrology/interpretation_adapters -g "*.py"`

Result: no hits.

`backend/app/domain/astrology/interpretation_adapters` ne contient pas:

- import SQLAlchemy;
- import infra/services/API;
- import prediction;
- appel LLM;
- texte narratif ou logique UI;
- mapping local de signaux, themes ou priorites.

## Serializer

`json_builder.py::_serialize_interpretation_adapter` projette uniquement le resultat deja present dans `NatalResult`.
