# Tables `astral_point_*`

Ce document décrit le contrat runtime des points astraux natals.

## Source canonique

Les familles, points, variantes, alias, mots-clés et profils éditoriaux viennent des tables `astral_point_*` alimentées par les JSON sous `docs/db_seeder/astrology/`. Le runtime natal consomme ces données via `AstrologyRuntimeReferenceRepository`, qui les convertit en dataclasses immutables.

## Contrat runtime

`AstrologyRuntimeReference.astral_points.items` expose des `AstralPointRuntime` avec variantes et alias typés. Pour le chargement ciblé, `AstrologyRuntimeReferenceRepository.load_astral_points()` retourne directement un `AstralPointReferenceSet` et ne laisse pas sortir de dictionnaires bruts du contrat runtime. Le calcul natal sélectionne la variante par défaut, résout une instruction via `AstralPointCalculationResolver`, puis publie les positions dans `NatalResult.astral_points[]`.

Chaque entrée `astral_points[]` contient :

- `code`
- `variant_code`
- `longitude`
- `sign`
- `degree_in_sign`
- `house`
- `calculation_source`

Le contrat runtime peut conserver `is_physical_body` pour les consommateurs internes, mais aucun champ interprétatif (`summary`, `keywords`, `micro_note`, `prompt_hints`) ne doit être présent dans `NatalResult.astral_points[]`. Aucun champ plat `true_node`, `mean_node` ou `lilith` n'est exposé.

Exemple de contrat JSON natal :

```json
{
  "astral_points": [
    {
      "code": "north_node",
      "variant_code": "true",
      "longitude": 123.45,
      "sign": "leo",
      "degree_in_sign": 3.45,
      "house": 8,
      "calculation_source": "swiss_ephemeris:SE_TRUE_NODE"
    }
  ]
}
```

## Points canoniques et variantes

Un point canonique représente l'objet métier stable, par exemple `north_node`, `lunar_apogee` ou `black_moon_lilith`. Une variante représente le mode de calcul appliqué à ce point, par exemple `mean` ou `true`.

`true_node` et `mean_node` ne sont pas des champs de résultat : ce sont des variantes de `north_node` ou `south_node`. De même, `Lilith` reste `black_moon_lilith`, avec une variante `mean` ou `true`.

## Calculs directs et dérivés

Les variantes directes utilisent une clé moteur SwissEph portée par les alias DB seedés. Si une clé moteur directe est absente, le resolver échoue explicitement. Les variantes dérivées appliquent un offset explicite de 180 degrés via `opposite_longitude(longitude)`.

Règles de calcul :

- `north_node` + `true` -> `SE_TRUE_NODE`
- `north_node` + `mean` -> `SE_MEAN_NODE`
- `south_node` + `true` -> opposition de `north_node` + `true`
- `south_node` + `mean` -> opposition de `north_node` + `mean`
- `lunar_apogee` + `mean` -> `SE_MEAN_APOG`
- `lunar_apogee` + `true` -> `SE_OSCU_APOG`
- `lunar_perigee` + `mean` -> opposition de `lunar_apogee` + `mean`
- `lunar_perigee` + `true` -> opposition de `lunar_apogee` + `true`
- `black_moon_lilith` + `mean` -> `SE_MEAN_APOG`
- `black_moon_lilith` + `true` -> `SE_OSCU_APOG`

Les points astraux sont placés en maison. Ils ne participent pas aux aspects par défaut. Le calcul d'aspects avec points astraux exige l'option explicite `include_points_in_aspects=True`.

## Interprétation

Le calcul natal brut ne charge pas les keywords ni les profils éditoriaux. Ces données restent réservées au couple `AstralPointInterpretationRepository` et `AstralPointInterpretationEnricher`, qui assemble une `NatalAstralPointPosition`, un `AstralPointInterpretationProfile` et ses `AstralPointInterpretationKeywords` sans mélanger calcul astronomique et contenu éditorial.

La frontière est stricte :

- `NatalResult` = positions objectives.
- `InterpretationContext` = positions + sens éditorial.
- prompt LLM = contexte interprétatif séparé, jamais DB brute.
