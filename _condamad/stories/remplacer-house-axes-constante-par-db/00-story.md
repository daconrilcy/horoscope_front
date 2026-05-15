# Remplacer la constante d'axes de maisons par les tables DB

## Goal

Remplacer l'usage runtime de `backend/app/domain/astrology/constants/house_axes.py` par les tables `astral_house_axis_members` et `astral_house_axis_definitions`.

## Context

Les tables `astral_house_axis_members` et `astral_house_axis_definitions` ont ete creees pour porter les axes astrologiques canoniques auparavant codes en dur.

## Acceptance Criteria

- AC1: Le runtime des maisons lit les axes depuis les donnees de reference chargees depuis les tables DB, sans appel actif a `HOUSE_AXES` ou `resolve_house_axis`.
- AC2: Les donnees exposees au calcul natal contiennent, pour chaque maison, la maison opposee et la cle d'axe issue des tables canoniques.
- AC3: L'absence ou l'incompletude des axes dans les donnees de reference echoue explicitement au lieu d'utiliser une constante ou un fallback silencieux.
- AC4: Les tests cibles couvrent le repository, le builder runtime et la validation d'erreur sans lancer de suite globale.
- AC5: Les scans No Legacy prouvent qu'aucun consommateur actif n'utilise encore `house_axes.py`, `HOUSE_AXES` ou `resolve_house_axis`.

## Constraints

- Backend uniquement.
- Pas de tests globaux; uniquement les tests cibles lies aux modifications.
- Toutes les commandes Python doivent etre lancees apres activation de `.\.venv\Scripts\Activate.ps1`.
- Ne pas creer de nouveau dossier racine sous `backend/`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - la surface touche `backend/app/domain/astrology/**`; elle ne doit pas importer prediction.
  - `RG-106` - les referentiels astrology doivent rester issus de sources DB/JSON canoniques, sans anciennes constantes ou fallbacks silencieux.
- Required regression evidence:
  - Tests cibles du runtime et repository.
  - Scans cibles des anciens symboles et des imports prediction interdits.
- Allowed differences: suppression du chemin constant en dur pour les axes de maisons.

