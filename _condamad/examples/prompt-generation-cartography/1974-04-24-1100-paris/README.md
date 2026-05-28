# Exemples JSON de prompt natal par plan

Ces fichiers montrent le payload final juste avant handoff provider pour une naissance `1974-04-24`, `11:00:00`, `Paris, France`, timezone `Europe/Paris`, sur les plans `free`, `basic` et `premium`.

## Methode

- Type de donnees: `runtime_generated_ephemeris_prompt_fixture`.
- Calcul local: positions, maisons, Ascendant, MC et aspects calcules avec `pyswisseph` dans le venv Python, sans provider LLM.
- Prompts: les templates seed `NATAL_SHORT_PROMPT`, `NATAL_COMPLETE_PROMPT` et `NATAL_COMPLETE_PROMPT_V3` ont ete rendus avec `locale`, `use_case`, `persona_name` et `llm_astrology_input_v1` remplaces par leurs valeurs.
- Appel provider: aucun appel n'a ete effectue; `provider_call_performed` vaut `false` dans chaque fichier JSON.

## Donnees utilisateur rejouees

- Date: `1974-04-24`.
- Heure locale: `11:00:00`.
- Lieu: `Paris, France`.
- Coordonnees utilisees: latitude `48.8566`, longitude `2.3522`.
- Normalisation temporelle: `1974-04-24T11:00:00+01:00` vers `1974-04-24T10:00:00+00:00`.
- Systeme de maisons: Placidus.

## Fichiers

- `intermediate-data.json`: entree normalisee, calculs locaux, signaux intermediaires, differences de plans et limites.
- `free-provider-payload.json`: payload provider-handoff court, plan `free`.
- `basic-provider-payload.json`: payload provider-handoff intermediaire, plan `basic`.
- `premium-provider-payload.json`: payload provider-handoff approfondi, plan `premium`.

## Frontiere prompt / audit

Le message `user` contient uniquement les blocs prompt-visible `facts`, `signals`, `limits` et `shaping`. Les champs `evidence`, `provenance`, hash, observability, replay et resultat post-provider restent listes hors prompt dans `audit_excluded_from_prompt`.

Ces exemples ne sont pas une interpretation finale et ne contiennent aucun jeton d'acces, aucune cle API et aucun resultat LLM.
