# Writing Review

Date: 2026-05-20

## Cycle 1

Findings:

- `00-story.md` annonçait un domaine unique strict tout en incluant la
  projection JSON hors `backend/app/domain/astrology`, ce qui rendait le
  périmètre d'exécution ambigu.
- La règle de baseline ne distinguait pas clairement un vrai snapshot runtime
  d'un marqueur valide indiquant l'absence de suite golden préalable.
- AC9 protégeait les fichiers de production, mais pas les helpers de test
  contre la réintroduction de doctrine locale.
- AC10 demandait d'enregistrer `zero changes`, alors que la story doit créer
  des tests et de l'evidence.
- Le plan de validation ne lançait pas `test_hayz_calculator.py`, pourtant
  directement lié aux invariants hayz/out-of-sect.

Corrections:

- Clarification du périmètre: domaine primaire unique, avec validation des
  surfaces de projection documentées.
- Clarification du `golden-cases-before.json`: snapshot réel si une suite
  existe, sinon marqueur JSON valide d'absence de baseline préalable.
- Extension d'AC9 et des scans aux surfaces de test concernées.
- Reformulation d'AC10 pour viser zéro changement interdit, pas zéro changement
  total.
- Ajout de `test_hayz_calculator.py` aux fichiers à inspecter, aux tests
  probables et au plan de validation.

## Cycle 2

Findings:

- Après correction, la règle `before/after must match` restait trop absolue si
  le fichier before est un marqueur d'absence et non un snapshot runtime.
- Les scans étendus aux tests pouvaient signaler des données explicites de
  fixture, sans distinguer ces hits d'une table doctrinale locale réutilisable.

Corrections:

- Restriction de la règle de comparaison aux cas où before et after sont tous
  deux des snapshots runtime.
- Ajout d'une règle de classification: les hits dans les fixtures de test sont
  acceptables seulement s'ils sont documentés comme données explicites par cas,
  pas comme tables doctrinales ou helpers de recalcul.

## Cycle 3

Findings:

- Aucune issue rédactionnelle bloquante restante identifiée.

Corrections:

- Aucune correction supplémentaire requise.

## Verdict final

Aucune issue rédactionnelle restante identifiée après le troisième cycle de
review.
