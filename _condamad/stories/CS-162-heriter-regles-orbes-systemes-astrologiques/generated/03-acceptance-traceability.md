<!-- Matrice de tracabilite des criteres d'acceptation de CS-162. -->

# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `astral_systems` ajoute une self-FK nullable. | Modele SQLAlchemy + migration Alembic + test schema. | `pytest -q app/tests/integration/test_reference_data_migrations.py` | PASS |
| AC2 | Le seed cree la carte d'heritage systeme exacte. | `_ensure_astral_systems` renseigne `traditional -> null`, `modern -> null`, `hellenistic/medieval -> traditional`. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py` | PASS |
| AC3 | Le JSON actif d'orbes n'a plus `copy_rules_from`. | `docs/recherches astro/astral_aspect_orb_rules.json` remplace les copies par `inherits_from`. | `rg -n "copy_rules_from" "../docs/recherches astro/astral_aspect_orb_rules.json"` zero hit | PASS |
| AC4 | Le seed produit exactement 79 regles physiques sans override enfant. | Compteurs seed et tests DB par systeme. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py` | PASS |
| AC5 | `modern` garde ses regles propres. | Resolver continue a matcher les regles locales `modern`. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC6 | `traditional` garde ses regles propres. | Resolver continue a matcher les regles locales `traditional`. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC7 | `hellenistic` herite de `traditional`. | Resolver suit la chaine d'heritage. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC8 | `medieval` herite de `traditional`. | Resolver suit la chaine d'heritage. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC9 | Une regle locale enfant gagne contre une regle parente. | Tri par profondeur locale avant parent. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC10 | Une priorite plus elevee gagne a profondeur egale. | Tri existant preserve a profondeur egale. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC11 | Une regle plus specifique gagne a priorite egale. | Tri existant preserve a priorite egale. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC12 | Un cycle d'heritage leve une erreur explicite. | Guard dans le resolver. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC13 | Le fallback `default_orb_deg` reste actif. | Retour definition par defaut si aucune regle heritee ne matche. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC14 | Une regle desactivee ne matche pas. | Filtre `is_enabled`. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC15 | `natal` reste symetrique. | `_rule_matches_bodies` preserve le matching inverse pour `natal`. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC16 | `transit_to_natal` reste directionnel. | `_rule_matches_bodies` preserve le sens strict. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py` | PASS |
| AC17 | Le seed refuse une copie complete des regles heritees dans les enfants. | Guard seed contre groupes enfants copiant `traditional`. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py` | PASS |
| AC18 | Le doc aspects contient le titre d'heritage. | Section doc ajoutee. | `rg -n "Héritage des systèmes astrologiques" "../docs/recherches astro/tables-aspects-et-roles.md"` | PASS |
| AC19 | Le doc maisons contient le titre d'heritage. | Section doc ajoutee. | `rg -n "Héritage des systèmes astrologiques" "../docs/recherches astro/tables-maisons-et-roles.md"` | PASS |
| AC20 | Le doc planetes contient le titre d'heritage. | Section doc ajoutee. | `rg -n "Héritage des systèmes astrologiques" "../docs/recherches astro/tables-planetes-et-roles.md"` | PASS |
| AC21 | Le doc aspects mappe `hellenistic` vers `traditional`. | Section doc explicite. | `rg -n "hellenistic.*traditional" "../docs/recherches astro/tables-aspects-et-roles.md"` | PASS |
| AC22 | Le doc aspects mappe `medieval` vers `traditional`. | Section doc explicite. | `rg -n "medieval.*traditional" "../docs/recherches astro/tables-aspects-et-roles.md"` | PASS |
| AC23 | Le doc maisons mappe `hellenistic` vers `traditional`. | Section doc explicite. | `rg -n "hellenistic.*traditional" "../docs/recherches astro/tables-maisons-et-roles.md"` | PASS |
| AC24 | Le doc maisons mappe `medieval` vers `traditional`. | Section doc explicite. | `rg -n "medieval.*traditional" "../docs/recherches astro/tables-maisons-et-roles.md"` | PASS |
| AC25 | Le doc planetes mappe `hellenistic` vers `traditional`. | Section doc explicite. | `rg -n "hellenistic.*traditional" "../docs/recherches astro/tables-planetes-et-roles.md"` | PASS |
| AC26 | Le doc planetes mappe `medieval` vers `traditional`. | Section doc explicite. | `rg -n "medieval.*traditional" "../docs/recherches astro/tables-planetes-et-roles.md"` | PASS |
