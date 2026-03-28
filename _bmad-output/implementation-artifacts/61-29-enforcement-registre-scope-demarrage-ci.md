# Story 61.29 : Enforcement du registre de scope au démarrage et dans la CI

Status: done

## Story

En tant que développeur backend ou opérateur,
je veux que la validation de cohérence du registre de scope (`FeatureRegistryConsistencyValidator`) soit exécutée automatiquement au démarrage de l'application et disponible comme étape explicite de validation CI,
afin qu'aucune incohérence entre `FEATURE_SCOPE_REGISTRY`, les gates quota et les features canoniques ne puisse atteindre un environnement d'exécution sans être détectée immédiatement.

## Contexte

La story 61.28 a introduit :

* `backend/app/services/feature_registry_consistency_validator.py`
* `FeatureRegistryConsistencyValidator` avec 4 vérifications statiques, sans DB
* le script CLI `backend/scripts/check_feature_scope_registry.py`

À ce stade, la protection existe mais reste encore partiellement **opt-in** : un développeur peut oublier de lancer le script avant de lancer ou avant de démarrer l'application.

La story 61.29 transforme cette vérification en **enforcement systématique** :

* au boot de l'application backend, via `_app_lifespan`
* via des tests de bootstrap dédiés
* via une commande CLI documentée comme étape obligatoire de validation CI

Cette story ne change **aucun contrat métier** des entitlements. Elle renforce uniquement la sûreté structurelle du système.

Tableau de complémentarité des trois couches de protection :

| Story     | Niveau de protection                                                          | Déclenchement                            |
| --------- |-------------------------------------------------------------------------------| ---------------------------------------- |
| **61.27** | Runtime — refuse le mauvais service de quota                                  | À chaque appel quota                     |
| **61.28** | Design-time / validation statique — détecte les incohérences de registre      | À la demande / en CI                     |
| **61.29** | Boot-time + CI explicite — bloque le démarrage ou la livraison si incohérence | Au démarrage de l'app + en validation CI |

---

## Acceptance Criteria

### AC 1 — Validation automatique au démarrage du backend

1. `FeatureRegistryConsistencyValidator.validate()` est exécuté automatiquement au démarrage de l'application backend.
2. Si la validation échoue en mode `strict`, le démarrage échoue immédiatement avec un log explicite contenant l'intégralité des incohérences détectées.
3. Le log d'échec contient un préfixe stable : `feature_scope_registry_startup_validation_failed`.
4. En cas de succès, un log INFO explicite est émis : `feature_scope_registry_startup_validation_ok`.

### AC 2 — Intégration propre dans le cycle de vie FastAPI

5. L'appel est branché explicitement dans `_app_lifespan` de `backend/app/main.py`, pas dans un import passif ou un effet de bord de module.
6. La validation n'est exécutée qu'une seule fois par processus applicatif, avant le `yield` du lifespan.
7. Aucun endpoint public n'est modifié.

### AC 3 — Mode de contournement contrôlé

8. Une variable de configuration dédiée est ajoutée dans `backend/app/core/config.py` :

   * nom Python : `feature_scope_validation_mode`
   * variable d'environnement : `FEATURE_SCOPE_VALIDATION_MODE`
   * valeurs valides : `"strict"`, `"warn"`, `"off"`
   * défaut : `"strict"`
9. En mode `strict` : succès → démarrage normal ; échec → exception et arrêt du démarrage.
10. En mode `warn` : échec → log ERROR structuré ; l'application continue à démarrer.
11. En mode `off` : la validation n'est pas exécutée ; un log WARNING explicite indique qu'elle est désactivée.
12. Une valeur invalide de `FEATURE_SCOPE_VALIDATION_MODE` est normalisée vers `"strict"` avec log WARNING explicite ; elle ne provoque pas de crash de configuration.

### AC 4 — Couverture de tests dédiée

13. `backend/app/tests/unit/test_feature_scope_startup_validation.py` est créé avec :

    * `test_startup_validation_strict_ok`
    * `test_startup_validation_strict_fails`
    * `test_startup_validation_warn_does_not_block`
    * `test_startup_validation_off_skips_validator`
    * `test_startup_validation_invalid_mode_falls_back_to_strict`

14. Les tests 61.27 et 61.28 continuent de passer sans modification métier.

### AC 5 — Validation CLI explicite pour la CI

15. La commande `python backend/scripts/check_feature_scope_registry.py` est documentée comme étape obligatoire de validation statique backend.
16. `backend/app/tests/unit/test_check_feature_scope_registry_cli.py` est créé avec :

    * `test_cli_main_exit_0_on_consistent_registry`
    * `test_cli_main_exit_1_on_inconsistent_registry`

