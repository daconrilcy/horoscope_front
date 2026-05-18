# Tables `astral_point_*`

Ce document décrit le contrat runtime des points astraux natals.

## Source canonique

Les familles, points, variantes, alias, mots-clés et profils éditoriaux viennent des tables `astral_point_*` alimentées par les JSON sous `docs/db_seeder/astrology/`. Le runtime natal consomme ces données via `AstrologyRuntimeReferenceRepository`, qui les convertit en dataclasses immutables.

## Contrat runtime

`AstrologyRuntimeReference.astral_points.items` expose des `AstralPointRuntime` avec variantes et alias typés. Pour le chargement ciblé, `AstrologyRuntimeReferenceRepository.load_astral_points()` retourne directement un `AstralPointReferenceSet` et ne laisse pas sortir de dictionnaires bruts du contrat runtime. Le calcul natal sélectionne la variante par défaut, résout une instruction via `AstralPointCalculationResolver`, puis publie les positions dans `NatalResult.points[]`.

Chaque entrée `points[]` contient `code`, `variant_code`, `longitude`, `sign`, `degree_in_sign`, `house` et `is_physical_body`. Aucun champ plat `true_node`, `mean_node` ou `lilith` n'est exposé.

## Calculs directs et dérivés

Les variantes directes utilisent une clé moteur SwissEph portée par les alias DB seedés. Si une clé moteur directe est absente, le resolver échoue explicitement. Les variantes dérivées appliquent un offset explicite de 180 degrés: `south_node` depuis `north_node`, et `lunar_perigee` depuis `lunar_apogee`.

## Interprétation

Le calcul natal brut ne charge pas les keywords ni les profils éditoriaux. Ces données restent réservées au couple `AstralPointInterpretationRepository` et `AstralPointInterpretationEnricher`, qui assemble une `NatalAstralPointPosition`, un `AstralPointInterpretationProfile` et ses `AstralPointInterpretationKeywords` sans mélanger calcul astronomique et contenu éditorial.
