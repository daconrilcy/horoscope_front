# Implementation Plan - CS-208

## Architecture Finding

Les contrats astrologiques voisins utilisent des `dataclass(frozen=True,
slots=True)` et des docstrings francaises. Aucun package
`planetary_conditions` n'existe avant cette story.

## Selected Approach

Creer un module contractuel autonome avec uniquement des imports de la standard
library: `dataclasses`, `enum`, `types` et `typing`.

## Patch Plan

1. Ajouter les enums `StrEnum` et les dataclasses immutables dans
   `contracts.py`.
2. Exporter explicitement les symboles publics dans `__init__.py`.
3. Ajouter un test unitaire qui couvre import, valeurs enum, immutabilite,
   bundle partiel, resultat multi-planetes, metadata read-only et annotations.
4. Capturer baseline, scans et validation dans `evidence/validation.md`.
5. Completer l'evidence finale et passer le statut story en review/done apres
   revue.

## No Legacy Stance

Aucun shim, alias, fallback, re-export legacy ou compatibilite n'est autorise.

## Rollback Strategy

Supprimer uniquement les nouveaux fichiers CS-208 et revenir au statut
`ready-to-dev` si un blocker apparait avant validation.
