# Audit des exceptions fallback prompts

Ce fichier documente les exceptions conservees dans `PROMPT_FALLBACK_CONFIGS`
apres suppression des prompts runtime pour les familles supportees explicites.

## Interdictions verifiees

Les cles suivantes ne doivent pas exister dans `PROMPT_FALLBACK_CONFIGS`:

- `chat`
- `chat_astrologer`
- `guidance_contextual`
- `natal_interpretation`
- `horoscope_daily`

## Exceptions conservees

| Cle | Classification | Justification |
|---|---|---|
| `natal_long_free` | bootstrap borne | Cas free historique hors cle premium interdite, conserve comme exception exacte. |
| `natal_interpretation_short` | bootstrap borne | Cible de bootstrap non-prod existante pour l'interpretation courte. |
| `guidance_daily` | bootstrap borne | Cas guidance quotidien conserve hors cle contextual interdite. |
| `guidance_weekly` | bootstrap borne | Cas guidance hebdomadaire conserve hors cle contextual interdite. |
| `event_guidance` | bootstrap borne | Cas evenementiel distinct de `guidance_contextual`. |
| `astrologer_selection_help` | bootstrap borne | Cas support distinct de la famille chat astrologer interdite. |
| `test_natal` | fixture synthetique | Use case reserve aux tests d'orchestration. |
| `test_guidance` | fixture synthetique | Use case reserve aux tests d'orchestration. |

## Garde executable

`backend/tests/llm_orchestration/test_prompt_governance_registry.py` verifie que
l'ensemble des exceptions est exactement celui liste ci-dessus. Toute nouvelle
cle fallback doit donc etre explicitement ajoutee a cet audit et au test associe.
