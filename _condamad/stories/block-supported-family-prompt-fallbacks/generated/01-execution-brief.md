# Execution Brief - block-supported-family-prompt-fallbacks

## Primary objective

Supprimer `PROMPT_FALLBACK_CONFIGS` comme proprietaire runtime concurrent pour les cles supportees explicitement interdites: `chat`, `chat_astrologer`, `guidance_contextual`, `natal_interpretation`, `horoscope_daily`.

## Boundaries

- Scope code: `backend/app/domain/llm/prompting`, `backend/app/domain/llm/runtime`, tests LLM orchestration.
- Ne pas modifier les routes QA 70.16, les prompts publies, le catalogue admin ou les seeds d'assembly.
- Ne pas ajouter de dependance.

## Write rules

- Supprimer les entrees fallback interdites au lieu de les masquer.
- Conserver seulement les exceptions exactes documentees dans `fallback-exception-audit.md`.
- Ajouter des tests qui echouent si les cles interdites reviennent.
- Les commandes Python doivent etre lancees apres `.\.venv\Scripts\Activate.ps1`.

## Done conditions

- AC1-AC4 ont une preuve code et validation.
- Les scans classent tous les hits restants.
- `generated/10-final-evidence.md` est complet.
