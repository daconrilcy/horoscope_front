# Exemples JSON de payload provider theme_astral

Ces fichiers montrent le payload provider canonique `theme_astral_prompt_v1` juste avant handoff provider pour une naissance `1974-04-24`, `11:00:00`, `Paris, France`, timezone `Europe/Paris`.

## Methode

- Type de donnees: `theme_astral_llm_input_v1`.
- Builder: `ThemeAstralProviderPayloadBuilder`, sans provider LLM.
- Contrat prompt: `theme_astral_prompt_v1`.
- Les profils commerciaux backend `free`, `basic` et `premium` changent les budgets et valeurs via `delivery_profile`; ils ne changent pas le squelette JSON provider.

## Donnees utilisateur rejouees

- Date: `1974-04-24`.
- Heure locale: `11:00:00`.
- Lieu: `Paris, France`.
- Coordonnees utilisees: latitude `48.8566`, longitude `2.3522`.
- Normalisation temporelle: `1974-04-24T11:00:00+01:00` vers `1974-04-24T10:00:00+00:00`.
- Systeme de maisons: Placidus.

## Fichiers

- `intermediate-data.json`: entree normalisee, calculs locaux, signaux intermediaires, differences de plans et limites.
- `free-provider-payload.json`: payload provider-handoff profil essentiel.
- `basic-provider-payload.json`: payload provider-handoff profil etendu.
- `premium-provider-payload.json`: payload provider-handoff profil complet.

## Frontiere prompt / audit

Le payload provider contient toujours `runtime_contract`, `safety_contract`, `astrologer_voice`, `feature_context`, `delivery_profile`, `input_data` et `output_contract`. Les anciens carriers `chart_json`, `natal_data` et `llm_astrology_input_v1` ne sont pas des inputs prompt-visible pour `theme_astral`.

Ces exemples ne sont pas une interpretation finale et ne contiennent aucun jeton d'acces, aucune cle API et aucun resultat LLM.