17. Les tests CLI appellent `main()` du script directement dans le même process Python ; ils ne reposent pas sur un `subprocess` patché de manière fragile.
18. Si le repo contient déjà un workflow ou runbook qualité backend versionné, la commande y est ajoutée ; sinon elle est au minimum documentée explicitement dans la doc canonique.

### AC 6 — Documentation

19. `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Enforcement startup + CI (Story 61.29)"** précisant :

    * la validation design-time introduite en 61.28
    * son exécution obligatoire au démarrage depuis 61.29
    * les 3 modes `strict`, `warn`, `off`
    * la commande CLI à intégrer en CI
    * la séquence recommandée de validation
    * la distinction entre les couches 61.27 / 61.28 / 61.29

### AC 7 — Non-régression

20. La suite pytest quota B2C/B2B existante, y compris les tests 61.27 et 61.28, reste verte.
21. Aucun contrat API public n'est modifié.
22. Aucune migration Alembic n'est créée.

---

## Tasks / Subtasks

- [x] **Créer le bootstrap de validation** (AC: 1, 2, 3)
  - [x] Créer `backend/app/startup/feature_scope_validation.py`
  - [x] Implémenter `run_feature_scope_startup_validation(mode: str) -> None`
  - [x] Mode `"off"` → log WARNING `feature_scope_registry_startup_validation_disabled`, retour immédiat
  - [x] Mode `"strict"` → appel `validate()`, log INFO si OK, log ERROR + re-raise sur échec
  - [x] Mode `"warn"` → appel `validate()`, log ERROR sur échec, ne pas propager
  - [x] Si mode invalide → log WARNING explicite + fallback `"strict"`

- [x] **Brancher la validation dans `main.py`** (AC: 1, 2)
  - [x] Importer `run_feature_scope_startup_validation`
  - [x] Appeler `run_feature_scope_startup_validation(settings.feature_scope_validation_mode)` dans `_app_lifespan`, avant le `yield`
  - [x] Positionner l'appel après les autres validations/seed startup déjà existants, dans une zone cohérente du lifecycle

- [x] **Ajouter la config dédiée dans `config.py`** (AC: 3)
  - [x] Lire `FEATURE_SCOPE_VALIDATION_MODE`
  - [x] Normaliser les valeurs invalides vers `"strict"`
  - [x] Exposer `settings.feature_scope_validation_mode`

- [x] **Créer `test_feature_scope_startup_validation.py`** (AC: 4)
  - [x] `test_startup_validation_strict_ok`
  - [x] `test_startup_validation_strict_fails`
  - [x] `test_startup_validation_warn_does_not_block`
  - [x] `test_startup_validation_off_skips_validator`
  - [x] `test_startup_validation_invalid_mode_falls_back_to_strict`

- [x] **Créer `test_check_feature_scope_registry_cli.py`** (AC: 5)
  - [x] `test_cli_main_exit_0_on_consistent_registry`
  - [x] `test_cli_main_exit_1_on_inconsistent_registry`

- [x] **Mettre à jour la documentation** (AC: 6)
  - [x] `backend/docs/entitlements-canonical-platform.md`
  - [x] Si présent dans le repo : runbook qualité / doc CI backend

- [x] **Validation finale** (AC: 7)
  - [x] `ruff check` sur tous les fichiers créés/modifiés
  - [x] `pytest backend/app/tests/unit/test_feature_scope_startup_validation.py`
  - [x] `pytest backend/app/tests/unit/test_check_feature_scope_registry_cli.py`
  - [x] `pytest backend/app/tests/unit/test_feature_registry_consistency_validator.py`
  - [x] suite non-régression 61.27 / 61.28

---

## Dev Notes

### Architecture de la solution

Le bootstrap est isolé dans `backend/app/startup/feature_scope_validation.py`, pour rester testable indépendamment de FastAPI et éviter de mélanger la logique métier de validation avec le wiring applicatif.

Il ne dépend ni de la DB, ni d'un endpoint, ni d'un objet FastAPI. Il reçoit simplement un `mode` et applique la politique de démarrage correspondante.

### Implémentation recommandée du bootstrap

```python
import logging

from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
    FeatureRegistryConsistencyValidator,
)

logger = logging.getLogger(__name__)

_VALID_MODES = frozenset({"strict", "warn", "off"})


def run_feature_scope_startup_validation(mode: str) -> None:
    """Run feature scope registry validation at application startup.

    strict -> failure blocks startup
    warn   -> failure is logged but startup continues
    off    -> validation skipped explicitly
    """
    if mode not in _VALID_MODES:
        logger.warning(
            "feature_scope_registry_startup_validation_invalid_mode mode=%s fallback=strict",
            mode,
        )
        mode = "strict"

    if mode == "off":
        logger.warning("feature_scope_registry_startup_validation_disabled")
        return

    try:
        FeatureRegistryConsistencyValidator.validate()
        logger.info("feature_scope_registry_startup_validation_ok")
    except FeatureRegistryConsistencyError as exc:
        logger.error(
            "feature_scope_registry_startup_validation_failed errors=%s",
            exc,
        )
        if mode == "strict":
            raise
