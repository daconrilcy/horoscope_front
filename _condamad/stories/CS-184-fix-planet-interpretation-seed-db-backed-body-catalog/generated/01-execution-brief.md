# Execution Brief

Objectif: corriger le seed des profils d'interprétation planétaire et supprimer les catalogues runtime hardcodés de types de corps astrologiques dans la surface prediction/aspects.

Scope:

- `backend/app/services/reference_data/**`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/domain/prediction/aspect_reference.py`
- `backend/app/domain/prediction/event_detector.py`
- contrats runtime aspects qui exposaient la même constante
- tests unitaires de seed et guardrails

Non-goals:

- Pas de modification du JSON source.
- Pas de refactor large du moteur astrologique.
- Pas de changement frontend.

Guardrails consultés:

- `_condamad/stories/regression-guardrails.md`
- RG-181 implicite via story CS-181: les constantes astrologiques hardcodées supprimées ne doivent pas revenir.
