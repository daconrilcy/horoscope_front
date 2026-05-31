# Baseline apres implementation CS-409

<!-- Commentaire global: preuve finale des surfaces apres ajout des contrats Basic V2. -->

- Story: `CS-409-contrats-versionnes-lecture-natale-basic-v2`
- Date: `2026-05-31`
- Delta attendu present:
  - `backend/app/domain/astrology/reading/basic_natal_contracts.py`
  - `backend/app/domain/astrology/reading/__init__.py`
  - `backend/app/services/api_contracts/public/natal_interpretation.py`
  - `backend/docs/basic-natal-reading-v2-contract.md`
  - `backend/docs/ownership-index.md`
  - `backend/tests/unit/test_basic_natal_reading_contracts.py`
  - `backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py`
  - `_condamad/stories/regression-guardrails.md`
- Identite runtime importee: `from app.main import app` depuis `backend/` retourne `230`
  routes chargees, sans ajout de route par cette story.
- Denylist publique: le scan des surfaces Basic V2 retourne uniquement les literals de garde
  du nouveau contrat et le validateur narratif public existant.
- Invariant durable ajoute: `RG-168` pour `basic_natal_interpretation_v2`.
- Statut final attendu tracker: `ready-to-review`.
