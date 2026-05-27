# Implementation Plan

## Initial repository findings

- `llm_astrology_input_v1.py` existait déjà comme owner canonique, mais le matériau de hash était local au builder.
- L'audit natal calculait encore `llm_input_hash` depuis une identité incluant `request_id`.
- Les chemins pytest exigés par CS-333 n'existaient pas tous; RG-022 impose des chemins collectés.

## Proposed changes

- Exposer un helper canonique `build_llm_input_hash_material`.
- Classer les rôles de données dans le contrat LLM.
- Aligner l'audit natal sur `llm_astrology_input_v1.provenance`.
- Ajouter les tests unitaires, intégration et architecture aux chemins demandés.
- Persister les preuves CS-333 sous `evidence/`.

## Files to modify

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- Tests sous `backend/tests/unit/domain/astrology`, `backend/tests/integration/llm`, `backend/tests/architecture`
- Capsule CS-333 sous `_condamad/stories/...`

## Files to delete

- Aucun fichier applicatif supprimé.
- Une capsule parallèle `_condamad/stories/cs-333` créée par une première préparation ambiguë a été supprimée immédiatement; la cible officielle est restée `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique`.

## Tests to add or update

- `test_llm_astrology_input_hash.py`
- `test_llm_astrology_input_evidence.py`
- `test_natal_llm_astrology_input_audit.py`
- `test_llm_astrology_input_audit_boundary.py`
- Mise à jour ciblée de `test_llm_astrology_input_v1.py`

## Risk assessment

- Risque principal: changement d'audit interne pour les réponses non rejetées, qui portent maintenant les refs du contrat LLM au lieu de `not_checked` vide.
- Risque réduit par les tests de non-exposition OpenAPI/routes et la suite backend complète.

## Rollback strategy

- Revenir les deux fichiers applicatifs et les tests CS-333; aucun schéma, migration, API publique ou frontend n'a été modifié.
