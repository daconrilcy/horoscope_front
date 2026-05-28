# Exemples JSON theme_astral LLM v1 par profil

Ces fichiers documentent le payload provider `theme_astral_llm_input_v1` pour une naissance le `1973-04-24` a `11:00` a Paris, France.

## Methode de generation

- Generation locale dans le venv via le script evidence `generate_examples.py`.
- Builder reutilise: `ThemeAstralProviderPayloadBuilder`.
- Materiau reutilise: `InterpretationMaterialBuilder` et sources `InterpretationMaterialSource` chargees via `InterpretationMaterialSourceRepository` depuis des tables SQLite locales seedees.
- Nature des sources: mixte. Les familles planetes, maisons et aspects proviennent de profils DB locaux seedes avec des textes production-like representatifs; les familles dominantes, tensions, ressources, leviers et avertissements restent des fixtures production-like explicites car aucune table applicative dediee ne les porte aujourd'hui.
- Contrats runtime: `theme_astral_prompt_v1`, `theme_astral_llm_input_v1`, `theme_astral_response_contract_v1`.
- Aucun appel LLM provider n'est effectue; aucun resultat final de provider n'est produit.

## Livrables

- `intermediate-data.json`: scenario, entree runtime, couverture source et densite.
- `free-provider-payload.json`: payload essentiel, budget court et selection limitee.
- `basic-provider-payload.json`: payload etendu, budget intermediaire.
- `premium-provider-payload.json`: payload complet, budget maximal.
- `structure-comparison.md`: squelette commun et differences de densite.

## Notes de source

- Propriete DB: `astral_planet_interpretation_profiles`, `astral_house_interpretation_profiles`, `astral_aspect_interpretation_profiles`.
- Propriete fixture: `theme_astral_production_like_fixture` pour les sections `dominant_themes`, `tensions`, `resources`, `integration_levers`, et `warnings`.
- Aucun texte fixture n'est presente comme contenu production reel; la couverture source dans `intermediate-data.json` indique le mixte DB locale seedee / production-like.

Le runtime actuel expose le contexte de naissance structure dans `input_data.birth_context`: `birth_date`, `birth_time_local`, `birth_place`, les coordonnees disponibles et les flags de precision. `chart_id` reste un identifiant technique; le scenario complet est aussi persiste dans `intermediate-data.json` pour rendre la date, l'heure et le lieu auditables sans modifier les payloads provider.
