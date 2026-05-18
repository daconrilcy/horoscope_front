# Final Evidence - CS-185

## Statut

- Story key: `CS-185-brancher-profils-signes-runtime-natal`
- Statut final: done
- Frontend touche: non
- Commit/push: effectues dans le workflow de review-fix.

## Resume

Le runtime natal charge maintenant les profils structurels des signes depuis
`astral_sign_profiles` et les taxonomies `astral_elements`,
`astral_modalities`, `astral_polarities`, sans modifier le payload public
`reference-data`. Les contrats runtime refusent les profils absents ou
`unknown`; les tests prouvent le chargement DB, la propagation builder et les
guards anti-retour.

## AC par AC

- AC1: PASS, jointure DB stricte dans `AstrologyRuntimeReferenceRepository`.
- AC2: PASS, `SignReferenceData` et `SignRuntimeData` typent les profils.
- AC3: PASS, test negatif sur suppression de profil DB.
- AC4: PASS, builder + signature consomment les profils runtime existants.
- AC5: PASS, aucun champ non sourceable n'a ete invente.
- AC6: PASS, guards DB-backed verts.
- AC7: PASS, artefacts evidence produits.

## Fichiers applicatifs changes

- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/services/prediction/reference_seed_service.py`

## Tests / guards changes

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`

## Validations executees

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` - PASS, 1398 files unchanged
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS
- `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS, 7 tests
- `pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py tests/unit/domain/astrology/test_chart_signature.py` - PASS
- `pytest -q tests/unit/domain/astrology/test_chart_signature_runtime_data.py` - PASS
- `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py` - PASS
- `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` - PASS
- Scans No Legacy RG-114 - PASS / `NO_MATCH`
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md` - PASS
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md` - PASS
- `cd backend; python -B -c "from app.main import app; print(len(app.routes))"` - PASS, 221 routes importees

## Findings reviewers corriges

- CR-1 public reference-data: corrige. `ReferenceRepository.get_reference_data()`
  ne projette plus les champs de profil; le runtime natal enrichit son payload
  dans `AstrologyRuntimeReferenceRepository`.
- CR-2 fixture fallback: corrige. La factory n'importe plus `SIGN_PROFILE_DATA`
  et refuse les fixtures de signes sans profil explicite.
- CR-3 erreur profil manquant ambiguë: corrige. Le chargement preserve les
  signes via outer join et remonte `field=sign_profiles`.

## Revue finale

- `generated/11-code-review.md`: CLEAN
- Iterations review/fix: 2 cycles de review, 1 cycle avec corrections, 1 cycle final sans nouvelle issue.

## Risques restants

Aucun risque restant identifie.
