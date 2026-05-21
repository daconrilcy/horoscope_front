# Execution Brief

## Story

- Key: CS-206-benefic-malefic-sect-mitigation-signals
- Objective: exposer des faits runtime-backed de mitigation/aggravation des benefiques et malefiques par la secte.

## Boundaries

- Modifier uniquement le domaine `backend/app/domain/astrology/advanced_conditions`, les seeds runtime avances, la projection JSON serialize-only, les tests backend et les preuves CS-206.
- Ne pas modifier les calculateurs de secte, dignites essentielles/accidentelles, routes API, migrations ou frontend sauf preuve d'insuffisance d'affichage.
- Les natures planetaires viennent de `AstrologyRuntimeReference.planet_natures`; la condition de secte vient de `PlanetSectCondition`.

## Write Rules

- Aucun mapping local de planetes benefiques/malefiques.
- Aucun branchement production sur Mars, Saturne, Jupiter ou Venus par nom.
- Aucun recalcul dans `json_builder.py`.
- Aucun fallback silencieux, alias legacy ou compatibilite.

## Done Conditions

- Contrat `SectNatureMitigationCondition` immutable.
- Detecteur pur avec tests pour benefique/malefique, in/out of sect, neutral/unknown et absence sans secte.
- Integration `AdvancedConditionEngine` via poids runtime `sect_nature_mitigation`.
- Projection JSON des faits pre-calcules dans `traditional_conditions`.
- Evidence before/after, validation et scans anti-retour.
- Story status synchronise apres revue.

## Halt Conditions

- Runtime planet nature indisponible sans contrat source.
- AC contradictoires avec les guardrails RG-124 a RG-133.
- Validation cible echoue sans correction sure dans le scope.
