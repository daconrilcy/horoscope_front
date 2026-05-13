# Priorite 3 : Runtime astrologique riche des maisons

## Objectif

Transformer les maisons natales en objets runtime complets et interpretables,
sans creer de table SQL ni persister une structure astrologique dynamique.

## Acceptance Criteria

- Chaque maison runtime expose `cusp_sign`, `contained_signs`,
  `intercepted_signs`, `ruler`, `occupants`, `axis` et `strength`.
- Les systemes Whole Sign ne produisent aucune interception.
- Les systemes quadrant detectent les interceptions quand une maison contient
  un signe absent des cuspides courante et suivante.
- `chart_results.result_payload.houses[]` expose les maisons enrichies.
- Le champ public `sign` reste expose comme compatibilite explicite vers
  `cusp_sign`.
- Les rulers restent issus de la source canonique `sign_rulerships`, chargee
  depuis `astral_planet_sign_dignities`.
- Aucune table SQL, migration ou persistance relationnelle de cuspides
  detaillees n'est ajoutee.
- Des tests couvrent contained signs, intercepted signs, house strength,
  builder runtime et scenarios golden.

## Non-objectifs

- Ne pas refaire SwissEph.
- Ne pas modifier les calculs astronomiques.
- Ne pas changer les systemes de maisons.
- Ne pas creer de moteur predictif.
- Ne pas ajouter de tables SQL.
- Ne pas modifier le moteur daily.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`.
- Applicable invariants:
  - `RG-091` a `RG-093`: les referentiels astrologiques restent canoniques et
    les maitrises de signes viennent des dignites planete-signe.
- Required regression evidence:
  - tests unitaires de domaine astrologie;
  - scan cible confirmant qu'aucune migration/table SQL maison runtime n'est
    ajoutee.