```

### Intégration dans `_app_lifespan`

L'appel doit être placé explicitement dans `_app_lifespan` de `backend/app/main.py`, avant le `yield`.
Il doit vivre au même niveau que les autres checks de startup déjà en place, et non dans un import de module opportuniste.

### Configuration `feature_scope_validation_mode`

Pattern recommandé dans `Settings.__init__` :

```python
raw_feature_scope_validation_mode = (
    os.getenv("FEATURE_SCOPE_VALIDATION_MODE", "strict").strip().lower()
)
if raw_feature_scope_validation_mode not in {"strict", "warn", "off"}:
    raw_feature_scope_validation_mode = "strict"
self.feature_scope_validation_mode = raw_feature_scope_validation_mode
```

### Tests bootstrap

Les tests mockent directement `FeatureRegistryConsistencyValidator.validate` dans le module bootstrap, pas dans le validateur source, pour tester le wiring réel du bootstrap.

```python
VALIDATE_PATH = (
    "app.startup.feature_scope_validation.FeatureRegistryConsistencyValidator.validate"
)
```

### Tests CLI

Pour éviter les faux positifs et les patchs inter-process peu fiables, les tests CLI appellent directement `main()` du script dans le même process Python.

Pattern recommandé :

```python
from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
)
from scripts.check_feature_scope_registry import main
```

Puis patch de `FeatureRegistryConsistencyValidator.validate` dans le module du script :

```python
VALIDATE_PATH_CLI = (
    "app.services.feature_registry_consistency_validator"
    ".FeatureRegistryConsistencyValidator.validate"
)

def test_cli_main_exit_0_on_consistent_registry():
    with patch(VALIDATE_PATH_CLI):
        assert main() == 0


def test_cli_main_exit_1_on_inconsistent_registry():
    with patch(
        VALIDATE_PATH_CLI,
        side_effect=FeatureRegistryConsistencyError("test error"),
    ):
        assert main() == 1
```

### Contraintes techniques

* Pas de connexion DB
* Pas de migration Alembic
* Pas de modification d'API
* Un seul appel par process via lifespan
* Le module `backend/app/startup/` doit être un package Python ; créer `__init__.py` si absent

### Séquence CI recommandée

```bash
ruff check backend/
pytest backend/app/tests/
python backend/scripts/check_feature_scope_registry.py
```

### Project Structure Notes

**Nouveaux fichiers :**

* `backend/app/startup/feature_scope_validation.py`
* `backend/app/tests/unit/test_feature_scope_startup_validation.py`
* `backend/app/tests/unit/test_check_feature_scope_registry_cli.py`

**Fichiers potentiellement créés si absent :**

* `backend/app/startup/__init__.py`

**Fichiers modifiés :**

* `backend/app/core/config.py`
* `backend/app/main.py`
* `backend/docs/entitlements-canonical-platform.md`

### References

- [Source: backend/app/main.py#L227-L260] — `_app_lifespan` actuel (pattern lifecycle)
- [Source: backend/app/core/config.py#L127] — `__init__` de `Settings` (pattern ajout config)
- [Source: backend/app/services/feature_registry_consistency_validator.py] — validateur 61.28
- [Source: backend/scripts/check_feature_scope_registry.py] — script CLI 61.28
- [Source: backend/app/tests/unit/test_feature_registry_consistency_validator.py] — tests 61.28 (technique de patch)
- [Source: backend/docs/entitlements-canonical-platform.md] — documentation existante 61.27/61.28
- [Source: _bmad-output/implementation-artifacts/61-28-validation-coherence-canonique-feature-code.md] — story précédente

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List
- Implemented `run_feature_scope_startup_validation` in `backend/app/startup/feature_scope_validation.py`.
- Added `FEATURE_SCOPE_VALIDATION_MODE` to `backend/app/core/config.py`.
- Integrated validation into `_app_lifespan` in `backend/app/main.py`.
- Added unit tests for startup validation and CLI exit codes.
- Updated documentation in `backend/docs/entitlements-canonical-platform.md`.
- Verified all tests pass and linting is clean.

### File List
- `backend/app/core/config.py` (modified)
- `backend/app/main.py` (modified)
- `backend/app/startup/__init__.py` (new)
- `backend/app/startup/feature_scope_validation.py` (new)
- `backend/app/tests/unit/test_feature_scope_startup_validation.py` (new)
- `backend/app/tests/unit/test_check_feature_scope_registry_cli.py` (new)
- `backend/docs/entitlements-canonical-platform.md` (modified)
