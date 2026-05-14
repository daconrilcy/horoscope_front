# Implementation Plan

## Initial repository findings

- Les candidats sémantiques devaient être priorisés avec provenance explicite plutôt que par ordre implicite.
- Les sources inconnues devaient être refusées dans les facts produits.

## Proposed changes

- Ajouter les contrats de provenance et candidat sémantique.
- Prioriser les candidats par autorité, confiance et ordre source.
- Intégrer la provenance dans les facts d'interprétation.

## Files to modify

- `backend/app/domain/astrology/interpretation/aspect_semantic_provenance.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py`
- `backend/app/domain/astrology/interpretation/__init__.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires de provenance, priorisation et construction de facts.

## Risk assessment

- Risque principal: accepter une provenance inconnue ou non déterministe. Couvert par validation et tests de tri.

## Rollback strategy

- Revenir les modules provenance/facts et tests associés; aucune migration.
