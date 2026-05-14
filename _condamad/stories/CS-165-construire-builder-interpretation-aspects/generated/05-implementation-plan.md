# Implementation Plan

## Initial repository findings

- Les faits sémantiques d'aspects n'avaient pas de contrat dédié pour alimenter un texte éditorial déterministe.
- Les profils JSON contenaient déjà des dimensions exploitables sans LLM.

## Proposed changes

- Ajouter les contrats de faits et de sortie éditoriale.
- Construire une interprétation déterministe depuis les faits, le runtime et le profil.
- Exporter les nouveaux types via le package d'interprétation.

## Files to modify

- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`
- `backend/app/domain/astrology/interpretation/__init__.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires des facts et du builder éditorial déterministe.

## Risk assessment

- Risque principal: mélange sémantique/editorial. Les contrats séparent facts, provenance et rendu.

## Rollback strategy

- Revenir les nouveaux modules d'interprétation et leurs exports/tests; aucun état persistant.
