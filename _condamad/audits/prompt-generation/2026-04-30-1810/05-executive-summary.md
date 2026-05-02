# Executive Summary - prompt-generation - 2026-04-30-1810

Le processus de generation de prompts est largement converge vers `AIEngineAdapter` puis `LLMGateway`: `natal`, `chat`, `horoscope_daily` nominal et `consultation specifique` via `guidance_contextual` utilisent les contrats typés et la resolution assembly/profile.

Les risques principaux ne sont pas dans la couche API: aucun import FastAPI/API n'a ete detecte dans le domaine audite. Les ecarts concernent plutot l'ownership de prompt et les surfaces legacy encore executable.

Complement BMAD 70: l'audit du 2026-04-21 et les stories 70.1-70.23 confirment que la migration de namespaces est deja couverte: `application/llm`, `domain/llm`, `infrastructure` et `ops/llm` sont la cible; `llm_orchestration`, `app.prompts` et `legacy_prompt_runtime` ne sont plus des points d'entree nominaux. L'audit du 2026-04-30 doit donc etre lu comme une verification des bords executables de la chaine, pas comme une remise en cause du socle 70.15.

Synthese des findings:

- High: 2
- Medium: 2
- Info: 2
- Story candidates: 4

Risques prioritaires:

1. `LLMNarrator` reste un chemin direct OpenAI executable pour `horoscope_daily`, alors que le registre legacy le classe comme candidat au retrait.
2. `PROMPT_FALLBACK_CONFIGS` contient encore des prompts executables pour les familles supportees, en doublon des assemblies.
3. Le prompt quotidien le plus structurant est construit dans `app.prediction` comme `question`, hors gouvernance assembly.
4. La consultation specifique n'a pas de taxonomie LLM propre; elle reutilise `guidance_contextual`, ce qui necessite une decision explicite.

Couverture confirmee:

- Admin prompts: routes dediees, catalogue, edition, historisation, rollback, release, consumption, audit et couches observables sont couverts par 70.1-70.12.
- Runtime backend: namespaces canoniques, renderer/persona/contracts/configuration/gouvernance/ops sont couverts par 70.14-70.15 et l'audit du 2026-04-21.
- Recette: doc, seed QA, routes internes et tests guidance/chat/natal/horoscope sont couverts par 70.16.
- Adapter/services: garde-fous DRY et anti-legacy sont couverts par 70.20-70.21.

Action recommandee: traiter d'abord F-001 et F-002 pour fermer les chemins legacy/dupliques, puis clarifier l'ownership de `horoscope_daily` et des consultations. Les corrections doivent reutiliser les harness BMAD 70 existants et ne pas recreer de shim, mini-pipeline QA ou source admin parallele.
