<!-- Audit avant implementation CS-199 du flux avance de secte. -->

# Advanced Sect Pipeline Before

- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` projetait `hayz` et `out_of_sect` depuis les codes de `accidental_breakdown`.
- `out_of_sect` dependait donc d'un breakdown accidentel, pas directement de `PlanetSectCondition.is_out_of_sect`.
- `hayz` dependait d'un breakdown accidentel complet; l'implementation ne validait pas explicitement `PlanetSectCondition.is_in_sect` comme precondition canonique.
- `condition`, `dominance`, `interpretation_adapters` et `json_builder.py` ne portaient pas d'import de `SectCalculator` ou `PlanetSectConditionCalculator`.
- Aucun changement frontend, API, DB, seed ou migration n'etait requis.

Conclusion: le point de convergence necessaire etait `HayzCalculator`, avec guards de non-recalcul dans les couches aval.
