<!-- Evidence runtime CS-194 pour les facteurs de dominance planetaires. -->

# Dominance Runtime Reference

La table `astral_dominance_factor_types` est creee par la migration
`20260519_0132_create_dominance_factor_types.py` et synchronisee par
`sync_astral_dignity_seed_data`.

Facteurs actifs charges pour `1.0.0`, tries par `sort_order`:

| code | label | category | weight | sort_order | active | description |
|---|---|---|---:|---:|---:|---|
| `chart_ruler` | Chart ruler | rulership | 1.20 | 10 | true | Poids du maitre de l'ascendant ou du theme selon les maitrises runtime. |
| `angularity` | Angularity | placement | 1.10 | 20 | true | Proximite factuelle aux angles et maisons angulaires deja calculees. |
| `condition_strength` | Condition strength | condition | 1.00 | 30 | true | Force fonctionnelle issue de PlanetConditionProfile. |
| `visibility` | Visibility | condition | 0.90 | 40 | true | Visibilite issue de PlanetConditionProfile. |
| `most_elevated` | Most elevated | placement | 0.80 | 50 | true | Contribution de la planete la plus elevee ou proche du MC dans les faits natals. |
| `luminary_emphasis` | Luminary emphasis | luminary | 0.80 | 60 | true | Accent factuel Soleil/Lune sans interpretation psychologique. |
| `house_rulership_load` | House rulership load | rulership | 0.75 | 70 | true | Charge de maitrises de maisons depuis NatalResult.house_rulers. |
| `aspect_centrality` | Aspect centrality | aspects | 0.70 | 80 | true | Centralite issue des aspects natals ou de chart_balance.dominant_aspects. |

Validation:

- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` -> PASS apres assertion full-row.
- `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` -> PASS, 5 passed.
