# CS-373 - Structurer Birth Context Theme Astral LLM Input V1

<!-- Commentaire global: ce brief cadre l'ajout d'un contexte de naissance structure dans le payload LLM theme astral. -->

## Resume

Faire evoluer `input_data.birth_context` pour exposer au LLM un contexte de naissance clair et structure, au lieu de porter date, heure et lieu principalement dans `chart_id`.

## Contexte

La revue a constate que `birth_context` contient seulement:

- `chart_id`;
- `locale`;
- `chart_type`.

Pourtant les exemples et la documentation attendent un contexte de naissance normalise. Un `chart_id` lisible par humain est insuffisant comme contrat stable: il oblige le LLM a parser une chaine alors que le backend possede ou peut reconstruire les champs utiles.

## Objectif

Ajouter a `input_data.birth_context` les champs normalises utiles a la redaction:

- date de naissance;
- heure locale;
- lieu;
- pays;
- timezone;
- latitude/longitude si disponibles;
- indicateur de precision ou de donnees manquantes;
- `chart_id` conserve comme identifiant technique non sensible si necessaire.

## Perimetre inclus

1. Lire `ChartInterpretationInputRuntimeData` et les builders amont.
2. Identifier la source correcte des donnees de naissance.
3. Ajouter les champs au contrat runtime si necessaire.
4. Adapter `_birth_context` dans le provider payload builder.
5. Adapter `THEME_ASTRAL_INPUT_SCHEMA` si le schema d'entree versionne porte les sous-cles.
6. Adapter les tests de payload et d'exemples.
7. Regenerer les exemples CS-371.
8. Mettre a jour la documentation de structure JSON.

## Hors perimetre

- Modifier le calcul astrologique.
- Changer la precision astronomique des exemples.
- Appeler un provider LLM.
- Ajouter des donnees personnelles inutiles au LLM.

## Sources obligatoires

- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`

## Structure cible indicative

```json
{
  "chart_id": "birth:1973-04-24 11:00 Europe/Paris Paris France",
  "birth_date": "1973-04-24",
  "birth_time_local": "11:00",
  "birth_place": {
    "city": "Paris",
    "country": "France",
    "timezone": "Europe/Paris",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "precision": {
    "birth_time_known": true,
    "coordinates_known": true
  },
  "locale": "fr-FR",
  "chart_type": "natal"
}
```

## Criteres d'acceptation

1. `birth_context` ne force plus le LLM a parser `chart_id`.
2. Les champs date, heure, ville, pays et timezone sont visibles dans les payloads exemples.
3. Les coordonnees sont incluses uniquement si disponibles et utiles.
4. Les absences sont explicites dans `birth_context.precision` ou `input_data.limits`.
5. Les tests prouvent la presence du contexte structure.
6. Les exemples du 24/04/1973 a 11:00 Paris sont regeneres et valides.
7. La documentation ne dit plus que le scenario complet est uniquement dans `intermediate-data.json`.
8. Le schema versionne documente ou valide les champs de `birth_context`.
9. Les champs personnels restent minimises: aucune donnee utilisateur inutile au theme astral n'est ajoutee.

## Commandes de validation minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short
```

Scans exemples:

```powershell
rg -n "birth_date|birth_time_local|birth_place|Europe/Paris|Paris|France|1973-04-24|11:00" ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1
rg -n "scenario complet.*intermediate|chart_id" ..\_condamad\docs\prompt-generation-cartography\theme-astral-llm-json-structure-v1.md ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\README.md
```

Le premier scan doit trouver les champs structures dans les payloads provider. Le second doit etre interprete: `chart_id` peut rester comme identifiant, mais la documentation ne doit plus dire que la date, l'heure et le lieu sont seulement auditables via `intermediate-data.json`.

## Risques

Le risque principal est d'ajouter des champs de naissance sans owner clair. Les donnees doivent venir du contrat runtime ou d'une projection explicite, pas d'un parsing opportuniste de `chart_id`.
