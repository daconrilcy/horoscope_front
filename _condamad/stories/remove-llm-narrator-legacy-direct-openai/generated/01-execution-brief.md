# Execution Brief

## Story key

`remove-llm-narrator-legacy-direct-openai`

## Primary objective

Supprimer la surface executable `LLMNarrator` et tout appel provider direct hors provider canonique, tout en conservant le contrat narratif utile via un module canonique.

## Boundaries

- Domaine cible: `backend/app/services/llm_generation/horoscope_daily`.
- Point d'entree applicatif attendu: `AIEngineAdapter.generate_horoscope_narration`.
- Contrat narratif autorise: module canonique sous `app.domain.llm.prompting`.
- Aucun changement frontend, route API, OpenAPI ou dependance.

## Non-goals

- Ne pas recreer `app.services.ai_engine_adapter`.
- Ne pas remettre la logique narrative dans `AIEngineAdapter`.
- Ne pas changer les schemas narratifs publics.
- Ne pas renommer le flag de configuration `llm_narrator_enabled` dans cette story.

## Preflight checks

- Lire `AGENTS.md`.
- Capturer `git status --short`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer l'inventaire avant des symboles `LLMNarrator`, `llm_narrator`, `openai.AsyncOpenAI` et `chat.completions.create`.

## Write rules

- Supprimer la facade legacy au lieu de la repointer.
- Migrer les imports actifs vers le contrat canonique.
- Garder les tests nominaux sur `AIEngineAdapter.generate_horoscope_narration`.
- Ajouter une garde deterministe contre le retour du provider direct hors provider canonique.

## Done conditions

- `LLMNarrator` n'est plus importable comme surface runtime.
- Les tests de migration passent par l'adaptateur canonique.
- Les scans directs provider ne trouvent aucun appel hors provider canonique.
- La trace AC et l'evidence finale sont completes.

## Halt conditions

- Une dependance externe nominale a `LLMNarrator` est prouvee.
- Un test requis echoue sans correctif scoped evident.
- La suppression impose un changement API ou schema hors scope.
