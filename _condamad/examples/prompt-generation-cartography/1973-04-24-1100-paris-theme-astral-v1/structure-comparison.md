# Comparaison des structures provider theme_astral

## Squelette commun

Les trois payloads partagent les memes cles de premier niveau:

```json
[
  "runtime_contract",
  "safety_contract",
  "astrologer_voice",
  "feature_context",
  "delivery_profile",
  "input_data",
  "output_contract"
]
```

Les trois payloads partagent les memes cles `input_data`:

```json
[
  "birth_context",
  "astrological_facts",
  "interpretation_material",
  "selected_themes",
  "limits"
]
```

## Differences de densite

| Profil backend | depth LLM-visible | objets | aspects | sections selectionnees | max sections sortie | max output tokens |
|---|---:|---:|---:|---:|---:|---:|
| free | essential | 3 | 1 | 4 | 4 | 1400 |
| basic | expanded | 6 | 3 | 6 | 6 | 2400 |
| premium | complete | 7 | 6 | 8 | 8 | 3600 |

Les differences restent portees par `delivery_profile`, les budgets, les selections et `output_contract`. Les etiquettes commerciales sont les noms de fichiers et ne sont pas presentes comme valeurs dans le contenu JSON transmis au LLM.
