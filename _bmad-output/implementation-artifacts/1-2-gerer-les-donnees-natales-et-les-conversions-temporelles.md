# Story 1.2: Gerer les donnees natales et les conversions temporelles

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want que mes donnees de naissance soient validees et converties correctement (date/heure/lieu -> UT/JD),  
so that les calculs astrologiques soient fiables.

## Acceptance Criteria

1. Given une date/heure/lieu de naissance valides, when le moteur prepare les donnees d entree, then les conversions temporelles necessaires sont produites de facon deterministe.
2. Les entrees invalides retournent des erreurs explicites et testables.

## Tasks / Subtasks

- [x] Modeliser les donnees natales d entree et de sortie
  - [x] Creer les schemas Pydantic pour input natal (date, heure, lieu, timezone) et output normalise
  - [x] Definir un contrat d erreur stable pour les validations rejetees
- [x] Implementer la validation metier de base
  - [x] Verifier la presence et la forme des champs obligatoires
  - [x] Verifier la coherence minimale date/heure/timezone
  - [x] Produire des erreurs explicites (`error.code`, message, details)
- [x] Implementer les conversions temporelles deterministes
  - [x] Ajouter conversion date/heure locale + timezone -> UTC
  - [x] Ajouter calcul du Julian Day (JD) a partir du timestamp UTC
  - [x] Garantir determinisme pour entrees identiques
- [x] Exposer le service via une route API v1 ciblee moteur
  - [x] Ajouter endpoint de preparation natal (ex: `POST /v1/astrology-engine/natal/prepare`)
  - [x] Aligner format reponse succes/erreur sur conventions architecture
- [x] Tester et valider
  - [x] Tests unitaires: validation inputs + conversions UTC/JD
  - [x] Tests integration API: cas valides et invalides
  - [x] Lint + tests backend passes

## Dev Notes

- Cette story est centree backend (pas de logique UI a implementer).
- Ne pas implementer de calcul astrologique complet ici (pas de maisons/aspects/ephemerides) ; uniquement preparation des donnees d entree.
- Reutiliser les conventions posees en Story 1.1:
  - structure `api/core/domain/services/infra`
  - format d erreurs coherent
  - tests executables dans le venv

### Technical Requirements

- Input minimal attendu:
  - `birth_date` (YYYY-MM-DD)
  - `birth_time` (HH:MM ou HH:MM:SS)
  - `birth_place` (string)
  - `birth_timezone` (IANA, ex: `Europe/Paris`)
- Output minimal attendu:
  - datetime locale normalisee
  - datetime UTC
  - timestamp
  - Julian Day (JD)
  - metadonnees de conversion (timezone appliquee)
- Erreurs:
  - codes stables (ex: `invalid_birth_date`, `invalid_birth_time`, `invalid_timezone`, `invalid_birth_input`)
  - message lisible + details testables

### Architecture Compliance

- Respecter strictement:
  - couches backend (`api/core/domain/services/infra`)
  - API REST versionnee `/v1`
  - modele d erreurs unifie
  - typage Python et validation via Pydantic
- Garder la logique de conversion dans `domain`/`services`, pas dans `api`.

### Library / Framework Requirements

- Backend:
  - FastAPI
  - Pydantic 2
  - Python 3.13
- Time handling:
  - utiliser les outils standards Python (`datetime`, `zoneinfo`) sauf besoin explicite d extension

### File Structure Requirements

- Recommandation d implantation:
  - `backend/app/domain/astrology/` (conversion/normalisation)
  - `backend/app/services/` (orchestration use-case)
  - `backend/app/api/v1/routers/` (endpoint)
  - `backend/app/tests/unit/` et `backend/app/tests/integration/`
- Si une arborescence `v1/routers` n est pas encore en place, l introduire proprement sans casser l existant.

### Testing Requirements

- Unit tests obligatoires:
  - parsing/validation inputs valides-invalides
  - conversion timezone -> UTC
  - calcul JD deterministe
- Integration tests obligatoires:
  - endpoint preparation natal 200 sur input valide
  - 4xx sur inputs invalides avec `error.code` attendu
- Commandes de verification:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 1.1 a etabli un socle propre:
  - backend FastAPI demarrable avec healthcheck
  - conventions de structure et tooling (ruff/pytest) deja en place
  - compose et environnement de dev operationnels
- Conserver ces acquis:
  - ne pas casser `/health`
  - ne pas introduire de dependances non necessaires
  - garder les modifications minimales et ciblees

### Project Context Reference

- Aucun `project-context.md` detecte; utiliser PRD/Architecture/Epics comme source d autorite.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.2)
- Priorite implementation: `_bmad-output/planning-artifacts/architecture.md` (Implementation Sequence, Data Architecture, API patterns)
- Contraintes metier foundation: `_bmad-output/planning-artifacts/prd.md` (FR3, FR4, FR8, Phase 0 Foundation)
- Story precedente: `_bmad-output/implementation-artifacts/1-1-set-up-initial-project-from-starter-template.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Create-story workflow execution
- Dev-story workflow execution
- Backend checks (venv active): `ruff check .`, `pytest -q`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Preparation des donnees natales implementee (validation + conversion timezone -> UTC + JD).
- Endpoint `POST /v1/astrology-engine/natal/prepare` ajoute avec gestion d erreurs explicites.
- Conventions d architecture preservees (domain/services/api v1).
- Tests unitaires et integration ajoutes et passes.
- Story promue au statut `review`.
- Code review auto-fix applique: contrat `invalid_birth_input` ajoute pour erreurs de schema, validation `birth_place` renforcee, OpenAPI response models explicites, tests invalid date/missing field ajoutes.
- Story promue au statut `done` apres correction des findings High/Medium/Low.

### File List

- _bmad-output/implementation-artifacts/1-2-gerer-les-donnees-natales-et-les-conversions-temporelles.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/pyproject.toml
- backend/app/main.py
- backend/app/api/v1/routers/astrology_engine.py
- backend/app/domain/astrology/natal_preparation.py
- backend/app/services/natal_preparation_service.py
- backend/app/tests/unit/test_natal_preparation.py
- backend/app/tests/integration/test_natal_prepare_api.py
- backend/app/domain/astrology/__init__.py
- backend/app/api/v1/__init__.py
- backend/app/api/v1/routers/__init__.py
- backend/app/tests/unit/__init__.py
- backend/app/tests/integration/__init__.py

### Change Log

- 2026-02-18: Story 1.2 implementee, tests backend passes, statut passe a review.
- 2026-02-18: Code review findings corriges automatiquement (High/Medium/Low), statut passe a done.
