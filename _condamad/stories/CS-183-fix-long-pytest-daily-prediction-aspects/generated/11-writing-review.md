# Writing Review

Date: 2026-05-18

## Cycle 1

Findings:

- `03-acceptance-traceability.md` contenait encore des placeholders de completion
  alors que `10-final-evidence.md` déclarait la story prête pour revue.
- `00-story.md` mélangeait `daily`, `quotidiennes` et des formulations longues
  sur un même critère d'acceptation.
- Le plan de validation parlait d'une vérification complète à lancer alors que
  l'evidence finale indiquait déjà que `pytest -q --long` était passé.
- La casse du statut final n'était pas alignée avec `story-status.md`.

Corrections:

- Remplacement des placeholders par une traçabilité AC complète et vérifiable.
- Clarification des critères d'acceptation: un invariant par ligne, avec séparation
  explicite du cas `reference_version_id` et du cas des doubles de test.
- Harmonisation de la terminologie française pour les prédictions quotidiennes.
- Alignement du plan de validation et du statut final sur l'evidence disponible.

## Cycle 2

Findings:

- Quelques lignes dépassaient encore une longueur confortable de relecture.
- Deux formulations restaient au présent de progression alors que la story est en
  `ready-to-review`.
- Les guardrails No Legacy ne couvraient pas explicitement le risque de second
  chemin de chargement des profils d'aspects.

Corrections:

- Repli des lignes longues dans les fichiers générés.
- Passage des formulations de progression en formulation de résultat.
- Ajout d'un guardrail contre la duplication du chargement des profils d'aspects.

## Verdict final

Aucune erreur rédactionnelle restante identifiée après le second cycle de revue.
