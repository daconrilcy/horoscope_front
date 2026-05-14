# Implementation Plan

## Initial repository findings

- Les dimensions métier d'interprétation devaient rester indépendantes de la rédaction finale.
- Aucun couplage LLM n'était nécessaire dans `domain/astrology`.

## Proposed changes

- Isoler les facts sémantiques et axes dans des contrats dédiés.
- Garder le builder éditorial comme consommateur déterministe des facts.
- Ajouter des scans de garde-fous contre les imports prediction/LLM.

## Files to modify

- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires des facts, du builder et scans d'absence de couplage prediction/LLM.

## Risk assessment

- Risque principal: responsabilité floue entre sémantique et éditorial. Couvert par types séparés et tests ciblés.

## Rollback strategy

- Revenir les contrats/facts/builders et tests associés; aucun état externe.
