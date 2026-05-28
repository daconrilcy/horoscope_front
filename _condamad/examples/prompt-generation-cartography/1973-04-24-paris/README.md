# Exemples JSON de prompt natal par plan

Ces fichiers montrent le payload final juste avant handoff provider pour une naissance `1973-04-24`, `Paris, France`, timezone `Europe/Paris`, sur les plans `free`, `basic` et `premium`.

## Methode

- Type de donnees: `synthetic_example`.
- Source de forme: `LLMGateway.compose_structured_messages`, `LLMGateway._call_provider`, `LLMAstrologyInputV1Builder` et la documentation `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`.
- Appel provider: aucun appel n'a ete effectue; `provider_call_performed` vaut `false` dans chaque fichier JSON.
- Les textes exacts de configuration runtime sont representes par des placeholders explicites, car cette story documente la forme du handoff et non une extraction live de configuration.

## Convention de temps

Le brief ne fournit pas d'heure de naissance verifiee. Les exemples utilisent donc `12:00:00` en heure locale `Europe/Paris` comme convention de demonstration. Les maisons, l'Ascendant et le MC ne sont pas verifies et ne doivent pas etre presentes comme calcules.

## Fichiers

- `intermediate-data.json`: entree normalisee, hypotheses, signaux intermediaires, differences de plans et limites.
- `free-provider-payload.json`: payload provider-handoff court, plan `free`.
- `basic-provider-payload.json`: payload provider-handoff intermediaire, plan `basic`.
- `premium-provider-payload.json`: payload provider-handoff approfondi, plan `premium`.

## Frontiere prompt / audit

Le message `user` contient uniquement les blocs prompt-visible `facts`, `signals`, `limits` et `shaping`. Les champs de tracabilite, hash, observability et resultat post-provider restent listes hors prompt dans `audit_excluded_from_prompt`.

Ces exemples ne sont pas une interpretation finale et ne contiennent aucun jeton d'acces, aucune cle API et aucun resultat LLM.
