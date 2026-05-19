# Execution Brief CS-191

Objectif: construire le moteur backend de dignites planetaires avance, base sur
`AstrologyRuntimeReference.dignity_reference`, puis exposer `dignities` dans le
payload natal.

Bornes:

- In scope: runtime reference, calculateurs purs `domain/astrology/dignities`,
  integration `NatalResult`, projection JSON, tests et guards.
- Out of scope: frontend, LLM, interpretation editoriale, persistance
  `astral_chart_planet_dignity_results`.
- Statut source: full story non-audit, pas de finding audit a fermer.

Correction post-revue: la couverture stricte de l'expression de besoin a ete
renforcee apres audit. Le runtime expose maintenant aussi les inventaires
`essential_types`, `accidental_types`, `term_systems` et `decan_systems`; les
breakdowns portent une `reason`; `peregrine` est ajoute quand aucune dignite
essentielle positive n'est detectee; les tests couvrent explicitement
`exaltation`, `detriment` et `fall`.

Done: AC1-AC8 couverts par tests cibles, scans RG-118 zero-hit, snapshots
payload avant/apres et evidence runtime persistés.
