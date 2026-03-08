# Story 39.1: Introduire un ruleset canonique 2.0.0

Status: completed

## Story

As a platform engineer,
I want créer un ruleset canonique `2.0.0` rattaché à la référence `2.0.0` sans supprimer le ruleset legacy `1.0.0`,
So that we have a clean source of truth for calculations while maintaining backward compatibility.

## Acceptance Criteria

- [x] AC1: Le script de seed de référence V2 crée un ruleset `1.0.0` (legacy)
- [x] AC2: Le script de seed de référence V2 crée un ruleset `2.0.0` (canonique)
- [x] AC3: Le script est idempotent (ne duplique pas les rulesets si déjà présents)
- [x] AC4: Le script échoue explicitement si l'état existant est partiel et VERROUILLÉ
- [x] AC5: Le script peut réparer un état partiel et DÉVERROUILLÉ
- [x] AC6: Création de `backend/app/core/versions.py` pour centraliser les versions actives
- [x] AC7: Les constantes `ACTIVE_REFERENCE_VERSION` et `ACTIVE_RULESET_VERSION` sont validées (format SemVer)

## Implementation Details

- Centralisation des versions dans `backend/app/core/versions.py`.
- Mise à jour de `Settings` dans `backend/app/core/config.py` pour utiliser les versions centralisées.
- Refactor du script de seed `backend/scripts/seed_31_prediction_reference_v2.py` pour gérer les deux rulesets et la réparation.
- Validation des formats de version via regex.
- Unification des alias de propriété dans la configuration.

### File List

- `backend/app/core/versions.py`
- `backend/app/core/config.py`
- `backend/scripts/seed_31_prediction_reference_v2.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `_bmad-output/implementation-artifacts/39-1-introduire-un-ruleset-canonique-2-0-0.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
