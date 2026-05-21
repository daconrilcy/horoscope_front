<!-- Brief d'execution CONDAMAD pour CS-205. -->

# CS-205 Execution Brief

## Objectif

Ajouter une suite golden dediee a la triplicite essentielle dependante de la
secte, avec preuves persistantes before/after, sans modifier la doctrine,
les scores, les seeds, les migrations, le JSON public ou le frontend.

## Contraintes

- Le runtime `AstrologyRuntimeReference.dignity_reference.triplicity_rulers`
  reste la source de verite.
- La secte active provient de `ChartSectResult.chart_sect`.
- Les tests ne doivent pas embarquer de table doctrinale locale par element.
- Aucune modification production n'est attendue.
- `RG-132` et les invariants CS-197 a CS-204 restent applicables.

## Done

- AC1 a AC11 couverts par tests, scans et evidence persistante.
- Snapshots `triplicity-golden-before.json` et `triplicity-golden-after.json`
  valides.
- Validation complete en venv.
- Revue finale `CLEAN`.
- Aucun commit/push automatique.

