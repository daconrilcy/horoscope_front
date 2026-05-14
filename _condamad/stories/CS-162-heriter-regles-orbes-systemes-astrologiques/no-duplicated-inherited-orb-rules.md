<!-- Preuve de garde anti-duplication des regles d'orbes heritees. -->

# No Duplicated Inherited Orb Rules

## Guard runtime et seed

- `backend/app/services/prediction/reference_seed_service.py` refuse tout groupe `copy_rules_from`.
- `_ensure_no_complete_inherited_orb_rule_copy` compare les signatures parent/enfant et leve `ValueError` si un enfant contient toute la copie du parent.
- `backend/app/tests/integration/test_seed_31_prediction_v2.py::test_seed_rejects_complete_inherited_orb_rule_copy` verrouille ce comportement.

## Guard physique

Le test d'integration `test_seed_31_prediction_v2_full_flow` valide le comptage par systeme pour la version `2.0.0`:

| System | Count |
|---|---:|
| `modern` | 39 |
| `traditional` | 40 |
| `hellenistic` | 0 |
| `medieval` | 0 |

## Scans

- `rg -n "copy_rules_from" "..\docs\recherches astro\astral_aspect_orb_rules.json"`: zero hit.
- `rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"`: zero hit.
- `rg -n "astro_characteristics|AstroCharacteristicModel" app tests`: hits uniquement dans les tests de migration historiques attendus par `RG-091`.
