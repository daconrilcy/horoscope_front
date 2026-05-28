# CS-367 - Bigbang Remplacer Ancien Contrat Prompt Theme Astral Supprimer Legacy

<!-- Commentaire global: ce brief cadre la bascule bigbang vers le nouveau contrat theme astral et la suppression complete du legacy. -->

## Resume

Basculer la feature `theme_astral` en mode bigbang vers le nouveau contrat de construction de prompt et supprimer completement les anciennes surfaces legacy associees.

La story ne doit pas laisser deux chemins runtime durables pour la meme feature.

## Contexte

Le projet veut eviter une coexistence longue entre:

- ancien `llm_astrology_input_v1` prompt-visible pour theme astral;
- vieux prompts natals par plan;
- carriers legacy `chart_json` / `natal_data`;
- schemas de sortie divergents par plan;
- nouveau contrat stable `theme_astral_prompt_v1`.

La bascule doit etre nette, testee et reversible seulement via Git/deploiement, pas via double runtime permanent.

## Objectif

Supprimer l'ancien contrat de prompt pour `theme_astral` et rendre le nouveau chemin unique:

`calculs astrologiques -> interpretation_material -> theme_astral_llm_input_v1 -> provider payload stable -> output_contract`.

## Perimetre inclus

1. Identifier les chemins legacy encore actifs apres CS-366.
2. Supprimer les anciens use cases/prompts/assemblies de `theme_astral` si remplaces.
3. Supprimer ou bloquer les fallbacks legacy pour cette feature.
4. Supprimer les tests/mocks qui valident l'ancien chemin.
5. Mettre a jour les tests d'architecture pour interdire le retour legacy.
6. Mettre a jour les exemples JSON.
7. Mettre a jour la documentation si necessaire.
8. Executer lint/tests.

## Hors perimetre

- Migrer d'autres features que `theme_astral`.
- Ajouter une compatibilite legacy temporaire.
- Appeler un provider LLM.
- Changer les textes metier sauf necessite de migration.

## Sources obligatoires

- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/llm_generation/natal/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/**`
- `_condamad/examples/prompt-generation-cartography/**`
- `_condamad/docs/prompt-generation-cartography/**`

## Criteres d'acceptation

1. Un seul chemin runtime actif existe pour le prompt `theme_astral`.
2. Les carriers legacy `chart_json` et `natal_data` ne peuvent plus alimenter le prompt `theme_astral`.
3. Les anciens prompts par plan ne sont plus utilises pour `theme_astral`.
4. Le plan commercial n'est pas expose au LLM.
5. Les payloads d'exemple ont une structure stable entre delivery profiles.
6. Les tests legacy obsoletes sont supprimes ou remplaces.
7. Les guardrails interdisent la reintroduction de l'ancien chemin.
8. L'app demarre localement ou une commande exacte de demarrage est fournie.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "chart_json|natal_data|llm_astrology_input_v1|natal_interpretation_short|NATAL_SHORT_PROMPT|NATAL_COMPLETE_PROMPT" app tests
rg -n "theme_astral_prompt_v1|theme_astral_llm_input_v1|interpretation_material|delivery_profile|astrologer_voice" app tests
```

Le scan legacy doit etre interprete: les occurrences permises doivent etre uniquement historiques, migrations, audit docs ou guardrails explicitement nommes.

## Risques

Le risque principal est de casser une feature publique sans preuve de remplacement complet. La story doit inclure des tests de bout en bout locaux avec provider double, sans appel externe.
